# -*- coding: utf-8 -*-
#
# Auteur : BKM
# Date   : 11 Avril 22
################################
from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
import logging
_logger = logging.getLogger(__name__)



class DiseaseModule(models.Model):

    _name = 'module.desease'
    _description = 'Pathologie'

    name = fields.Char(string='Pathologie')
    reference = fields.Char(string="Référence")

    _sql_constraints = [
        ('pathologie_uniq', 'unique(name)', 'Cette pathologie est déjà enregistré, verifier la liste des pathologies'),
    ]
    
class PathologieModule(models.Model):
    """ Gestion des Pathologies"""

    _name = 'module.diagnostics'
    _description = 'Diagnostics'
    _order = 'date_diagnostic desc'

    diag_name = fields.Char(string="ID Diagnostics")
    patient_id = fields.Many2one('fertility.patient', string='Patient')
    nompatient = fields.Char(related='patient_id.nom', string="Nom")
    pnompatient = fields.Char(related='patient_id.postnom', string="Postnom")
    prnompatient = fields.Char(related='patient_id.prenom', string="Prenom")
    dob = fields.Date(related='patient_id.birth', string='Date Naiss', readonly=True, )
    sex = fields.Selection([('m', 'Masculin'), ('f', 'Féminin')], string='Sexe', readonly=True)
    age = fields.Integer(related='patient_id.age', string='Age', readonly=True)
    date_diagnostic = fields.Datetime(string='Date', readonly=True, default=fields.Date.today)
    medecin = fields.Many2one('fertility.doctor', readonly=True, string="Médecin")
    medecin_diag = fields.Many2one('res.users', readonly=True, string="Médecin")
    internal_status = fields.Selection([('hypo', 'Hypothèse'), ('def', 'Définitive')],
                                      default='hypo', string='Diagnostics')
    origine = fields.Selection([('homme', 'Masculine'), ('femme', 'Feminine'), ('mixte', 'Mixte')],
                                      string="Origine")
    description = fields.Char(string="Autres Pathologies")
    explication = fields.Text(string="Description")
    pathologie = fields.Many2one('module.desease', string="Pathologie")

    #@api.model
    #def create(self, vals):
    #    obj_doctors = self.env['fertility.doctor'].search([('user_id', '=', self.env.uid)])
    #    if obj_doctors is not None:
    #        for doctor in obj_doctors:
    #            vals['medecin'] = doctor.id
        #self.medecin_diag=self.env.user

     #   return super(PathologieModule, self).create(vals)

    #@api.model
    #def write(self, vals):
    #   return super(PrescriptionModule, self).write(vals)

    #def unlink(self):
    #    return super(PrescriptionModule, self).unlink()

    @api.model
    def default_get(self, fields):
        res = super(PathologieModule, self).default_get(fields)
        res['medecin_diag'] = self.env.user.id
        return res

class ChirurgieModule(models.Model):
    """ Gestion des Pathologies"""

    _name = 'module.chirurgie'
    _description = 'Chirurgie'
    #_order = 'date_diagnostic desc'

    date_chirurgie = fields.Date(string='Date', readonly=True, default=fields.Date.today())
    medecin = fields.Many2one('res.users', readonly=True, string="Médecin")
    protocole = fields.Html(string="Protocole")
    appointment_id = fields.Many2one('fertility.appointment', string="Appointment")
    product = fields.Many2one('product.template', string="Actes")
    internal_status = fields.Selection(
        [('draft', 'En attente'), ('invoicing', 'Facturation'), ('protocol', 'Saisie de protocole'),
         ('ongoing', 'Validation'), ('done', 'Fait')], 'Etat', default='draft')
    @api.model
    def default_get(self, fields):
        res = super(ChirurgieModule, self).default_get(fields)
        res['medecin'] = self.env.user.id
        return res