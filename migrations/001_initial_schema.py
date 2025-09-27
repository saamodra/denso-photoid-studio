"""
Initial database schema migration
Creates all tables based on the ERD design
"""
import logging

logger = logging.getLogger(__name__)

def upgrade(conn):
    """Apply the migration"""
    cursor = conn.cursor()

    logger.info("Creating initial database schema...")

    # Create apps_config table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS apps_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            value TEXT
        )
    """)
    logger.info("Created apps_config table")

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
    logger.info("Created users table")

    # Create photo_histories table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS photo_histories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            npk TEXT NOT NULL,
            photo_time DATETIME NOT NULL,
            FOREIGN KEY (npk) REFERENCES users (npk) ON DELETE CASCADE
        )
    """)
    logger.info("Created photo_histories table")

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
    logger.info("Created request_histories table")

    # Create indexes for better performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_photo_histories_npk ON photo_histories (npk)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_photo_histories_time ON photo_histories (photo_time)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_request_histories_npk ON request_histories (npk)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_request_histories_time ON request_histories (request_time)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_role ON users (role)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_section ON users (section_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_department ON users (department_id)")
    logger.info("Created database indexes")

    # Insert default app configuration
    default_configs = [
        ('app_name', 'ID Card Photo Machine'),
        ('image_save_path', 'images'),
    ]

    for name, value in default_configs:
        cursor.execute("""
            INSERT OR IGNORE INTO apps_config (name, value)
            VALUES (?, ?)
        """, (name, value))

    logger.info("Inserted default application configurations")

    conn.commit()
    logger.info("Initial schema migration completed successfully")

def downgrade(conn):
    """Rollback the migration"""
    cursor = conn.cursor()

    logger.info("Rolling back initial schema...")

    # Drop tables in reverse order (respecting foreign key constraints)
    cursor.execute("DROP TABLE IF EXISTS request_histories")
    cursor.execute("DROP TABLE IF EXISTS photo_histories")
    cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute("DROP TABLE IF EXISTS apps_config")

    conn.commit()
    logger.info("Initial schema rollback completed")
