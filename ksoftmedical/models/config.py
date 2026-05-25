# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class Config(models.Model):
	_name = 'fertility.config'



	journal_id = fields.Many2one('account.journal', string='Journal de vente', domain="[('type', '=', 'sale')]")
	stimulation_product_id = fields.Many2one('product.template')
	transfer_product_id = fields.Many2one('product.template')