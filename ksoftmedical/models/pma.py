# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)

class PMAStimulation(models.Model):
	_name = 'fertility.pma.stimulation'
	_description = 'PMA Stimulation'

	pma_id=fields.Many2one('fertility.pma')
	jour = fields.Selection([('s1','S1'),('s2','S2'),('s3','S3'),('s4','S4'),('s5','S5'),('s6','S6'),('s7','S7'),('s8','S8'),('s9','S9'),
		('s10','S10'),('s11','S11'),('s12','S12'),('s13','S13'),('s14','S14'),('s15','S15'),('s16','S16')], string='Jour de traitement')
	e2 = fields.Char(string='E2')
	lh = fields.Char(string='LH')
	pr = fields.Char(string='Pr')
	ovaire_droit = fields.Html(string='OVAIRE DROIT')
	ovaire_gauche = fields.Html(string='OVAIRE GAUCHE')
	endometre = fields.Char(string='ENDOMETRE')


class PMA(models.Model):
	_name = 'fertility.pma'
	_description = 'PMA'
	_inherits = {
		'fertility.examen': 'consult_examen_id'
	}

	consult_examen_id = fields.Many2one('fertility.examen', required=True, ondelete="cascade", string="Examens")

	internal_status = fields.Selection([
		('invoicing1','Facturation'),
		('stimulation','Stimulation'),
		('open_stimulation','Attente de résultat'),
		('ponction','Ponction'),
		('invoicing2','Facturation'),
		('transfer','En Transfert'),
		('open_transfer','Attente de résultat'),
		('closed','Fermé')], string='Status', default='invoicing1')
	status = fields.Selection([
		('invoicing1','Facturation'),
		('stimulation','Stimulation'),
		('open_stimulation','Attente de résultat'),
		('ponction','Ponction'),
		('invoicing2','Facturation'),
		('transfer','En Transfert'),
		('open_transfer','Attente de résultat'),
		('closed','Fermé')], compute='_get_status')

	name = fields.Char(string='Name', readonly=True)
	move_id1 = fields.Many2one('account.move') #
	move_id2 = fields.Many2one('account.move') #

	triage_id = fields.Many2one('fertility.triage', compute='_get_triage')

	triage_id1 = fields.Many2one('fertility.triage') #
	triage_id2 = fields.Many2one('fertility.triage') #
	triage_id3 = fields.Many2one('fertility.triage') # 

	date = fields.Date('Date de création', required=True, default=fields.Date.today)
	datetime = fields.Datetime('Date/Heure', required=True, default=fields.Datetime.now)
	appointment_id = fields.Many2one('fertility.appointment')
	journal_id = fields.Many2one('account.journal', related='appointment_id.consultation_type.journal_id')
	parent_id = fields.Many2one(related='patient_id.parent_id')
	gender = fields.Selection(related='patient_id.gender')
	age = fields.Integer(related='patient_id.age')
	doctor_id = fields.Many2one('fertility.doctor')

### SIMULATION


	technique_envisage = fields.Selection([('fiv','FIV'),('icsi','ICSI'),('iiu','IIU'),('tec','TEC')], string='Technique envisagée')
	origine_gamete = fields.Selection([('couple','Couple'),('don','Don'),('spzcongel','SPZ congèl'),('spzchir','Spz chir.')], string='Origine gamètes')
	technique_associe = fields.Selection([('imsi','IMSI'),('hatch','Hatch.'),('cp','CP'),('j2j5','J2/J5')], string='Technique associée')
	indication_fertilite = fields.Selection([('mixte','Mixte'),('homme','Homme'),('femme','Femme')], string='Indication Infertilité')

	tentative_no = fields.Integer('Tentative N')
	tentative_total = fields.Integer('Nombre total tentatives')
	tentative_project = fields.Integer('Pour ce projet')
	tentative_muette = fields.Integer('Dont Muette')

	date_serologie_f = fields.Date('Sérologie date F')
	date_serologie_h = fields.Date('Sérologie date H')
	date_cs = fields.Date('CS Anesthésie date')
	date_bilan = fields.Date('Bilan Pré-op date')

	cycle_naturel = fields.Boolean('Cycle naturel')
	cycle_programme = fields.Boolean('Cycle programmé')
	cycle_substitue = fields.Boolean('Cycle substitué')
	cycle_naturel_modif = fields.Boolean('Cycle naturel modifié')
	gonal = fields.Boolean('GONAL F')
	purgegon = fields.Boolean('PURGEGON')
	fostimon = fields.Boolean('FOSTIMON')
	pergoveris = fields.Boolean('PERGOVERIS')
	menopur = fields.Boolean('MENOPU')
	luveris = fields.Boolean('LUVERIS')
	traitement_stimulation = fields.Char('Traitement')


	traitement_ids = fields.One2many('fertility.pma.stimulation','pma_id')


	agonistes = fields.Boolean('Agonistes')
	protocol_court = fields.Boolean('Protocole court')
	protocol_long_retard = fields.Boolean('Protocole long forme retard')
	protocol_long_folliculaire = fields.Boolean('Protocole long forme rapide Phase folliculaire')
	protocol_long_luteale = fields.Boolean('Protocole long forme rapide Phase lutéale')
	antagonistes = fields.Boolean('Antagonistes')
	dose_unique = fields.Boolean('Dose unique')
	dose_multiple = fields.Boolean('Dose multiple')
	orgalutran = fields.Boolean('Orgalutran')
	cetrotide = fields.Boolean('Cetrotide')
	citrate = fields.Boolean('Citrate de Clomiphène')
	nb_total_comprime = fields.Integer('Nb. Total comprimés')

	commentaire_clinique = fields.Text('Commentaires clinique')

	declenchement_traitement = fields.Char('Traitement post transfert')
	hcg_urinaire = fields.Boolean('HCG Urinaire')
	hcg_recombinante = fields.Boolean('HCG Recombinante')
	progestatif = fields.Boolean('Progestatif')
	hcg = fields.Boolean('HCG')
	declenchement_datetime = fields.Datetime('HCG Urinaire')
	declenchement_autre = fields.Char('Autre')

###

	patient_id = fields.Many2one('fertility.patient')
	date = fields.Date('Date de création', default=fields.Date.today)
	# name = fields.Char(size=256, related='triage_id.Numéro', readonly=True),
	# user_id = fields.Many2one('res.users', related='triage_id.Infirmier(ère)')
	weight = fields.Float(related='triage_id.weight')		
	height = fields.Float(related='triage_id.height')
	systolic = fields.Char(related='triage_id.systolic')
	diastolics = fields.Integer(related='triage_id.diastolics')
	hip = fields.Float(related='triage_id.hip')
	bmi = fields.Float(related='triage_id.bmi')
	respiratory_rate = fields.Integer(related='triage_id.respiratory_rate')		
	temperature = fields.Float(related='triage_id.temperature')									
	osat= fields.Integer(related='triage_id.osat')
	notes_eval = fields.Text(related='triage_id.notes_eval')
	bpm = fields.Integer(related='triage_id.bpm')
	abdominal_circ = fields.Float(related='triage_id.abdominal_circ')
	triage_pc = fields.Float(related='triage_id.triage_pc')
	triage_pb = fields.Float(related='triage_id.triage_pb')
	pc = fields.Float(related='triage_id.pc')
	pb = fields.Float(related='triage_id.pb')
	is_glycemia = fields.Boolean(related='triage_id.is_glycemia')
	glycemia = fields.Float(related='triage_id.glycemia')
	done = fields.Boolean(related='triage_id.done')
	
	## PONCTION
	date_ponction = fields.Date(string="Date de la ponction")
	ponctionner = fields.Many2one('fertility.doctor', string="Ponctionneur")
	is_verify = fields.Boolean(string="Verification")
	date_declenchement = fields.Datetime(string="Date-Heure de declenchement")
	ponction = fields.Selection([('asp','Aspiration'),('sering','Seringue')], string="Ponction")
	nbre_foll1 = fields.Integer(string="Nbre Foll > 16 mm")
	nbre_foll2 = fields.Integer(string="Nbre Foll 13-15 mm")
	nbre_ovocyte = fields.Integer(string="Nbre Ovocytes recueillis")

	## EMBRYOLOGIE
	techn_embryologie = fields.Selection([('fiv','FIV'),('icsi','ICSI'),('imsi','IMSI')], string='Technique')
	nbre_ovocyt_mature = fields.Integer(string="Nbre Ovocytes matures/injectés")
	nbre_embryon = fields.Integer(string="Nbre Embryons Obtenus")
	congelation = fields.Selection([('oui','OUI'),('non','NON')],string="Congelation Embryonnaire")
	congelation1 = fields.Char(string="Congelation Nb")
	congelation1 = fields.Char(string="Congelation J")

	type_embryon1 = fields.Char(string="Type Embryons Nb")
	type_embryon2 = fields.Char(string="Type Embryons J")
	type_embryon3 = fields.Char(string="Type Embryons")
	
	# @api.model
	# def create(self, vals):	
		# ctx = self.env.context.copy()
		# _logger.info(ctx)
		# vals['name'] = self.env['ir.sequence'].next_by_code('fertility.pma.name')

		# vals['move_id1'] = self.env['account.move'].with_context(self.env.context).create({
			# 'move_type':'out_invoice', 
			# 'ref':vals['name'], 
			# 'invoice_line_ids':[ (0,0,{ 'name': 'FIV', 'price_unit': 0, 'quantity':1 })] }).id

		# pma = super(PMA, self).create(vals)
		# self.patient_id.pma_id = pma.id
		# return pma
		
	@api.model
	def create(self, vals): 
		ctx = self.env.context.copy()
		_logger.info(ctx)
		vals['name'] = self.env['ir.sequence'].next_by_code('fertility.pma.name')

		pma = super(PMA, self).create(vals)
		
		product1 = pma.appointment_id.appointment_type.stimulation_product_id
		pma.write({'move_id1':self.env['account.move'].with_context(self.env.context).create({
			'move_type':'out_invoice', 
			'ref':vals['name'], 
			'invoice_line_ids':[ (0,0,{ 'product_id': product1.id, 'price_unit': product1.list_price, 'quantity':1 })] }).id })

		product2 = pma.appointment_id.appointment_type.transfer_product_id
		pma.write({'move_id2':self.env['account.move'].with_context(self.env.context).create({
			'move_type':'out_invoice',
			'ref':vals['name'],
			'invoice_line_ids':[ (0,0,{ 'product_id': product2.id, 'price_unit': product2.list_price, 'quantity':1 })] }).id })
		
		self.patient_id.pma_id = pma.id

		return pma

	def _get_triage(self):
		for pma in self:		
			if pma.triage_id3.done:
				pma.triage_id = pma.triage_id3.id
			else :
				if pma.triage_id2.done :
					pma.triage_id = pma.triage_id2.id
				else :
					pma.triage_id = pma.triage_id1.id

	def _get_status(self):
		for pma in self:		
			if pma.internal_status=='invoicing1' and pma.move_id1.payment_state=='paid' :
				pma.internal_status = 'stimulation'
			if pma.internal_status=='invoicing2' and pma.move_id2.payment_state=='paid' :
				pma.internal_status = 'transfer'
			pma.status = pma.internal_status

	def unlink(self):
		for pma in self:
			pma.consult_examen_id.unlink()		
		return super(PMA, self).unlink()

	def action_home_done (self):
		self.write({'internal_status':'invoicing1','triage_id1':self.env['fertility.triage'].with_context(self.env.context).create({}).id})

	def action_stimulation_done (self):
		self.ensure_one()
		# imagerie_ids = self.consult_examen_id.imagerie_ids.filtered(lambda imagerie: imagerie.status == 'draft')
		# labo_ids = self.consult_examen_id.labo_ids.filtered(lambda imagerie: imagerie.status == 'draft')

		# lines = [ (0,0,{'display_type':'line_section', 'name':'Imagerie', 'debit':0, 'credit':0, 'account_id':False})]
		# lines.extend( imagerie_ids.mapped(lambda imagerie : (0,0,{ 'product_id': imagerie.analyse.id, 'price_unit': imagerie.analyse.list_price, 'quantity':1 })) )
		# lines.append( (0,0,{'display_type':'line_section', 'name':'Laboratoire', 'debit':0, 'credit':0, 'account_id':False}) )
		# lines.extend( labo_ids.mapped(lambda labo : (0,0,{'product_id': labo.analyse.id, 'price_unit': labo.analyse.list_price, 'quantity':1 })) )

		# move_id = self.env['account.move'].create({
			# 'move_type':'out_invoice', 
			# 'journal_id':self.journal_id.id,
			# 'partner_id':self.patient_id.partner_id.id,
			# 'ref':self.appointment_id.name			})
		# move_id.write({'invoice_line_ids':lines})
		# imagerie_ids.write({'move_id': move_id.id,'internal_status':'invoicing','patient_id':self.patient_id.id})
		# labo_ids.write({'move_id': move_id.id,'internal_status':'invoicing','patient_id':self.patient_id.id})
		self.internal_status = 'ponction'

	def action_stimulation_done2 (self):
		self.internal_status = 'ponction'

	def action_poction_done (self):
		self.internal_status = 'invoicing2'

	def action_transfer_done (self):
		self.internal_status = 'open_transfer'

	def action_close (self):
		self.internal_status = 'closed'

	def action_return (self):
		self.internal_status = 'home'
		self.consult_examen_id.imagerie_ids.write({'internal_status':'draft'})
		self.consult_examen_id.labo_ids.write({'internal_status':'draft'})

	def action_patient (self):
		return {
			'name': 'Patient',
			'view_mode': 'form',
			'res_model': 'fertility.patient',
			'res_id': self.patient_id.id,
			'type': 'ir.actions.act_window',
		}