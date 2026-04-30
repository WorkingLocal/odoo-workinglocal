from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    intervention_type = fields.Selection([
        ('wifi_install', 'Wifi-installatie'),
        ('wifi_audit', 'Wifi-audit'),
        ('network', 'Netwerk'),
        ('hardware', 'Hardware'),
        ('other', 'Andere'),
    ], string='Type interventie')
    location_description = fields.Char(string='Locatie')
    checklist_ids = fields.One2many('intervention.checklist', 'task_id', string='Checklist')
