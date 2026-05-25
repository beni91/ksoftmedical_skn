# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
import logging
from datetime import datetime, time

_logger = logging.getLogger(__name__)

class ModuleTransfert2(models.Model):
    """ Gère le transfert entre modules """

    _inherit = 'module.transfert.patient'
    _description = 'Transfert Patient'
    # _order = 'date_prescription desc, id desc'

    date_confirmation = fields.Datetime(string='Date_Heure de confirmation')
    hospi_id = fields.Many2one('module.hospitalisation', string="Hospitalisation")
    user_inf_id = fields.Many2one('res.users', string="Confirmé par")
    medecin_tut = fields.Many2one('fertility.doctor', string='Médecin traitant',
                                  required=False, select=True, help='Médecin traitant')
    
    chambre_ids = fields.Many2one('ksoft.chambre', string="Chambre")
        
    def confirme_transfert(self):
        text = 'normal'
        if self.service_id.type_rdv == 'urg':
            text = 'obser'
        else:
            text = 'normal'
        
        hospi_id = self.env['module.hospitalisation'].create({
            'patient_id': self.patient_id.id,
            #'user_inf_id': self.env.user.id,
            'medecin_tut':self.medecin_tut.id,
            'service_a': self.service_id.id,
            'unite_a': self.pavillon_dest.id,
            'type_hospitalisation':text,
            'raison_admin':self.note_medecin,
            'lit':self.chambre_ids.id,
        })
        
        self.write({'user_inf_id': self.env.user.id, 'date_confirmation':datetime.now(), 'status':'conf'})

# class InheritModuleHospitalisation(models.Model):

    # _inherit = 'module.hospitalisation'
    
    # transfer_ids = fields.One2many('module.transfert.patient', 'consultation_id', string="Transfert")
    # is_tranfert = fields.Boolean(string="Transferé", default=False)
    
    
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
        
    
    

