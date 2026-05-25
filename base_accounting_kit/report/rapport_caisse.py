# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import logging
from datetime import datetime, date, timedelta
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)


class WizardRapportCaisse(models.TransientModel):
    """ Permet de l'impression du rapport de caisse. """

    _name = 'account.cash.report'
    _description = 'Rapport de caisse'

    start_date = fields.Date(string="Debut", required=True)
    end_date = fields.Date(string="Fin", required=False)
    end_date_pharma = fields.Date(string="Fin", store=True, readonly=False)
    journal = fields.Many2one('account.journal', string="Journal", required=False)
    categorie = fields.Selection([('prive', 'Privé'), ('convention', 'Abonné')], string="Catégorie")
    journal_payement = fields.Many2one('account.journal', string="Paiement")
    
    code_jour = fields.Many2one('account.journal.code', string="Code Jour")
    convention = fields.Many2one('res.partner', string="Convention")
    
    convention_ids = fields.Many2many('res.partner', string="Convention")

    #journal_payement_ = fields.Many2one('account.payment.register', string="Paiement")
    #patient = fields.Many2one('res.partner', string="Patient", required=True)
    
    # @api.onchange('code_jour')
    # def get_info_code_jour(self):
        #combine search condition
        # if self.code_jour:
            # self.start_date = self.code_jour.date_ouverture
            # self.end_date = self.code_jour.date_fermeture
        
        
    @api.onchange('start_date')
    def _set_fermeture_date(self):
        if self.start_date:
            self.end_date_pharma = self.start_date + timedelta(days=1)
            
            
    def change_society_to_person(self):
        for item_ids in self:
            for item in item_ids.convention_ids:
                if item.is_company and item.company_type:
                    self.env['res.partner'].browse(item.id).write({'company_type': 'person', 'is_company':False})
        
        
        
    def pharma_private_report_print(self):
        # combine search condition
        search_conditions = []
        company = False
        start = False
        end = False

        '''
            Le model account.move enregistre à la fois les entrées de caisse et le facture et le champs move_type permet de faire cette difference
            move_type = entry pour les entrées de caisse
            move_type = out_invoice pour les factures clients
            Les liens entre le 2 est fait par le champs "ref" pour les entrées de caisse et le champs "name" pour les factures qui indiquent le num
            de la facture pour le move_type=out_invoice et la ref facture pour le move_type=entry

            ** Il suffira de comparer le 2 champs
        '''
        if (self.code_jour):

            ### Recuperer les company qui ont été facturées
            
            query1 = """
                select line.invoice_date AS Date, line.name AS N_Facture, partner.display_name AS NOM_POSTNOM, (line.amount_total-line.amount_residual_signed) AS M_FACTURE from account_move as line
                inner join res_partner as partner on line.partner_id = partner.id and partner.parent_id is null
                AND line.code_jour = '%s' AND line.state ='posted';
            """ % (self.code_jour.code_jour)
            
            
            #raise UserError(_((query1)))
            self.env.cr.execute(query1)
            res = self.env.cr.fetchall()
           
        # # pass data to view 
        data = {
            'form_data': self.read()[0],
            'reporting_data': res,
            #'company_data': res1,
            #'docs':docs,
            #'details_data': liste,
        }
        # call report action
        # this action is get from report/calendar_report.xml
        # .with_context(landscape=True) is to make the pdf to become horizontal, if landscape=False, pdf will become vertical
        report_action = self.env.ref('ksoftmedical.action_prives_report_compta').with_context(landscape=False).report_action(self, data=data)

        return report_action
    
    def compta_convention_report_print(self):
        # combine search condition
        search_conditions = []
        company = False
        start = False
        end = False

        if (self.code_jour and self.convention):

            ### Recuperer les company qui ont été facturées
            
            query = """
                select line.invoice_date AS Date, line.name AS N_Facture, partner.display_name AS NOM_POSTNOM, (line.amount_total-line.amount_residual_signed) AS M_FACTURE from account_move as line
                inner join res_partner as partner on line.partner_id = partner.id and partner.parent_id = '%s'
                AND line.code_jour = '%s' AND line.state ='posted';
            """ % (self.convention.id, self.code_jour.code_jour)
            
            
            #raise UserError(_((query1)))
            self.env.cr.execute(query)
            res = self.env.cr.fetchall()
           
        # # pass data to view 
        data = {
            'form_data': self.read()[0],
            'reporting_data': res,
            #'company_data': res1,
            #'docs':docs,
            #'details_data': liste,
        }
        # call report action
        # this action is get from report/calendar_report.xml
        # .with_context(landscape=True) is to make the pdf to become horizontal, if landscape=False, pdf will become vertical
        report_action = self.env.ref('ksoftmedical.action_convention_report_compta').with_context(landscape=False).report_action(self, data=data)

        return report_action
    
    def dailybook_print(self):
        # combine search condition
        search_conditions = []

        '''
            Le model account.move enregistre à la fois les entrées de caisse et le facture et le champs move_type permet de faire cette difference
            move_type = entry pour les entrées de caisse
            move_type = out_invoice pour les factures clients
            Les liens entre le 2 est fait par le champs "ref" pour les entrées de caisse et le champs "name" pour les factures qui indiquent le num
            de la facture pour le move_type=out_invoice et la ref facture pour le move_type=entry

            ** Il suffira de comparer le 2 champs
        '''
        if (self.journal_payement and self.journal):

            query = """
                SELECT moves3.invoice_date as D_facturation, moves1.date as D_Paiement, moves3.NN as N_Facture, moves1.move_type, moves3.move_type, moves3.invoice_partner_display_name as Patient, moves1.invoice_partner_display_name, moves1.journal_id as J_Paiement, moves3.amount_total as M_total, moves1.amount_total as M_Payé, moves3.amount_residual as M_Restant, 
                moves3.journal_id, moves3.payment_state as Etat FROM account_move as moves1 
                INNER JOIN (SELECT moves2.id, moves2.name as NN, moves2.date, moves2.ref, moves2.state, moves2.move_type, moves2.journal_id, moves2.partner_id, moves2.payment_reference, moves2.payment_id, moves2.amount_total, moves2.amount_residual, moves2.invoice_date,moves2.invoice_partner_display_name, moves2.payment_state FROM account_move as moves2) as moves3  
                ON moves1.ref=moves3.NN AND moves1.date BETWEEN '%s' AND '%s' AND moves3.payment_state IN ('paid', 'partial') AND moves1.journal_id=%s

            """ % (self.start_date, self.end_date, self.journal_payement.id)
            #self.env.cr.execute(query, {tuple(self.start_date),tuple(self.end_date),tuple(self.journal_payement.id)})
            self.env.cr.execute(query)
            res = self.env.cr.fetchall()

        # pass data to view
        data = {
            'form_data': self.read()[0],
            'reporting_data': res
        }
        # call report action
        # this action is get from report/calendar_report.xml
        # .with_context(landscape=True) is to make the pdf to become horizontal, if landscape=False, pdf will become vertical
        report_action = self.env.ref('base_accounting_kit.action_report_caisse').with_context(landscape=True).report_action(self, data=data)

        return report_action

        #raise UserError(_(reporting_data))

    def dailybook_patient_print(self):
        # combine search condition
        search_conditions = []

        if (self.journal):
            search_conditions += [('journal_id', '=', self.journal.id)]
        if (self.start_date):
            search_conditions += [('invoice_date', '>=', self.start_date)]
        if (self.end_date):
            search_conditions += [('invoice_date', '<=', self.end_date)]

        search_conditions += [('payment_state','in',['in_payment','not_paid','partial', 'apa']),('state','=','posted')]

        reporting_data = self.env['account.move'].search_read(search_conditions)
        # pass data to view
        data = {
            'form_data': self.read()[0],
            'reporting_data': reporting_data
        }
        # call report action
        # this action is get from report/calendar_report.xml
        # .with_context(landscape=True) is to make the pdf to become horizontal, if landscape=False, pdf will become vertical
        report_action = self.env.ref('base_accounting_kit.action_report_dette').with_context(portrait=True).report_action(self, data=data)

        return report_action

#class AccountInvoiceReport(models.Model):
#   """ Pour ajouter le filtre par catégorie """

#   _inherit = 'account.invoice.report'

#   patient_id = fields.Many2one('fertility.patient')
#   categorie = fields.Selection([('prive', 'Privé'), ('convention', 'Abonné')], string="Catégorie", store=True, related='move_id.categorie')