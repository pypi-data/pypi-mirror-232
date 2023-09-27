import os
import functools
from werkzeug.wrappers import Request, Response
from werkzeug.exceptions import Forbidden

class Tailsman:
    """
    Tailsman is a security middleware for Emonic that helps you add various security headers and settings
    to your web application.

    Args:
        app (Emonic): The Emonic application to which the Tailsman middleware should be applied.
        content_security_policy (dict): The Content Security Policy (CSP) directives.
        force_https (bool): Whether to enforce HTTPS (default is False).
        strict_transport_security (bool): Whether to enable HTTP Strict Transport Security (HSTS) (default is False).
        frame_options (str): The X-Frame-Options header value (default is None).
        session_cookie_secure (bool): Whether to secure session cookies (default is False).
        content_security_policy_nonce_in (list): List of CSP directives to add nonces to (default is None).
        content_security_policy_report_only (bool): Whether to enable CSP in report-only mode (default is False).
        referrer_policy (str): The Referrer-Policy header value (default is None).
        x_content_type_options (str): The X-Content-Type-Options header value (default is None).
        x_xss_protection (str): The X-XSS-Protection header value (default is None).
        x_content_security_policy (str): The X-Content-Security-Policy header value (default is None).
        x_content_security_policy_report_only (str): The X-Content-Security-Policy-Report-Only header value (default is None).

    Example:
        Initialize Tailsman and apply it to an Emonic app with various security settings:

        ```python
        from emonic import Emonic

        app = Emonic(__name__)

        csp = {
            'default-src': ['\'self\''],
            'img-src': ['*'],
            'style-src': ['\'self\'', 'maxcdn.bootstrapcdn.com'],
            'script-src': ['\'self\'', 'code.jquery.com'],
            'font-src': ['\'self\'', 'fonts.gstatic.com'],
        }

        tailsman = Tailsman(
            app,
            content_security_policy=csp,
            force_https=True,
        )
        ```

    """

    def __init__(self, app=None, content_security_policy=None, force_https=False, strict_transport_security=False,
                 frame_options=None, session_cookie_secure=False, content_security_policy_nonce_in=None,
                 content_security_policy_report_only=False, referrer_policy=None, x_content_type_options=None,
                 x_xss_protection=None, x_content_security_policy=None, x_content_security_policy_report_only=None):
        self.app = app
        self.content_security_policy = content_security_policy
        self.force_https = force_https
        self.strict_transport_security = strict_transport_security
        self.frame_options = frame_options
        self.session_cookie_secure = session_cookie_secure
        self.content_security_policy_nonce_in = content_security_policy_nonce_in
        self.content_security_policy_report_only = content_security_policy_report_only
        self.referrer_policy = referrer_policy
        self.x_content_type_options = x_content_type_options
        self.x_xss_protection = x_xss_protection
        self.x_content_security_policy = x_content_security_policy
        self.x_content_security_policy_report_only = x_content_security_policy_report_only

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """
        Initialize Tailsman with an Emonic app.

        Args:
            app (Emonic): The Emonic application to which the Tailsman middleware should be applied.
        """
        self.app = app
        self.app.before_request(self._add_security_headers)

    def _add_security_headers(self, request):
        """
        Add security headers to the response.

        Args:
            request (Request): The incoming request object.

        Returns:
            Response: The response with security headers added.
        """
        response = Response()

        # Set Content Security Policy (CSP)
        if self.content_security_policy:
            csp = "; ".join([f"{key} {value}" if isinstance(value, str) else f"{key} {' '.join(value)}" for key, value in self.content_security_policy.items()])
            response.headers['Content-Security-Policy'] = csp

        # Enforce HTTPS
        if self.force_https:
            if not request.is_secure:
                return Response('HTTPS is required for this resource.', status=403)

        # Enable HTTP Strict Transport Security (HSTS)
        if self.strict_transport_security:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

        # Set X-Frame-Options
        if self.frame_options:
            response.headers['X-Frame-Options'] = self.frame_options

        # Secure session cookies
        if self.session_cookie_secure:
            response.set_cookie('session_id', secure=True)

        # Add nonce to specified CSP directives
        if self.content_security_policy_nonce_in:
            for directive in self.content_security_policy_nonce_in:
                response.headers[f'Content-Security-Policy-{directive}'] = f"'nonce-{os.urandom(32).hex()}'"

        # Disable report-only mode
        if self.content_security_policy_report_only:
            response.headers.pop('Content-Security-Policy-Report-Only', None)

        # Set Referrer-Policy
        if self.referrer_policy:
            response.headers['Referrer-Policy'] = self.referrer_policy

        # Set X-Content-Type-Options
        if self.x_content_type_options:
            response.headers['X-Content-Type-Options'] = self.x_content_type_options

        # Set X-XSS-Protection
        if self.x_xss_protection:
            response.headers['X-XSS-Protection'] = self.x_xss_protection

        # Set X-Content-Security-Policy
        if self.x_content_security_policy:
            response.headers['X-Content-Security-Policy'] = self.x_content_security_policy

        # Set X-Content-Security-Policy-Report-Only
        if self.x_content_security_policy_report_only:
            response.headers['X-Content-Security-Policy-Report-Only'] = self.x_content_security_policy_report_only

        response.headers.update(request.headers)

        return None
    
    def __call__(self):
        """
        Decorator to apply security settings to a view function.

        Example:
        ```python
        @app.route('/')
        @tailsman()
        def index(request):
            return 'Hello, World!'
        ```
        """
        def decorator(view_func):
            @functools.wraps(view_func)
            def wrapper(*args, **kwargs):
                response = view_func(*args, **kwargs)
                return response
            return wrapper
        return decorator

    def enforce_https(self, view_func):
        """
        Decorator to enforce HTTPS for a view function.

        Args:
            view_func (function): The view function to be decorated.

        Example:
            ```python
            @app.route('/')
            @tailsman.enforce_https
            def index(request):
                return 'Hello, World!'
            ```
        """
        @functools.wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not self.app.debug and not request.is_secure:
                return Response('HTTPS is required for this resource.', status=403)
            return view_func(request, *args, **kwargs)
        return wrapper


    def strict_transport_security(self, view_func):
        """
        Decorator to enable HTTP Strict Transport Security (HSTS) for a view function.

        Args:
            view_func (function): The view function to be decorated.

        Example:
            ```python
            @app.route('/')
            @tailsman.strict_transport_security
            def index(request):
                return 'Hello, World!'
            ```
        """
        @functools.wraps(view_func)
        def wrapper(*args, **kwargs):
            response = view_func(*args, **kwargs)
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            return response
        return wrapper

    def frame_options(self, value):
        """
        Decorator to set the X-Frame-Options header for a view function.

        Args:
            value (str): The X-Frame-Options header value ('DENY', 'SAMEORIGIN', or 'ALLOW-FROM').

        Example:
            ```python
            @app.route('/')
            @tailsman.frame_options('DENY')
            def index(request):
                return 'Hello, World!'
            ```
        """
        def decorator(view_func):
            @functools.wraps(view_func)
            def wrapper(*args, **kwargs):
                response = view_func(*args, **kwargs)
                response.headers['X-Frame-Options'] = value
                return response
            return wrapper
        return decorator

    def secure_cookies(self, view_func):
        """
        Decorator to secure session cookies for a view function.

        Args:
            view_func (function): The view function to be decorated.

        Example:
            ```python
            @app.route('/')
            @tailsman.secure_cookies
            def index(request):
                return 'Hello, World!'
            ```
        """
        @functools.wraps(view_func)
        def wrapper(*args, **kwargs):
            response = view_func(*args, **kwargs)
            response.set_cookie('session_id', secure=True)
            return response
        return wrapper

    def add_nonce_to_csp(self, directives):
        """
        Decorator to add nonce to specified CSP directives for a view function.

        Args:
            directives (list): List of CSP directives to add nonces to.

        Example:
            ```python
            @app.route('/')
            @tailsman.add_nonce_to_csp(['script-src'])
            def index(request):
                return 'Hello, World!'
            ```
        """
        def decorator(view_func):
            @functools.wraps(view_func)
            def wrapper(*args, **kwargs):
                response = view_func(*args, **kwargs)
                request = Request()
                for directive in directives:
                    response.headers[f'Content-Security-Policy-{directive}'] = f"'nonce-{os.urandom(32).hex()}'"
                return response
            return wrapper
        return decorator

    def disable_report_only_mode(self, view_func):
        """
        Decorator to disable CSP report-only mode for a view function.

        Args:
            view_func (function): The view function to be decorated.

        Example:
            ```python
            @app.route('/')
            @tailsman.disable_report_only_mode
            def index(request):
                return 'Hello, World!'
            ```
        """
        @functools.wraps(view_func)
        def wrapper(*args, **kwargs):
            response = view_func(*args, **kwargs)
            response.headers.pop('Content-Security-Policy-Report-Only', None)
            return response
        return wrapper

    def referrer_policy(self, value):
        """
        Decorator to set the Referrer-Policy header for a view function.

        Args:
            value (str): The Referrer-Policy header value.

        Example:
            ```python
            @app.route('/')
            @tailsman.referrer_policy('no-referrer')
            def index(request):
                return 'Hello, World!'
            ```
        """
        def decorator(view_func):
            @functools.wraps(view_func)
            def wrapper(*args, **kwargs):
                response = view_func(*args, **kwargs)
                response.headers['Referrer-Policy'] = value
                return response
            return wrapper
        return decorator

    def content_type_options(self, value):
        """
        Decorator to set the X-Content-Type-Options header for a view function.

        Args:
            value (str): The X-Content-Type-Options header value ('nosniff').

        Example:
            ```python
            @app.route('/')
            @tailsman.content_type_options('nosniff')
            def index(request):
                return 'Hello, World!'
            ```
        """
        def decorator(view_func):
            @functools.wraps(view_func)
            def wrapper(*args, **kwargs):
                response = view_func(*args, **kwargs)
                response.headers['X-Content-Type-Options'] = value
                return response
            return wrapper
        return decorator

    def xss_protection(self, value):
        """
        Decorator to set the X-XSS-Protection header for a view function.

        Args:
            value (str): The X-XSS-Protection header value ('1; mode=block' or '0').

        Example:
            ```python
            @app.route('/')
            @tailsman.xss_protection('1; mode=block')
            def index(request):
                return 'Hello, World!'
            ```
        """
        def decorator(view_func):
            @functools.wraps(view_func)
            def wrapper(*args, **kwargs):
                response = view_func(*args, **kwargs)
                response.headers['X-XSS-Protection'] = value
                return response
            return wrapper
        return decorator

    def content_security_policy_header(self, value):
        """
        Decorator to set the X-Content-Security-Policy header for a view function.

        Args:
            value (str): The X-Content-Security-Policy header value.

        Example:
            ```python
            @app.route('/')
            @tailsman.content_security_policy_header('default-src \'self\'')
            def index(request):
                return 'Hello, World!'
            ```
        """
        def decorator(view_func):
            @functools.wraps(view_func)
            def wrapper(*args, **kwargs):
                response = view_func(*args, **kwargs)
                response.headers['X-Content-Security-Policy'] = value
                return response
            return wrapper
        return decorator

    def content_security_policy_report_only_header(self, value):
        """
        Decorator to set the X-Content-Security-Policy-Report-Only header for a view function.

        Args:
            value (str): The X-Content-Security-Policy-Report-Only header value.

        Example:
            ```python
            @app.route('/')
            @tailsman.content_security_policy_report_only_header('default-src \'self\'')
            def index(request):
                return 'Hello, World!'
            ```
        """
        def decorator(view_func):
            @functools.wraps(view_func)
            def wrapper(*args, **kwargs):
                response = view_func(*args, **kwargs)
                response.headers['X-Content-Security-Policy-Report-Only'] = value
                return response
            return wrapper
        return decorator
