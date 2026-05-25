# -*- coding: utf-8 -*-
################################################################################
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
################################################################################
from odoo import api, fields, models, _


class account_account(models.Model):
    _inherit = 'account.account'
    
    discount_account = fields.Boolean('Discount Account')