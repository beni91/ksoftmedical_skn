# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
import logging

_logger = logging.getLogger(__name__)

class ModuleTransfert(models.Model):
    """ Gère le transfert entre modules """

    _name = 'module.transfert.patient'
    _description = 'Transfert Patient'
    # _order = 'date_prescription desc, id desc'

    date_transfert = fields.Datetime(string='Date_Heure', readonly=True, default=fields.Datetime.now)
    pavillon_dest = fields.Many2one('ksoft.unite.soins', string="Pavillon destination", required=False)
    service_id = fields.Many2one('ksoft.services', string="Services")
    pavillon_origin = fields.Many2one('ksoft.unite.soins', string="Pavillon Origine", required=False)
    note_medecin = fields.Text(string="Instruction", required=False)
    consultation_id = fields.Many2one('fertility.appointment', string="Consultation")
    user_id = fields.Many2one('res.users', string="Transferé par")
    patient_id = fields.Many2one('fertility.patient', string="Patient")
    status = fields.Selection([
        ('draft', 'En attente'),
        ('conf', 'Confirmé'),
        ('cancel', 'Annulé')], default='draft', string="Etat")
    
    type_transfert = fields.Selection([
        ('interne', 'Interne'),
        ('externe', 'Externe')], default='interne', string="Type de transfert")
        
    def transferer_salle_attente(self):
        print("ok")


class InheritModuleConsultation(models.Model):

    _inherit = 'fertility.appointment'
    
    transfer_ids = fields.One2many('module.transfert.patient', 'consultation_id', string="Transfert")
    is_tranfert = fields.Boolean(string="Transferé", default=False)
    
    
    # def action_transfert_patient(self):
        # action = self.env.ref('ksoftmedical.action_transfert_patient').read()[0]
        # #action.update({'context':{'default_patient_id': self.patient_id}})
        # return action
        
    # def action_transfert_patient2(self):
        
        # #try:
        # form_view_id = self.env.ref("ksoftmedical.view_transfert_patient_form").id

        # #except Exception as e:
        # #    form_view_id = False
            
        # #    logger.info("****##########skdjsk %s", form_view_id)
            
        # #raise Exception(_(form_view_id))
        # return {
            # 'name': 'Transfert Patient',
            # 'view_type': 'form',
            # 'view_mode': 'form',
            # 'res_model': 'module.transfert.patient',
            # 'views': [(form_view_id, 'form')],
            # 'res_id': self.id,
            # 'type': 'ir.actions.act_window',
            # 'target': 'new',
        # }
        
    
    

