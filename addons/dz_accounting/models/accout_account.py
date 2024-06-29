# -*- coding: utf-8 -*-
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError
from datetime import  datetime
from odoo.exceptions import UserError, ValidationError

class AccountAccount(models.Model):
    _inherit = 'account.account'

    first_root = fields.Char('First digit', compute='_compute_account_root_first')
    third_root = fields.Char('Second digit', compute='_compute_account_root_first')

    def _compute_account_root_first(self):
        for record in self:
            if record.code:
                record.first_root = str(record.code[0])
                if len(record.code) > 3:
                    record.third_root = str(record.code[:3])
                else:
                    record.third_root = ''
