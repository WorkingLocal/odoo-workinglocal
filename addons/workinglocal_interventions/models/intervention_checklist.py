from odoo import fields, models


class InterventionChecklist(models.Model):
    _name = 'intervention.checklist'
    _description = 'Interventie checklist item'
    _order = 'sequence, id'

    task_id = fields.Many2one('project.task', required=True, ondelete='cascade', index=True)
    name = fields.Char(string='Stap', required=True)
    done = fields.Boolean(string='Klaar')
    sequence = fields.Integer(default=10)
