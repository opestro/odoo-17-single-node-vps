# -*- coding: utf-8 -*-
import re

from odoo import api, models, fields
import logging
_logger = logging.getLogger(__name__)
class FinancialReport(models.TransientModel):
    _inherit = "financial.report"

    def get_account_lines(self, data):
        res = super(FinancialReport, self).get_account_lines(data)
        _logger.info(str(res))
        return res

    def view_report_pdf(self):
        """This function will be executed when we click the view button
                from the wizard. Based on the values provided in the wizard, this
                function will print pdf report"""
        self.ensure_one()
        data = dict()
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(
            ['date_from', 'enable_filter', 'debit_credit', 'date_to',
             'account_report_id', 'target_move', 'view_format',
             'company_id'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(
            used_context,
            lang=self.env.context.get('lang') or 'en_US')

        report_lines = self.get_account_lines(data['form'])
        # find the journal items of these accounts
        journal_items = self.find_journal_items(report_lines, data['form'])

        def set_report_level(rec):
            """This function is used to set the level of each item.
            This level will be used to set the alignment in the dynamic reports."""
            level = 1
            if not rec['parent']:
                return level
            else:
                for line in report_lines:
                    key = 'a_id' if line['type'] == 'account' else 'id'
                    if line[key] == rec['parent']:
                        return level + set_report_level(line)

        # finding the root
        for item in report_lines:
            item['balance'] = round(item['balance'], 2)
            if not item['parent']:
                item['level'] = 1
                parent = item
                report_name = item['name']
                id = item['id']
                report_id = item['r_id']
            else:
                item['level'] = set_report_level(item)
        currency = self._get_currency()
        data['currency'] = currency
        data['journal_items'] = journal_items
        data['report_lines'] = report_lines
        # Data before this period

        data_previous = dict()
        data_previous['ids'] = self.env.context.get('active_ids', [])
        data_previous['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data_previous['form'] = self.read(
            ['date_from', 'enable_filter', 'debit_credit', 'date_to',
             'account_report_id', 'target_move', 'view_format',
             'company_id'])[0]
        data_previous['form']['date_to'] = data_previous['form']['date_from']
        first_line = self.env['account.move.line'].search([],order='date ASC')[0]
        data_previous['form']['date_from'] = first_line.date if first_line else data_previous['form']['date_from']
        used_context = self._build_contexts(data_previous)
        data_previous['form']['used_context'] = dict(
            used_context,
            lang=self.env.context.get('lang') or 'en_US')

        report_lines = self.get_account_lines(data_previous['form'])
        # find the journal items of these accounts
        journal_items = self.find_journal_items(report_lines, data_previous['form'])

        def set_report_level(rec):
            """This function is used to set the level of each item.
            This level will be used to set the alignment in the dynamic reports."""
            level = 1
            if not rec['parent']:
                return level
            else:
                for line in report_lines:
                    key = 'a_id' if line['type'] == 'account' else 'id'
                    if line[key] == rec['parent']:
                        return level + set_report_level(line)

        # finding the root
        for item in report_lines:
            item['balance'] = round(item['balance'], 2)
            if not item['parent']:
                item['level'] = 1
                parent = item
                report_name = item['name']
                id = item['id']
                report_id = item['r_id']
            else:
                item['level'] = set_report_level(item)
        currency = self._get_currency()
        data_previous['currency'] = currency
        data_previous['journal_items'] = journal_items
        data_previous['report_lines'] = report_lines
        data['previous_report_lines'] = report_lines

        # checking view type

        _logger.info("=====================***")

        return self.env.ref(
            'dz_accounting.financial_report_pdf_ext').report_action(self,
                                                                      data)

class ReportPdf(models.AbstractModel):
    """ Abstract model for generating PDF report value and send to template """

    _name = 'report.dz_accounting.report_financial_ext'
    _description = 'Financial Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        """ Provide report values to template """
        ctx = {
            'data': data,
            'journal_items': data['journal_items'],
            'report_lines': data['report_lines'],
            'previous_report_lines': data['previous_report_lines'],
            'account_report': data['form']['account_report_id'][1],
            'currency': data['currency'],
        }
        return ctx
