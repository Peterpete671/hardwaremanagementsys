"""
Middleware to capture current user for audit logging
Stores user in local-thread storage
"""

import threading

_thread_locals = threading.local()

def get_current_user():
    """Get the current user from the thread local storage."""
    return getattr(_thread_locals, "user", None)

def set_current_user(user):
    """Set the current user in thread local storage."""
    _thread_locals.user = user

class AuditMiddleware:
    """
    Middleware to capture the current user for audit logging.
    Must be added to MIDDLEWARE in settings.py
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        #Store user in thread local
        set_current_user(getattr(request, 'user', None))

        response = self.get_response(request)

        #Clean up
        set_current_user(None)

        return response