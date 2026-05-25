# -*- coding: utf-8 -*-
#
# Auteur : BKM
# Date	 : 11 Avril 22
################################
from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
import logging
_logger = logging.getLogger(__name__)



class Doctor(models.Model):
	_name = 'module.doctor'
	_description = 'Doctor'

	cnom = fields.Char('CNom')	
	name = fields.Char(string='Nom', required=True)	
	service_id = fields.Many2one('module.service', 'Service')
	active = fields.Boolean(
		'Active', default=True,
		help="If unchecked, it will allow you to hide the doctor without removing it.")
	
class RubriqueModule(models.Model):

	_name = 'module.rubrique'
	_description = 'Description les rubriques de l\'hopital'
	
	name = fields.Char(string="Rubrique", required=True)
	code = fields.Char(string="Code")
	service_id = fields.Many2one('module.service', 'Service')
	active = fields.Boolean(
		'Active', default=True,
		help="If unchecked, it will allow you to hide the rubrique without removing it.")


	def unlink(self):
		return super(RubriqueModule, self).unlink()

class ServicesModule(models.Model):

	_name = 'module.service'
	_description = 'Descrit les services de l\'hopital'
	
	name = fields.Char(string="Service", required=True)
	code = fields.Char(string="Code")
	medecin = fields.One2many('module.doctor', 'service_id', string="Medecin")
	rubrique = fields.One2many('module.rubrique', 'service_id', string="Rubriques")
	active = fields.Boolean(
		'Active', default=True,
		help="If unchecked, it will allow you to hide the service without removing it.")


	def unlink(self):
		return super(ServicesModule, self).unlink()

		


