"""Create and verify the Healthcare Analytics database."""

import os
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv
from mysql.connector import Error


PROJECT_ROOT = Path(__file__).resolve().parent
SCHEMA_FILE = PROJECT_ROOT / "healthcare_schema.sql"
REQUIRED_TABLES = {"users", "patients", "predictions", "admin"}


def get_database_settings():
    """Load database settings from the project root .env file."""
    load_dotenv(PROJECT_ROOT / ".env")

    settings = {
        "host": os.getenv("DB_HOST", "localhost").strip(),
        "user": os.getenv("DB_USER", "root").strip(),
        "password": os.getenv("DB_PASSWORD"),
        "database": os.getenv("DB_NAME", "healthcare_db").strip(),
        "port": int(os.getenv("DB_PORT", "3306")),
    }

    if not settings["password"]:
        raise RuntimeError("DB_PASSWORD is missing from the project .env file.")

    return settings


def schema_statements():
    """Return executable SQL statements from healthcare_schema.sql."""
    schema_text = SCHEMA_FILE.read_text(encoding="utf-8")
    schema_without_comments = "\n".join(
        line for line in schema_text.splitlines()
        if not line.strip().startswith("--")
    )
    return [
        statement.strip()
        for statement in schema_without_comments.split(";")
        if statement.strip()
    ]


def main():
    settings = get_database_settings()
    server_settings = {
        key: settings[key]
        for key in ("host", "user", "password", "port")
    }

    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(**server_settings)
        cursor = connection.cursor()
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS `{settings['database']}` "
            "DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        connection.commit()
        cursor.close()
        connection.close()

        connection = mysql.connector.connect(**settings)
        cursor = connection.cursor()
        skipped_duplicates = 0

        for statement in schema_statements():
            try:
                cursor.execute(statement)
                connection.commit()
            except Error as error:
                if error.errno in (1061, 1062):
                    skipped_duplicates += 1
                    connection.rollback()
                    continue
                raise

        cursor.execute("SHOW TABLES")
        tables = {row[0] for row in cursor.fetchall()}
        missing_tables = REQUIRED_TABLES - tables

        if missing_tables:
            missing = ", ".join(sorted(missing_tables))
            raise RuntimeError(f"Database setup is incomplete. Missing tables: {missing}")

        print(f"Database '{settings['database']}' is ready.")
        print("Tables found:")
        for table in sorted(tables):
            print(f"- {table}")
        if skipped_duplicates:
            print(f"Skipped {skipped_duplicates} already-existing duplicate object or record(s).")
        print("Required tables users, patients, predictions, and admin were verified successfully.")
    except (Error, OSError, ValueError, RuntimeError) as error:
        print(f"Database setup failed: {error}")
        raise SystemExit(1) from error
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


if __name__ == "__main__":
    main()