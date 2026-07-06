{
    'name': 'Working Local Theme',
    'version': '19.0.2.0.0',
    'category': 'Theme',
    'summary': 'Working Local huisstijl — backend, website, documenten en e-mail',
    'author': 'Working Local',
    'website': 'https://workinglocal.be',
    'depends': ['web', 'website', 'account', 'mail'],
    'data': [
        'data/company_data.xml',
        'views/webclient_templates.xml',
        'views/mail_templates.xml',
        'views/menu_data.xml',
        'views/website_pages.xml',
        'data/website_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            ('prepend', 'workinglocal_theme/static/src/scss/variables.scss'),
            'workinglocal_theme/static/src/scss/workinglocal_theme.scss',
        ],
        'web.assets_frontend': [
            ('prepend', 'workinglocal_theme/static/src/scss/variables.scss'),
            'workinglocal_theme/static/src/scss/login.scss',
            'workinglocal_theme/static/src/scss/website.scss',
        ],
        'web.report_assets_common': [
            'workinglocal_theme/static/src/scss/report.scss',
        ],
    },
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
