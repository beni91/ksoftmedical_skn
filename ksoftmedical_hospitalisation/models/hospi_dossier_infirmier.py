# -*- coding: utf-8 -*-
#
# Auteur : BKM
# Date   : 11 Avril 22
################################
from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
import logging
_logger = logging.getLogger(__name__)


class HospitalisationModule(models.Model):
    _inherit = 'module.hospitalisation'
    _description = 'Hospitalisation'

    # Surveillance Infirmieres
    hospi_surveillance = fields.One2many('module.feuille.surveillance', 'surveillance_hospi', string="Surveillance")
    # Evolutions Infirmieres
    hospi_evolution_inf = fields.One2many('module.evolutions.infirmiers', 'evolution_inf_hospi', string="Observations Infirmieres")
    # Traitement
    hospi_traitement_inf = fields.One2many('module.feuille.traitement', 'traitement_inf_hospi', string="Plan de traitement")
    # Fiche des stocks
    hospi_stock_inf = fields.One2many('module.fiche.stock', 'fiche_stock_hospi', string="Fiche de stock")
    # Facturation des actes en hospitalisation
    hospi_actes_fact = fields.One2many('module.facturation.actes', 'fact_actes_hospi', string="Facturation des Actes")
    # Facturation des medicaments en hospitalisation
    hospi_medic_fact = fields.One2many('module.facturation.medicament', 'fact_produit_hospi', string="Facturation des Medicaments")
    # Facturation des materiels en hospitalisation
    hospi_materiel_fact = fields.One2many('module.facturation.materiels', 'fact_materiels_hospi', string="Facturation des Materiels")


    

class SurveillanceInfHospitalisation(models.Model):
    """ Gestion de la surveillance infirmiere dans le circuit hospitalisation"""

    _inherit = 'module.feuille.surveillance'

    surveillance_hospi = fields.Many2one('module.hospitalisation', string="Hospitalisation")


class EvolutionInfirmierHospitalisation(models.Model):
    """ Gestion des evolutions infirmieres dans le circuit hospitalisation"""

    _inherit = 'module.evolutions.infirmiers'

    evolution_inf_hospi = fields.Many2one('module.hospitalisation', string="Hospitalisation")

class FicheStockHospitalisation(models.Model):
    """ Gestion de la fiche de stock dans le circuit hospitalisation"""

    _inherit = 'module.fiche.stock'

    fiche_stock_hospi = fields.Many2one('module.hospitalisation', string="Hospitalisation")


"""
    Objet de facturation
"""
class FacturationDeActesHospitalisation(models.Model):
    """ Gestion de la facturation des actes en Hospitalisation """

    _inherit = 'module.facturation.actes'

    fact_actes_hospi = fields.Many2one('module.hospitalisation', string="Hospitalisation")

 

class FacturationDeMedicHospitalisation(models.Model):
    """ Gestion de la facturation des medicaments en Hospitalisation """

    _inherit = 'module.facturation.medicament'
    
    fact_produit_hospi = fields.Many2one('module.hospitalisation', string="Hospitalisation")


class FacturationDeMaterielHospitalisation(models.Model):
    """ Gestion de la facturation des materiels en Hospitalisation """

    _inherit = 'module.facturation.materiels'
    
    fact_materiels_hospi = fields.Many2one('module.hospitalisation', string="Hospitalisation")

 


class PlanTraitementHospitalisation(models.Model):
    """ Gestion du plan de traitement infirmieres dans le circuit hospitalisation"""

    _inherit = 'module.feuille.traitement'

    traitement_inf_hospi = fields.Many2one('module.hospitalisation', string="Hospitalisation")
    
    def confirm_traitement_soins(self):
        fiche_stock = {}
        for soins in self:
            #if soins.internal_status == 'done':
            #if soins.nbre_occurence_rea > 0 and soins.produit_perso == False:
            soins.internal_status = 'done'

            return True
            
    #@api.onchange('is_valider')
    def confirm_traitement(self):
        fiche_stock = {}
        for soins in self:
            #if soins.internal_status == 'done':
            if soins.nbre_occurence_rea > 0 and soins.produit_perso == False:
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
                            
                soins.internal_status = 'done'
            else:
                soins.internal_status = 'done'

            return True



