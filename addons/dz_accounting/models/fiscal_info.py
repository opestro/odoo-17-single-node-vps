# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

import odoo.addons.decimal_precision as dp
from odoo.tools.float_utils import float_round
from odoo.exceptions import UserError, RedirectWarning, ValidationError
from datetime import datetime
import operator as py_operator
import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    vat = fields.Char(
        string="N.I.F",
        index=True,
        help="The Tax Identification Number. Complete it if the contact is subjected to government taxes. Used in some legal statements.",
    )
    nis = fields.Char(string="N.I.S")
    ai = fields.Char(string="Article d'imposition")
    code_activite = fields.Char(string="Code d'activité")
    company_registry = fields.Char(string="R.C")


class ResCompany(models.Model):
    _inherit = "res.company"

    vat = fields.Char(related="partner_id.vat", string="N.I.F", readonly=True)
    nis = fields.Char(related="partner_id.nis", string="N.I.S", readonly=True)
    ai = fields.Char(
        related="partner_id.ai", string="Article d'imposition", readonly=True
    )
    code_activite = fields.Char(
        related="partner_id.code_activite", string="Code d'activité", readonly=True
    )
    company_registry = fields.Char(
        related="partner_id.company_registry", string="R.C", readonly=True
    )
