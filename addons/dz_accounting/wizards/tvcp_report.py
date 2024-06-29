# -*- coding: utf-8 -*-
from datetime import date

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class BankBookWizard(models.TransientModel):
    _name = 'account.tvcp.report'

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
        current = self.env['account.liasse.config'].get_tvcp_lines(self.date_from, self.date_to)
        current.update({

            'Capital_social_1':current['line'].Capital_social_1,
        'Prime_emission_1':current['line'].Prime_emission_1,
        'Ecart_Evaluation_1':current['line'].Ecart_Evaluation_1,
        'EcartReevaluation_1':current['line'].EcartReevaluation_1,
        'ResevesResultats_1':current['line'].ResevesResultats_1,
        'Capital_social_2':current['line'].Capital_social_2,
        'Prime_emission_2':current['line'].Prime_emission_2,
        'Ecart_Evaluation_2':current['line'].Ecart_Evaluation_2,
        'EcartReevaluation_2':current['line'].EcartReevaluation_2,
        'ResevesResultats_2':current['line'].ResevesResultats_2,
        'Capital_social_22':current['line'].Capital_social_22,
        'Prime_emission_22':current['line'].Prime_emission_22,
        'Ecart_Evaluation_22':current['line'].Ecart_Evaluation_22,
        'EcartReevaluation_22':current['line'].EcartReevaluation_22,
        'ResevesResultats_22':current['line'].ResevesResultats_22,
        'Capital_social_3':current['line'].Capital_social_3,
        'Prime_emission_3':current['line'].Prime_emission_3,
        'Ecart_Evaluation_3':current['line'].Ecart_Evaluation_3,
        'EcartReevaluation_3':current['line'].EcartReevaluation_3,
        'ResevesResultats_3':current['line'].ResevesResultats_3,
        'Capital_social_4':current['line'].Capital_social_4,
        'Prime_emission_4':current['line'].Prime_emission_4,
        'Ecart_Evaluation_4':current['line'].Ecart_Evaluation_4,
        'EcartReevaluation_4':current['line'].EcartReevaluation_4,
        'ResevesResultats_4':current['line'].ResevesResultats_4,
        'Capital_social_5':current['line'].Capital_social_5,
        'Prime_emission_5':current['line'].Prime_emission_5,
        'Ecart_Evaluation_5':current['line'].Ecart_Evaluation_5,
        'EcartReevaluation_5':current['line'].EcartReevaluation_5,
        'ResevesResultats_5':current['line'].ResevesResultats_5,
        'Capital_social_6':current['line'].Capital_social_6,
        'Prime_emission_6':current['line'].Prime_emission_6,
        'Ecart_Evaluation_6':current['line'].Ecart_Evaluation_6,
        'EcartReevaluation_6':current['line'].EcartReevaluation_6,
        'ResevesResultats_6':current['line'].ResevesResultats_6,
        'Capital_social_7':current['line'].Capital_social_7,
        'Prime_emission_7':current['line'].Prime_emission_7,
        'Ecart_Evaluation_7':current['line'].Ecart_Evaluation_7,
        'EcartReevaluation_7':current['line'].EcartReevaluation_7,
        'ResevesResultats_7':current['line'].ResevesResultats_7,
        'Capital_social_8':current['line'].Capital_social_8,
        'Prime_emission_8':current['line'].Prime_emission_8,
        'Ecart_Evaluation_8':current['line'].Ecart_Evaluation_8,
        'EcartReevaluation_8':current['line'].EcartReevaluation_8,
        'ResevesResultats_8':current['line'].ResevesResultats_8,
        'Capital_social_9':current['line'].Capital_social_9,
        'Prime_emission_9':current['line'].Prime_emission_9,
        'Ecart_Evaluation_9':current['line'].Ecart_Evaluation_9,
        'EcartReevaluation_9':current['line'].EcartReevaluation_9,
        'ResevesResultats_9':current['line'].ResevesResultats_9,
        'Capital_social_10':current['line'].Capital_social_10,
        'Prime_emission_10':current['line'].Prime_emission_10,
        'Ecart_Evaluation_10':current['line'].Ecart_Evaluation_10,
        'EcartReevaluation_10':current['line'].EcartReevaluation_10,
        'ResevesResultats_10':current['line'].ResevesResultats_10,
        'Capital_social_11':current['line'].Capital_social_11,
        'Prime_emission_11':current['line'].Prime_emission_11,
        'Ecart_Evaluation_11':current['line'].Ecart_Evaluation_11,
        'EcartReevaluation_11':current['line'].EcartReevaluation_11,
        'ResevesResultats_11':current['line'].ResevesResultats_11,
        'Capital_social_12':current['line'].Capital_social_12,
        'Prime_emission_12':current['line'].Prime_emission_12,
        'Ecart_Evaluation_12':current['line'].Ecart_Evaluation_12,
        'EcartReevaluation_12':current['line'].EcartReevaluation_12,
        'ResevesResultats_12':current['line'].ResevesResultats_12,
        'Capital_social_13':current['line'].Capital_social_13,
        'Prime_emission_13':current['line'].Prime_emission_13,
        'Ecart_Evaluation_13':current['line'].Ecart_Evaluation_13,
        'EcartReevaluation_13':current['line'].EcartReevaluation_13,
        'ResevesResultats_13':current['line'].ResevesResultats_13,
        'Capital_social_14':current['line'].Capital_social_14,
        'Prime_emission_14':current['line'].Prime_emission_14,
        'Ecart_Evaluation_14':current['line'].Ecart_Evaluation_14,
        'EcartReevaluation_14':current['line'].EcartReevaluation_14,
        'ResevesResultats_14':current['line'].ResevesResultats_14

        })
        tft = {'current': current}
        data.update(tft)
        return self.env.ref('dz_accounting.tvcp_report_action').report_action(self, data=data)
