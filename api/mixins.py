from rest_framework import authentication, filters, permissions
from rest_framework_jwt.authentication import JSONWebTokenAuthentication


class DefaultsMixin(object):
    """
    Default settings for view authentication and permissions.
    """
    authentication_classes = (
        authentication.BasicAuthentication,
        authentication.SessionAuthentication,
        JSONWebTokenAuthentication,
    )
    permission_classes = (
        permissions.IsAuthenticated,
    )


class FiltersMixin(object):
    """
    Default settings for view filters.
    """
    filter_backends = (
        filters.SearchFilter,
        filters.OrderingFilter,
    )
