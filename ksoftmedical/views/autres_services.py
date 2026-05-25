# -*- coding: utf-8 -*-
#
# Auteur : BKM
# Date   : 11 Avril 22
################################
from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
import logging
_logger = logging.getLogger(__name__)



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
    orientation = fields.Char(string='Orientation')
    description = fields.Html(string="Clinique")
   

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


