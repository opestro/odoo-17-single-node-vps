# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)

class UpdateG50(models.TransientModel):
    _name = 'update.g50.wizard'

    tap = fields.Float('TAP')
    timbre = fields.Float('Droits de timbre')
    ibs = fields.Float('IBS')
    irg = fields.Float('IRG')
    tva = fields.Float('TVA à payer')
    tva_sale = fields.Float('TVA collectée')
    tva_purchase = fields.Float('TVA déductible')
    ca_imposable = fields.Float('C.A Imposable')


    def action_launch(self):
        """ Launch Action of Wizard"""
        self.ensure_one()
        declaration = self.env['declaration.g50'].search([('id', '=', self.env.context.get('declaration_id'))])
        if len(declaration):
            declaration.tap = self.tap
            declaration.timbre = self.timbre
            declaration.ibs = self.ibs
            declaration.irg = self.irg
            declaration.tva = self.tva
            declaration.tva_sale = self.tva_sale
            declaration.tva_purchase = self.tva_purchase
            declaration.ca_imposable = self.ca_imposable
            declaration.amount_total = self.tap + self.timbre + self.ibs + self.irg + self.tva

