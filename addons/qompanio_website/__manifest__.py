{
    'name': 'Qompanio Website',
    'version': '19.0.1.0.0',
    'category': 'Website',
    'summary': 'Qompanio publieke website — homepage',
    'author': 'Qompanio',
    'website': 'https://qompanio.be',
    'depends': ['website'],
    'data': [
        'views/website_layout.xml',
        'views/website_pages.xml',
        'data/website_data.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'qompanio_website/static/src/css/qompanio_website.css',
        ],
    },
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
