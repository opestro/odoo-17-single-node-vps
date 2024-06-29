# -*- coding: utf-8 -*-
from odoo import api, fields, models, SUPERUSER_ID, _
from datetime import date

class ExerciceComptable(models.Model):
    _name = "account.exercice"
    _order = 'date_from desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Nom', compute='_get_year')
    date_from = fields.Date(string='Start Date', default=date.today().replace(day=1, month=1),required=True)
    date_to = fields.Date(string='End Date', default=date.today().replace(day=31, month=12),required=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    year = fields.Char('Année', compute='_get_year')
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    resultat_impot = fields.Monetary(string='Résultat imposable', track_visibility='always', currency_field='currency_id')
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('posted', 'En cours'),
        ('closed', 'Validé'),
    ], string="State", default='draft', track_visibility='always')
    is_first = fields.Boolean('Est le premier exercice')
    previous_exercice_id = fields.Many2one('account.exercice', 'Exercice précédent',compute='_get_year')
    g50_ids = fields.One2many('declaration.g50', 'exercice_id', string="G50s")

    def action_validate(self):
        self.state = 'closed'

    def action_set_draft(self):
        self.state = 'draft'

    def _get_year(self):
        for record in self:
            record.year = str(record.date_from.year)
            record.name = 'Exercice ' + str(record.date_from.year)
            if not record.is_first:
                exercice = self.env['account.exercice'].search([]).filtered(lambda x: x.company_id.id == record.company_id.id and int(x.year) == int(record.year) - 1)
                record.previous_exercice_id = exercice.id if exercice else None
            else:
                record.previous_exercice_id = None

