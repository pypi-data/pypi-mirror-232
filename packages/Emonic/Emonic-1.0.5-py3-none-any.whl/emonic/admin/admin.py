import os
import argparse
import subprocess
from colorama import Fore, Style  # Import colorama for colored output

def create_project(project_name, use_database, setup_routing, setup_engine):
    # Create a folder for the project
    os.makedirs(project_name, exist_ok=True)

    # Create settings.py
    with open(os.path.join(project_name, 'settings.py'), 'w') as settings_file:
        settings_data = f"""# Server settings
HOST = 'localhost'  
# The host on which the server will run. Use 'localhost' for development. 
# To allow requests from any host, set HOST = '0.0.0.0'.
PORT = 8000  
# The port on which the server will listen for incoming requests. 
# You can change this to any available port, e.g., 80 for HTTP or 443 for HTTPS.
DEBUG = True  
# Enable debugging mode for hot reloading and detailed error messages. 
# It's useful during development but should be turned off in production.
SECRET_KEY = 'your_secret_key'  
# A secret key for secure session data and other cryptographic operations. 
# Keep this key secret and unique for your application.
STATIC_FOLDER = 'static'  
# The folder path where static files (e.g., CSS, JavaScript) are stored. 
# By default, they are served from the 'static' folder in your project.

# Template settings
TEMPLATES = [
    {{
        'BACKEND': 'emonic.backends.EmonicTemplates',  
        # Template backend for Emonic. Leave this as is for using Emonic's built-in templates.
        'DIRS': ['views'],  
        # List of directories containing templates. Customize as needed.
    }}
]

# Database settings (optional)
DATABASES = {{
    'default': {{
        'ENGINE': 'emonic.db.backends.electrus',  
        # Database engine, Electrus in this case. You can change it based on your database choice, Emonic supports ['Electrus', 'MongoDB', 'MySql'].
        'HOST': 'localhost',  
        # Database host address. Update this to your database server's address.
        'PORT': 37017,  
        # Database port number. Change this to your database server's port.
        'USER': 'root',  
        # Database username for authentication. Modify this based on your database setup.
        'PASSWORD': 'root',  
        # Database password for authentication. Customize as needed.
    }}
}}

# Email (mailer) settings
MAILER = [
    {{
        "SMTP": "VALUE",  
        # SMTP server address for sending emails. Replace "VALUE" with your SMTP server's address.
        "PORT": "VALUE",  
        # SMTP server port number for email communication. Update as required.
        "USERNAME": "VALUE",  
        # SMTP server username (if required for authentication). Set to your username or None.
        "PASSWORD": "VALUE",  
        # SMTP server password (if required for authentication). Set to your password or None.
        "SSL": True,  
        # Use SSL/TLS for secure email sending. Modify based on your email server's security settings.
        "DEFAULT_SENDER": "VALUE",  
        # Default sender email address for outgoing emails. Customize as needed.
    }}
]

# Cross-Origin Resource Sharing (CORS) settings
CORS = {{
    'default': {{
        'allowed_origins': '*',  
        # Allowed origins for CORS requests. You can specify specific origins or use '*' for any.
        'allowed_methods': ['GET'],  
        # Allowed HTTP methods for CORS. Adjust based on your application's requirements.
        'max_age': 3600,  
        # Maximum age (in seconds) for preflight request result caching. Modify as needed.
        'allowed_headers': ['Content-Type'],  
        # Allowed request headers. Customize for your application's needs.
        'expose_headers': ['X-Custom-Header'],  
        # Headers exposed to the response. Add more headers if required.
        'allow_credentials': True,  
        # Allow credentials (e.g., cookies) in cross-origin requests. Adjust as necessary.
        'cors_profile': 'default',  
        # CORS profile (default or wildcard). Use 'default' in most cases.
        'validate_request_origin': None,  
        # Validation function for request origin (None for no validation). Define a custom function if needed.
        'log_cors_requests': False,  
        # Log CORS requests for debugging purposes. Enable during development if necessary.
        'cors_logger_name': 'cors',  
        # Name of the CORS logger for logging CORS-related activities.
    }}
}}

# Session settings
SESSION = {{
    'localSession': {{
        'SECRET_KEY': 'your_secret_key',  
        # Secret key for session data encryption and signing. Keep it secure.
        'SESSION_FOLDER': 'storage',  
        # Folder where session data is stored on the server. Customize as needed.
        'SESSION_EXPIRATION': 3600,  
        # Default lifetime of a session (in seconds). Modify as per your application's requirements.
        'SESSION_PERMANENT': True,  
        # If True, sessions are stored permanently until manually deleted. Set based on your use case.
        'ENCRYPTION_KEY': 'your_encryption_key',  
        # Encryption key used to encrypt session data (optional). Add if necessary for extra security.
        'TIMEOUT_HANDLER': None,  
        # Custom handler function for timed-out sessions (optional). Define if needed.
        'ROTATE_SESSIONS': False,  
        # If True, sessions for the same user agent are rotated. Set based on your application's security needs.
        'FINGERPRINT_SESSIONS': False,  
        # If True, sessions are fingerprinted to prevent session reuse. Use when necessary.
        'USER_AGENT_VERIFICATION': False,  
        # If True, user agent verification is performed for sessions. Enable if required.
        'SESSION_ID_PREFIX': '',  
        # Prefix added to generated session IDs (if needed). Modify as per your requirements.
        'COOKIE_NAME': 'session',  
        # Name of the session cookie. Customize based on your application's naming conventions.
        'COOKIE_DOMAIN': None,  
        # Domain for which the session cookie is valid (None for all domains). Adjust as needed.
        'COOKIE_PATH': '/',  
        # Path within the domain for which the session cookie is valid. Modify as per your application's needs.
        'COOKIE_SECURE': False,  
        # If True, the session cookie is marked as secure. Enable for HTTPS-only sites.
    }}
}}

# Script configuration (e.g., for running Emonic apps)
SCRIPT = [
    {{
        "config": {{
            "wsgi": "emonic.wsgi.http",  
            # WSGI application entry point. Modify only if needed for advanced use cases.
            "host": "localhost",  
            # Host on which the application will run. Update based on your deployment environment.
            "port": "8000",  
            # Port on which the application will listen for requests. Customize for your needs.
            "debug": "True",  
            # Enable debugging mode for the application. Set to "False" in production.
        }},
        "apps": {{
            "emonic",  
            # List of Emonic apps to run. Add more apps as necessary for your project.
            "emonic-admin",
            # Additional Emonic apps can be included here, e.g., electrus, nexusdb, etc.
        }}
    }}
]
    """
        settings_file.write(settings_data)

    if setup_routing:
        # Create Router folder
        os.makedirs(os.path.join(project_name, 'Routes'), exist_ok=True)

        # Create clust.py inside Routes folder
        clust_py_content = """from emonic.components.blueprint import Blueprint

home = Blueprint('Home', __name__, url_prefix='/home')

@home.route('/')
def BlueprintHomeRoute(request):
    return home.text_response('hello')
    """

        routes_folder = os.path.join(project_name, 'Routes')
        os.makedirs(routes_folder, exist_ok=True)

        with open(os.path.join(routes_folder, 'clust.py'), 'w') as clust_file:
            clust_file.write(clust_py_content)

    else:
        # Create app folder
        os.makedirs(os.path.join(project_name, 'app'), exist_ok=True)

    if setup_engine:
        # Create views and static folders
        os.makedirs(os.path.join(project_name, 'views'), exist_ok=True)
        os.makedirs(os.path.join(project_name, 'static'), exist_ok=True)

    if use_database:
        # Install Electrus package
        subprocess.run(['pip', 'install', 'electrus'])

    # Create main.py
    main_py_content = """from emonic.core import Emonic

app = Emonic(__name__)

@app.route('/<name>', methods=['GET', 'POST'])
def emonicHomeRoute(request, name):
    return f"Welcome, {name} to Emonic Web server"

if __name__ == "__main__":
    app.run()
    """
    with open(os.path.join(project_name, 'main.py'), 'w') as main_file:
        main_file.write(main_py_content)

    # Create config.ini outside the project folder
    project_path = os.path.abspath(project_name)
    config_ini_content = f"""[PROJECT]
SERVER = "Emonic"
HOST = "localhost"
PORT = 8000
ALIAS = "Keep-Active-2.1"
ROOT = {project_path}
NAME = {project_name}
"""
    with open('config.ini', 'w') as config_file:
        config_file.write(config_ini_content)

def main():
    parser = argparse.ArgumentParser(description='Build a project')
    parser.add_argument('command', choices=['buildproject'], help='The command to execute')
    args = parser.parse_args()

    if args.command == 'buildproject':
        project_name = input(f"{Fore.BLUE}Enter the project name: {Style.RESET_ALL}")
        use_database = input(f"{Fore.BLUE}Would you like to use Electrus Database? (Y/N): {Style.RESET_ALL}").strip().lower() in ['y', 'yes']
        setup_routing = input(f"{Fore.BLUE}Would you like to setup Routing? (Y/N): {Style.RESET_ALL}").strip().lower() in ['y', 'yes']
        setup_engine = input(f"{Fore.BLUE}Would you like to setup the Emonic Template & Static engine? (Y/N): {Style.RESET_ALL}").strip().lower() in ['y', 'yes']

        create_project(project_name, use_database, setup_routing, setup_engine)
        print(f"Project '{project_name}' created successfully!")

if __name__ == "__main__":
    main()
