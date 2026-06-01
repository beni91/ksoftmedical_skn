# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
import logging

_logger = logging.getLogger(__name__)


class WizardModuleTransfert(models.TransientModel):

    _name = 'module.transfert.patient.wizard'
    _description = 'Wizard Transfert Patient'
    # _order = 'date_prescription desc, id desc'

    date_transfert = fields.Datetime(string='Date_Heure', readonly=True, default=fields.Datetime.now)
    pavillon_dest = fields.Many2one('ksoft.unite.soins', string="Pavillon destination", required=False)
    pavillon_origin = fields.Many2one('ksoft.unite.soins', string="Pavillon Origine", required=False)
    service_id = fields.Many2one('ksoft.services', string="Services")
    pavillon_confirmation = fields.Many2one('ksoft.unite.soins', string="Pavillon destination", required=False)
    note_medecin = fields.Text(string="Instruction", required=False)
    consultation_id = fields.Many2one('fertility.appointment', string="Consultation")
    user_id = fields.Many2one('res.users', string="Transferé par", default=lambda self: self.env.user)
    patient_id = fields.Many2one('fertility.patient', string="Patient")
    status = fields.Selection([
        ('draft', 'En attente'),
        ('conf', 'Confirmé'),
        ('cancel', 'Annulé')], default='draft', string="Etat")
        
    type_transfert = fields.Selection([
        ('interne', 'Interne'),
        ('externe', 'Externe')], default='interne', string="Type de transfert")
        
    def transferer_salle_attente(self):
        appointment_transfert = self.env['module.transfert.patient'].create({
            'patient_id':self.consultation_id.patient_id.id,
            'user_id':self.user_id.id,
            'service_id':self.service_id.id,
            'consultation_id':self.consultation_id.id,
            'note_medecin':self.note_medecin,
            'pavillon_dest':self.pavillon_dest.id,
            'pavillon_origin':self.pavillon_origin.id,
            'date_transfert':self.date_transfert,
            
            })
        if appointment_transfert:
            self.consultation_id.write({'internal_status':'transfered', 'status':'transfered'})
            


