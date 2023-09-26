import django.dispatch


bind_extra_request_metadata = django.dispatch.Signal()
""" Signal to add extra ``structlog`` bindings from ``django``'s request.

:param logger: the logger to bind more metadata or override existing bound metadata

>>> from django.dispatch import receiver
>>> from django_structlog import signals
>>> import structlog
>>>
>>> @receiver(signals.bind_extra_request_metadata)
... def bind_user_email(request, logger, **kwargs):
...     structlog.contextvars.bind_contextvars(user_email=getattr(request.user, 'email', ''))

"""

bind_extra_request_finished_metadata = django.dispatch.Signal()
""" Signal to add extra ``structlog`` bindings from ``django``'s finished request and response.

:param logger: the logger to bind more metadata or override existing bound metadata
:param response: the response resulting of the request

>>> from django.dispatch import receiver
>>> from django_structlog import signals
>>> import structlog
>>>
>>> @receiver(signals.bind_extra_request_finished_metadata)
... def bind_user_email(request, logger, response, **kwargs):
...     structlog.contextvars.bind_contextvars(user_email=getattr(request.user, 'email', ''))

"""

bind_extra_request_failed_metadata = django.dispatch.Signal()
""" Signal to add extra ``structlog`` bindings from ``django``'s failed request and exception.

:param logger: the logger to bind more metadata or override existing bound metadata
:param exception: the exception resulting of the request

>>> from django.dispatch import receiver
>>> from django_structlog import signals
>>> import structlog
>>>
>>> @receiver(signals.bind_extra_request_failed_metadata)
... def bind_user_email(request, logger, exception, **kwargs):
...     structlog.contextvars.bind_contextvars(user_email=getattr(request.user, 'email', ''))

"""

update_failure_response = django.dispatch.Signal()
""" Signal to update response failure response before it is returned.

:param request: the request returned by the view
:param response: the response resulting of the request
:param logger: the logger
:param exception: the exception

>>> from django.dispatch import receiver
>>> from django_structlog import signals
>>> import structlog
>>>
>>> @receiver(signals.update_failure_response)
... def add_request_id_to_error_response(request, response, logger, exception, **kwargs):
...     context = structlog.contextvars.get_merged_contextvars(logger)
...     response['X-Request-ID'] = context["request_id"]

"""
