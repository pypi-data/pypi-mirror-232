from datetime import datetime

startv = "4"
endv = "6"

startt = "2023-04-01 05:00:30.001000"
endt = "2023-04-02 05:03:30.001000"

def change_params(start: str, end: str) -> int:
    try:
        a = int(start)
        b = int(end)
        return {"starting_version": a, "ending_version":b}
    except ValueError as ae:
        a = datetime.fromisoformat(start)
        b = datetime.fromisoformat(end)
        return {"starting_timestamp": a, "ending_timestamp":b}

# print(change_params(start = startv, end = endv))
# print(change_params(start = startt, end = endt))

c = iter([0,1,2,3,4,5,6,7,8,9])
for i in c:
    j = next(c)
    print(f"{i} {j}")