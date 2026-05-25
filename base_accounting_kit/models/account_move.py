# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2019-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.addons.base.models import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF


class AccountMove(models.Model):
    _inherit = 'account.move'

    asset_depreciation_ids = fields.One2many('account.asset.depreciation.line',
                                             'move_id',
                                             string='Assets Depreciation Lines')
                                             
    patient_id = fields.Many2one('fertility.patient')                                         
                                             
    matricule = fields.Char(string="Matricule")
    convention_id = fields.Many2one('res.partner', string='Convention')
    service_id = fields.Many2one('module.service', string='Service',)
    service_code = fields.Char(related='service_id.code', string='Code Service', store=True)
    rubrique_id = fields.Many2one('module.rubrique', 'Rubrique')
    medecin_id = fields.Many2one('module.doctor', string='Médecin',)
    autres_medecin = fields.Many2one('module.doctor', string='Autres Médecins',)
    #is_labo = fields.Boolean(string='Laboratoire')
    
    service_id2 = fields.Many2one('ksoft.services', string='Service',)
    service_code2 = fields.Char(related='service_id2.service_name', string='Code Service', store=True)
    rubrique_id2 = fields.Many2one('ksoft.rubrique', 'Rubrique')
    medecin_id2 = fields.Many2one('fertility.doctor', string='Médecin',)
    autres_medecin2 = fields.Many2one('fertility.doctor', string='Autres Médecins',)

    ## Info patient
    categorie = fields.Selection([('prive','Privé'),('prive2','Ayant-Droit'),('convention','Abonné')], string="Catégorie", readonly=False, store=True)
    classe = fields.Selection([('agent','Agent'),('epoux','Epoux(se)'),('enf','Enfants')], string="Classe", readonly=False, store=True)

    numero_billet = fields.Char(string="Billet d'envoi")
    email = fields.Char(string="Email")
    phone = fields.Char(string="Téléphone")
    function = fields.Char(string="Profession")

    ## Elements medicales
    consultation_id = fields.Many2one('ksoft.appointment')
    consultation_consultation_id = fields.Many2one('fertility.appointment')
    imagerie_id = fields.Many2one('fertility.examen.imagerie')  
    prescription_id = fields.Many2one('module.ordonnance')  
    lunettes_id = fields.Many2one('module.prescription')
    
    

    def setStatus(self):  # line_ids
        if self.consultation_consultation_id:
            appo = self.env['fertility.appointment'].browse(int(self.consultation_consultation_id.id))
            appo.setInternalStatus()
            self.env['sh.announcement'].notifTriage()

        elif self.invoice_line_ids.imagerie_id or self.line_ids.imagerie_id:
            for img in self.invoice_line_ids:
                if img.imagerie_id:
                    self.env['fertility.examen.imagerie'].browse(img.imagerie_id.id).setStatus()

        elif self.prescription_id:
            ord = self.env['module.ordonnance'].browse(int(self.prescription_id))
            ord.setInternalStatus()
        #
        elif self.lunettes_id:
            presc = self.env['module.prescription'].browse(int(self.lunettes_id))
            presc.setInternalStatus()
            
        self.payment_state = 'apa'
        return True
        
        
    def button_cancel(self):
        for move in self:
            for line in move.asset_depreciation_ids:
                line.move_posted_check = False
        return super(AccountMove, self).button_cancel()

    def post(self):

        self.mapped('asset_depreciation_ids').post_lines_and_close_asset()
        return super(AccountMove, self).post()
    

    @api.onchange('patient_id')
    def _onchange_patient_id(self):
        vals = None
        if self.patient_id:
            self.onchange_partner_suite(self.patient_id)
            
    def onchange_partner_suite(self, patient):
        pt = False
        if patient:
            pt = patient.id
            self.convention_id = self.env['fertility.patient'].browse(pt).parent_id
            self.matricule = self.env['fertility.patient'].browse(pt).matricule
            self.categorie = self.env['fertility.patient'].browse(pt).categorie
            self.classe = self.env['fertility.patient'].browse(pt).classe
            self.email = self.env['fertility.patient'].browse(pt).email
            self.phone = self.env['fertility.patient'].browse(pt).phone
            self.function = self.env['fertility.patient'].browse(pt).function
            self.partner_id = self.env['fertility.patient'].browse(pt).partner_id

    @api.model
    def _refund_cleanup_lines(self, lines):
        result = super(AccountMove, self)._refund_cleanup_lines(lines)
        for i, line in enumerate(lines):
            for name, field in line._fields.items():
                if name == 'asset_category_id':
                    result[i][2][name] = False
                    break
        return result

    def action_cancel(self):
        res = super(AccountMove, self).action_cancel()
        self.env['account.asset.asset'].sudo().search(
            [('invoice_id', 'in', self.ids)]).write({'active': False})
        return res

    def action_post(self):
        result = super(AccountMove, self).action_post()

        for inv in self:
            context = dict(self.env.context)
            # Within the context of an invoice,
            # this default value is for the type of the invoice, not the type of the asset.
            # This has to be cleaned from the context before creating the asset,
            # otherwise it tries to create the asset with the type of the invoice.
            context.pop('default_type', None)
            inv.invoice_line_ids.with_context(context).asset_create()
        return result


class AccountInvoiceLine(models.Model):
    _inherit = 'account.move.line'

    asset_category_id = fields.Many2one('account.asset.category',
                                        string='Asset Category')
    asset_start_date = fields.Date(string='Asset Start Date',
                                   compute='_get_asset_date', readonly=True,
                                   store=True)
    asset_end_date = fields.Date(string='Asset End Date',
                                 compute='_get_asset_date', readonly=True,
                                 store=True)
    asset_mrr = fields.Float(string='Monthly Recurring Revenue',
                             compute='_get_asset_date',
                             readonly=True, digits='Account',
                             store=True)
                             
                             
                             
    ## Bon 
    #patient_id = fields.Many2one(related='move_id.patient_id', store=True, string="Patient", readonly=False)
    patient_id = fields.Many2one('fertility.patient')    
    # doctor_id = fields.Many2one(related='move_id.medecin_id', store=True, readonly=False)
    # matricule = fields.Char(related='move_id.matricule',string="Matricule", store=True, readonly=False)
    # categorie = fields.Selection(related='move_id.categorie', store=True,  string="Catégorie", readonly=False)
    # classe = fields.Selection(related='move_id.classe', string="Classe", readonly=False, store=True)

    # etat_paiement = fields.Selection(related='move_id.payment_state', string="Etat Paiement", readonly=False, store=True)
    # date_realisation = fields.Datetime(string="Date de réalisation", default=fields.Date.today)
    doctor_id = fields.Many2one('fertility.doctor', string='Médecin',)
    numero_billet = fields.Char(string="Billet d'envoi")

    # # product_category_id = fields.Char(string="Categorie Article")
    # # product_category_name = fields.Char(string="Nom Categorie Article")
    # # product_category_parent_id = fields.Char(string="Categorie Parent Article")
    # # product_name_cat_parent_id = fields.Char(string="Nom Categorie Article")

    # # product_category_id = fields.Many2one(related='product_id.product_tmpl_id.categ_id', store=True, string="Categorie Article")
    # # product_category_name = fields.Char(related='product_id.product_tmpl_id.categ_id.name', store=True, string="Nom Categorie Article")
    # # product_category_parent_id = fields.Many2one(related='product_id.product_tmpl_id.categ_id.parent_id', store=True, string="Categorie Parent Article")
    # # product_name_cat_parent_id = fields.Char(related='product_id.product_tmpl_id.categ_id.parent_id.name', store=True, string="Nom Categorie Article")
    # # ## Id Imagerie
    # imagerie_id = fields.Many2one('fertility.examen.imagerie')

    # ### Selection
    print_select = fields.Boolean(string="Print", default=False)
    state_line = fields.Selection([('not_paid','Non payé'),('paid','payé')], default='not_paid', string="Etat Line")

                             
    ## CUSTOMER
    num_billet = fields.Char(string="N° Billet")
    date_realisation = fields.Date(string="Date-Heure")
    service_id = fields.Many2one(related='move_id.service_id', string='Service', store=True, readonly=True)
    rubrique_id = fields.Many2one(related='move_id.rubrique_id', string='Rubrique', store=True, readonly=True)
    # service_id2 = fields.Many2one(related='move_id.service_id2', string='Service', store=True, readonly=True)
    # rubrique_id2 = fields.Many2one(related='move_id.rubrique_id2', string='Rubrique', store=True, readonly=True)

    @api.depends('asset_category_id', 'move_id.invoice_date')
    def _get_asset_date(self):
        for record in self:
            record.asset_mrr = 0
            record.asset_start_date = False
            record.asset_end_date = False
            cat = record.asset_category_id
            if cat:
                if cat.method_number == 0 or cat.method_period == 0:
                    raise UserError(_(
                        'The number of depreciations or the period length of your asset category cannot be null.'))
                months = cat.method_number * cat.method_period
                if record.move_id in ['out_invoice', 'out_refund']:
                    record.asset_mrr = record.price_subtotal_signed / months
                if record.move_id.invoice_date:
                    start_date = datetime.strptime(
                        str(record.move_id.invoice_date), DF).replace(day=1)
                    end_date = (start_date + relativedelta(months=months,
                                                           days=-1))
                    record.asset_start_date = start_date.strftime(DF)
                    record.asset_end_date = end_date.strftime(DF)

    def asset_create(self):
        for record in self:
            if record.asset_category_id:
                vals = {
                    'name': record.name,
                    'code': record.move_id.name or False,
                    'category_id': record.asset_category_id.id,
                    'value': record.price_subtotal,
                    'partner_id': record.partner_id.id,
                    'company_id': record.move_id.company_id.id,
                    'currency_id': record.move_id.company_currency_id.id,
                    'date': record.move_id.invoice_date,
                    'invoice_id': record.move_id.id,
                }
                changed_vals = record.env[
                    'account.asset.asset'].onchange_category_id_values(
                    vals['category_id'])
                vals.update(changed_vals['value'])
                asset = record.env['account.asset.asset'].create(vals)
                if record.asset_category_id.open_asset:
                    asset.validate()
        return True

    @api.onchange('asset_category_id')
    def onchange_asset_category_id(self):
        if self.move_id == 'out_invoice' and self.asset_category_id:
            self.account_id = self.asset_category_id.account_asset_id.id
        elif self.move_id == 'in_invoice' and self.asset_category_id:
            self.account_id = self.asset_category_id.account_asset_id.id

    @api.onchange('product_uom_id')
    def _onchange_uom_id(self):
        result = super(AccountInvoiceLine, self)._onchange_uom_id()
        self.onchange_asset_category_id()
        return result

    @api.onchange('product_id')
    def _onchange_product_id(self):
        vals = super(AccountInvoiceLine, self)._onchange_product_id()
        if self.product_id:
            if self.move_id == 'out_invoice':
                self.asset_category_id = self.product_id.product_tmpl_id.deferred_revenue_category_id
            elif self.move_id == 'in_invoice':
                self.asset_category_id = self.product_id.product_tmpl_id.asset_category_id
        return vals

    def _set_additional_fields(self, invoice):
        if not self.asset_category_id:
            if invoice.type == 'out_invoice':
                self.asset_category_id = self.product_id.product_tmpl_id.deferred_revenue_category_id.id
            elif invoice.type == 'in_invoice':
                self.asset_category_id = self.product_id.product_tmpl_id.asset_category_id.id
            self.onchange_asset_category_id()
        super(AccountInvoiceLine, self)._set_additional_fields(invoice)

    def get_invoice_line_account(self, type, product, fpos, company):
        return product.asset_category_id.account_asset_id or super(
            AccountInvoiceLine, self).get_invoice_line_account(type, product,
                                                               fpos, company)
