# -*- coding: utf-8 -*-

from odoo import models, fields
import logging
_logger = logging.getLogger(__name__)

class WizardAppointment(models.TransientModel):
    """Wizard pour creation des rdvs."""

    _name = 'fertility.wizard.appointment'
    _description = 'Wizard Appointment'

    patient_id = fields.Many2one('fertility.patient','Patient',required=True)
    doctor_id = fields.Many2one('fertility.doctor', 'Médecin',required=True)
    product_id = fields.Many2one('product.template', string='Type de Consultation', required=True)
    appointment_type = fields.Many2one('fertility.appointment.type', required=True)
    category_id = fields.Many2one('product.category',related='appointment_type.category_id')

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
        # id = self.sudo().config_id.write({'appointment_ids':[(0,0,{
        #   'patient_id':self.patient_id.id,
        #   'operation_ids': self.config_id.step_ids.mapped(lambda step : (0,0,{
        #       'sequence' : step.sequence,
        #       'operation_config_id': step.operation_id.id,
        #       # 'account_move': step.operation_id.account_move.id if step.operation_id.billable else '',
        #       'param_ids' : step.operation_id.param_ids.mapped(lambda param_id : (0,0,{'param_id':param_id.id}))
        #   }))
        # })]})
        # _logger.info("{} - {}".format('action_create','called'))


class WizardLabo(models.TransientModel):
    """Wizard pour demande examen laboratoire."""

    _name = 'fertility.wizard.labo'
    _description = 'Wizard Labo'

    appointment_id = fields.Many2one('fertility.appointment')
    pma_id = fields.Many2one('fertility.pma')
    category_id = fields.Many2one('product.category', required=True)
    product_ids = fields.Many2many('product.template', required=True)

    def action_create(self):
        _logger.info(self._context)
        if self.appointment_id :
            product_ids = self.product_ids.mapped(lambda product_id : (0,0,{'analyse':product_id.id}) )
            self.appointment_id.consult_examen_id.write({'labo_ids':product_ids})

        if self.pma_id :
            product_ids = self.product_ids.mapped(lambda product_id : (0,0,{
                'analyse':product_id.id,
                'move_id':self.pma_id.move_id1.id,
                'internal_status':'invoicing',
                'patient_id':self.pma_id.patient_id.id
                }) )
            self.pma_id.consult_examen_id.write({'labo_ids':product_ids})

class WizardImagerie(models.TransientModel):
    """Wizard pour demande examen imagerie."""

    _name = 'fertility.wizard.imagerie'
    _description = 'Wizard Imagerie'

    appointment_id = fields.Many2one('fertility.appointment')
    date_demande = fields.Date(string="Date de demande", default=fields.Datetime.now)
    pma_id = fields.Many2one('fertility.pma')
    category_id = fields.Many2one('product.category', required=True, string="Catégorie")
    product_ids = fields.Many2many('product.template', required=True, string="Analyses Imageries")
    product_labo_ids = fields.Many2many('product.template', 'product_labo_rel', 'product_id', 'labo_id',
          required=True, string="Analyses Laboratoires")

    def action_create(self):
        _logger.info(self._context)     
        if self.appointment_id :
            if self.product_ids:
                product_ids = self.product_ids.mapped(lambda product_id : (0,0,{'analyse':product_id.id}) )
                self.appointment_id.consult_examen_id.write({'imagerie_ids':product_ids})
            if self.product_labo_ids:
                product_labo_ids = self.product_labo_ids.mapped(lambda product_id : (0,0,{'analyse':product_id.id}) )
                self.appointment_id.consult_examen_id.write({'labo_ids':product_labo_ids})

        if self.pma_id :
            product_ids = self.product_ids.mapped(lambda product_id : (0,0,{
                'analyse':product_id.id,
                'move_id':self.pma_id.move_id1.id,
                'internal_status':'invoicing',
                'patient_id':self.pma_id.patient_id.id
                }) )
            self.pma_id.consult_examen_id.write({'imagerie_ids':product_ids})

class WizardMvtAdministratifPatent(models.TransientModel):
    """Wizard pour changer la convention ou la catégorie d'un patient"""

    _name = 'ksfot.patient.wizard.mvtadministrif'

    datemodif = fields.Date(string="Date de modification")
    actuel = fields.Boolean(string="Situation actuel", default=False)
    categorie = fields.Selection([('prive','Privé'),('convention','Abonné')], string="Catégorie", required=True)
    classe = fields.Selection([('agent','Agent'),('epoux','Epoux(se)'),('enf','Enfants')], string="Classe")
    matricule = fields.Char(string="Matricule")
    convention = fields.Many2one('res.partner', domain="[('is_company', '=', True)]")
    user_id = fields.Many2one('res.users', string='Modifié par')
    patient_id = fields.Many2one('fertility.patient', string='Patient',required=True)

    def action_create(self):
        patient = self.env['ksfot.patient.mvtadministrif'].create({
            'datemodif':fields.Date.today(),
            'actuel': True,
            'categorie':self.categorie,
            'classe':self.classe,
            'matricule':self.matricule,
            'convention':self.convention.id,
            'user_id':self.env.uid,
            })
        return True
        

class WizardResultatLabo(models.TransientModel):
    """Permet de l'impression de resultat labo."""

    _name = 'fertility.wizard.result.labo'
    _description = 'Wizard Resultat Labo'

    patient_id = fields.Many2one('fertility.patient')
    birth = fields.Date(related='patient_id.birth', string="Date de naissance")
    age = fields.Integer(related='patient_id.age', string="Age")
    gender = fields.Selection([('M','Masculin'),('F','Féminin')], 'Genre', related='patient_id.gender')
    start_date = fields.Date(string="Debut")
    end_date = fields.Date(string="Fin")

    def labo_print_results(self):
        # combine search condition
        search_conditions = []
        if (self.patient_id):
            search_conditions += [('patient_id','=',self.patient_id.id)]
        if (self.start_date):
            search_conditions += [('date_request', '>=', self.start_date)]
        if (self.end_date):
            search_conditions += [('date_request', '<=', self.end_date)]

        labo_data = self.env['fertility.examen.labo'].search_read(search_conditions)
        # pass data to view
        data = {
            'form_data': self.read()[0],
            'labo_data': labo_data
        }
        # call report action
        # this action is get from report/calendar_report.xml
        # .with_context(landscape=True) is to make the pdf to become horizontal, if landscape=False, pdf will become vertical
        report_action = self.env.ref('fertility.action_report_laboratoire').with_context(landscape=True).report_action(self, data=data)

        return report_action

    def labo_print_results_xlsx(self):
        # combine search condition
        search_conditions = []
        if (self.patient_id):
            search_conditions += [('patient_id','=',self.patient_id.id)]
        if (self.start_date):
            search_conditions += [('date_request', '>=', self.start_date)]
        if (self.end_date):
            search_conditions += [('date_request', '<=', self.end_date)]

        labo_data = self.env['fertility.examen.labo'].search_read(search_conditions)
        # pass data to view
        data = {
            'form_data': self.read()[0],
            'labo_data': labo_data
        }
        # call report action
        # this action is get from report/calendar_report.xml
        # .with_context(landscape=True) is to make the pdf to become horizontal, if landscape=False, pdf will become vertical
        report_action = self.env.ref('fertility.action_report_laboratoire').with_context(landscape=True).report_action(self, data=data)

        return report_action
