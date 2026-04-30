{
    'name': 'Working Local — Interventies',
    'version': '19.0.1.0.0',
    'category': 'Services/Field Service',
    'summary': 'Interventieregistratie met checklists en PDF-rapport, gebouwd op Odoo Project',
    'author': 'Working Local',
    'website': 'https://www.workinglocal.be',
    'license': 'LGPL-3',
    'depends': ['project'],
    'data': [
        'security/ir.model.access.csv',
        'views/project_project_views.xml',
        'views/project_task_views.xml',
        'report/intervention_report.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
