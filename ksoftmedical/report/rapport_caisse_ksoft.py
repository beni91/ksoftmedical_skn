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

    start_date = fields.Datetime(string="Debut", required=True)
    end_date = fields.Datetime(string="Fin", required=False)
    end_date_pharma = fields.Datetime(string="Fin", store=True, readonly=False)
    journal = fields.Many2one('account.journal', string="Journal", required=False)
    categorie = fields.Selection([('prive', 'Privé'), ('convention', 'Abonné')], string="Catégorie")
    journal_payement = fields.Many2one('account.journal', string="Paiement")
    
    code_jour = fields.Many2one('account.journal.code', string="Code Jour")
    code_jour_ids = fields.Many2many('account.journal.code', string="Codes Jours")
    convention = fields.Many2one('res.partner', string="Convention")
    
    convention_ids = fields.Many2many('res.partner', string="Convention")
    
    type_rapport = fields.Selection([('journalier','Journalier'),('periodique','Périodique')], 
                                        default="journalier", required=True, string="Type de rapport")
                                        
    contenu = fields.Html(string="Contenu")

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
        
    def get_consultation_global_convention(self):
        search_conditions = []
        libelle_list = []
        item_list = []
        name_list = []
        cont = ""
        
        if self.start_date <= self.end_date:
            query = """
                    
                SELECT factures.libelle, sum(factures.amount_total_signed) as M_total, count(factures.partner_id)
                FROM account_move as factures 
                WHERE factures.invoice_date BETWEEN '%s' AND '%s' AND factures.state = 'posted' 
                AND factures.convention_id=%s AND factures.payment_state = 'not_paid' 
                GROUP BY factures.libelle;


            """ % (self.start_date, self.end_date, self.convention.id)
            #self.env.cr.execute(query, {tuple(self.start_date),tuple(self.end_date),tuple(self.journal_payement.id)})
            self.env.cr.execute(query)
            res = self.env.cr.fetchall()
            
            cont += "<h3 style='text-align:center;'>RAPPORT PERIODE DE CONVENTION PAR SERVICE</h3>"
            cont += "</br></br>"
            cont += "<table border=1 class='table table-sm o_main_table' width=100% >" 
            cont += "<tr>"
            cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>SERVICES</th>"
            # cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>M. ATTENDU ($)</th>"
            cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>M. A PAYER ($)</th>"
            cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>Nbre FACT </th>"

            tmontant_attendu = 0.0
            tmontant_percu = 0.0
            tmontant_restant = 0.0
            for x in res:

                cont += "<tbody>"
                cont += "<tr>"
                cont += "<td>"+str(x[0].upper()) +"</td>"
                #cont += "<td style='text-align:center;'>"+str(x[1]) +"</td>"
                cont += "<td style='text-align:center;'>"+'{:,}'.format(x[1])+"</td>"
                cont += "<td style='text-align:left;'>"+str(x[2]) +"</td>"
                cont += "</tr>"
                cont += "</tbody>"
                
                #tmontant_attendu += x[8]
                tmontant_percu += float(x[1])
                #tmontant_restant += x[10]
                
            cont += "<tfooter>"
            cont += "<tr>"
            cont += "<td style='text-align:right;' colspan='2'><b>TOTAL GEN.</b></td>"
            #cont += "<td style='text-align:center;background:#27AE60 ;color:#ffffff'><b>"+str(tmontant_attendu) +"</b></td>"
            cont += "<td style='text-align:center;background:#27AE60 ;color:#ffffff'><b>"+'{:.2f}'.format(float(tmontant_percu))+"</b></td>"
            # cont += "<td style='text-align:center;background:#27AE60 ;color:#ffffff'><b>"+str(tmontant_restant) +"</b></td>"
            #cont += "<td style='text-align:center;background:#27AE60 ;color:#ffffff'><b></b></td>"
            cont += "</tr>"
            cont += "</tfooter>"
                
            cont += "</table>"

            self.write({'contenu':cont})
            
           
        else:
            raise UserError(_("La date de debut de la période ne peut être supérieur à la date de fin de la période"))
 
    def get_consultation_global_prive(self):
        search_conditions = []
        libelle_list = []
        item_list = []
        name_list = []
        cont = ""
        
        if self.start_date <= self.end_date:
            query = """
                    SELECT facture.libelle, sum(facture.amount_total_signed) as M_total, sum(paiement.amount_total_signed) as M_Payé, sum(facture.amount_residual_signed) as M_Restant, count(facture.fact)
                    FROM account_move as paiement 
                    INNER JOIN (SELECT moves2.categorie as categ, moves2.service_id2 as t, moves2.id as fact, moves2.name as NN, moves2.date, moves2.ref, moves2.state, 
                                moves2.move_type, moves2.journal_id, moves2.partner_id, moves2.payment_reference, moves2.payment_id, moves2.amount_total_signed, 
                                moves2.amount_residual_signed, moves2.invoice_date,moves2.invoice_partner_display_name, moves2.payment_state,moves2.libelle 
                    FROM account_move as moves2) as facture  
                    ON paiement.ref=facture.NN AND paiement.date BETWEEN '%s' AND '%s' AND facture.payment_state IN ('paid', 'partial') 
                    AND paiement.journal_id=%s and facture.categ in ('prive', 'prive2', 'vip', 'social')
                    GROUP BY facture.libelle

            """ % (self.start_date, self.end_date, self.journal_payement.id)
            #self.env.cr.execute(query, {tuple(self.start_date),tuple(self.end_date),tuple(self.journal_payement.id)})
            self.env.cr.execute(query)
            res = self.env.cr.fetchall()
            
            #cont += "<h3 style='text-align:center;'>RAPPORT DES CONSULTATIONS ROTONDE /PRIVES</h3>"
            cont += "</br></br>"
            cont += "<table border=1 class='table table-sm o_main_table' width=100% >" 
            cont += "<tr>"
            cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>SERVICES</th>"
            cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>N° FACT.</th>"
            cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>M. PERCU ($)</th>"
            # cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>M. RESTANT ($)</th>"

            tmontant_attendu = 0.0
            tmontant_percu = 0.0
            tmontant_restant = 0.0
            for x in res:

                cont += "<tbody>"
                cont += "<tr>"
                cont += "<td style='text-transform:uppercase !important;'>"+str(x[0].upper()) +"</td>"
                cont += "<td style='text-align:center;'>"+str(x[4]) +"</td>"
                cont += "<td style='text-align:center;'>"+ '{:,}'.format(x[2])+"</td>"
                #cont += "<td style='text-align:left;'>"+str(x[3]) +"</td>"
                cont += "</tr>"
                cont += "</tbody>"
                
                #tmontant_attendu += x[8]
                tmontant_percu += float(x[2])
                #tmontant_restant += x[10]
                
            cont += "<tfooter>"
            cont += "<tr>"
            cont += "<td style='text-align:right;' colspan='2'><b>TOTAL GEN.</b></td>"
            #cont += "<td style='text-align:center;background:#27AE60 ;color:#ffffff'><b>"+str(tmontant_attendu) +"</b></td>"
            cont += "<td style='text-align:center;background:#27AE60 ;color:#ffffff'><b>"+'{:.2f}'.format(float(tmontant_percu))+"</b></td>"
            cont += "</tr>"
            cont += "</tfooter>"
                
            cont += "</table>"

            self.write({'contenu':cont})
            
           
        else:
            raise UserError(_("La date de debut de la période ne peut être supérieur à la date de fin de la période"))

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
            res = {}
            query1 = """
                select line.invoice_date AS Date, line.name AS N_Facture, partner.display_name AS NOM_POSTNOM, 
                (line.amount_total-line.amount_residual_signed) AS M_FACTURE, line.client_name
                from account_move as line
                inner join res_partner as partner on line.partner_id = partner.id and line.categorie in ('prive','prive2')
                AND line.code_jour = '%s' AND line.payment_state in ('paid','partial');
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
        else:
            raise UserError(_(("Veuillez vérifier que les champs code_jour, date de fin, type de rapport journalier sont bien selectionnés ")))
        
    def pharma_convention_report_print(self):
        # combine search condition
        search_conditions = []
        company = False
        start = False
        end = False

        if (self.code_jour and self.convention):
            res = {}
            ### Recuperer les company qui ont été facturées
            
            # query = """
                # select line.invoice_date AS Date, line.name AS N_Facture, partner.display_name AS NOM_POSTNOM, (line.amount_total-line.amount_residual_signed) AS M_FACTURE from account_move as line
                # inner join res_partner as partner on line.partner_id = partner.id and partner.parent_id = '%s'
                # AND line.code_jour = '%s' AND line.state ='posted';
            # """ % (self.convention.id, self.code_jour.code_jour)
            
            query = """
                select line.invoice_date AS Date, line.name AS N_Facture, partner.display_name AS NOM_POSTNOM, (line.amount_total-line.amount_residual_signed) AS M_FACTURE, line.client_name from account_move as line
                inner join res_partner as partner on line.partner_id = partner.id and line.partner_id = '%s' AND line.categorie = 'convention'
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
        else:
            raise UserError(_(("Veuillez vérifier que les champs code_jour, convention, date de fin, type de rapport journalier sont bien selectionnés ")))
            
    def pharma_convention_period_report_print(self):
        # combine search condition
        search_conditions = []
        company = False
        start = False
        end = False
        res = {}
        if (len(self.code_jour_ids)> 0 and self.convention and self.type_rapport=="periodique"):
            code_list = []
            ### Recuperer les company qui ont été facturées
            
            # query = """
                # select line.invoice_date AS Date, line.name AS N_Facture, partner.display_name AS NOM_POSTNOM, (line.amount_total-line.amount_residual_signed) AS M_FACTURE from account_move as line
                # inner join res_partner as partner on line.partner_id = partner.id and partner.parent_id = '%s'
                # AND line.code_jour = '%s' AND line.state ='posted';
            # """ % (self.convention.id, self.code_jour.code_jour)
            for code in self.code_jour_ids:
                code_list.append(code.code_jour)
            
            query = """
                select line.invoice_date AS Date, line.name AS N_Facture, partner.display_name AS NOM_POSTNOM, (line.amount_total-line.amount_residual_signed) AS M_FACTURE, line.client_name from account_move as line
                inner join res_partner as partner on line.partner_id = partner.id and line.partner_id = '%s' AND line.categorie = 'convention'
                AND line.code_jour in %s AND line.state ='posted';
            """ % (self.convention.id, tuple(code_list))
            
            
            
            self.env.cr.execute(query)
            res = self.env.cr.fetchall()
            #raise UserError(_((res)))
            
            
           
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
        else:
            raise UserError(_(("Veuillez vérifier que les champs code_jour, convention, date de fin, type de rapport périodique sont bien selectionnés ")))
    
    def get_laboratoire_detail_convention(self):
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
        if self.start_date <= self.end_date:

            if (self.convention):
            
            

                query = """
                    SELECT moves3.invoice_date as D_facturation, moves1.date as D_Paiement, moves3.NN as N_Facture, moves3.invoice_partner_display_name as Patient, moves3.amount_total_signed as M_total, moves1.amount_total_signed as M_Payé, moves3.amount_residual_signed as M_Restant, 
                    moves3.payment_state as Etat, moves3.libelle, moves3.libelle as Libelle, moves1.matricule as Matricule
                    FROM account_move as moves1 
                    INNER JOIN (SELECT moves2.categorie as categ, moves2.service_id2 as t, moves2.id, moves2.name as NN, moves2.date, moves2.ref, moves2.state, moves2.move_type, moves2.journal_id, moves2.partner_id, moves2.payment_reference, moves2.payment_id, moves2.amount_total_signed, moves2.amount_residual_signed, moves2.invoice_date,moves2.invoice_partner_display_name, moves2.payment_state,moves2.libelle FROM account_move as moves2) as moves3  
                    
                    ON moves1.invoice_date BETWEEN '%s' AND '%s' AND moves3.payment_state IN ('not_paid') and moves3.libelle = 'laboratoire' and moves3.categ ='convention' AND moves3.state ='posted' and moves1.convention_id=%s
                    

                """ % (self.start_date, self.end_date, self.convention.id)
                #self.env.cr.execute(query, {tuple(self.start_date),tuple(self.end_date),tuple(self.journal_payement.id)})
                self.env.cr.execute(query)
                res = self.env.cr.fetchall()
                
                

                #cont += "<h3 style='text-align:center;'>RAPPORT DETAILLE DES CONSULTATIONS  ROTONDE /PRIVES</h3>"
                cont += "</br></br>"
                cont += "<table border=1 class='table table-sm o_main_table' width=100% >" 
                cont += "<tr>"
                
                cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>DATE FAC.</th>"
               
                cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>N° FACTURE</th>"
                cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>NOM PATIENT</th>"
                cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>MATRICULE</th>"
                cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>M. TOTAL</th>"
                # cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>M. PAYE</th>"
                # cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>M. Dû</th>"
                # cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>ETAT</th>"
                #cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>SERVICE</th>"
                cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>LIBELLE</th>"
                cont += "</tr>"

                tmontant_attendu = 0.0
                tmontant_percu = 0.0
                tmontant_restant = 0.0
                for x in res:

                    cont += "<tbody>"
                    cont += "<tr>"
                    cont += "<td>"+str(x[0]) +"</td>"
                    
                    cont += "<td style='text-align:center;'>"+str(x[2])+"</td>"
                    cont += "<td style='text-align:left;'>"+str(x[3]) +"</td>"
                    cont += "<td style='text-align:center;'>"+str(x[10]) +"</td>"
                    cont += "<td style='text-align:right;'>"+str(float(x[4])) +"</td>"
                    # cont += "<td style='text-align:right;'>"+str(float(x[5])) +"</td>"
                    # cont += "<td style='text-align:right;'>"+str(float(x[6])) +"</td>"
                    # cont += "<td style='text-align:center;'>"+str(x[7]) +"</td>"
                    #cont += "<td style='text-align:center;'>"+str(x[8]) +"</td>"
                    cont += "<td style='text-align:center;'>"+str(x[9]) +"</td>"
                    cont += "</tr>"
                    cont += "</tbody>"
                    
                    tmontant_attendu += x[4]
                    tmontant_percu += (float(x[5]))
                    tmontant_restant += x[6]
                    
                cont += "<tfooter>"
                cont += "<tr>"
                cont += "<td colspan='4' style='text-align:right;'><b>TOTAL GEN.</b></td>"
                cont += "<td style='text-align:right;background:#27AE60 ;color:#ffffff'><b>"+str(tmontant_attendu) +"</b></td>"
                # cont += "<td style='text-align:right;background:#27AE60 ;color:#ffffff'><b>"+str(tmontant_percu)+"</b></td>"
                # cont += "<td style='text-align:right;background:#27AE60 ;color:#ffffff'><b>"+str(tmontant_restant) +"</b></td>"
                cont += "<td colspan='1' style='text-align:center;background:#27AE60 ;color:#ffffff'><b></b></td>"
                cont += "</tr>"
                cont += "</tfooter>"
                    
                cont += "</table>"

                self.write({'contenu':cont})

            else:
                raise UserError(_("La date de debut de la période ne peut être supérieur à la date de fin de la période"))

    def get_laboratoire_detail_prive(self):
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
        if self.start_date <= self.end_date:

            if (self.journal_payement and self.journal):
            
            

                query = """
                    SELECT moves3.invoice_date as D_facturation, moves1.date as D_Paiement, moves3.NN as N_Facture, moves3.invoice_partner_display_name as Patient, moves3.amount_total_signed as M_total, moves1.amount_total_signed as M_Payé, moves3.amount_residual_signed as M_Restant, 
                    moves3.payment_state as Etat,  moves3.libelle as Libelle
                    FROM account_move as moves1 
                    INNER JOIN (SELECT moves2.categorie as categ, moves2.service_id2 as t, moves2.id, moves2.name as NN, moves2.date, moves2.ref, moves2.state, moves2.move_type, moves2.journal_id, moves2.partner_id, moves2.payment_reference, moves2.payment_id, moves2.amount_total_signed, moves2.amount_residual_signed, moves2.invoice_date,moves2.invoice_partner_display_name, moves2.payment_state,moves2.libelle FROM account_move as moves2) as moves3  
                   
                    ON moves1.ref=moves3.NN AND moves1.date BETWEEN '%s' AND '%s' AND moves3.payment_state IN ('paid', 'partial') AND moves1.journal_id=%s and moves3.libelle = 'laboratoire' and moves3.categ in ('prive', 'prive2')
                    

                """ % (self.start_date, self.end_date, self.journal_payement.id)
                #self.env.cr.execute(query, {tuple(self.start_date),tuple(self.end_date),tuple(self.journal_payement.id)})
                self.env.cr.execute(query)
                res = self.env.cr.fetchall()
                
                

                #cont += "<h3 style='text-align:center;'>RAPPORT DETAILLE DES CONSULTATIONS  ROTONDE /PRIVES</h3>"
                cont += "</br></br>"
                cont += "<table border=1 class='table table-sm o_main_table' width=100% >" 
                cont += "<tr>"
                
                cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>DATE FAC.</th>"
                cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>DATE PAIEMENT.</th>"
                cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>N° FACTURE</th>"
                cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>NOM PATIENT</th>"
                cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>M. TOTAL</th>"
                cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>M. PAYE</th>"
                cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>M. Dû</th>"
                cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>ETAT</th>"
                # cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>SERVICE</th>"
                cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>LIBELLE</th>"
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
                    cont += "<td style='text-align:left;'>"+str(x[3]) +"</td>"
                    cont += "<td style='text-align:right;'>"+str(float(x[4])) +"</td>"
                    cont += "<td style='text-align:right;'>"+str(float(x[5])) +"</td>"
                    cont += "<td style='text-align:right;'>"+str(float(x[6])) +"</td>"
                    cont += "<td style='text-align:center;'>"+str(x[7]) +"</td>"
                    # cont += "<td style='text-align:center;'>"+str(x[8]) +"</td>"
                    cont += "<td style='text-align:center;'>"+str(x[8]) +"</td>"
                    cont += "</tr>"
                    cont += "</tbody>"
                    
                    tmontant_attendu += x[4]
                    tmontant_percu += (float(x[5]))
                    tmontant_restant += x[6]
                    
                cont += "<tfooter>"
                cont += "<tr>"
                cont += "<td colspan='4' style='text-align:right;'><b>TOTAL GEN.</b></td>"
                cont += "<td style='text-align:right;background:#27AE60 ;color:#ffffff'><b>"+str(tmontant_attendu) +"</b></td>"
                cont += "<td style='text-align:right;background:#27AE60 ;color:#ffffff'><b>"+str(tmontant_percu)+"</b></td>"
                cont += "<td style='text-align:right;background:#27AE60 ;color:#ffffff'><b>"+str(tmontant_restant) +"</b></td>"
                cont += "<td colspan='2' style='text-align:center;background:#27AE60 ;color:#ffffff'><b></b></td>"
                cont += "</tr>"
                cont += "</tfooter>"
                    
                cont += "</table>"

                self.write({'contenu':cont})

            else:
                raise UserError(_("La date de debut de la période ne peut être supérieur à la date de fin de la période"))
 
    def get_consultation_detail_convention(self):
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
        if self.start_date <= self.end_date:

            if (self.convention):
            
            

                query = """
                    SELECT factures.invoice_date as D_facturation, factures.name as N_Facture, factures.invoice_partner_display_name as Patient, 
                    factures.matricule as Matricule,factures.numero_billet as N_Billet, factures.amount_total_signed as M_total, 
                    factures.payment_state as Etat, factures.libelle as Libelle
                    FROM account_move as factures 
                    WHERE factures.invoice_date BETWEEN '%s' AND '%s' AND factures.state = 'posted' 
                    AND factures.convention_id=%s AND factures.payment_state = 'not_paid' 
                    ORDER BY factures.libelle, factures.partner_id;

                """ % (self.start_date, self.end_date, self.convention.id)
                #self.env.cr.execute(query, {tuple(self.start_date),tuple(self.end_date),tuple(self.journal_payement.id)})
                self.env.cr.execute(query)
                res = self.env.cr.fetchall()
                
                #cont += "<h3 style='text-align:center;'>RAPPORT DETAILLE DES CONSULTATIONS  ROTONDE /PRIVES</h3>"
                cont += "</br></br>"
                cont += "<table border=1 class='table table-sm o_main_table' width=100% >" 
                cont += "<tr>"
                cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>DATE FAC.</th>"
                cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>N° FACTURE</th>"
                cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>NOM PATIENT</th>"
                cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>MATRICULE</th>"
                cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>N° BILLET</th>"
                cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>M. A PAYER</th>"
                cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>SERVICE</th>"
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
                    cont += "<td style='text-align:center;'>"+str(x[7].upper()) +"</td>"
                    cont += "</tr>"
                    cont += "</tbody>"
                    
                    tmontant_attendu += float(x[5])
                    
                cont += "<tfooter>"
                cont += "<tr>"
                cont += "<td colspan='4' style='text-align:right;'><b>TOTAL GEN.</b></td>"
                cont += "<td style='text-align:right;background:#27AE60 ;color:#ffffff'><b>"+'{:.2f}'.format(float(tmontant_attendu)) +"</b></td>"
                # cont += "<td style='text-align:right;background:#27AE60 ;color:#ffffff'><b>"+str(tmontant_percu)+"</b></td>"
                # cont += "<td style='text-align:right;background:#27AE60 ;color:#ffffff'><b>"+str(tmontant_restant) +"</b></td>"
                cont += "<td colspan='2' style='text-align:center;background:#27AE60 ;color:#ffffff'><b></b></td>"
                cont += "</tr>"
                cont += "</tfooter>"
                    
                cont += "</table>"

                self.write({'contenu':cont})

            else:
                raise UserError(_("La date de debut de la période ne peut être supérieur à la date de fin de la période"))
    
    def get_consultation_detail_prive(self):
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
        if self.start_date <= self.end_date:

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
                    AND paiement.journal_id=%s and factures.categ in ('prive', 'prive2', 'vip', 'social') order by factures.libelle asc;

                """ % (self.start_date, self.end_date, self.journal_payement.id)
                #self.env.cr.execute(query, {tuple(self.start_date),tuple(self.end_date),tuple(self.journal_payement.id)})
                self.env.cr.execute(query)
                res = self.env.cr.fetchall()
                
                

                #cont += "<h3 style='text-align:center;'>RAPPORT DETAILLE DES CONSULTATIONS  ROTONDE /PRIVES</h3>"
                cont += "</br></br>"
                cont += "<table border=1 class='table table-sm o_main_table' width=100% >" 
                cont += "<tr>"
                
                cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>DATE FAC.</th>"
                cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>DATE PAIEMENT.</th>"
                cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>N° FACTURE</th>"
                cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>NOM PATIENT</th>"
                cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>M. TOTAL</th>"
                cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>M. PAYE</th>"
                cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>M. Dû</th>"
                cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>ETAT</th>"
                #cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>SERVICE</th>"
                cont += "<th style='text-align:center;background:#7fb5da;color:#ffffff'>LIBELLE</th>"
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
                    cont += "<td style='text-align:left;'>"+str(x[3]) +"</td>"
                    cont += "<td style='text-align:right;'>"+'{:.2f}'.format(float(x[4])) +"</td>"
                    cont += "<td style='text-align:right;'>"+'{:.2f}'.format(float(x[5])) +"</td>"
                    cont += "<td style='text-align:right;'>"+'{:.2f}'.format(float(x[6])) +"</td>"
                    cont += "<td style='text-align:center;'>"+str(x[7]) +"</td>"
                    cont += "<td style='text-align:center;'>"+str(x[8].upper()) +"</td>"
                    #cont += "<td style='text-align:center;'>"+str(x[9]) +"</td>"
                    cont += "</tr>"
                    cont += "</tbody>"
                    
                    tmontant_attendu += x[4]
                    tmontant_percu += (float(x[5]))
                    tmontant_restant += x[6]
                    
                cont += "<tfooter>"
                cont += "<tr>"
                cont += "<td colspan='4' style='text-align:right;'><b>TOTAL GEN.</b></td>"
                cont += "<td style='text-align:right;background:#27AE60 ;color:#ffffff'><b>"+'{:.2f}'.format(float(tmontant_attendu)) +"</b></td>"
                cont += "<td style='text-align:right;background:#27AE60 ;color:#ffffff'><b>"+'{:.2f}'.format(float(tmontant_percu))+"</b></td>"
                cont += "<td style='text-align:right;background:#27AE60 ;color:#ffffff'><b>"+'{:.2f}'.format(float(tmontant_restant)) +"</b></td>"
                cont += "<td colspan='3' style='text-align:center;background:#27AE60 ;color:#ffffff'><b></b></td>"
                cont += "</tr>"
                cont += "</tfooter>"
                    
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