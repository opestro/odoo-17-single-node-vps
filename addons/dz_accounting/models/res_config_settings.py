# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'



    # G50
    tap_percentage = fields.Float("Pourcentage de TAP", related="company_id.tap_percentage", readonly=False)
    tap_refaction = fields.Float("Pourcentage de rafaction de TAP", related="company_id.tap_refaction", readonly=False)

    fait_generateur = fields.Selection([('paiement', 'Encaissement'),
                                 ('livraison', 'Livraison')]
                                , string="Fait génératuer", related='company_id.fait_generateur',
                                readonly=False )

    tap_code = fields.Selection([('C 1 A 11', 'C 1 A 11'),
                               ('C 1 A 12', 'C 1 A 12'),
                               ('C 1 A 13', 'C 1 A 13'),
                               ('C 1 A 14', 'C 1 A 14')]
                                , string="CODE TAP" ,related='company_id.account_tap_code', readonly=False)

    tva_code = fields.Selection(
        [('E 3 B 11', 'E 3 B 11'),
         ('E 3 B 12', 'E 3 B 12'),
         ('E 3 B 13', 'E 3 B 13'),
         ('E 3 B 14', 'E 3 B 14'),
         ('E 3 B 15', 'E 3 B 15'),
         ('E 3 B 16', 'E 3 B 16'),
         ('E 3 B 21', 'E 3 B 21'),
         ('E 3 B 22', 'E 3 B 22'),
         ('E 3 B 23', 'E 3 B 23'),
         ('E 3 B 24', 'E 3 B 24'),
         ('E 3 B 25', 'E 3 B 25'),
         ('E 3 B 26', 'E 3 B 26'),
         ('E 3 B 28', 'E 3 B 28'),
         ('E 3 B 31', 'E 3 B 31'),
         ('E 3 B 32', 'E 3 B 32'),
         ('E 3 B 33', 'E 3 B 33'),
         ('E 3 B 34', 'E 3 B 34'),
         ('E 3 B 35', 'E 3 B 35'),
         ('E 3 B 36', 'E 3 B 36'),
         ('E 3 B 37', 'E 3 B 37')] ,string="CODE TVA", related='company_id.account_tva_code', readonly=False)

    tap_credit_account_id = fields.Many2one('account.account', string="Compte TAP crédit", related='company_id.account_tap_credit_account_id', readonly=False)
    tap_debit_account_id = fields.Many2one('account.account', string="Compte TAP débit", related='company_id.account_tap_debit_account_id', readonly=False)
    tva_credit_account_id = fields.Many2one('account.account', string="Compte TVA à décaisser", related='company_id.account_tva_credit_account_id', readonly=False)
    tva_debit_account_id = fields.Many2one('account.account', string="Compte crédit de TVA", related='company_id.account_tva_debit_account_id', readonly=False)

    # IBS

    percentage_ibs = fields.Float('IBS Pourcentage', related='company_id.account_percentage_ibs', readonly=False)
    start_year_ibs = fields.Integer('Année début activité', related='company_id.account_start_year_ibs', readonly=False)
    ibs_credit_account_id = fields.Many2one('account.account', string="IBS Compte crédit", related='company_id.account_ibs_credit_account_id', readonly=False)
    ibs_debit_account_id = fields.Many2one('account.account', string="IBS Compte débit", related='company_id.account_ibs_debit_account_id', readonly=False)

    # IRG
    irg_debit_account_id = fields.Many2one('account.account', string="Compte IRG", related='company_id.account_irg_debit_account_id', readonly=False)

    precompte = fields.Float('Précompte', related='company_id.account_precompte', readonly=False)
    #DGI impots
    wilaya = fields.Char('Wilaya de', related='company_id.account_wilaya', readonly=False)
    commune = fields.Char('Commune de', related='company_id.account_commune', readonly=False)
    inspection = fields.Char('Inspection des impôts', related='company_id.account_inspection', readonly=False)
    recette = fields.Char('Recette des impôts', related='company_id.account_recette', readonly=False)
