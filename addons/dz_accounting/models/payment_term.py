# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
#

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError ,UserError


class AccountPaymentTerm(models.Model):
    _inherit = 'account.payment.term'

    payment_type = fields.Selection([('cash','Cash'),
                                     ('nocash','Other'),
                                     ],'Type', required=True, default='nocash')
  

