
import logging
import argparse
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
import json
from urllib.error import HTTPError

from icecream import ic
import delta_sharing
import yaml
import pandas as pd

from pycsn.pycsn import PyCSN

from to_hana import table_exists, schema_exists, create_schema, create_table,execute_sql, upload, insert, delete, update, insert_batch


def change_params(start: str, end: str) -> int:
    try:
        a = int(start)
        b = int(end) if end else end
        return {"starting_version": a, "ending_version":b}
    except ValueError as ae:
        #a = datetime.fromisoformat(start)
        #b = datetime.fromisoformat(end)
        return {"starting_timestamp": start, "ending_timestamp":end}
    

def get_metadata(table_url):
    metadata = delta_sharing.get_table_metadata(table_url)
    columns = { c['name']: {'type': c['type'],'nullable': c['nullable']} for c in json.loads(metadata.schema_string)['fields']}
    metadata = {"name": metadata.name, "description": metadata.description, "format": metadata.format.provider, "version": metadata.version,
                "enableChangeDataFeed": metadata.configuration['enableChangeDataFeed'], "size": metadata.size, "columns": columns}
    return metadata


logging.basicConfig(level=logging.INFO)

@dataclass
class C:
    n: str = "\033[0m"
    red: str = "\033[31m"
    green: str = "\033[32m"
    yellow: str = "\033[33m"
    blue: str = "\033[34m"
    magenta: str = "\033[35m"
    cyan: str = "\033[36m"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("profile", help="Profile of delta sharing")
    parser.add_argument('table', nargs='?', help="(optional) Table URL: <share>.<schema>.<table>. If not given table can be selected from available table list. ")
    parser.add_argument("-p", "--path", help="Directory to store data." )
    parser.add_argument("-d", "--delta", help="Capture delta feeds", action="store_true")
    parser.add_argument("-s", "--starting", help="Start version (int, min=1)m or timestamp (str,\"2019-09-26T07:58:30.996+0200\")")
    parser.add_argument("-e", "--ending", help="End version (int, min=1) or timestamp (str,\"2019-09-26T07:58:30.996+0200\")",default=None)
    parser.add_argument("-m", "--meta", help="Show metadata", action="store_true")
    parser.add_argument("-c", "--config-file", help="Config-file for HANA access (yaml with url, user, pwd, port)", default="config.yaml")
    parser.add_argument("-H", "--Hana", help="Upload to hana", action="store_true")
    parser.add_argument("-S", "--Sync", help="Sync files with hana", action="store_true")
    args = parser.parse_args()
    profile = args.profile

    # TABLE
    if args.table:
        table = args.table
        table_file = table.replace('.','_')
    else:
        client = delta_sharing.SharingClient(profile)
        tables = client.list_all_tables()
        print(f"{C.red}Tables in share:{C.n}\n-------------------")
        for i, t in enumerate(tables):
            print(f"{i+1}: {C.green}{t.share}.{t.schema}.{t.name}{C.n}")
        selected = input(f"{C.red}Select table number for download: {C.n}")
        if selected:
            index = int(selected) - 1
            table = f"{tables[index].share}.{tables[index].schema}.{tables[index].name}"
            table_file = f"{tables[index].share}_{tables[index].schema}_{tables[index].name}"
        else:
            raise ValueError(f"{C.red}No table selected!{C.n}")
    table_url = profile + '#' + table
    share, schema, table_short = table.split('.')

    # PATH
    if args.path:
        data_path = Path(args.path)
        if not data_path.is_dir():
            data_path.mkdir()
    else:
        data_path = Path('.')

    # DOWNLOADS
    if args.meta:
        metadata = get_metadata(table_url=table_url)
        # Print
        print(f"Metadata of   {C.green}{table}{C.n}")
        print(f"Name:         {C.green}{metadata['name']}{C.n}")
        print(f"Description:  {C.green}{metadata['description']}{C.n}")
        print(f"Format:       {C.green}{metadata['format']}{C.n}")
        print(f"Version:      {C.green}{metadata['version']}{C.n}")
        print(f"CDF enabled:  {C.green}{metadata['enableChangeDataFeed']}{C.n}")
        print(f"Size:         {C.green}{metadata['size']}{C.n}")
        print(f"Fields:")
        padding_length = max([len(c)for c in metadata['columns'].keys()]) + 3
        for c, v in metadata['columns'].items():
            print(f"- {C.green}{c:<{padding_length}}{v['type']:<15}nullable: {v['nullable']}{C.n}")

        filename = data_path /  Path(table_file + '_meta.json')
        print(f"Write metadata to: {filename}")
        with open(filename, "w") as fp:
            json.dump(metadata, fp, indent=4)

    elif args.delta and not args.Sync:  
        if args.starting:     
            cp = change_params(args.starting, args.ending)
            df = delta_sharing.load_table_changes_as_pandas(table_url, **cp)
            filename = data_path /  Path(f"{table_file}_{args.starting}-{args.ending}.csv")
            print(f"Save file to {C.green}{filename}{C.n}")
            df.to_csv(filename, index=False)
        else:
            delta_filename = data_path / Path(f'{table_file}_delta.csv')
            version_filename = data_path / Path(f'{table_file}_version.txt')
            if version_filename.is_file():
                last_version = int(open(version_filename).readline())
            else: 
                last_version = 0
            version = delta_sharing.get_table_version(table_url)
            if version > last_version:     
                print(f"New version: {C.green}{version}{C.n} (last version: {C.green}{last_version}{C.n})")
                df = delta_sharing.load_table_changes_as_pandas(table_url, starting_version=last_version+1)   
                print(f"Save data to {C.green}{delta_filename}{C.n}")
                if not delta_filename.is_file(): 
                    df.to_csv(delta_filename, index=False)
                else: 
                    df.to_csv(delta_filename, mode='a', header=False, index=False)
                open(version_filename, 'w').write(str(version))
                if args.Hana:
                    hana_last_version = int(open(data_path / Path(f'{table_file}_hana_version.txt')).readline())
                    if hana_last_version != last_version:
                        raise ValueError("Hana last version not equal file last version! Sync first delta files to hana. ")
                    with open(args.config) as yamls:
                        db = yaml.safe_load(yamls)
                    columns = [c for c in df.columns if c not in ['_change_type','_commit_version','_commit_timestamp']]
                    for v in range(last_version+1,version+1):
                        df_insert = df.loc[(df["_change_type"]=='insert') & (df["_commit_version"]==v),columns]
                        if not df_insert.empty:
                            insert(db, schema=schema, table=table_short, df=df_insert)
                        
                        df_delete = df.loc[(df["_change_type"]=='delete') & (df["_commit_version"]==v),columns]
                        if not df_delete.empty:
                            delete(db, schema=schema, table=table_short, columns=columns, df=df_delete)

                        df_update = df.loc[((df["_change_type"]=='update_preimage') | (df["_change_type"]=='update_postimage'))
                                            & (df["_commit_version"]==v),columns]
                        if not df_update.empty:
                            update(db, schema=schema, table=table_short, df=df_update)
                    open(data_path / Path(f'{table_file}_hana_version.txt'), 'w').write(str(version))

            else:
                print(f"No newer version than: {C.green}{last_version}{C.n}")

    elif args.Sync:
        print(f"Sync table {C.green}{table}{C.n}")
        last_version = int(open(data_path / Path(f'{table_file}_version.txt')).readline())
        hana_last_version = int(open(data_path / Path(f'{table_file}_hana_version.txt')).readline())
        if last_version ==  hana_last_version:
            print(f"Table {C.green}{table}{C.n} is in sync (file:{last_version} = hana:{hana_last_version} ")
            return 0
        df = pd.read_csv(data_path / Path(f'{table_file}_delta.csv'))
        df = df.loc[df['_commit_version'] > hana_last_version]
        with open(args.config) as yamls:
            db = yaml.safe_load(yamls)

        columns = [c for c in df.columns if c not in ['_change_type','_commit_version','_commit_timestamp']]

        for v in range(hana_last_version+1, last_version+1):
            df_insert = df.loc[(df["_change_type"]=='insert') & (df["_commit_version"]==v),columns]
            if not df_insert.empty:
                insert(db, schema=schema, table=table_short, df=df_insert)
                insert_batch(db, schema=schema, table=table_short, df=df_insert)
            
            df_delete = df.loc[(df["_change_type"]=='delete') & (df["_commit_version"]==v),columns]
            if not df_delete.empty:
                delete(db, schema=schema, table=table_short, columns=columns, df=df_delete)

            df_update = df.loc[((df["_change_type"]=='update_preimage') | (df["_change_type"]=='update_postimage'))
                                & (df["_commit_version"]==v),columns]
            if not df_update.empty:
                update(db, schema=schema, table=table_short, df=df_update)
        open(data_path / Path(f'{table_file}_hana_version.txt'), 'w').write(str(last_version))

    else:
        filename = data_path / Path(f'{table_file}.csv')
        print(f"Save data to file:{C.green}{filename}{C.n}")
        df = delta_sharing.load_as_pandas(table_url)
        df.to_csv(filename, index=False)
        
        cdf = get_metadata(table_url=table_url)["enableChangeDataFeed"]
        if cdf:
            version = delta_sharing.get_table_version(table_url)
            open(data_path / Path(f'{table_file}_version.txt'), 'w').write(str(version))

        if args.Hana:
            with open(args.config) as yamls:
                db = yaml.safe_load(yamls)

            if not schema_exists(db,schema=schema):
                print(f"{C.red}Schema is not existing: {C.green}\"{schema.upper()}\"{C.n}")
                create_schema(db, schema)
            
            if not table_exists(db,schema=schema, table=table_short):
                print(f"{C.red}Table is not existing -> create table: {C.green}\"{schema}\".\"{table_short}\"{C.n}")
                csn_file = filename.with_suffix('.csn')
                if csn_file.is_file():
                    print(f"CSN-file exists: {C.green}{csn_file}{C.n}")
                    csn = PyCSN(csn_file)
                    execute_sql(db,csn.create_table_sql(f"{schema.upper()}.{table_short.upper()}"))
                else:
                    columns = get_metadata(table_url)['columns']
                    create_table(db, schema, table_short, columns)

            print(f"Save data to hana {C.green}{db['host']}{C.n}")
            upload(db, schema=schema, table=table_short, df=df)
            if cdf:
                open(data_path / Path(f'{table_file}_hana_version.txt'), 'w').write(str(version))


if __name__ == "__main__":
    main()