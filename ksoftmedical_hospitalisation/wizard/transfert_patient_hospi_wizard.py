# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
import logging

_logger = logging.getLogger(__name__)


class WizardModuleTransfertHospi(models.TransientModel):

    _inherit = 'module.transfert.patient.wizard'
    _description = 'Wizard Transfert Patient'
    # _order = 'date_prescription desc, id desc'
    
    hospi_id = fields.Many2one('module.hospitalisation', string="Hospitalisation")

        
    def make_out_patient(self):
        for hospi in self:
            if hospi.hospi_id:
                patient = hospi.hospi_id.patient_id
                origine = hospi.hospi_id.unite_a
                    
                if hospi.type_transfert == 'interne': 
                        
                    appointment_transfert = self.env['module.transfert.patient'].create({
                        'patient_id':patient.id,
                        'user_id':self.user_id.id,
                        'service_id':self.service_id.id,
                        'hospi_id':hospi.hospi_id.id,
                        'note_medecin':self.note_medecin,
                        'pavillon_dest':self.pavillon_dest.id,
                        'pavillon_origin':origine.id,
                        'date_transfert':self.date_transfert
                        
                        })
                    
                
                elif hospi.type_transfert == 'externe':
                    appointment_transfert = self.env['module.transfert.patient'].create({
                        'patient_id':patient.id,
                        'user_id':self.user_id.id,
                        'service_id':self.service_id.id,
                        'hospi_id':hospi.hospi_id.id,
                        'note_medecin':self.note_medecin,
                        'pavillon_dest':self.pavillon_dest.id,
                        'pavillon_origin':origine.id,
                        'date_transfert':self.date_transfert,
                        'type_transfert':'externe'
                        })
                    
                if appointment_transfert:
                    hospi.hospi_id.action_sortir()
                



