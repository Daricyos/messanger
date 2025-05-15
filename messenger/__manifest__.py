{
    "name": "Messenger",

    "version": "18.0.1.0.0",

    "author": "Maksym Litovchenko",

    "license": "AGPL-3",

    "category": "Productivity",

    "depends": [
        "base",
        "contacts",
        "mail"
    ],

    "data": [
        'security/ir.model.access.csv',

        'views/res_partner.xml',
        'views/res_config_settings.xml',
        'wizards/sms_exting_views.xml'
    ],

    'assets': {
        'web.assets_backend': [
            'messenger/static/src/js/*.js',
            'messenger/static/src/js/*.xml',
        ],
    },

    'installable': True,
    'application': True,
}
