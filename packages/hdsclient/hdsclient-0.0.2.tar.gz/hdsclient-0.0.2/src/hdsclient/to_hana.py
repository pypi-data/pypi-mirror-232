import logging
from dataclasses import dataclass

from hdbcli import dbapi
import yaml
from icecream import ic

logging.basicConfig(format='%(message)s', level=logging.INFO)

@dataclass
class C:
    n: str = "\033[0m"
    red: str = "\033[31m"
    green: str = "\033[32m"
    yellow: str = "\033[33m"
    blue: str = "\033[34m"
    magenta: str = "\033[35m"
    cyan: str = "\033[36m"

dl2sql = {
    "string": "NVARCHAR(100)",
    "long": "BIGINT",
    "timestamp": "TIMESTAMP"
}


def execute_sql(db: dict,sql: str) -> None:
    conn = dbapi.connect(address=db['host'], port=db['port'], user=db['user'], password=db['pwd'], encrypt=True, sslValidateCertificate=False)
    cursor = conn.cursor()
    ret = cursor.execute(sql)
    logging.info(f"Execute sql: {sql}")
    if ret :
        logging.debug(f'Successfully executed sql: {sql}')
    cursor.close()
    conn.close()

def schema_exists(db: dict,schema: str) -> bool:
    conn = dbapi.connect(address=db['host'], port=db['port'], user=db['user'], password=db['pwd'], encrypt=True, sslValidateCertificate=False)
    cursor = conn.cursor()
    sql = f"SELECT count(*) FROM SCHEMAS WHERE \"SCHEMA_NAME\"='{schema.upper()}';"
    logging.info(f"Execute sql: {C.green}{sql}{C.n}")
    ret = cursor.execute(sql)
    if not ret:
        raise ConnectionError(ret)
    num_rows = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return True if num_rows > 0  else False

def table_exists(db: dict,schema: str, table: str) -> bool:
    conn = dbapi.connect(address=db['host'], port=db['port'], user=db['user'], password=db['pwd'], encrypt=True, sslValidateCertificate=False)
    cursor = conn.cursor()
    sql = f"SELECT COUNT(*) FROM \"PUBLIC\".\"M_TABLES\" WHERE \"SCHEMA_NAME\"='{schema.upper()}' and \"TABLE_NAME\" = '{table.upper()}';"
    logging.info(f"Execute sql: {C.green}{sql}{C.n}")
    ret = cursor.execute(sql)
    if not ret:
        raise ConnectionError(ret)
    num_rows = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return True if num_rows > 0  else False

def create_table_sql(schema: str, table: str, columns: dict) -> str:
    sql = f"CREATE COLUMN TABLE \"{schema.upper()}\".\"{table.upper()}\" (\n"
    for c, v in columns.items():
        not_null = ' NOT NULL' if v['nullable'] else ''
        sql += f"\t{c} {dl2sql[v['type']]}{not_null},\n"
    sql = sql[:-2] + ');'
    return sql


def create_table(db: dict, schema: str, table: str, columns: dict) -> str:
    execute_sql(db, create_table_sql(schema=schema, table=table, columns=columns))


def create_schema(db: dict, schema: str) -> str:
    execute_sql(db, f"CREATE SCHEMA {schema.upper()}")


def upload(db: dict,schema: str, table: str, df) :
    conn = dbapi.connect(address=db['host'], port=db['port'], user=db['user'], password=db['pwd'], encrypt=True,
                         sslValidateCertificate=False)
    cursor = conn.cursor()
    col_names = ','.join([c for c in df.columns])
    place_holders = ','.join(['?'] * df.shape[1])
    sql = f"INSERT INTO \"{schema.upper()}\".\"{table.upper()}\" ({col_names}) VALUES ({place_holders})"
    print(f'Uploading SQL: {C.green}{sql}{C.n}')
    data = list(df.itertuples(index=False))
    cursor.executemany(sql, data)
    cursor.close()
    conn.close()


def insert_batch(db: dict, schema: str, table: str, df):
    conn = dbapi.connect(address=db['host'], port=db['port'], user=db['user'], password=db['pwd'], encrypt=True,
                         sslValidateCertificate=False)
    cursor = conn.cursor()
    columns = [c for c in df.columns]
    place_holders = ','.join(['?'] * df.shape[1])
    sql = f"INSERT INTO \"{schema.upper()}\".\"{table.upper()}\" ({','.join(columns)}) VALUES ({place_holders})"
    print(f'INSERT SQL: {C.green}{sql}{C.n}')
    data = list(df[columns].itertuples(index=False))
    cursor.executemany(sql, data)
    cursor.close()
    conn.close()

def insert(db: dict, schema: str, table: str, df):
    conn = dbapi.connect(address=db['host'], port=db['port'], user=db['user'], password=db['pwd'], encrypt=True,
                         sslValidateCertificate=False)
    cursor = conn.cursor()
    columns = [c for c in df.columns]
    
    data = list(df[columns].itertuples(index=False))
    for row in data:
        values = ','.join([f"\'{v}\'" for v in row])
        sql = f"INSERT INTO \"{schema.upper()}\".\"{table.upper()}\" ({','.join(columns)}) VALUES ({values})"
        print(f'INSERT SQL: {C.green}{sql}{C.n}')
        cursor.execute(sql)
    cursor.close()
    conn.close()

def delete(db: dict, schema: str, table: str, columns: list, df):
    conn = dbapi.connect(address=db['host'], port=db['port'], user=db['user'], password=db['pwd'], encrypt=True,
                         sslValidateCertificate=False)
    cursor = conn.cursor()

    data =  df.to_dict('records')
    for row in data:
        where_statement = ' and '.join([ f"{k}=\'{v}\'" for k,v in row.items()])
        sql = f"DELETE FROM  \"{schema.upper()}\".\"{table.upper()}\" WHERE {where_statement}"
        print(f'DELETE SQL: {C.green}{sql}{C.n}')

    cursor.execute(sql)
    cursor.close()
    conn.close()


def update(db: dict, schema: str, table: str, df):
    conn = dbapi.connect(address=db['host'], port=db['port'], user=db['user'], password=db['pwd'], encrypt=True,
                         sslValidateCertificate=False)
    cursor = conn.cursor()

    data =  iter(df.to_dict('records'))
    for row_pre in data:
        where_statement = ' and '.join([ f"{k}=\'{v}\'" for k,v in row_pre.items()])
        row_post = next(data)
        set_statement = ', '.join([ f"{k}=\'{v}\'" for k,v in row_post.items()])
        sql = f"UPDATE \"{schema.upper()}\".\"{table.upper()}\" SET {set_statement} WHERE {where_statement}"
        print(f'UPDATE SQL: {C.green}{sql}{C.n}')
        cursor.execute(sql)
        
    cursor.close()
    conn.close()


def main() :

    with open('config.yaml') as yamls:
        db = yaml.safe_load(yamls)

    
    schema='SPARK'
    table='STOREX'
    
    if table_exists(db,schema=schema, table=table):
        logging.info(f"Table exists! ({schema}.{table})")


if __name__ == '__main__':
    main()

    