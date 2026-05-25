# -*- coding: utf-8 -*-

from odoo import models, fields, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
import logging
_logger = logging.getLogger(__name__)

class WizardHospitalisationClosed(models.TransientModel):
    """ Wizard qui permet de determiner si la cloture du dossier 
        d'hospitalisation est totale ou partielle et d'en preciser
        la période si c'est partielle ."""

    _name = 'hospitalisation.wizard.closed'
    _description = 'Cloture dossier Hospitalisation'

    closing_type = fields.Selection([('partiel','Partielle'),('complete','Complete')], required=True, string="Type de cloture")
    date_start = fields.Date(string="Date debut")
    date_sorti = fields.Datetime(string="Date de sortie")
    date_end = fields.Date(string="Date de fin")
    hospi_id = fields.Many2one('module.hospitalisation', string="Hospitalisation")
    is_facturable = fields.Boolean(string="Creer une facture", default=False)

    
    
    def action_closing_hospifolder(self):
        #self.internal_status = 'open'
        ## Check la categorie pour placer dans le journal qui convient
        journal_id = self.env['ksoft.appointment'].get_journal_type(self.hospi_id.categorie)
        sejour = self.hospi_id.calcul_sejour(self.hospi_id.date_entree, self.date_sorti)
        imagerie_ids = self.hospi_id.hospi_examen_id.imagerie_ids.filtered(lambda imagerie: imagerie.status == 'done' and imagerie.etat_facturation == False)
        labo_ids = self.hospi_id.hospi_examen_id.labo_ids.filtered(lambda labo: labo.status == 'done' and labo.etat_facturation == False)
        actes_ids = self.hospi_id.hospi_actes_fact.filtered(lambda actes: actes.internal_status == 'draft')
        materiels_ids = self.hospi_id.hospi_materiel_fact.filtered(lambda materiels: materiels.internal_status == 'draft')
        medicaments_ids = self.hospi_id.hospi_medic_fact.filtered(lambda medicaments: medicaments.internal_status == 'draft')
        
        if actes_ids or materiels_ids or medicaments_ids:
            
            #if self.hospi_id:
            _logger.info("#################### Sejour hospi : %s", sejour)
            lines = [ (0,0,{'display_type':'line_section', 'name':'Hospitalisation: Sejour', 'debit':0, 'credit':0, 'account_id':False})]
            #lines.append[(0,False,{'product_id': , 'price_unit': , 'quantity': })]
            lines.extend(self.mapped(lambda x :(0, 0, {
                            'product_id': self.env['product.product'].search([('product_tmpl_id', '=', x.hospi_id.lit.chambre_id.id)]).id,
                            'price_unit': x.hospi_id.lit.chambre_id.list_price, 
                            'quantity': sejour})))
                            
            lines.append((0,0,{'display_type':'line_section', 'name':'Hospitalisation: Imagerie', 'debit':0, 'credit':0, 'account_id':False}))
            lines.extend( imagerie_ids.mapped(lambda imagerie : (0,0,{ 'product_id': imagerie.analyse.id, 'price_unit': imagerie.analyse.list_price, 'quantity':1, 'ref_item':imagerie.imagerie_name, })) )
            
            lines.append((0,0,{'display_type':'line_section', 'name':'Hospitalisation: Laboratoire', 'debit':0, 'credit':0, 'account_id':False}))
            lines.extend( labo_ids.mapped(lambda labo : (0,0,{ 'product_id': labo.analyse.id, 'price_unit': labo.analyse.list_price, 'quantity':1, 'ref_item':labo.labo_name, })) )
            
            lines.append((0,0,{'display_type':'line_section', 'name':'Hospitalisation: Actes', 'debit':0, 'credit':0, 'account_id':False}))
            lines.extend( actes_ids.mapped(lambda acte : (0,0,{'product_id':self.env['product.product'].search([('product_tmpl_id', '=', acte.actes.id)]).id, 'price_unit': acte.actes.list_price, 'quantity':acte.qtity})) )

            lines.append( (0,0,{'display_type':'line_section', 'name':'Hospitalisation: Materiels', 'debit':0, 'credit':0, 'account_id':False}) )
            lines.extend( materiels_ids.mapped(lambda materiel : (0,0,{'product_id':self.env['product.product'].search([('product_tmpl_id', '=', materiel.produit.id)]).id, 'price_unit': materiel.produit.list_price, 'quantity':materiel.qtity})) )

            lines.append( (0,0,{'display_type':'line_section', 'name':'Hospitalisation: Médicaments', 'debit':0, 'credit':0, 'account_id':False}) )
            lines.extend( medicaments_ids.mapped(lambda medicament : (0,0,{'product_id':self.env['product.product'].search([('product_tmpl_id', '=', medicament.produit.id)]).id , 'price_unit': medicament.produit.list_price, 'quantity':medicament.qtity })) )

            #raise UserError(_(lines))
            libelle = ""
            if self.hospi_id.type_service == 'hospi':
                libelle = 'hospi'
            elif self.hospi_id.type_service == 'urg':
                libelle = 'urgence'
            elif self.hospi_id.type_service == 'rea':
                libelle = 'reanimation'
            elif self.hospi_id.type_service == 'soins':
                libelle = 'soins'
            else:
                libelle = 'autres'
            
            
            move_id = self.env['account.move'].create({
                'move_type':'out_invoice',

                'journal_id': journal_id,
                'patient_id': self.hospi_id.patient_id.id,
                'numero_billet': self.hospi_id.numero_billet,
                    
                'convention_id': self.hospi_id.parent_id.id,
                'matricule': self.hospi_id.matricule,
                'categorie': self.hospi_id.categorie,
                'classe': self.hospi_id.classe,
                
                'libelle':libelle,

                'partner_id':self.hospi_id.patient_id.partner_id.id,
                'ref':self.hospi_id.hospi_name   })
                
            move_id.write({'invoice_line_ids':lines})

            
            if len(move_id) > 0:
                actes_ids.write({'internal_status':'compta','invoice_ref':move_id.name})
                materiels_ids.write({'internal_status':'compta','invoice_ref':move_id.name})
                medicaments_ids.write({'internal_status':'compta','invoice_ref':move_id.name})
                imagerie_ids.write({'move_id': move_id.id,})
                labo_ids.write({'move_id': move_id.id,})
                self.hospi_id.write({'state':'invoiced','state_ambul':'invoiced'})
        else:

            raise UserError(_('Aucun éléments à facturer'))




class WizardImagerieHospi(models.TransientModel):
    """Wizard pour demande examen imagerie."""

    _inherit = 'fertility.wizard.imagerie'
    _description = 'Wizard Hospitalisation'

    hospi_id = fields.Many2one('module.hospitalisation')

    def button_draft(self):
        res = super().button_draft()
        self.is_prelever = False
        for line in self.invoice_line_ids.filtered(lambda ligne:ligne.etat):
            line.etat = False
        obj_frais_info = self.env['frais.informatique'].search([('num_fac','=',self.name)])
        obj_frais_info.unlink()

    def action_create(self):
        _logger.info(self._context) 
        res = super().action_create()
        if self.hospi_id :
            if self.product_ids:
                product_ids = self.product_ids.mapped(lambda product_id : (0,0,{'analyse':product_id.id}) )
                self.hospi_id.hospi_examen_id.write({'imagerie_ids':product_ids})
            if self.product_labo_ids:
                product_labo_ids = self.product_labo_ids.mapped(lambda product_id : (0,0,{'analyse':product_id.id}) )
                self.hospi_id.hospi_examen_id.write({'labo_ids':product_labo_ids})


        



    


