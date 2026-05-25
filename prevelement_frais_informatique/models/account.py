# -*- coding: utf-8 -*-

from odoo import models,fields,tools, api, _
from odoo.tools import float_is_zero
import datetime
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class account_move_line(models.Model):
    _inherit = 'account.move.line'

    select = fields.Boolean('Select', default=True) 
    etat = fields.Boolean('Payé ?', readonly=True)

    
class AccountMove(models.Model):
    _inherit = 'account.move'

    is_prelever = fields.Boolean('est Prelevé', readonly=True)

    def button_draft(self):
        res = super().button_draft()
        self.is_prelever = False
        for line in self.invoice_line_ids.filtered(lambda ligne:ligne.etat):
            line.etat = False
        obj_frais_info = self.env['frais.informatique'].search([('num_fac','=',self.name)])
        obj_frais_info.unlink()

   

    def _get_reconciled_info_JSON_values(self):
        foreign_currency = self.currency_id if self.currency_id != self.company_id.currency_id else False

        reconciled_vals = []
        pay_term_line_ids = self.line_ids.filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
        partials = pay_term_line_ids.mapped('matched_debit_ids') + pay_term_line_ids.mapped('matched_credit_ids')
        for partial in partials:
            counterpart_lines = partial.debit_move_id + partial.credit_move_id
            counterpart_line = counterpart_lines.filtered(lambda line: line not in self.line_ids)

            if foreign_currency and partial.currency_id == foreign_currency:
                amount = partial.amount_currency
            else:
                amount = partial.company_currency_id._convert(partial.amount, self.currency_id, self.company_id, self.date)

            if float_is_zero(amount, precision_rounding=self.currency_id.rounding):
                continue

            ref = counterpart_line[0].move_id.name
            if counterpart_line[0].move_id.ref:
                ref += ' (' + counterpart_line[0].move_id.ref + ')'

            reconciled_vals.append({
                'name': counterpart_line[0].name,
                'journal_name': counterpart_line[0].journal_id.name,
                'amount': amount,
                'currency': self.currency_id.symbol,
                'digits': [69, self.currency_id.decimal_places],
                'position': self.currency_id.position,
                'date': counterpart_line[0].date,
                'payment_id': counterpart_line[0].id,
                'account_payment_id': counterpart_line[0].payment_id.id,
                'payment_method_name': counterpart_line[0].payment_id.payment_method_id.name if counterpart_line[0].journal_id.type == 'bank' else None,
                'move_id': counterpart_line[0].move_id.id,
                'ref': ref,
            })

        return reconciled_vals

class account_payment_register(models.TransientModel):
    _inherit = 'account.payment.register'

    #frais_info = fields.Monetary('Frais Informatique', readonly=True, compute='frais_informatique')

    frais_info = fields.Float('Frais Informatique', readonly=True)

    @api.depends('source_amount', 'source_amount_currency', 'source_currency_id', 'company_id', 'currency_id', 'payment_date')
    def _compute_amount(self):

        res = super()._compute_amount()

        active_ids = self._context.get('active_ids') or self._context.get('active_id')
        invoices = self.env['account.move'].browse(active_ids).filtered(lambda move: move.is_invoice(include_receipts=True))

        
        select_subtotal = sum(line.price_subtotal for line in invoices.invoice_line_ids.filtered(lambda ligne:ligne.select != True))

        self.amount = self.amount - select_subtotal

        return res

    def _create_payment_vals_from_wizard(self):
        res = super()._create_payment_vals_from_wizard()
        
        active_ids = self._context.get('active_ids') or self._context.get('active_id')
        invoices = self.env['account.move'].browse(active_ids).filtered(lambda move: move.is_invoice(include_receipts=True))
        
        #raise UserError(_(invoices))
        
        select_subtotal = sum(line.price_subtotal for line in invoices.invoice_line_ids.filtered(lambda ligne:ligne.select != True))
        res['amount'] = res['amount'] - select_subtotal
        return res
    
    def action_create_payments(self):
        
        data = self._create_payment_vals_from_wizard()
        data['frais_info'] = self.frais_info


        if data['amount'] == 0.0:
            raise UserError(_('Selection au moin une ligne de la facture pour passer le paiement'))
        
        active_ids = self._context.get('active_ids') or self._context.get('active_id')
        invoices = self.env['account.move'].browse(active_ids).filtered(lambda move: move.is_invoice(include_receipts=True))
        
        invoice_lines = invoices

        if invoice_lines:
            for lig in invoices.invoice_line_ids.filtered(lambda ligne:ligne.select):
                lig.etat = True

            config = self.env['res.config.settings'].sudo().get_values()
            config_value = config.get('type_prevelement')

            if config_value == 'par_categorie_article':
                self.create_frais_informatique(data)
            elif config_value == 'par_montant_global' and not invoices.is_prelever:
                self.create_frais_informatique(data)
                invoice_lines.is_prelever = True
        res = super().action_create_payments()
        return res

    @api.depends('amount')
    def frais_informatique(self):
        
        active_ids = self._context.get('active_ids') or self._context.get('active_id')
        invoices = self.env['account.move'].browse(active_ids).filtered(lambda move: move.is_invoice(include_receipts=True))
        
        config = self.env['res.config.settings'].sudo().get_values()
        config_value = config.get('type_prevelement')

        if config_value == 'par_categorie_article':
            somme = 0.0
            for line in invoices.invoice_line_ids.filtered(lambda ligne:ligne.select and not ligne.etat):
                if line.product_id.categ_id.montant_prelever > 0.0:
                        somme += line.product_id.categ_id.montant_prelever
                else:
                    raise UserError(
				                    _("Configurer la categorie du produit (%s) avec le montant du prelement de frais informatique" % line.product_id.name))
            self.frais_info = somme

        elif config_value == 'par_montant_global':
            if invoices.is_prelever:
                self.frais_info = 0
            else:
                self.frais_info = config.get('montant_prelever')
        else:
            raise UserError(
				_("Veuillez configurer le prélevement de frais informatique (Voir l'Admin) -> Configuration -> Prélevement Frais Informatique."))

    def create_frais_informatique(self, data):
        fac_id = self.env['account.move'].search([('name','=',data['ref'])],limit=1)
        res = self.env['frais.informatique'].create({
                                                'date' : data['date'],
                                                'num_fac' :  data['ref'],
                                                'partner_id' : fac_id.partner_id.id,
                                                'montant_paie' :  data['amount'],
                                                'frais_informatique' : data['frais_info'],
                                                'state' : 'non_paye',
                                            })
        return res
       

    
    

