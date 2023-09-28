from django.conf import settings
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin


class RedirectPermissionDeniedMiddleware(MiddlewareMixin):
    """
    Middleware that translates permission denied
    exception in redirects with error messages.
    """

    def process_exception(self, request, exception):
        """
        This method handles the PermissionDenied exception changing the behaviour
        in a redirect to the login page
        """
        if isinstance(exception, PermissionDenied):
            messages.error(
                request,
                f"{settings.MESSAGE_UNAUTHORIZED}: {exception}",
            )
            return redirect(to=settings.LOGIN_REDIRECT_URL)
