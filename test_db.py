"""
Comprehensive Database Diagnostic Script for Healthcare Analytics
Tests MySQL connectivity, database setup, and registration prerequisites
"""

import os
from dotenv import load_dotenv, find_dotenv
import mysql.connector
from mysql.connector import Error

def print_header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

# ========== Step 1: Load Environment Variables ==========
print_header("Step 1: Environment Variables")

dotenv_path = find_dotenv('.env', raise_error_if_not_found=False)
loaded = load_dotenv(dotenv_path)
print(f"✓ .env loaded: {loaded}")
print(f"  Path: {dotenv_path}")

host = os.getenv('DB_HOST', 'localhost')
user = os.getenv('DB_USER', 'root')
password = os.getenv('DB_PASSWORD')
database = os.getenv('DB_NAME', 'healthcare_db')

print(f"\n✓ Environment Variables:")
print(f"  DB_HOST:     {host!r}")
print(f"  DB_USER:     {user!r}")
print(f"  DB_PASSWORD: {'SET' if password else 'NOT SET'}")
print(f"  DB_NAME:     {database!r}")

if not password:
    print("\n⚠️  WARNING: DB_PASSWORD is not set in .env!")
    print("   This will cause connection to fail.")

# ========== Step 2: Test MySQL Connection ==========
print_header("Step 2: MySQL Connection Test")

conn = None
cursor = None

try:
    print("Attempting connection with provided credentials...")
    print(f"  Host: {host}")
    print(f"  User: {user}")
    print(f"  Database: {database}")
    
    conn = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    
    if conn.is_connected():
        print("\n✓ MySQL connection successful!")
        print(f"  Connection: {conn}")
        cursor = conn.cursor(dictionary=True)
    else:
        print("\n✗ Connection object created but not active")
        
except Error as e:
    error_code = getattr(e, 'errno', 'Unknown')
    error_msg = getattr(e, 'msg', str(e))
    print(f"\n✗ Connection failed [{error_code}]:")
    print(f"  Error: {error_msg}")
    print("\n  Possible causes:")
    if error_code == 1045:
        print("    - Invalid username or password")
        print("    - User does not have privileges on the database")
    elif error_code == 1049:
        print("    - Database does not exist")
        print("    - Create it with: CREATE DATABASE healthcare_db;")
    elif error_code == 2003:
        print("    - MySQL server is not running")
        print("    - Start it with: sudo service mysql start")
    print("\n  Check Flask console for detailed error output.")

# ========== Step 3: Database & Tables Check ==========
if cursor:
    print_header("Step 3: Database & Tables Structure")
    
    try:
        # Check current database
        cursor.execute("SELECT DATABASE()")
        current_db = cursor.fetchone()
        print(f"✓ Current database: {current_db}")
        
        # List all databases
        cursor.execute("SHOW DATABASES")
        databases = [row['Database'] for row in cursor.fetchall()]
        print(f"\n✓ Available databases:")
        for db in databases:
            marker = " ← TARGET" if db == database else ""
            print(f"  - {db}{marker}")
        
        if database not in databases:
            print(f"\n✗ WARNING: Database '{database}' not found!")
            print(f"   Create it with:\n   CREATE DATABASE IF NOT EXISTS {database};")
        
        # Check tables in target database
        print(f"\n✓ Tables in '{database}':")
        cursor.execute("SHOW TABLES")
        tables = [row[f'Tables_in_{database}'] for row in cursor.fetchall()]
        
        if not tables:
            print(f"  ✗ No tables found!")
            print(f"   Run healthcare_schema.sql to create tables")
        else:
            for table in tables:
                print(f"  - {table}")
        
        # Check users table schema if it exists
        if 'users' in tables:
            print(f"\n✓ 'users' table schema:")
            cursor.execute("DESCRIBE users")
            columns = cursor.fetchall()
            for col in columns:
                col_name = col['Field']
                col_type = col['Type']
                null_able = col['Null']
                key = col['Key']
                print(f"  - {col_name:20} {col_type:30} NULL={null_able} KEY={key}")
        else:
            print(f"\n✗ 'users' table not found!")
            print(f"   Run healthcare_schema.sql to create it")
    
    except Error as e:
        print(f"✗ Error querying database: {e}")

# ========== Step 4: Test User Insert (Like Registration) ==========
if cursor:
    print_header("Step 4: Test User Registration Insert")
    
    try:
        # Check if users table exists
        cursor.execute("SHOW TABLES LIKE 'users'")
        if not cursor.fetchone():
            print("✗ 'users' table does not exist")
            print("  Cannot test insertion without table")
        else:
            print("✓ 'users' table exists")
            
            # Try a test insert
            test_email = 'test@healthcare-debug.com'
            test_username = 'testuser'
            test_password = 'hashed_password_hash_here'
            
            try:
                insert_query = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
                cursor.execute(insert_query, (test_username, test_email, test_password))
                conn.commit()
                print(f"\n✓ Test insert successful!")
                print(f"  Inserted: username='{test_username}', email='{test_email}'")
                
                # Verify the insert
                cursor.execute("SELECT * FROM users WHERE email = %s", (test_email,))
                user = cursor.fetchone()
                if user:
                    print(f"\n✓ Verification successful!")
                    print(f"  User ID: {user.get('id')}")
                    print(f"  Username: {user.get('username')}")
                    print(f"  Email: {user.get('email')}")
                
                # Clean up test record
                cursor.execute("DELETE FROM users WHERE email = %s", (test_email,))
                conn.commit()
                print(f"\n✓ Cleaned up test record")
                
            except Error as e:
                error_code = getattr(e, 'errno', 'Unknown')
                error_msg = getattr(e, 'msg', str(e))
                print(f"\n✗ Insert failed [{error_code}]: {error_msg}")
                if error_code == 1364:
                    print("  - Missing required column in INSERT")
                elif error_code == 1062:
                    print("  - Duplicate entry (email or username already exists)")
    
    except Error as e:
        print(f"✗ Error during test insert: {e}")

# ========== Step 5: Summary & Next Steps ==========
print_header("Step 5: Summary & Next Steps")

if conn and conn.is_connected():
    print("✓ DATABASE CONNECTION: SUCCESS")
else:
    print("✗ DATABASE CONNECTION: FAILED")

print("\nNext steps if registration is failing:")
print("  1. Check Flask console for detailed database error logs")
print("  2. Verify MySQL credentials in .env match your database")
print("  3. Ensure healthcare_db database exists")
print("  4. Verify users table schema matches the code")
print("  5. Check that your MySQL user has INSERT privilege on healthcare_db.users")

print("\nSQL commands to verify manually:")
print("  SHOW DATABASES;")
print("  USE healthcare_db;")
print("  SHOW TABLES;")
print("  DESCRIBE users;")
print("  SELECT * FROM users;")

# Cleanup
if cursor:
    cursor.close()
if conn and conn.is_connected():
    conn.close()
    print("\n✓ Connection closed")
