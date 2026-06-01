# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)

class ConsultationTriage(models.Model):
	_name = 'fertility.triage'
	_description = 'Consultation Triage'

	triage_name = fields.Char(string='Triage ID')

	def name_get(self):
		result = []
		for rec in self:
			result.append((rec.id, "%s" % (rec.triage_name)))		
		return result




	patient_id = fields.Many2one('fertility.patient')
	parent_id = fields.Many2one(related='patient_id.parent_id')
	gender = fields.Selection(related='patient_id.gender')
	age = fields.Integer(related='patient_id.age')
	date = fields.Date('Date de création', default=fields.Date.today)
	# name = fields.Char(size=256, string='Numéro', readonly=True),
	# user_id = fields.Many2one('res.users', string='Infirmier(ère)')
	weight = fields.Float(string='Poids', help='Poids en Kilos')		
	height = fields.Float(string='Taille')
	systolic = fields.Char(string='Tension artérielle')
	diastolics = fields.Integer(string='Pression Diastolique')
	hip = fields.Float(string='Périmètre Pelvien')
	bmi = fields.Float(string='IMC')
	respiratory_rate = fields.Integer(string='Fréquence Respiratoire')		
	temperature = fields.Float(string='Température',help='Température en Celcius')									
	osat= fields.Integer(string='Saturation en Oxygène')
	
	# starttime = fields.datetime(string='Start', required=True)
	# endtime = fields.datetime(string='End', required=False)

	notes_eval = fields.Text(string='Notes')
	# notes_anamnese = fields.Text(string='Notes')
	bpm = fields.Integer(string='Fréquence Cardiaque')
	abdominal_circ = fields.Float(string='Périmètre Abdominal')
	
	triage_pc = fields.Float(string='Périmètre Crânien')
	triage_pb = fields.Float(string='Périmètre Brachial')
	pc = fields.Float(string='Périmètre Crânien')
	pb = fields.Float(string='Périmètre Brachial')
	# autre_indication = fields.Text(string='Autres Diagnostics'),
	# diagnostiques = fields.Text(string='Diagnostique(s) définitif(s)'),
	# is_definir = fields.Boolean('Déterminer les diagnostiques définitif(s)')
	# resume_clinique = fields.Text(string="Résumé Clinique / Traitement")
	# resume_recommande = fields.Text(string="Autres Recommandation")
	
	antecedent = fields.Text(string='Antécédents')
	is_glycemia = fields.Boolean('> 500')
	glycemia = fields.Float(string='Glycémie – Dextro')
	done = fields.Boolean(string='Fait',default=False)
	# # Examen physique
	# etat_general = :fields.Text('Etat général')
	# neurologie = fields.Text('Neurologie')
	# tete_cou = fields.Text('Tête et cou')
	# thorax = fields.Text('Thorax')
	# abdomen = fields.Text('Abdomen')
	# membre = fields.Text('Membres')
	# autres = fields.Text('Autres')

	@api.model
	def create(self, vals):	
		vals['triage_name'] = self.env['ir.sequence'].next_by_code('fertility.triage.name')
		return super(ConsultationTriage, self).create(vals)	


	def action_done (self):
		self.done = True
	
	@api.model
	def get_available_qr_methods_in_sequence(self):
		""" Same as _get_available_qr_methods but without returning the sequence,
		and using it directly to order the returned list.
		"""
		_logger.info("------------------------------HERE-------------------------------")
		_logger.info(self.env.context)
		all_available = []
		all_available.sort(key=lambda x: x[2])
		return [(code, name) for (code, name, sequence) in all_available]