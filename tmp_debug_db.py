import os
from dotenv import load_dotenv, find_dotenv
import mysql.connector

p = find_dotenv('.env', raise_error_if_not_found=False)
print('dotenv path=', repr(p))
load_dotenv(p, override=True)
for var in ['DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME', 'DB_AUTH_PLUGIN']:
    v = os.getenv(var)
    print(var, repr(v), 'len=' + str(len(v)) if v is not None else 'len=None')
    if isinstance(v, str):
        print('  chars=', [(i, repr(c), ord(c)) for i,c in enumerate(v)])

try:
    conn = mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )
    print('connected', conn.is_connected())
    conn.close()
except Exception as e:
    print('connection exception:', repr(e))
