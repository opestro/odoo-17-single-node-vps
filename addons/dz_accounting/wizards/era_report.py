# -*- coding: utf-8 -*-
from datetime import date

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class BankBookWizard(models.TransientModel):
    _name = 'account.era.report'

    company_id = fields.Many2one('res.company', string='Company',
                                 readonly=True,
                                 default=lambda self: self.env.user.company_id)
    exercice_id = fields.Many2one('account.exercice', 'Exercice comptable', required=True)
    date_from = fields.Date(string='Start Date', related="exercice_id.date_from")
    date_to = fields.Date(string='End Date', related="exercice_id.date_to")



    def check_report(self):
        self.ensure_one()
        data = {
            'currency_id': self.company_id.currency_id,
            'nif': list(self.company_id.vat) if self.company_id.vat else [],
            'company': self.company_id.name,
            'address': self.company_id.street,
            'activity': self.company_id.activite,
            'current_year': self.date_from.year,
            'previous_year': self.date_from.year - 1,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'consolidate': True
                }
        tft = {'current': self.env['account.liasse.config'].get_era_lines(self.date_from, self.date_to)}
        data.update(tft)
        return self.env.ref('dz_accounting.era_report_action').report_action(self, data=data)
