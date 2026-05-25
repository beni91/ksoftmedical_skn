# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class AccountJournal(models.Model):
    _inherit = "account.journal"

    user_ids = fields.Many2many('res.users', 'journal_user_rel', string='Utilisateurs autorisés')
    
    def action_get_users(self):
        serv1 = []
        serv2 = []
        
        context = self._context
        current_uid  = context.get('uid')
        serv1 = self.env['res.users'].browse(current_uid ).journal_ids
        for i in serv1:
            serv2.append(i.id)
            
        #kanban_id = self.env.ref('account.account_journal_dashboard_kanban_view')
        kanban_id = self.env.ref('od_journal_restriction.account_journal_dashboard_kanban_view1')
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Vue d\'ensemble comptable',
            'view_type': 'kanban',
            'view_mode': 'kanban',
            'res_model': 'account.journal',
            'domain': [('id', 'in', serv2)],
            'view_id': kanban_id.id,    
            'target': 'current',
            'context': context,
        }


class account_payment_register2(models.TransientModel):
    _inherit = 'account.payment.register'

    def _create_payment_vals_from_wizard(self):
    
        
        indice = "faux"
        t=[]
        indice2 = self.journal_id.id
        user_id = self._context.get('uid') or self._context.get('uid')
        
        journal_user = self.env['account.journal'].search([('user_ids','child_of', user_id)])
        
        for jr in journal_user:
          t.append(jr.id)  
          
        if indice2 in t:
            indice = "vrai"
        
        #raise UserError(_(indice))
        
        #t = jr.id
        if indice == "vrai":
            res = super()._create_payment_vals_from_wizard()
            return res
       
        else:
            raise UserError(_("Vous n'etes pas autorisé à effectuer une opération dans cette caisse, veuillez selectionnez votre caisse",))
    
    
  
  