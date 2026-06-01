# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
import logging

_logger = logging.getLogger(__name__)
from datetime import datetime, time, date, timedelta


class Partner_Custom(models.Model):
    _inherit = "res.partner"
   
    srvice_stock = fields.Boolean(string="Service Stock")
    
    @api.onchange('srvice_stock')
    def make_service_particular(self):
        for service in self:
            if service.srvice_stock == True:
                service.company_type = 'person'

