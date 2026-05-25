# -*- coding: utf-8 -*-


from odoo import models, fields, api


class ResConfigSettingInherited(models.TransientModel):
	_inherit = 'res.config.settings'

	type_prelevement = [
							('par_categorie_article','Par Categorie Article'),
							('par_montant_global','Par Montant Global'),
		     		   ]
	
	type_prevelement = fields.Selection(type_prelevement,string = 'Manière de Préveler', required=True)
	montant_prelever = fields.Float('Montant à Prélever')

	@api.model
	def get_values(self):
		my_selection_value = self.env['ir.config_parameter'].sudo().get_param('prevelement_frais_informatique.type_prevelement', default='par_categorie_article')
		my_float_value = self.env['ir.config_parameter'].sudo().get_param('prevelement_frais_informatique.montant_prelever', default=0.0)
		
		return {
					'type_prevelement': my_selection_value,
					'montant_prelever': float(my_float_value),
				}
	
	def set_values(self):
		self.env['ir.config_parameter'].sudo().set_param('prevelement_frais_informatique.type_prevelement', self.type_prevelement)
		self.env['ir.config_parameter'].sudo().set_param('prevelement_frais_informatique.montant_prelever', str(self.montant_prelever))