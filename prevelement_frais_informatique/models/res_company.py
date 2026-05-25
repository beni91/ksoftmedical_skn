# -*- coding: utf-8 -*-


from odoo import api, fields, models,tools, _


class ResCompanyInherit(models.Model):
	_inherit = 'res.company'

	type_prelevement = [
							('par_categorie_article','Par Categorie Article'),
							('par_montant_global','Par Montant Global'),
		     		   ]
	
	type_prevelement = fields.Selection(type_prelevement,string = 'Manière de Préveler', required=True)
