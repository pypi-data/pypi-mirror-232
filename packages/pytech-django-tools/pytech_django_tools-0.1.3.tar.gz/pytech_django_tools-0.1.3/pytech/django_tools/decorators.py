from functools import wraps

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.db.models import Model
from django.shortcuts import get_object_or_404

from pytech.domain.messages import MESSAGE_ACCESS_DENIED, MESSAGE_PAGE_EXPIRED

__all__ = [
    "anonymous_user_or_permission_denied",
    "login_required_or_permission_denied",
    "object_passes_test",
    "raise_permission_denied_if_redirect_to_login",
    "user_owns_the_object",
]


def raise_permission_denied_if_redirect_to_login(error_message):
    """
    Decorator factory that raises a PermissionDenied error 
    if a redirect is returned from a view.
    :param error_message: The error message to use in the PermissionDenied error
    :raise PermissionDenied:
    :return: the decorator
    """
    def decorator(view_func):
        """
        The actual decorator
        :param view_func: the view to decorate
        :return: the decorated view
        """
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            response = view_func(request, *args, **kwargs)

            if response.status_code == 302:
                # Raise PermissionDenied if it's a redirect to the login page
                if f"?{REDIRECT_FIELD_NAME}=" in response.url:
                    raise PermissionDenied(error_message)

            return response

        return _wrapped_view

    return decorator


def anonymous_user_or_permission_denied(view_func):
    """
    Decorator that raises a PermissionDenied error if the user is logged.

    :param view_func: the view to protect
    :raise PermissionDenied:
    :return: the decorated view
    """
    return raise_permission_denied_if_redirect_to_login(MESSAGE_ACCESS_DENIED)(
        user_passes_test(lambda user: not user.is_authenticated)(view_func)
    )


def login_required_or_permission_denied(view_func):
    """
    Decorator that raises a PermissionDenied error if the user is not logged.

    :param view_func: the view to protect
    :raise PermissionDenied:
    :return: the decorated view
    """
    return raise_permission_denied_if_redirect_to_login(MESSAGE_ACCESS_DENIED)(
        login_required(view_func, login_url=None)
    )


def object_passes_test(model_class, test_func):
    """
    Decorator for views that checks that the user passes the given test,
    redirecting to the log-in page if necessary. The test should be a callable
    that takes the user object and returns True if the user passes.
    """
    if not issubclass(model_class, Model):
        raise TypeError(f"{model_class} is not a valid Model")

    def decorator(view_func):
        """
        The actual decorator
        :param view_func: the view to decorate
        :return: the decorated view
        """
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            obj = get_object_or_404(model_class, pk=kwargs["pk"])
            if not test_func(obj):
                raise PermissionDenied(MESSAGE_PAGE_EXPIRED)

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


def user_owns_the_object(model_class):
    """
    Decorator factory bound to the provided model.
    It is supposed to decorate a SingleObject django view.
    The model is supposed to have a "owner" field
    that is a Foreign Key to the User model.

    # TODO: this can be improved

    The generated decorators will check if the logged user is the owner of the object.

    :param model_class: The model class related to the view
    :raise PermissionDenied:
    :return: the decorator that checks the ownership
    """
    def _user_owns_the_object(view_func):
        """
        The actual decorator
        :param view_func: the view to decorate
        :return: the decorated view
        """
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            current_obj = get_object_or_404(model_class, pk=kwargs["pk"])

            if current_obj.owner != request.user:
                raise PermissionDenied(MESSAGE_ACCESS_DENIED)

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return _user_owns_the_object
