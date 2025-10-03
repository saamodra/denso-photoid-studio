# Database Setup Guide

This guide explains how to set up and use the SQLite database for the ID Card Photo Machine application.

## Database Schema

The database follows the Entity-Relationship Diagram (ERD) with the following tables:

### Tables

1. **`app_configs`** - Application configuration settings
   - `id` (INTEGER, PRIMARY KEY)
   - `name` (TEXT, UNIQUE) - Configuration key
   - `value` (TEXT) - Configuration value

2. **`users`** - User information
   - `npk` (TEXT, PRIMARY KEY) - Employee number
   - `name` (TEXT) - Full name
   - `password` (TEXT) - Encrypted password
   - `role` (TEXT) - User role (admin, user, supervisor)
   - `section_id` (TEXT) - Section identifier
   - `section_name` (TEXT) - Section name
   - `department_id` (TEXT) - Department identifier
   - `department_name` (TEXT) - Department name
   - `company` (TEXT) - Company name
   - `plant` (TEXT) - Plant location
   - `last_access` (DATETIME) - Last access time
   - `last_take_photo` (DATETIME) - Last photo capture time
   - `photo_filename` (TEXT) - Current photo filename
   - `card_filename` (TEXT) - Current card filename

3. **`photo_histories`** - Photo capture history
   - `id` (INTEGER, PRIMARY KEY)
   - `npk` (TEXT, FOREIGN KEY) - References users.npk
   - `photo_time` (DATETIME) - Photo capture timestamp

4. **`request_histories`** - Request tracking
   - `id` (INTEGER, PRIMARY KEY)
   - `npk` (TEXT, FOREIGN KEY) - References users.npk
   - `request_time` (DATETIME) - Request timestamp
   - `request_desc` (TEXT) - Request description
   - `status` (TEXT) - Request status (requested, approved, rejected)
   - `remark` (TEXT) - Additional remarks
   - `respons_time` (DATETIME) - Response timestamp
   - `respons_name` (TEXT) - Responder name

## Quick Start

### 1. Initialize Database

```bash
# Run the database initialization script
python scripts/init_database.py
```

This will:
- Create the database file at `data/photoid_studio.db`
- Run all pending migrations
- Set up the initial schema

### 2. Insert Sample Data (Optional)

```bash
# Insert sample data for testing
python scripts/insert_sample_data.py
```

This will create sample users, photo histories, and request histories.

### 3. Test Database

```bash
# Run database tests
python test_database.py

# View database schema
python test_database.py schema
```

## Database Management

### Using the Database Manager

```python
from modules.database import db_manager

# Get all users
users = db_manager.get_all_users()

# Get user by NPK
user = db_manager.get_user_by_npk('EMP001')

# Create new user
user_data = {
    'npk': 'EMP006',
    'name': 'New Employee',
    'role': 'user',
    'section_id': 'SEC001',
    'section_name': 'IT Department',
    # ... other fields
}
db_manager.create_user(user_data)

# Add photo history
db_manager.add_photo_history('EMP001', datetime.now())

# Add request history
db_manager.add_request_history('EMP001', 'Card replacement request', 'requested')

# Get application configuration
value = db_manager.get_app_config('app_name')

# Set application configuration
db_manager.set_app_config('maintenance_mode', 'false')
```

### Migration Management

```python
from migrations.migration_manager import MigrationManager

# Initialize migration manager
migration_manager = MigrationManager()

# Run all pending migrations
migration_manager.run_migrations()

# Get migration status
status = migration_manager.get_migration_status()
print(f"Applied: {status['applied_count']}, Pending: {status['pending_count']}")

# Rollback a migration
migration_manager.rollback_migration('001_initial_schema')
```

## File Structure

```
denso-photoid-studio/
├── data/
│   └── photoid_studio.db          # SQLite database file
├── migrations/
│   ├── __init__.py
│   ├── migration_manager.py       # Migration management
│   └── 001_initial_schema.py     # Initial schema migration
├── modules/
│   └── database.py                # Database manager
├── scripts/
│   ├── init_database.py          # Database initialization
│   └── insert_sample_data.py     # Sample data insertion
└── test_database.py              # Database testing
```

## Configuration

Database settings are configured in `config.py`:

```python
DATABASE_SETTINGS = {
    'db_path': 'data/photoid_studio.db',
    'backup_path': 'data/backups',
    'max_connections': 10,
    'timeout': 30.0
}
```

## Backup and Recovery

### Create Backup

```python
from modules.database import db_manager

# Create backup
backup_path = f"data/backups/backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
db_manager.backup_database(backup_path)
```

### Restore from Backup

```python
import shutil

# Restore from backup
shutil.copy2('data/backups/backup_20231201_120000.db', 'data/photoid_studio.db')
```

## Troubleshooting

### Common Issues

1. **Database file not found**
   - Ensure the `data/` directory exists
   - Run `python scripts/init_database.py`

2. **Migration errors**
   - Check migration files in `migrations/` directory
   - Verify migration syntax and dependencies

3. **Permission errors**
   - Ensure write permissions for the `data/` directory
   - Check file ownership

### Debugging

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

View database schema:

```bash
python test_database.py schema
```

Check migration status:

```python
from migrations.migration_manager import MigrationManager
mm = MigrationManager()
status = mm.get_migration_status()
print(status)
```

## Performance Considerations

- Indexes are created on frequently queried columns
- Foreign key constraints are enforced
- Connection pooling is handled automatically
- Use transactions for bulk operations

## Security Notes

- Passwords should be hashed before storage
- Use parameterized queries to prevent SQL injection
- Regular backups are recommended
- Consider encryption for sensitive data
