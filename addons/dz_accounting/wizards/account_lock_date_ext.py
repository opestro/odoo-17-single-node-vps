# -*- coding: utf-8 -*-
from odoo import api, fields, models, SUPERUSER_ID, _


class AccountUpdateLockDate(models.TransientModel):
    _inherit = 'account.lock.date'


    @api.model
    def default_get(self, field_list):
        res = super(AccountUpdateLockDate, self).default_get(field_list)
        company = self.env.user.company_id
        confirm = self.env.context.get('confirm')
        if not confirm:
            res.update({
                'company_id': company.id,
                'period_lock_date': company.period_lock_date,
                'fiscalyear_lock_date': company.fiscalyear_lock_date,
            })
        else:
            res.update({
                'company_id': self.env.context.get('company_id'),
                'period_lock_date': self.env.context.get('period_lock_date'),
                'fiscalyear_lock_date': self.env.context.get('fiscalyear_lock_date')
            })
        return res