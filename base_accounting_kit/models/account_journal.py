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

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from datetime import datetime, date, timedelta



class AccountJournal(models.Model):
    _inherit = "account.journal"
    
    orientation_journal = fields.Selection([('code','Journal à Code'),('normal','Journal Normal')], default='normal', string="Orientation Journal")
    code_jour = fields.Char(string="Code Jour", readonly="1")

    is_private = fields.Boolean(string="Journal patient privé")
    is_abonne = fields.Boolean(string="Journal patient abonné")

    # def set_code_jour(self, code):
        # if code:
            # self.code_jour = code    

    # def cancel_code_jour(self):
        # self.code_jour = ""

    def action_open_reconcile(self):
        if self.type in ['bank', 'cash']:
            # Open reconciliation view for bank statements belonging to this journal
            bank_stmt = self.env['account.bank.statement'].search([('journal_id', 'in', self.ids)]).mapped('line_ids')
            return {
                'type': 'ir.actions.client',
                'tag': 'bank_statement_reconciliation_view',
                'context': {'statement_line_ids': bank_stmt.ids, 'company_ids': self.mapped('company_id').ids},
            }
        else:
            # Open reconciliation view for customers/suppliers
            action_context = {'show_mode_selector': False, 'company_ids': self.mapped('company_id').ids}
            if self.type == 'sale':
                action_context.update({'mode': 'customers'})
            elif self.type == 'purchase':
                action_context.update({'mode': 'suppliers'})
            return {
                'type': 'ir.actions.client',
                'tag': 'manual_reconciliation_view',
                'context': action_context,
            }
            
            
            
# class AccountJournalCode(models.Model):
    # _name = "account.journal.code"

    # date_ouverture = fields.Date(string="Date debut", required="1")
    # code = fields.Char(string="Code")
    # date_fermeture = fields.Date(string="Date de fin", compute='_set_fermeture_date', store=True)
    # date_ouverture1 = fields.Datetime(string="Date d'Ouverture", readonly="1")
    # date_fermeture1 = fields.Datetime(string="Date de fermeture", readonly="1")
    # code_jour = fields.Char(string="Code Jour", readonly="0")
    # journal = fields.Many2one('account.journal', string="Journal")
    # equipe = fields.Many2one('res.users', 'Crée par:', default=lambda self: self.env.user, readonly="True")
    # internal_status = fields.Selection([
        # ('new', 'Nouveau'),
        # ('cours', 'En cours'),
        # ('close', 'Cloturé'),
    # ], string='Status', default='new')

    # @api.model
    # def create(self, vals):
        # #if vals['date_ouverture'] > vals['date_fermeture']:
        # #    raise UserError(_("La date de debut ne peut être supérieur à la date de fin"))
        # #else:
        # vals['code'] = self.env['ir.sequence'].next_by_code('account.journal.code.name')

        # return super(AccountJournalCode, self).create(vals)
        
        
    # def name_get(self):
        # result = []
        # for rec in self:
            # result.append((rec.id, "%s" % (rec.code_jour)))       
        # return result
        
    
    # @api.onchange('date_ouverture')
    # def _set_fermeture_date(self):
        # if self.date_ouverture:
            # self.date_fermeture = self.date_ouverture + timedelta(days=1)
    
    # def check_validaty_status(self, journal):
        # nbre = self.search([('internal_status','=','cours'),('journal','=',journal)])
        # return len(nbre)

    # def write(self, vals):
        # ## Check validaté de la date
        # date_format = '%Y-%m-%d'

        # date_ouv = vals['date_ouverture'] if vals.get('date_ouverture') else self.date_ouverture
        # date_ferm = vals['date_fermeture'] if vals.get('date_fermeture') else self.date_fermeture

        # dt_ouv = datetime.strptime(str(date_ouv), date_format)
        # dt_ferme = datetime.strptime(str(date_ferm), date_format)
        # #raise UserError(_("%s , %s", dt_ouv ,dt_ferme))
        # if dt_ouv > dt_ferme:
            # raise UserError(_("La date de debut ne peut être supérieur à la date de fin"))

        # return super(AccountJournalCode, self).write(vals)
    
    # def open_generate_code(self):
        # if self.date_ouverture and self.date_fermeture:
            # nbre = self.check_validaty_status(self.journal.id)
            # #raise UserError(_("%s ", jr))
            # if nbre == 0:
                # sequence = str(self.journal.code)+"/"+str(self.code)
                # self.code_jour = sequence
                # self.date_ouverture1 = fields.Datetime.now()
                # self.internal_status = 'cours'

                # self.env['account.journal'].search([('code', '=', self.journal.code)]).set_code_jour(sequence)
            # else:
                # raise UserError(_("Veillez cloturer tous les codes jours en cours de validité avant d'executer cette tâche"))
            # #self.env['account.journal'].search([('code', '=', self.journal.code)]).write({'code_jour':self.code_jour})


    # def close_generate_code(self):
        # if self.date_ouverture and self.date_fermeture:
            # self.date_fermeture1 = fields.Datetime.now()
            # self.internal_status = 'close'
            # self.env['account.journal'].search([('code', '=', self.journal.code)]).cancel_code_jour()


# class AccountMoveCodeJour(models.Model):
    # _inherit = "account.move"
    
    # code_jour = fields.Char(string="Code Jour")
    
    
    # @api.model
    # def create(self, vals_list):
        #OVERRIDE
        # mv_id = super(AccountMoveCodeJour, self).create(vals_list)
        # if mv_id.journal_id.orientation_journal == "code":
            # self.code_jour == mv_id.journal_id.code_jour

        # return mv_id
        
    # @api.onchange('journal_id')
    # def on_change_journal(self):
        # if self.journal_id.orientation_journal == 'code':
            # self.code_jour = self.journal_id.code_jour