# Session Management System

This document describes the session management system implemented for the Denso Photo ID Studio application.

## Overview

The session management system provides:
- **User Session Tracking**: Maintains current user information throughout the application
- **Login State Management**: Tracks whether a user is logged in
- **User Context**: Provides easy access to current user data
- **Photo Association**: Links captured photos to the current user
- **Logout Functionality**: Properly cleans up sessions

## Architecture

### Components

1. **SessionManager** (`modules/session_manager.py`)
   - Core session management class
   - Handles login/logout operations
   - Provides user information access
   - Manages photo information updates

2. **Main Application** (`main.py`)
   - Integrates session manager with UI
   - Handles session lifecycle
   - Passes user data to windows

3. **Main Window** (`ui/main_window.py`)
   - Displays current user information
   - Provides logout functionality
   - Updates user info when session changes

## Features

### Session Management
- **Login**: Start a new user session with user data
- **Logout**: End current session and clear user data
- **Session Tracking**: Monitor login time and session duration
- **User Context**: Access current user information anywhere in the app

### User Information Display
- **Current User Panel**: Shows user name, NPK, role, and department
- **Real-time Updates**: Updates when user changes
- **Logout Button**: Allows user to logout with confirmation

### Photo Association
- **Automatic Linking**: Photos are automatically linked to current user
- **Database Updates**: User's photo information is updated in database
- **Photo History**: Tracks when user last took photos

## Usage

### Starting a Session
```python
from modules.session_manager import session_manager

# Login user (typically called after authentication)
user_data = {
    'npk': 'USER001',
    'name': 'John Doe',
    'role': 'user',
    'department_name': 'Manufacturing'
}

success = session_manager.login(user_data)
if success:
    print("User logged in successfully")
```

### Accessing User Information
```python
# Get current user data
current_user = session_manager.get_current_user()

# Get specific user information
npk = session_manager.get_user_npk()
name = session_manager.get_user_name()
role = session_manager.get_user_role()
department = session_manager.get_user_department()

# Check permissions
can_take_photos = session_manager.can_take_photos()
is_admin = session_manager.is_admin()
can_access_admin = session_manager.can_access_admin()
```

### Updating Photo Information
```python
# Update user's photo information
success = session_manager.update_user_photo_info(
    photo_filename="photo_123.jpg",
    card_filename="id_card_123.jpg"  # optional
)
```

### Ending a Session
```python
# Logout user
success = session_manager.logout()
if success:
    print("User logged out successfully")
```

## UI Integration

### Main Window User Panel
The main window displays a user information panel that shows:
- User name with icon
- NPK (Employee ID)
- Role (Admin, User, Manager)
- Department name
- Logout button

### Session State Display
```python
# Update user info display in UI
def update_user_info(self):
    current_user = session_manager.get_current_user()
    if current_user:
        self.user_name_label.setText(f"👤 {current_user['name']}")
        self.user_npk_label.setText(f"NPK: {current_user['npk']}")
        # ... update other labels
```

## Database Integration

### User Photo Updates
When photos are captured, the system automatically:
1. Gets current user from session
2. Updates user's photo filename in database
3. Records last photo capture time
4. Links photos to user for tracking

### Session Persistence
- User data is stored in memory during session
- Database is updated when photos are captured
- Session ends when user logs out
- No persistent session storage (user must login each time)

## Security Considerations

### Session Security
- Sessions are stored in memory only
- No persistent session tokens
- Automatic logout when application closes
- User must re-authenticate for new sessions

### Data Protection
- User passwords are not stored in session
- Only necessary user information is kept in memory
- Sensitive data is cleared on logout

## Error Handling

### Session Errors
- Invalid user data handling
- Database update failures
- Session state validation
- Graceful error recovery

### UI Error Handling
- User info display errors
- Logout confirmation
- Session state validation
- Error message display

## Testing

### Test Coverage
The system includes comprehensive tests for:
- Session creation and management
- User information access
- Photo information updates
- Database integration
- Session persistence
- Logout functionality

### Running Tests
```bash
python test_session_system.py
```

## Configuration

### Session Settings
- Session timeout: Not implemented (can be added)
- Auto-logout: Not implemented (can be added)
- Session validation: Basic validation only

### User Permissions
- Photo capture: All logged-in users
- Admin access: Admin and Manager roles
- Database updates: All logged-in users

## Future Enhancements

### Planned Features
- [ ] Session timeout functionality
- [ ] Auto-logout after inactivity
- [ ] Session validation on each operation
- [ ] Multiple concurrent sessions
- [ ] Session history tracking
- [ ] Advanced permission system

### Security Improvements
- [ ] Session token validation
- [ ] Encrypted session storage
- [ ] Session audit logging
- [ ] Automatic session cleanup

## Troubleshooting

### Common Issues

1. **User Info Not Displaying**
   - Check if user is logged in: `session_manager.is_logged_in`
   - Verify user data: `session_manager.get_current_user()`
   - Update UI: `main_window.update_user_info()`

2. **Photos Not Linked to User**
   - Verify session is active
   - Check database connection
   - Ensure photo filename is valid

3. **Logout Not Working**
   - Check signal connections
   - Verify session manager state
   - Check for UI errors

### Debug Information
```python
# Get complete session information
session_info = session_manager.get_session_info()
print(f"Session Info: {session_info}")

# Check user permissions
print(f"Can take photos: {session_manager.can_take_photos()}")
print(f"Is admin: {session_manager.is_admin()}")
```

## API Reference

### SessionManager Methods

#### Session Management
- `login(user_data)`: Start new session
- `logout()`: End current session
- `is_logged_in`: Check login state

#### User Information
- `get_current_user()`: Get complete user data
- `get_user_npk()`: Get user NPK
- `get_user_name()`: Get user name
- `get_user_role()`: Get user role
- `get_user_department()`: Get department name

#### Permissions
- `can_take_photos()`: Check photo permission
- `is_admin()`: Check admin role
- `is_manager()`: Check manager role
- `can_access_admin()`: Check admin access

#### Photo Management
- `update_user_photo_info(photo_filename, card_filename)`: Update photo info

#### Session Information
- `get_session_duration()`: Get session duration
- `get_user_display_info()`: Get formatted user info
- `get_session_info()`: Get complete session data
