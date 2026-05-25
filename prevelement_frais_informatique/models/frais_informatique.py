# -*- coding: utf-8 -*-

from odoo import api, fields, models,tools, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class Frais_Informatique(models.Model):
    _name = 'frais.informatique'

    num_op = fields.Char('Numero Operation', readonly=True)
    num_fac = fields.Char('Numero Facture', readonly=True)
    date = fields.Date('Date', readonly=True)
    partner_id = fields.Many2one('res.partner', 'Partenaire',  readonly=True)
    frais_informatique = fields.Float('Frais Informatique', readonly=True)
    montant_paie = fields.Float('Montant Payé', readonly=True)
    state = fields.Selection([('non_paye','Non Paie'),('paye','Paie')],'Etat', readonly=True)

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('frais.informatique')
        vals['num_op'] = "FI/" + str(sequence)
        res = super().create(vals)
        return res     
    
