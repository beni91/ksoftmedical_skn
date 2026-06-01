# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import AccessError, UserError, ValidationError


class PartnerCustom(models.Model):
    _inherit = "res.partner"
   
    matricule = fields.Boolean(string="Matricule")
    bon_envoi = fields.Boolean(string="Bon d'envoi")
    classeuser = fields.Boolean(string="Catégorie")
   