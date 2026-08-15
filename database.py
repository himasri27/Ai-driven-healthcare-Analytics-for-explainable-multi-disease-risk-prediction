"""
Database Configuration and Connection Module
Handles MySQL database connectivity and operations
"""

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv, find_dotenv

# Load environment variables from the project root .env file
dotenv_path = find_dotenv('.env', raise_error_if_not_found=False)
loaded = load_dotenv(dotenv_path, override=True)
print(f"dotenv load path={dotenv_path}, loaded={loaded}")

def _clean_env(value):
    return value.strip() if isinstance(value, str) else value

# Safe debug: report whether essential DB env vars are present (do not print password)
_db_host = _clean_env(os.getenv('DB_HOST'))
_db_user = _clean_env(os.getenv('DB_USER'))
_db_password = _clean_env(os.getenv('DB_PASSWORD'))
_db_name = _clean_env(os.getenv('DB_NAME'))
print(
    f"ENV DB_HOST={_db_host!r}, DB_USER={_db_user!r}, "
    f"DB_PASSWORD={'SET' if _db_password else 'NOT SET'}, DB_NAME={_db_name!r}"
)

class Database:
    """Database connection and operations handler"""
    
    def __init__(self):
        """Initialize database connection parameters"""
        self.host = _clean_env(os.getenv('DB_HOST', 'localhost'))
        self.user = _clean_env(os.getenv('DB_USER', 'root'))
        self.password = _clean_env(os.getenv('DB_PASSWORD'))
        self.database = _clean_env(os.getenv('DB_NAME', 'healthcare_db'))
        self.connection = None
        self.cursor = None
        self.connected = False

    def _get_connection_kwargs(self, include_database=True):
        kwargs = {
            'host': self.host,
            'user': self.user,
            'password': self.password,
        }
        if include_database:
            kwargs['database'] = self.database
        auth_plugin = _clean_env(os.getenv('DB_AUTH_PLUGIN'))
        if auth_plugin:
            kwargs['auth_plugin'] = auth_plugin
        return kwargs

    def create_database_if_missing(self):
        if not self.database:
            print('Database creation skipped: DB_NAME is missing')
            return False

        try:
            print(f"Attempting to create database '{self.database}' if it does not exist...")
            conn = mysql.connector.connect(**self._get_connection_kwargs(include_database=False))
            cursor = conn.cursor()
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{self.database}` "
                "DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
            conn.commit()
            cursor.close()
            conn.close()
            print(f"Database '{self.database}' is present or was created.")
            return True
        except Error as e:
            print(f"Failed to create database '{self.database}': {e}")
            return False

    def _ensure_connection(self):
        if self.connection and getattr(self.connection, 'is_connected', lambda: False)():
            if not self.cursor:
                self.cursor = self.connection.cursor(dictionary=True)
            return self.connection
        return None

    def connect(self):
        """
        Establish connection to MySQL database
        Returns: Connection object or None if failed
        """
        if self.user is None or self.password is None or self.database is None:
            print('Database connection error: missing DB_USER, DB_PASSWORD, or DB_NAME')
            print(
                f"DB_HOST={self.host!r}, DB_USER={self.user!r}, "
                f"DB_PASSWORD={'SET' if self.password is not None else 'NOT SET'}, "
                f"DB_NAME={self.database!r}"
            )
            return None

        existing_conn = self._ensure_connection()
        if existing_conn:
            print(f'Database connection reused: {existing_conn}')
            return existing_conn

        try:
            print(f'Attempting database connection to {self.host} as {self.user}...')
            self.connection = mysql.connector.connect(**self._get_connection_kwargs(include_database=True))
            if not self.connection or not self.connection.is_connected():
                raise Error('MySQL connector did not establish a connection')

            self.cursor = self.connection.cursor(dictionary=True)
            self.connected = True
            print(f'Database connection successful: {self.connection}')
            return self.connection
        except Error as e:
            error_code = getattr(e, 'errno', 'Unknown')
            error_msg = getattr(e, 'msg', str(e))
            print(f'Database connection error [{error_code}]: {error_msg}')

            if error_code == 1049 and self.create_database_if_missing():
                try:
                    self.connection = mysql.connector.connect(**self._get_connection_kwargs(include_database=True))
                    if self.connection and self.connection.is_connected():
                        self.cursor = self.connection.cursor(dictionary=True)
                        self.connected = True
                        print(f'Database connection successful after creating database: {self.connection}')
                        return self.connection
                except Error as retry_error:
                    retry_code = getattr(retry_error, 'errno', 'Unknown')
                    retry_msg = getattr(retry_error, 'msg', str(retry_error))
                    print(f'Retry connection error [{retry_code}]: {retry_msg}')

            print(f'Connection details: host={self.host}, user={self.user}, database={self.database}')
            self.connected = False
            self.connection = None
            self.cursor = None
            return None
    
    def disconnect(self):
        """Close database connection"""
        if self.cursor:
            try:
                self.cursor.close()
            except Exception:
                pass
        if self.connection:
            try:
                self.connection.close()
            except Exception:
                pass
        self.connected = False
        self.connection = None
        self.cursor = None
        print('Database connection closed')
    
    def execute_query(self, query, params=None):
        """
        Execute a database query
        Args:
            query: SQL query string
            params: Query parameters (tuple)
        Returns: Query result or None if failed
        """
        if not self.connection:
            print('Execute query error: connection is None')
            return False
        if not self.cursor:
            print('Execute query error: cursor is None')
            return False
        if not getattr(self.connection, 'is_connected', lambda: False)():
            print('Execute query error: connection is not active')
            return False

        try:
            print(f'Executing query: {query}')
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.connection.commit()
            print(f'Query executed successfully, rows affected: {self.cursor.rowcount}')
            return True
        except Error as e:
            error_code = getattr(e, 'errno', 'Unknown')
            error_msg = getattr(e, 'msg', str(e))
            print(f'Query execution error [{error_code}]: {error_msg}')
            print(f'Failed query: {query}')
            try:
                if self.connection and self.connection.is_connected():
                    self.connection.rollback()
            except Exception:
                pass
            return False
    
    def fetch_one(self, query, params=None):
        """
        Fetch single row from database
        Args:
            query: SQL SELECT query
            params: Query parameters (tuple)
        Returns: Dictionary with column names or None
        """
        if not self.connection or not self.cursor or not getattr(self.connection, 'is_connected', lambda: False)():
            print('Fetch error: no active database connection')
            return None

        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchone()
        except Error as e:
            print(f'Fetch error: {e}')
            return None
    
    def fetch_all(self, query, params=None):
        """
        Fetch all rows from database
        Args:
            query: SQL SELECT query
            params: Query parameters (tuple)
        Returns: List of dictionaries
        """
        if not self.connection or not self.cursor or not getattr(self.connection, 'is_connected', lambda: False)():
            print('Fetch error: no active database connection')
            return None

        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print(f'Fetch error: {e}')
            return None
    
    def insert_user(self, username, email, password):
        """Insert new user into database"""
        query = 'INSERT INTO users (username, email, password) VALUES (%s, %s, %s)'
        return self.execute_query(query, (username, email, password))
    
    def insert_patient(self, user_id, age, gender, blood_type):
        """Insert patient information"""
        query = 'INSERT INTO patients (user_id, age, gender, blood_type) VALUES (%s, %s, %s, %s)'
        return self.execute_query(query, (user_id, age, gender, blood_type))
    
    def insert_prediction(self, user_id, patient_id, disease, prediction, confidence, explanation):
        """Insert prediction record"""
        query = ('INSERT INTO predictions (user_id, patient_id, disease, prediction, confidence, explanation) '
                 'VALUES (%s, %s, %s, %s, %s, %s)')
        return self.execute_query(query, (user_id, patient_id, disease, prediction, confidence, explanation))
    
    def get_user(self, email):
        """Get user by email"""
        query = 'SELECT * FROM users WHERE email = %s'
        return self.fetch_one(query, (email,))
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        query = 'SELECT * FROM users WHERE id = %s'
        return self.fetch_one(query, (user_id,))
    
    def get_patient(self, user_id):
        """Get patient information by user ID"""
        query = 'SELECT * FROM patients WHERE user_id = %s'
        return self.fetch_one(query, (user_id,))
    
    def get_predictions(self, user_id):
        """Get all predictions for a user"""
        query = 'SELECT * FROM predictions WHERE user_id = %s ORDER BY prediction_date DESC'
        return self.fetch_all(query, (user_id,))
    
    def get_all_predictions(self):
        """Get all predictions (Admin only)"""
        query = ('SELECT p.*, u.username, u.email FROM predictions p '
                 'JOIN users u ON p.user_id = u.id '
                 'ORDER BY p.prediction_date DESC')
        return self.fetch_all(query)
    
    def get_all_users(self):
        """Get all users (Admin only)"""
        query = 'SELECT id, username, email, created_at FROM users ORDER BY created_at DESC'
        return self.fetch_all(query)
    
    def update_patient(self, user_id, age, gender, blood_type):
        """Update patient information"""
        query = 'UPDATE patients SET age = %s, gender = %s, blood_type = %s WHERE user_id = %s'
        return self.execute_query(query, (age, gender, blood_type, user_id))

# Initialize database object
db = Database()
