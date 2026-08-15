import os
from dotenv import load_dotenv, find_dotenv
import mysql.connector

dotenv_path = find_dotenv('.env', raise_error_if_not_found=False)
load_dotenv(dotenv_path, override=True)

host = os.getenv('DB_HOST', 'localhost')
user = os.getenv('DB_USER', 'root')
password = os.getenv('DB_PASSWORD')
database = os.getenv('DB_NAME', 'healthcare_db')

conn = mysql.connector.connect(host=host, user=user, password=password, database=database)
cursor = conn.cursor(dictionary=True)

tables = ['users', 'patients', 'predictions']

print('DATABASE:', database)
print('CONNECTED:', conn.is_connected())
print('')
for table in tables:
    print('TABLE:', table)
    cursor.execute("SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_KEY, EXTRA, COLUMN_DEFAULT FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s ORDER BY ORDINAL_POSITION", (database, table))
    cols = cursor.fetchall()
    if not cols:
        print('  MISSING TABLE')
        print('')
        continue
    for col in cols:
        print('  {name} | {type} | nullable={null} | key={key} | extra={extra} | default={default}'.format(
            name=col['COLUMN_NAME'],
            type=col['COLUMN_TYPE'],
            null=col['IS_NULLABLE'],
            key=col['COLUMN_KEY'],
            extra=col['EXTRA'],
            default=col['COLUMN_DEFAULT']))
    cursor.execute("SELECT CONSTRAINT_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME FROM information_schema.KEY_COLUMN_USAGE WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND REFERENCED_TABLE_NAME IS NOT NULL", (database, table))
    fks = cursor.fetchall()
    if fks:
        print('  FOREIGN KEYS:')
        for fk in fks:
            print('    {cn} references {rt}({rc}) via {name}'.format(
                cn=fk['COLUMN_NAME'], rt=fk['REFERENCED_TABLE_NAME'], rc=fk['REFERENCED_COLUMN_NAME'], name=fk['CONSTRAINT_NAME']))
    cursor.execute("SELECT INDEX_NAME, NON_UNIQUE, SEQ_IN_INDEX, COLUMN_NAME FROM information_schema.STATISTICS WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s ORDER BY INDEX_NAME, SEQ_IN_INDEX", (database, table))
    idxs = cursor.fetchall()
    if idxs:
        print('  INDEXES:')
        current = None
        for idx in idxs:
            if idx['INDEX_NAME'] != current:
                current = idx['INDEX_NAME']
                print('    {name} (unique={uq})'.format(name=current, uq=idx['NON_UNIQUE'] == 0))
            print('      seq={seq} col={col}'.format(seq=idx['SEQ_IN_INDEX'], col=idx['COLUMN_NAME']))
    print('')

cursor.close()
conn.close()
