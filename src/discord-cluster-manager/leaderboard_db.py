import psycopg2
from psycopg2 import Error
from typing import Optional

class LeaderboardDB:
    def __init__(self, host: str, database: str, user: str, password: str, port: str = "5432"):
        """Initialize database connection parameters"""
        self.connection_params = {
            "host": host,
            "database": database,
            "user": user,
            "password": password,
            "port": port
        }
        self.connection: Optional[psycopg2.extensions.connection] = None
        self.cursor: Optional[psycopg2.extensions.cursor] = None

    def connect(self) -> bool:
        """Establish connection to the database"""
        try:
            self.connection = psycopg2.connect(**self.connection_params)
            self.cursor = self.connection.cursor()
            self._create_tables()
            return True
        except Error as e:
            print(f"Error connecting to PostgreSQL: {e}")
            return False

    def disconnect(self):
        """Close database connection and cursor"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def _create_tables(self):
        """Create necessary tables if they don't exist"""
        create_table_query = """
        CREATE TABLE IF NOT EXISTS leaderboard (
            id BIGINT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            deadline TIMESTAMP NOT NULL,
            template_code TEXT NOT NULL
        );
        """

        create_submission_table_query = """
        CREATE TABLE IF NOT EXISTS submissions (
            id BIGINT PRIMARY KEY,
            leaderboard_id BIGINT NOT NULL,
            user_id BIGINT NOT NULL,
            submission_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            code TEXT NOT NULL,
            FOREIGN KEY (leaderboard_id) REFERENCES leaderboard(id)
        );
        """

        try:
            self.cursor.execute(create_table_query)
            self.cursor.execute(create_submission_table_query)
            self.connection.commit()
        except Error as e:
            print(f"Error creating table: {e}")

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
