# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
import logging

_logger = logging.getLogger(__name__)


class BlocOperatoire(models.Model):
    """" Ici on crée le modèle bloc operatoire   """
    _name = "module.blocoperatoire"
    _description = "Bloc Opératoire"
    _order = 'date_intervention desc' 

    bloc_name = fields.Char(string='ID Bloc')
    # Info patient
    patient_id = fields.Many2one('fertility.patient',required=True, string="Patient")
    nompatient = fields.Char(related='patient_id.nom', string="Nom")
    pnompatient = fields.Char(related='patient_id.postnom', string="Postnom")
    prnompatient = fields.Char(related='patient_id.prenom', string="Prenom")
    age = fields.Integer(related='patient_id.age', string='Age', readonly=True)
    dob = fields.Date(related='patient_id.birth', string='Date Naiss', readonly=True)
    sex = fields.Selection([('m', 'M'), ('f', 'F')], related='patient_id.gender', string="Sex")
    categorie = fields.Selection(related='patient_id.categorie', string='Catégorie', readonly=True)
    convention = fields.Many2one(related='patient_id.parent_id', string="Convention")

    # Info Chrirugien
    doctor = fields.Many2one('fertility.doctor', string='Chirurgien')
    assistant_doctor = fields.Many2many('fertility.doctor', string="Assistant Médecin")
    infirmiers = fields.Many2many('res.users', string="Infirmiers")

    # Info intervention
    date_intervention = fields.Date(string="Date Intervention")
    heure_intervention = fields.Char(string="Heure prevue")
    heure_debut = fields.Char(string="Heure de debut")
    heure_fin = fields.Char(string="Heure de fin")

    actes = fields.Many2one('product.template', string='Actes Chirurgical', required=True)

    diagnostic_pre = fields.Html(size=64, string='Diagnostic Pré-Opératoire')
    diagnostic_post = fields.Html(size=64, string='Diagnostic Post-Opératoire')
    incident = fields.Html(string='Incident per Operatoire')
    traitement = fields.Html(string="Plan de traitement")
    
    #info anesthesie
    type_anesthesie = fields.Selection([('gen', 'Général'), ('local', 'Local')], string="Type Anesthésie")
    type_planification = fields.Selection([('normal', 'Normal'), ('autres', 'Autres')], string="Type planification")

    # Anamnèse Infirmiere
    disponibilite = fields.Selection([('oui', 'O'), ('non', 'N'), ('na', 'N.A')], string="Disponibilite")
    proprete = fields.Selection([('oui', 'O'), ('non', 'N'), ('na', 'N.A')], string="Proprete")
    accueil = fields.Selection([('oui', 'O'), ('non', 'N'), ('na', 'N.A')], string="Accueil")
    parametres = fields.Selection([('oui', 'O'), ('non', 'N'), ('na', 'N.A')], string="Parametres")
    rasage = fields.Selection([('oui', 'O'), ('non', 'N'), ('na', 'N.A')], string="Rasage")
    douche = fields.Selection([('oui', 'O'), ('non', 'N'), ('na', 'N.A')], string="Douche")
    administrer = fields.Selection([('oui', 'O'), ('non', 'N'), ('na', 'N.A')], string="Administrer")
    informer = fields.Selection([('oui', 'O'), ('non', 'N'), ('na', 'N.A')], string="Informer")
    information = fields.Selection([('oui', 'O'), ('non', 'N'), ('na', 'N.A')], string="Informations")
    # Jour de l'intervention
    reveil = fields.Selection([('oui', 'O'), ('non', 'N'), ('na', 'N.A')], string="Reveil")
    douchepreop = fields.Selection([('oui', 'O'), ('non', 'N'), ('na', 'N.A')], string="Douche preoperatoire")
    blouse = fields.Selection([('oui', 'O'), ('non', 'N'), ('na', 'N.A')], string="Blouse")
    jeune = fields.Selection([('oui', 'O'), ('non', 'N'), ('na', 'N.A')], string="Jeune patient")
    premedication = fields.Selection([('oui', 'O'), ('non', 'N'), ('na', 'N.A')], string="Administrer la premedication")
    changement = fields.Selection([('oui', 'O'), ('non', 'N'), ('na', 'N.A')], string="Changement")
    user_id = fields.Many2one('res.users', string="Par:")

    # Anamnese Infirmier
    # informations generales
    motif = fields.Text(string="Motif d'Hospitalisation")
    accompagnant = fields.Char(string="Accompagnant")

    # informations medicales
    antecedent_id = fields.Many2one('patient_id.antecedent_id', required=False, ondelete="cascade")

    ## besoins fondamentaux
    respirer = fields.Selection([('1a', 'Sans gêne'),
                                 ('2a', 'Toux sèche'),
                                 ('3a', 'Toux productive'),
                                 ('4a', 'Dyspnée au repos et/ou à l\'effort'),
                                 ('5a', 'Utilisation appareillages (cpap, extracteur,..')], string="Respirer")
    boire = fields.Selection([('1b', 'Mange seul'), ('2b', 'Installation et/ou stimulation'),
                              ('3b', 'Aide partielle'), ('4b', 'Aide complète'),
                              ('5b', 'Appareilles (SNG, Gastrostomie, Jéjunostomie)')],
                             string="Boire et manger")
    eliminer = fields.Selection([('1c', 'Continence'), ('2c', 'Soutien logistique(urinal,panne)'),
                                 ('3c', 'Aide partielle'), ('4c', 'Incontinence diurne'),
                                 ('5c', 'Incontinence nocture'), ('6c', 'Incontinence complète'),
                                 ('7c', 'Appareillage(Stomies, SVD, ...)'), ], string="Eliminer")
    mouvoir = fields.Selection([('1t', 'Se déplacer seul'), ('2t', 'Se déplace avec canne (Canne, ou une personne)'),
                                ('3t', 'Aide complète (Porter)')], string="Se mouvoir")
    etre_propre = fields.Selection([('1d', 'Se lave seul'), ('2d', 'Se lave seul doit être stimulé'),
                                    ('3d', 'Aide partielle'), ('4d', 'Aide complète')], string="Etre propre")
    eviter_dangers = fields.Selection([('1e', 'Lucide'), ('2e', 'Confus et/ou desorienté épisodiquement'),
                                       ('3e', 'Confus et/ou désorienté en permence'),
                                       ('4e', 'Dangereux pour lui-même et pour les autres')], string="Etre propre")
    communiquer = fields.Selection([('1f', 'S\'exprimer sans difficulté'), ('2f', 'S\'exprime avec difficulté'),
                                    ('3f', 'Besoin d\'aide (interprète)'),
                                    ('4f', 'Ne peut pas s\'exprimer (asphasie)'), ('5f', 'Ne veut pas s\'exprimer')],
                                   string="Eviter les dangers")
    apprendre = fields.Selection([('1g', 'Se prend en charge'), ('2g', 'A besoin de stimulation'),
                                  ('3g', 'Apathique'), ('4g', 'Refus ou résignation')], string="Communiquer")
    dormir = fields.Selection([('1i', 'Dort naturellement'), ('2i', 'Dort avec aide (médicament)'),
                               ('3i', 'Réveils fréquents'), ('4i', 'Insomnies fréquentes')],
                              string="Dormir et se reposer")

    # Compte Rendu Bloc Operatoire
    compte_rendu = fields.Html(string='Compte Rendu')
    instruction_postop = fields.Html(string='Instruction Post-Operatoire')

    state = fields.Selection([('confirme', 'Confirmer'), ('finish', 'Terminer'),
                              ('canced', 'Annuler')],
                            default="confirme", string="Etat")
                            
                            
    ## Hospitalisation
    bloc_hospi = fields.Many2one('module.hospitalisation', string="Hospitalisation")

    ## Fiche de stock
    bloc_fiche_stock = fields.One2many('module.fiche.stock', 'fiche_stock_bloc', string="Fiche de stock")

    ## Facturation des actes
    bloc_fact_actes = fields.One2many('module.facturation.actes', 'fact_actes_bloc', string="Fiche de stock")

    ## Facturation des materiels 
    bloc_fact_materiels = fields.One2many('module.facturation.materiels', 'fact_materiels_bloc', string="Fiche de stock")

    ## Facturation des medicaments
    bloc_fact_produits = fields.One2many('module.facturation.medicament', 'fact_produit_bloc', string="Fiche de stock")


    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, "%s " % (rec.patient_id)))
        return result


    @api.model
    def create(self, vals):
        ID_bloc = self.env['ir.sequence'].next_by_code('module.blocoperatoire.name')
        vals['bloc_name'] = self.env['ir.sequence'].next_by_code('module.blocoperatoire.name')
        return super(BlocOperatoire, self).create(vals)
        
    def get_document(self):
        raise UserError(_("Module en construction"))
        


class BlocHospitalisation(models.Model):
    """ Gestion des activités du bloc operatoire dans le circuit hospitalisation"""

    _inherit = 'module.hospitalisation'

    hospi_bloc = fields.One2many('module.blocoperatoire', 'bloc_hospi', string="Bloc Opératoire")


class BlocFicheDeStock(models.Model):
    """ Gestion de la fiche de stock au bloc operatoire"""

    _inherit = 'module.fiche.stock'

    fiche_stock_bloc = fields.Many2one('module.blocoperatoire', string="Bloc Opératoire")


"""
    Objet de facturation
"""
class FacturationDeActesBloc(models.Model):
    """ Gestion de la facturation des actes en bloc Operatoire """

    _inherit = 'module.facturation.actes'

    fact_actes_bloc = fields.Many2one('module.blocoperatoire', string="Bloc Opératoire")

 

class FacturationDeMedicBloc(models.Model):
    """ Gestion de la facturation des medicaments en bloc Operatoire """

    _inherit = 'module.facturation.medicament'
    
    fact_produit_bloc = fields.Many2one('module.blocoperatoire', string="Bloc Opératoire")


class FacturationDeMaterielBloc(models.Model):
    """ Gestion de la facturation des materiels en bloc Operatoire """

    _inherit = 'module.facturation.materiels'
    
    fact_materiels_bloc = fields.Many2one('module.blocoperatoire', string="Bloc Opératoire")
