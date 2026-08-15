# Registration Debugging Guide

## Current Status
- Flask app starts successfully
- Login page opens
- Registration page opens
- When clicking "Create Account": **"Database connection failed"**

## Root Cause Analysis

The error message is generic, but the **actual error is printed to the Flask console**. Follow these steps to find it.

---

## Step 1: Check Flask Console Output

When you get the registration error, look at your Flask console (terminal where you ran `python app.py`).

### You should see one of these error messages:

**Error 1045 - Authentication Failed**
```
Database connection error [1045]: Access denied for user 'root'@'localhost' (using password: YES)
Connection details: host=localhost, user=root, database=healthcare_db
```
**Solution:** Wrong MySQL password. Update `.env` with correct password.

**Error 1049 - Unknown Database**
```
Database connection error [1049]: Unknown database 'healthcare_db'
Connection details: host=localhost, user=root, database=healthcare_db
```
**Solution:** Database doesn't exist. Create it with SQL commands below.

**Error 1064 - SQL Syntax Error**
```
Query execution error [1064]: You have an error in your SQL syntax
Failed query: INSERT INTO users (username, email, password) VALUES (%s, %s, %s)
```
**Solution:** Table schema is incorrect. Recreate with SQL commands below.

**Error 1364 - Missing Default Value**
```
Query execution error [1364]: Field 'users.is_admin' doesn't have a default value
Failed query: INSERT INTO users (username, email, password) VALUES (%s, %s, %s)
```
**Solution:** Table missing required columns. Recreate table.

**Connection is None**
```
Execute query error: connection is None
Execute query error: cursor is None
```
**Solution:** Database never connected. Fix credentials or MySQL server.

---

## Step 2: Verify MySQL Server is Running

### Windows PowerShell:
```powershell
Get-Service MySQL80
# or
Get-Service MySQL
```

Should show: `Running`

If not running, start it:
```powershell
Start-Service MySQL80
# or
net start MySQL80
```

### Linux/Mac:
```bash
sudo service mysql status
# or
sudo systemctl status mysql
```

---

## Step 3: Verify MySQL Credentials

### Test connection manually:
```bash
mysql -u root -p
```

Enter password when prompted. If it works, your credentials are correct.

### Check what's in `.env`:
```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=hima
DB_NAME=healthcare_db
```

**Your password must match your MySQL root password.**

---

## Step 4: Check if healthcare_db Exists

### Connect to MySQL:
```bash
mysql -u root -p
```

### Run these SQL commands:
```sql
-- Show all databases
SHOW DATABASES;

-- Check if healthcare_db exists
SHOW DATABASES LIKE 'healthcare_db';
```

If `healthcare_db` is missing, create it:
```sql
CREATE DATABASE IF NOT EXISTS healthcare_db;
```

---

## Step 5: Check if users Table Exists

### Connect and select database:
```bash
mysql -u root -p
```

```sql
-- Select the healthcare database
USE healthcare_db;

-- List all tables
SHOW TABLES;

-- Check if users table exists
SHOW TABLES LIKE 'users';

-- If it exists, check its structure
DESCRIBE users;
```

---

## Step 6: Create Missing Tables

If the `users` table doesn't exist, create it with this SQL:

```sql
-- First, make sure you're in the correct database
USE healthcare_db;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create patients table
CREATE TABLE IF NOT EXISTS patients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    age INT,
    gender VARCHAR(10),
    blood_type VARCHAR(5),
    medical_history TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create predictions table
CREATE TABLE IF NOT EXISTS predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    patient_id INT,
    disease VARCHAR(100) NOT NULL,
    prediction VARCHAR(100),
    confidence FLOAT,
    explanation LONGTEXT,
    prediction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_disease (disease),
    INDEX idx_prediction_date (prediction_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Verify tables were created
SHOW TABLES;

-- Verify users table structure
DESCRIBE users;
```

---

## Step 7: Complete Debugging Checklist

Use this checklist to identify the problem:

```
[ ] 1. Flask app is running: python app.py
[ ] 2. .env file exists and has DB_PASSWORD set
[ ] 3. MySQL server is running (Get-Service MySQL80 shows "Running")
[ ] 4. MySQL credentials are correct (can login: mysql -u root -p)
[ ] 5. Database exists: SHOW DATABASES;
[ ] 6. Users table exists: USE healthcare_db; SHOW TABLES;
[ ] 7. Users table has correct columns: DESCRIBE users;
[ ] 8. Flask console shows specific error code, not generic "connection failed"
```

---

## Step 8: Run Diagnostic Test

From your project directory:

```powershell
.\.venv\Scripts\Activate.ps1
python test_db.py
```

This will:
- ✓ Test .env loading
- ✓ Test MySQL connection
- ✓ List available databases
- ✓ List tables in healthcare_db
- ✓ Show users table schema
- ✓ Test insert operation

---

## Step 9: Complete Fix Process

1. **Stop Flask app** (Ctrl+C)

2. **Verify MySQL is running**:
   ```powershell
   Get-Service MySQL80
   ```

3. **Check credentials** - make sure `.env` has correct password

4. **Create database** if missing:
   ```bash
   mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS healthcare_db;"
   ```

5. **Create tables** if missing:
   ```bash
   mysql -u root -p healthcare_db < healthcare_schema.sql
   ```

6. **Verify tables exist**:
   ```bash
   mysql -u root -p -e "USE healthcare_db; SHOW TABLES; DESCRIBE users;"
   ```

7. **Run diagnostic**:
   ```powershell
   python test_db.py
   ```

8. **Restart Flask app**:
   ```powershell
   python app.py
   ```

9. **Try registration** and check Flask console for actual error

---

## Step 10: If Still Failing

If registration still shows "Database connection failed":

1. **Look at Flask console** for the specific error message
2. **Copy the error code** (like [1045], [1049], etc.)
3. **Look at the "You should see" section above** for that error code
4. **Follow the solution** for that specific error

---

## Expected Success Output

When registration works:

**Flask Console:**
```
Attempting database connection to localhost as root...
Database connection successful: <mysql.connector.abstracts.MySQLConnectionAbstract object>
Executing query: INSERT INTO users (username, email, password) VALUES (%s, %s, %s)
Query executed successfully, rows affected: 1
```

**Browser:**
- Redirects to login page after registration
- New user can login with registered credentials

**Database:**
```sql
USE healthcare_db;
SELECT * FROM users;
-- Shows your new registered user
```

---

## Common Solutions Quick Reference

| Error | Cause | Solution |
|-------|-------|----------|
| `1045 Access denied` | Wrong password | Update `.env` with correct MySQL password |
| `1049 Unknown database` | DB doesn't exist | Run `CREATE DATABASE healthcare_db;` |
| `1364 Missing default` | Wrong table schema | Recreate users table with correct schema |
| `Connection is None` | DB never connected | Check MySQL is running and credentials work |
| `users table doesn't exist` | Tables not created | Run `SOURCE healthcare_schema.sql;` |

---

## Next Steps After Registration Works

1. Test login with new account
2. Verify user appears in database: `SELECT * FROM users;`
3. Test dashboard access
4. Verify predictions can be made and saved
5. Check prediction history loads correctly
