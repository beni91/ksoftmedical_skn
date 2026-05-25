# -*- coding: utf-8 -*-
#
# Auteur : BKM
# Date   : 11 Avril 22
################################
from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
import logging
_logger = logging.getLogger(__name__)

    
class PmaTraitementInfirmier(models.Model):
    _inherit = 'fertility.pma'
    _description = 'PMA'

    # Surveillance Infirmieres
    pma_surveillance = fields.One2many('module.feuille.surveillance', 'surveillance_pma', string="Surveillance")
    # Evolutions Infirmieres
    pma_evolution_inf = fields.One2many('module.evolutions.infirmiers', 'evolution_inf_pma', string="Observations Infirmieres")
    # Traitement
    pma_traitement_inf = fields.One2many('module.feuille.traitement', 'traitement_inf_pma', string="Plan de traitement")
    
    # Traitement 2
    pma_traitement_inf2 = fields.One2many('module.feuille.traitement', 'traitement_inf_pma2', string="Plan de traitement")
    # Fiche des stocks
    pma_stock_inf = fields.One2many('module.fiche.stock', 'fiche_stock_pma', string="Fiche de stock")
    # Observation médicales
    pma_evolution = fields.One2many('module.evolutions.medicaux', 'evolution_med_pma', string="Evolutions Médicales")
    # Facturation des actes en hospitalisation
    # # hospi_actes_fact = fields.One2many('module.facturation.actes', 'fact_actes_hospi', string="Facturation des Actes")
    # Facturation des medicaments en hospitalisation
    # # hospi_medic_fact = fields.One2many('module.facturation.medicament', 'fact_produit_hospi', string="Facturation des Medicaments")
    # Facturation des materiels en hospitalisation
    # # hospi_materiel_fact = fields.One2many('module.facturation.materiels', 'fact_materiels_hospi', string="Facturation des Materiels")


    
class SurveillanceInfPMA(models.Model):
    """ Gestion de la surveillance infirmiere dans le circuit hospitalisation"""

    _inherit = 'module.feuille.surveillance'

    surveillance_pma = fields.Many2one('fertility.pma', string="PMA")


class EvolutionInfirmierPMA(models.Model):
    """ Gestion des evolutions infirmieres dans le circuit hospitalisation"""

    _inherit = 'module.evolutions.infirmiers'

    evolution_inf_pma = fields.Many2one('fertility.pma', string="PMA")

class FicheStockPMA(models.Model):
    """ Gestion de la fiche de stock dans le circuit hospitalisation"""

    _inherit = 'module.fiche.stock'

    fiche_stock_pma = fields.Many2one('fertility.pma', string="PMA")
    
class ActesMedicauxPMA(models.Model):
    """ Gestion des actes médicaux dans le circuit hospitalisation"""

    _inherit = 'module.evolutions.medicaux'

    evolution_med_pma = fields.Many2one('fertility.pma', string="PMA")

    @api.model
    def create(self, vals):
        vals['origine'] = "Stimulation PMA"
        
        return super(ActesMedicauxPMA, self).create(vals)
        ##raise UserError(_(obj_doctors))



# """
    # Objet de facturation
# """
# class FacturationDeActesHospitalisation(models.Model):
    # """ Gestion de la facturation des actes en Hospitalisation """

    # _inherit = 'module.facturation.actes'

    # fact_actes_hospi = fields.Many2one('module.hospitalisation', string="PMA")

 

# class FacturationDeMedicPMA(models.Model):
    # """ Gestion de la facturation des medicaments en Hospitalisation """

    # _inherit = 'module.facturation.medicament'
    
    # fact_produit_pma = fields.Many2one('module.hospitalisation', string="PMA")


# class FacturationDeMaterielPMA(models.Model):
    # """ Gestion de la facturation des materiels en Hospitalisation """

    # _inherit = 'module.facturation.materiels'
    
    # fact_materiels_pma = fields.Many2one('module.hospitalisation', string="PMA")

 


class PlanTraitementPMA(models.Model):
    """ Gestion du plan de traitement infirmieres dans le circuit hospitalisation"""

    _inherit = 'module.feuille.traitement'

    traitement_inf_pma = fields.Many2one('fertility.pma', string="PMA")
    traitement_inf_pma2 = fields.Many2one('fertility.pma', string="PMA")
    
    #@api.onchange('is_valider')
    def confirm_traitement(self):
        fiche_stock = {}
        for soins in self:
            #if soins.internal_status == 'done':
            if soins.nbre_occurence_rea > 0 and soins.produit_perso != True:
                #raise UserError(_("Ce Traitement est déjà validé")) 
                #else:
                #   if  soins.nbre_occurence_rea > 0
                if soins.produit:
                    ## Remplissage fiche de stock
                    self.env['module.fiche.stock'].create({
                            'patient_id':soins.traitement_inf_hospi.patient_id.id,
                            'fiche_stock_hospi':soins.traitement_inf_hospi.id,
                            'date_consommation':soins.date_traitement,
                            'infirmier':soins.infirmier.id,
                            'produit':soins.produit.id,
                            'origine':'hospi',
                            'qtity':soins.nbre_occurence_rea,
                            'internal_status':'draft'
                        })


                    ## Remplissage des produits dans la feuille de facturation
                    self.env['module.facturation.medicament'].create({
                            'patient_id':soins.traitement_inf_hospi.patient_id.id,
                            'fact_produit_hospi':soins.traitement_inf_hospi.id,
                            'date_realisation':soins.date_traitement,
                            'infirmier':soins.infirmier.id,
                            'produit':soins.produit.id,
                            'origine':'hospi',
                            'qtity':soins.nbre_occurence_rea,
                            'internal_status':'draft'
                        })

                elif soins.actes_medicaux:

                    ## Remplissage des actes dans la feuille de facturation
                    self.env['module.facturation.actes'].create({
                            'patient_id':soins.traitement_inf_hospi.patient_id.id,
                            'fact_actes_hospi':soins.traitement_inf_hospi.id,
                            'date_realisation':soins.date_traitement,
                            'infirmier':soins.infirmier.id,
                            'actes':soins.actes_medicaux.id,
                            'origine':'hospi',
                            'qtity':soins.nbre_occurence_rea,
                            'internal_status':'draft'
                        })

                    if soins.materiels:
                        for materiel in soins.materiels:
                            # Creation de la fiche des stock 
                            fiche_stock = {
                                'patient_id':soins.traitement_inf_hospi.patient_id.id,
                                'fiche_stock_hospi':soins.traitement_inf_hospi.id,
                                'date_consommation':soins.date_traitement,
                                'infirmier':soins.infirmier.id,
                                'produit':materiel.id,
                                'origine':'hospi',
                                'qtity':soins.nbre_occurence_rea,
                                'internal_status':'draft'
                            }
                            self.env['module.fiche.stock'].create(fiche_stock)

                            # Creation de la ligne des matériels à facturer
                            self.env['module.facturation.materiels'].create({
                                'patient_id':soins.traitement_inf_hospi.patient_id.id,
                                'fact_materiels_hospi':soins.traitement_inf_hospi.id,
                                'date_realisation':soins.date_traitement,
                                'infirmier':soins.infirmier.id,
                                'produit':materiel.id,
                                'origine':'hospi',
                                'qtity':soins.nbre_occurence_rea,
                                'internal_status':'draft'
                            })

                #else:
                soins.internal_status = 'done'

            return True
            
            #raise UserError(_(soins.materiels)) 



