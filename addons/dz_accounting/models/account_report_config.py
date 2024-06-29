#-*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)

class AccountCode(models.Model):
    _name = 'account.code'

    name = fields.Char("Name")
    display_name = fields.Char('Display Name', compute="_compute_display_name")

    def _compute_display_name(self):
        for record in self:
            record.display_name = record.name

class AccountLine(models.Model):
    _name = 'account.line'

    account = fields.Many2many('account.code','account_line_code' , string="Code")
    sauf = fields.Many2many('account.code','account_line_except', string='Sauf')
    sold_actif_id = fields.Many2one('report.bilan.actif', string='sold_actif_id',ondelete='cascade')
    credit_actif_id = fields.Many2one('report.bilan.actif', string='credit_actif_id',ondelete='cascade')
    debit_actif_id = fields.Many2one('report.bilan.actif', string='debit_id_id',ondelete='cascade')
    amortissement_actif_id = fields.Many2one('report.bilan.actif', string='amortissement_actif_id',ondelete='cascade')

    sold_passif_id = fields.Many2one('report.bilan.passif', string='sold_passif_id', ondelete='cascade')
    credit_passif_id = fields.Many2one('report.bilan.passif', string='credit_passif_id', ondelete='cascade')
    debit_passif_id = fields.Many2one('report.bilan.passif', string='debit_passfi_id', ondelete='cascade')

    sold_compte_res_id = fields.Many2one('report.compte.res', string='sold_passif_id', ondelete='cascade')
    sold_second_compte_res_id = fields.Many2one('report.compte.res_two', string='sold_passif_id', ondelete='cascade')

    sold_charges_id = fields.Many2one('report.charges', string='sold_passif_id', ondelete='cascade')
    sold_other_charges_id = fields.Many2one('report.charges.others', string='sold_passif_id', ondelete='cascade')

    sold_amortissement_id = fields.Many2one('report.amortissement', string='sold_amo_id', ondelete='cascade')
    sold_immobilisation_id = fields.Many2one('report.immobilisation', string='sold_immo_id', ondelete='cascade')

    sold_stock_id = fields.Many2one('report.stock.move', string='sold_stock_id', ondelete='cascade')
    sold_intermittent_id = fields.Many2one('report.stock.intermittent', string='sold_intermittent_id', ondelete='cascade')
    sold_fluctuation_id = fields.Many2one('report.fluctuation', string='sold_intermittent_id', ondelete='cascade')

    display_name = fields.Char('Display Name', compute="_compute_display_name")
    name = fields.Char('Name', compute="_compute_display_name")

    def _compute_display_name(self):
        for record in self:
            name = ""
            for account in record.account:
                name = (name + " ," + account.name) if len(name) else account.name
            for account in record.sauf:
                name = (name + " , -" + account.name) if len(name) else ("-" + account.name)
            record.display_name = name
            record.name = name

class ConfigMask(models.AbstractModel):
    _name = 'report.config.mask'

    name = fields.Char("Name")
    domain = fields.Char("Domain")
    domain_credit = fields.Char("Domain credit")
    domain_debit = fields.Char("Domain debit")
    code_credit = fields.Char("Code credit")
    code_debit = fields.Char("Code debit")
    code = fields.Char("Code")
    sequence = fields.Integer('Display order')



    @api.model
    def get_sold(self,year):
        return self.get_bilan_lines(year)

    @api.model
    def get_credit(self, year):
        return self.get_bilan_lines(year,'C')

    @api.model
    def get_debit(self, year):
        return self.get_bilan_lines(year,'D')

    def string_domain_to_list(self,domain):
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
        return domain

    def domain_to_records(self,domain):
        domain = self.string_domain_to_list(domain)
        result = []
        i = 0
        _logger.info("################ " + str(domain))
        while i < len(domain):
            domain[i] = domain[i].strip()
            if domain[i] in ['|', '!']:
                result.append(domain[i])
                i = i+1
            else:
                result.append((domain[i], domain[i + 1], domain[i + 2]))
                i = i + 3
        return result

    def domain_to_list(self, domain):
        reslut = {'code': [], 'except': []}
        array = []
        domain = self.domain_to_records(domain)
        _logger.info("============" + str(domain))
        for element in reversed(domain):
            _logger.info(str(element) + " !!!! " + str(len(element)) )
            if element == '|':
                reslut['code'] += array
                array = []
            elif element == '!':
                reslut['except'] += array
                array = []
            elif len(element) == 3:
                code = self.env['account.code'].create({'name':element[2].replace('%', '').strip()})
                array.append(code.id)
        if len(array):
            reslut['code'] += array
        return reslut

    def records_to_strdomain(self, records):
        domain = []
        account = []
        sauf = []
        for record in records:
            for code in record.account:
                account.append(('code', '=like', code.name + '%'))
                if len(account) > 1:
                    account.append('|')
            for code in record.sauf:
                sauf.append('!')
                sauf.append(('code', '=like', code.name+'%'))
        account.reverse()
        domain = account + sauf
        return domain

    def write(self, vals):
        result = super(ConfigMask, self).write(vals)
        if 'code' in vals:
            for res in self:
                if len(res.code):
                    res.domain = self.records_to_strdomain(res.code)
        if 'code_debit' in vals:
            for res in self:
                if len(res.code_debit):
                    res.domain_debit = self.records_to_strdomain(res.code_debit)
        if 'code_credit' in vals:
            for res in self:
                if len(res.code_credit):
                    res.domain_credit = self.records_to_strdomain(res.code_credit)
        return result
    @api.model
    def create(self, vals):
        res = super(ConfigMask, self).create(vals)
        ################### DOMAIN TO RECORDS
        if isinstance(res.domain, str) and len(res.domain) and res.domain and not len(res.code):
            code = self.domain_to_list(res.domain)
            code_ids = self.env['account.line'].create({'account': [(6, 0, code['code'])],'sauf': [(6, 0, code['except'])],})
            res.code = [(6,0,[code_ids.id])]
        if isinstance(res.domain_credit, str) and len(res.domain_credit) and res.domain_credit and not len(res.code_credit):
            code = self.domain_to_list(res.domain_credit)
            code_ids = self.env['account.line'].create({'account': [(6, 0, code['code'])],'sauf': [(6, 0, code['except'])],})
            res.code_credit = [(6,0,[code_ids.id])]
        if isinstance(res.domain_debit, str) and len(res.domain_debit) and res.domain_debit and not len(res.code_debit):
            code = self.domain_to_list(res.domain_debit)
            code_ids = self.env['account.line'].create({'account': [(6, 0, code['code'])],'sauf': [(6, 0, code['except'])],})
            res.code_debit = [(6,0,[code_ids.id])]
        ################### RECORDS TO DOMAIN
        if not isinstance(res.domain, str) and not isinstance(res.code, bool) and len(res.code):
            res.domain = self.records_to_strdomain(res.code)
        if not isinstance(res.domain_credit, str) and not isinstance(res.code_credit, bool) and len(res.code_credit):
            res.domain_credit = self.records_to_strdomain(res.code_credit)
        if not isinstance(res.domain_debit, str) and not isinstance(res.code_debit, bool) and len(res.code_debit):
            res.domain_debit = self.records_to_strdomain(res.code_debit)

        return res

class AccountBilanActif(models.Model):
    _name = 'report.bilan.actif'
    _inherit = ['report.config.mask']

    liasse_id = fields.Many2one('account.liasse.report_config', string="Liasse", default=lambda self: self.env.ref('dz_accounting.liasse_fiscal_report_config'),ondelete='cascade')
    amortissement = fields.Char(string="Amortissement Domain")
    amortissement_code = fields.One2many('account.line','amortissement_actif_id', string="Amortissement Code")
    code = fields.One2many('account.line', 'sold_actif_id', string="Compte solde")
    code_credit = fields.One2many('account.line', 'credit_actif_id', string="Compte credit")
    code_debit = fields.One2many('account.line', 'debit_actif_id', string="Compte debit")

    @api.model
    def create(self, vals):
        res = super(AccountBilanActif, self).create(vals)

        if isinstance(res.amortissement, str) and len(res.amortissement) and res.amortissement and not len(res.amortissement_code):
            code = self.domain_to_list(res.amortissement)
            code_ids = self.env['account.line'].create({
                'account': [(6, 0, code['code'])],
                'sauf': [(6, 0, code['except'])],
            })
            res.amortissement_code = [(6, 0, [code_ids.id])]

        if not isinstance(res.amortissement, str) and len(res.amortissement_code):
            res.amortissement = self.records_to_strdomain(res.amortissement_code)
        return res

    def write(self, vals):
        result = super(AccountBilanActif, self).write(vals)
        if 'amortissement_code' in vals:
            for res in self:
                if len(res.amortissement_code):
                    res.amortissement = self.records_to_strdomain(res.amortissement_code)

        return result

class AccountBllanPassif(models.Model):
    _name = 'report.bilan.passif'
    _inherit = ['report.config.mask']
    liasse_id = fields.Many2one('account.liasse.report_config', string="Liasse", default=lambda self: self.env.ref('dz_accounting.liasse_fiscal_report_config'),ondelete='cascade')
    code = fields.One2many('account.line', 'sold_passif_id', string="Compte solde")
    code_credit = fields.One2many('account.line', 'credit_passif_id', string="Compte credit")
    code_debit = fields.One2many('account.line', 'debit_passif_id', string="Compte debit")

class Report(models.Model):
    _name = 'account.liasse.report_config'

    name = fields.Char("Name")
    type = fields.Selection([
        ('liasse', 'Liasse'),
        ('bilan', 'BILAN'),
        ('tcr', 'TCR'),
        ('tft', 'TFT'),
        ('era', 'ERA'),
        ('tvcp', 'TVCP'),
    ], string="type", default='liasse')
    inventory = fields.Selection([('permanent', 'Permanent'),('intermittent', 'Intermittent')],string="Méthode d'inenvtaire",default='permanent')
    bilan_passif_ids = fields.One2many('report.bilan.passif', 'liasse_id', string='Bilan Passif')
    bilan_actif_ids = fields.One2many('report.bilan.actif', 'liasse_id', string='Bilan Actif')

    compte_res_ids = fields.One2many('report.compte.res', 'liasse_id', string='Compte de résultat')
    compte_res_second_ids = fields.One2many('report.compte.res_two', 'liasse_id', string='Compte de résultat 2')

    charges_ids = fields.One2many('report.charges', 'liasse_id', string='3/ Charges de personnel, impôts, taxes et versements assimilés, autres services')
    other_charge_ids = fields.One2many('report.charges.others', 'liasse_id', string='4/ Autres charges et produits opérationnels')

    amo_ids = fields.One2many('report.amortissement', 'liasse_id', string='5/ amortissements')
    immo_ids = fields.One2many('report.immobilisation', 'liasse_id', string='6/ immobilisations')

    stock_ids = fields.One2many('report.stock.move', 'liasse_id', string='1/ Stock')
    intermittent_ids = fields.One2many('report.stock.intermittent', 'liasse_id', string='1/ Stock')
    fluctuation_ids = fields.One2many('report.fluctuation', 'liasse_id', string='2/ Fluctuation')

    cession_ids = fields.One2many('report.cession', 'liasse_id', string="7/Cessions")
    provision_ids = fields.One2many('report.provision', 'liasse_id', string="8/Provisions")

    perte_creance_ids = fields.One2many('perte.creance', 'liasse_id', string="8.1/Pertes creance")
    perte_action_ids = fields.One2many('perte.action', 'liasse_id', string="8.2/Pertes ations")

    fiscal_ids = fields.One2many('res.fiscal.line', 'liasse_id', string="9/Résultat fiscal")

    affectation_ids = fields.One2many('report.affectation.tab', 'liasse_id', string="10/Affectations")
    participation_ids = fields.One2many('participation.tap', 'liasse_id', string="10/Participations")

    honoraire_ids = fields.One2many('report.honoraire', 'liasse_id', string="12/Honoraires")
    tap_ids = fields.One2many('report.tap', 'liasse_id', string="13/TAP")

    tvcp_ids = fields.One2many('report.tvcp', 'liasse_id', string="TVCP")

class ReportComptRes(models.Model):
    _name = 'report.compte.res'
    _inherit = ['report.config.mask']

    liasse_id = fields.Many2one('account.liasse.report_config', string="Liasse", default=lambda self: self.env.ref('dz_accounting.liasse_fiscal_report_config'), ondelete='cascade')
    code = fields.One2many('account.line', 'sold_compte_res_id', string="Compte solde")

class ReportResTwo(models.Model):
    _name = 'report.compte.res_two'
    _inherit = ['report.config.mask']

    liasse_id = fields.Many2one('account.liasse.report_config', string="Liasse", default=lambda self: self.env.ref('dz_accounting.liasse_fiscal_report_config'), ondelete='cascade')
    code = fields.One2many('account.line', 'sold_second_compte_res_id', string="Compte solde")

class ReportCharges(models.Model):
    _name = 'report.charges'
    _inherit = ['report.config.mask']
    liasse_id = fields.Many2one('account.liasse.report_config', string="Liasse", default=lambda self: self.env.ref('dz_accounting.liasse_fiscal_report_config'), ondelete='cascade')
    code = fields.One2many('account.line', 'sold_charges_id', string="Compte solde")

class ReportChargesOther(models.Model):
    _name = 'report.charges.others'
    _inherit = ['report.config.mask']
    liasse_id = fields.Many2one('account.liasse.report_config', string="Liasse", default=lambda self: self.env.ref('dz_accounting.liasse_fiscal_report_config'), ondelete='cascade')
    code = fields.One2many('account.line', 'sold_other_charges_id', string="Compte solde")

class ReportAmmo(models.Model):
    _name = 'report.amortissement'
    _inherit = ['report.config.mask']
    liasse_id = fields.Many2one('account.liasse.report_config', string="Liasse", default=lambda self: self.env.ref('dz_accounting.liasse_fiscal_report_config'), ondelete='cascade')
    code = fields.One2many('account.line', 'sold_amortissement_id', string="Compte solde")

class ReportImmo(models.Model):
    _name = 'report.immobilisation'
    _inherit = ['report.config.mask']
    liasse_id = fields.Many2one('account.liasse.report_config', string="Liasse", default=lambda self: self.env.ref('dz_accounting.liasse_fiscal_report_config'), ondelete='cascade')
    code = fields.One2many('account.line', 'sold_immobilisation_id', string="Compte solde")

class ReportStockMove(models.Model):
    _name = 'report.stock.move'
    _inherit = ['report.config.mask']

    liasse_id = fields.Many2one('account.liasse.report_config', string="Liasse", default=lambda self: self.env.ref('dz_accounting.liasse_fiscal_report_config'), ondelete='cascade')
    code = fields.One2many('account.line', 'sold_stock_id', string="Compte solde")

class ReportStockIntermittent(models.Model):
    _name = 'report.stock.intermittent'
    _inherit = ['report.config.mask']

    liasse_id = fields.Many2one('account.liasse.report_config', string="Liasse", default=lambda self: self.env.ref('dz_accounting.liasse_fiscal_report_config'), ondelete='cascade')
    code = fields.One2many('account.line', 'sold_intermittent_id', string="Compte solde")

class ReportFluctuation(models.Model):
    _name = 'report.fluctuation'
    _inherit = ['report.config.mask']

    liasse_id = fields.Many2one('account.liasse.report_config', string="Liasse", default=lambda self: self.env.ref('dz_accounting.liasse_fiscal_report_config'), ondelete='cascade')
    code = fields.One2many('account.line', 'sold_fluctuation_id', string="Compte solde")

class ReportProvision(models.Model):
    _name = 'report.provision'

    liasse_id = fields.Many2one('account.liasse.report_config', string="Liasse", ondelete='cascade')
    date_from = fields.Date(string='Start Date', default=date.today().replace(day=1, month=1), requred=True)
    date_to = fields.Date(string='End Date', default=date.today().replace(day=31, month=12), requred=True)
    year = fields.Char("Exercice", compute="compute_fiscal_year")
    name = fields.Char("Name")
    domain = fields.Char("Domain")
    def _default_line_ids(self):
        return [
            (0, 0, {'name': line.name})
            for line in [self.env.ref("dz_accounting.account_report__liasse_134")
                        , self.env.ref("dz_accounting.account_report__liasse_135")
                        , self.env.ref("dz_accounting.account_report__liasse_136")
                        , self.env.ref("dz_accounting.account_report__liasse_137")
                        , self.env.ref("dz_accounting.account_report__liasse_138")
                        , self.env.ref("dz_accounting.account_report__liasse_139")
                        , self.env.ref("dz_accounting.account_report__liasse_140")
                        , self.env.ref("dz_accounting.account_report__liasse_141")
                         ]
        ]
    line_ids = fields.One2many('report.provision.line', 'provision_id', string="lines",default=_default_line_ids)

    def compute_fiscal_year(self):
        for record in self:
            record.year = record.date_to.strftime("%Y")

class ReportProvisionLine(models.Model):
    _name = 'report.provision.line'

    provision_id = fields.Many2one('report.provision', string="Provision")
    name = fields.Char("Rubrique")
    provision_cumul = fields.Float('Provisions cumulées')
    dotation_exercice = fields.Float("Dotations de l’exercice")
    reprise_exercice = fields.Float('Reprises sur l’exercice')

class ReportCessionAmo(models.Model):
    _name = 'report.cession'

    liasse_id = fields.Many2one('account.liasse.report_config', string="Liasse", default=lambda self: self.env.ref('dz_accounting.liasse_fiscal_report_config'), ondelete='cascade')
    line_ids = fields.One2many('report.cession.line', 'cession_id', string="lines")
    date_from = fields.Date(string='Start Date', default=date.today().replace(day=1, month=1), requred=True)
    date_to = fields.Date(string='End Date', default=date.today().replace(day=31, month=12), requred=True)
    year = fields.Char("Exercice", compute="compute_fiscal_year")
    def compute_fiscal_year(self):
        for record in self:
            record.year = record.date_to.strftime("%Y")

class ReportCessionAmoLine(models.Model):
    _name = 'report.cession.line'

    cession_id = fields.Many2one('report.cession', string="Cessions")
    asset_id = fields.Many2one('account.asset.asset', string='Asset',required=True, ondelete='cascade')
    date = fields.Date("Date acquisition")
    net_amount = fields.Float('Montant net figurant à l’actif')
    amortissement = fields.Float('Amortissements pratiqués')
    cesssion_amount = fields.Float("Prix de cession")

    @api.onchange('asset_id')
    def onchange_asset(self):
        if self.asset_id:
            self.date = self.asset_id.date
            self.net_amount = self.asset_id.value
            amo = sum(self.asset_id.depreciation_line_ids.filtered(lambda x: self.cession_id.date_from <= x.depreciation_date <= self.cession_id.date_to ).mapped('amount'))
            self.amortissement = self.asset_id.value - amo

class PertesCreance(models.Model):
    _name = 'perte.creance'

    liasse_id = fields.Many2one('account.liasse.report_config', string="Liasse", ondelete='cascade')
    date_from = fields.Date(string='Start Date', default=date.today().replace(day=1, month=1), requred=True)
    date_to = fields.Date(string='End Date', default=date.today().replace(day=31, month=12), requred=True)
    year = fields.Char("Exercice", compute="compute_fiscal_year")
    name = fields.Char("Name")
    domain = fields.Char("Domain")
    line_ids = fields.One2many('perte.creance.line', 'perte_creance_id', string="lines")

    def compute_fiscal_year(self):
        for record in self:
            record.year = record.date_to.strftime("%Y")

class PertesCreanceLine(models.Model):
    _name = 'perte.creance.line'

    perte_creance_id = fields.Many2one('perte.creance', string="Perte creance")
    debiteur = fields.Char('Désignation des débiteurs')
    creance_value = fields.Float("Valeur de la créance")
    perte_value = fields.Float('Perte de valeur constituée')

class PertesAction(models.Model):
    _name = 'perte.action'

    liasse_id = fields.Many2one('account.liasse.report_config', string="Liasse", ondelete='cascade')
    date_from = fields.Date(string='Start Date', default=date.today().replace(day=1, month=1), requred=True)
    date_to = fields.Date(string='End Date', default=date.today().replace(day=31, month=12), requred=True)
    year = fields.Char("Exercice", compute="compute_fiscal_year")
    name = fields.Char("Name")
    domain = fields.Char("Domain")
    line_ids = fields.One2many('perte.action.line', 'perte_action_id', string="lines")

    def compute_fiscal_year(self):
        for record in self:
            record.year = record.date_to.strftime("%Y")

class PertesActionLine(models.Model):
    _name = 'perte.action.line'

    perte_action_id = fields.Many2one('perte.action', string="Perte action")
    filaile = fields.Char('Filiale')
    nominal_value = fields.Float("Valeur nominale au début de l’exercice")
    perte_value = fields.Float('Perte de valeur constituée')

class ReportResFiscalLine(models.Model):
    _name = 'res.fiscal.line'

    liasse_id = fields.Many2one('account.liasse.report_config', string="Liasse")
    exercice_id = fields.Many2one('account.exercice', 'Exercice comptable', required=True)
    date_from = fields.Date(string='Start Date', related="exercice_id.date_from")
    date_to = fields.Date(string='End Date', related="exercice_id.date_to")
    year = fields.Char("Exercice", compute="compute_fiscal_year")
    r1 = fields.Float("Charges des immeubles non affectés directement à l'exploitation")
    r2 = fields.Float("Quote–part des cadeaux publicitaires non déductibles")
    r3 = fields.Float("Quote–part du sponsoring et parrainage non déductibles")
    r4 = fields.Float("Frais de réception non déductibles")
    r5 = fields.Float("Cotisations et dons non déductibles")
    r6 = fields.Float("Impôts et taxes non déductibles")
    r7 = fields.Float("Provisions non déductibles")
    r8 = fields.Float("Amortissements non déductibles")
    r9 = fields.Float("Quote-part des frais de recherche développement non déductibles")
    r10 = fields.Float("Amortissements non déductibles liés aux opérations de crédit bail (Preneur) (cf.art 27 de LFC 2010)")
    r11 = fields.Float("Loyers hors produits financiers (bailleur) (cf.art 27 de LFC 2010)")
    r12 = fields.Float("Impôts sur les bénéfices des sociétés")
    r13 = fields.Float("Impôt exigible sur le résultat", compute="compute_fiscal_amount")
    r14 = fields.Float("Impôt différé (variation)",  compute="compute_fiscal_amount")
    r15 = fields.Float("Pertes de valeurs non déductibles")
    r16 = fields.Float("Amendes et pénalités")
    r17 = fields.Float("Autres réintégrations (*)")

    d1 = fields.Float("Plus values sur cession d'éléments d'actif immobilisés (cf.art 173 du CIDTA)")
    d2 = fields.Float("Les produits et les plus values de cession des actions et titre assimilés ainsi que ceux des actions ou part d'OPCVM cotées en bourse.")
    d3 = fields.Float("impôt sur les bénéfices des sociétés ou expressément exonérés (cf.art 147 bis du CIDTA)")
    d4 = fields.Float("Amortissements liés aux opérations de crédit bail (Bailleur) (cf.art 27 de LFC 2010)")
    d5 = fields.Float("Loyers hors charges financières (Preneur) (cf.art 27 de LFC 2010)")
    d6 = fields.Float("Complément d'amortissements")
    d7 = fields.Float("Autres déductions (*)")

    deficit1 = fields.Float("Déficit de l’année 1")
    deficit2 = fields.Float("Déficit de l’année 2")
    deficit3 = fields.Float("Déficit de l’année 3")
    deficit4 = fields.Float("Déficit de l’année 4")

    res_comptable_net = fields.Float("Résultat comptable de l'exercice", compute="compute_fiscal_amount")
    res_fiscal_net = fields.Float("Résultat fiscal de l'exercice", compute="compute_fiscal_amount")

    def compute_fiscal_year(self):
        for record in self:
            record.year = record.date_to.strftime("%Y")

    def compute_fiscal_amount(self):
        for record in self:
            env = self.env['account.account']
            charge = self.env['account.liasse.config'].get_account_balance(env.search([('code', '=like', '6%')]),record.date_from,record.date_to)
            produit = self.env['account.liasse.config'].get_account_balance(env.search([('code', '=like', '7%')]),record.date_from,record.date_to)
            ibs_domain = self.env['account.liasse.config'].string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_76').domain)
            variation_domain = self.env['account.liasse.config'].string_domain_to_list(self.env.ref('dz_accounting.account_report__liasse_77').domain)
            ibs = self.env['account.liasse.config'].get_account_balance(env.search(ibs_domain),record.date_from,record.date_to)
            variation = self.env['account.liasse.config'].get_account_balance(env.search(variation_domain),record.date_from,record.date_to)
            res_comptable_net = - charge - produit
            record.r13 = ibs
            record.r14 = variation
            r_total = record.r1 + record.r2 + record.r3 + record.r4 + record.r5 + record.r6 + record.r7 + record.r8 + record.r9 + record.r10 + record.r11 + record.r12 + record.r13 + record.r14 + record.r15 + record.r16 + record.r17
            d_total = record.d1 + record.d2 + record.d3 + record.d4 + record.d5 + record.d6 + record.d7
            deficit_total = record.deficit1 + record.deficit2 + record.deficit3 + record.deficit4
            res_fiscal_net = res_comptable_net + r_total - d_total - deficit_total
            record.res_comptable_net = res_comptable_net
            record.res_fiscal_net = res_fiscal_net

class ReportResFiscal(models.Model):
    _name = 'report.res.fiscal'
    _inherit = ['report.config.mask']

    liasse_id = fields.Many2one('account.liasse.report_config', string="Liasse", default=lambda self: self.env.ref('dz_accounting.liasse_fiscal_report_config'), ondelete='cascade')

class ReportAffectation(models.Model):
    _name = 'report.affectation.tab'

    liasse_id = fields.Many2one('account.liasse.report_config', string="Liasse")
    date_from = fields.Date(string='Start Date', default=date.today().replace(day=1, month=1), requred=True)
    date_to = fields.Date(string='End Date', default=date.today().replace(day=31, month=12), requred=True)
    year = fields.Char("Exercice", compute="compute_fiscal_year")
    report_previous = fields.Float("Report à nouveau de l’exercice N-1")
    res_previous = fields.Float("Résultat de l’exercice N-1")
    prelevement_reserve = fields.Float("Prélèvements sur réserves (à détailler)")
    reserve = fields.Float("Réserves (à détailler)")
    capital_augmentation = fields.Float("Augmentation du capital")
    dividendes = fields.Float("Dividendes")
    report_current = fields.Float("Report à nouveau (à détailler)")

    def compute_fiscal_year(self):
        for record in self:
            record.year = record.date_to.strftime("%Y")

    def calculate_origine(self):
        res = self.env['account.liasse.config'].get_compte_res(self.date_from.replace(year=self.date_from.year - 1),self.date_to.replace(year=self.date_from.year - 1))
        self.report_previous = res['res_net_exercice'][0] or res['res_net_exercice'][1]

class ReportParticipationTab(models.Model):
    _name = 'participation.tap'

    liasse_id = fields.Many2one('account.liasse.report_config', string="Liasse", ondelete='cascade')
    date_from = fields.Date(string='Start Date', default=date.today().replace(day=1, month=1), requred=True)
    date_to = fields.Date(string='End Date', default=date.today().replace(day=31, month=12), requred=True)
    year = fields.Char("Exercice", compute="compute_fiscal_year")
    filiale_ids = fields.One2many('participation.tap.filiale', 'participation_id', string="Filiales")
    entite_ids = fields.One2many('participation.tap.entite', 'participation_id', string="Entité")

    def compute_fiscal_year(self):
        for record in self:
            record.year = record.date_to.strftime("%Y")

class ReportParticipationTabFiliale(models.Model):
    _name = 'participation.tap.filiale'

    participation_id = fields.Many2one('participation.tap', string="Participation")
    filaile = fields.Char('Filiale')
    capitaux = fields.Float("Capitaux propres")
    dont_capital = fields.Float("Dont capital")
    res = fields.Float("Résultat Dernier exercice")
    avances = fields.Float("Prêts et avances accordées")
    dividende = fields.Float("Dividendes encaissés")
    account_value = fields.Float("Valeur comptable des titres détenus")


class ReportParticipationTabEntite(models.Model):
    _name = 'participation.tap.entite'

    participation_id = fields.Many2one('participation.tap', string="Participation")
    filaile = fields.Char('Entité')
    capitaux = fields.Float("Capitaux propres")
    dont_capital = fields.Float("Dont capital")
    res = fields.Float("Résultat Dernier exercice")
    avances = fields.Float("Prêts et avances accordées")
    dividende = fields.Float("Dividendes encaissés")
    account_value = fields.Float("Valeur comptable des titres détenus")

class ReportHonoraire(models.Model):
    _name = 'report.honoraire'


    liasse_id = fields.Many2one('account.liasse.report_config', string="Liasse")
    date_from = fields.Date(string='Start Date', default=date.today().replace(day=1, month=1), requred=True)
    date_to = fields.Date(string='End Date', default=date.today().replace(day=31, month=12), requred=True)
    year = fields.Char("Exercice", compute="compute_fiscal_year")
    line_ids = fields.One2many('report.honoraire.line', 'honoraire_id', string="lines")

    def compute_fiscal_year(self):
        for record in self:
            record.year = record.date_to.strftime("%Y")

    def calculate_honoraire(self):
        res = self.env['account.liasse.config'].get_compte_res(self.date_from.replace(year=self.date_from.year - 1),self.date_to.replace(year=self.date_from.year - 1))

class ReportHonoraireLine(models.Model):
    _name = 'report.honoraire.line'

    honoraire_id = fields.Many2one('report.honoraire', string="honoraire")
    partner_id = fields.Many2one('res.partner', string='Contact',requred=True)
    amount = fields.Float('Montant')

class ReportTAP(models.Model):
    _name = 'report.tap'


    liasse_id = fields.Many2one('account.liasse.report_config', string="Liasse")
    date_from = fields.Date(string='Start Date', default=date.today().replace(day=1, month=1), requred=True)
    date_to = fields.Date(string='End Date', default=date.today().replace(day=31, month=12), requred=True)
    year = fields.Char("Exercice", compute="compute_fiscal_year")
    line_ids = fields.One2many('report.tap.line', 'tap_id', string="lines")

    def compute_fiscal_year(self):
        for record in self:
            record.year = record.date_to.strftime("%Y")

    def calculate_tap(self):
        res = self.env['account.liasse.config'].get_compte_res(self.date_from.replace(year=self.date_from.year - 1),self.date_to.replace(year=self.date_from.year - 1))

class ReportTAPLine(models.Model):
    _name = 'report.tap.line'

    tap_id = fields.Many2one('report.tap', string="TAP")
    partner_id = fields.Many2one('res.partner', string='Contact',requred=True)
    tap_amount = fields.Float('TAP')
    ca_imposable = fields.Float('CA imposable')
    ca_exo = fields.Float('CA exonéré')

class ReportTVCP(models.Model):
    _name = 'report.tvcp'


    liasse_id = fields.Many2one('account.liasse.report_config', string="Liasse")
    exercice_id = fields.Many2one('account.exercice', 'Exercice comptable', required=True)
    date_from = fields.Date(string='Start Date', related="exercice_id.date_from")
    date_to = fields.Date(string='End Date', related="exercice_id.date_to")
    year = fields.Char("Exercice", compute="compute_fiscal_year")
    # Solde au 31/12/N-2
    Capital_social_1 = fields.Float('Capital social')
    Prime_emission_1 = fields.Float('Prime emission')
    Ecart_Evaluation_1 = fields.Float('Ecart Evaluation')
    EcartReevaluation_1 = fields.Float('Ecart Réévaluation')
    ResevesResultats_1 = fields.Float('Reseves Résultats')
    # Changement méthode comptable N-1
    Capital_social_2 = fields.Float('Capital social')
    Prime_emission_2 = fields.Float('Prime emission')
    Ecart_Evaluation_2 = fields.Float('Ecart Evaluation')
    EcartReevaluation_2 = fields.Float('Ecart Réévaluation')
    ResevesResultats_2 = fields.Float('Reseves Résultats')
    # Correction d'erreurs significatives N-1
    Capital_social_22 = fields.Float('Capital social')
    Prime_emission_22 = fields.Float('Prime emission')
    Ecart_Evaluation_22 = fields.Float('Ecart Evaluation')
    EcartReevaluation_22 = fields.Float('Ecart Réévaluation')
    ResevesResultats_22 = fields.Float('Reseves Résultats')
    # Réévaluation des immobilisations N-1
    Capital_social_3 = fields.Float('Capital social')
    Prime_emission_3 = fields.Float('Prime emission')
    Ecart_Evaluation_3 = fields.Float('Ecart Evaluation')
    EcartReevaluation_3 = fields.Float('Ecart Réévaluation')
    ResevesResultats_3 = fields.Float('Reseves Résultats')
    # Profits ou pertes non comptabilisés dans le compte de résultat N-1
    Capital_social_4 = fields.Float('Capital social')
    Prime_emission_4 = fields.Float('Prime emission')
    Ecart_Evaluation_4 = fields.Float('Ecart Evaluation')
    EcartReevaluation_4 = fields.Float('Ecart Réévaluation')
    ResevesResultats_4 = fields.Float('Reseves Résultats')
    # Dividendes payés  N-1
    Capital_social_5 = fields.Float('Capital social')
    Prime_emission_5 = fields.Float('Prime emission')
    Ecart_Evaluation_5 = fields.Float('Ecart Evaluation')
    EcartReevaluation_5 = fields.Float('Ecart Réévaluation')
    ResevesResultats_5 = fields.Float('Reseves Résultats')
    # Augmentation de capital
    Capital_social_6 = fields.Float('Capital social')
    Prime_emission_6 = fields.Float('Prime emission')
    Ecart_Evaluation_6 = fields.Float('Ecart Evaluation')
    EcartReevaluation_6 = fields.Float('Ecart Réévaluation')
    ResevesResultats_6 = fields.Float('Reseves Résultats')
    # Résultat net de l'exercice  N-1
    Capital_social_7 = fields.Float('Capital social')
    Prime_emission_7 = fields.Float('Prime emission')
    Ecart_Evaluation_7 = fields.Float('Ecart Evaluation')
    EcartReevaluation_7 = fields.Float('Ecart Réévaluation')
    ResevesResultats_7 = fields.Float('Reseves Résultats')
    # Changement méthode comptable N
    Capital_social_8 = fields.Float('Capital social')
    Prime_emission_8 = fields.Float('Prime emission')
    Ecart_Evaluation_8 = fields.Float('Ecart Evaluation')
    EcartReevaluation_8 = fields.Float('Ecart Réévaluation')
    ResevesResultats_8 = fields.Float('Reseves Résultats')
    # Correction d'erreurs significatives N
    Capital_social_9 = fields.Float('Capital social')
    Prime_emission_9 = fields.Float('Prime emission')
    Ecart_Evaluation_9 = fields.Float('Ecart Evaluation')
    EcartReevaluation_9 = fields.Float('Ecart Réévaluation')
    ResevesResultats_9 = fields.Float('Reseves Résultats')
    # Réévaluation des immobilisations N
    Capital_social_10 = fields.Float('Capital social')
    Prime_emission_10 = fields.Float('Prime emission')
    Ecart_Evaluation_10 = fields.Float('Ecart Evaluation')
    EcartReevaluation_10 = fields.Float('Ecart Réévaluation')
    ResevesResultats_10 = fields.Float('Reseves Résultats')
    # Profits ou pertes non comptabilisés dans le compte de résultat N
    Capital_social_11 = fields.Float('Capital social')
    Prime_emission_11 = fields.Float('Prime emission')
    Ecart_Evaluation_11 = fields.Float('Ecart Evaluation')
    EcartReevaluation_11 = fields.Float('Ecart Réévaluation')
    ResevesResultats_11 = fields.Float('Reseves Résultats')
    # Dividendes payés  N
    Capital_social_12 = fields.Float('Capital social')
    Prime_emission_12 = fields.Float('Prime emission')
    Ecart_Evaluation_12 = fields.Float('Ecart Evaluation')
    EcartReevaluation_12 = fields.Float('Ecart Réévaluation')
    ResevesResultats_12 = fields.Float('Reseves Résultats')
    # Augmentation de capital N
    Capital_social_13 = fields.Float('Capital social')
    Prime_emission_13 = fields.Float('Prime emission')
    Ecart_Evaluation_13 = fields.Float('Ecart Evaluation')
    EcartReevaluation_13 = fields.Float('Ecart Réévaluation')
    ResevesResultats_13 = fields.Float('Reseves Résultats')
    # Résultat net de l'exercice  N
    Capital_social_14 = fields.Float('Capital social')
    Prime_emission_14 = fields.Float('Prime emission')
    Ecart_Evaluation_14 = fields.Float('Ecart Evaluation')
    EcartReevaluation_14 = fields.Float('Ecart Réévaluation')
    ResevesResultats_14 = fields.Float('Reseves Résultats')
    def compute_fiscal_year(self):
        for record in self:
            record.year = record.date_to.strftime("%Y")




