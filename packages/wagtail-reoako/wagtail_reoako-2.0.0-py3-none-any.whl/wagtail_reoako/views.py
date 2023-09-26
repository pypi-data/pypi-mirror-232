from django.template.response import TemplateResponse

from wagtail.admin.forms.search import SearchForm
from wagtail.admin.modal_workflow import render_modal_workflow
from wagtail_reoako.reoako_client import ReoakoApiClient

from django.conf import settings


def get_context(request):
    client = ReoakoApiClient(
        api_token=settings.REOAKO_API_KEY,
        api_domain=settings.REOAKO_API_DOMAIN,
        referer=request.META.get('HTTP_REFERER'),
    )

    search_term = request.GET.get('q')
    search_form = SearchForm(request.GET) if search_term else SearchForm()
    error_message = None
    results = []
    count = 0

    if 'q' in request.GET:
        api_search_resp = client.search(search_term)
        results = api_search_resp.get('results', None)
        error_message = api_search_resp.get('message', None)
        count = api_search_resp.get('count', 0)

    context = {
        'search_form': search_form,
        'search_term': search_term,
        'results': results,
        'error_message': error_message,
        'count': count,
    }

    return context


def search_view(request):
    return TemplateResponse(
        request,
        'wagtail_reoako/_ajax_results.html',
        get_context(request)
    )


def modal_view(request):
    return render_modal_workflow(
        request,
        'wagtail_reoako/reoako.html',
        None,
        get_context(request),
        json_data={
            'step': 'browse',
        },
    )

