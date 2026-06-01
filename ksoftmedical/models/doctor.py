# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class Doctor(models.Model):
	_name = 'fertility.doctor'
	_description = 'Fertility Doctor'

	name = fields.Char('Nom', required=True)	
	cnom = fields.Char('CNOM')
	user_id = fields.Many2one('res.users', 'User', required=True)	
	speciality_id = fields.Many2one('fertility.doctor.speciality', 'Specialité')
	service_id = fields.Many2one('ksoft.services', string="Service")


class DoctorSpeciality(models.Model):
	_name = 'fertility.doctor.speciality'
	_description = 'Doctor Speciality'
	
	code = fields.Char('Code', size=5)
	name = fields.Char('Specialité', required=True)	