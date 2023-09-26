# About Wagtail Reoako

Wagtail CMS plugin for [reoako.nz](https://www.reoako.nz/). Contact the team at Reoako to get your API key.

# Installation

1. Add wagtail_reoako to INSTALLED_APPS
        
        INSTALLED_APPS = [
            ...
            'wagtail_reoako',
            ...
        ]

2. Add REOAKO API KEY to settings

        # Add Reoako settings
        REOAKO_API_KEY = '<your_api_key>' # Required. And client domains must be whitelisted
        REOAKO_API_DOMAIN = 'https://api.reoako.nz' 

    Note, any environment domains and port numbers (including dev domains) must be whitelisted against your API key. e.g. if your developing locally on http://localhost:8000 this must be whitelisted for your API key. Get in touch with the Reoako team to discuss. 

# Configuration

If you're using the default Draftail Rich Text Area and have completed the installation steps, Reoako will now be available as a tool in the editor.

If you have non standard Draftail editors defined and you'd like to add it as an additional feature, this can be defined like so:

        # Add Reoako to draftail editor.
        WAGTAILADMIN_RICH_TEXT_EDITORS = {
            'default': {
                'WIDGET': 'wagtail.admin.rich_text.DraftailRichTextArea',
                'OPTIONS': {
                    'features': [
                        ...       
                        'reoako',
                        ...
                    ]
                 }
            },
        }
