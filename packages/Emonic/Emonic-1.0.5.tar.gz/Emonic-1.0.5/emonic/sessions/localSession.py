import os
import json
import secrets
import hashlib
import base64
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from json import JSONEncoder
import time
import threading
import http.client
import importlib
from http.cookies import SimpleCookie

class DateTimeEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)

class SessionManager:
    """
    SessionManager provides a flexible and secure way to manage user sessions in web applications.

    Args:
        config (dict, optional): Configuration options for session management. If not provided, it attempts
            to load the configuration from a `settings.py` module in the current directory.

    Attributes:
        secret_key (str): The secret key used for session data encryption and signing.
        serializer (URLSafeTimedSerializer): Serializer for securely serializing and deserializing session data.
        session_folder (str): The folder where session data is stored.
        session_lifetime (timedelta): The default lifetime of a session.
        session_permanent (bool): If True, sessions are stored permanently until manually deleted.
        loaded_session (str): The ID of the currently loaded session.
        encryption_key (bytes, optional): The encryption key used to encrypt session data.
        timeout_handler (callable, optional): A custom handler function for timed-out sessions.
        rotate_sessions (bool): If True, sessions for the same user agent are rotated.
        fingerprint_sessions (bool): If True, sessions are fingerprinted to prevent session reuse.
        user_agent_verification (bool): If True, user agent verification is performed for sessions.
        session_id_prefix (str): A prefix added to generated session IDs.
        cookie_name (str): The name of the session cookie.
        cookie_domain (str, optional): The domain for which the session cookie is valid.
        cookie_path (str): The path within the domain for which the session cookie is valid.
        cookie_secure (bool): If True, the session cookie is marked as secure.

    Methods:
        load_config_from_settings(): Attempts to load session configuration from a `settings.py` module.
        generate_session_id(): Generates a new session ID.
        regenerate_session_id(session_id): Regenerates a new session ID for an existing session.
        save_session(data, custom_lifetime=None, session_id=None, regenerate_id=False):
            Saves session data to a file.
        load_session(session_id=None): Loads session data from a file.
        delete_session(session_id): Deletes a session and its associated file.
        renew_session(custom_lifetime=None): Extends the current session's lifetime.
        clear_expired_sessions(): Periodically clears expired sessions.
        set_session_id_prefix(prefix): Sets a custom session ID prefix.
        set_custom_serializer(serializer): Sets a custom serialization method for session data.
        session_exists(session_id): Checks if a session exists.
        set_session(data, session_id=None): Sets the session data.
        get_session(): Retrieves the session data.
        clear_session(): Clears the loaded session.
        set_session_timeout(session_id, timeout_seconds): Sets a timeout for a session.
        check_session_timeout(session_id): Checks if a session has timed out.
        rotate_user_sessions(current_session_id): Rotates sessions for the same user agent.
        get_user_agent_hash(): Computes a hash of the user agent.
        verify_user_agent(session_data): Verifies the user agent against session data.
        verify_session_fingerprint(session_id): Verifies the session fingerprint.
        set(key, value, session_id=None): Sets a value in the session data.
        get(key, session_id=None, default=None): Retrieves a value from the session data.
        pop(key, session_id=None, default=None): Removes and returns a value from the session data.
        clear(session_id=None): Clears the session data.
        keys(session_id=None): Retrieves keys from the session data.
        values(session_id=None): Retrieves values from the session data.
        items(session_id=None): Retrieves items (key-value pairs) from the session data.
        has_key(key, session_id=None): Checks if a key exists in the session data.
        get_user_agent(): Retrieves the user agent.
        setdefault(key, default=None, session_id=None): Sets a default value for a key in the session data.
        update(other_dict, session_id=None): Updates the session data with values from another dictionary.
        get_or_create(key, default=None, session_id=None): Retrieves a value or creates it if it doesn't exist.
        popitem(session_id=None): Removes and returns an arbitrary key-value pair from the session data.
        set_many(data_dict, session_id=None): Sets multiple values in the session data.
        get_many(keys, session_id=None): Retrieves multiple values from the session data.
        delete_many(keys, session_id=None): Deletes multiple keys from the session data.
        increment(key, amount=1, session_id=None): Increments a numeric value in the session data.
        decrement(key, amount=1, session_id=None): Decrements a numeric value in the session data.
        set_cookie_options(name=None, domain=None, path=None, secure=None): Sets cookie options.
        extend_session(session_id, custom_lifetime=None): Extends the session's lifetime.
        save_to_client(session_id, response): Saves session data to the client's response.
        load_from_client(request): Loads session data from the client's request.

    """
    def __init__(self, app):
        self.config = app.config or self.load_config_from_settings()
        self.secret_key = self.config.get('SECRET_KEY', secrets.token_urlsafe(32))
        self.serializer = URLSafeTimedSerializer(self.secret_key)
        self.session_folder = self.config.get('SESSION_FOLDER', 'sessions')
        self.session_lifetime = self.config.get('SESSION_EXPIRATION', timedelta(hours=1))
        self.session_permanent = self.config.get('SESSION_PERMANENT', True)
        self.loaded_session = None
        self.encryption_key = self.config.get('ENCRYPTION_KEY')
        self.timeout_handler = self.config.get('TIMEOUT_HANDLER', None)
        self.rotate_sessions = self.config.get('ROTATE_SESSIONS', False)
        self.fingerprint_sessions = self.config.get('FINGERPRINT_SESSIONS', False)
        self.user_agent_verification = self.config.get('USER_AGENT_VERIFICATION', False)
        self.session_id_prefix = self.config.get('SESSION_ID_PREFIX', '')
        self.cookie_name = self.config.get('COOKIE_NAME', 'session')
        self.cookie_domain = self.config.get('COOKIE_DOMAIN', None)
        self.cookie_path = self.config.get('COOKIE_PATH', '/')
        self.cookie_secure = self.config.get('COOKIE_SECURE', False)

        clear_sessions_thread = threading.Thread(target=self.clear_expired_sessions)
        clear_sessions_thread.daemon = True
        clear_sessions_thread.start()

        if not os.path.exists(self.session_folder):
            os.makedirs(self.session_folder)

    def load_config_from_settings(self):
        try:
            settings = importlib.import_module('settings')
            session_config = getattr(settings, 'SESSION', {})
            return session_config.get('localSession', {})
        except ImportError:
            raise ImportError("settings.py not found or SESSION configuration is missing.")

    def generate_session_id(self):
        """
        Generates a new session ID with an optional session ID prefix.

        Returns:
            str: The generated session ID.
        """
        # Add the session ID prefix to the generated session ID
        return self.session_id_prefix + secrets.token_hex(32)

    def regenerate_session_id(self, session_id):
        """
        Regenerates a new session ID and renames the session file accordingly.

        Args:
            session_id (str): The current session ID to regenerate.

        Returns:
            str: The new session ID.
        """
        new_session_id = self.generate_session_id()
        old_session_file = os.path.join(self.session_folder, session_id)
        new_session_file = os.path.join(self.session_folder, new_session_id)

        if os.path.exists(old_session_file):
            os.rename(old_session_file, new_session_file)

        return new_session_id

    def save_session(self, data, custom_lifetime=None, session_id=None, regenerate_id=False):
        """
        Saves session data to a file with optional custom parameters.

        Args:
            data (dict): The session data to be saved.
            custom_lifetime (timedelta, optional): Custom session lifetime.
            session_id (str, optional): The session ID. If not provided, a new one is generated.
            regenerate_id (bool): If True, regenerate the session ID after saving.

        Returns:
            dict: A dictionary containing the session ID.
        """
        if not session_id:
            session_id = self.generate_session_id()

        session_file = os.path.join(self.session_folder, session_id)

        session_data = {
            'data': data,
            'expiration': datetime.now() + (custom_lifetime or self.session_lifetime),
            'timeout': None,
            'user_agent': self.get_user_agent_hash() if self.user_agent_verification else None,
        }

        session_data_json = json.dumps(session_data, cls=DateTimeEncoder)
        if self.encryption_key:
            cipher_suite = Fernet(self.encryption_key)
            session_data_encrypted = cipher_suite.encrypt(session_data_json.encode())
        else:
            session_data_encrypted = session_data_json.encode()

        with open(session_file, 'wb') as f:
            f.write(session_data_encrypted)

        if self.rotate_sessions:
            self.rotate_user_sessions(session_id)

        if regenerate_id:
            # Regenerate a new session ID
            session_id = self.regenerate_session_id(session_id)

        self.loaded_session = session_id
        return {'session_id': session_id}

    def load_session(self, session_id=None):
        """
        Loads session data from a session file.

        Args:
            session_id (str, optional): The session ID to load. If not provided, uses the currently loaded session.

        Returns:
            dict or None: The session data or None if the session does not exist or is expired.
        """
        if not session_id and self.loaded_session:
            session_id = self.loaded_session

        if not session_id:
            return None

        session_file = os.path.join(self.session_folder, session_id)

        if os.path.exists(session_file):
            with open(session_file, 'rb') as f:
                session_data_encrypted = f.read()

                if self.encryption_key:
                    cipher_suite = Fernet(self.encryption_key)
                    session_data_json = cipher_suite.decrypt(session_data_encrypted).decode()
                else:
                    session_data_json = session_data_encrypted.decode()

                session_data = json.loads(session_data_json)

                expiration = session_data.get('expiration')
                if (
                    expiration and
                    datetime.fromisoformat(expiration) > datetime.now() and
                    (not self.user_agent_verification or self.verify_user_agent(session_data)) and
                    (not self.fingerprint_sessions or self.verify_session_fingerprint(session_id))
                ):
                    if session_data['timeout'] and self.timeout_handler:
                        self.timeout_handler(session_data)
                    return session_data['data']
                else:
                    self.delete_session(session_id)
                    return None
        else:
            return None

    def delete_session(self, session_id):
        """
        Deletes a session file associated with the given session ID.

        Args:
            session_id (str): The session ID to delete.
        """
        session_file = os.path.join(self.session_folder, session_id)

        if os.path.exists(session_file):
            os.remove(session_file)

    def renew_session(self, custom_lifetime=None):
        """
    Renews the current session by updating its expiration time.

    Args:
        custom_lifetime (timedelta, optional): Custom session lifetime.
    """
        if self.loaded_session:
            session_data = self.load_session(self.loaded_session)
            if session_data:
                self.save_session(session_data, custom_lifetime)

    def clear_expired_sessions(self):
        """
    Periodically clears expired sessions from the session folder.
    """
        while True:
            current_time = datetime.now()
            for filename in os.listdir(self.session_folder):
                session_id = os.path.splitext(filename)[0]
                session_data = self.load_session(session_id)

                if session_data and session_data.get('expiration') and session_data['expiration'] < current_time:
                    self.delete_session(session_id)

            time.sleep(3600)

    def set_session_id_prefix(self, prefix):
        """
    Sets the session ID prefix.

    Args:
        prefix (str): The new session ID prefix.
    """
        # Set the session ID prefix
        self.session_id_prefix = prefix

    def set_custom_serializer(self, serializer):
        """
    Sets a custom serialization method for session data.

    Args:
        serializer (callable): The custom serialization method.
    """
        # Set a custom serialization method for session data
        self.serializer = serializer

    def session_exists(self, session_id):
        """
    Checks if a session file with the given session ID exists.

    Args:
        session_id (str): The session ID to check.

    Returns:
        bool: True if the session file exists; otherwise, False.
    """
        session_file = os.path.join(self.session_folder, session_id)
        return os.path.exists(session_file)

    def set_session(self, data, session_id=None):
        """
    Sets session data with an optional session ID.

    Args:
        data (dict): The session data to set.
        session_id (str, optional): The session ID to use. If not provided, a new one is generated.

    Returns:
        dict: A dictionary containing the session ID.
    """
        return self.save_session(data, session_id=session_id)

    def get_session(self):
        """
    Gets the currently loaded session data.

    Returns:
        dict or None: The session data or None if no session is loaded.
    """
        return self.load_session()

    def clear_session(self):
        """
    Clears the currently loaded session.
    """
        self.loaded_session = None

    def set_session_timeout(self, session_id, timeout_seconds):
        """
    Sets a timeout for a specific session.

    Args:
        session_id (str): The session ID to set the timeout for.
        timeout_seconds (int): The timeout duration in seconds.
    """
        session_data = self.load_session(session_id)
        if session_data:
            session_data['timeout'] = datetime.now() + timedelta(seconds=timeout_seconds)
            self.save_session(session_data, session_id=session_id)

    def check_session_timeout(self, session_id):
        """
    Checks if a session has timed out.

    Args:
        session_id (str): The session ID to check.

    Returns:
        bool: True if the session has timed out; otherwise, False.
    """
        session_data = self.load_session(session_id)
        if session_data and session_data['timeout'] and datetime.now() > session_data['timeout']:
            return True
        return False

    def rotate_user_sessions(self, current_session_id):
        """
    Rotates user sessions based on their user agent hash.

    Args:
        current_session_id (str): The session ID of the current user.
    """
        user_agent_hash = self.get_user_agent_hash()
        for filename in os.listdir(self.session_folder):
            session_id = os.path.splitext(filename)[0]
            if session_id != current_session_id:
                session_data = self.load_session(session_id)
                if session_data and 'user_agent' in session_data and session_data['user_agent'] == user_agent_hash:
                    self.delete_session(session_id)

    def get_user_agent_hash(self):
        """
    Generates a hash of the user agent string.

    Returns:
        str: The hashed user agent string.
    """
        user_agent = self.get_user_agent()  # Get user agent using socket
        return base64.urlsafe_b64encode(hashlib.sha256(user_agent.encode()).digest()).decode()

    def verify_user_agent(self, session_data):
        """
    Verifies the user agent of a session against the current user agent.

    Args:
        session_data (dict): The session data to verify.

    Returns:
        bool: True if the user agent matches; otherwise, False.
    """
        user_agent_hash = self.get_user_agent_hash()
        return 'user_agent' in session_data and session_data['user_agent'] == user_agent_hash

    def verify_session_fingerprint(self, session_id):
        """
    Verifies the session fingerprint against the user agent hash.

    Args:
        session_id (str): The session ID to verify.

    Returns:
        bool: True if the session fingerprint matches; otherwise, False.
    """
        return session_id.startswith(self.get_user_agent_hash())

    def set(self, key, value, session_id=None):
        """
    Sets a key-value pair in the session data.

    Args:
        key (str): The key to set.
        value (Any): The value to associate with the key.
        session_id (str, optional): The session ID to use.

    Returns:
        None
    """
        session_data = self.load_session(session_id) or {}
        session_data[key] = value
        self.save_session(session_data, session_id=session_id)

    def get(self, key, session_id=None, default=None):
        """
    Gets the value associated with a key in the session data.

    Args:
        key (str): The key to retrieve.
        session_id (str, optional): The session ID to use.
        default (Any, optional): The default value to return if the key is not found.

    Returns:
        Any: The value associated with the key or the default value.
    """
        session_data = self.load_session(session_id)
        return session_data.get(key, default) if session_data else default

    def pop(self, key, session_id=None, default=None):
        """
    Removes a key-value pair from the session data.

    Args:
        key (str): The key to remove.
        session_id (str, optional): The session ID to use.
        default (Any, optional): The default value to return if the key is not found.

    Returns:
        Any: The value associated with the removed key or the default value.
    """
        session_data = self.load_session(session_id)
        value = session_data.pop(key, default) if session_data else default
        if session_data:
            self.save_session(session_data, session_id=session_id)
        return value

    def clear(self, session_id=None):
        """
    Clears all data in the session.

    Args:
        session_id (str, optional): The session ID to clear. If not provided, clears the currently loaded session.
    """
        self.save_session({}, session_id=session_id)

    def keys(self, session_id=None):
        """
    Gets a list of keys in the session data.

    Args:
        session_id (str, optional): The session ID to use.

    Returns:
        List[str]: A list of keys in the session data.
    """
        session_data = self.load_session(session_id)
        return list(session_data.keys()) if session_data else []

    def values(self, session_id=None):
        """
    Gets a list of values in the session data.

    Args:
        session_id (str, optional): The session ID to use.

    Returns:
        List[Any]: A list of values in the session data.
    """
        session_data = self.load_session(session_id)
        return list(session_data.values()) if session_data else []

    def items(self, session_id=None):
        """
    Gets a list of key-value pairs in the session data.

    Args:
        session_id (str, optional): The session ID to use.

    Returns:
        List[Tuple[str, Any]]: A list of key-value pairs in the session data.
    """
        session_data = self.load_session(session_id)
        return list(session_data.items()) if session_data else []

    def has_key(self, key, session_id=None):
        """
    Checks if a key exists in the session data.

    Args:
        key (str): The key to check for.
        session_id (str, optional): The session ID to use.

    Returns:
        bool: True if the key exists; otherwise, False.
    """
        session_data = self.load_session(session_id)
        return key in session_data if session_data else False

    def get_user_agent(self):
        """
    Gets the user agent string of the client.

    Returns:
        str: The user agent string.
    """
        try:
            conn = http.client.HTTPConnection("ifconfig.me")
            conn.request("GET", "/ua")
            res = conn.getresponse()
        except Exception as e:
            print(f"Error getting user agent: {e}")
            return ""

        user_agent = res.read().decode().strip()
        return user_agent
    
    def setdefault(self, key, default=None, session_id=None):
        """
    Sets a default value for a key if it does not exist in the session data.

    Args:
        key (str): The key to set.
        default (Any, optional): The default value to set if the key does not exist.
        session_id (str, optional): The session ID to use.

    Returns:
        Any: The value associated with the key, either the existing value or the default.
    """
        session_data = self.load_session(session_id) or {}
        value = session_data.setdefault(key, default)
        self.save_session(session_data, session_id=session_id)
        return value

    def update(self, other_dict, session_id=None):
        """
    Updates the session data with key-value pairs from another dictionary.

    Args:
        other_dict (dict): The dictionary containing key-value pairs to update the session data.
        session_id (str, optional): The session ID to use.

    Returns:
        None
    """
        session_data = self.load_session(session_id) or {}
        session_data.update(other_dict)
        self.save_session(session_data, session_id=session_id)

    def get_or_create(self, key, default=None, session_id=None):
        """
    Gets the value associated with a key in the session data, creating it if it does not exist.

    Args:
        key (str): The key to retrieve or create.
        default (Any, optional): The default value to set if the key does not exist.
        session_id (str, optional): The session ID to use.

    Returns:
        Any: The value associated with the key, either the existing value or the default.
    """
        session_data = self.load_session(session_id) or {}
        value = session_data.get(key, default)
        if value is None:
            session_data[key] = default
            self.save_session(session_data, session_id=session_id)
        return value
    
    def popitem(self, session_id=None):
        """
    Removes and returns an arbitrary key-value pair from the session data.

    Args:
        session_id (str, optional): The session ID to use.

    Returns:
        Tuple[str, Any] or None: A key-value pair or None if the session is empty.
    """
        session_data = self.load_session(session_id) or {}
        if session_data:
            key, value = session_data.popitem()
            self.save_session(session_data, session_id=session_id)
            return key, value
        return None

    def set_many(self, data_dict, session_id=None):
        """
    Sets multiple key-value pairs in the session data.

    Args:
        data_dict (dict): A dictionary containing key-value pairs to set.
        session_id (str, optional): The session ID to use.

    Returns:
        None
    """
        session_data = self.load_session(session_id) or {}
        session_data.update(data_dict)
        self.save_session(session_data, session_id=session_id)

    def get_many(self, keys, session_id=None):
        """
    Gets multiple values associated with the given keys in the session data.

    Args:
        keys (List[str]): A list of keys to retrieve.
        session_id (str, optional): The session ID to use.

    Returns:
        dict: A dictionary containing key-value pairs for the requested keys.
    """
        session_data = self.load_session(session_id) or {}
        return {key: session_data[key] for key in keys if key in session_data}

    def delete_many(self, keys, session_id=None):
        """
    Deletes multiple keys and their associated values from the session data.

    Args:
        keys (List[str]): A list of keys to delete.
        session_id (str, optional): The session ID to use.

    Returns:
        None
    """
        session_data = self.load_session(session_id) or {}
        for key in keys:
            session_data.pop(key, None)
        self.save_session(session_data, session_id=session_id)

    def increment(self, key, amount=1, session_id=None):
        """
    Increments the value associated with a key in the session data.

    Args:
        key (str): The key to increment.
        amount (int, optional): The amount to increment by (default is 1).
        session_id (str, optional): The session ID to use.

    Returns:
        int: The new value associated with the key after incrementing.
    """
        session_data = self.load_session(session_id) or {}
        current_value = session_data.get(key, 0)
        session_data[key] = current_value + amount
        self.save_session(session_data, session_id=session_id)
        return session_data[key]

    def decrement(self, key, amount=1, session_id=None):
        """
    Decrements the value associated with a key in the session data.

    Args:
        key (str): The key to decrement.
        amount (int, optional): The amount to decrement by (default is 1).
        session_id (str, optional): The session ID to use.

    Returns:
        int: The new value associated with the key after decrementing.
    """
        session_data = self.load_session(session_id) or {}
        current_value = session_data.get(key, 0)
        session_data[key] = max(0, current_value - amount)
        self.save_session(session_data, session_id=session_id)
        return session_data[key]
    
    def set_cookie_options(self, name=None, domain=None, path=None, secure=None):
        """
    Sets options for the session cookie.

    Args:
        name (str, optional): The name of the session cookie.
        domain (str, optional): The domain for the session cookie.
        path (str, optional): The path for the session cookie.
        secure (bool, optional): Whether the session cookie should be secure (HTTPS only).

    Returns:
        None
    """
        if name is not None:
            self.cookie_name = name
        if domain is not None:
            self.cookie_domain = domain
        if path is not None:
            self.cookie_path = path
        if secure is not None:
            self.cookie_secure = secure

    def extend_session(self, session_id, custom_lifetime=None):
        """
    Extends the expiration time of a session.

    Args:
        session_id (str): The session ID to extend.
        custom_lifetime (timedelta, optional): Custom lifetime to add to the session (default is None).

    Returns:
        None
    """
        session_data = self.load_session(session_id)
        if session_data:
            session_data['expiration'] += (custom_lifetime or self.session_lifetime)
            self.save_session(session_data, session_id=session_id)

    def save_to_client(self, session_id, response):
        """
    Saves the session data to a client's response as a cookie.

    Args:
        session_id (str): The session ID to save.
        response (object): The response object to attach the session data cookie to.

    Returns:
        None
    """
        session_data = self.load_session(session_id)
        if session_data:
            session_data_json = json.dumps(session_data, cls=DateTimeEncoder)
            if self.encryption_key:
                cipher_suite = Fernet(self.encryption_key)
                session_data_encrypted = cipher_suite.encrypt(session_data_json.encode())
            else:
                session_data_encrypted = session_data_json.encode()

            cookie = SimpleCookie()
            cookie[self.cookie_name] = session_id
            cookie[self.cookie_name]['path'] = self.cookie_path
            if self.cookie_domain:
                cookie[self.cookie_name]['domain'] = self.cookie_domain
            if self.cookie_secure:
                cookie[self.cookie_name]['secure'] = True
            cookie[self.cookie_name]['expires'] = session_data['expiration'].strftime('%a, %d %b %Y %H:%M:%S GMT')

            response.headers['Set-Cookie'] = cookie[self.cookie_name].OutputString()
            response.body = session_data_encrypted

    def load_from_client(self, request):
        """
    Loads session data from a client's request cookie.

    Args:
        request (object): The request object containing cookies.

    Returns:
        Any: The loaded session data or None if not found.
    """
        if self.cookie_name not in request.cookies:
            return None

        session_id = request.cookies[self.cookie_name].value
        return self.load_session(session_id)
