from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = 'project.project'

    unifi_design_url = fields.Char(string='UniFi Design Center')
