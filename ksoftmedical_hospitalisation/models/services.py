# -*- coding: utf-8 -*-
#
# Auteur : BKM
# Date   : 11 Avril 22
################################
from odoo import api, fields, models, _
from datetime import datetime, date, timedelta
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
import logging
_logger = logging.getLogger(__name__)



mode_admission = [
                    ('iv', 'I.V'), ('im', 'I.M'),
                    ('sc', 'S.C'), ('peros', 'Peros'),
                    ('ir', 'I.R')
                ]

class PrescriptionModule(models.Model):
    """ Gestion des Prescriptions médicales dans le circuit hospitalisation"""

    _name = 'module.prescription'
    _description = 'Prescription Médicale'
    _order = 'date_prescription desc, id desc'

    pres_name = fields.Char(string="ID Prescr")
    patient_id = fields.Many2one('fertility.patient', string='Patient')
    nompatient = fields.Char(related='patient_id.nom', string="Nom")
    pnompatient = fields.Char(related='patient_id.postnom', string="Postnom")
    prnompatient = fields.Char(related='patient_id.prenom', string="Prenom")
    dob = fields.Date(related='patient_id.birth', string='Date Naiss', readonly=True, )
    sex = fields.Selection([('m', 'Masculin'), ('f', 'Féminin')], string='Sexe', readonly=True)
    rh = fields.Char(size=64, string='Rhésus', readonly=True)
    age = fields.Integer(related='patient_id.age', string='Age', readonly=True)
    date_prescription = fields.Datetime(string='Date', readonly=True, default=fields.Datetime.now())
    medecin = fields.Many2one('fertility.doctor', readonly=True, string="Médecin")
    internal_status = fields.Selection([('draft', 'Brouillon'), ('valid', 'Realiser'),
                                        ('invoicing', 'Facturer'),('canced', 'Annuler')],
                                      default='draft', string='Status')
    origine = fields.Char(string="Origine")
    description = fields.Char(string="Posologie")
    medicament = fields.Many2one('product.product', string="Produits")
    autre_produits = fields.Char(string="Autres Produits")
    is_print = fields.Boolean(string="#", default=False)

    @api.model
    def create(self, vals):
        obj_doctors = self.env['fertility.doctor'].search([('user_id', '=', self.env.uid)])
        if obj_doctors is not None:
            for doctor in obj_doctors:
                vals['medecin'] = doctor.id
        return super(PrescriptionModule, self).create(vals)

    @api.model
    def write(self, vals):
        return super(PrescriptionModule, self).write(vals)

    def unlink(self):
        #self.ensure_one()

        return super(PrescriptionModule, self).unlink()


class ActesMedicauxModule(models.Model):
    """ Gestion des Actes Medicaux """

    _name = 'module.actes.medicaux'
    _description = 'Actes Médicales'
    _order = 'date_actes desc'

    actes_name = fields.Char(string="ID Actes")
    patient_id = fields.Many2one('fertility.patient', string='Patient')
    nompatient = fields.Char(related='patient_id.nom', string="Nom")
    pnompatient = fields.Char(related='patient_id.postnom', string="Postnom")
    prnompatient = fields.Char(related='patient_id.prenom', string="Prenom")
    dob = fields.Date(related='patient_id.birth', string='Date Naiss', readonly=True, )
    sex = fields.Selection([('m', 'Masculin'), ('f', 'Féminin')], string='Sexe', readonly=True)
    rh = fields.Char(size=64, string='Rhésus', readonly=True)
    age = fields.Integer(related='patient_id.age', string='Age', readonly=True)
    date_actes = fields.Date(string='Date', readonly=True, default=fields.Datetime.now())
    medecin = fields.Many2one('fertility.doctor', readonly=True, string="Médecin")
    internal_status = fields.Selection([('draft', 'Brouillon'), ('valid', 'Realiser'),
                                        ('invoicing', 'Facturer'),('canced', 'Annuler')],
                                      default='draft', string='Status')
    origine = fields.Char(string="Origine")
    description = fields.Char(string="Description")
    type_analyse = fields.Many2one('product.category', string="Type d'analyse")
    actes_medicaux = fields.Many2one('product.template', string='Actes Médicaux', required=True)
    price_unit = fields.Float(string='Unit Price', digits='Product Price')
    is_print = fields.Boolean(string="#", default=True)

    @api.model
    def create(self, vals):
        obj_doctors = self.env['fertility.doctor'].search([('user_id', '=', self.env.uid)])
        if obj_doctors is not None:
            for doctor in obj_doctors:
                vals['medecin'] = doctor.id
        return super(ActesMedicauxModule, self).create(vals)

   
    def write(self, vals):
        return super(ActesMedicauxModule, self).write(vals)

    @api.onchange('actes_medicaux')
    def get_price_actes(self):
        for actes in self:
            self.price_unit = self.actes_medicaux.list_price

    def unlink(self):
        return super(ActesMedicauxModule, self).unlink()


class EvolutionMedicalModule(models.Model):
    """ Gestion des Evolutions Medicales """

    _name = 'module.evolutions.medicaux'
    _description = 'Evolutions Médicales'
    _order = 'date_evolution desc, id desc'

    evolution_name = fields.Char(string="ID Actes")
    patient_id = fields.Many2one('fertility.patient', string='Patient')
    nompatient = fields.Char(related='patient_id.nom', string="Nom")
    pnompatient = fields.Char(related='patient_id.postnom', string="Postnom")
    prnompatient = fields.Char(related='patient_id.prenom', string="Prenom")
    dob = fields.Date(related='patient_id.birth', string='Date Naiss', readonly=True, )
    sex = fields.Selection([('m', 'Masculin'), ('f', 'Féminin')], string='Sexe', readonly=True)

    age = fields.Integer(related='patient_id.age', string='Age', readonly=True)
    date_evolution = fields.Datetime(string='Date', readonly=False, default=fields.Datetime.now())

    medecin = fields.Many2one('fertility.doctor', readonly=True, string="Médecin")
    internal_status = fields.Selection([('draft', 'Brouillon'),('deleted', 'Supprimer')],
                                       default='draft', string='Status')
    origine = fields.Char(string="Origine")
    evolution = fields.Html(string="Observations Médicales", required=True)
    is_print = fields.Boolean(string="#", default=True)

    @api.model
    def create(self, vals):
        obj_doctors = self.env['fertility.doctor'].search([('user_id', '=', self.env.uid)])
        if obj_doctors is not None:
            for doctor in obj_doctors:
                vals['medecin'] = doctor.id
        return super(EvolutionMedicalModule, self).create(vals)

   
    def write(self, vals):
        obj_doctors = self.env['fertility.doctor'].search([('user_id', '=', self.env.uid)])
        if obj_doctors is not None:
            for doctor in obj_doctors:
                if self.env['fertility.doctor'].browse(doctor.id).id == self.medecin.id:
                    return super(EvolutionMedicalModule, self).write(vals)
                else:
                    raise UserError(_("Vous ne pouvez modifier cette observation,"
                                      "seul %s peut modifier cette observation", self.medecin.name))
                return None

    def unlink(self):
        obj_doctors = self.env['fertility.doctor'].search([('user_id', '=', self.env.uid)])
        if obj_doctors is not None:
            for doctor in obj_doctors:

                if self.env['fertility.doctor'].browse(doctor.id).id == self.medecin.id:
                    _logger.info('############################ %s - %s ############', self.env['fertility.doctor'].browse(doctor.id).id,self.medecin.id)
                    #return super(EvolutionMedicalModule, self).unlink()
                    self.write({'internal_status': 'deleted'})
                else:
                    raise UserError(_("Vous ne pouvez supprimer cette observation,"
                                      "seul %s peut supprimer cette observation", self.medecin.name))
                return None

class EvolutionInfirmiersModule(models.Model):
    """ Gestion des Evolutions Infirmiers """

    _name = 'module.evolutions.infirmiers'
    _description = 'Evolutions Infirmiers'
    _order = 'date_evolution desc, id desc'

    evolution_name = fields.Char(string="ID Observation")
    patient_id = fields.Many2one('fertility.patient', string='Patient')
    nompatient = fields.Char(related='patient_id.nom', string="Nom")
    pnompatient = fields.Char(related='patient_id.postnom', string="Postnom")
    prnompatient = fields.Char(related='patient_id.prenom', string="Prenom")
    dob = fields.Date(related='patient_id.birth', string='Date Naiss', readonly=True, )
    sex = fields.Selection([('m', 'Masculin'), ('f', 'Féminin')], string='Sexe', readonly=True)

    age = fields.Integer(related='patient_id.age', string='Age', readonly=True)
    date_evolution = fields.Datetime(string='Date', readonly=False, default=fields.Datetime.now())

    infirmier = fields.Many2one('res.users', string="Infirmier",
                                default=lambda self: self.env.user, required=True)
    equipe = fields.Char(string="Equipe")
    evolution = fields.Html(string="Observations Médicales", required=True)
    internal_status = fields.Selection([('draft', 'Brouillon'),('deleted', 'Supprimer')],
                                       default='draft', string='Status')
    is_print = fields.Boolean(string="#", default=True)

    @api.model
    def create(self, vals):
        return super(EvolutionInfirmiersModule, self).create(vals)

   
    def write(self, vals):
        for evol in self:
            if self.env.uid == self.infirmier.id:
                return super(EvolutionInfirmiersModule, self).write(vals)
            else:
                raise UserError(_("Vous ne pouvez modifier cette observation,"
                                  "seul %s peut modifier cette observation", self.infirmier.name))
            return None

    def unlink(self):
        for evol in self:
            if self.env.uid == self.infirmier.id:
                #_logger.info('############################ %s - %s ############', self.env['fertility.doctor'].browse(doctor.id).id,self.medecin.id)
                #return super(EvolutionInfirmiersModule, self).unlink()
                self.write({'internal_status': 'deleted'})
            else:
                raise UserError(_("Vous ne pouvez supprimer cette observation,"
                                   "seul %s peut supprimer cette observation", self.infirmier.name))
            return None


class FeuilleDeSurveillanceModule(models.Model):
    """ Gestion de la feuille de surveillance  """

    _inherit = 'module.feuille.surveillance'
    _description = 'Feuille de surveillance Infirmieres'
    _order = 'date_surveillance desc, id desc'


    pad = fields.Integer(string="PAD")
    pas = fields.Integer(string="PAS")
    glascow = fields.Integer(string="Score de Glasgow")

    conscience = fields.Selection([('l','L'),('ob','OB'),('s','S')], string="Etat de Conscience")
    mvts = fields.Selection([('+','+'),('-','-')], string="Mouvement")
    vomissement = fields.Selection([('+','+'),('-','-')], string="Vomissement")
    qtity_vomi = fields.Float(string="Qtité Vomissement")
    diarhee = fields.Selection([('+','+'),('-','-')], string="Diarhée")
    qtity_diarhe = fields.Float(string="Qtité Diarhée")
    duirese = fields.Selection([('+','+'),('-','-')], string="Duirese")
    qtity_duirese = fields.Float(string="Qtité Duirese")
    pansement = fields.Selection([('+','+'),('-','-')], string="Pansement")
    aspect_pansement = fields.Char(string="Aspect Pansement")
    

    @api.model
    def create(self, vals):
        return super(FeuilleDeSurveillanceModule, self).create(vals)

  
    def write(self, vals):
        return super(FeuilleDeSurveillanceModule, self).write(vals)
 

    def unlink(self):
        return super(FeuilleDeSurveillanceModule, self).unlink()


class PlanDeSoinsModule(models.Model):
    """ Gestion de la feuille de traitement  """

    _name = 'module.feuille.traitement'
    _description = 'Feuille de traitement'
    _order = 'date_traitement desc, id desc'


    @api.depends('done_traitement.heure')
    def _get_plan_traitement(self):
        
        plan = ""
        for plans in self:
            plan += "<ul>" 
            for valeurs in plans.done_traitement:
                if valeurs.heure:
                    plan += '<li>'+ valeurs.heure +'</li>'
            plan += "</ul>" 
            plans.plan_traitement = plan 

    @api.depends('done_traitement.is_done','done_traitement.is_notdone')
    def _get_plan_realisation(self):
        
        plan = ""
        for plans in self:
            plan += "<ul>" 
            for valeurs in plans.done_traitement:
                if valeurs.is_done:
                    plan += '<li>'+ str(valeurs.heure_rea) +'==>'+ str(valeurs.infirmier_rea.display_name) +'</li>'
                    
                elif valeurs.is_notdone:
                    plan += '<li>'+ str(valeurs.heure) +'==> Not Fait</li>'
                    
            plan += "</ul>" 
            plans.plan_realisation = plan

    @api.depends('done_traitement.nbre_occurence')
    def _get_nbre_realisation(self):     
        nbre = 0
        for rea in self:
            for done in rea.done_traitement:
                if done.nbre_occurence == 1:
                    nbre += done.nbre_occurence
            rea.nbre_occurence_rea = nbre

           
    traitement_name = fields.Char(string="ID Traitement")
    patient_id = fields.Many2one('fertility.patient', string='Patient')
    nompatient = fields.Char(related='patient_id.nom', string="Nom")
    pnompatient = fields.Char(related='patient_id.postnom', string="Postnom")
    prnompatient = fields.Char(related='patient_id.prenom', string="Prenom")
    dob = fields.Date(related='patient_id.birth', string='Date Naiss', readonly=True, )
    sex = fields.Selection([('m', 'Masculin'), ('f', 'Féminin')], string='Sexe', readonly=True)
    age = fields.Integer(related='patient_id.age', string='Age', readonly=True)
    date_traitement = fields.Date(string='Date', readonly=False, default=fields.Datetime.now())
    is_closed = fields.Boolean(string="Terminer traitement")
    is_valider = fields.Boolean(string="Valider")
    infirmier = fields.Many2one('res.users', string="Infirmier",
                                default=lambda self: self.env.user)
    heure = fields.Char(string="Heure", required=False)
    internal_status = fields.Selection([('draft', 'En cours'),('done', 'Terminer')],
                                       default='draft', string='Status')
    # Plan de soins
    plan_traitement = fields. Html(string='Plan de Traitement', compute='_get_plan_traitement', store=True, readonly=False)
    plan_realisation = fields.Html(string="Plan de Réalisation", compute='_get_plan_realisation', store=True, readonly=False)
    posologie = fields.Text(string="Posologie")
    voie = fields.Selection([('iv', 'I.V'), ('im', 'I.M'),
                            ('sc', 'S.C'), ('peros', 'Peros'),
                            ('ir', 'I.R')], string='Voie')
    nbre_occurence = fields.Integer(string='Occurence', default=0)
    nbre_occurence_rea = fields.Integer(string='Nbre de realisation', default=0, compute='_get_nbre_realisation', store=True, readonly=True)
    remarque_occurence = fields.Char(string='Text Occurence')
    status_traitement = fields.Selection([('cours', 'En cours'), ('finish', 'Terminer')], string='Etat traitement', readonly=True)
    # Parametres vitaux
    produit = fields.Many2one('product.template', string="Produit")
    actes_medicaux = fields.Many2one('product.template', string="Actes Medicaux/Infirmiers")
    materiels = fields.Many2many('product.template', string="Materiels")
    medecin = fields.Many2one('fertility.doctor', string="Médecin")

    done_traitement = fields.One2many('module.feuille.traitement.donne','traitement_done', string="Traitement donné")
    is_print = fields.Boolean(string="#", default=True)
    
    ## Duplication facturation
    intervention_multiple = fields.Boolean(string="Duplication", default=False)
    nbre_jr = fields.Integer(string="Nbre de jours", default=1)
    produit_perso = fields.Boolean(string="Produit Personnel ?", default=False)
    
    @api.model
    def create(self, vals):
        return super(PlanDeSoinsModule, self).create(vals)

    @api.onchange('done_traitement.nbre_occurence')
    def _get_len_line(self):
        nbre = 0
        for traitemnt in self.done_traitement:
            nbre += traitemnt.nbre_occurence

        self.nbre_occurence_rea = nbre
        
    
    def duplication_traitement(self):
        for rec in self:
            ## Create les interventions par jour
            
            # Recupération de détails traitement
            details_taitement_ids = rec.done_traitement.filtered(lambda details: details.internal_status == 'draft')
            
            #raise UserError(_("##### %s", self.traitement_inf_hospi))
            #Recupération dans une liste des opérateurs à facturer
            #operateurs_ids =  rec.operateurs_lines.filtered(lambda operateur: operateur.status == 'attente')
            
            if rec.intervention_multiple == True and rec.nbre_jr > 1:
                compteur = 1
                start_date = rec.date_traitement
                nbre = rec.nbre_jr
                #compteur = rec.nbre_jr
                lines_matos = []
                lines_operateurs = []
                     
                while nbre > compteur:
                    lines_details = [(0, 0, {'heure': dtails.heure, 
                                        'infirmier': dtails.infirmier.id, 
                                        'heure_rea': dtails.heure_rea, 
                                        'infirmier_rea': dtails.infirmier_rea,
                                        'nbre_occurence':dtails.nbre_occurence,
                                        'internal_status':'draft',
                                        
                                        'traitement_done_hospi':rec.traitement_inf_hospi.id,
                                        'traitement_done':rec.id,
                                        'patient_id':rec.traitement_inf_hospi.patient_id.id,
                                        
                                    }) for dtails in rec.done_traitement] 
                
                    copy_id = rec.with_context({'from_copy':True}).copy({
                            'produit_perso':rec.produit_perso,
                            'produit':rec.produit.id,
                            'posologie':rec.posologie,
                            'voie':rec.voie,
                            'traitement_inf_hospi':rec.traitement_inf_hospi.id,
                            'actes_medicaux':rec.actes_medicaux,
                            'medecin':rec.medecin.id,
                            'date_traitement':rec.date_traitement + timedelta(days=compteur),
                            'done_traitement':lines_matos
                    })
                    #_logger.info("*************** bonjour Ness: %s - %s **********************",rec.id, copy_id)
                                
                        
                    # if len(copy_id.intervention_lines) > 0:
                        # for mt in copy_id.intervention_lines:
                            # if mt.product_id and mt.date_intervention:
                                # etat =  self.env['poc.reservation'].search([('date_intervention','=',mt.date_intervention),('materiels_id','=',mt.product_id.id)])

                                # if len(etat) > 0:
                                    # mt.write({'status_available':'undispo'})
                                # else:
                                    # mt.write({'status_available':'dispo'})
                                    
                    # self.reservation_ressources(rec.intervention_date + timedelta(days=compteur))
                    # self.action_send_mail()
                    
                    lines_matos = []
                    
                    compteur += 1
            else:
                raise UserError(_("Pas d'élément à dupliquer"))
                #operateurs_ids.write({'status':'attente'})
                #materiels_ids.write({'status':'in_consultation',})

                #self.reservation_ressources(rec.intervention_date)
                #self.action_send_mail()
            ## Envoyer des emails aux operatuers
            ## Gerer les statuts des operateurs
                ### Lancer l'alerte à l'opérateur
            #rec.state = 'conf'

    
    def write(self, vals):
        return super(PlanDeSoinsModule, self).write(vals)

    def unlink(self):
        return super(PlanDeSoinsModule, self).unlink()

    def launchTraitemnt(self):
        #self.internal_status = "draft"
        return {
            'name': _('Traitement realisé'),
            'res_model': 'module.feuille.traitement.donne',
            'view_mode': 'form',
            'context': {
                'default_patient_id': self.patient_id.id,
                'default_traitement_done':self.id,
                'default_traitement_inf_hospi':self.traitement_inf_hospi.id,
                'default_produit':self.produit.id,
                'active_id': self.ids[0],
                'active_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }


class PlanDeSoinsRealiserModule(models.Model):
    """ Gestion de traitement réalisé """

    _name = 'module.feuille.traitement.donne'
    _description = 'Feuille de traitement realise'
    _order = 'date_realisation desc'

    donetraitement_name = fields.Char(string="ID Traitement")
    patient_id = fields.Many2one('fertility.patient', string='Patient')
    nompatient = fields.Char(related='patient_id.nom', string="Nom")
    pnompatient = fields.Char(related='patient_id.postnom', string="Postnom")
    prnompatient = fields.Char(related='patient_id.prenom', string="Prenom")
    dob = fields.Date(related='patient_id.birth', string='Date Naiss', readonly=True, )
    sex = fields.Selection([('m', 'Masculin'), ('f', 'Féminin')], string='Sexe', readonly=True)
    age = fields.Integer(related='patient_id.age', string='Age', readonly=True)
    date_realisation = fields.Date(string='Date', readonly=True)
    
    infirmier = fields.Many2one('res.users', string="Planifié par:", readonly=True,
        default=lambda self:self.env.user)
    heure = fields.Char(string="Heure", required=True)
    heure_rea = fields.Char(string="Heure réalisée", required=False)
    internal_status = fields.Selection([('draft', 'En cours'),('done', 'Terminer')],
                                       default='draft', readonly=True, string='Status')
    infirmier_rea = fields.Many2one('res.users', string="Donné par:", readonly=False, store=True,)
   
    # Parametres vitaux
    produit = fields.Many2one('product.template', string="Produit")
    traitement_done_hospi = fields.Many2one('module.hospitalisation', string="Hospitalisation")
    traitement_done = fields.Many2one('module.feuille.traitement', string="Traitement donné")
    nbre_occurence = fields.Integer(string="Occurence Initial", readonly=False, store=True, default=0)
    nbre_occurence_reste = fields.Integer(string="Occurence realisé", readonly=False)

    done_traitement_details = fields.One2many('module.traitement.donne.details','traitement', string="Traitement donné")
    is_done = fields.Boolean(string="Fait", default=False)
    is_notdone = fields.Boolean(string="Non Fait", default=False)
    observation = fields.Text(string="Observ.")


    @api.model
    def create(self, vals):
        return super(PlanDeSoinsRealiserModule, self).create(vals)

    # @api.model
    def write(self, vals):
        return super(PlanDeSoinsRealiserModule, self).write(vals)
 
    def unlink(self):
        return super(PlanDeSoinsRealiserModule, self).unlink()

    @api.onchange('is_done')
    def change_state_done(self):
        if self.is_done == True:
            self.internal_status = 'done'
            self.infirmier_rea = self.env.user
            self.nbre_occurence = 1
            
        else:
            self.internal_status = 'draft'
            self.infirmier_rea = None
            self.nbre_occurence = 0
            
    @api.onchange('is_notdone')
    def change_state_notdone(self):
        if self.is_notdone == True:
            self.internal_status = 'done'
            self.infirmier_rea = self.env.user
            self.nbre_occurence = 0
            
        else:
            self.internal_status = 'draft'
            self.infirmier_rea = None
            self.nbre_occurence = 0
            
            

class PlanDetailerDeSoinsRealiserModule(models.Model):
    """ Gestion de traitement réalisé """

    _name = 'module.traitement.donne.details'
    _description = 'Details de la Feuille de traitement realise'
    _order = 'date_realisation desc'

    date_realisation = fields.Date(string='Date', readonly=True)
    
    infirmier = fields.Many2one('res.users', string="Planifié par:", readonly=True, default=lambda self:self.env.user)
    infirmier_rea = fields.Many2one('res.users', string="Donné par:", readonly=True)
    heure = fields.Char(string="Heure planifiée", required=True)
    heure_rea = fields.Char(string="Heure réalisée", required=False)
    internal_status = fields.Selection([('draft', 'En cours'),('done', 'Terminer')],
                                       default='draft', string='Status')
    is_done = fields.Boolean(string="Fait", default=False)
    # Plan de soins
    
    # Parametres vitaux
    traitement = fields.Many2one('module.feuille.traitement.donne', string="Traitement")
    active = fields.Boolean(string="Active", default=True)

    @api.model
    def create(self, vals):

        return super(PlanDetailerDeSoinsRealiserModule, self).create(vals)

    #@api.model
    def write(self, vals):
        return super(PlanDetailerDeSoinsRealiserModule, self).write(vals)
 
    def unlink(self):
        return super(PlanDetailerDeSoinsRealiserModule, self).unlink()

    @api.onchange('is_done')
    def change_state_done(self):
        if self.is_done == True:
            self.internal_status = 'done'
            self.infirmier_rea = self.env.user

        else:
            self.internal_status = 'draft'
            self.internal_status = False
 

class FicheDeStockModule(models.Model):
    """ Gestion de la fiche de stock  """

    _name = 'module.fiche.stock'
    _description = 'Fiche de stock'
    _order = 'date_consommation desc, id desc'

    stock_name = fields.Char(string="ID Traitement")
    patient_id = fields.Many2one('fertility.patient', string='Patient')
    nompatient = fields.Char(related='patient_id.nom', string="Nom")
    pnompatient = fields.Char(related='patient_id.postnom', string="Postnom")
    prnompatient = fields.Char(related='patient_id.prenom', string="Prenom")
    dob = fields.Date(related='patient_id.birth', string='Date Naiss', readonly=True, )
    sex = fields.Selection([('m', 'Masculin'), ('f', 'Féminin')], string='Sexe', readonly=True)
    age = fields.Integer(related='patient_id.age', string='Age', readonly=True)
    date_consommation = fields.Date(string='Date', readonly=True, default=fields.Datetime.now())
    is_closed = fields.Boolean(string="Terminer traitement")
    is_valider = fields.Boolean(string="Valider")
    infirmier = fields.Many2one('res.users', string="Infirmier",
                                default=lambda self: self.env.user)
    heure = fields.Char(string="Heure", required=False)
    internal_status = fields.Selection([('draft', 'Brouillon'),('done', 'Verrouiller')
                                        ,('compta', 'Comptabiliser'),('supprimer', 'Annuler')],
                                       default='draft', string='Status')

    # Parametres vitaux
    produit = fields.Many2one('product.template', string="Produit")
    categorie = fields.Many2one(related='produit.categ_id',string="Catégorie")
    qtity = fields.Integer(string="Quantité", default=1)

    service = fields.Char(string="Service")
    origine = fields.Selection([('hospi','Hospitalisation'),('urgence','Urgence'),('rea','Reanimation'),
                                ('dialyz','Dialyse'),('disp','Dispensaire')])
    is_print = fields.Boolean(string="#", default=True)
    
    def write(self, vals):
        return super(FicheDeStockModule, self).write(vals)
 

    def unlink(self):
        self.internal_status = 'supprimer'
        return False
        #raise UserError(_(self.internal_status)) 



class FacturationDeActesModule(models.Model):
    """ Feuille de facturation des actes faits  """

    _name = 'module.facturation.actes'
    _description = 'Facturation de Actes'
    _order = 'date_realisation desc, id desc'

    actes_name = fields.Char(string="ID Actes")
    patient_id = fields.Many2one('fertility.patient', string='Patient')
    nompatient = fields.Char(related='patient_id.nom', string="Nom")
    pnompatient = fields.Char(related='patient_id.postnom', string="Postnom")
    prnompatient = fields.Char(related='patient_id.prenom', string="Prenom")
    dob = fields.Date(related='patient_id.birth', string='Date Naiss', readonly=True, )
    sex = fields.Selection([('m', 'Masculin'), ('f', 'Féminin')], related='patient_id.gender', string='Sexe', readonly=True)
    age = fields.Integer(related='patient_id.age', string='Age', readonly=True)
    date_realisation = fields.Date(string='Date realisation', readonly=True, default=fields.Datetime.now())
    
    infirmier = fields.Many2one('res.users', string="Infirmier",
                                default=lambda self: self.env.user)
    internal_status = fields.Selection([('draft', 'Brouillon'),('done', 'Verrouiller'),
                                        ('facturation', 'Facturation'),('facturation', 'Facturation'),
                                        ('compta', 'Comptabiliser'),
                                        ('supprimer', 'Annuler')],
                                       default='draft', string='Status')

    # Items
    actes = fields.Many2one('product.template', string="Actes réalisés")
    categorie = fields.Many2one(related='actes.categ_id',string="Catégorie")
    qtity = fields.Integer(string="Quantité", default=1)
    invoice_ref = fields.Char(string="Ref Facture") ## Nous donne la reference de la facture

    service = fields.Char(string="Service")
    origine = fields.Selection([('hospi','Hospitalisation'),('urgence','Urgence'),('rea','Reanimation'),
                                ('dialyz','Dialyse'),('disp','Dispensaire')])
    is_print = fields.Boolean(string="#", default=True)
    
    def write(self, vals):
        return super(FacturationDeActesModule, self).write(vals)
 

    def unlink(self):
        self.internal_status = 'supprimer'
        return False
        #raise UserError(_(self.internal_status)) 


class FacturationDeMedicamentModule(models.Model):
    """ Feuille de facturation des médicaments utilisé  """

    _name = 'module.facturation.medicament'
    _description = 'Facturation de medicaments'
    _order = 'date_realisation desc, id desc'

    med_name = fields.Char(string="ID Medicaments")
    patient_id = fields.Many2one('fertility.patient', string='Patient')
    nompatient = fields.Char(related='patient_id.nom', string="Nom")
    pnompatient = fields.Char(related='patient_id.postnom', string="Postnom")
    prnompatient = fields.Char(related='patient_id.prenom', string="Prenom")
    dob = fields.Date(related='patient_id.birth', string='Date Naiss', readonly=True, )
    sex = fields.Selection([('m', 'Masculin'), ('f', 'Féminin')], related='patient_id.gender', string='Sexe', readonly=True)
    age = fields.Integer(related='patient_id.age', string='Age', readonly=True)
    date_realisation = fields.Date(string='Date realisation', readonly=True, default=fields.Datetime.now())
    
    infirmier = fields.Many2one('res.users', string="Infirmier",
                                default=lambda self: self.env.user)
    internal_status = fields.Selection([('draft', 'Brouillon'),('done', 'Verrouiller'),
                                        ('compta', 'Comptabiliser'),('facturation', 'Facturation'),
                                        ('supprimer', 'Annuler')],
                                       default='draft', string='Status')

    # Items
    produit = fields.Many2one('product.template', string="Médicaments")
    categorie = fields.Many2one(related='produit.categ_id',string="Catégorie")
    qtity = fields.Integer(string="Quantité", default=1)
    invoice_ref = fields.Char(string="Ref Facture") ## Nous donne la reference de la facture

    service = fields.Char(string="Service")
    origine = fields.Selection([('hospi','Hospitalisation'),('urgence','Urgence'),('rea','Reanimation'),
                                ('dialyz','Dialyse'),('disp','Dispensaire')])
    is_print = fields.Boolean(string="#", default=True)
    
    def write(self, vals):
        return super(FacturationDeMedicamentModule, self).write(vals)
 

    def unlink(self):
        self.internal_status = 'supprimer'
        return False
        #raise UserError(_(self.internal_status)) 


class FacturationDeMaterielModule(models.Model):
    """ Feuille de facturation des materiels utilisé  """

    _name = 'module.facturation.materiels'
    _description = 'Facturation de materiels'
    _order = 'date_realisation desc, id desc'

    mat_name = fields.Char(string="ID Materiels")
    patient_id = fields.Many2one('fertility.patient', string='Patient')
    nompatient = fields.Char(related='patient_id.nom', string="Nom")
    pnompatient = fields.Char(related='patient_id.postnom', string="Postnom")
    prnompatient = fields.Char(related='patient_id.prenom', string="Prenom")
    dob = fields.Date(related='patient_id.birth', string='Date Naiss', readonly=True, )
    sex = fields.Selection([('m', 'Masculin'), ('f', 'Féminin')], string='Sexe', readonly=True)
    age = fields.Integer(related='patient_id.age', string='Age', readonly=True)
    date_realisation = fields.Date(string='Date realisation', readonly=True, default=fields.Datetime.now())
    
    infirmier = fields.Many2one('res.users', string="Infirmier",
                                default=lambda self: self.env.user)
    internal_status = fields.Selection([('draft', 'Brouillon'),('done', 'Verrouiller')
                                        ,('compta', 'Comptabiliser'),('supprimer', 'Annuler')],
                                       default='draft', string='Status')

    # Items
    produit = fields.Many2one('product.template', string="Materiels")
    categorie = fields.Many2one(related='produit.categ_id',string="Catégorie")
    qtity = fields.Integer(string="Quantité", default=1)
    invoice_ref = fields.Char(string="Ref Facture") ## Nous donne la reference de la facture

    service = fields.Char(string="Service")
    origine = fields.Selection([('hospi','Hospitalisation'),('urgence','Urgence'),('rea','Reanimation'),
                                ('dialyz','Dialyse'),('disp','Dispensaire')])
    is_print = fields.Boolean(string="#", default=True)
    
    def write(self, vals):
        return super(FacturationDeMaterielModule, self).write(vals)
 

    def unlink(self):
        self.internal_status = 'supprimer'
        return False
        #raise UserError(_(self.internal_status)) 
