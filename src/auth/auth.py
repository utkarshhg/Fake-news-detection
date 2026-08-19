

import bcrypt
from loguru import logger

from src.config import ROLES


def hash_password(password: str) -> str:
    
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    
    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8"),
        )
    except Exception as e:
        logger.error(f"Password verification failed: {e}")
        return False


def authenticate_user(username: str, password: str) -> dict:
    
    from src.database.db import get_user_by_username, update_last_login

    user = get_user_by_username(username)

    if user is None:
        return {"success": False, "user": None, "message": "User not found"}

    if not user.is_active:
        return {"success": False, "user": None, "message": "Account is deactivated"}

    if not verify_password(password, user.password_hash):
        return {"success": False, "user": None, "message": "Incorrect password"}

    
    update_last_login(user.id)

    logger.info(f"User '{username}' authenticated successfully.")
    return {"success": True, "user": user, "message": "Login successful"}


def register_user(username: str, email: str, password: str, role: str = "reporter") -> dict:
    
    from src.database.db import get_user_by_username, create_user

    
    if not username or len(username) < 3:
        return {"success": False, "user": None, "message": "Username must be at least 3 characters"}

    if not email or "@" not in email:
        return {"success": False, "user": None, "message": "Invalid email address"}

    if not password or len(password) < 6:
        return {"success": False, "user": None, "message": "Password must be at least 6 characters"}

    if role not in ROLES:
        return {"success": False, "user": None, "message": f"Invalid role. Must be one of: {ROLES}"}

    
    existing = get_user_by_username(username)
    if existing:
        return {"success": False, "user": None, "message": "Username already taken"}

    
    try:
        pw_hash = hash_password(password)
        user = create_user(username, email, pw_hash, role)
        return {"success": True, "user": user, "message": "Account created successfully!"}
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        return {"success": False, "user": None, "message": f"Registration failed: {str(e)}"}


def has_permission(user_role: str, required_role: str) -> bool:
    
    hierarchy = {"reporter": 0, "researcher": 1, "admin": 2}

    user_level = hierarchy.get(user_role, -1)
    required_level = hierarchy.get(required_role, 99)

    return user_level >= required_level
