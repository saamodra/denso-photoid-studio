"""
Migration Manager for Database Schema Management
"""
import os
import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Any
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class MigrationManager:
    """Manages database migrations"""

    def __init__(self, db_path: str = "data/photoid_studio.db"):
        self.db_path = db_path
        self.migrations_dir = os.path.dirname(os.path.abspath(__file__))
        self.init_migration_table()

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def init_migration_table(self):
        """Initialize the migrations tracking table"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS migrations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        version TEXT NOT NULL UNIQUE,
                        name TEXT NOT NULL,
                        applied_at DATETIME NOT NULL,
                        checksum TEXT
                    )
                """)
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to initialize migration table: {e}")
            raise

    def get_applied_migrations(self) -> List[str]:
        """Get list of applied migration versions"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT version FROM migrations ORDER BY version")
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get applied migrations: {e}")
            return []

    def get_pending_migrations(self) -> List[Dict[str, Any]]:
        """Get list of pending migrations"""
        applied = set(self.get_applied_migrations())
        pending = []

        # Look for migration files in the migrations directory
        for filename in os.listdir(self.migrations_dir):
            if filename.endswith('.py') and filename != '__init__.py' and filename != 'migration_manager.py':
                version = filename.replace('.py', '')
                if version not in applied:
                    migration_path = os.path.join(self.migrations_dir, filename)
                    pending.append({
                        'version': version,
                        'filename': filename,
                        'path': migration_path
                    })

        return sorted(pending, key=lambda x: x['version'])

    def apply_migration(self, migration_info: Dict[str, Any]) -> bool:
        """Apply a single migration"""
        try:
            version = migration_info['version']
            migration_path = migration_info['path']

            # Import and execute the migration
            import importlib.util
            spec = importlib.util.spec_from_file_location(f"migration_{version}", migration_path)
            migration_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(migration_module)

            # Execute the migration
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Run the migration
                migration_module.upgrade(conn)

                # Record the migration
                cursor.execute("""
                    INSERT INTO migrations (version, name, applied_at, checksum)
                    VALUES (?, ?, ?, ?)
                """, (version, migration_info['filename'], datetime.now(), ''))

                conn.commit()
                logger.info(f"Applied migration: {version}")
                return True

        except Exception as e:
            logger.error(f"Failed to apply migration {migration_info['version']}: {e}")
            return False

    def run_migrations(self) -> bool:
        """Run all pending migrations"""
        try:
            pending = self.get_pending_migrations()

            if not pending:
                logger.info("No pending migrations")
                return True

            logger.info(f"Found {len(pending)} pending migrations")

            for migration in pending:
                if not self.apply_migration(migration):
                    logger.error(f"Migration {migration['version']} failed")
                    return False

            logger.info("All migrations completed successfully")
            return True

        except Exception as e:
            logger.error(f"Migration process failed: {e}")
            return False

    def rollback_migration(self, version: str) -> bool:
        """Rollback a specific migration"""
        try:
            migration_path = os.path.join(self.migrations_dir, f"{version}.py")

            if not os.path.exists(migration_path):
                logger.error(f"Migration file not found: {migration_path}")
                return False

            # Import and execute the rollback
            import importlib.util
            spec = importlib.util.spec_from_file_location(f"migration_{version}", migration_path)
            migration_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(migration_module)

            # Execute the rollback
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Run the rollback
                if hasattr(migration_module, 'downgrade'):
                    migration_module.downgrade(conn)
                else:
                    logger.warning(f"No downgrade function found for migration {version}")

                # Remove the migration record
                cursor.execute("DELETE FROM migrations WHERE version = ?", (version,))
                conn.commit()

                logger.info(f"Rolled back migration: {version}")
                return True

        except Exception as e:
            logger.error(f"Failed to rollback migration {version}: {e}")
            return False

    def get_migration_status(self) -> Dict[str, Any]:
        """Get current migration status"""
        applied = self.get_applied_migrations()
        pending = self.get_pending_migrations()

        return {
            'applied_count': len(applied),
            'pending_count': len(pending),
            'applied_migrations': applied,
            'pending_migrations': [m['version'] for m in pending]
        }
