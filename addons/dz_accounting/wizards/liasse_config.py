# -*- coding: utf-8 -*-
from datetime import date

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class BankBookWizard(models.TransientModel):
    _name = 'account.liasse.config'

    company_id = fields.Many2one('res.company', string='Company',
                                 readonly=True,
                                 default=lambda self: self.env.user.company_id)
    exercice_id = fields.Many2one('account.exercice', 'Exercice comptable', required=True)
    date_from = fields.Date(string='Start Date', related="exercice_id.date_from")
    date_to = fields.Date(string='End Date', related="exercice_id.date_to")

    def string_domain_to_list(self, domain):
        if isinstance(domain, str) and len(domain):
            domain = domain.replace(" ", "")
            domain = domain.replace("'", "")
            domain = domain.replace("(", "")
            domain = domain.replace(")", "")
            domain = domain.replace("\n", "")
            domain = domain.replace("[", "")
            domain = domain.replace("]", "")
            domain = domain.split(',')
            for d in domain:
                d = d.strip()
            i = 0
            result = []
            while i < len(domain):
                domain[i] = domain[i].strip()
                if domain[i] in ['|', '!']:
                    result.append(domain[i])
                    i = i + 1
                else:
                    result.append((domain[i], domain[i + 1], domain[i + 2]))
                    i = i + 3
            return result
        return [('id','=',False)]

    def get_tft_financier_domains(self):
        domains = {
            'Encaissement_clients': [self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_1').domain),self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_1').domain_debit),self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_1').domain_credit)],
            'Sommes_verse': [self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_2').domain),self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_2').domain_debit),self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_2').domain_credit)],
            'Interets_autres_frais': [self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_3').domain),self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_3').domain_debit),self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_3').domain_credit)],
            'Impots': [self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_4').domain),self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_4').domain_debit),self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_4').domain_credit)],
            'extraordinaires': [self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_5').domain),self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_5').domain_debit),self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_5').domain_credit)],
            'Decaissements_immo': [self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_6').domain),self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_6').domain_debit),self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_6').domain_credit)],
            'Encaissements_immo': [self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_7').domain),self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_7').domain_debit),self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_7').domain_credit)],
            'Decaissements_finance': [self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_8').domain),self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_8').domain_debit),self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_8').domain_credit)],
            'Encaissements_finance': [self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_9').domain),self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_9').domain_debit),self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_9').domain_credit)],
            'Interets_encaisses': [self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_10').domain),self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_10').domain_debit),self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_10').domain_credit)],
            'Dividendes_recus': [self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_11').domain),self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_11').domain_debit),self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_11').domain_credit)],
            'Encaissements_action': [self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_12').domain),self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_12').domain_debit),self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_12').domain_credit)],
            'Dividendes_distributions': [self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_13').domain),self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_13').domain_debit),self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_13').domain_credit)],
            'Encaissements_emprunts': [self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_14').domain),self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_14').domain_debit),self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_14').domain_credit)],
            'Remboursements_emprunts': [self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_15').domain),self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_15').domain_debit),self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_15').domain_credit)],
            'Subvention': [self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_16').domain),self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_16').domain_debit),self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_16').domain_credit)],
            'Tresorie_ou_equivalent': [self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_17').domain),self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_17').domain_debit),self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_17').domain_credit)],
        }
        return domains
    def get_era_domains(self):
        domains = {
            'era_1': [self.string_domain_to_list(self.env.ref('dz_accounting.account_report_era_liasse_1').domain)],
            'era_2': [self.string_domain_to_list(self.env.ref('dz_accounting.account_report_era_liasse_2').domain)],
            'era_3': [self.string_domain_to_list(self.env.ref('dz_accounting.account_report_era_liasse_3').domain)],
            'era_4': [self.string_domain_to_list(self.env.ref('dz_accounting.account_report_era_liasse_4').domain)],
            'era_5': [self.string_domain_to_list(self.env.ref('dz_accounting.account_report_era_liasse_5').domain)],
            'era_6': [self.string_domain_to_list(self.env.ref('dz_accounting.account_report_era_liasse_6').domain)],
            'era_7': [self.string_domain_to_list(self.env.ref('dz_accounting.account_report_era_liasse_7').domain)],
            'era_8': [self.string_domain_to_list(self.env.ref('dz_accounting.account_report_era_liasse_8').domain)],
            'era_9': [self.string_domain_to_list(self.env.ref('dz_accounting.account_report_era_liasse_9').domain)],
            'era_10': [self.string_domain_to_list(self.env.ref('dz_accounting.account_report_era_liasse_10').domain)],
            'era_11': [self.string_domain_to_list(self.env.ref('dz_accounting.account_report_era_liasse_11').domain)],
            'era_12': [self.string_domain_to_list(self.env.ref('dz_accounting.account_report_era_liasse_12').domain)],
            'era_13': [self.string_domain_to_list(self.env.ref('dz_accounting.account_report_era_liasse_13').domain)],
            'era_14': [self.string_domain_to_list(self.env.ref('dz_accounting.account_report_era_liasse_14').domain)],
            'era_15': [self.string_domain_to_list(self.env.ref('dz_accounting.account_report_era_liasse_15').domain)],
            'era_16': [self.string_domain_to_list(self.env.ref('dz_accounting.account_report_era_liasse_16').domain)],
            'era_17': [self.string_domain_to_list(self.env.ref('dz_accounting.account_report_era_liasse_17').domain)],
            'era_18': [self.string_domain_to_list(self.env.ref('dz_accounting.account_report_era_liasse_18').domain)],
            'era_19': [self.string_domain_to_list(self.env.ref('dz_accounting.account_report_era_liasse_19').domain)],
            'era_20': [self.string_domain_to_list(self.env.ref('dz_accounting.account_report_era_liasse_20').domain)],
            'era_21': [self.string_domain_to_list(self.env.ref('dz_accounting.account_report_era_liasse_21').domain)],
            'era_22': [self.string_domain_to_list(self.env.ref('dz_accounting.account_report_era_liasse_22').domain)]
        }
        return domains
    def get_bilan_financier_domains(self):
        domains = {
            'goodwill': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_actif_2').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_actif_2').domain_debit), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_actif_2').amortissement)],
            'immo_incorp': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_actif_3').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_actif_3').domain_debit), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_actif_3').amortissement)],
            'immo_corp': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_actif_4').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_actif_3').domain_debit), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_actif_3').amortissement)],
            'immo_encours': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_actif_9').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_actif_9').domain_debit), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_actif_9').amortissement)],
            'titre_equi': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_actif_11').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_actif_11').domain_debit), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_actif_11').amortissement)],
            'autres_participation': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_actif_13').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_actif_13').domain_debit), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_actif_13').amortissement)],
            'autre_titre': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_actif_14').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_actif_14').domain_debit), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_actif_14').amortissement)],
            'pret': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_actif_15').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_actif_15').domain_debit), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_actif_15').amortissement)],
            'stock_encours': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_actif_19').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_actif_19').domain_debit), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_actif_19').amortissement)],
            'clients': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_actif_21').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_actif_21').domain_debit), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_actif_21').amortissement)],
            'autre_debiteur': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_actif_22').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_actif_22').domain_debit), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_actif_22').amortissement)],
            'impots_assim': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_actif_23').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_actif_23').domain_debit), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_actif_23').amortissement)],
            'autre_creance': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_actif_24').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_actif_24').domain_debit), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_actif_24').amortissement)],
            'placements_actif': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_actif_26').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_actif_26').domain_debit), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_actif_26').amortissement)],
            'tresorerie': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_actif_27').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_actif_27').domain_debit), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_actif_27').amortissement)],
            'capital_emis': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_passif_2').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_passif_2').domain_credit)],
            'capital_non_app': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_passif_3').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_passif_3').domain_credit)],
            'prime': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_passif_4').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_passif_4').domain_credit)],
            'ecart_reeval': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_passif_5').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_passif_5').domain_credit)],
            'ecart_equi': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_passif_6').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_passif_6').domain_credit)],
            'resultat_net': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_passif_7').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_passif_7').domain_credit)],
            'autre_capitaux': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_passif_8').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_passif_8').domain_credit)],
            'emprunt_dette': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_passif_13').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_passif_13').domain_credit)],
            'impot_diff': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_passif_14').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_passif_14').domain_credit)],
            'autre_dette': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_passif_15').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_passif_15').domain_credit)],
            'provision_produit': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_passif_16').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_passif_16').domain_credit)],
            'fournisseur': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_passif_18').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_passif_18').domain_credit)],
            'impots_passif': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_passif_19').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_passif_19').domain_credit)],
            'autre_dette_passif': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_passif_20').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_passif_20').domain_credit)],
            'tresorerie_passif': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_passif_21').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_financier_passif_21').domain_credit)],
        }
        return domains
    def get_bilan_domains(self):
        domains = {
            'goodwill': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_actif_2').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_actif_2').domain_debit), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_actif_2').amortissement)],
            'immo_incorp': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_actif_3').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_actif_3').domain_debit), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_actif_3').amortissement)],
            'terrains': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_actif_5').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_actif_5').domain_debit), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_actif_5').amortissement)],
            'batiment': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_actif_6').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_actif_6').domain_debit), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_actif_6').amortissement)],
            'autre_immo_corp': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_actif_7').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_actif_7').domain_debit), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_actif_7').amortissement)],
            'immo_concession': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_actif_8').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_actif_8').domain_debit), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_actif_8').amortissement)],
            'immo_encours': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_actif_9').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_actif_9').domain_debit), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_actif_9').amortissement)],
            'titre_equi': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_actif_11').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_actif_11').domain_debit), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_actif_11').amortissement)],
            'autres_participation': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_actif_13').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_actif_13').domain_debit), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_actif_13').amortissement)],
            'autre_titre': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_actif_14').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_actif_14').domain_debit), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_actif_14').amortissement)],
            'pret': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_actif_15').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_actif_15').domain_debit), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_actif_15').amortissement)],
            'impots_actif': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_actif_16').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_actif_16').domain_debit), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_actif_16').amortissement)],
            'stock_encours': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_actif_19').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_actif_19').domain_debit), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_actif_19').amortissement)],
            'clients': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_actif_21').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_actif_21').domain_debit), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_actif_21').amortissement)],
            'autre_debiteur': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_actif_22').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_actif_22').domain_debit), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_actif_22').amortissement)],
            'impots_assim': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_actif_23').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_actif_23').domain_debit), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_actif_23').amortissement)],
            'autre_creance': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_actif_24').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_actif_24').domain_debit), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_actif_24').amortissement)],
            'placements_actif': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_actif_26').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_actif_26').domain_debit), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_actif_26').amortissement)],
            'tresorerie': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_actif_27').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_actif_27').domain_debit), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_actif_27').amortissement)],
            'capital_emis': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_passif_2').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_passif_2').domain_credit)],
            'capital_non_app': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_passif_3').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_passif_3').domain_credit)],
            'prime': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_passif_4').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_passif_4').domain_credit)],
            'ecart_reeval': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_passif_5').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_passif_5').domain_credit)],
            'ecart_equi': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_passif_6').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_passif_6').domain_credit)],
            'resultat_net': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_passif_7').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_passif_7').domain_credit)],
            'autre_capitaux': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_passif_8').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_passif_8').domain_credit)],
            'emprunt_dette': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_passif_13').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_passif_13').domain_credit)],
            'impot_diff': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_passif_14').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_passif_14').domain_credit)],
            'autre_dette': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_passif_15').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_passif_15').domain_credit)],
            'provision_produit': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_passif_16').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_passif_16').domain_credit)],
            'fournisseur': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_passif_18').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_passif_18').domain_credit)],
            'impots_passif': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_passif_19').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_passif_19').domain_credit)],
            'autre_dette_passif': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_passif_20').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_passif_20').domain_credit)],
            'tresorerie_passif': [self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_passif_21').domain), self.string_domain_to_list(self.env.ref('dz_accounting.report_bilan_passif_21').domain_credit)],
        }
        return domains
    def get_compte_res_financier_domains(self):
        domains = {
        'Ventes_marchandises':self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_27').domain),
        'Variations_stocks':self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_28').domain),
        'Production_immobilise':self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_35').domain),
        'Subventions':self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_36').domain),
        'Achats_de_marchandises':self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_38').domain),
        'Services_exterieurs':self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_39').domain),
        'Charges_de_personnel':self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_58').domain),
        'Impots_et_taxes':self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_59').domain),
        'Autres_produits_operationnels':self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_62').domain),
        'Autres_charges_operationnelles':self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_63').domain),
        'Dotations_aux_amortissements':self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_64').domain),
        'Reprise_sur_pertes':self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_67').domain),
        'Produits_financier':self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_69').domain),
        'Charges_financiere':self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_70').domain),
        'Elements_extraordinaires':self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_73').domain),
        'Elements_extraordinaires_2':self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_74').domain),
        'Impots_exigibles_sur':self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_76').domain),
        'Impots_differes_variations':self.string_domain_to_list(self.env.ref('dz_accounting.account_report_tcr_financier_liasse_77').domain),
        }
        return domains
    def get_compte_res_domains(self):
        domains = {
        'Ventes_marchandises':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_27').domain),
        'Produits_fabrique':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_28').domain),
        'Prestations_de_services':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_29').domain),
        'Vente_de_travaux':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_30').domain),
        'Produits_annexe':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_31').domain),
        'Rabais_remises_1':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_32').domain),
        'Production_stocke':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_34').domain),
        'Production_immobilise':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_35').domain),
        'Subventions':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_36').domain),
        'Achats_de_marchandises':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_38').domain),
        'Matieres_premiere':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_39').domain),
        'Autres_approvisionnement':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_40').domain),
        'Variations_des_stocks':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_41').domain),
        'Achats_marchandises':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_42').domain),
        'Autres_consommation':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_43').domain),
        'Rabais_remises_2':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_44').domain),
        'Sous_traitance_generale':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_45').domain),
        'Locations_field':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_47').domain),
        'Entretien_reparations_et':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_48').domain),
        'Primes':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_49').domain),
        'Personnel_exterieur':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_50').domain),
        'Remuneration':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_51').domain),
        'Publicite_field':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_52').domain),
        'Deplacements_missions_et':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_53').domain),
        'Autres_service':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_54').domain),
        'Rabais__remises':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_55').domain),
        'Charges_de_personnel':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_58').domain),
        'Impots_et_taxes':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_59').domain),
        'Autres_produits_operationnels':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_62').domain),
        'Autres_charges_operationnelles':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_63').domain),
        'Dotations_aux_amortissements':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_64').domain),
        'Provision__field':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_65').domain),
        'Pertes_de_valeur':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_66').domain),
        'Reprise_sur_pertes':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_67').domain),
        'Produits_financier':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_69').domain),
        'Charges_financiere':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_70').domain),
        'Elements_extraordinaires':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_73').domain),
        'Elements_extraordinaires_2':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_74').domain),
        'Impots_exigibles_sur':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_76').domain),
        'Impots_differes_variations':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_77').domain),
        }
        return domains
    def get_charges_prod_domains(self):
        domains = {
        'charges_locatives':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_87').domain),
        'etudes_recherche':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_88').domain),
        'documentation_diver':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_89').domain),
        'transports_biens':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_90').domain),
        'frais_postaux':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_91').domain),
        'services_bancaires':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_92').domain),
        'cotisation_divers':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_93').domain),
        'remunerations_personnel':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_95').domain),
        'remunerations_exploitation':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_96').domain),
        'cotisations_organismes':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_97').domain),
        'charges_sociales_expl':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_98').domain),
        'autres_charges_sociales':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_99').domain),
        'autres_charges_personnel':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_100').domain),
        'impot_versements':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_102').domain),
        'impot_non_recuperables':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_103').domain),
        'impot_autres_taxes':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_104').domain),
        'redevances_pour_concessions':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_106').domain),
        'moins_values_sur':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_107').domain),
        'jetons_presence':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_108').domain),
        'perte_creances':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_109').domain),
        'quot_part':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_110').domain),
        'amendes_penalite':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_111').domain),
        'charges_except':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_112').domain),
        'autres_charges_gestion':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_113').domain),
        'redevances_concessions':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_115').domain),
        'plus_values':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_116').domain),
        'jetons_presence_produit':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_117').domain),
        'quotes_parts_sub':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_118').domain),
        'quote_part_res':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_119').domain),
        'rentre_creances':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_120').domain),
        'produits_except':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_121').domain),
        'autres_produits':self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_122').domain),
        }
        return domains
    def get_ammo_domains(self):
        domains = {
            'goodwill_amort': self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_123').domain),
            'immo_incorp_amort': self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_124').domain),
            'immo_corp_amort': self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_125').domain),
            'participation_amort': self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_126').domain),
            'autre_actif_amort': self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_127').domain),
        }
        return domains
    def get_imo_domains(self):
        domains = {
            'goodwill_amort': self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_128').domain),
            'immo_incorp_amort': self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_129').domain),
            'immo_corp_amort': self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_130').domain),
            'participation_amort': self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_131').domain),
            'autre_actif_amort': self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_132').domain),
        }
        return domains

    def get_stock_domains(self,intermittent=False):
        domains = {
            'Stocks_marchandises': self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_79_a').domain),
            'Matieres_fournitures': self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_79').domain),
            'Autres_approvisionnements': self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_80').domain),
            'Encours_production_biens': self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_81').domain),
            'Encours_production_services': self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_82').domain),
            'Stocks_produits': self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_83').domain),
            'Stocks_provenant': self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_84').domain),
            'Stocks_exterieur': self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_85').domain),
        }
        if intermittent:
            domains = {
                'Stocks_marchandises': self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_79_a_intermittent').domain),
                'Matieres_fournitures': self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_79_intermittent').domain),
                'Autres_approvisionnements': self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_80_intermittent').domain),
                'Encours_production_biens': self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_81_intermittent').domain),
                'Encours_production_services': self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_82_intermittent').domain),
                'Stocks_produits': self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_83_intermittent').domain),
                'Stocks_provenant': self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_84_intermittent').domain),
                'Stocks_exterieur': self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_85_intermittent').domain),
            }

        return domains
    def get_fluctuation_domains(self):
        domains = {
            'fluctuation': self.string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_85_fluctuation').domain),
        }
        return domains

    def get_account_balance(self, accounts,date_from=None,date_to=None,etat = None):
        if date_from:
            line_ids = self.env['account.move.line'].search([('move_id.state', '=', 'posted'),('move_id.is_closing', '!=', True),
                                                         ('date','<=',date_to),('date','>=',date_from),
                                                         ('account_id', 'in', accounts.mapped('id'))])
        else:
            line_ids = self.env['account.move.line'].search([('move_id.state', '=', 'posted'), ('date', '<=', date_to),
                                                             ('account_id', 'in', accounts.mapped('id'))])
        if str(etat) == 'C':

            credit = sum(line_ids.mapped('credit'))
            debit = sum(line_ids.mapped('debit'))
            if credit > debit:
                return credit - debit
            else:
                return 0
        if str(etat) == 'D':
            debit = sum(line_ids.mapped('debit'))
            credit = sum(line_ids.mapped('credit'))
            if debit > credit:
                return debit - credit
            else:
                return 0
        return sum(line_ids.mapped('balance'))
    def get_ecriture_moves(self, accounts,date_from=None,date_to=None,etat = None):
        if date_from:
            line_ids = self.env['account.move.line'].search([('move_id.state', '=', 'posted'),('move_id.is_closing', '!=', True),
                                                         ('date','<=',date_to),('date','>=',date_from),
                                                         ('account_id', 'in', accounts.mapped('id'))])
        else:
            line_ids = self.env['account.move.line'].search([('move_id.state', '=', 'posted'),('move_id.is_closing', '!=', True), ('date', '<=', date_to),
                                                             ('account_id', 'in', accounts.mapped('id'))])

        new_line_ids = line_ids.filtered(lambda l: l.move_id.contain_tft_accounts is True)
        if str(etat) == 'C':
            credit = sum(new_line_ids.mapped('credit'))
            return credit
        if str(etat) == 'D':
            debit = sum(new_line_ids.mapped('debit'))
            return debit
        return sum(new_line_ids.mapped('balance'))

    def get_imo_tax_sum(self, accounts,date_from=None,date_to=None,etat = None):
        if date_from:
            line_ids = self.env['account.move.line'].search([('move_id.state', '=', 'posted'),
                                                         ('date','<=',date_to),('date','>=',date_from),
                                                         ('account_id', 'in', accounts.mapped('id'))])
        else:
            line_ids = self.env['account.move.line'].search([('move_id.state', '=', 'posted'), ('date', '<=', date_to),
                                                             ('account_id', 'in', accounts.mapped('id'))])

        return sum(line_ids.mapped('price_total')) - sum(line_ids.mapped('price_subtotal'))

    def get_tft_financier_lines(self, date_from, date_to):
        env = self.env['account.account']
        domains = self.get_tft_financier_domains()
        Encaissement_clients = self.get_ecriture_moves(env.search(domains['Encaissement_clients'][0]), date_from, date_to) + self.get_ecriture_moves(env.search(domains['Encaissement_clients'][1]), date_from, date_to, 'D') + self.get_ecriture_moves(env.search(domains['Encaissement_clients'][2]), date_from, date_to, 'C')
        Sommes_verse = self.get_ecriture_moves(env.search(domains['Sommes_verse'][0]), date_from, date_to) + self.get_ecriture_moves(env.search(domains['Sommes_verse'][1]), date_from, date_to, 'D') + self.get_ecriture_moves(env.search(domains['Sommes_verse'][2]), date_from, date_to, 'C')
        Interets_autres_frais = self.get_ecriture_moves(env.search(domains['Interets_autres_frais'][0]), date_from, date_to) + self.get_ecriture_moves(env.search(domains['Interets_autres_frais'][1]), date_from, date_to, 'D') + self.get_ecriture_moves(env.search(domains['Interets_autres_frais'][2]), date_from, date_to, 'C')
        Impots = self.get_ecriture_moves(env.search(domains['Impots'][0]), date_from, date_to) + self.get_ecriture_moves(env.search(domains['Impots'][1]), date_from, date_to, 'D') + self.get_ecriture_moves(env.search(domains['Impots'][2]), date_from, date_to, 'C')
        extraordinaires = self.get_ecriture_moves(env.search(domains['extraordinaires'][0]), date_from, date_to) + self.get_ecriture_moves(env.search(domains['extraordinaires'][1]), date_from, date_to, 'D') + self.get_ecriture_moves(env.search(domains['extraordinaires'][2]), date_from, date_to, 'C')
        Decaissements_immo = self.get_ecriture_moves(env.search(domains['Decaissements_immo'][0]), date_from, date_to) + self.get_ecriture_moves(env.search(domains['Decaissements_immo'][1]), date_from, date_to, 'D') + self.get_ecriture_moves(env.search(domains['Decaissements_immo'][2]), date_from, date_to, 'C')
        Encaissements_immo = - self.get_ecriture_moves(env.search(domains['Encaissements_immo'][0]), date_from, date_to) + self.get_ecriture_moves(env.search(domains['Encaissements_immo'][1]), date_from, date_to, 'D') + self.get_ecriture_moves(env.search(domains['Encaissements_immo'][2]), date_from, date_to, 'C')
        Decaissements_finance = self.get_ecriture_moves(env.search(domains['Decaissements_finance'][0]), date_from, date_to) + self.get_ecriture_moves(env.search(domains['Decaissements_finance'][1]), date_from, date_to, 'D') + self.get_ecriture_moves(env.search(domains['Decaissements_finance'][2]), date_from, date_to, 'C')
        Encaissements_finance = self.get_ecriture_moves(env.search(domains['Encaissements_finance'][0]), date_from, date_to) + self.get_ecriture_moves(env.search(domains['Encaissements_finance'][1]), date_from, date_to, 'D') + self.get_ecriture_moves(env.search(domains['Encaissements_finance'][2]), date_from, date_to, 'C')
        Interets_encaisses = self.get_ecriture_moves(env.search(domains['Interets_encaisses'][0]), date_from, date_to) + self.get_ecriture_moves(env.search(domains['Interets_encaisses'][1]), date_from, date_to, 'D') + self.get_ecriture_moves(env.search(domains['Interets_encaisses'][2]), date_from, date_to, 'C')
        Dividendes_recus = self.get_ecriture_moves(env.search(domains['Dividendes_recus'][0]), date_from, date_to) + self.get_ecriture_moves(env.search(domains['Dividendes_recus'][1]), date_from, date_to, 'D') + self.get_ecriture_moves(env.search(domains['Dividendes_recus'][2]), date_from, date_to, 'C')
        Encaissements_action = self.get_ecriture_moves(env.search(domains['Encaissements_action'][0]), date_from, date_to) + self.get_ecriture_moves(env.search(domains['Encaissements_action'][1]), date_from, date_to, 'D') + self.get_ecriture_moves(env.search(domains['Encaissements_action'][2]), date_from, date_to, 'C')
        Dividendes_distributions = self.get_ecriture_moves(env.search(domains['Dividendes_distributions'][0]), date_from, date_to) + self.get_ecriture_moves(env.search(domains['Dividendes_distributions'][1]), date_from, date_to, 'D') + self.get_ecriture_moves(env.search(domains['Dividendes_distributions'][2]), date_from, date_to, 'C')
        Encaissements_emprunts = self.get_ecriture_moves(env.search(domains['Encaissements_emprunts'][0]), date_from, date_to) + self.get_ecriture_moves(env.search(domains['Encaissements_emprunts'][1]), date_from, date_to, 'D') + self.get_ecriture_moves(env.search(domains['Encaissements_emprunts'][2]), date_from, date_to, 'C')
        Remboursements_emprunts = self.get_ecriture_moves(env.search(domains['Remboursements_emprunts'][0]), date_from, date_to) + self.get_ecriture_moves(env.search(domains['Remboursements_emprunts'][1]), date_from, date_to, 'D') + self.get_ecriture_moves(env.search(domains['Remboursements_emprunts'][2]), date_from, date_to, 'C')
        Subvention = self.get_ecriture_moves(env.search(domains['Subvention'][0]), date_from, date_to) + self.get_ecriture_moves(env.search(domains['Subvention'][1]), date_from, date_to, 'D') + self.get_ecriture_moves(env.search(domains['Subvention'][2]), date_from, date_to, 'C')
        Tresorie_ou_equivalent_debut = self.get_account_balance(env.search(domains['Tresorie_ou_equivalent'][0]), False, date_from)
        Tresorie_ou_equivalent_fin = self.get_account_balance(env.search(domains['Tresorie_ou_equivalent'][0]), False, date_to)

        flux_op_avant_extra = Encaissement_clients + Sommes_verse + Interets_autres_frais + Impots
        flux_op_net = flux_op_avant_extra + extraordinaires
        flux_inves = Decaissements_immo + Encaissements_immo + Decaissements_finance + Encaissements_finance + Interets_encaisses + Dividendes_recus
        flux_finance = Encaissements_action + Dividendes_distributions + Encaissements_emprunts + Remboursements_emprunts
        variation_abc = flux_op_net + flux_inves + flux_finance
        variation_periode = Tresorie_ou_equivalent_fin - Tresorie_ou_equivalent_debut

        return {
            'Encaissement_clients':-Encaissement_clients,
            'Sommes_verse': +Sommes_verse,
            'Interets_autres_frais':+Interets_autres_frais,
            'Impots':+Impots,
            'extraordinaires':-extraordinaires,
            'Decaissements_immo':+Decaissements_immo,
            'Encaissements_immo':-Encaissements_immo,
            'Decaissements_finance':+Decaissements_finance,
            'Encaissements_finance':-Encaissements_finance,
            'Interets_encaisses':-Interets_encaisses,
            'Dividendes_recus':-Dividendes_recus,
            'Encaissements_action':-Encaissements_action,
            'Dividendes_distributions':+Dividendes_distributions,
            'Encaissements_emprunts':-Encaissements_emprunts,
            'Remboursements_emprunts':+Remboursements_emprunts,
            'Subvention':Subvention,
            'Tresorie_ou_equivalent_debut':Tresorie_ou_equivalent_debut,
            'Tresorie_ou_equivalent_fin':Tresorie_ou_equivalent_fin,
            'flux_op_avant_extra':-flux_op_avant_extra,
            'flux_op_net':-flux_op_net,
            'flux_inves':-flux_inves,
            'flux_finance':-flux_finance,
            'variation_abc':-variation_abc,
            'variation_periode':variation_periode
        }
    def get_era_lines(self, date_from, date_to):
        env = self.env['account.account']
        domains = self.get_era_domains()
        era_1 = self.get_account_balance(env.search(domains['era_1'][0]), date_from,date_to)
        era_2 = self.get_account_balance(env.search(domains['era_2'][0]), date_from,date_to)
        era_3 = self.get_account_balance(env.search(domains['era_3'][0]), date_from,date_to)
        era_4 = self.get_account_balance(env.search(domains['era_4'][0]), date_from,date_to)
        era_5 = self.get_account_balance(env.search(domains['era_5'][0]), date_from,date_to)
        era_6 = self.get_account_balance(env.search(domains['era_6'][0]),False ,date_to)
        era_7 = self.get_account_balance(env.search(domains['era_7'][0]), date_from,date_to)
        era_8 = self.get_ecriture_moves(env.search(domains['era_8'][0]), date_from,date_to, 'D')
        era_9 = self.get_account_balance(env.search(domains['era_9'][0]), date_from,date_to)
        era_10 = self.get_account_balance(env.search(domains['era_10'][0]), date_from,date_to)
        era_11 = self.get_account_balance(env.search(domains['era_11'][0]), date_from,date_to)
        era_12 = self.get_account_balance(env.search(domains['era_12'][0]), date_from,date_to)
        era_13 = self.get_account_balance(env.search(domains['era_13'][0]), date_from,date_to)
        era_14 = self.get_account_balance(env.search(domains['era_14'][0]), date_from,date_to)
        era_15 = self.get_account_balance(env.search(domains['era_15'][0]), date_from,date_to)
        era_16 = self.get_account_balance(env.search(domains['era_16'][0]), date_from,date_to)
        era_17 = self.get_account_balance(env.search(domains['era_17'][0]), date_from,date_to)
        era_18 = self.get_account_balance(env.search(domains['era_18'][0]), date_from,date_to)
        era_19 = era_7 if era_7 > 0 else 0
        fiscal_line = self.env['res.fiscal.line'].search([('date_from', '=', date_from), ('date_to', '=', date_to)])
        era_20 = fiscal_line.res_fiscal_net if fiscal_line else 0
        era_21 = self.get_account_balance(env.search(domains['era_21'][0]), date_from,date_to)
        era_22 = self.get_account_balance(env.search(domains['era_22'][0]), date_from,date_to)
        return {
            'era_1': -era_1,
            'era_2': era_2,
            'era_3': -era_3,
            'era_4': -era_4,
            'era_5': era_5,
            'era_6': -era_6,
            'era_7': -era_7,
            'era_8': era_8,
            'era_9': -era_9,
            'era_10': -era_10,
            'era_11': era_11,
            'era_12': era_12,
            'era_13': era_13,
            'era_14': era_14,
            'era_15': era_15,
            'era_16': -era_16,
            'era_17': -era_17,
            'era_18': era_18,
            'era_19': era_19,
            'era_20': era_20,
            'era_21': era_21,
            'era_22': era_22
        }

    def get_tvcp_lines(self, date_from, date_to):
        tvcp_line = self.env['report.tvcp'].search([('date_from', '=', date_from), ('date_to', '=', date_to)])
        solde_n_01  = tvcp_line.Capital_social_1 + tvcp_line.Capital_social_2 + tvcp_line.Capital_social_22 + tvcp_line.Capital_social_3 + tvcp_line.Capital_social_4 + tvcp_line.Capital_social_5 + tvcp_line.Capital_social_6 + tvcp_line.Capital_social_7
        solde_n_02 = tvcp_line.Prime_emission_1 + tvcp_line.Prime_emission_2 + tvcp_line.Prime_emission_22 + tvcp_line.Prime_emission_3 + tvcp_line.Prime_emission_4 + tvcp_line.Prime_emission_5 + tvcp_line.Prime_emission_6 + tvcp_line.Prime_emission_7
        solde_n_03 = tvcp_line.Ecart_Evaluation_1 + tvcp_line.Ecart_Evaluation_2 + tvcp_line.Ecart_Evaluation_22 + tvcp_line.Ecart_Evaluation_3 + tvcp_line.Ecart_Evaluation_4 + tvcp_line.Ecart_Evaluation_5 + tvcp_line.Ecart_Evaluation_6 + tvcp_line.Ecart_Evaluation_7
        solde_n_04 = tvcp_line.EcartReevaluation_1 + tvcp_line.EcartReevaluation_2 + tvcp_line.EcartReevaluation_22 + tvcp_line.EcartReevaluation_3 + tvcp_line.EcartReevaluation_4 + tvcp_line.EcartReevaluation_5 + tvcp_line.EcartReevaluation_6 + tvcp_line.EcartReevaluation_7
        solde_n_05 = tvcp_line.ResevesResultats_1 + tvcp_line.ResevesResultats_2 + tvcp_line.ResevesResultats_22 + tvcp_line.ResevesResultats_3 + tvcp_line.ResevesResultats_4 + tvcp_line.ResevesResultats_5 + tvcp_line.ResevesResultats_6 + tvcp_line.ResevesResultats_7

        solde_n_11 = solde_n_01 + tvcp_line.Capital_social_8 + tvcp_line.Capital_social_9 + tvcp_line.Capital_social_10 + tvcp_line.Capital_social_11 + tvcp_line.Capital_social_12 + tvcp_line.Capital_social_13 + tvcp_line.Capital_social_14
        solde_n_12 = solde_n_02 + tvcp_line.Prime_emission_8 + tvcp_line.Prime_emission_9 + tvcp_line.Prime_emission_10 + tvcp_line.Prime_emission_11 + tvcp_line.Prime_emission_12 + tvcp_line.Prime_emission_13 + tvcp_line.Prime_emission_14
        solde_n_13 = solde_n_03 + tvcp_line.Ecart_Evaluation_8 + tvcp_line.Ecart_Evaluation_9 + tvcp_line.Ecart_Evaluation_10 + tvcp_line.Ecart_Evaluation_11 + tvcp_line.Ecart_Evaluation_12 + tvcp_line.Ecart_Evaluation_13 + tvcp_line.Ecart_Evaluation_14
        solde_n_14 = solde_n_04 + + tvcp_line.EcartReevaluation_8 + tvcp_line.EcartReevaluation_9 + tvcp_line.EcartReevaluation_10 + tvcp_line.EcartReevaluation_11 + tvcp_line.EcartReevaluation_12 + tvcp_line.EcartReevaluation_13 + tvcp_line.EcartReevaluation_14
        solde_n_15 = solde_n_05 + tvcp_line.ResevesResultats_8 + tvcp_line.ResevesResultats_9 + tvcp_line.ResevesResultats_10 + tvcp_line.ResevesResultats_11 + tvcp_line.ResevesResultats_12 + tvcp_line.ResevesResultats_13 + tvcp_line.ResevesResultats_14
        return {'line':tvcp_line,
                'solde_n_01': solde_n_01,
                'solde_n_02': solde_n_02,
                'solde_n_03': solde_n_03,
                'solde_n_04': solde_n_04,
                'solde_n_05': solde_n_05,
                'solde_n_11': solde_n_11,
                'solde_n_12': solde_n_12,
                'solde_n_13': solde_n_13,
                'solde_n_14': solde_n_14,
                'solde_n_15': solde_n_15,
                }

    def get_bilan_financier_lines(self, date_from, date_to):
        env = self.env['account.account']
        domains = self.get_bilan_financier_domains()
        goodwill = self.get_account_balance(env.search(domains['goodwill'][0]),False,date_to) + self.get_account_balance(env.search(domains['goodwill'][1]),False,date_to,'D')
        goodwill_amort = self.get_account_balance(env.search(domains['goodwill'][2]),False,date_to)
        immo_incorp = self.get_account_balance(env.search(domains['immo_incorp'][0]),False,date_to) + self.get_account_balance(env.search(domains['immo_incorp'][1]),False,date_to,'D')
        immo_incorp_amort = self.get_account_balance(env.search(domains['immo_incorp'][2]),False,date_to)
        immo_corp = self.get_account_balance(env.search(domains['immo_corp'][0]),False,date_to) + self.get_account_balance(env.search(domains['immo_corp'][1]),False,date_to,'D')
        immo_corp_amort = self.get_account_balance(env.search(domains['immo_corp'][2]),False,date_to)
        immo_encours = self.get_account_balance(env.search(domains['immo_encours'][0]),False,date_to) + self.get_account_balance(env.search(domains['immo_encours'][1]),False,date_to,'D')
        immo_encours_amort = self.get_account_balance(env.search(domains['immo_encours'][2]),False,date_to)
        titre_equi = self.get_account_balance(env.search(domains['titre_equi'][0]),False,date_to) + self.get_account_balance(env.search(domains['titre_equi'][1]),False,date_to,'D')
        titre_equi_amort = self.get_account_balance(env.search(domains['titre_equi'][2]),False,date_to)
        autres_participation = self.get_account_balance(env.search(domains['autres_participation'][0]),False,date_to) + self.get_account_balance(env.search(domains['autres_participation'][1]),False,date_to,'D')
        autres_participation_amort = self.get_account_balance(env.search(domains['autres_participation'][2]),False,date_to)
        autre_titre = self.get_account_balance(env.search(domains['autre_titre'][0]),False,date_to) + self.get_account_balance(env.search(domains['autre_titre'][1]),False,date_to,'D')
        autre_titre_amort = self.get_account_balance(env.search(domains['autre_titre'][2]),False,date_to)
        pret = self.get_account_balance(env.search(domains['pret'][0]),False,date_to) + self.get_account_balance(env.search(domains['pret'][1]),False,date_to,'D')
        pret_amort = self.get_account_balance(env.search(domains['pret'][2]),False,date_to)
        stock_encours = self.get_account_balance(env.search(domains['stock_encours'][0]),False,date_to) + self.get_account_balance(env.search(domains['stock_encours'][1]),False,date_to,'D')
        stock_encours_amort = self.get_account_balance(env.search(domains['stock_encours'][2]),False,date_to)
        clients = self.get_account_balance(env.search(domains['clients'][0]),False,date_to) + self.get_account_balance(env.search(domains['clients'][1]),False,date_to,'D')
        clients_amort = self.get_account_balance(env.search(domains['clients'][2]),False,date_to)
        autre_debiteur = self.get_account_balance(env.search(domains['autre_debiteur'][0]),False,date_to) + self.get_account_balance(env.search(domains['autre_debiteur'][1]),False,date_to,'D')
        autre_debiteur_amort = self.get_account_balance(env.search(domains['autre_debiteur'][2]),False,date_to)
        impots_assim = self.get_account_balance(env.search(domains['impots_assim'][0]),False,date_to) + self.get_account_balance(env.search(domains['impots_assim'][1]),False,date_to,'D')
        impots_assim = impots_assim if impots_assim > 0 else 0
        impots_assim_amort = 0
        autre_creance = self.get_account_balance(env.search(domains['autre_creance'][0]),False,date_to) + self.get_account_balance(env.search(domains['autre_creance'][1]),False,date_to,'D')
        autre_creance_amort = 0
        placements_actif = self.get_account_balance(env.search(domains['placements_actif'][0]),False,date_to) + self.get_account_balance(env.search(domains['placements_actif'][1]),False,date_to,'D')
        placements_actif_amort = 0
        tresorerie = self.get_account_balance(env.search(domains['tresorerie'][0]),False,date_to) + self.get_account_balance(env.search(domains['tresorerie'][1]),False,date_to,'D')
        tresorerie_amort = self.get_account_balance(env.search(domains['tresorerie'][2]),False,date_to)
        immo_finance = titre_equi + autres_participation + autre_titre + pret
        immo_finance_amort = titre_equi_amort + autres_participation_amort + autre_titre_amort + pret_amort
        actif_non_courant = immo_finance + immo_encours + immo_corp + immo_incorp + goodwill
        actif_non_courant_amort = immo_finance_amort + immo_encours_amort + immo_corp_amort + immo_incorp_amort + goodwill_amort
        creance_assim = clients + autre_debiteur + impots_assim + autre_creance
        creance_assim_amort = clients_amort + autre_debiteur_amort + impots_assim_amort + autre_creance_amort
        dispo_assim = placements_actif + tresorerie
        dispo_assim_amort = placements_actif_amort + tresorerie_amort
        actif_courant = dispo_assim + stock_encours + creance_assim
        actif_courant_amort = dispo_assim_amort + stock_encours_amort + creance_assim_amort
        total_actif= actif_courant + actif_non_courant
        total_actif_amort = actif_courant_amort + actif_non_courant_amort


        #  **************   PASSIF ********************

        capital_emis = self.get_account_balance(env.search(domains['capital_emis'][0]),False,date_to) - self.get_account_balance(env.search(domains['capital_emis'][1]),False,date_to,'C')
        capital_non_app = self.get_account_balance(env.search(domains['capital_non_app'][0]),False,date_to) - self.get_account_balance(env.search(domains['capital_non_app'][1]),False,date_to,'C')
        prime = self.get_account_balance(env.search(domains['prime'][0]),False,date_to) - self.get_account_balance(env.search(domains['prime'][1]),False,date_to,'C')
        ecart_reeval = self.get_account_balance(env.search(domains['ecart_reeval'][0]),False,date_to) - self.get_account_balance(env.search(domains['ecart_reeval'][1]),False,date_to,'C')
        ecart_equi = self.get_account_balance(env.search(domains['ecart_equi'][0]),False,date_to) - self.get_account_balance(env.search(domains['ecart_equi'][1]),False,date_to,'C')
        resultat_net = self.get_account_balance(env.search(domains['resultat_net'][0]),False,date_to) - self.get_account_balance(env.search(domains['resultat_net'][1]),False,date_to,'C')
        autre_capitaux = self.get_account_balance(env.search(domains['autre_capitaux'][0]),False,date_to) - self.get_account_balance(env.search(domains['autre_capitaux'][1]),False,date_to,'C')
        emprunt_dette = self.get_account_balance(env.search(domains['emprunt_dette'][0]),False,date_to) - self.get_account_balance(env.search(domains['emprunt_dette'][1]),False,date_to,'C')
        impot_diff = self.get_account_balance(env.search(domains['impot_diff'][0]),False,date_to) - self.get_account_balance(env.search(domains['impot_diff'][1]),False,date_to,'C')
        autre_dette = self.get_account_balance(env.search(domains['autre_dette'][0]),False,date_to) - self.get_account_balance(env.search(domains['autre_dette'][1]),False,date_to,'C')
        provision_produit = self.get_account_balance(env.search(domains['provision_produit'][0]),False,date_to) - self.get_account_balance(env.search(domains['provision_produit'][1]),False,date_to,'C')
        fournisseur = self.get_account_balance(env.search(domains['fournisseur'][0]),False,date_to) - self.get_account_balance(env.search(domains['fournisseur'][1]),False,date_to,'C')
        impots_passif = self.get_account_balance(env.search(domains['impots_passif'][0]),False,date_to) - self.get_account_balance(env.search(domains['impots_passif'][1]),False,date_to,'C')
        impots_passif = impots_passif if impots_passif < 0 else 0
        autre_dette_passif = self.get_account_balance(env.search(domains['autre_dette_passif'][0]),False,date_to) - self.get_account_balance(env.search(domains['autre_dette_passif'][1]),False,date_to,'C')
        tresorerie_passif = self.get_account_balance(env.search(domains['tresorerie_passif'][0]),False,date_to) - self.get_account_balance(env.search(domains['tresorerie_passif'][1]),False,date_to,'C')
        capitaux_propres = capital_emis + capital_non_app + prime + ecart_reeval + ecart_equi + resultat_net + autre_capitaux
        passif_non_courant = emprunt_dette + impot_diff + autre_dette + provision_produit
        passif_courant = fournisseur + impots_passif + autre_dette_passif + tresorerie_passif
        total_passif = capitaux_propres + passif_non_courant + passif_courant

        return {
            'goodwill':goodwill,
            'goodwill_amort': - goodwill_amort,
            'immo_incorp':immo_incorp,
            'immo_incorp_amort': - immo_incorp_amort,
            'immo_encours': immo_encours,
            'immo_encours_amort': - immo_encours_amort,
            'titre_equi':titre_equi,
            'titre_equi_amort': - titre_equi_amort,
            'autres_participation':autres_participation,
            'autres_participation_amort': - autres_participation_amort,
            'autre_titre':autre_titre,
            'autre_titre_amort': - autre_titre_amort,
            'pret':pret,
            'pret_amort': - pret_amort,
            'stock_encours':stock_encours,
            'stock_encours_amort': - stock_encours_amort,
            'clients':clients,
            'clients_amort': - clients_amort,
            'autre_debiteur':autre_debiteur,
            'autre_debiteur_amort': - autre_debiteur_amort,
            'impots_assim':impots_assim if impots_assim > 0 else 0,
            'impots_assim_amort': - impots_assim_amort,
            'autre_creance':autre_creance,
            'autre_creance_amort': - autre_creance_amort,
            'placements_actif':placements_actif,
            'placements_actif_amort': - placements_actif_amort,
            'tresorerie':tresorerie,
            'tresorerie_amort': - tresorerie_amort,
            'capital_emis': - capital_emis,
            'capital_non_app': - capital_non_app,
            'prime': - prime,
            'ecart_reeval': - ecart_reeval,
            'ecart_equi': - ecart_equi,
            'resultat_net': - resultat_net,
            'autre_capitaux': - autre_capitaux,
            'emprunt_dette': - emprunt_dette,
            'impot_diff': - impot_diff,
            'autre_dette': - autre_dette,
            'provision_produit': - provision_produit,
            'fournisseur': - fournisseur,
            'impots_passif': - impots_passif if impots_passif < 0 else 0,
            'autre_dette_passif': - autre_dette_passif,
            'tresorerie_passif': - tresorerie_passif,
            'immo_corp':immo_corp,
            'immo_corp_amort': - immo_corp_amort,
            'immo_finance':immo_finance,
            'immo_finance_amort': - immo_finance_amort,
            'creance_assim': creance_assim,
            'creance_assim_amort': -  creance_assim_amort,
            'dispo_assim': dispo_assim,
            'dispo_assim_amort': -  dispo_assim_amort,
            'actif_courant': actif_courant,
            'actif_courant_amort': -  actif_courant_amort,
            'actif_non_courant': actif_non_courant,
            'actif_non_courant_amort': -  actif_non_courant_amort,
            'total_actif':total_actif,
            'total_actif_amort': - total_actif_amort,
            'capitaux_propres':- capitaux_propres,
            'passif_non_courant':- passif_non_courant,
            'passif_courant': - passif_courant,
            'total_passif': - total_passif,
        }
    def get_bilan_lines(self, date_from, date_to):
        env = self.env['account.account']
        domains = self.get_bilan_domains()
        goodwill = self.get_account_balance(env.search(domains['goodwill'][0]),False,date_to) + self.get_account_balance(env.search(domains['goodwill'][1]),False,date_to,'D')
        goodwill_amort = self.get_account_balance(env.search(domains['goodwill'][2]),False,date_to)
        immo_incorp = self.get_account_balance(env.search(domains['immo_incorp'][0]),False,date_to) + self.get_account_balance(env.search(domains['immo_incorp'][1]),False,date_to,'D')
        immo_incorp_amort = self.get_account_balance(env.search(domains['immo_incorp'][2]),False,date_to)
        terrains = self.get_account_balance(env.search(domains['terrains'][0]),False,date_to) + self.get_account_balance(env.search(domains['terrains'][1]),False,date_to,'D')
        terrains_amort = self.get_account_balance(env.search(domains['terrains'][2]),False,date_to)
        batiment = self.get_account_balance(env.search(domains['batiment'][0]),False,date_to) + self.get_account_balance(env.search(domains['batiment'][1]),False,date_to,'D')
        batiment_amort = self.get_account_balance(env.search(domains['batiment'][2]),False,date_to)
        autre_immo_corp = self.get_account_balance(env.search(domains['autre_immo_corp'][0]),False,date_to) + self.get_account_balance(env.search(domains['autre_immo_corp'][1]),False,date_to,'D')
        autre_immo_corp_amort = self.get_account_balance(env.search(domains['autre_immo_corp'][2]),False,date_to)
        immo_concession = self.get_account_balance(env.search(domains['immo_concession'][0]),False,date_to) + self.get_account_balance(env.search(domains['immo_concession'][1]),False,date_to,'D')
        immo_concession_amort = self.get_account_balance(env.search(domains['immo_concession'][2]),False,date_to)
        immo_encours = self.get_account_balance(env.search(domains['immo_encours'][0]),False,date_to) + self.get_account_balance(env.search(domains['immo_encours'][1]),False,date_to,'D')
        immo_encours_amort = self.get_account_balance(env.search(domains['immo_encours'][2]),False,date_to)
        titre_equi = self.get_account_balance(env.search(domains['titre_equi'][0]),False,date_to) + self.get_account_balance(env.search(domains['titre_equi'][1]),False,date_to,'D')
        titre_equi_amort = self.get_account_balance(env.search(domains['titre_equi'][2]),False,date_to)
        autres_participation = self.get_account_balance(env.search(domains['autres_participation'][0]),False,date_to) + self.get_account_balance(env.search(domains['autres_participation'][1]),False,date_to,'D')
        autres_participation_amort = self.get_account_balance(env.search(domains['autres_participation'][2]),False,date_to)
        autre_titre = self.get_account_balance(env.search(domains['autre_titre'][0]),False,date_to) + self.get_account_balance(env.search(domains['autre_titre'][1]),False,date_to,'D')
        autre_titre_amort = self.get_account_balance(env.search(domains['autre_titre'][2]),False,date_to)
        pret = self.get_account_balance(env.search(domains['pret'][0]),False,date_to) + self.get_account_balance(env.search(domains['pret'][1]),False,date_to,'D')
        pret_amort = self.get_account_balance(env.search(domains['pret'][2]),False,date_to)
        impots_actif = self.get_account_balance(env.search(domains['impots_actif'][0]),False,date_to) + self.get_account_balance(env.search(domains['impots_actif'][1]),False,date_to,'D')
        impots_actif_amort = 0
        stock_encours = self.get_account_balance(env.search(domains['stock_encours'][0]),False,date_to) + self.get_account_balance(env.search(domains['stock_encours'][1]),False,date_to,'D')
        stock_encours_amort = self.get_account_balance(env.search(domains['stock_encours'][2]),False,date_to)
        clients = self.get_account_balance(env.search(domains['clients'][0]),False,date_to) + self.get_account_balance(env.search(domains['clients'][1]),False,date_to,'D')
        clients_amort = self.get_account_balance(env.search(domains['clients'][2]),False,date_to)
        autre_debiteur = self.get_account_balance(env.search(domains['autre_debiteur'][0]),False,date_to) + self.get_account_balance(env.search(domains['autre_debiteur'][1]),False,date_to,'D')
        autre_debiteur_amort = self.get_account_balance(env.search(domains['autre_debiteur'][2]),False,date_to)
        impots_assim = self.get_account_balance(env.search(domains['impots_assim'][0]),False,date_to) + self.get_account_balance(env.search(domains['impots_assim'][1]),False,date_to,'D')
        impots_assim = impots_assim if impots_assim > 0 else 0
        impots_assim_amort = 0
        autre_creance = self.get_account_balance(env.search(domains['autre_creance'][0]),False,date_to) + self.get_account_balance(env.search(domains['autre_creance'][1]),False,date_to,'D')
        autre_creance_amort = 0
        placements_actif = self.get_account_balance(env.search(domains['placements_actif'][0]),False,date_to) + self.get_account_balance(env.search(domains['placements_actif'][1]),False,date_to,'D')
        placements_actif_amort = 0
        tresorerie = self.get_account_balance(env.search(domains['tresorerie'][0]),False,date_to) + self.get_account_balance(env.search(domains['tresorerie'][1]),False,date_to,'D')
        tresorerie_amort = self.get_account_balance(env.search(domains['tresorerie'][2]),False,date_to)
        immo_corp = terrains + batiment + autre_immo_corp + immo_concession
        immo_corp_amort = terrains_amort + batiment_amort + autre_immo_corp_amort + immo_concession_amort
        immo_finance = titre_equi + autres_participation + autre_titre + pret + impots_actif
        immo_finance_amort = titre_equi_amort + autres_participation_amort + autre_titre_amort + pret_amort + impots_actif_amort
        actif_non_courant = immo_finance + immo_encours + immo_corp + immo_incorp + goodwill
        actif_non_courant_amort = immo_finance_amort + immo_encours_amort + immo_corp_amort + immo_incorp_amort + goodwill_amort
        creance_assim = clients + autre_debiteur + impots_assim + autre_creance
        creance_assim_amort = clients_amort + autre_debiteur_amort + impots_assim_amort + autre_creance_amort
        dispo_assim = placements_actif + tresorerie
        dispo_assim_amort = placements_actif_amort + tresorerie_amort
        actif_courant = dispo_assim + stock_encours + creance_assim
        actif_courant_amort = dispo_assim_amort + stock_encours_amort + creance_assim_amort
        total_actif= actif_courant + actif_non_courant
        total_actif_amort = actif_courant_amort + actif_non_courant_amort


        #  **************   PASSIF ********************

        capital_emis = self.get_account_balance(env.search(domains['capital_emis'][0]),False,date_to) - self.get_account_balance(env.search(domains['capital_emis'][1]),False,date_to,'C')
        capital_non_app = self.get_account_balance(env.search(domains['capital_non_app'][0]),False,date_to) - self.get_account_balance(env.search(domains['capital_non_app'][1]),False,date_to,'C')
        prime = self.get_account_balance(env.search(domains['prime'][0]),False,date_to) - self.get_account_balance(env.search(domains['prime'][1]),False,date_to,'C')
        ecart_reeval = self.get_account_balance(env.search(domains['ecart_reeval'][0]),False,date_to) - self.get_account_balance(env.search(domains['ecart_reeval'][1]),False,date_to,'C')
        ecart_equi = self.get_account_balance(env.search(domains['ecart_equi'][0]),False,date_to) - self.get_account_balance(env.search(domains['ecart_equi'][1]),False,date_to,'C')
        resultat_net = self.get_account_balance(env.search(domains['resultat_net'][0]),False,date_to) - self.get_account_balance(env.search(domains['resultat_net'][1]),False,date_to,'C')
        autre_capitaux = self.get_account_balance(env.search(domains['autre_capitaux'][0]),False,date_to) - self.get_account_balance(env.search(domains['autre_capitaux'][1]),False,date_to,'C')
        emprunt_dette = self.get_account_balance(env.search(domains['emprunt_dette'][0]),False,date_to) - self.get_account_balance(env.search(domains['emprunt_dette'][1]),False,date_to,'C')
        impot_diff = self.get_account_balance(env.search(domains['impot_diff'][0]),False,date_to) - self.get_account_balance(env.search(domains['impot_diff'][1]),False,date_to,'C')
        autre_dette = self.get_account_balance(env.search(domains['autre_dette'][0]),False,date_to) - self.get_account_balance(env.search(domains['autre_dette'][1]),False,date_to,'C')
        provision_produit = self.get_account_balance(env.search(domains['provision_produit'][0]),False,date_to) - self.get_account_balance(env.search(domains['provision_produit'][1]),False,date_to,'C')
        fournisseur = self.get_account_balance(env.search(domains['fournisseur'][0]),False,date_to) - self.get_account_balance(env.search(domains['fournisseur'][1]),False,date_to,'C')
        impots_passif = self.get_account_balance(env.search(domains['impots_passif'][0]),False,date_to) - self.get_account_balance(env.search(domains['impots_passif'][1]),False,date_to,'C')
        impots_passif = impots_passif if impots_passif < 0 else 0
        autre_dette_passif = self.get_account_balance(env.search(domains['autre_dette_passif'][0]),False,date_to) - self.get_account_balance(env.search(domains['autre_dette_passif'][1]),False,date_to,'C')
        tresorerie_passif = self.get_account_balance(env.search(domains['tresorerie_passif'][0]),False,date_to) - self.get_account_balance(env.search(domains['tresorerie_passif'][1]),False,date_to,'C')
        capitaux_propres = capital_emis + capital_non_app + prime + ecart_reeval + ecart_equi + resultat_net + autre_capitaux
        passif_non_courant = emprunt_dette + impot_diff + autre_dette + provision_produit
        passif_courant = fournisseur + impots_passif + autre_dette_passif + tresorerie_passif
        total_passif = capitaux_propres + passif_non_courant + passif_courant

        return {

        'goodwill':goodwill,
        'goodwill_amort': - goodwill_amort,
        'immo_incorp':immo_incorp,
        'immo_incorp_amort': - immo_incorp_amort,
        'terrains':terrains,
        'terrains_amort': - terrains_amort,
        'batiment':batiment,
        'batiment_amort': - batiment_amort,
        'autre_immo_corp':autre_immo_corp,
        'autre_immo_corp_amort': - autre_immo_corp_amort,
        'immo_concession':immo_concession,
        'immo_concession_amort': - immo_concession_amort,
        'immo_encours':immo_encours,
        'immo_encours_amort': - immo_encours_amort,
        'titre_equi':titre_equi,
        'titre_equi_amort': - titre_equi_amort,
        'autres_participation':autres_participation,
        'autres_participation_amort': - autres_participation_amort,
        'autre_titre':autre_titre,
        'autre_titre_amort': - autre_titre_amort,
        'pret':pret,
        'pret_amort': - pret_amort,
        'impots_actif':impots_actif,
        'impots_actif_amort': - impots_actif_amort,
        'stock_encours':stock_encours,
        'stock_encours_amort': - stock_encours_amort,
        'clients':clients,
        'clients_amort': - clients_amort,
        'autre_debiteur':autre_debiteur,
        'autre_debiteur_amort': - autre_debiteur_amort,
        'impots_assim':impots_assim if impots_assim > 0 else 0,
        'impots_assim_amort': - impots_assim_amort,
        'autre_creance':autre_creance,
        'autre_creance_amort': - autre_creance_amort,
        'placements_actif':placements_actif,
        'placements_actif_amort': - placements_actif_amort,
        'tresorerie':tresorerie,
        'tresorerie_amort': - tresorerie_amort,
        'capital_emis': - capital_emis,
        'capital_non_app': - capital_non_app,
        'prime': - prime,
        'ecart_reeval': - ecart_reeval,
        'ecart_equi': - ecart_equi,
        'resultat_net': - resultat_net,
        'autre_capitaux': - autre_capitaux,
        'emprunt_dette': - emprunt_dette,
        'impot_diff': - impot_diff,
        'autre_dette': - autre_dette,
        'provision_produit': - provision_produit,
        'fournisseur': - fournisseur,
        'impots_passif': - impots_passif if impots_passif < 0 else 0,
        'autre_dette_passif': - autre_dette_passif,
        'tresorerie_passif': - tresorerie_passif,
        'immo_corp':immo_corp,
        'immo_corp_amort': - immo_corp_amort,
        'immo_finance':immo_finance,
        'immo_finance_amort': - immo_finance_amort,
        'creance_assim': creance_assim,
        'creance_assim_amort': -  creance_assim_amort,
        'dispo_assim': dispo_assim,
        'dispo_assim_amort': -  dispo_assim_amort,
        'actif_courant': actif_courant,
        'actif_courant_amort': -  actif_courant_amort,
        'actif_non_courant': actif_non_courant,
        'actif_non_courant_amort': -  actif_non_courant_amort,
        'total_actif':total_actif,
        'total_actif_amort': - total_actif_amort,
        'capitaux_propres':- capitaux_propres,
        'passif_non_courant':- passif_non_courant,
        'passif_courant': - passif_courant,
        'total_passif': - total_passif,



        }
    def get_compte_res_financier(self, date_from, date_to):
        env = self.env['account.account']
        domains = self.get_compte_res_financier_domains()

        Ventes_marchandises = [self.get_account_balance(env.search(domains['Ventes_marchandises']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Ventes_marchandises']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Ventes_marchandises']),date_from,date_to)]
        Variations_stocks = [self.get_account_balance(env.search(domains['Variations_stocks']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Variations_stocks']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Variations_stocks']),date_from,date_to)]
        Production_immobilise = [self.get_account_balance(env.search(domains['Production_immobilise']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Production_immobilise']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Production_immobilise']),date_from,date_to)]
        Subventions = [self.get_account_balance(env.search(domains['Subventions']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Subventions']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Subventions']),date_from,date_to)]
        somme_1 = Ventes_marchandises[2] + Variations_stocks[2] + Production_immobilise[2] + Subventions[2]
        Production_excercie = [somme_1]

        Achats_de_marchandises = [self.get_account_balance(env.search(domains['Achats_de_marchandises']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Achats_de_marchandises']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Achats_de_marchandises']),date_from,date_to)]
        Services_exterieurs = [self.get_account_balance(env.search(domains['Services_exterieurs']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Services_exterieurs']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Services_exterieurs']),date_from,date_to)]
        somme_2 = Achats_de_marchandises[2] + Services_exterieurs[2]
        consommation_total = [somme_2]
        valeur_ajoute = [somme_1 + somme_2]

        Charges_de_personnel = [self.get_account_balance(env.search(domains['Charges_de_personnel']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Charges_de_personnel']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Charges_de_personnel']),date_from,date_to)]
        Impots_et_taxes = [self.get_account_balance(env.search(domains['Impots_et_taxes']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Impots_et_taxes']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Impots_et_taxes']),date_from,date_to)]
        somme_4 = somme_1 + somme_2 + Charges_de_personnel[2] + Impots_et_taxes[2]
        excedent_brut = [somme_4]

        Autres_produits_operationnels = [self.get_account_balance(env.search(domains['Autres_produits_operationnels']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Autres_produits_operationnels']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Autres_produits_operationnels']),date_from,date_to)]
        Autres_charges_operationnelles = [self.get_account_balance(env.search(domains['Autres_charges_operationnelles']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Autres_charges_operationnelles']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Autres_charges_operationnelles']),date_from,date_to)]
        Dotations_aux_amortissements = [self.get_account_balance(env.search(domains['Dotations_aux_amortissements']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Dotations_aux_amortissements']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Dotations_aux_amortissements']),date_from,date_to)]
        Reprise_sur_pertes = [self.get_account_balance(env.search(domains['Reprise_sur_pertes']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Reprise_sur_pertes']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Reprise_sur_pertes']),date_from,date_to)]
        somme_5 = somme_4 + Autres_produits_operationnels[2] + Autres_charges_operationnelles[2] + Dotations_aux_amortissements[2] + Reprise_sur_pertes[2]
        res_operation = [somme_5]

        Produits_financier = [self.get_account_balance(env.search(domains['Produits_financier']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Produits_financier']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Produits_financier']),date_from,date_to)]
        Charges_financiere = [self.get_account_balance(env.search(domains['Charges_financiere']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Charges_financiere']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Charges_financiere']),date_from,date_to)]
        somme_6 = Produits_financier[2] + Charges_financiere[2]
        res_financier = [somme_6]
        resultat_ordinaire = [somme_5 + somme_6]

        Impots_exigibles_sur = [self.get_account_balance(env.search(domains['Impots_exigibles_sur']), date_from, date_to, 'D'), self.get_account_balance(env.search(domains['Impots_exigibles_sur']), date_from, date_to, 'C'), self.get_account_balance(env.search(domains['Impots_exigibles_sur']), date_from, date_to)]
        Impots_differes_variations = [self.get_account_balance(env.search(domains['Impots_differes_variations']), date_from, date_to, 'D'), self.get_account_balance(env.search(domains['Impots_differes_variations']), date_from, date_to, 'C'), self.get_account_balance(env.search(domains['Impots_differes_variations']), date_from, date_to)]
        resultat_ordinaire_net = [somme_5 + somme_6 + Impots_exigibles_sur[2] + Impots_differes_variations[2]]

        Elements_extraordinaires = [self.get_account_balance(env.search(domains['Elements_extraordinaires']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Elements_extraordinaires']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Elements_extraordinaires']),date_from,date_to)]
        Elements_extraordinaires_2 = [self.get_account_balance(env.search(domains['Elements_extraordinaires_2']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Elements_extraordinaires_2']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Elements_extraordinaires_2']),date_from,date_to)]
        somme_7 = Elements_extraordinaires[2] + Elements_extraordinaires_2[2]
        res_extraordinair = [somme_7]

        somme_8 = somme_5 + somme_6 + somme_7 + Impots_exigibles_sur[2] + Impots_differes_variations[2]
        res_net_exercice = [somme_8]

        return {

        'Ventes_marchandises':Ventes_marchandises,
        'Variations_stocks':Variations_stocks,
        'Production_immobilise':Production_immobilise,
        'Subventions':Subventions,
        'Production_excercie':Production_excercie,
        'Achats_de_marchandises':Achats_de_marchandises,
        'Services_exterieurs':Services_exterieurs,
        'consommation_total':consommation_total,
        'valeur_ajoute':valeur_ajoute,
        'Charges_de_personnel':Charges_de_personnel,
        'Impots_et_taxes':Impots_et_taxes,
        'excedent_brut':excedent_brut,
        'Autres_produits_operationnels':Autres_produits_operationnels,
        'Autres_charges_operationnelles':Autres_charges_operationnelles,
        'Dotations_aux_amortissements':Dotations_aux_amortissements,
        'Reprise_sur_pertes':Reprise_sur_pertes,
        'res_operation':res_operation,
        'Produits_financier':Produits_financier,
        'Charges_financiere':Charges_financiere,
        'res_financier':res_financier,
        'resultat_ordinaire':resultat_ordinaire,
        'Elements_extraordinaires':Elements_extraordinaires,
        'Elements_extraordinaires_2':Elements_extraordinaires_2,
        'res_extraordinair':res_extraordinair,
        'Impots_exigibles_sur':Impots_exigibles_sur,
        'Impots_differes_variations':Impots_differes_variations,
        'resultat_ordinaire_net':resultat_ordinaire_net,
        'res_net_exercice':res_net_exercice,
        }
    def get_compte_res(self, date_from, date_to):
        env = self.env['account.account']
        domains = self.get_compte_res_domains()
        Ventes_marchandises = [self.get_account_balance(env.search(domains['Ventes_marchandises']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Ventes_marchandises']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Ventes_marchandises']),date_from,date_to)]
        Produits_fabrique = [self.get_account_balance(env.search(domains['Produits_fabrique']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Produits_fabrique']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Produits_fabrique']),date_from,date_to)]
        Prestations_de_services = [self.get_account_balance(env.search(domains['Prestations_de_services']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Prestations_de_services']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Prestations_de_services']),date_from,date_to)]
        Vente_de_travaux = [self.get_account_balance(env.search(domains['Vente_de_travaux']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Vente_de_travaux']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Vente_de_travaux']),date_from,date_to)]
        Produits_annexe = [self.get_account_balance(env.search(domains['Produits_annexe']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Produits_annexe']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Produits_annexe']),date_from,date_to)]
        Rabais_remises_1 = [self.get_account_balance(env.search(domains['Rabais_remises_1']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Rabais_remises_1']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Rabais_remises_1']),date_from,date_to)]
        somme = Ventes_marchandises[1] + Produits_fabrique[1] + Prestations_de_services[1] + Vente_de_travaux[1] + Produits_annexe[1] - Rabais_remises_1[0]
        somme = Ventes_marchandises[2] + Produits_fabrique[2] + Prestations_de_services[2] + Vente_de_travaux[2] + Produits_annexe[2] + Rabais_remises_1[2]
        ca_net_rabais = [somme if somme > 0 else 0, abs(somme) if somme <= 0 else 0]

        Production_stocke = [self.get_account_balance(env.search(domains['Production_stocke']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Production_stocke']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Production_stocke']),date_from,date_to)]
        Production_immobilise = [self.get_account_balance(env.search(domains['Production_immobilise']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Production_immobilise']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Production_immobilise']),date_from,date_to)]
        Subventions = [self.get_account_balance(env.search(domains['Subventions']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Subventions']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Subventions']),date_from,date_to)]
        somme_1 = Production_stocke[1] - Production_stocke[0] + Production_immobilise[1] + Subventions[1]
        somme_1 = somme + Production_stocke[2] + Production_immobilise[2] + Subventions[2]
        Production_excercie = [somme_1 if somme_1 > 0 else 0, abs(somme_1) if somme_1 <= 0 else 0]

        Achats_de_marchandises = [self.get_account_balance(env.search(domains['Achats_de_marchandises']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Achats_de_marchandises']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Achats_de_marchandises']),date_from,date_to)]
        Matieres_premiere = [self.get_account_balance(env.search(domains['Matieres_premiere']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Matieres_premiere']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Matieres_premiere']),date_from,date_to)]
        Autres_approvisionnement = [self.get_account_balance(env.search(domains['Autres_approvisionnement']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Autres_approvisionnement']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Autres_approvisionnement']),date_from,date_to)]
        Variations_des_stocks = [self.get_account_balance(env.search(domains['Variations_des_stocks']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Variations_des_stocks']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Variations_des_stocks']),date_from,date_to)]
        Achats_marchandises = [self.get_account_balance(env.search(domains['Achats_marchandises']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Achats_marchandises']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Achats_marchandises']),date_from,date_to)]
        Autres_consommation = [self.get_account_balance(env.search(domains['Autres_consommation']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Autres_consommation']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Autres_consommation']),date_from,date_to)]
        Rabais_remises_2 = [self.get_account_balance(env.search(domains['Rabais_remises_2']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Rabais_remises_2']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Rabais_remises_2']),date_from,date_to)]
        Sous_traitance_generale = [self.get_account_balance(env.search(domains['Sous_traitance_generale']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Sous_traitance_generale']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Sous_traitance_generale']),date_from,date_to)]
        Locations_field = [self.get_account_balance(env.search(domains['Locations_field']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Locations_field']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Locations_field']),date_from,date_to)]
        Entretien_reparations_et = [self.get_account_balance(env.search(domains['Entretien_reparations_et']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Entretien_reparations_et']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Entretien_reparations_et']),date_from,date_to)]
        Primes = [self.get_account_balance(env.search(domains['Primes']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Primes']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Primes']),date_from,date_to)]
        Personnel_exterieur = [self.get_account_balance(env.search(domains['Personnel_exterieur']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Personnel_exterieur']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Personnel_exterieur']),date_from,date_to)]
        Remuneration = [self.get_account_balance(env.search(domains['Remuneration']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Remuneration']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Remuneration']),date_from,date_to)]
        Publicite_field = [self.get_account_balance(env.search(domains['Publicite_field']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Publicite_field']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Publicite_field']),date_from,date_to)]
        Deplacements_missions_et = [self.get_account_balance(env.search(domains['Deplacements_missions_et']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Deplacements_missions_et']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Deplacements_missions_et']),date_from,date_to)]
        Autres_service = [self.get_account_balance(env.search(domains['Autres_service']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Autres_service']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Autres_service']),date_from,date_to)]
        Rabais__remises = [self.get_account_balance(env.search(domains['Rabais__remises']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Rabais__remises']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Rabais__remises']),date_from,date_to)]
        somme_2 = - Variations_des_stocks[1] - Rabais__remises[1] - Rabais_remises_2[1] + Achats_de_marchandises[0] + Matieres_premiere[0] + Autres_approvisionnement[0] + Variations_des_stocks[0] + Achats_marchandises[0] + Autres_consommation[0] + Rabais_remises_2[0] + Sous_traitance_generale[0] + Locations_field[0] + Entretien_reparations_et[0] + Primes[0] + Personnel_exterieur[0] + Remuneration[0] + Publicite_field[0] + Deplacements_missions_et[0] + Autres_service[0] + Rabais__remises[0]
        somme_2 = Achats_de_marchandises[2] + Matieres_premiere[2] + Autres_approvisionnement[2] + Variations_des_stocks[2] + Achats_marchandises[2] + Autres_consommation[2] + Rabais_remises_2[2] + Sous_traitance_generale[2] + Locations_field[2] + Entretien_reparations_et[2] + Primes[2] + Personnel_exterieur[2] + Remuneration[2] + Publicite_field[2] + Deplacements_missions_et[2] + Autres_service[2] + Rabais__remises[2]
        consommation_total = [somme_2 if somme_2 > 0 else 0, abs(somme_2) if somme_2 <= 0 else 0]
        valeur_ajoute = [somme_1 + somme_2 if somme_1 + somme_2 > 0 else 0, abs(somme_1 + somme_2) if somme_1 + somme_2 <= 0 else 0]

        Charges_de_personnel = [self.get_account_balance(env.search(domains['Charges_de_personnel']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Charges_de_personnel']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Charges_de_personnel']),date_from,date_to)]
        Impots_et_taxes = [self.get_account_balance(env.search(domains['Impots_et_taxes']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Impots_et_taxes']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Impots_et_taxes']),date_from,date_to)]
        somme_4 = somme_1 + somme_2 + Charges_de_personnel[2] + Impots_et_taxes[2]
        excedent_brut = [somme_4 if somme_4 > 0 else 0, abs(somme_4) if somme_4 <= 0 else 0]

        Autres_produits_operationnels = [self.get_account_balance(env.search(domains['Autres_produits_operationnels']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Autres_produits_operationnels']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Autres_produits_operationnels']),date_from,date_to)]
        Autres_charges_operationnelles = [self.get_account_balance(env.search(domains['Autres_charges_operationnelles']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Autres_charges_operationnelles']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Autres_charges_operationnelles']),date_from,date_to)]
        Dotations_aux_amortissements = [self.get_account_balance(env.search(domains['Dotations_aux_amortissements']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Dotations_aux_amortissements']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Dotations_aux_amortissements']),date_from,date_to)]
        Provision__field = [self.get_account_balance(env.search(domains['Provision__field']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Provision__field']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Provision__field']),date_from,date_to)]
        Pertes_de_valeur = [self.get_account_balance(env.search(domains['Pertes_de_valeur']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Pertes_de_valeur']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Pertes_de_valeur']),date_from,date_to)]
        Reprise_sur_pertes = [self.get_account_balance(env.search(domains['Reprise_sur_pertes']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Reprise_sur_pertes']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Reprise_sur_pertes']),date_from,date_to)]
        somme_5 = -somme_4 - Autres_produits_operationnels[1] - Reprise_sur_pertes[1] + Autres_produits_operationnels[0] + Autres_charges_operationnelles[0] + Dotations_aux_amortissements[0] + Provision__field[0] + Pertes_de_valeur[0] + Reprise_sur_pertes [0]
        somme_5 = somme_4 + Autres_produits_operationnels[2] + Autres_charges_operationnelles[2] + Dotations_aux_amortissements[2] + Provision__field[2] + Pertes_de_valeur[2] + Reprise_sur_pertes [2]
        res_operation = [somme_5 if somme_5 >= 0 else 0 , abs(somme_5) if somme_5 <= 0 else 0]

        Produits_financier = [self.get_account_balance(env.search(domains['Produits_financier']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Produits_financier']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Produits_financier']),date_from,date_to)]
        Charges_financiere = [self.get_account_balance(env.search(domains['Charges_financiere']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Charges_financiere']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Charges_financiere']),date_from,date_to)]
        somme_6 = Produits_financier[1] - Charges_financiere[0]
        somme_6 = Produits_financier[2] + Charges_financiere[2]
        res_financier = [somme_6 if somme_6 >= 0 else 0 , abs(somme_6) if somme_6 <= 0 else 0]
        resultat_ordinaire = [somme_5 + somme_6 if somme_5 + somme_6 >= 0 else 0 , abs(somme_5 + somme_6) if somme_5 + somme_6 <= 0 else 0]

        Elements_extraordinaires = [self.get_account_balance(env.search(domains['Elements_extraordinaires']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Elements_extraordinaires']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Elements_extraordinaires']),date_from,date_to)]
        Elements_extraordinaires_2 = [self.get_account_balance(env.search(domains['Elements_extraordinaires_2']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Elements_extraordinaires_2']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Elements_extraordinaires_2']),date_from,date_to)]
        somme_7 = Elements_extraordinaires[2] + Elements_extraordinaires_2[2]
        res_extraordinair = [somme_7 if somme_7 >= 0 else 0 , abs(somme_7) if somme_7 <= 0 else 0]

        Impots_exigibles_sur = [self.get_account_balance(env.search(domains['Impots_exigibles_sur']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Impots_exigibles_sur']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Impots_exigibles_sur']),date_from,date_to)]
        Impots_differes_variations = [self.get_account_balance(env.search(domains['Impots_differes_variations']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Impots_differes_variations']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Impots_differes_variations']),date_from,date_to)]
        somme_8 = - somme_5 + somme_6 + somme_7 - Impots_exigibles_sur [0] - Impots_differes_variations[0] + Impots_differes_variations[1]
        somme_8 = somme_5 + somme_6 + somme_7 + Impots_exigibles_sur[2] + Impots_differes_variations[2]
        res_net_exercice = [somme_8 if somme_8 >= 0 else 0, abs(somme_8) if somme_8 <= 0 else 0]

        return {

        'Ventes_marchandises':Ventes_marchandises,
        'Produits_fabrique':Produits_fabrique,
        'Prestations_de_services':Prestations_de_services,
        'Vente_de_travaux':Vente_de_travaux,
        'Produits_annexe':Produits_annexe,
        'Rabais_remises_1':Rabais_remises_1,
        'ca_net_rabais':ca_net_rabais,
        'Production_stocke':Production_stocke,
        'Production_immobilise':Production_immobilise,
        'Subventions':Subventions,
        'Production_excercie':Production_excercie,
        'Achats_de_marchandises':Achats_de_marchandises,
        'Matieres_premiere':Matieres_premiere,
        'Autres_approvisionnement':Autres_approvisionnement,
        'Variations_des_stocks':Variations_des_stocks,
        'Achats_marchandises':Achats_marchandises,
        'Autres_consommation':Autres_consommation,
        'Rabais_remises_2':Rabais_remises_2,
        'Sous_traitance_generale':Sous_traitance_generale,
        'Locations_field':Locations_field,
        'Entretien_reparations_et':Entretien_reparations_et,
        'Primes':Primes,
        'Personnel_exterieur':Personnel_exterieur,
        'Remuneration':Remuneration,
        'Publicite_field':Publicite_field,
        'Deplacements_missions_et':Deplacements_missions_et,
        'Autres_service':Autres_service,
        'Rabais__remises':Rabais__remises,
        'consommation_total':consommation_total,
        'valeur_ajoute':valeur_ajoute,
        'Charges_de_personnel':Charges_de_personnel,
        'Impots_et_taxes':Impots_et_taxes,
        'excedent_brut':excedent_brut,
        'Autres_produits_operationnels':Autres_produits_operationnels,
        'Autres_charges_operationnelles':Autres_charges_operationnelles,
        'Dotations_aux_amortissements':Dotations_aux_amortissements,
        'Provision__field':Provision__field,
        'Pertes_de_valeur':Pertes_de_valeur,
        'Reprise_sur_pertes':Reprise_sur_pertes,
        'res_operation':res_operation,
        'Produits_financier':Produits_financier,
        'Charges_financiere':Charges_financiere,
        'res_financier':res_financier,
        'resultat_ordinaire':resultat_ordinaire,
        'Elements_extraordinaires':Elements_extraordinaires,
        'Elements_extraordinaires_2':Elements_extraordinaires_2,
        'res_extraordinair':res_extraordinair,
        'Impots_exigibles_sur':Impots_exigibles_sur,
        'Impots_differes_variations':Impots_differes_variations,
        'res_net_exercice':res_net_exercice,
        }
    def get_ammo_lines(self, date_from, date_to):
        env = self.env['account.account']
        domain = self.get_ammo_domains()
        goodwill_amort = [
           - self.get_account_balance(env.search(domain['goodwill_amort']),False,date_from),
            self.get_account_balance(env.search(domain['goodwill_amort']),date_from,date_to,'C'),
            self.get_account_balance(env.search(domain['goodwill_amort']),date_from,date_to,'D'),
           - self.get_account_balance(env.search(domain['goodwill_amort']),False,date_to),
        ]

        immo_incorp_amort = [
           - self.get_account_balance(env.search(domain['immo_incorp_amort']),False,date_from),
            self.get_account_balance(env.search(domain['immo_incorp_amort']),date_from, date_to,'C'),
            self.get_account_balance(env.search(domain['immo_incorp_amort']),date_from, date_to,'D'),
           - self.get_account_balance(env.search(domain['immo_incorp_amort']),False, date_to),
        ]

        immo_corp_amort = [
           - self.get_account_balance(env.search(domain['immo_corp_amort']),False,date_from),
            self.get_account_balance(env.search(domain['immo_corp_amort']),date_from, date_to,'C'),
            self.get_account_balance(env.search(domain['immo_corp_amort']),date_from, date_to,'D'),
           - self.get_account_balance(env.search(domain['immo_corp_amort']),False, date_to),
        ]

        participation_amort = [
           - self.get_account_balance(env.search(domain['participation_amort']),False,date_from),
            self.get_account_balance(env.search(domain['participation_amort']),date_from, date_to,'C'),
            self.get_account_balance(env.search(domain['participation_amort']),date_from, date_to,'D'),
           - self.get_account_balance(env.search(domain['participation_amort']),False, date_to),
        ]
        autre_actif_amort = [
           - self.get_account_balance(env.search(domain['autre_actif_amort']),False,date_from),
            self.get_account_balance(env.search(domain['autre_actif_amort']),date_from, date_to,'C'),
            self.get_account_balance(env.search(domain['autre_actif_amort']),date_from, date_to,'D'),
           - self.get_account_balance(env.search(domain['autre_actif_amort']),False, date_to),
        ]

        total = [
            goodwill_amort [0] + immo_incorp_amort [0] + immo_corp_amort [0] + participation_amort [0] + autre_actif_amort [0],
            goodwill_amort [1] + immo_incorp_amort [1] + immo_corp_amort [1] + participation_amort [1] + autre_actif_amort [1],
            goodwill_amort [2] + immo_incorp_amort [2] + immo_corp_amort [2] + participation_amort [2] + autre_actif_amort [2],
            goodwill_amort [3] + immo_incorp_amort [3] + immo_corp_amort [3] + participation_amort [3] + autre_actif_amort [3],
        ]

        return {
            'goodwill_amort':goodwill_amort,
            'immo_incorp_amort':immo_incorp_amort,
            'immo_corp_amort':immo_corp_amort,
            'participation_amort':participation_amort,
            'autre_actif_amort':autre_actif_amort,
            'total':total
        }
    def get_imo_lines(self, date_from, date_to):
        env = self.env['account.account']
        domains = self.get_imo_domains()
        goodwill_amort = [
            self.get_account_balance(env.search(domains['goodwill_amort']),date_from,date_to),
            self.get_imo_tax_sum(env.search(domains['goodwill_amort']),date_from,date_to)
        ]

        immo_incorp_amort = [
            self.get_account_balance(env.search(domains['immo_incorp_amort']),date_from, date_to),
            self.get_imo_tax_sum(env.search(domains['immo_incorp_amort']),date_from, date_to)
        ]

        immo_corp_amort = [
            self.get_account_balance(env.search(domains['immo_corp_amort']),date_from, date_to),
            self.get_imo_tax_sum(env.search(domains['immo_corp_amort']),date_from, date_to)
        ]

        participation_amort = [
            self.get_account_balance(env.search(domains['participation_amort']),date_from, date_to),
            self.get_imo_tax_sum(env.search(domains['participation_amort']),date_from, date_to)
        ]
        autre_actif_amort = [
            self.get_account_balance(env.search(domains['autre_actif_amort']),date_from, date_to),
            self.get_imo_tax_sum(env.search(domains['autre_actif_amort']),date_from, date_to)
        ]

        total = [
            goodwill_amort[0] + immo_incorp_amort[0] + immo_corp_amort[0] + participation_amort[0] + autre_actif_amort[0],
            goodwill_amort[1] + immo_incorp_amort[1] + immo_corp_amort[1] + participation_amort[1] + autre_actif_amort[1]
        ]

        return {
            'goodwill_imo':goodwill_amort,
            'immo_incorp_imo':immo_incorp_amort,
            'immo_corp_imo':immo_corp_amort,
            'participation_imo':participation_amort,
            'autre_actif_imo':autre_actif_amort,
            'total_imo':total
        }
    def get_charge_prod_lines(self, date_from, date_to):
        env = self.env['account.account']
        domains = self.get_charges_prod_domains()
        charges_locatives = self.get_account_balance(env.search(domains['charges_locatives']), date_from, date_to)
        etudes_recherche = self.get_account_balance(env.search(domains['etudes_recherche']), date_from, date_to)
        documentation_diver = self.get_account_balance(env.search(domains['documentation_diver']), date_from, date_to)
        transports_biens = self.get_account_balance(env.search(domains['transports_biens']), date_from, date_to)
        frais_postaux = self.get_account_balance(env.search(domains['frais_postaux']), date_from, date_to)
        services_bancaires = self.get_account_balance(env.search(domains['services_bancaires']), date_from, date_to)
        cotisation_divers = self.get_account_balance(env.search(domains['cotisation_divers']), date_from, date_to)
        total_3 = charges_locatives + etudes_recherche + documentation_diver + transports_biens + frais_postaux + services_bancaires + cotisation_divers

        remunerations_personnel = self.get_account_balance(env.search(domains['remunerations_personnel']), date_from, date_to)
        remunerations_exploitation = self.get_account_balance(env.search(domains['remunerations_exploitation']), date_from, date_to)
        cotisations_organismes = self.get_account_balance(env.search(domains['cotisations_organismes']), date_from, date_to)
        charges_sociales_expl = self.get_account_balance(env.search(domains['charges_sociales_expl']), date_from, date_to)
        autres_charges_sociales = self.get_account_balance(env.search(domains['autres_charges_sociales']), date_from, date_to)
        autres_charges_personnel = self.get_account_balance(env.search(domains['autres_charges_personnel']), date_from, date_to)
        total_1 = remunerations_personnel + remunerations_exploitation + cotisations_organismes + charges_sociales_expl + autres_charges_sociales + autres_charges_personnel

        impot_versements = self.get_account_balance(env.search(domains['impot_versements']), date_from, date_to)
        impot_non_recuperables = self.get_account_balance(env.search(domains['impot_non_recuperables']), date_from, date_to)
        impot_autres_taxes = self.get_account_balance(env.search(domains['impot_autres_taxes']), date_from, date_to)
        total_2 = impot_versements + impot_non_recuperables + impot_autres_taxes


        redevances_pour_concessions = self.get_account_balance(env.search(domains['redevances_pour_concessions']), date_from, date_to)
        moins_values_sur = self.get_account_balance(env.search(domains['moins_values_sur']), date_from, date_to)
        jetons_presence = self.get_account_balance(env.search(domains['jetons_presence']), date_from, date_to)
        perte_creances = self.get_account_balance(env.search(domains['perte_creances']), date_from, date_to)
        quot_part = self.get_account_balance(env.search(domains['quot_part']), date_from, date_to)
        amendes_penalite = self.get_account_balance(env.search(domains['amendes_penalite']), date_from, date_to)
        charges_except = self.get_account_balance(env.search(domains['charges_except']), date_from, date_to)
        autres_charges_gestion = self.get_account_balance(env.search(domains['autres_charges_gestion']), date_from, date_to)
        total_4 = redevances_pour_concessions + moins_values_sur + jetons_presence + perte_creances + quot_part + amendes_penalite + charges_except + autres_charges_gestion

        redevances_concessions = self.get_account_balance(env.search(domains['redevances_concessions']), date_from, date_to)
        plus_values = self.get_account_balance(env.search(domains['plus_values']), date_from, date_to)
        jetons_presence_produit = self.get_account_balance(env.search(domains['jetons_presence_produit']), date_from, date_to)
        quotes_parts_sub = self.get_account_balance(env.search(domains['quotes_parts_sub']), date_from, date_to)
        quote_part_res = self.get_account_balance(env.search(domains['quote_part_res']), date_from, date_to)
        rentre_creances = self.get_account_balance(env.search(domains['rentre_creances']), date_from, date_to)
        produits_except = self.get_account_balance(env.search(domains['produits_except']), date_from, date_to)
        autres_produits = self.get_account_balance(env.search(domains['autres_produits']), date_from, date_to)
        total_5 = redevances_concessions + plus_values + jetons_presence_produit  + quotes_parts_sub  + quote_part_res  + rentre_creances  + produits_except + autres_produits

        charge_interet = self.get_account_balance(env.search([('code', '=like', '661%')]), date_from, date_to)
        perte_change = self.get_account_balance(env.search([('code', '=like', '666%')]), date_from, date_to)

        return {

        'remunerations_personnel':remunerations_personnel,
        'remunerations_exploitation':remunerations_exploitation,
        'cotisations_organismes':cotisations_organismes,
        'charges_sociales_expl':charges_sociales_expl,
        'autres_charges_sociales':autres_charges_sociales,
        'autres_charges_personnel':autres_charges_personnel,
        'total_1':total_1,
        'impot_versements':impot_versements,
        'impot_non_recuperables':impot_non_recuperables,
        'impot_autres_taxes':impot_autres_taxes,
        'total_2':total_2,
        'charges_locatives':charges_locatives,
        'etudes_recherche':etudes_recherche,
        'documentation_diver':documentation_diver,
        'transports_biens':transports_biens,
        'frais_postaux':frais_postaux,
        'services_bancaires':services_bancaires,
        'cotisation_divers':cotisation_divers,
        'total_3':total_3,
        'redevances_pour_concessions':redevances_pour_concessions,
        'moins_values_sur':moins_values_sur,
        'jetons_presence':jetons_presence,
        'perte_creances':perte_creances,
        'quot_part':quot_part,
        'amendes_penalite':amendes_penalite,
        'charges_except':charges_except,
        'autres_charges_gestion':autres_charges_gestion,
        'charge_interet':charge_interet,
        'perte_change':perte_change,
        'total_4':total_4,
        'redevances_concessions':redevances_concessions,
        'plus_values':plus_values,
        'jetons_presence_produit':jetons_presence_produit,
        'quotes_parts_sub':quotes_parts_sub,
        'quote_part_res':quote_part_res,
        'rentre_creances':rentre_creances,
        'produits_except':produits_except,
        'autres_produits':autres_produits,
        'total_5':total_5,

        }
    def get_stock_lines(self, date_from, date_to):
        env = self.env['account.account']
        inventory = True if self.env.ref('dz_accounting.account_report__liasse_85_intermittent').liasse_id.inventory == 'intermittent' else False
        domains = self.get_stock_domains(inventory)
        Stocks_marchandises = [self.get_account_balance(env.search(domains['Stocks_marchandises']),False,date_to),self.get_account_balance(env.search(domains['Stocks_marchandises']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Stocks_marchandises']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Stocks_marchandises']),date_from,date_to)]
        Matieres_fournitures = [self.get_account_balance(env.search(domains['Matieres_fournitures']),False,date_to),self.get_account_balance(env.search(domains['Matieres_fournitures']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Matieres_fournitures']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Matieres_fournitures']),date_from,date_to)]
        Autres_approvisionnements = [self.get_account_balance(env.search(domains['Autres_approvisionnements']),False,date_to),self.get_account_balance(env.search(domains['Autres_approvisionnements']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Autres_approvisionnements']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Autres_approvisionnements']),date_from,date_to)]
        Encours_production_biens = [self.get_account_balance(env.search(domains['Encours_production_biens']),False,date_to),self.get_account_balance(env.search(domains['Encours_production_biens']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Encours_production_biens']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Encours_production_biens']),date_from,date_to)]
        Encours_production_services = [self.get_account_balance(env.search(domains['Encours_production_services']),False,date_to),self.get_account_balance(env.search(domains['Encours_production_services']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Encours_production_services']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Encours_production_services']),date_from,date_to)]
        Stocks_produits = [self.get_account_balance(env.search(domains['Stocks_produits']),False,date_to),self.get_account_balance(env.search(domains['Stocks_produits']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Stocks_produits']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Stocks_produits']),date_from,date_to)]
        Stocks_provenant = [self.get_account_balance(env.search(domains['Stocks_provenant']),False,date_to),self.get_account_balance(env.search(domains['Stocks_provenant']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Stocks_provenant']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Stocks_provenant']),date_from,date_to)]
        Stocks_exterieur = [self.get_account_balance(env.search(domains['Stocks_exterieur']),False,date_to),self.get_account_balance(env.search(domains['Stocks_exterieur']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['Stocks_exterieur']),date_from,date_to,'C'),self.get_account_balance(env.search(domains['Stocks_exterieur']),date_from,date_to)]
        total = [
            Stocks_marchandises[0] + Matieres_fournitures[0] + Autres_approvisionnements[0] + Encours_production_biens[0] + Encours_production_services[0] + Stocks_produits[0] + Stocks_provenant[0] + Stocks_exterieur[0] ,
            Stocks_marchandises[1] + Matieres_fournitures[1] + Autres_approvisionnements[1] + Encours_production_biens[1] + Encours_production_services[1] + Stocks_produits[1] + Stocks_provenant[1] + Stocks_exterieur[1] ,
            Stocks_marchandises[2] + Matieres_fournitures[2] + Autres_approvisionnements[2] + Encours_production_biens[2] + Encours_production_services[2] + Stocks_produits[2] + Stocks_provenant[2] + Stocks_exterieur[2] ,
            Stocks_marchandises[3] + Matieres_fournitures[3] + Autres_approvisionnements[3] + Encours_production_biens[3] + Encours_production_services[3] + Stocks_produits[3] + Stocks_provenant[3] + Stocks_exterieur[3]
        ]
        return {
            'Stocks_marchandises':Stocks_marchandises,
            'Matieres_fournitures':Matieres_fournitures,
            'Autres_approvisionnements':Autres_approvisionnements,
            'Encours_production_biens':Encours_production_biens,
            'Encours_production_services':Encours_production_services,
            'Stocks_produits':Stocks_produits,
            'Stocks_provenant':Stocks_provenant,
            'Stocks_exterieur':Stocks_exterieur,
            'total':total
        }
    def get_fluctuation_lines(self,date_to,date_from):
        env = self.env['account.account']
        domains = self.get_fluctuation_domains()
        sold = self.get_account_balance(env.search(domains['fluctuation']),date_from,date_to)
        fluctuation = [self.get_account_balance(env.search(domains['fluctuation']),date_from,date_to,'D'),self.get_account_balance(env.search(domains['fluctuation']),date_from,date_to,'C'),sold if sold > 0 else 0,sold if sold > 0 else 0]
        return {'fluctuation':fluctuation}
    def get_res_fiscal_lines(self, date_from, date_to):
        fiscal_line = self.env['res.fiscal.line'].search([('date_from', '=', date_from), ('date_to', '=', date_to)])
        r1 = fiscal_line.r1 if fiscal_line else 0
        r2 = fiscal_line.r2 if fiscal_line else 0
        r3 = fiscal_line.r3 if fiscal_line else 0
        r4 = fiscal_line.r4 if fiscal_line else 0
        r5 = fiscal_line.r5 if fiscal_line else 0
        r6 = fiscal_line.r6 if fiscal_line else 0
        r7 = fiscal_line.r7 if fiscal_line else 0
        r8 = fiscal_line.r8 if fiscal_line else 0
        r9 = fiscal_line.r9 if fiscal_line else 0
        r10 = fiscal_line.r10 if fiscal_line else 0
        r11 = fiscal_line.r11 if fiscal_line else 0
        r12 = fiscal_line.r12 if fiscal_line else 0
        r13 = fiscal_line.r13 if fiscal_line else 0
        r14 = fiscal_line.r14 if fiscal_line else 0
        r15 = fiscal_line.r15 if fiscal_line else 0
        r16 = fiscal_line.r16 if fiscal_line else 0
        r17 = fiscal_line.r17 if fiscal_line else 0
        r_total = r1+ r2 +r3 +r4 +r5 +r6 +r7 +r8 +r9 +r10 +r11 +r12 +r13 +r14 +r15 +r16 +r17

        d1 = fiscal_line.d1 if fiscal_line else 0
        d2 = fiscal_line.d2 if fiscal_line else 0
        d3 = fiscal_line.d3 if fiscal_line else 0
        d4 = fiscal_line.d4 if fiscal_line else 0
        d5 = fiscal_line.d5 if fiscal_line else 0
        d6 = fiscal_line.d6 if fiscal_line else 0
        d7 = fiscal_line.d7 if fiscal_line else 0
        d_total = d1 + d2 + d3 + d4 + d5 + d6 + d7

        deficit1 = fiscal_line.deficit1 if fiscal_line else 0
        deficit2 = fiscal_line.deficit2 if fiscal_line else 0
        deficit3 = fiscal_line.deficit3 if fiscal_line else 0
        deficit4 = fiscal_line.deficit4 if fiscal_line else 0
        deficit_total = deficit1 + deficit2 + deficit3 + deficit4
        res_net_exercice = fiscal_line.res_comptable_net if fiscal_line else 0
        res_fiscal = fiscal_line.res_fiscal_net if fiscal_line else 0

        return {
        'r1':r1,
        'r2':r2,
        'r3':r3,
        'r4':r4,
        'r5':r5,
        'r6':r6,
        'r7':r7,
        'r8':r8,
        'r9':r9,
        'r10':r10,
        'r11':r11,
        'r12':r12,
        'r13':r13,
        'r14':r14,
        'r15':r15,
        'r16':r16,
        'r17':r17,
        'r_total':r_total,
        'd1':d1,
        'd2':d2,
        'd3':d3,
        'd4':d4,
        'd5':d5,
        'd6':d6,
        'd7':d7,
        'd_total':d_total,
        'deficit1':deficit1,
        'deficit2':deficit2,
        'deficit3':deficit3,
        'deficit4':deficit4,
        'deficit_total':deficit_total,
        'res_net_exercice':res_net_exercice,
        'res_fiscal':res_fiscal,
        }
    def get_affectation_reserve(self, date_from, date_to):
        affectation = self.env['report.affectation.tab'].search([('liasse_id', '=', self.env.ref('dz_accounting.liasse_fiscal_report_config').id),('date_from', '=', date_from), ('date_to', '=', date_to)])
        report_previous = affectation.report_previous if affectation else 0
        res_previous = affectation.res_previous if affectation else 0
        prelevement_reserve = affectation.prelevement_reserve if affectation else 0
        origin = report_previous + res_previous + prelevement_reserve
        reserve = affectation.reserve if affectation else 0
        capital_augmentation = affectation.capital_augmentation if affectation else 0
        dividendes = affectation.dividendes if affectation else 0
        report_current = affectation.report_current if affectation else 0
        affectation = reserve + capital_augmentation + dividendes + report_current
        return {
            'report_previous': report_previous,
            'res_previous': res_previous,
            'prelevement_reserve': prelevement_reserve,
            'origin': origin,
            'reserve': reserve,
            'capital_augmentation': capital_augmentation,
            'dividendes': dividendes,
            'report_current': report_current,
            'affectation': affectation
        }
    def get_honoraire_et_tap(self, date_from, date_to):
        honoraire_ids = self.env['report.honoraire'].search([('liasse_id', '=', self.env.ref('dz_accounting.liasse_fiscal_report_config').id),('date_from', '=', date_from), ('date_to', '=', date_to)])
        honoraires = []
        for honoraire in honoraire_ids.line_ids:
            honoraires.append({'partner': honoraire.partner_id.name,
                               'nif': honoraire.partner_id.vat,
                               'address': (honoraire.partner_id.street if honoraire.partner_id.street else "") + (honoraire.partner_id.country_id.name if honoraire.partner_id.country_id else "") + (honoraire.partner_id.state_id.name if honoraire.partner_id.country_id else ""),
                               'amount': honoraire.amount})

        tap_ids = self.env['report.tap'].search([('liasse_id', '=', self.env.ref('dz_accounting.liasse_fiscal_report_config').id), ('date_from', '=', date_from), ('date_to', '=', date_to)], limit=1)
        taps = []
        for tap in tap_ids.line_ids:
            taps.append({'partner': tap.partner_id.name,
                         'ca_imposable': tap.ca_imposable,
                         'ca_exo': tap.ca_exo,
                         'tap_amount': tap.tap_amount})

        return {
            'honoraires': honoraires,
            'taps': taps
        }
    def get_provision_immo(self, date_from, date_to):
        provision_ids = self.env['report.provision'].search([('liasse_id', '=', self.env.ref('dz_accounting.liasse_fiscal_report_config').id), ('date_from', '=', date_from), ('date_to', '=', date_to)], limit=1)
        provisions = []
        for provision in provision_ids.line_ids:
            provisions.append({
                                'name': provision.name,
                                'provision_cumul': provision.provision_cumul,
                                'dotation_exercice': provision.dotation_exercice,
                                'reprise_exercice': provision.reprise_exercice
            })
        total = {'name': 'TOTAL',
                 'provision_cumul': sum(provision_ids.line_ids.mapped("provision_cumul")),
                 'dotation_exercice': sum(provision_ids.line_ids.mapped("dotation_exercice")),
                 'reprise_exercice': sum(provision_ids.line_ids.mapped("reprise_exercice"))
        }
        cession_ids = self.env['report.cession'].search([('liasse_id', '=', self.env.ref('dz_accounting.liasse_fiscal_report_config').id), ('date_from', '=', date_from), ('date_to', '=', date_to)], limit=1)
        cessions = []
        for cession in cession_ids.line_ids:
            cessions.append({
                'asset_id': cession.asset_id.name,
                'date': cession.date,
                'net_amount': cession.net_amount,
                'amortissement': cession.amortissement,
                'cesssion_amount': cession.cesssion_amount,
                'account_amount': cession.net_amount - cession.amortissement,
                'plus_value': cession.cesssion_amount - (cession.net_amount - cession.amortissement),
            })
        return {
            'provisions': provisions,
            'cessions': cessions,
            'total': total
        }
    def get_pertes(self, date_from, date_to):
        creance_ids = self.env['perte.creance'].search([('liasse_id', '=', self.env.ref('dz_accounting.liasse_fiscal_report_config').id), ('date_from', '=', date_from), ('date_to', '=', date_to)], limit=1)
        creances = []
        for creance in creance_ids.line_ids:
            creances.append({
                                'debiteur': creance.debiteur,
                                'creance_value': creance.creance_value,
                                'perte_value': creance.perte_value,
            })
        action_ids = self.env['perte.action'].search([('liasse_id', '=', self.env.ref('dz_accounting.liasse_fiscal_report_config').id), ('date_from', '=', date_from), ('date_to', '=', date_to)], limit=1)
        actions = []
        for action in action_ids.line_ids:
            actions.append({
                'filaile': action.filaile,
                'nominal_value': action.nominal_value,
                'perte_value': action.perte_value,
                'account_value': action.nominal_value - action.perte_value,
            })
        return {
            'creances': creances,
            'actions': actions,
        }
    def get_participation(self, date_from, date_to):
        participation_ids = self.env['participation.tap'].search([('liasse_id', '=', self.env.ref('dz_accounting.liasse_fiscal_report_config').id), ('date_from', '=', date_from), ('date_to', '=', date_to)], limit=1)
        filiales = []
        for filiale in participation_ids.filiale_ids:
            filiales.append({
                                'filaile': filiale.filaile,
                                'capitaux': filiale.capitaux,
                                'dont_capital': filiale.dont_capital,
                                'pourcentage': filiale.dont_capital * 100 / filiale.capitaux if filiale.capitaux != 0 else 0,
                                'res': filiale.res,
                                'avances': filiale.avances,
                                'dividende': filiale.dividende,
                                'account_value': filiale.account_value,

            })
        entites = []
        for entite in participation_ids.entite_ids:
            entites.append({
                'filaile': entite.filaile,
                'capitaux': entite.capitaux,
                'dont_capital': entite.dont_capital,
                'res': entite.res,
                'avances': entite.avances,
                'dividende': entite.dividende,
                'account_value': entite.account_value,
                'pourcentage': entite.dont_capital * 100 / entite.capitaux if entite.capitaux != 0 else 0,
            })
        return {
            'filiales': filiales,
            'entites': entites,
        }
    def check_report(self, destiner=" AU CONTRIBUABLE"):
        self.ensure_one()
        data = {
                'current': self.get_bilan_lines(self.date_from, self.date_to),
                'previous': self.get_bilan_lines(self.date_from.replace(year=self.date_from.year - 1), self.date_to.replace(year=self.date_to.year - 1)),
                'currency_id': self.company_id.currency_id,
                'nif': list(self.company_id.vat) if self.company_id.vat else [],
                'company': self.company_id.name,
                'address': self.company_id.street,
                'activity': self.company_id.activite,
                'current_year': self.date_from.year,
                'previous_year': self.date_from.year - 1,
                'date_from': self.date_from,
                'date_to': self.date_to,
                'consolidate': True,
                'destiner': destiner
                }
        data.update({'amortissement': self.get_ammo_lines(self.date_from, self.date_to)})
        data.update({'stock': self.get_stock_lines(self.date_from, self.date_to)})
        data.update({'fluctuation': self.get_fluctuation_lines(self.date_from, self.date_to)})
        data.update({'immobilisation': self.get_imo_lines(self.date_from, self.date_to)})
        data.update(self.get_charge_prod_lines(self.date_from, self.date_to))
        compte_res = {'compte_res': self.get_compte_res(self.date_from, self.date_to)}
        compte_res_prev = {'compte_res_previous': self.get_compte_res(self.date_from.replace(year=self.date_from.year - 1), self.date_to.replace(year=self.date_to.year - 1))}
        res_fiscal = {'res_fiscal': self.get_res_fiscal_lines(self.date_from, self.date_to)}
        affectation = {'affectation': self.get_affectation_reserve(self.date_from, self.date_to)}
        honoraire = {'honoraire': self.get_honoraire_et_tap(self.date_from, self.date_to)}
        provision = {'provision': self.get_provision_immo(self.date_from, self.date_to)}
        perte = {'perte': self.get_pertes(self.date_from, self.date_to)}
        participation = {'participation': self.get_participation(self.date_from, self.date_to)}
        data.update(honoraire)
        data.update(participation)
        data.update(perte)
        data.update(provision)
        data.update(res_fiscal)
        data.update(compte_res)
        data.update(compte_res_prev)
        data.update(affectation)
        data.update({
            'ids': self.env.context.get('active_ids', []),
            'model': self.env.context.get('active_model', 'ir.ui.menu')})
        return self.env.ref('dz_accounting.liasse_config_report_action').report_action(self, data=data)
    def liasse_administration(self):
        return self.check_report(destiner=" A L’ADMINISTRATION")
