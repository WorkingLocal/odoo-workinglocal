{
    'name': 'Working Local Theme',
    'version': '19.0.1.0.0',
    'category': 'Theme',
    'summary': 'Working Local huisstijl voor Odoo backend',
    'author': 'Working Local',
    'website': 'https://workinglocal.be',
    'depends': ['web'],
    'assets': {
        'web.assets_backend': [
            # Prepend: onze variabelen VOOR Odoo pre_variables laden
            ('prepend', 'workinglocal_theme/static/src/scss/variables.scss'),
        ],
        'web.assets_backend_lazy': [
            ('prepend', 'workinglocal_theme/static/src/scss/variables.scss'),
        ],
    },
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
