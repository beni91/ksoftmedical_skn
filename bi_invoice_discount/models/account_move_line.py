# -*- coding: utf-8 -*-
################################################################################
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
################################################################################
from odoo import api, fields, models, _


class account_move_line(models.Model):
    _inherit = 'account.move.line' 

    discount_line = fields.Boolean('is a discount line')                    
