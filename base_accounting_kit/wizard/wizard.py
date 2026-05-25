# -*- coding: utf-8 -*-


from datetime import datetime
from datetime import date
from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)



class RapportConventionDetail(models.TransientModel):
    _name = 'rapport.convention.detail'

    date_debut = fields.Date('Date Début', required=True,
                            default=lambda self: fields.Date.to_string(date.today().replace(day=1)))
    date_fin = fields.Date('Date Fin', required=True,
                          default=lambda self: fields.Date.to_string(date.today()))
    convention_id = fields.Many2one('res.partner', 'Convention')


    #OK
    def print_report(self):
        data = {}
        report = []
        liste_des_factures = {}

        invoices_ids = self.env['account.move'].search([
            ('invoice_date', '>=', self.date_debut),
            ('invoice_date', '<=', self.date_fin),
            ('convention_id', '=', self.convention_id.id),
            ('state', '=', 'posted')
        ])

        montant_global = 0

        for facture in invoices_ids:
            ligne_de_facture = []
            montant_ligne = 0

            for line in facture.invoice_line_ids:
                if line.product_id:
                    montant_ligne += line.price_subtotal
                    vals_lines = {
                        'date': line.date,
                        'produit': line.product_id.name,
                        'prix': line.price_subtotal,
                        'somme_ligne': montant_ligne
                    }
                    montant_global = montant_global + vals_lines['somme_ligne']
                    ligne_de_facture.append(vals_lines)

            vals = {
                'partner': facture.partner_id.name,
                'ref': facture.name,
                'date': facture.invoice_date,
                'lignes_de_facture': ligne_de_facture,
                'devise': ("Fc" if facture.currency_id.name == 'CDF' else facture.currency_id.name)
            }

            if facture.partner_id.name not in liste_des_factures:
                liste_des_factures[facture.partner_id.name] = []
            liste_des_factures[facture.partner_id.name].append(vals)

        data['montant_global'] = montant_global
        dev = ""
        for d in invoices_ids.mapped('currency_id'):
            dev = dev + ('-' if dev else '') + d.name.upper()
        data['devise'] = dev

        data['factures'] = [{'partner': partner, 'invoices': invoices} for partner, invoices in liste_des_factures.items()]

        vals_report = {
            'date_debut': self.date_debut,
            'date_fin': self.date_fin,
            'convention_id': self.convention_id.name,
        }

        report.append(vals_report)
        data['report_infos'] = report

        return self.env.ref('base_accounting_kit.rapport_periodique_convention').report_action(self, data=data)



    # N 2
    # def print_report(self):
    #     data = {}
    #     report = []
    #     liste_des_factures = {}

    #     invoices_ids = self.env['account.move'].search([
    #         ('invoice_date', '>=', self.date_debut),
    #         ('invoice_date', '<=', self.date_fin),
    #         ('convention_id', '=', self.convention_id.id),
    #         ('state', '=', 'posted')
    #     ])

    #     montant_global = 0

    #     for facture in invoices_ids:
    #         ligne_de_facture = []
    #         montant_ligne = 0

    #         for line in facture.invoice_line_ids:
    #             if line.product_id:
    #                 montant_ligne += line.price_subtotal
    #                 vals_lines = {
    #                     'date': line.date,
    #                     'produit': line.product_id.name,
    #                     'prix': line.price_subtotal,
    #                     'somme_ligne': montant_ligne
    #                 }
    #                 montant_global = montant_global + vals_lines['somme_ligne']
    #                 ligne_de_facture.append(vals_lines)

    #         vals = {
    #             'partner': facture.partner_id.name,
    #             'ref': facture.name,
    #             'date': facture.invoice_date,
    #             'lignes_de_facture': ligne_de_facture,
    #             'devise': ("Fc" if facture.currency_id.name == 'CDF' else facture.currency_id.name)
    #         }

    #         # Calculate the total sum for each partner
    #         if facture.partner_id.name not in liste_des_factures:
    #             liste_des_factures[facture.partner_id.name] = {'invoices': [], 'total_sum': 0}

    #         liste_des_factures[facture.partner_id.name]['invoices'].append(vals)
    #         liste_des_factures[facture.partner_id.name]['total_sum'] += montant_global

    #     data['montant_global'] = montant_global
    #     dev = ""
    #     for d in invoices_ids.mapped('currency_id'):
    #         dev = dev + ('-' if dev else '') + d.name.upper()
    #     data['devise'] = dev

    #     # Update the 'factures' key with total sums
    #     data['factures'] = [{'partner': partner, 'invoices': invoices, 'total_sum': total_sum}
    #                         for partner, (invoices, total_sum) in liste_des_factures.items()]

    #     vals_report = {
    #         'date_debut': self.date_debut,
    #         'date_fin': self.date_fin,
    #         'convention_id': self.convention_id.name,
    #     }

    #     report.append(vals_report)
    #     data['report_infos'] = report

    #     return self.env.ref('accounting_pdf_reports.rapport_periodique_convention').report_action(self, data=data)


    
    
    # def print_report(self):

    #     data = {}
    #     report = []
    #     liste_des_factures = []

    #     # statement_ids = self.env['account.bank.statement'].search(
    #     #     [('date', '>=', self.date_debut), 
    #     #     ('date', '<=', self.date_fin)],
    #     #      order='date asc',)
    #     invoices_ids = self.env['account.move'].search([
    #             ('invoice_date', '>=', self.date_debut),
    #             ('invoice_date', '<=', self.date_fin),
    #             ('convention_id', '=', self.convention_id.id),
    #             ('state', '=', 'posted')
    #         ])

    #     montant_global = 0
    #     montant_ligne = 0

    #     for facture in invoices_ids:
            
    #         ligne_de_facture = []

    #         for line in facture.invoice_line_ids:
    #             if line.product_id:
    #                 s = montant_ligne + line.price_subtotal
    #                 vals_lines={
    #                     'date' : line.date,
    #                     'produit' : line.product_id.name,
    #                     'prix' : line.price_subtotal,
    #                     'somme_ligne' : s
    #                 }
    #                 montant_global = montant_global + vals_lines['somme_ligne']
    #                 ligne_de_facture.append(vals_lines)

    #         vals = {
    #             'partner': facture.partner_id.name,
    #             'ref': facture.name,
    #             'date': facture.invoice_date,
    #             'lignes_de_facture':ligne_de_facture,
    #             'devise': ("Fc" if facture.currency_id.name=='CDF' else facture.currency_id.name)
    #         }

    #         liste_des_factures.append(vals)

    #     data['montant_global'] = montant_global

    #     dev=""
    #     for d in invoices_ids.currency_id:
    #         dev=dev+('-' if dev else '')+d.name.upper()
    #     data['devise'] = dev

    #     data['factures'] = liste_des_factures


    #     vals_report = {
    #                 'date_debut': self.date_debut,
    #                 'date_fin': self.date_fin,
    #                 'convention_id': self.convention_id.name,
    #         }

    #     report.append(vals_report)

    #     data['report_infos'] = report
    #     return self.env.ref('accounting_pdf_reports.rapport_periodique_convention').report_action(self, data=data)
