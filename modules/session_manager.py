"""
Session Manager for ID Card Photo Machine
Handles user sessions, login state, and user context throughout the application
"""
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from .database import db_manager

logger = logging.getLogger(__name__)

class SessionManager:
    """Manages user sessions and login state"""

    def __init__(self):
        self.current_user: Optional[Dict[str, Any]] = None
        self.login_time: Optional[datetime] = None
        self.session_id: Optional[str] = None
        self.is_logged_in: bool = False

    def login(self, user_data: Dict[str, Any]) -> bool:
        """
        Start a new user session

        Args:
            user_data: User information from authentication

        Returns:
            True if login successful, False otherwise
        """
        try:
            self.current_user = user_data
            self.login_time = datetime.now()
            self.session_id = f"session_{user_data['npk']}_{int(self.login_time.timestamp())}"
            self.is_logged_in = True

            # Update last access time in database
            db_manager.update_user(user_data['npk'], {'last_access': self.login_time})

            logger.info(f"User {user_data['name']} (NPK: {user_data['npk']}) logged in successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to start session for user {user_data.get('npk', 'Unknown')}: {e}")
            return False

    def logout(self) -> bool:
        """
        End the current user session

        Returns:
            True if logout successful, False otherwise
        """
        try:
            if self.current_user:
                logger.info(f"User {self.current_user['name']} (NPK: {self.current_user['npk']}) logged out")

            self.current_user = None
            self.login_time = None
            self.session_id = None
            self.is_logged_in = False

            return True

        except Exception as e:
            logger.error(f"Failed to logout: {e}")
            return False

    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """
        Get current logged in user data

        Returns:
            User data dictionary or None if not logged in
        """
        return self.current_user

    def get_user_npk(self) -> Optional[str]:
        """
        Get current user's NPK

        Returns:
            NPK string or None if not logged in
        """
        return self.current_user['npk'] if self.current_user else None

    def get_user_name(self) -> Optional[str]:
        """
        Get current user's name

        Returns:
            Name string or None if not logged in
        """
        return self.current_user['name'] if self.current_user else None

    def get_user_role(self) -> Optional[str]:
        """
        Get current user's role

        Returns:
            Role string or None if not logged in
        """
        return self.current_user['role'] if self.current_user else None

    def get_user_department(self) -> Optional[str]:
        """
        Get current user's department name

        Returns:
            Department name string or None if not logged in
        """
        return self.current_user['department_name'] if self.current_user else None

    def get_session_duration(self) -> Optional[float]:
        """
        Get current session duration in seconds

        Returns:
            Session duration in seconds or None if not logged in
        """
        if not self.is_logged_in or not self.login_time:
            return None

        return (datetime.now() - self.login_time).total_seconds()

    def is_admin(self) -> bool:
        """
        Check if current user is an admin

        Returns:
            True if user is admin, False otherwise
        """
        return self.get_user_role() == 'admin'

    def is_manager(self) -> bool:
        """
        Check if current user is a manager

        Returns:
            True if user is manager, False otherwise
        """
        return self.get_user_role() == 'manager'

    def can_take_photos(self) -> bool:
        """
        Check if current user can take photos

        Returns:
            True if user can take photos, False otherwise
        """
        # All logged in users can take photos
        return self.is_logged_in

    def can_access_admin(self) -> bool:
        """
        Check if current user can access admin functions

        Returns:
            True if user can access admin, False otherwise
        """
        return self.is_admin() or self.is_manager()

    def get_user_display_info(self) -> str:
        """
        Get formatted user information for display

        Returns:
            Formatted string with user information
        """
        if not self.current_user:
            return "Not logged in"

        user = self.current_user
        return f"{user['name']} ({user['npk']}) - {user['role'].title()}"

    def get_session_info(self) -> Dict[str, Any]:
        """
        Get complete session information

        Returns:
            Dictionary with session details
        """
        if not self.is_logged_in:
            return {
                'is_logged_in': False,
                'user': None,
                'login_time': None,
                'session_duration': None,
                'session_id': None
            }

        return {
            'is_logged_in': True,
            'user': self.current_user,
            'login_time': self.login_time,
            'session_duration': self.get_session_duration(),
            'session_id': self.session_id
        }

    def update_user_photo_info(self, photo_filename: str, card_filename: str = None) -> bool:
        """
        Update user's photo information in database

        Args:
            photo_filename: Name of the photo file
            card_filename: Name of the ID card file (optional)

        Returns:
            True if update successful, False otherwise
        """
        if not self.current_user:
            logger.warning("Cannot update photo info: No user logged in")
            return False

        try:
            update_data = {
                'photo_filename': photo_filename,
                'last_take_photo': datetime.now()
            }

            if card_filename:
                update_data['card_filename'] = card_filename

            success = db_manager.update_user(self.current_user['npk'], update_data)

            if success:
                # Update current user data
                self.current_user.update(update_data)
                logger.info(f"Updated photo info for user {self.current_user['npk']}")

            return success

        except Exception as e:
            logger.error(f"Failed to update photo info for user {self.current_user['npk']}: {e}")
            return False

# Global session manager instance
session_manager = SessionManager()
