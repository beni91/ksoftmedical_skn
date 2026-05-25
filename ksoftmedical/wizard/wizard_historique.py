# -*- coding: utf-8 -*-

from odoo import models, fields
import logging
_logger = logging.getLogger(__name__)

class WizardHistoriquePatient(models.TransientModel):
    """Resumé du dossier patient."""

    _name = 'patient.dossier.historique'
    _description = 'Historique dossier patient'

    patient_id = fields.Many2one('fertility.patient','Patient',required=True)
    historique = fields.Html(string="Historique")
    # doctor_id = fields.Many2one('fertility.doctor', 'Médecin',required=True)
    # product_id = fields.Many2one('product.template', string='Type de Consultation', required=True)
    # appointment_type = fields.Many2one('fertility.appointment.type', required=True)
    # category_id = fields.Many2one('product.category',related='appointment_type.category_id')
    def action_create(self):
        appointment = self.env['fertility.appointment'].create({
            'patient_id':self.patient_id.id,
            'doctor_id':self.doctor_id.id,
            'appointment_type':self.appointment_type.id,
            'product_id':self.product_id.id
            })
        return {
            'name': "Rendez-vous",
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'fertility.appointment',
            'res_id': appointment.id,
            }
            
    def action_create(self):
        appointment = self.env['fertility.appointment'].create({
            'patient_id':self.patient_id.id,
            'doctor_id':self.doctor_id.id,
            'appointment_type':self.appointment_type.id,
            'product_id':self.product_id.id
            })
        return {
            'name': "Rendez-vous",
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'fertility.appointment',
            'res_id': appointment.id,
            }

# class WizardLabo(models.TransientModel):
#     """Base Synchronization."""

#     _name = 'fertility.wizard.labo'
#     _description = 'Wizard Labo'

#     appointment_id = fields.Many2one('fertility.appointment')
#     pma_id = fields.Many2one('fertility.pma')
#     category_id = fields.Many2one('product.category', required=True)
#     product_ids = fields.Many2many('product.template', required=True)

#     def action_create(self):
#         _logger.info(self._context)
#         if self.appointment_id :
#             product_ids = self.product_ids.mapped(lambda product_id : (0,0,{'analyse':product_id.id}) )
#             self.appointment_id.consult_examen_id.write({'labo_ids':product_ids})

#         if self.pma_id :
#             product_ids = self.product_ids.mapped(lambda product_id : (0,0,{
#                 'analyse':product_id.id,
#                 'move_id':self.pma_id.move_id1.id,
#                 'internal_status':'invoicing',
#                 'patient_id':self.pma_id.patient_id.id
#                 }) )
#             self.pma_id.consult_examen_id.write({'labo_ids':product_ids})

# class WizardImagerie(models.TransientModel):
#     """Base Synchronization."""

#     _name = 'fertility.wizard.imagerie'
#     _description = 'Wizard Imagerie'

#     appointment_id = fields.Many2one('fertility.appointment')
#     pma_id = fields.Many2one('fertility.pma')
#     category_id = fields.Many2one('product.category', required=True)
#     product_ids = fields.Many2many('product.template', required=True)

#     def action_create(self):
#         _logger.info(self._context)     
#         if self.appointment_id :
#             product_ids = self.product_ids.mapped(lambda product_id : (0,0,{'analyse':product_id.id}) )
#             self.appointment_id.consult_examen_id.write({'imagerie_ids':product_ids})

#         if self.pma_id :
#             product_ids = self.product_ids.mapped(lambda product_id : (0,0,{
#                 'analyse':product_id.id,
#                 'move_id':self.pma_id.move_id1.id,
#                 'internal_status':'invoicing',
#                 'patient_id':self.pma_id.patient_id.id
#                 }) )
#             self.pma_id.consult_examen_id.write({'imagerie_ids':product_ids})


# class WizardResultatLabo(models.TransientModel):
#     """Permet de l'impression de resultat labo."""

#     _name = 'fertility.wizard.result.labo'
#     _description = 'Wizard Resultat Labo'

#     patient_id = fields.Many2one('fertility.patient')
#     birth = fields.Date(related='patient_id.birth', string="Date de naissance")
#     age = fields.Integer(related='patient_id.age', string="Age")
#     gender = fields.Selection([('M','Masculin'),('F','Féminin')], 'Genre', related='patient_id.gender')
#     start_date = fields.Date(string="Debut")
#     end_date = fields.Date(string="Fin")

#     def labo_print_results(self):
#         # combine search condition
#         search_conditions = []
#         if (self.patient_id):
#             search_conditions += [('patient_id','=',self.patient_id.id)]
#         if (self.start_date):
#             search_conditions += [('date_request', '>=', self.start_date)]
#         if (self.end_date):
#             search_conditions += [('date_request', '<=', self.end_date)]

#         labo_data = self.env['fertility.examen.labo'].search_read(search_conditions)
#         # pass data to view
#         data = {
#             'form_data': self.read()[0],
#             'labo_data': labo_data
#         }
#         # call report action
#         # this action is get from report/calendar_report.xml
#         # .with_context(landscape=True) is to make the pdf to become horizontal, if landscape=False, pdf will become vertical
#         report_action = self.env.ref('fertility.action_report_laboratoire').with_context(landscape=True).report_action(self, data=data)

#         return report_action

#     def labo_print_results_xlsx(self):
#         # combine search condition
#         search_conditions = []
#         if (self.patient_id):
#             search_conditions += [('patient_id','=',self.patient_id.id)]
#         if (self.start_date):
#             search_conditions += [('date_request', '>=', self.start_date)]
#         if (self.end_date):
#             search_conditions += [('date_request', '<=', self.end_date)]

#         labo_data = self.env['fertility.examen.labo'].search_read(search_conditions)
#         # pass data to view
#         data = {
#             'form_data': self.read()[0],
#             'labo_data': labo_data
#         }
#         # call report action
#         # this action is get from report/calendar_report.xml
#         # .with_context(landscape=True) is to make the pdf to become horizontal, if landscape=False, pdf will become vertical
#         report_action = self.env.ref('fertility.action_report_laboratoire').with_context(landscape=True).report_action(self, data=data)

#         return report_action
