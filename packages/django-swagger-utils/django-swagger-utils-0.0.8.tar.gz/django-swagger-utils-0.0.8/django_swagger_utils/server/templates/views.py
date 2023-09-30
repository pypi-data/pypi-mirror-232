__all__ = ['VIEWS_TEMPLATE']

VIEWS_TEMPLATE = """
from django.http import HttpResponse
from .validator_class import ValidatorClass

@validate_decorator(validator_class=ValidatorClass)
def api_wrapper(*args, **kwargs):
    response = {}
    return HttpResponse(response)

    # ---------MOCK IMPLEMENTATION---------
    try:
        from {{ app }}.views.{{ operation_id }}.tests.test_case_01 \
            import TEST_CASE as test_case
    except ImportError:
        from {{ app }}.views.{{ operation_id }}.tests.test_case_01 \
            import test_case

    from django_swagger_utils.drf_server.utils.server_gen.mock_response \
        import mock_response
    try:
        from {{ app }}.views.{{ operation_id }}.request_response_mocks \
            import RESPONSE_200_JSON
    except ImportError:
        RESPONSE_200_JSON = ''
    response_tuple = mock_response(
        app_name={{ app }}, test_case=test_case,
        operation_name={{ operation_id }},
        kwargs=kwargs, default_response_body=RESPONSE_200_JSON)
    return response_tuple[1]
"""
