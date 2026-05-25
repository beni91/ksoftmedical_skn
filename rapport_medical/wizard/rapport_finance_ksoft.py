# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import logging
from datetime import datetime, date, timedelta
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)


class WizardRapportFinancier(models.TransientModel):
    """ Permet de l'impression du rapport de caisse. """

    _inherit = 'account.cash.report'
    _description = 'Rapport de caisse'

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
        
    def get_final_detail_prive(self):
        # combine search condition
        search_conditions = []
        cont = ""
        '''
            Le model account.move enregistre à la fois les entrées de caisse et le facture et le champs move_type permet de faire cette difference
            move_type = entry pour les entrées de caisse
            move_type = out_invoice pour les factures clients
            Les liens entre le 2 est fait par le champs "ref" pour les entrées de caisse et le champs "name" pour les factures qui indiquent le num
            de la facture pour le move_type=out_invoice et la ref facture pour le move_type=entry

            ** Il suffira de comparer le 2 champs
        '''
        
        query1 = """
                    SELECT DISTINCT libelle FROM account_move 
                    WHERE invoice_date BETWEEN '%s' AND '%s' AND payment_state IN ('partial','paid')
                    AND journal_id=%s AND categorie in ('prive', 'prive2', 'vip', 'social') ORDER BY libelle asc;

                """ % (self.start_date, self.end_date, self.journal.id)
        #self.env.cr.execute(query, {tuple(self.start_date),tuple(self.end_date),tuple(self.journal_payement.id)})
        self.env.cr.execute(query1)
        res1 = self.env.cr.fetchall()
        
        if self.start_date <= self.end_date:
            tmontant_generale = 0.0
            tmontant_dette = 0.0
            for y in res1:
         
                if (self.journal_payement and self.journal):
                
                    query = """
                        SELECT factures.invoice_date as D_facturation, paiement.date as D_Paiement, factures.NN as N_Facture, factures.invoice_partner_display_name as Patient, 
                        factures.amount_total_signed as M_total, paiement.amount_total_signed as M_Payé, factures.amount_residual_signed as M_Restant, 
                        factures.payment_state as Etat, factures.libelle as Libelle
                        FROM account_move as paiement 
                        INNER JOIN (SELECT moves2.categorie as categ, moves2.service_id2 as t, moves2.id, moves2.name as NN, moves2.date, moves2.ref, moves2.state,
                                moves2.move_type, moves2.journal_id, moves2.partner_id, moves2.payment_reference, moves2.payment_id, moves2.amount_total_signed, 
                                moves2.amount_residual_signed, moves2.invoice_date,moves2.invoice_partner_display_name, moves2.payment_state,moves2.libelle 
                                FROM account_move as moves2) as factures 
                        ON paiement.ref=factures.NN AND paiement.date BETWEEN '%s' AND '%s' AND factures.payment_state IN ('paid', 'partial') 
                        AND paiement.journal_id=%s and factures.categ in ('prive', 'prive2', 'vip', 'social') AND factures.libelle ='%s' order by factures.libelle asc;

                    """ % (self.start_date, self.end_date, self.journal_payement.id, y[0])
                    #self.env.cr.execute(query, {tuple(self.start_date),tuple(self.end_date),tuple(self.journal_payement.id)})
                    self.env.cr.execute(query)
                    res = self.env.cr.fetchall()
                    
                    

                    cont += "<h3 style='text-align:center;'></h3>"
                    cont += "</br></br>"
                    cont += "<table border=1 class='table table-sm o_main_table' width=100% >" 
                    cont += "<tr>"
                    cont += "<th style='text-align:center;background:#cccccc;color:#000000' colspan='8'><h5>"+ y[0].upper() +"</h5></th>"
                    cont += "</tr>"
                    
                    cont += "<tr>"
                    cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>DATE FAC.</th>"
                    cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>DATE PAIEMENT.</th>"
                    cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>N° FACTURE</th>"
                    cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>NOM PATIENT</th>"
                    cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>M. TOTAL</th>"
                    cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>M. PAYE</th>"
                    cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>M. Dû</th>"
                    cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>ETAT</th>"
                    #cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>LIBELLE</th>"
                    cont += "</tr>"

                    tmontant_attendu = 0.0
                    tmontant_percu = 0.0
                    tmontant_restant = 0.0
                    
                    for x in res:

                        cont += "<tbody>"
                        cont += "<tr>"
                        cont += "<td>"+str(x[0]) +"</td>"
                        cont += "<td style='text-align:center;'>"+str(x[1]) +"</td>"
                        cont += "<td style='text-align:center;'>"+str(x[2])+"</td>"
                        cont += "<td style='text-align:left;'>"+str(x[3].upper()) +"</td>"
                        cont += "<td style='text-align:right;'>"+'{:.2f}'.format(float(x[4])) +"</td>"
                        cont += "<td style='text-align:right;'>"+'{:.2f}'.format(float(x[5])) +"</td>"
                        cont += "<td style='text-align:right;'>"+'{:.2f}'.format(float(x[6])) +"</td>"
                        cont += "<td style='text-align:center;'>"+str(x[7]) +"</td>"
                        #cont += "<td style='text-align:center;'>"+str(x[8].upper()) +"</td>"
                        #cont += "<td style='text-align:center;'>"+str(x[9]) +"</td>"
                        cont += "</tr>"
                        cont += "</tbody>"
                        
                        tmontant_attendu += x[4]
                        tmontant_percu += (float(x[5]))
                        tmontant_restant += x[6]
                        
                    cont += "<tfooter>"
                    cont += "<tr>"
                    cont += "<td colspan='4' style='text-align:right;'><b>S/TOTAL.</b></td>"
                    cont += "<td style='text-align:right;background:#27AE60 ;color:#ffffff'><b>"+'{:.2f}'.format(float(tmontant_attendu)) +"</b></td>"
                    cont += "<td style='text-align:right;background:#27AE60 ;color:#ffffff'><b>"+'{:.2f}'.format(float(tmontant_percu))+"</b></td>"
                    cont += "<td style='text-align:right;background:#27AE60 ;color:#ffffff'><b>"+'{:.2f}'.format(float(tmontant_restant)) +"</b></td>"
                    cont += "<td><b></b></td>"
                    cont += "</tr>"
                    cont += "</tfooter>"
                        
                    cont += "</table>"
                    tmontant_generale += float(tmontant_percu)
                    tmontant_dette += float(tmontant_restant)
            cont += "<table border=1 class='table table-sm o_main_table' width=100% >" 
            cont += "<tr>"
            cont += "<td colspan='7' style='text-align:right;'><h5><b>TOTAL GENERAL.</b></h5></td>"
            cont += "<td style='text-align:right;background:#27AE60 ;color:#ffffff'><h5><b>"+'{:.2f}'.format(float(tmontant_generale)) +"</b></h5></td>"
            cont += "</tr>"
            cont += "<tr>"
            cont += "<td colspan='7' style='text-align:right;'><h5><b>TOTAL  DETTE.</b></h5></td>"
            cont += "<td style='text-align:right;background:#27AE60 ;color:#ffffff'><h5><b>"+'{:.2f}'.format(float(tmontant_dette)) +"</b></h5></td>"
            cont += "</tr>"
            cont += "</table>"
            
            self.write({'contenu':cont})
            
        else:
            raise UserError(_("La date de debut de la période ne peut être supérieur à la date de fin de la période"))
    
            
    def get_final_detail_convention(self):
        # combine search condition
        search_conditions = []
        cont = ""
        '''
            Le model account.move enregistre à la fois les entrées de caisse et le facture et le champs move_type permet de faire cette difference
            move_type = entry pour les entrées de caisse
            move_type = out_invoice pour les factures clients
            Les liens entre le 2 est fait par le champs "ref" pour les entrées de caisse et le champs "name" pour les factures qui indiquent le num
            de la facture pour le move_type=out_invoice et la ref facture pour le move_type=entry

            ** Il suffira de comparer le 2 champs
        '''
        
        query1 = """
                    SELECT DISTINCT libelle FROM account_move 
                    WHERE invoice_date BETWEEN '%s' AND '%s' AND payment_state IN ('not_paid','paid', 'partial') AND state IN ('posted')
                    AND convention_id=%s AND categorie in ('convention') ORDER BY libelle asc;

                """ % (self.start_date, self.end_date, self.convention.id)
        #self.env.cr.execute(query, {tuple(self.start_date),tuple(self.end_date),tuple(self.journal_payement.id)})
        self.env.cr.execute(query1)
        res1 = self.env.cr.fetchall()
        
        if self.start_date <= self.end_date:
            tmontant_generale = 0.0
            for y in res1:
         
                if (self.convention):
                
                    query = """
                        SELECT factures.invoice_date as D_facturation, factures.name as N_Facture, factures.invoice_partner_display_name as Patient, 
                        factures.matricule as Matricule,factures.numero_billet as N_Billet, factures.amount_total_signed as M_total, 
                        factures.payment_state as Etat, factures.libelle as Libelle
                        FROM account_move as factures 
                        WHERE factures.invoice_date BETWEEN '%s' AND '%s' AND factures.state = 'posted' 
                        AND factures.convention_id=%s AND factures.payment_state IN ('not_paid','paid', 'partial') AND factures.libelle ='%s'
                        ORDER BY factures.libelle, factures.partner_id;

                    """ % (self.start_date, self.end_date, self.convention.id, y[0])
                    #self.env.cr.execute(query, {tuple(self.start_date),tuple(self.end_date),tuple(self.journal_payement.id)})
                    self.env.cr.execute(query)
                    res = self.env.cr.fetchall()
                    
                    

                    cont += "<h3 style='text-align:center;'></h3>"
                    cont += "</br></br>"
                    cont += "<table border=1 class='table table-sm o_main_table' width=100% >" 
                    cont += "<tr>"
                    cont += "<th style='text-align:center;background:#cccccc;color:#000000' colspan='7'><h5>"+ y[0].upper() +"</h5></th>"
                    cont += "</tr>"
                    
                    cont += "<tr>"
                    cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>DATE FAC.</th>"
                    cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>N° FACTURE</th>"
                    cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>NOM PATIENT</th>"
                    cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>MATRICULE</th>"
                    cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>N° BILLET</th>"
                    cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>M. A PAYER</th>"
                    cont += "</tr>"

                    tmontant_attendu = 0.0
                    tmontant_percu = 0.0
                    tmontant_restant = 0.0
                    
                    for x in res:

                        cont += "<tbody>"
                        cont += "<tr>"
                        cont += "<td>"+str(x[0]) +"</td>"
                        cont += "<td style='text-align:center;'>"+str(x[1])+"</td>"
                        cont += "<td style='text-align:left;'>"+str(x[2].upper()) +"</td>"
                        cont += "<td style='text-align:center;'>"+str(x[3]) +"</td>"
                        cont += "<td style='text-align:center;'>"+str(x[4]) +"</td>"
                        cont += "<td style='text-align:right;'>"+ '{:,}'.format(float(x[5])) +"</td>"
                        #cont += "<td style='text-align:center;'>"+str(x[7].upper()) +"</td>"
                        cont += "</tr>"
                        cont += "</tbody>"
                        
                        #tmontant_attendu += x[4]
                        tmontant_percu += (float(x[5]))
                        #tmontant_restant += x[6]
                        
                    cont += "<tfooter>"
                    cont += "<tr>"
                    cont += "<td colspan='5' style='text-align:right;'><b>S/TOTAL.</b></td>"
                    cont += "<td style='text-align:right;background:#27AE60 ;color:#ffffff'><b>"+'{:.2f}'.format(float(tmontant_percu))+"</b></td>"
                    
                    cont += "</tr>"
                    cont += "</tfooter>"
                        
                    cont += "</table>"
                    tmontant_generale += float(tmontant_percu)
            
            cont += "<table border=1 class='table table-sm o_main_table' width=100% >" 
            cont += "<tr>"
            cont += "<td colspan='5' style='text-align:right;'><h4><b>TOTAL GENERAL.</b></h4></td>"
            cont += "<td style='text-align:right;background:#27AE60 ;color:#ffffff'><h4><b>"+'{:.2f}'.format(float(tmontant_generale)) +"</b></h4></td>"
            cont += "</tr>"
            cont += "</table>"
            
            self.write({'contenu':cont})
            
        else:
            raise UserError(_("La date de debut de la période ne peut être supérieur à la date de fin de la période"))
    
            
            
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