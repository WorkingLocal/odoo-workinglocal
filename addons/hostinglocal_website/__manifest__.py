{
    'name': 'Hosting Local Website',
    'version': '19.0.1.0.0',
    'category': 'Website',
    'summary': 'Hosting Local publieke website — branding, paginas en lead-formulier',
    'author': 'Hosting Local',
    'website': 'https://hostinglocal.be',
    'depends': ['website', 'website_sale', 'crm'],
    'data': [
        'security/ir.model.access.csv',
        'views/website_layout.xml',
        'views/website_pages.xml',
        'data/website_data.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'hostinglocal_website/static/src/css/hostinglocal_website.css',
        ],
    },
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
