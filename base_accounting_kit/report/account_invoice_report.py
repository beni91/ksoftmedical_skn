# -*- coding: utf-8 -*-

from odoo import models, fields, api

from functools import lru_cache


class AccountInvoiceReportCustom(models.Model):
	_inherit = "account.invoice.report"
	_description = "Invoices Statistics"
	_auto = False
	_rec_name = 'invoice_date'
	_order = 'invoice_date desc'

	# ==== Invoice fields ====
	
	matricule = fields.Char(string="Matricule")
	convention_id = fields.Many2one('res.partner', string='Convention')
	service_id = fields.Many2one('module.service', string='Service')
	rubrique_id = fields.Many2one('module.rubrique', 'Rubrique')
	medecin_id = fields.Many2one('module.doctor', string='Médecin',)
	
	
	amount_residual_signed = fields.Monetary(string='Amount Due Signed', store=True,  currency_field='company_currency_id')


	_depends = {
		'account.move': [
			'name', 'state', 'move_type', 'partner_id', 'invoice_user_id', 'fiscal_position_id',
			'invoice_date', 'invoice_date_due', 'invoice_payment_term_id', 'partner_bank_id',
			'matricule','convention_id','service_id','rubrique_id','medecin_id'
		],
		'account.move.line': [
			'quantity', 'price_subtotal', 'amount_residual', 'balance', 'amount_currency',
			'move_id', 'product_id', 'product_uom_id', 'account_id', 'analytic_account_id',
			'journal_id', 'company_id', 'currency_id', 'partner_id'
		],
		'product.product': ['product_tmpl_id'],
		'product.template': ['categ_id'],
		'uom.uom': ['category_id', 'factor', 'name', 'uom_type'],
		'res.currency.rate': ['currency_id', 'name'],
		'res.partner': ['country_id'],
	}

	# @property
	# def _table_query(self):
		# return '%s %s %s' % (self._select(), self._from(), self._where())

	@api.model
	def _select(self):
		return '''
			SELECT
				line.id,
				line.move_id,
				line.product_id,
				line.account_id,
				line.analytic_account_id,
				line.journal_id,
				line.company_id,
				line.company_currency_id,
				line.partner_id AS commercial_partner_id,
				
				move.state,
				move.move_type,
				move.partner_id,
				move.invoice_user_id,
				move.fiscal_position_id,
				move.payment_state,
				move.invoice_date,
				move.invoice_date_due,
				
				move.matricule,
				move.convention_id,
				move.service_id,
				move.rubrique_id,
				move.medecin_id,
				
				uom_template.id												AS product_uom_id,
				template.categ_id											AS product_categ_id,
				line.quantity / NULLIF(COALESCE(uom_line.factor, 1) / COALESCE(uom_template.factor, 1), 0.0) * (CASE WHEN move.move_type IN ('in_invoice','out_refund','in_receipt') THEN -1 ELSE 1 END)
																			AS quantity,
				-line.balance * currency_table.rate							AS price_subtotal,
				-COALESCE(
				   -- Average line price
				   (line.balance / NULLIF(line.quantity, 0.0)) * (CASE WHEN move.move_type IN ('in_invoice','out_refund','in_receipt') THEN -1 ELSE 1 END)
				   -- convert to template uom
				   * (NULLIF(COALESCE(uom_line.factor, 1), 0.0) / NULLIF(COALESCE(uom_template.factor, 1), 0.0)),
				   0.0) * currency_table.rate								AS price_average,
				COALESCE(partner.country_id, commercial_partner.country_id) AS country_id
		'''

	# @api.model
	# def _from(self):
		# return '''
			# FROM account_move_line line
				# LEFT JOIN res_partner partner ON partner.id = line.partner_id
				# LEFT JOIN product_product product ON product.id = line.product_id
				# LEFT JOIN account_account account ON account.id = line.account_id
				# LEFT JOIN account_account_type user_type ON user_type.id = account.user_type_id
				# LEFT JOIN product_template template ON template.id = product.product_tmpl_id
				# LEFT JOIN uom_uom uom_line ON uom_line.id = line.product_uom_id
				# LEFT JOIN uom_uom uom_template ON uom_template.id = template.uom_id
				# INNER JOIN account_move move ON move.id = line.move_id
				# LEFT JOIN res_partner commercial_partner ON commercial_partner.id = move.commercial_partner_id
				# JOIN {currency_table} ON currency_table.company_id = line.company_id
		# '''.format(
			# currency_table=self.env['res.currency']._get_query_currency_table({'multi_company': True, 'date': {'date_to': fields.Date.today()}}),
		# )

	# @api.model
	# def _where(self):
		# return '''
			# WHERE move.move_type IN ('out_invoice', 'out_refund', 'in_invoice', 'in_refund', 'out_receipt', 'in_receipt')
				# AND line.account_id IS NOT NULL
				# AND NOT line.exclude_from_invoice_tab
		# '''


class ReportInvoiceWithoutPayment(models.AbstractModel):
	_name = 'report.account.report_invoice'
	_description = 'Account report without payment lines'

	@api.model
	def _get_report_values(self, docids, data=None):
		docs = self.env['account.move'].browse(docids)

		qr_code_urls = {}
		for invoice in docs:
			if invoice.display_qr_code:
				new_code_url = invoice.generate_qr_code()
				if new_code_url:
					qr_code_urls[invoice.id] = new_code_url

		return {
			'doc_ids': docids,
			'doc_model': 'account.move',
			'docs': docs,
			'qr_code_urls': qr_code_urls,
		}

class ReportInvoiceWithPayment(models.AbstractModel):
	_name = 'report.account.report_invoice_with_payments'
	_description = 'Account report with payment lines'
	_inherit = 'report.account.report_invoice'

	@api.model
	def _get_report_values(self, docids, data=None):
		rslt = super()._get_report_values(docids, data)
		rslt['report_type'] = data.get('report_type') if data else ''
		return rslt
