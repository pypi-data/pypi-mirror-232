from pkg_resources import parse_version
from draftjs_exporter.dom import DOM

import wagtail.admin.rich_text.editors.draftail.features as draftail_features

from wagtail import __version__ as WAGTAIL_VERSION

if parse_version(WAGTAIL_VERSION) < parse_version('3.0'):
    from wagtail.core import hooks
else:
    from wagtail import hooks

from wagtail.admin.rich_text.converters.html_to_contentstate import InlineEntityElementHandler

from .urls import urlpatterns

@hooks.register('register_admin_urls')
def wagtail_reoako_urls():
    return urlpatterns

@hooks.register("register_icons")
def register_icons(icons):
    return icons + ['wagtail_reoako/reoako_icon.svg']


def reoako_entity_decorator(props):
    """
    Draft.js ContentState to database HTML.
    Converts the reoako entities into a span tag.

    TODO:
        this is a bit ugly storing and display all this info since the headword & translation
        are only used by content editor in the cms. future state could just store id and fetch it
        from api when page is loaded.
    """
    return DOM.create_element('span', {
        'data-reoako-id': props.get('reoakoId'),
        'data-reoako-headword': props.get('reoakoHeadword'),
        'data-reoako-translation': props.get('reoakoTranslation'),
    }, props['children'])


class ReoakoEntityElementHandler(InlineEntityElementHandler):
    """
    Database HTML to Draft.js ContentState.
    Converts the span tag into a Reoako entity, with the right data.
    """
    mutability = 'IMMUTABLE'

    def get_attribute_data(self, attrs):
        """
        Take the ``stock`` value from the ``data-stock`` HTML attribute.
        """
        return {
            'reoakoTranslation': attrs.get('data-reoako-translation'),
            'reoakoHeadword': attrs.get('data-reoako-headword'),
            'reoakoId': attrs.get('data-reoako-id'),
        }


@hooks.register('register_rich_text_features')
def register_reoako_feature(features):
    features.default_features.append('reoako')
    feature_name = 'reoako'
    type_ = 'REOAKO'

    control = {
        'type': type_,
        'label': '',
        'description': 'Reoako',
        'icon': 'reoako_icon',
    }

    features.register_editor_plugin(
        'draftail', feature_name, draftail_features.EntityFeature(
            control,
            js=['wagtail_reoako/js/reoako.js'],
        )
    )

    features.register_converter_rule('contentstate', feature_name, {
        'from_database_format': {'span[data-reoako-id]': ReoakoEntityElementHandler(type_)},
        'to_database_format': {'entity_decorators': {type_: reoako_entity_decorator}},
    })
