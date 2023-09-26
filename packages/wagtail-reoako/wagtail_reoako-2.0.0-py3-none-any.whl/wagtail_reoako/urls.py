from django.urls import re_path
from wagtail_reoako.views import modal_view, search_view

urlpatterns = [
    # these should be prefixed with admin route when consumed
    # i.e. url(r'^admin/', include('wagtail_reoako.urls')),
    re_path(r'^reoako-modal/?$', modal_view, name='reoako_modal'),
    re_path(r'^reoako-modal/search/?$', search_view, name='reoako_modal_search')
]
