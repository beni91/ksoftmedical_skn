# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
import logging

_logger = logging.getLogger(__name__)

class RapportJournalier(models.Model):
    _name = 'ksoft.rapport.dailly'

    date_record = fields.Datetime(string="Date", required="True")
    resume = fields.Html(string="Resumé", required="True")
    medecin = fields.Many2one('res.users', string="Médecin", default=lambda self: self.env.user, )