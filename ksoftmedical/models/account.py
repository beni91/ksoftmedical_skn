# -*- coding: utf-8 -*-

from odoo import models,fields,tools, api, _
from odoo.tools import float_is_zero
import datetime
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class AccountCustom(models.Model):
    _inherit = 'account.move.line'

    ref_item = fields.Char('Réf. Item')
    

