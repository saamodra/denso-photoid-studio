# Authentication System

This document describes the database-based authentication system implemented for the Denso Photo ID Studio application.

## Overview

The authentication system uses:
- **Database storage**: User credentials are stored in SQLite database
- **Password encryption**: Passwords are hashed using PBKDF2 with SHA-256
- **Secure authentication**: No plain text passwords are stored
- **User management**: Support for different user roles and departments

## Features

### Security
- **Password Hashing**: Uses PBKDF2 with SHA-256 and 100,000 iterations
- **Salt Generation**: Each password has a unique random salt
- **Secure Comparison**: Uses constant-time comparison to prevent timing attacks
- **No Plain Text Storage**: Passwords are never stored in plain text

### User Management
- **User Roles**: admin, user, manager
- **Department Support**: Users belong to sections and departments
- **Last Access Tracking**: Records when users last logged in
- **User Search**: Search users by name or NPK

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    npk TEXT PRIMARY KEY,           -- Employee ID (Primary Key)
    name TEXT NOT NULL,             -- Full name
    password TEXT,                  -- Hashed password
    role TEXT,                      -- User role (admin, user, manager)
    section_id TEXT,                -- Section identifier
    section_name TEXT,              -- Section name
    department_id TEXT,             -- Department identifier
    department_name TEXT,           -- Department name
    company TEXT,                   -- Company name
    plant TEXT,                     -- Plant location
    last_access DATETIME,           -- Last login time
    last_take_photo DATETIME,       -- Last photo taken
    photo_filename TEXT,            -- Photo file name
    card_filename TEXT              -- ID card file name
);
```

## Usage

### Authentication
```python
from modules.database import db_manager

# Authenticate user
user = db_manager.authenticate_user("ADMIN001", "admin123")
if user:
    print(f"Welcome, {user['name']}!")
else:
    print("Authentication failed")
```

### Creating Users
```python
# Create user with encrypted password
user_data = {
    'npk': 'USER001',
    'name': 'John Doe',
    'role': 'user',
    'section_id': 'PROD',
    'section_name': 'Production',
    'department_id': 'MFG',
    'department_name': 'Manufacturing',
    'company': 'Denso',
    'plant': 'Plant 1'
}

success = db_manager.create_user_with_password(user_data, "password123")
```

### Password Management
```python
# Update user password
db_manager.update_user_password("USER001", "new_password")

# Reset user password (admin function)
db_manager.reset_user_password("USER001", "reset_password")
```

## Sample Users

The system comes with sample users for testing:

| NPK | Name | Role | Password |
|-----|------|------|----------|
| ADMIN001 | Administrator | admin | admin123 |
| USER001 | John Doe | user | user123 |
| USER002 | Jane Smith | user | password123 |
| MANAGER001 | Manager User | manager | manager123 |

## Security Considerations

### Password Requirements
- No minimum length enforced (can be added)
- No complexity requirements (can be added)
- No password history (can be added)

### Recommendations
1. **Change Default Passwords**: Change all default passwords in production
2. **Password Policy**: Implement password complexity requirements
3. **Account Lockout**: Add account lockout after failed attempts
4. **Session Management**: Implement proper session timeouts
5. **Audit Logging**: Log all authentication attempts

## File Structure

```
modules/
├── auth.py              # Authentication and password hashing
├── database.py          # Database operations and user management
ui/
├── login_window.py      # Login UI with database integration
scripts/
├── create_sample_users_auto.py  # Script to create sample users
test_auth.py             # Authentication system tests
```

## Testing

Run the authentication tests:
```bash
python test_auth.py
```

Test the login UI:
```bash
python test_login_ui.py
```

Create sample users:
```bash
python scripts/create_sample_users_auto.py
```

## Dependencies

- `cryptography>=41.0.0` - For password hashing and encryption
- `sqlite3` - Database (built-in Python module)
- `PyQt6` - UI framework

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Initialize database:
```bash
python scripts/init_database.py
```

3. Create sample users:
```bash
python scripts/create_sample_users_auto.py
```

## Troubleshooting

### Common Issues

1. **Import Error**: Make sure cryptography is installed
2. **Database Error**: Check database file permissions
3. **Authentication Failed**: Verify user exists and password is correct

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

- [ ] Password complexity requirements
- [ ] Account lockout after failed attempts
- [ ] Password expiration
- [ ] Two-factor authentication
- [ ] LDAP integration
- [ ] Session management
- [ ] Audit logging
- [ ] Password reset functionality
