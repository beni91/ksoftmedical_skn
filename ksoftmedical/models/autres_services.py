# -*- coding: utf-8 -*-
#
# Auteur : BKM
# Date   : 11 Avril 22
################################
from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
import logging
_logger = logging.getLogger(__name__)


type_service = [('adm','Administration'),
                                 ('cons','Consultation'),
                                 ('urg','Urgence'),('rea','Réanimation'),('hospi','Hospitalisation'),
                                 ('soins','Soins ambulatoires'),('labo','Laboratoire'),
                                 ('pharma','Pharmacie'),('shop','Shop Optique'),
                                 ('img','Imagerie'),('vac','Vaccination'),('chi','Chirurgie'),
                                 ('dial','Dialyse'),('autres','Autres')
                ]


class AutresOrientationsModule(models.Model):

    _name = 'module.orientation'
    _description = 'Autres Orientations'
    _order = 'date_orientation desc'

    diag_name = fields.Char(string="ID Orientation")
    patient_id = fields.Many2one('fertility.patient', string='Patient')
    nompatient = fields.Char(related='patient_id.nom', string="Nom")
    pnompatient = fields.Char(related='patient_id.postnom', string="Postnom")
    prnompatient = fields.Char(related='patient_id.prenom', string="Prenom")
    dob = fields.Date(related='patient_id.birth', string='Date Naiss', readonly=True, )
    sex = fields.Selection([('m', 'Masculin'), ('f', 'Féminin')], string='Sexe', 
        related='patient_id.gender', readonly=True)
    age = fields.Integer(related='patient_id.age', string='Age', readonly=True)
    date_orientation = fields.Date(string='Date', readonly=True, default=fields.Datetime.now())
    medecin = fields.Many2one('fertility.doctor', readonly=True, string="Médecin")
    medecin_ = fields.Many2one('res.users', readonly=True, string="Médecin")
    orientation = fields.Char(string='Orientation')
    description = fields.Char(string="Clinique")
    is_print = fields.Boolean(string="#", default=True)

    protocole = fields.Html(string="Observation")
    product = fields.Many2one('product.template', string="Actes Med/Actes Inf")
    medicament = fields.Many2one('product.template', string="Produits")
    materiels = fields.Many2many('product.template', string="Materiels")
    internal_status = fields.Selection(
        [('draft', 'En attente'), ('invoicing', 'Facturation'), 
         ('ongoing', 'Validation'), ('done', 'Fait')], 'Etat', default='draft')
    is_done = fields.Boolean(string="Fait", default=True)

    ## Selectionner le service ou sera donnée les soins
    service = fields.Many2one('ksoft.services', string="service")

    @api.onchange('is_actes')
    def set_product_traitement(self):
        if self.medicament or self.materiels:
            self.is_actes = False
           

    @api.model
    def default_get(self, fields):
        res = super(AutresOrientationsModule, self).default_get(fields)
        res['medecin_'] = self.env.user.id
        return res

    @api.model
    def create(self, vals):
        obj_doctors = self.env['fertility.doctor'].search([('user_id', '=', self.env.uid)])
        if obj_doctors is not None:
            for doctor in obj_doctors:
                vals['medecin'] = doctor.id
        return super(AutresOrientationsModule, self).create(vals)

    @api.model
    def write(self, vals):
        return super(AutresOrientationsModule, self).write(vals)

    def unlink(self):

        return super(AutresOrientationsModule, self).unlink()

class GetKinesitherapieModule(models.Model):

    _name = 'module.kine.request'
    _description = 'Demandes de kinesitheurapie'
    _order = 'date_recorded desc'

    patient_id = fields.Many2one('fertility.patient', string='Patient')
    nompatient = fields.Char(related='patient_id.nom', string="Nom")
    pnompatient = fields.Char(related='patient_id.postnom', string="Postnom")
    prnompatient = fields.Char(related='patient_id.prenom', string="Prenom")
    dob = fields.Date(related='patient_id.birth', string='Date Naiss', readonly=True, )
    sex = fields.Selection([('m', 'Masculin'), ('f', 'Féminin')], string='Sexe', 
        related='patient_id.gender', readonly=True)
    age = fields.Integer(related='patient_id.age', string='Age', readonly=True)
    date_recorded = fields.Date(string='Date', readonly=True, default=fields.Datetime.now())
    medecin = fields.Many2one('fertility.doctor', readonly=True, string="Médecin")
    medecin_ = fields.Many2one('res.users', readonly=True, string="Médecin")
    product = fields.Many2one('product.template', string="Actes kiné")
    nbre_seance = fields.Integer(string="Nbre séance")
    
    is_print = fields.Boolean(string="#", default=True)

    
    internal_status = fields.Selection(
        [('draft', 'Demande'), ('send', 'Envoyé')], 'Etat', default='draft')
    is_done = fields.Boolean(string="Fait", default=True)
    is_physical_medecine = fields.Boolean(string="Seance Méd. Physique", default=False)
    is_paid = fields.Boolean(string="Payé")

    ## Selectionner le service ou sera donnée les soins
    #service = fields.Many2one('ksoft.services', string="service")

    @api.model
    def create(self, vals):
        obj_doctors = self.env['fertility.doctor'].search([('user_id', '=', self.env.uid)])
        if obj_doctors is not None:
            for doctor in obj_doctors:
                vals['medecin'] = doctor.id
        return super(GetKinesitherapieModule, self).create(vals)

    @api.model
    def write(self, vals):
        return super(GetKinesitherapieModule, self).write(vals)

    def unlink(self):
        return super(GetKinesitherapieModule, self).unlink()  

class KinesitherapieModule(models.Model):

    _name = 'module.kinesitheurapie'
    _description = 'kinesitheurapie'
    _order = 'date_recorded desc'

    patient_id = fields.Many2one('fertility.patient', string='Patient')
    nompatient = fields.Char(related='patient_id.nom', string="Nom")
    pnompatient = fields.Char(related='patient_id.postnom', string="Postnom")
    prnompatient = fields.Char(related='patient_id.prenom', string="Prenom")
    dob = fields.Date(related='patient_id.birth', string='Date Naiss', readonly=True, )
    sex = fields.Selection([('m', 'Masculin'), ('f', 'Féminin')], string='Sexe', 
        related='patient_id.gender', readonly=True)
    age = fields.Integer(related='patient_id.age', string='Age', readonly=True)
    date_recorded = fields.Date(string='Date', readonly=True, default=fields.Datetime.now())
    date_done = fields.Date(string='Date de réalisation')
    medecin = fields.Many2one('fertility.doctor', readonly=True, string="Médecin")
    medecin_ = fields.Many2one('res.users', readonly=True, string="Médecin")
    product = fields.Many2one('product.template', string="Actes kiné")
    orientation = fields.Char(string='Observation')
    nbre_seance = fields.Integer(string="Nbre séance")
    description = fields.Char(string="Clinique")
    is_print = fields.Boolean(string="#", default=True)
    
    internal_status = fields.Selection(
        [('draft', 'Demande'), ('invoicing', 'Facturation'),
         ('pending', 'En attente'), ('done', 'Fait')], 'Etat', default='draft')
    is_done = fields.Boolean(string="Fait", default=True)
    is_physical_medecine = fields.Boolean(string="Seance Méd. Physique", default=False)
    is_paid = fields.Boolean(string="Payé")

    ## Selectionner le service ou sera donnée les soins
    service = fields.Many2one('ksoft.services', string="service")

    @api.model
    def create(self, vals):
        obj_doctors = self.env['fertility.doctor'].search([('user_id', '=', self.env.uid)])
        if obj_doctors is not None:
            for doctor in obj_doctors:
                vals['medecin'] = doctor.id
        return super(KinesitherapieModule, self).create(vals)

    @api.model
    def write(self, vals):
        return super(KinesitherapieModule, self).write(vals)

    def unlink(self):
        return super(KinesitherapieModule, self).unlink()


class HotellerieModule(models.Model):

    _name = 'ksoft.chambre'
    _description = 'Gestion de chambre'
    _order = 'id desc'

    #service_name = fields.Char(string="Unité de Soins Service")
    chambre_id =  fields.Many2one('product.template', domain=[('is_chambre','=',True)], string="Chambre")
    pavillon_id = fields.Many2one('ksoft.unite.soins', string="Pavillon")
    description = fields.Char(string="Description")
    state = fields.Selection([('free','Libre'),('occup','Occupé'),('reserved','Reservé'),('closed','Fermé')], default="free", string="Etat")
    type_chambre = fields.Selection([('standard','Standard'),('vip','VIP')], default="standard", string="Type de chambre")
    #patient_id
    #Lit
    
    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, "%s - %s" % (rec.pavillon_id.service_name, rec.chambre_id.name))) 
        return result
        
    def reserve_chambre(self):
        print('ok')

class UnitedeSoinsModule(models.Model):

    _name = 'ksoft.unite.soins'
    _description = 'Unité de soins'
    _order = 'id desc'

    service_name = fields.Char(string="Unité de Soins Service")
    service_id = fields.Many2one('ksoft.services', string="Services")
    chambre_ids = fields.One2many('ksoft.chambre', 'pavillon_id', string="Chambre")
    type_unite = fields.Selection([('interne','Interne'),('externe','Externe')], default="interne", string="Type Unité")
    
    _sql_constraints = [
        ('service_names', 'unique (service_name)', 'Cette Unité existe déjà !')

    ]

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, "%s " % (rec.service_name))) 
        return result


class ServiceModule(models.Model):

    _name = 'ksoft.services'
    _description = 'Services'
    _order = 'id desc'

    service_name = fields.Char(string="ID Service")
    service = fields.Char(string='Services', required="True")
    type_rdv = fields.Selection(type_service, required="True", string="Type de service")
    responsable = fields.Many2one('res.users', 'Responsable:', default=lambda self: self.env.user)
    entrepot = fields.Many2one('stock.location', 'Location',
                                domain=[('usage', 'in', ['internal'])], ondelete='cascade')

    unit_soins = fields.Many2many('ksoft.unite.soins', string="Unité des soins")
    medecin = fields.One2many('fertility.doctor', 'service_id', string="Medecin")
    rubrique = fields.One2many('ksoft.rubrique', 'service_id', string="Rubriques")
    type_unite = fields.Selection([('interne','Interne'),('externe','Externe')], default="interne", string="Localisation")
    
    
    _sql_constraints = [
        ('services', 'unique (service)', 'Ce service existe déjà !')

    ]
    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, "%s " % (rec.service))) 
        return result


class RubriqueModule(models.Model):

    _name = 'ksoft.rubrique'
    _description = 'Description les rubriques de l\'hopital'
    
    name = fields.Char(string="Rubrique", required=True)
    code = fields.Char(string="Code")
    service_id = fields.Many2one('ksoft.services', 'Service')
    active = fields.Boolean(
        'Active', default=True,
        help="If unchecked, it will allow you to hide the rubrique without removing it.")


    def unlink(self):
        return super(RubriqueModule, self).unlink()
