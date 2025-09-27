"""
Database module for ID Card Photo Machine
Handles SQLite database operations and migrations
"""
import sqlite3
import os
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from contextlib import contextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages SQLite database operations and migrations"""

    def __init__(self, db_path: str = "data/photoid_studio.db"):
        self.db_path = db_path
        self.ensure_db_directory()
        self.init_database()

    def ensure_db_directory(self):
        """Ensure the database directory exists"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            logger.info(f"Created database directory: {db_dir}")

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def init_database(self):
        """Initialize database with tables if they don't exist"""
        try:
            with self.get_connection() as conn:
                # Check if tables exist
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT name FROM sqlite_master
                    WHERE type='table' AND name IN ('app_configs', 'users', 'photo_histories', 'request_histories')
                """)
                existing_tables = [row[0] for row in cursor.fetchall()]

                if len(existing_tables) < 4:
                    logger.info("Creating database tables...")
                    self.create_tables(conn)
                    logger.info("Database tables created successfully")
                else:
                    logger.info("Database tables already exist")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    def create_tables(self, conn: sqlite3.Connection):
        """Create all database tables"""
        cursor = conn.cursor()

        # Create app_configs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS app_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                value TEXT
            )
        """)

        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                npk TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                password TEXT,
                role TEXT,
                section_id TEXT,
                section_name TEXT,
                department_id TEXT,
                department_name TEXT,
                company TEXT,
                plant TEXT,
                last_access DATETIME,
                last_take_photo DATETIME,
                photo_filename TEXT,
                card_filename TEXT
            )
        """)

        # Create photo_histories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS photo_histories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                npk TEXT NOT NULL,
                photo_time DATETIME NOT NULL,
                FOREIGN KEY (npk) REFERENCES users (npk) ON DELETE CASCADE
            )
        """)

        # Create request_histories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS request_histories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                npk TEXT NOT NULL,
                request_time DATETIME NOT NULL,
                request_desc TEXT,
                status TEXT,
                remark TEXT,
                respons_time DATETIME,
                respons_name TEXT,
                FOREIGN KEY (npk) REFERENCES users (npk) ON DELETE CASCADE
            )
        """)

        # Create indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_photo_histories_npk ON photo_histories (npk)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_photo_histories_time ON photo_histories (photo_time)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_request_histories_npk ON request_histories (npk)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_request_histories_time ON request_histories (request_time)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_role ON users (role)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_section ON users (section_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_department ON users (department_id)")

        conn.commit()

    def execute_query(self, query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results as list of dictionaries"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise

    def execute_update(self, query: str, params: Tuple = ()) -> int:
        """Execute an INSERT/UPDATE/DELETE query and return affected rows count"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            logger.error(f"Update execution failed: {e}")
            raise

    def get_user_by_npk(self, npk: str) -> Optional[Dict[str, Any]]:
        """Get user by NPK"""
        results = self.execute_query("SELECT * FROM users WHERE npk = ?", (npk,))
        return results[0] if results else None

    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users"""
        return self.execute_query("SELECT * FROM users ORDER BY name")

    def create_user(self, user_data: Dict[str, Any]) -> bool:
        """Create a new user"""
        try:
            query = """
                INSERT INTO users (npk, name, password, role, section_id, section_name,
                                 department_id, department_name, company, plant,
                                 last_access, last_take_photo, photo_filename, card_filename)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (
                user_data.get('npk'),
                user_data.get('name'),
                user_data.get('password'),
                user_data.get('role'),
                user_data.get('section_id'),
                user_data.get('section_name'),
                user_data.get('department_id'),
                user_data.get('department_name'),
                user_data.get('company'),
                user_data.get('plant'),
                user_data.get('last_access'),
                user_data.get('last_take_photo'),
                user_data.get('photo_filename'),
                user_data.get('card_filename')
            )
            self.execute_update(query, params)
            return True
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            return False

    def update_user(self, npk: str, user_data: Dict[str, Any]) -> bool:
        """Update user information"""
        try:
            # Build dynamic update query
            set_clauses = []
            params = []

            for key, value in user_data.items():
                if key != 'npk' and value is not None:
                    set_clauses.append(f"{key} = ?")
                    params.append(value)

            if not set_clauses:
                return False

            params.append(npk)
            query = f"UPDATE users SET {', '.join(set_clauses)} WHERE npk = ?"
            self.execute_update(query, tuple(params))
            return True
        except Exception as e:
            logger.error(f"Failed to update user: {e}")
            return False

    def add_photo_history(self, npk: str, photo_time: datetime = None) -> bool:
        """Add photo history record"""
        try:
            if photo_time is None:
                photo_time = datetime.now()

            query = "INSERT INTO photo_histories (npk, photo_time) VALUES (?, ?)"
            self.execute_update(query, (npk, photo_time))
            return True
        except Exception as e:
            logger.error(f"Failed to add photo history: {e}")
            return False

    def add_request_history(self, npk: str, request_desc: str, status: str = "pending",
                          remark: str = None, respons_name: str = None) -> bool:
        """Add request history record"""
        try:
            request_time = datetime.now()
            query = """
                INSERT INTO request_histories (npk, request_time, request_desc, status, remark, respons_name)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            self.execute_update(query, (npk, request_time, request_desc, status, remark, respons_name))
            return True
        except Exception as e:
            logger.error(f"Failed to add request history: {e}")
            return False

    def get_photo_histories(self, npk: str = None) -> List[Dict[str, Any]]:
        """Get photo histories, optionally filtered by NPK"""
        if npk:
            return self.execute_query(
                "SELECT * FROM photo_histories WHERE npk = ? ORDER BY photo_time DESC",
                (npk,)
            )
        return self.execute_query("SELECT * FROM photo_histories ORDER BY photo_time DESC")

    def get_request_histories(self, npk: str = None) -> List[Dict[str, Any]]:
        """Get request histories, optionally filtered by NPK"""
        if npk:
            return self.execute_query(
                "SELECT * FROM request_histories WHERE npk = ? ORDER BY request_time DESC",
                (npk,)
            )
        return self.execute_query("SELECT * FROM request_histories ORDER BY request_time DESC")

    def get_app_config(self, name: str) -> Optional[str]:
        """Get application configuration value"""
        results = self.execute_query("SELECT value FROM app_configs WHERE name = ?", (name,))
        return results[0]['value'] if results else None

    def set_app_config(self, name: str, value: str) -> bool:
        """Set application configuration value"""
        try:
            query = """
                INSERT OR REPLACE INTO app_configs (name, value)
                VALUES (?, ?)
            """
            self.execute_update(query, (name, value))
            return True
        except Exception as e:
            logger.error(f"Failed to set app config: {e}")
            return False

    def backup_database(self, backup_path: str) -> bool:
        """Create a backup of the database"""
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"Database backed up to: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to backup database: {e}")
            return False

# Global database manager instance
db_manager = DatabaseManager()
