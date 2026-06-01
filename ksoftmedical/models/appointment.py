# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
import logging

_logger = logging.getLogger(__name__)
from datetime import datetime, time

motif_rdv = [('bilan','Bilan'),('suivi','Suivi'),
             ('urgence','Urgences'),
             ('autre','Autres')
]

categorie_patient = [('prive','Standard'),('vip','VIP'),
             ('convention','Conventionné'),('social','Social'),
             ('prive2','Ayant Droit')
]

# PAYMENT_STATE_SELECTION = [
#         ('not_paid', 'Not Paid'),
#         ('in_payment', 'In Payment'),
#         ('paid', 'Paid'),
#         ('partial', 'Partially Paid'),
#         ('reversed', 'Reversed'),
#         ('invoicing_legacy', 'Invoicing App Legacy'),
# ]
class AppointmentAccount_Move(models.Model):
    _inherit = 'account.move'

    libelle = fields.Selection([('consultation','Consultation générale'),('consultation2','Consultation Vasculaire'),('consultation3','Consultation Gynécologique'),
                                ('chirurgie','Chirurgie'),('laboratoire','Laboratoire'),('rfa','RFA'),('tpn','TPN'),('cpn','CPN'),('ambu','Ambulances'),('stock','Gestion de stock'),
                                ('imagerie','Imagerie'),('pharmacie','Pharmacie'),('shop_optique','Shop Optique'),('hospi','Hospitalisation'),
                                ('urgence','Urgence'),('reanimation','Réanimation'),('soins','Dispensaire'),('plaie','Soins de plaies'),('kine','Kinésitheurapie'),], string="Libelle")
    client_name = fields.Char(string="Nom Patient")
    
    
class Appointment(models.Model):
    _name = 'ksoft.appointment'
    _description = 'Gestion des rdv'
    _order = 'date_rdv desc, id desc'
    
    
    def _get_company_currency(self):
        for ordo in self:
            if ordo.patient_id.partner_id.company_id:
                ordo.currency_id = ordo.patient_id.partner_id.sudo().company_id.currency_id
            else:
                ordo.currency_id = self.env.company.currency_id

    # DELEGATION INHERITANCE
    appointment_move_id = fields.Many2one('account.move', required=False, ondelete="cascade")
    status_moved = fields.Selection(related='appointment_move_id.payment_state', string="Status Facturation",
                                    store=True)
    ref_moved = fields.Char(related='appointment_move_id.name', string="N° Facturation", store=True)

    appointment_name = fields.Char(string='ID')
    title = fields.Selection([('Consultation', 'CONSULTATION'), ('Rdv', 'RENDEZ-VOUS'), ('Autres', 'AUTRES')],
                             string="Titre", required=False)
    date_rdv = fields.Datetime(string='Date de rdv')
    heure_rdv = fields.Char(string='Heure de rdv')
    date_conf = fields.Datetime(string='Date confirmation')
    date_now = fields.Datetime(string="Date Now :")
    time_since_conf = fields.Char(string="Temps attente", compute="get_time_since_conf")

    motif = fields.Selection(motif_rdv, string="Motif du rdv")
    cancel_motif = fields.Text(string="Motif annulation")
    service = fields.Many2one('ksoft.services', string="Services")
    type_rdv = fields.Selection([('adm','Administration'),
                                 ('cons','Consultation'),
                                 ('urg','Urgence'),('rea','Réanimation'),('hospi','Hospitalisation'),
                                 ('soins','Soins ambulatoires'),('labo','Laboratoire'),
                                 ('pharma','Pharmacie'),('shop','Shop Optique'),
                                 ('img','Imagerie'),('vac','Vaccination'),('chi','Chirurgie'),
                                 ('dial','Dialyse')],
                                related='service.type_rdv',
                                readonly="True", string="Type de rdv")
    medecin = fields.Many2one('fertility.doctor', string="Médecin")
    speciality = fields.Many2one('fertility.doctor.speciality', related='medecin.speciality_id', string="Spécialité")

    patient_id = fields.Many2one('fertility.patient', string="Patient")
    visitor = fields.Char(string="Visiteur")
    convention_id = fields.Many2one(related='patient_id.parent_id', store=True)
    gender = fields.Selection(related='patient_id.gender', store=True)
    age = fields.Integer(related='patient_id.age', store=True)
    nom = fields.Char(related='patient_id.nom', string='Nom', store=True)
    prenom = fields.Char(related='patient_id.prenom', string='Prenom', store=True)
    postnom = fields.Char(related='patient_id.postnom', string='Postnom', store=True)

    matricule = fields.Char(related='patient_id.matricule', string="Matricule", store=True)
    categorie = fields.Selection(related='patient_id.categorie', string="Catégorie", store=True)
    classe = fields.Selection(related='patient_id.classe', string="Classe", store=True)
    image_1920 = fields.Image(string="Photo", max_width=1920, max_height=1920)
    numero_billet = fields.Char(string="Billet d'envoi")
    email = fields.Char(related='patient_id.email', string="Email", store=True)
    phone = fields.Char(related='patient_id.phone', string="Téléphone", store=True)
    function = fields.Char(related='patient_id.function', string="Profession", store=True)
    
    zone = fields.Selection(related='patient_id.zone', string="Zone", store=True)
    

    note = fields.Text(string="Note")

    etat = fields.Selection([('draft', 'Brouillon'), ('conf', 'Confirmé'), ('annul', 'Annulé')], string="Etat")
    user_id = fields.Many2one('res.users', 'Crée par:', default=lambda self: self.env.user, readonly="True")

    ### Articles
    product_ids = fields.Many2one('product.template', string="Consultation")
    product_id = fields.Many2one('product.product', string="Consultation")
    product_id2 = fields.Many2one('product.template', string="Type de chirurgie")
    ### Facturation

    ### Consultation
    consultation_id = fields.Many2one('fertility.appointment', string="Consultation")
    status_consultation = fields.Selection(related='consultation_id.internal_status', string="Status Consultation")
    internal_status = fields.Selection([
        ('home', 'Non confirmé'),
        ('valid', 'confirmé'),
        #('invoicing', 'Facturation'),
        #('triage', 'Triage'),
        #('consult_gyneco', 'Consultation'),
        #('open', 'En attente'),
        #('closed', 'Terminé')
    ], string='Status Interne', default='home')

    status = fields.Selection([
        ('home', 'Reception'),
        ('valid', 'Valider'),
        ('invoicing', 'Facturation'),
        ('triage', 'Triage'),
        ('attente', 'Attente de consultation'),
        ('consult_gyneco', 'Consultation'),
        ('open', 'En attente'),
        ('closed', 'Terminé')], string='Status', )

    ### Motif annulation RDV
    motannul = fields.Text(string="Motif d'annulation")

    ### Follow_up
    is_followUp = fields.Boolean(string="Follow up")

    ### Type de rdv
    time_rdv = fields.Selection([('immed', 'Immediat'),
                                 ('rdv', 'Rendez-vous')], default='immed',
                                  readonly="False", string="Type de rdv")

    type_patient = fields.Selection([('new', 'Nouveau Patient'),
                                 ('anc', 'Ancien Patient')], 
                                  string="Type de patient")
    date_recorded = fields.Datetime(string="Date d'enregistrement:", default=fields.Date.today)

    service_consultation = fields.Many2one('ksoft.unite.soins', string="Service")
    
    total_invoiced = fields.Monetary(compute='_compute_invoiced_total_amount', string="Montant Total", store=True)

    currency_id = fields.Many2one('res.currency', compute='_get_company_currency', readonly=True,
        string="Currency", help='Utility field to express amount currency')
        
    type_transfert = fields.Selection([('avcdoc', 'Avc Document'),
                                 ('sdoc', 'Sans Document')], 
                                  string="Type de Transfert")
    origine_patient = fields.Selection([('domicile', 'Domicile'),
                                 ('centre', 'Centre de Santé'),('ailleurs', 'Ailleurs')], 
                                  string="Origine patient")
    
    nom_centre = fields.Char(string="Hopital d'Orgine")

    # is_followUp_Destinataire = fields.Many2one('res.users', string='Receptioniste')

    ### Notification
    # notification_id=fields.Many2one('sh.announcement', string='Notification')

    ## Recuperer automatiquement la specialité du médecin
    #
    # @api.onchange('speciality')
    # def get_doctor_speciality(self):
    #     if self.medecin:
    #         #if len(self.diagnostics_ids) >= 1 :
    #         self.speciality = self.medecin.speciality_id.id


    ## Pour passer de follow up à rdv
    def add_to_appoint(self):
        self.is_followUp = False

        msg = ("AJOUT REUSSI !!!")
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'warning',
                'message': msg,
                'next': {'type': 'ir.actions.act_window_close'},
                'sticky': False,
            }
        }
    
    def action_view_partner_consult_invoices(self):
        self.ensure_one()
        action = self.env.ref('account.action_move_out_invoice_type')
        result = action.read()[0]
        result.pop('id', None)
        result['context'] = {}
        result['domain'] = [('id', '=', self.appointment_move_id.id)]
        pick_ids = sum([self.appointment_move_id.id])
        if pick_ids:
            res = self.env.ref('account.view_out_invoice_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = pick_ids or False
        return result
        
    def change_statut(self):
        self._get_status()
        
        
    @api.depends('appointment_move_id')
    def _compute_invoiced_total_amount(self):
        AccountMove = self.env['account.move']
        for ordo in self:
            ordo.total_invoiced = AccountMove.browse(ordo.appointment_move_id.id).amount_total
            
            
    # Pour le calcul du temps depuis la confirmation du rdv
    @api.model
    def get_time_since_conf(self):
        for appoint in self:

            if self.date_conf:
                conf_day = self.date_conf
                lelo = datetime.now()
                appoint.date_now = lelo

                temps_en_sec = self.date_diff_in_seconds(lelo, conf_day)
                temps_en_jhms_cond = self.dhms_from_seconds_conditionnel(temps_en_sec)

                appoint.time_since_conf = temps_en_jhms_cond
            else:
                appoint.time_since_conf = "O Sec"

    def date_diff_in_seconds(self, dt2, dt1):
        timedelta = dt2 - dt1
        a = timedelta.days * 24 * 3600 + timedelta.seconds
        return a

    def dhms_from_seconds_conditionnel(self, seconds):

        if seconds > 0 and seconds < 60:
            # minutes, seconds = divmod(seconds, 60)
            remaining_time = str(seconds) + "Sec"

        elif seconds >= 60 and seconds < 3600:
            minutes, seconds = divmod(seconds, 60)
            res = minutes, seconds
            remaining_time = str(res[0]) + "M " + str(res[1]) + "S"

        elif seconds >= 3600 and seconds < 86400:
            minutes, seconds = divmod(seconds, 60)
            hours, minutes = divmod(minutes, 60)
            res = hours, minutes, seconds
            remaining_time = str(res[0]) + "H " + str(res[1]) + "M " + str(res[2]) + "S"
        elif seconds >= 86400:
            minutes, seconds = divmod(seconds, 60)
            hours, minutes = divmod(minutes, 60)
            days, hours = divmod(hours, 24)
            res = days, hours, minutes, seconds
            remaining_time = str(res[0]) + "J " + str(res[1]) + "H " + str(res[2]) + "M " + str(res[3]) + "S"
        else:
            remaining_time = seconds

        return remaining_time

    def _get_status(self):
        for exam in self:
            continue

    # for exam in self:
    # if exam.internal_status=='invoicing' :
    # if exam.status_moved :
    # if exam.status_moved=='paid' :
    # exam.internal_status = 'triage'
    # exam.action_create_consultation()
    # exam.status = exam.internal_status

    def shop(self):
        self.env['module.prescription'].create({

            'patient_id': self.patient_id.id,
            'numero_billet': self.numero_billet,
            # 'medecin': self.doctor_id.id,
            'parent_id': self.patient_id.parent_id.id,
            'matricule': self.patient_id.matricule,
            'categorie': self.patient_id.categorie,
            'classe': self.patient_id.classe,
            'function': self.patient_id.function,
            'email': self.patient_id.email,
            'phone': self.patient_id.phone,
            # 'cord_commentaire': self.cord_commentaire,
        })
        message = "DEMANDE OPTIQUE ENVOYEE"
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'danger',
                'message': message,
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }
    
    def action_create_woutinvoice(self):
        service_id = self.service
        service_nom = self.service.type_rdv
        
        #print("xxxxxxxxxxx")
        #raise UserError(_(service_nom))
        if service_id:
            if service_nom == "cons":
                product_id = self.product_id
                line_section = self.service.service

                #### Recuperer le prix selon la liste de prix définie
                product_context = dict(
                    self.env.context,
                    partner_id=self.patient_id.partner_id.id,
                    date=self.date_conf or fields.Date.today(),
                    uom=self.product_id.uom_id.id,
                )
                prix, ruled = self.patient_id.partner_id.property_product_pricelist.with_context(
                    product_context).get_product_price_rule(
                    self.product_id, 1.0,
                    self.patient_id.partner_id) if self.patient_id.partner_id.property_product_pricelist else self.product_id.list_price

                lines = [(0, 0, {'display_type': 'line_section', 'name': line_section, 'debit': 0, 'credit': 0,
                                 'account_id': False}),
                                 
                        #  (0, 0, {'product_id': self.env['product.product'].search(
                        #      [('product_tmpl_id', '=', product_id.id)]).id, 'price_unit': prix, 'quantity': 1,
                        #          'patient_id': self.patient_id.id, 'doctor_id': self.medecin.id,
                        #          'date_realisation': fields.Datetime.now(), 'numero_billet': self.numero_billet})]
                
                        (0, 0, {'product_id': self.product_id.id, 'price_unit': prix, 'quantity': 1,
                                 'patient_id': self.patient_id.id, 'doctor_id': self.medecin.id,
                                 'date_realisation': fields.Datetime.now(), 'numero_billet': self.numero_billet})]

                ctx = self.env.context.copy()

                # raise UserError(_("##### %s", lines))
                # ctx.update({'default_move_type':'out_invoice', 'default_journal_id':self.appointment_type.journal_id.id, 'default_partner_id':self.patient_id.partner_id.id })
                ctx.update({'default_move_type': 'out_invoice', 'default_partner_id': self.patient_id.partner_id.id})
                if self.categorie:
                    journal_id = self.get_journal_type(self.categorie)
                    self.appointment_move_id = self.appointment_move_id.create({
                        'move_type': 'out_invoice',
                        'journal_id': journal_id,
                        'partner_id': self.patient_id.partner_id.id,
                        'patient_id': self.patient_id.id,
                        #'medecin_id': self.medecin.id,
                        'convention_id': self.convention_id.id,

                        'matricule': self.matricule,
                        'categorie': self.categorie,
                        'classe': self.classe,
                        'email': self.email,
                        'phone': self.phone,
                        'function': self.function,
                        
                        'service_id2': self.medecin.service_id.id,
                        'medecin_id2': self.medecin.id,
                        

                        'consultation_id': self.id,
                        'numero_billet': self.numero_billet,
                        'ref': self.appointment_name,

                        ### Get list price
                        #'pricelist_id': self.patient_id.partner_id.parent_id.property_product_pricelist,

                        'invoice_line_ids': lines
                    })
              
                    consult_id = self.action_create_consultation_sansfacture()
                    ## Transferer la clé de facturation

                    ## Ajouter l'id de la consultation dans la facture
                    self.appointment_move_id.write({'consultation_consultation_id': consult_id, 'libelle':'consultation'})
                    if consult_id:
                        self.internal_status = 'valid'
                else:
                    raise UserError(_("Veuillez selectionner la catégorie du patient"))

                ### Date de confirmation du RDV
                self.date_conf = datetime.now()

                message = "RDV CONFIRME"
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'type': 'danger',
                        'message': message,
                        'sticky': False,
                        'next': {'type': 'ir.actions.act_window_close'},

                    }
                }
                
        else:
            print("Aucun service selectionné")
                   
    def action_create(self):
        service_id = self.service
        service_nom = self.service.type_rdv
        
        #print("xxxxxxxxxxx")
        #raise UserError(_(service_nom))
        if service_id:
            if service_nom == "cons":
                product_id = self.product_id
                line_section = self.service.service

                #### Recuperer le prix selon la liste de prix définie
                product_context = dict(
                    self.env.context,
                    partner_id=self.patient_id.partner_id.id,
                    date=self.date_conf or fields.Date.today(),
                    uom=self.product_id.uom_id.id,
                )
                prix, ruled = self.patient_id.partner_id.property_product_pricelist.with_context(
                    product_context).get_product_price_rule(
                    self.product_id, 1.0,
                    self.patient_id.partner_id) if self.patient_id.partner_id.property_product_pricelist else self.product_id.list_price

                lines = [(0, 0, {'display_type': 'line_section', 'name': line_section, 'debit': 0, 'credit': 0,
                                 'account_id': False}),
                                 
                        #  (0, 0, {'product_id': self.env['product.product'].search(
                        #      [('product_tmpl_id', '=', product_id.id)]).id, 'price_unit': prix, 'quantity': 1,
                        #          'patient_id': self.patient_id.id, 'doctor_id': self.medecin.id,
                        #          'date_realisation': fields.Datetime.now(), 'numero_billet': self.numero_billet})]
                
                        (0, 0, {'product_id': self.product_id.id, 'price_unit': prix, 'quantity': 1,
                                 'patient_id': self.patient_id.id, 'doctor_id': self.medecin.id,
                                 'date_realisation': fields.Datetime.now(), 'numero_billet': self.numero_billet})]

                ctx = self.env.context.copy()

                # raise UserError(_("##### %s", lines))
                # ctx.update({'default_move_type':'out_invoice', 'default_journal_id':self.appointment_type.journal_id.id, 'default_partner_id':self.patient_id.partner_id.id })
                ctx.update({'default_move_type': 'out_invoice', 'default_partner_id': self.patient_id.partner_id.id})
                if self.categorie:
                    if self.categorie == 'prive' or self.categorie == 'prive2':
                        # consult_id = self.action_create_consultation()
                        #raise UserError(_("##### %s", self.categorie))
                        journal_id = self.get_journal_type(self.categorie)
                        self.appointment_move_id = self.appointment_move_id.create({
                            'move_type': 'out_invoice',
                            'journal_id': journal_id,
                            'partner_id': self.patient_id.partner_id.id,
                            'patient_id': self.patient_id.id,
                            #'medecin_id': self.medecin.id,
                            'convention_id': self.convention_id.id,

                            'matricule': self.matricule,
                            'categorie': self.categorie,
                            'classe': self.classe,
                            'email': self.email,
                            'phone': self.phone,
                            'function': self.function,
                            
                            'service_id2': self.medecin.service_id.id,
                            'medecin_id2': self.medecin.id,
                            
                            
                            'numero_billet': self.numero_billet,
                            'ref': self.appointment_name,

                            'consultation_id': self.id,
                            # 'consultation_consultation_id': consult_id,
                            'invoice_line_ids': lines
                        })
                        # self.consult_move_id.with_context(ctx).write({'invoice_line_ids': lines        })
                        # self.internal_status = 'invoicing'
                        # self.action_create_consultation()
                        consult_id = self.action_create_consultation()
                        ## Transferer la clé de facturation

                        ## Ajouter l'id de la consultation dans la facture
                        self.appointment_move_id.write({'consultation_consultation_id': consult_id, 'libelle':'consultation'})

                        if consult_id:
                            self.internal_status = 'valid'

                    if self.categorie == 'convention':
                        journal_id = self.get_journal_type(self.categorie)
                        self.appointment_move_id = self.appointment_move_id.create({
                            'move_type': 'out_invoice',
                            'journal_id': journal_id,
                            'partner_id': self.patient_id.partner_id.id,
                            'patient_id': self.patient_id.id,
                            #'medecin_id': self.medecin.id,
                            'convention_id': self.convention_id.id,

                            'matricule': self.matricule,
                            'categorie': self.categorie,
                            'classe': self.classe,
                            'email': self.email,
                            'phone': self.phone,
                            'function': self.function,
                            
                            'service_id2': self.medecin.service_id.id,
                            'medecin_id2': self.medecin.id,
                            

                            'consultation_id': self.id,
                            'numero_billet': self.numero_billet,
                            'ref': self.appointment_name,

                            ### Get list price
                            #'pricelist_id': self.patient_id.partner_id.parent_id.property_product_pricelist,

                            'invoice_line_ids': lines
                        })
                        # self.consult_move_id.with_context(ctx).write({        })
                        # self.internal_status = 'triage'
                        # self.action_create_consultation()
                        consult_id = self.action_create_consultation()
                        ## Transferer la clé de facturation

                        ## Ajouter l'id de la consultation dans la facture
                        self.appointment_move_id.write({'consultation_consultation_id': consult_id, 'libelle':'consultation'})
                        if consult_id:
                            self.internal_status = 'valid'
                else:
                    raise UserError(_("Veuillez selectionner la catégorie du patient"))

                ### Date de confirmation du RDV
                self.date_conf = datetime.now()

                message = "RDV CONFIRME"
                # return {
                    # 'type': 'ir.actions.client',
                    # 'tag': 'display_notification',
                    # 'params': {
                        # 'type': 'danger',
                        # 'message': message,
                        # 'sticky': False,
                        # 'next': {'type': 'ir.actions.act_window_close'},

                    # }
                # }
            elif service_nom == "SHOP OPTIQUE":
                self.env['module.prescription'].create({

                    'patient_id': self.patient_id.id,
                    'numero_billet': self.numero_billet,
                    # 'medecin': self.doctor_id.id,
                    'parent_id': self.patient_id.parent_id.id,
                    'matricule': self.patient_id.matricule,
                    'categorie': self.patient_id.categorie,
                    'classe': self.patient_id.classe,
                    'function': self.patient_id.function,
                    'email': self.patient_id.email,
                    'phone': self.patient_id.phone,
                    # 'cord_commentaire': self.cord_commentaire,
                })

                # Envoi notification Shop
                self.env['sh.announcement'].NotifShop()

                message = "DEMANDE OPTIQUE ENVOYEE"
                # return {
                    # 'type': 'ir.actions.client',
                    # 'tag': 'display_notification',
                    # 'params': {
                        # 'type': 'danger',
                        # 'message': message,
                        # 'sticky': False,
                        # 'next': {'type': 'ir.actions.act_window_close'},
                    # }
                # }

            elif service_nom == "pharma":
                # Envoi à la pharmacie
                ordonn_id = self.env['module.ordonnance'].create({

                    'patient_id': self.patient_id.id,
                    # 'poids': self.poids,

                    'parent_id': self.patient_id.parent_id.id,
                    'matricule': self.patient_id.matricule,
                    'categorie': self.patient_id.categorie,
                    'classe': self.patient_id.classe,
                    'function': self.patient_id.function,
                    'email': self.patient_id.email,
                    'phone': self.patient_id.phone,

                    'numero_billet': self.numero_billet,
                    # 'medecin': self.doctor_id.id,
                    # 'commentaire_medecin': self.cord_commentaire_pharma,

                })
                message = "DEMANDE PHARMACIE ENVOYEE"
                # return {
                    # 'type': 'ir.actions.client',
                    # 'tag': 'display_notification',
                    # 'params': {
                        # 'type': 'danger',
                        # 'message': message,
                        # 'sticky': False,
                        # 'next': {'type': 'ir.actions.act_window_close'},

                    # }
                # }
            elif service_nom == "CHIRURGIE":
                product_id = self.product_id2
                line_section = self.service.service

                #### Recuperer le prix selon la liste de prix définie
                product_context = dict(
                    self.env.context,
                    partner_id=self.patient_id.partner_id.id,
                    date=self.date_conf or fields.Date.today(),
                    uom=self.product_id2.uom_id.id,
                )
                prix, ruled = self.patient_id.partner_id.property_product_pricelist.with_context(
                    product_context).get_product_price_rule(
                    self.product_id2, 1.0,
                    self.patient_id.partner_id) if self.patient_id.partner_id.property_product_pricelist else self.product_id2.list_price

                lines = [(0, 0, {'display_type': 'line_section', 'name': line_section, 'debit': 0, 'credit': 0,
                                 'account_id': False}),
                         (0, 0, {'product_id': self.env['product.product'].search(
                             [('product_tmpl_id', '=', product_id.id)]).id, 'price_unit': prix, 'quantity': 1,
                                 'patient_id': self.patient_id.id, 'doctor_id': self.medecin.id,
                                 'date_realisation': fields.Datetime.now(), 'numero_billet': self.numero_billet})]

                ctx = self.env.context.copy()

                # raise UserError(_("##### %s", lines))
                # ctx.update({'default_move_type':'out_invoice', 'default_journal_id':self.appointment_type.journal_id.id, 'default_partner_id':self.patient_id.partner_id.id })
                ctx.update({'default_move_type': 'out_invoice', 'default_partner_id': self.patient_id.partner_id.id})
                if self.categorie:
                    if self.categorie == 'prive' or self.categorie == 'prive2':
                        # consult_id = self.action_create_consultation()
                        journal_id = self.get_journal_type(self.categorie)
                        self.appointment_move_id = self.appointment_move_id.create({
                            'move_type': 'out_invoice',
                            'journal_id': journal_id,
                            'partner_id': self.patient_id.partner_id.id,
                            'patient_id': self.patient_id.id,
                            'doctor_id': self.medecin.id,
                            'convention_id': self.convention_id.id,

                            'matricule': self.matricule,
                            'categorie': self.categorie,
                            'classe': self.classe,
                            'email': self.email,
                            'phone': self.phone,
                            'function': self.function,

                            'numero_billet': self.numero_billet,
                            'ref': self.appointment_name,

                            'consultation_id': self.id,
                            # 'consultation_consultation_id': consult_id,
                            'invoice_line_ids': lines
                        })
                        # self.consult_move_id.with_context(ctx).write({        })
                        # self.internal_status = 'invoicing'
                        # self.action_create_consultation()
                        consult_id = self.action_create_chirurgie()
                        ## Transferer la clé de facturation

                        ## Ajouter l'id de la consultation dans la facture
                        self.appointment_move_id.write({'consultation_consultation_id': consult_id})

                        if consult_id:
                            self.internal_status = 'valid'

                    if self.categorie == 'convention':
                        journal_id = self.get_journal_type(self.categorie)
                        self.appointment_move_id = self.appointment_move_id.create({
                            'move_type': 'out_invoice',
                            'journal_id': journal_id,
                            'partner_id': self.patient_id.partner_id.id,
                            'patient_id': self.patient_id.id,
                            'doctor_id': self.medecin.id,
                            'convention_id': self.convention_id.id,

                            'matricule': self.matricule,
                            'categorie': self.categorie,
                            'classe': self.classe,
                            'email': self.email,
                            'phone': self.phone,
                            'function': self.function,

                            'consultation_id': self.id,
                            'numero_billet': self.numero_billet,
                            'ref': self.appointment_name,

                            ### Get list price
                            'pricelist_id': self.patient_id.partner_id.property_product_pricelist,

                            'invoice_line_ids': lines
                        })
                        # self.consult_move_id.with_context(ctx).write({        })
                        # self.internal_status = 'triage'
                        # self.action_create_consultation()
                        consult_id = self.action_create_chirurgie()
                        ## Transferer la clé de facturation

                        ## Ajouter l'id de la consultation dans la facture
                        self.appointment_move_id.write({'consultation_consultation_id': consult_id})
                        if consult_id:
                            self.internal_status = 'valid'
                else:
                    raise UserError(_("Veuillez selectionner la catégorie du patient"))

                ### Date de confirmation du RDV
                self.date_conf = datetime.now()

                message = "RDV CONFIRME"
                # return {
                    # 'type': 'ir.actions.client',
                    # 'tag': 'display_notification',
                    # 'params': {
                        # 'type': 'danger',
                        # 'message': message,
                        # 'sticky': False,
                        # 'next': {'type': 'ir.actions.act_window_close'},

                    # }
                # }


        else:
            print("Aucun service selectionné")

    # @api.multi

    def get_journal_type(self, categorie):
        res = False
        if len(self.env['account.journal'].search([('is_private', '=', True)]))> 0 and len(self.env['account.journal'].search([('is_abonne', '=', True)]))> 0:
            if categorie:
                if categorie in ['prive','prive2']:
                    res = self.env['account.journal'].search([('is_private', '=', True)])[0].id
                if categorie == 'convention':
                    res = self.env['account.journal'].search([('is_abonne', '=', True)])[0].id
            else:
                raise UserError(_("Veuillez préciser la catégorie du patient"))
        else:
            raise UserError(_("Aucun journal de facturation lié à la catégorie du patient selectionné, Contactez l'administrateur"))

        return res

    def name_get(self):
        result = []
        for rec in self:
            if rec.service:
                result.append((rec.id, "%s - %s" % (rec.service.service_name, rec.patient_id.name)))
            else:
                result.append((rec.id, "%s - %s" % (rec.service.service_name, rec.visitor)))
        return result

    def action_return(self):
        if self.etat == 'conf' or self.etat == 'annul':
            self.etat = 'draft'
        return True

    def confirm_appointment(self):
        """
            Confirmation du rdv et transfert vers le service concerné
        """
    
    def action_pass_rdv_to_immed(self):
        self.time_rdv = 'immed'
        self.consultation_id.write({'time_rdv': 'immed'})
        #raise UserError(self.consultation_id.motif_rdv)
        
    
    def action_create_consultation_sansfacture(self):
        appointment = self.env['fertility.appointment'].create({
            'patient_id': self.patient_id.id,
            'doctor_id': self.medecin.id,
            'date': self.date_rdv,
            #'datetime': fields.Datetime.now()
            'datetime': self.date_rdv,
            'user_id': self.user_id.id,
            'consult_move_id': self.appointment_move_id.id,
            # 'appointment_type':self.appointment_type.id,
            'internal_status': "triage",
            # 'product_id':self.env['product.product'].search(['product_tmpl_id','=',self.product_id.id]).id,
            'product_id': self.product_id.id,
            'numero_billet': self.numero_billet,
            'motif_rdv': self.motif,
            'time_rdv': self.time_rdv,
            'type_transfert': self.type_transfert,
            'origine_patient': self.origine_patient,
            'nom_centre': self.nom_centre,
            'av_pio_last_consultation': self.env['fertility.patient'].last_cons(self.patient_id.id)
        })
        self.consultation_id = appointment.id
        return appointment
        
    # @api.depends('appointment_move_id')
    def action_create_consultation(self):
        appointment = self.env['fertility.appointment'].create({
            'patient_id': self.patient_id.id,
            'doctor_id': self.medecin.id,
            'date': self.date_rdv,
            #'datetime': fields.Datetime.now()
            'datetime': self.date_rdv,
            'user_id': self.user_id.id,
            'consult_move_id': self.appointment_move_id.id,
            # 'appointment_type':self.appointment_type.id,
            'internal_status': "invoicing" if self.categorie == "prive" else "triage",
            # 'product_id':self.env['product.product'].search(['product_tmpl_id','=',self.product_id.id]).id,
            'product_id': self.product_id.id,
            'numero_billet': self.numero_billet,
            'motif_rdv': self.motif,
            'time_rdv': self.time_rdv,
            'type_transfert': self.type_transfert,
            'origine_patient': self.origine_patient,
            'nom_centre': self.nom_centre,
            'av_pio_last_consultation': self.env['fertility.patient'].last_cons(self.patient_id.id)
        })
        self.consultation_id = appointment.id
        return appointment

    def action_create_chirurgie(self):
        appointment = self.env['fertility.appointment'].create({
            'patient_id': self.patient_id.id,
            'doctor_id': self.medecin.id,
            'datetime': fields.Datetime.now(),
            'user_id': self.user_id.id,
            'consult_move_id': self.appointment_move_id.id,
            'internal_status': "invoicing" if self.categorie == "prive" else "triage",
            'product_id': self.product_id2.id,
            'numero_billet': self.numero_billet,
            'motif_rdv': self.motif,
            'av_pio_last_consultation': self.env['fertility.patient'].last_cons(self.patient_id.id)
        })

        self.consultation_id = appointment.id

        # return {'warning':{'title':'warning','message':'Consultation créee avec succès'}}
        # raise UserError(appointment.consult_move_id)
        return appointment


class ConsultationSocial(models.Model):
    _name = 'fertility.social'
    _description = 'Consultation Sociale'

    social_name = fields.Char(string='ID')
    social_description = fields.Html(string='Description Consultation sociale')
    social_datetime = fields.Datetime('Date/Heure', required=False)

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, "%s" % (rec.social_name)))
        return result

    @api.model
    def create(self, vals):
        vals['social_name'] = self.env['ir.sequence'].next_by_code('fertility.social.name')
        return super(ConsultationSocial, self).create(vals)


class ConsultationGyneco(models.Model):
    _name = 'fertility.gyneco'
    _description = 'Consultation Gyneco'

    gyneco_name = fields.Char(string='ID')
    gyneco_datetime = fields.Datetime('Date/Heure', required=False)
    anamnese = fields.Html('Anamnèse')

    douleurs_pelviennes = fields.Boolean('Douleurs pelviennes')
    dysmenorrhee = fields.Boolean('Dysménorrhée')
    dyspareunie = fields.Boolean('Dyspareunie')
    menometrorragie = fields.Boolean('Ménométrorragie')
    duree_regle = fields.Char('Durée des règles')
    duree_cycle = fields.Char('Durée des cycles')

    physique = fields.Html('Examen physique')
    ###
    inspection = fields.Html('Inspection')
    meo = fields.Html('Meo')
    laf = fields.Html('OD Laf')
    laf2 = fields.Html('OG Laf')
    fo = fields.Html('OD Fo')
    fo2 = fields.Html('OG Fo')

    gonioscopie_od = fields.Selection([('1', '1/4'), ('2', '2/4'), ('3', '3/4'), ('4', '4/4')], string="OD Gonioscopie")
    gonioscopie_og = fields.Selection([('1', '1/4'), ('2', '2/4'), ('3', '3/4'), ('4', '4/4')], string="OG Gonioscopie")

    commentaire = fields.Html('Commentaire')

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, "%s" % (rec.gyneco_name)))
        return result

    @api.model
    def create(self, vals):
        vals['gyneco_name'] = self.env['ir.sequence'].next_by_code('fertility.gyneco.name')
        return super(ConsultationGyneco, self).create(vals)


class Examen(models.Model):
    _name = 'fertility.examen'
    _description = 'Examen'

    examen_name = fields.Char(string='ID')
    imagerie_ids = fields.One2many('fertility.examen.imagerie', 'examen_id')
    labo_ids = fields.One2many('fertility.examen.labo', 'examen_id')
    imagerie_exam_ids = fields.One2many('fertility.examen.imagerie2', 'examen_id')

    def name_get(self):
        result = []
        for rec in self:
            imagerie_done, imagerie_all = len(rec.imagerie_ids.filtered(lambda exam: exam.status == 'done')), len(
                rec.imagerie_ids)
            labo_done, labo_all = len(rec.labo_ids.filtered(lambda exam: exam.status == 'done')), len(rec.labo_ids)
            result.append(
                (rec.id, "Imagerie : %s/%s | Labo : %s/%s" % (imagerie_done, imagerie_all, labo_done, labo_all)))
        return result

class TubeLaboratoire(models.Model):
    _name = 'tube.laboratoire'

    tube = fields.Char('Tube')
    code = fields.Char('Code')
    images = fields.Binary('Images')
        
class Product(models.Model):
    _inherit = 'product.template'

    valeur_normale = fields.Text('Valeur normale')
    tube = fields.Many2one('tube.laboratoire', string="Tube")


class DemandeExamen(models.Model):
    _name = 'fertility.examen.labo.demande'
    _description = 'Examen'

    patient_id = fields.Many2one('fertility.patient')
    doctor_id = fields.Many2one('fertility.doctor')
    partner_id = fields.Many2one('res.partner', ondelete="cascade",)
    client_nom = fields.Char(string="Nom Patient")
    ## PATIENT INFO
    prenom = fields.Char(string="Prenom", store=True)
    nom = fields.Char(string="Nom", store=True)
    postnom = fields.Char(string="Postnom", store=True)
    birth = fields.Date(string="Date de naissance")
    age = fields.Integer(string="Age")
    function = fields.Char(string="Profession")
    gender = fields.Selection([('M', 'Masculin'), ('F', 'Féminin')], 'Genre')
    date_request = fields.Datetime(string='Date', readonly=False, default=fields.Datetime.now())

    parent_id = fields.Many2one('res.partner', string="Convention")
    matricule = fields.Char(string="Matricule")
    categorie = fields.Selection(categorie_patient, string="Catégorie", readonly=False)
    classe = fields.Selection([('agent','Agent'),('epoux','Epoux(se)'),('enf','Enfants')], string="Classe", readonly=False)

    numero_billet = fields.Char(string="Billet d'envoi")
    email = fields.Char(string="Email")
    phone = fields.Char(string="Téléphone")
    function = fields.Char(string="Profession")

    labo_ids = fields.One2many('fertility.examen.labo', 'demande_examen_id')


    @api.onchange('patient_id')
    def _onchange_patient_id(self):
        if self.patient_id.id:
            self.onchange_patient_suite(self.patient_id.id)

    def onchange_patient_suite(self, patient):
        pt = False
        if patient:
            pt = patient
            self.patient_id = self.env['fertility.patient'].browse(pt).id
            self.parent_id = self.env['fertility.patient'].browse(pt).parent_id
            self.nom = self.env['fertility.patient'].browse(pt).nom
            self.postnom = self.env['fertility.patient'].browse(pt).postnom
            self.prenom = self.env['fertility.patient'].browse(pt).prenom
            self.matricule = self.env['fertility.patient'].browse(pt).matricule
            self.categorie = self.env['fertility.patient'].browse(pt).categorie
            self.classe = self.env['fertility.patient'].browse(pt).classe
            self.phone = self.env['fertility.patient'].browse(pt).phone
            self.email = self.env['fertility.patient'].browse(pt).email
            #self.numero_billet = self.env['fertility.patient'].browse(pt).numero_billet
            self.gender = self.env['fertility.patient'].browse(pt).gender
            self.birth = self.env['fertility.patient'].browse(pt).birth
            
            self.function = self.env['fertility.patient'].browse(pt).function

    def action_to_facturation(self):
        ## Check la categorie pour placer dans le journal qui convient
        journal_id = self.env['ksoft.appointment'].get_journal_type(self.categorie)

        # Recupération dans une liste des examens d'imagérie selectionnés dans le champs "imagerie_ids"
        #imagerie_ids = self.consult_examen_id.imagerie_ids.filtered(lambda imagerie: imagerie.status == 'draft')

        # Recupération dans une liste des examens de laboratoire selectionnés dans le champs "labo_ids"
        labo_ids =  self.labo_ids.filtered(lambda labo: labo.status == 'draft')

        #{'move_line_id':[line.id for line in self.env['account.move'].browse(move_id.id).invoice_line_ids if line.ref_item == self.env['fertility.examen.imagerie'].browse(img.id).imagerie_name]}

        if self.labo_ids:
        ## Creation facture laboratoire
            if labo_ids:
                lines = []
                lines = [(0, 0, {'display_type': 'line_section', 'name': 'Laboratoire', 'debit': 0, 'credit': 0,
                                 'account_id': False})]

                for labo in labo_ids:
                    #### Recuperer le prix selon la liste de prix defini
                    product_context = dict(
                        self.env.context,
                        partner_id=self.patient_id.partner_id.id,
                        date=fields.Date.today(),
                        uom=labo.analyse.uom_id.id,
                    )

                    # prix, ruled = self.patient_id.partner_id.property_product_pricelist.with_context(
                    #     product_context).get_product_price_rule(
                    #     labo.analyse, 1,
                    #     self.patient_id.partner_id) if self.patient_id.partner_id.property_product_pricelist else self.product.list_price

                    # raise UserError(_("##### %s", product_context))

                    lines.extend((0, 0, {
                        'product_id': self.env['product.product'].search([('product_tmpl_id', '=', labo.analyse.id)]).id,
                        'price_unit': labo.analyse.list_price, 
                        'ref_item':labo.labo_name,
                        'quantity': 1}))


                move_id = self.env['account.move'].create({
                    'move_type': 'out_invoice',
                    'journal_id': journal_id,
                    'patient_id': self.patient_id.id,
                    'numero_billet': self.numero_billet,
                    
                    'convention_id': self.parent_id.id,
                    'matricule': self.matricule,
                    'categorie': self.categorie,
                    'classe': self.classe,
                    'libelle':'laboratoire',
                    'client_name':self.client_nom,

                    'partner_id': self.patient_id.partner_id.id if self.patient_id else self.partner_id.id  ,
                    
                    #'ref': self.name,
                    'invoice_line_ids': lines
                })


                ### màj de la demande d'examen de labo créée
                #raise UserError(_([line.id for line in self.env['account.move'].browse(move_id.id).invoice_line_ids if line.ref_item == self.env['fertility.examen.labo'].browse(labo.id).labo_name]))
                labo_ids.write({'move_id': move_id.id, 'internal_status': 'invoicing', 'patient_id': self.patient_id.id,
                                'medecin_demander': self.doctor_id.id, 'partner_id':self.partner_id.id, 'client_nom':self.client_nom
    
                                })
             

        else:
            raise UserError(_("Vous n'avez selectionné aucuns examens de laboratoire"))
            print("Pas de imagerie_ids")


class ExamenLabo(models.Model):
    _name = 'fertility.examen.labo'
    _description = 'Examen Labo'
    _inherit = ['mail.thread']
    _order = 'date_request desc, id desc'
    
    
    def _get_company_currency(self):
        for ordo in self:
            if ordo.patient_id.partner_id.company_id:
                ordo.currency_id = ordo.patient_id.partner_id.sudo().company_id.currency_id
            else:
                ordo.currency_id = self.env.company.currency_id

    labo_name = fields.Char(string='Labo ID')
    examen_id = fields.Many2one('fertility.examen')
    
    demande_examen_id = fields.Many2one('fertility.examen.labo.demande') 

    date_request = fields.Date(string='Date demande', readonly=True, default=fields.Date.today)
    date_analyse = fields.Datetime('Date/Heure analyse')
    date_prelevement = fields.Datetime('Date/Heure prélèvement')
    status = fields.Selection(
        [('draft', 'En attente'), ('invoicing', 'Facturation'), ('sample', 'En attente de Prélèvement'),
         ('ongoing', 'En cours'), ('done', 'Fait')], 'Etat', compute='_get_status')
    internal_status = fields.Selection(
        [('draft', 'En attente'), ('invoicing', 'Facturation'), ('sample', 'En attente de Prélèvement'),
         ('ongoing', 'En cours'), ('done', 'Fait')], 'Etat', default='draft')
    technicien = fields.Many2one('res.users', string='Par')
    tech_prelevement = fields.Many2one('res.users', string='Prélèvé par')

    technicien_prelevement = fields.Many2one('res.users', string='Prélévé par')
    echantillon_num = fields.Char("Numéro d'échantillon")
    echantillon_type = fields.Char("Type d'échantillon")
    description = fields.Text('Résultat')
    analyse_autres = fields.Char(string='Analyses')
    analyse = fields.Many2one('product.template', string='Analyse')
    analyses = fields.Many2one('product.product', string='Analyse')
    type_analyse = fields.Many2one(related='analyse.categ_id', store=True)
    valeur_normale = fields.Text(related='analyse.valeur_normale')
    move_id = fields.Many2one('account.move')
    patient_id = fields.Many2one('fertility.patient')
    parent_id = fields.Many2one(related='patient_id.parent_id', string="Convention")
    gender = fields.Selection(related='patient_id.gender')
    age = fields.Integer(related='patient_id.age')

    matricule = fields.Char(related='patient_id.matricule', string="Matricule")
    categorie = fields.Selection(related='patient_id.categorie', string="Catégorie")
    classe = fields.Selection(related='patient_id.classe', string="Classe")

    numero_billet = fields.Char(string="Billet d'envoi")
    email = fields.Char(related='patient_id.email', string="Email")
    phone = fields.Char(related='patient_id.phone', string="Téléphone")
    function = fields.Char(related='patient_id.function', string="Profession")

    is_print = fields.Boolean(string="#", default=True)
    clinique = fields.Html(string="Clinique")
    but = fields.Text(string="But")
    echantillon = fields.Selection([('urine', 'Urines'), ('selles', 'Selles'),
                                    ('crachat', 'Crachat'), ('frotisv', 'Frottis Vaginal'),
                                    ('furt', 'Frottis Uretral')], 'Type echantillon')

    medecin_demander = fields.Many2one('fertility.doctor', string="Medecin demandeur")
    examen_text = fields.Html(string="Examen Labo")
    demandeur = fields.Many2one('res.users', string="Demandé par ")
    
    partner_id = fields.Many2one('res.partner', ondelete="cascade",)
    client_nom = fields.Char(string="Nom Patient")

    move_line_id = fields.Many2one('account.move.line', compute='_get_account_move_line_id', default=False, string="Line")
    etat_facturation = fields.Boolean('Payé ?', related='move_line_id.etat', readonly=True)

    is_pathologique = fields.Boolean('R. Pathologique', default=False)
    
    total_invoiced = fields.Monetary(compute='_compute_invoiced_total_amount', string="Montant Total", store=True)
    currency_id = fields.Many2one('res.currency', compute='_get_company_currency', readonly=True,
        string="Currency", help='Utility field to express amount currency')


    @api.model
    def default_get(self, fields):
        res = super(ExamenLabo, self).default_get(fields)
        res['demandeur'] = self.env.user.id
        return res
        
    @api.depends('move_id')
    def _compute_invoiced_total_amount(self):
        AccountMove = self.env['account.move']
        for ordo in self:
            ordo.total_invoiced = AccountMove.browse(ordo.move_id.id).amount_total
    
    def action_view_partner_invoices(self):
        self.ensure_one()   
        action = self.env.ref('account.action_move_out_invoice_type')
        result = action.read()[0]
        result.pop('id', None)
        result['context'] = {}
        result['domain'] = [('id', '=', self.move_id.id)]
        pick_ids = sum([self.move_id.id])
        if pick_ids:
            res = self.env.ref('account.view_out_invoice_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = pick_ids or False
        return result
        
    def _get_account_move_line_id(self):
        for item in self:
            item.move_line_id = self.env['account.move.line'].search([('ref_item','=',item.labo_name)]).id

            print("************************************************************************************")
            #if item.move_id:
            #    try:
            #        self.env['account.move.line'].search([('ref_item','=',item.labo_name)]).id
            #        item.move_line_id = self.env['account.move.line'].search([('ref_item','=',item.labo_name)]).id
            #    except Exception as e:
            #        item.move_line_id = False
            #else:
            #    item.move_line_id = 2

    @api.model
    def create(self, vals):
        vals['labo_name'] = self.env['ir.sequence'].next_by_code('fertility.labo.name')
        return super(ExamenLabo, self).create(vals)

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, "%s" % (rec.labo_name)))
        return result

    def _get_status(self):
        for exam in self:
            if exam.internal_status == 'invoicing':
                if exam.move_id and exam.categorie == 'convention':
                    if exam.move_id.state == 'posted':
                        exam.internal_status = 'sample'
                
                if exam.move_id and exam.categorie != 'convention':
                    if exam.move_id.payment_state in ['partial', 'paid'] and exam.etat_facturation == True:
                        exam.internal_status = 'sample'
            exam.status = exam.internal_status

    def action_sample_done(self):
        self.ensure_one()
        self.date_prelevement = fields.Datetime.now()
        self.technicien_prelevement = self.env.uid
        self.internal_status = 'ongoing'

    def action_done(self):
        self.ensure_one()
        self.date_analyse = fields.Datetime.now()
        self.technicien = self.env.uid
        self.internal_status = 'done'

class ExamenImagerie2(models.Model):
    _name = 'fertility.examen.imagerie2'
    _description = 'Examen d imagerie'
    _inherit = ['mail.thread']
    _order = 'date_request desc, id desc'

    labo_name = fields.Char(string='Labo ID')
    examen_id = fields.Many2one('fertility.examen')

    date_request = fields.Date(string='Date demande', readonly=True, default=fields.Date.today)
    date_analyse = fields.Datetime('Date/Heure analyse')
    date_prelevement = fields.Datetime('Date/Heure prélèvement')
    is_print = fields.Boolean(string="#", default=True)
    examen_text = fields.Html(string="Examen imagerie")


class ExamenImagerie(models.Model):
    _name = 'fertility.examen.imagerie'
    _description = 'Examen'
    _inherit = ['mail.thread']
    _order = 'date_request desc, id desc'

    imagerie_name = fields.Char(string='ID Imagerie')
    examen_id = fields.Many2one('fertility.examen')

    date_request = fields.Date(string='Date demande', readonly=True, default=fields.Date.today)
    date_analyse = fields.Datetime('Date/Heure analyse')
    status = fields.Selection(
        [('draft', 'En attente'), ('invoicing', 'Facturation'), ('protocol', 'Saisie de protocole'),
         ('ongoing', 'En cours'), ('done', 'Fait')], 'Etat', compute='_get_status')
    internal_status = fields.Selection(
        [('draft', 'En attente'), ('invoicing', 'Facturation'), ('protocol', 'Saisie de protocole'),
         ('ongoing', 'Validation'), ('done', 'Fait')], 'Etat', default='draft')
    technicien = fields.Many2one('res.users', string='Par')
    protocol = fields.Text('Protocole')
    description = fields.Text('Résultat')
    analyse = fields.Many2one('product.template', string='Analyse')

    analyses = fields.Many2one('product.product', string='Analyse')
    type_analyse = fields.Many2one(related='analyse.categ_id', store=True)
    valeur_normale = fields.Text(related='analyse.valeur_normale')

    move_id = fields.Many2one('account.move')
    patient_id = fields.Many2one('fertility.patient')
    parent_id = fields.Many2one(related='patient_id.parent_id')
    gender = fields.Selection(related='patient_id.gender')
    age = fields.Integer(related='patient_id.age')

    matricule = fields.Char(related='patient_id.matricule', string="Matricule")
    categorie = fields.Selection(related='patient_id.categorie', string="Catégorie")
    classe = fields.Selection(related='patient_id.classe', string="Classe")

    numero_billet = fields.Char(string="Billet d'envoi")
    email = fields.Char(related='patient_id.email', string="Email")
    phone = fields.Char(related='patient_id.phone', string="Téléphone")
    function = fields.Char(related='patient_id.function', string="Profession")

    is_print = fields.Boolean(string="#", default=True)
    clinique = fields.Html(string="Clinique")
    medecin_demander = fields.Many2one('fertility.doctor', string="Medecin demandeur")
    demandeur = fields.Many2one('res.users', string="Demandé par ")

    move_line_id = fields.Many2one('account.move.line',  compute='_get_account_move_line_id', default=False, string="Line")
    etat_facturation = fields.Boolean(related='move_line_id.etat', string="Payé ?", readonly=True)

    ### 
    url_clicher = fields.Char(string="Voir le cliché")

    is_pathologique = fields.Boolean('R. Pathologique', default=False)
    

    @api.model
    def default_get(self, fields):
        res = super(ExamenImagerie, self).default_get(fields)
        res['demandeur'] = self.env.user.id
        return res

    def _get_account_move_line_id(self):
        #res = []
        for item in self:
            item.move_line_id = self.env['account.move.line'].search([('ref_item','=',item.imagerie_name)]).id
            # if item.move_id:
            #     try:
            #         #logger.info("#####################################################################################skdjsk")
            #         #raise UserError(self.env['account.move.line'].search([('ref_item','=',item.imagerie_name)]).id)
            #         item.move_line_id = self.env['account.move.line'].search([('ref_item','=',item.imagerie_name)]).id

            #     except Exception as e:
            #         raise UserError(Exception)
            # item.move_line_id = 2
                    #item.move_line_id = False
                # return {
                #     'name': 'Patient',
                #     'view_type': 'form',
                #     'view_mode': 'form',
                #     'res_model': 'fertility.patient',
                #     'views': [(form_view_id, 'form')],
                #     'res_id': self.patient_id.id,
                #     'type': 'ir.actions.act_window',
                #     'target': 'new',
                # }
                

    @api.model
    def create(self, vals):
        vals['imagerie_name'] = self.env['ir.sequence'].next_by_code('fertility.imagerie.name')
        return super(ExamenImagerie, self).create(vals)

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, "%s" % (rec.imagerie_name)))
        return result

    def _get_status(self):
        for exam in self:
            if exam.internal_status == 'invoicing':
                if exam.move_id and exam.categorie == 'convention':
                    if exam.move_id.state == 'posted':
                        exam.internal_status = 'protocol' 
                    
                if exam.move_id and exam.categorie != 'convention':
                    if exam.move_id.payment_state in ['partial', 'paid'] and exam.etat_facturation == True:
                        exam.internal_status = 'protocol'
                        
            exam.status = exam.internal_status

    def setStatus(self):
        self.internal_status = 'protocol'

    def action_protocol_done(self):
        self.ensure_one()
        self.internal_status = 'ongoing'

    def action_done(self):
        self.ensure_one()
        self.date_analyse = fields.Datetime.now()
        self.technicien = self.env.uid
        self.internal_status = 'done'
    
    def get_imagerie_resultat(self):
        try:
            form_view_id = self.env.ref("ksoftmedical.view_examenresultat_form").id

        except Exception as e:
            form_view_id = False
        
        return {
            'name': 'Résultat Imagerie',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'fertility.examen.resultat.imagerie',
            'type': 'ir.actions.act_window',
            'views': [(form_view_id, 'form')],
            'target': 'new',
            'context': {
                **self.env.context,
                #'active_ids': self.ids,
                'default_url_clicher': self.url_clicher,
                'default_protocol': self.protocol,
            }
        }

class ExamenResultatImagerie(models.Model):
    _name = 'fertility.examen.resultat.imagerie'
    _description = 'Resultat Examen Imagerie'

    url_clicher = fields.Char(string='ID Imagerie')
    protocol = fields.Text('Protocole')


class ConsulationType(models.Model):
    _name = 'fertility.consultation.type'
    _description = 'Consultation Type'

    name = fields.Char(string='Type de Consultation')
    product_id = fields.Many2one('product.template', string='Produit')
    journal_id = fields.Many2one('account.journal', string='Journal de vente', domain="[('type', '=', 'sale')]")


class PathologieAppointment(models.Model):
    """ Gestion des Pathologies"""

    _inherit = 'module.diagnostics'
    _description = 'Diagnostics'
    _order = 'date_diagnostic desc'

    appointment_id = fields.Many2one('fertility.appointment', string='Appointment')
    saving_pathologie = fields.Boolean(string="OK")
    cancel_pathologie = fields.Boolean(string="NO")
    confirm_status = fields.Selection([('draft', 'Brouillon'), ('conf', 'Confirmer'), ('cancel', 'Annuler')],
                                      default='draft', string='Etat')
    cancel_by = fields.Many2one('res.users', readonly=True, string="Cancel par")
    date_cancel = fields.Datetime(string='Date')
    active = fields.Boolean(default=True)
    
    @api.depends('appointment_id')
    def appointment_patient(self):
        if self.appointment_id:
            self.patient_id = self.appointment_id.patient_id.id

    @api.onchange('saving_pathologie')
    def save_pathologie_medical(self):
        if self.saving_pathologie:
            patho = self.create({
                'pathologie': self.pathologie.id,
                'explication': self.explication,
                'confirm_status':'conf',
                #'saving_pathologie':True,
                #'date_diagnostic': fields.Datetime.now(),
            })

    @api.onchange('cancel_pathologie')
    def cancel_pathologie_medical(self):
        if self.cancel_pathologie:
            patho = self.write({
                'cancel_by': self.env.user.id,
                'confirm_status':'cancel',
                'cancel_pathologie':True,
                'date_cancel': fields.Datetime.now(),
                'active': False,
            })

    def unlink(self):
        #self.ensure_one()
        raise UserError(_("Vous ne pouvez pas effectuer cette action"))

class AppointmentType(models.Model):
    _name = 'fertility.appointment.type'
    _description = 'Appointment Type'

    name = fields.Char(string='Type de Rendez-vous')
    appointment_ids = fields.One2many('fertility.appointment', 'appointment_type')
    count_appointment = fields.Integer(compute='_compute_appointment_count')
    journal_id = fields.Many2one('account.journal', string='Journal de vente', domain="[('type', '=', 'sale')]")
    category_id = fields.Many2one('product.category')
    stimulation_product_id = fields.Many2one('product.template', string='Facturation PMA 1')
    transfer_product_id = fields.Many2one('product.template', string='Facturation PMA 2')

    @api.depends('appointment_ids')
    def _compute_appointment_count(self):
        for type_app in self:
            type_app.count_appointment = len(
                type_app.appointment_ids.filtered(lambda appointment: appointment.date == fields.Date.today()))


class AutresOrientationAppointment(models.Model):
    """ Gestion des autres Orientations médicales dans le circuit ambulatoires"""

    _inherit = 'module.orientation'
    _description = 'Autres Orientations Médicales'
    _order = 'date_orientation desc, id desc'

    orientation_id = fields.Many2one('fertility.appointment', string='Autres Orientations')


class RequestKineToAppointment1(models.Model):
    """ Selection des elements de la kiné depuis la consultation"""

    _inherit =  'module.kine.request'

    kine_request_id = fields.Many2one('fertility.appointment', string='Demande kiné')

class RequestKineToAppointment2(models.Model):
    """ Selection des elements de la kiné depuis la consultation"""

    _inherit =  'module.kinesitheurapie'

    kine_id = fields.Many2one('fertility.appointment', string='Demande kiné')


class Appointment(models.Model):
    _name = 'fertility.appointment'
    _description = 'Appointment'

    _order = 'date desc, id desc'
    _inherits = {
        'account.move': 'consult_move_id',
        'fertility.triage': 'consult_triage_id',
        'fertility.social': 'consult_social_id',
        'fertility.gyneco': 'consult_gyneco_id',
        'fertility.examen': 'consult_examen_id',
    }

    # DELEGATION INHERITANCE
    consult_move_id = fields.Many2one('account.move', required=False, ondelete="cascade")
    status_moved = fields.Selection(related='consult_move_id.payment_state', string="Status Facture")
    consult_triage_id = fields.Many2one('fertility.triage', required=False, ondelete="cascade")
    consult_social_id = fields.Many2one('fertility.social')
    consult_gyneco_id = fields.Many2one('fertility.gyneco', required=False, ondelete="cascade")
    consult_examen_id = fields.Many2one('fertility.examen', required=False, ondelete="cascade", string="Examens")
    consult_examen_img_id = fields.Many2one('fertility.examen', required=False, ondelete="cascade", string="Examens imagerie")
    # PROPERTY
    appointment_type = fields.Many2one('fertility.appointment.type')
    consultation_type = fields.Many2one('fertility.consultation.type')
    internal_status = fields.Selection([
        ('home', 'Reception'),
        ('invoicing', 'Facturation'),
        ('triage', 'Triage'),
        ('attente', 'Attente du médecin'),
        ('consult_gyneco', 'Consultation'),
        ('open', 'En attente'),
        ('closed', 'Fermé'),('transfered', 'Transferé')], string='Status', default='triage')
    status = fields.Selection([
        ('home', 'Reception'),
        ('invoicing', 'Facturation'),
        ('triage', 'Triage'),
        ('attente', 'Attente du médecin'),
        #('wait_doc', 'En attente du medecin'),
        ('consult_gyneco', 'Consultation'),
        ('open', 'En attente'),
        ('closed', 'Fermé'),('transfered', 'Transferé')], compute='_get_status')

    name = fields.Char(string='Name', readonly=True)
    patient_id = fields.Many2one('fertility.patient')
    doctor_id = fields.Many2one('fertility.doctor')
    speciality = fields.Many2one(related='doctor_id.speciality_id', string="Spécialité")
    journal_id = fields.Many2one(related='consultation_type.journal_id')
    product_id = fields.Many2one('product.template')

    product_ids = fields.Many2one('product.product')

    # is_pris = fields.Boolean(string="Est pris", default=False, compute="setEstPris")
    # is_pris = fields.Boolean(string="Est pris", compute="_computePrisePatient")
    is_pris = fields.Selection([('pris', 'Pris'), ('nonp', 'Non pris')], string="En consultation")
    type_vue = fields.Char(string="Vue_type", default="")

    waiting_time = fields.Char(string="En attente depuis", compute="get_waiting_time")
    validation_time = fields.Datetime()
    attente_time = fields.Integer(string="Temps etat attente du medecin")

    ## PATIENT INFO
    prenom = fields.Char(related='patient_id.prenom', string="Prenom", store=True)
    nom = fields.Char(related='patient_id.nom', string="Nom", store=True)
    postnom = fields.Char(related='patient_id.postnom', string="Postnom", store=True)
    birth = fields.Date(related='patient_id.birth', string="Date de naissance", store=True)
    age = fields.Integer(related='patient_id.age', string="Age", store=True)
    function = fields.Char(related='patient_id.function', string="Profession", store=True)
    gender = fields.Selection([('M', 'Masculin'), ('F', 'Féminin')], 'Genre', related='patient_id.gender', store=True)
    conjoint = fields.Many2one(related='patient_id.conjoint', string='Conjoint', store=True)

    parent_id = fields.Many2one(related='patient_id.parent_id', string="Convention", store=True)
    matricule = fields.Char(related='patient_id.matricule', string="Matricule", store=True)
    categorie = fields.Selection(related='patient_id.categorie', string="Catégorie", store=True)
    classe = fields.Selection(related='patient_id.classe', string="Classe", store=True)
    zone = fields.Selection(related='patient_id.zone', string="Zone", store=True)

    numero_billet = fields.Char(string="Billet d'envoi")
    email = fields.Char(related='patient_id.email', string="Email", store=True)
    phone = fields.Char(related='patient_id.phone', string="Téléphone", store=True)
    function = fields.Char(related='patient_id.function', string="Profession", store=True)

    # patient_id = fields.Char(related='patient_id.ID', string="Patient ID")
    # company_name = fields.Char(related='patient_id.prenom', string="Prenom")
    ## ANTECEDENTS

    # # Obstétricaux et Gynécologiques
    # gestite = fields.Char(related='patient_id.gestite')
    # parite = fields.Char(related='patient_id.parite')
    # enfant_vivant = fields.Char(related='patient_id.enfant_vivant')
    # age_dernier_accouchement = fields.Char(related='patient_id.age_dernier_accouchement')
    # total_accouchement = fields.Text(related='patient_id.total_accouchement')
    # total_accouchement_spontane = fields.Text(related='patient_id.total_accouchement_spontane')
    # total_accouchement_instru = fields.Text(related='patient_id.total_accouchement_instru')
    # total_accouchement_cesarienne = fields.Text(related='patient_id.total_accouchement_cesarienne')
    # fausse_spontane = fields.Text(related='patient_id.fausse_spontane')
    # fausse_tardive = fields.Text(related='patient_id.fausse_tardive')
    # grossesse_ectopique = fields.Text(related='patient_id.grossesse_ectopique')
    # interrupt_med_grossesse = fields.Text(related='patient_id.interrupt_med_grossesse')
    # enfant_autres = fields.Text(related='patient_id.enfant_autres')
    # ddr = fields.Char(related='patient_id.ddr')
    # age_premiere_regles = fields.Text(related='patient_id.age_premiere_regles')

    # # Familiaux et héréditairesBoolean
    # infertilite = fields.Text(related='patient_id.infertilite')

    # # Médicaux (si oui, préciser la durée et le traitement en cours)
    # diabete = fields.Text(related='patient_id.diabete')
    # hypertension = fields.Text(related='patient_id.hypertension')
    # obesite = fields.Text(related='patient_id.obesite')
    # asthme = fields.Text(related='patient_id.asthme')
    # dysthyroidie = fields.Text(related='patient_id.dysthyroidie')
    # med_description = fields.Text(related='patient_id.med_description')

    # # Chirurgicaux(Si OUI, préciser l’année)
    # coelioscopie = fields.Text(related='patient_id.coelioscopie')
    # myomectomie = fields.Text(related='patient_id.myomectomie')
    # kystectomie = fields.Text(related='patient_id.kystectomie')
    # curetage = fields.Text(related='patient_id.curetage')
    # cicatrice_sous = fields.Text(related='patient_id.cicatrice_sous')
    # retention_placentaire = fields.Text(related='patient_id.retention_placentaire')
    # cicatrice_sus = fields.Text(related='patient_id.cicatrice_sus')
    # appendicectomie = fields.Text(related='patient_id.appendicectomie')
    # pfannestiel = fields.Text(related='patient_id.pfannestiel')
    # chr_description = fields.Text(related='patient_id.chr_description')

    # # Autres antécédents
    # autres_tabac = fields.Text(related='patient_id.autres_tabac')
    # autres_alcool = fields.Text(related='patient_id.autres_alcool')
    # autres_description = fields.Text(related='patient_id.autres_description')

    # # ATCD
    # atcd_grossesse = fields.Text(related='patient_id.atcd_grossesse')
    # atcd_fiv = fields.Text(related='patient_id.atcd_fiv')
    # atcd_don = fields.Text(related='patient_id.atcd_don')
    # atcd_embryontransfert = fields.Text(related='patient_id.atcd_embryontransfert')
    # atcd_embryonj3 = fields.Text(related='patient_id.atcd_embryonj3')
    # atcd_blastocyste = fields.Text(related='patient_id.atcd_blastocyste')
    # atcd_echec = fields.Text(related='patient_id.atcd_echec')
    # atcd_embryonrestant = fields.Text(related='patient_id.atcd_embryonrestant')
    # atcd_description = fields.Text(related='patient_id.atcd_description')
    # ## ATCD Ophta ###
    allergie = fields.One2many(related='patient_id.allergie', string="Allergie")
    atcd_medical = fields.One2many(related='patient_id.atcd_medical', string="ATCD Médicaux")

    lunettes = fields.Selection(related='patient_id.lunettes')
    # lunettes_comment = fields.Text(related='patient_id.lunettes_comm')
    # derniere_consult = fields.Date(related='patient_id.derniere_consult')
    # atcd_description = fields.Text(related='patient_id.atcd_description')
    # lst_produit = fields.Text(related='patient_id.lst_produit')

    # ## Pre-examen
    # histoire_occ = fields.Text(related='patient_id.histoire_occ')
    raison_cons = fields.Text(string="Raison de la consult")
    refraction = fields.Char(string="Refraction")

    # Acuité Visuelle (A.V)
    od_sc = fields.Char(string="S.C", size=64)
    od_cc = fields.Char(string="C.C", size=64)
    od_ts = fields.Char(string="T.S", size=64)

    os_sc = fields.Char(string="S.C", size=64)
    os_cc = fields.Char(string="C.C", size=64)
    os_ts = fields.Char(string="T.S", size=64)

    # Pression Intra-Oculaire
    # Avant
    od_pression = fields.Float(string="OD (mmHg)", size=64)
    os_pression = fields.Float(string="OS (mmHg)", size=64)
    # Après
    od_pression_apres = fields.Float(string="OD (mmHg)", size=64)
    os_pression_apres = fields.Float(string="OS (mmHg)", size=64)
    # Max
    od_pio_max = fields.Float(string="OD (mmHg)", size=64, related='patient_id.od_pio_max', readonly=False)
    os_pio_max = fields.Float(string="OS (mmHg)", size=64, related='patient_id.os_pio_max', readonly=False)
    # od_pio_max = fields.Float(string="OD (mmHg)", size=64, compute="_action_pioMax", inverse="_inverse_action_pioMax", store=True)
    # os_pio_max = fields.Float(string="OS (mmHg)", size=64, compute="_action_pioMax", inverse="_inverse_action_pioMax", store=True)

    od_pachymetrie = fields.Char(string="OD (µm)", size=64)
    os_pachymetrie = fields.Char(string="OS (µm)", size=64)

    # Distance Pupillaire
    od_dist = fields.Float(string="OD")
    og_dist = fields.Float(string="OG")
    dist_pp = fields.Float(string="PD", store=True, compute="_action_compute_dpp")

    od_dist2 = fields.Float(string="OD")
    og_dist2 = fields.Float(string="OG")
    dist_pp2 = fields.Float(string="PD")

    # Vision des couleurs
    od_vision_coul = fields.Char(string="OD")
    os_vision_coul = fields.Char(string="OS")

    # Refraction
    od_refs = fields.Char(string="S", size=64)
    od_refc = fields.Char(string="C", size=64)
    od_refa = fields.Char(string="A", size=64)

    og_refs = fields.Char(string="S", size=64)
    og_refc = fields.Char(string="C", size=64)
    og_refa = fields.Char(string="A", size=64)

    # Refraction
    pod_refs = fields.Char(string="S", size=64)
    pod_refc = fields.Char(string="C", size=64)
    pod_refa = fields.Char(string="A", size=64)

    pog_refs = fields.Char(string="S", size=64)
    pog_refc = fields.Char(string="C", size=64)
    pog_refa = fields.Char(string="A", size=64)

    # Gouttes
    gouttes = fields.Text(string="Gouttes")

    # Signes vitaux
    temp = fields.Char(string="T (C°)", size=64)
    ta = fields.Char(string="TA (mmHg)", size=64)
    glyc = fields.Char(string="Glycémie (mg/dl )", size=64)
    fr = fields.Char(string="Fr (cpm )", size=64)
    fc = fields.Char(string="Fc (bpm)", size=64)
    taille = fields.Char(string=" Taille (m)", size=64)
    poids = fields.Char(string="Poids (kg)", size=64)
    so = fields.Char(string="Saturation en O2", size=64)

    # BMI
    bmi = fields.Float(string="IMC")
    bmi_state = fields.Selection([('sp', 'SousPoids'), ('normal', 'Normal'), ('srp', 'Surpoids'), ('obez', 'Obèse')],
                                 string="Etat")
    is_bmi = fields.Boolean(string="Calculer l'IMC")
    is_alert = fields.Boolean(string="Alerte", default=False)

    ## END ANTECEDENT

    ## Diagnostics
    diagnostics_ids = fields.One2many('module.diagnostics', 'appointment_id')

    ## Prescriptions
    done_ordonnance = fields.One2many('module.ordonnance.line', 'appointment_id', string="Ordonnances")

    ## Prescriptions lunettes
    done_lunettes = fields.One2many('module.prescription.lunette', 'appointment_id', string="Pres. Lunettes")

    ## Autres Orientations
    done_orientation = fields.One2many('module.orientation', 'orientation_id', string="Autres Orientations")

    ## Kinesitheurapie
    request_kine = fields.One2many('module.kine.request', 'kine_request_id', string="Demande Kiné")
    kinesitheurapie = fields.One2many('module.kinesitheurapie', 'kine_id', string="Kinesitheurapie")
    
    clinique = fields.Html(string="Clinique")
    clinique2 = fields.Html(string="Clinique")

    ##Chirurgie
    done_chirurgie = fields.One2many('module.chirurgie', 'appointment_id', string="Chirurgie")

    # Consultation Sociale
    situation_pro = fields.Html(string="Situation Pro Mr")
    situation_pro2 = fields.Html(string="Situation Pro Mme")
    adresse = fields.Char(string="Residence")
    niveauetude1 = fields.Char(string="Niveau Etude Hoe")
    niveauetude2 = fields.Char(string="Niveau Etude Femme")
    is_first_conslt = fields.Selection([('oui', 'OUI'), ('non', 'NON')], string="Demarche Commune")
    commentaire_demarche = fields.Html(string="Descript. demarche")

    is_antecedent = fields.Selection([('oui', 'OUI'), ('non', 'NON')], string="Antécédents de consult")
    traitement_antcd = fields.Html(string="Traitement réçu")

    is_rapport = fields.Selection([('oui', 'OUI'), ('non', 'NON')], string="Rapport médicaux")
    document_rapport = fields.Html(string="Rapport")

    is_connaissance = fields.Selection([('oui', 'OUI'), ('non', 'NON')], string="Connaissance de traitement")
    traitement_fert = fields.Html(string="Traitement fertilité")

    is_fonct = fields.Selection([('oui', 'OUI'), ('non', 'NON')], string="Expl. fonctionnement FIV")
    cord_commentaire = fields.Text(string="Commentaire")
    cord_commentaire_pharma = fields.Text(string="Commentaire")

    ###
    user_id = fields.Many2one('res.users', 'Crée par:', readonly="True")
    motif_rdv = fields.Text(string="Motif du RDV")

    ##Annotations des médecins
    done_annotation = fields.One2many('module.annotation', 'annotation_id', string="Annotations")
    done_signes_vitaux = fields.One2many('module.signes.vitaux', 'signesV_id', string="Signes vitaux")

    done_feuille_signes_vitaux = fields.One2many('module.feuille.surveillance', 'feuille_signesV_id', string="Signes vitaux")

    ## Chirurgie
    cord_commentaire = fields.Text(string="Commentaire")

    # Signature infirmière
    infirmiere_id = fields.Many2one('res.users', 'Infirmière:', readonly="True")

    #Re-ouverture du dossier
    re_ouver_par = fields.Many2one('res.users', 'Re-ouver par:', readonly="True")
    is_re_ouvert = fields.Boolean(string="Re-ouvert")
    show_last_cons = fields.Boolean(string="Cons préc", default=True)

    #Resumé pre-examen et antecedents
    resume = fields.Html(string="Resumé")

    av_pio_last_consultation = fields.Html(string="Dernière consultation")

    type_lunette = fields.Many2one('fertility.types.lunettes', 'Type de lunette')

    pre_exam_antecedent = fields.Html(string="Pre-examen et antecedents")

    ##
    anamnese = fields.Text(string="Plaintes")
    hstr_affection = fields.Text(string="Histoire de l'affection")
    cpm_anamnese = fields.Text(string="Compléments d’anamnèse")
    examen_physique = fields.Text(string="Examen physique")
    traitement = fields.Text(string="Traitement")
    
    afficher_patient = fields.Boolean(string="Afficher les info patients", default=False)
    ## Ophta
    type_consultation = fields.Selection([('stand', 'Standard'),('ophta', 'Ophtamologie'),('dent', 'Dentiste'),
                                            ('gync', 'Gynéco-Obstétrique'),('vasc', 'Vasculaire'),('nephr', 'Nephrologue'),
                                            ('autres', 'Autres'),], default='stand',string="Type de consultation")
                                  
    ac_odbrute = fields.Char(string="OD Brute")
    ac_ogbrute = fields.Char(string="OG Brute")
    ac_addbrute = fields.Char(string="Add Brute")
    
    ac_odcorrige = fields.Char(string="OD Corrigé")
    ac_ogcorrige = fields.Char(string="OG Corrigé")
    
    ac_odcorrection = fields.Char(string="OD Correction")
    ac_ogcorrection = fields.Char(string="OD Correction")
    ac_addcorrection = fields.Char(string="Add Correction")
    
    insp_palpation = fields.Text(string="Inspection Palpation")
    fond_oeil = fields.Text(string="Fond d'oeil")
    tonometrie = fields.Text(string="Tonomètrie")
    autres_examen = fields.Text(string="Autres examens")
    
    od_biomi = fields.Char(string="OD")
    og_biomi = fields.Char(string="OG")
    
    ref_od = fields.Char(string="OD")
    ref_ag = fields.Char(string="OG")
    ref_dp = fields.Char(string="DP")
    
    ## Transfert patient
    hospi_id = fields.Many2one('module.hospitalisation', string="Hospitalisation")

    ## Gestion de temps dans différents services
    date = fields.Date(required=True, string="Date de rdv")
    datetime = fields.Datetime('D. arrivé triage', required=False)
    date_triage_2 = fields.Datetime('D. depart triage', required=False)

    date_cons_1 = fields.Datetime('D. arrivé cab.', required=False)
    date_cons_2 = fields.Datetime('D. depart cab.', required=False)

    is_diagnostic = fields.Boolean(string="Pas de diagnostic", default=False)
    check_diagnostic = fields.Integer(string="Check Diagnostic",)

    ### Type de rdv
    time_rdv = fields.Selection([('immed', 'Immediat'),
                                 ('rdv', 'Rendez-vous')], default='immed',
                                  string="Type de rdv")

    ### Salle de soins
    salle_soins = fields.Many2one('ksoft.services', string="Salle de soins")
    type_service = fields.Selection([('adm','Administration'),
                                 ('cons','Consultation'),
                                 ('urg','Urgence'),('rea','Réanimation'),('hospi','Hospitalisation'),
                                 ('soins','Soins ambulatoires'),('labo','Laboratoire'),
                                 ('pharma','Pharmacie'),('shop','Shop Optique'),
                                 ('img','Imagerie'),('vac','Vaccination'),('chi','Chirurgie'),
                                 ('dial','Dialyse')],
                                related='salle_soins.type_rdv',
                                readonly="True", string="Type de rdv", store=True)

    salle_soins_tampon = fields.Many2one('ksoft.services', compute="_get_salle_soins_tampon", store=True, string="Salle de soins")

    type_cas = fields.Selection([('new', 'Nouveau Cas'),
                                 ('anc', 'Ancien Cas')], 
                                  string="Type de Cas")
                                                               
    note_infirmier = fields.Text(string="Notes Infirmières")
    
    type_transfert = fields.Selection([('avcdoc', 'Avc Document'),
                                 ('sdoc', 'Sans Document')], 
                                  string="Type de Transfert")
    origine_patient = fields.Selection([('domicile', 'Domicile'),
                                 ('centre', 'Centre de Santé'),('ailleurs', 'Ailleurs')], 
                                  string="Origine patient")
    
    nom_centre = fields.Char(string="Hopital d'Orgine")
    
    instruction_soins = fields.Text(string="Instruction Médicale")
    
    ### Résumé de consultation
    resume_consult = fields.Html(string="Résumé Consultation")
    
    ### Résumé antécédents
    resume_atcd = fields.Html(related='patient_id.resume_atcd',string="Résumé Antécédent")

    resume_diagnost = fields.Html(compute='_get_last_diagnostics',string="Résumé Diagnostics")
    
    

    def confirmer_atcd(self):
        for atcd in self.atcd_medical:
            atcd.get_patient_atcd_medical()
    
    def cancel_atcd(self):
        for atcd in self.atcd_medical:
            atcd.cancel_atcd_medical()


    @api.onchange('type_consultation')
    def set_examen_physique(self):
        cont = ""
        if self.type_consultation == 'stand':
            if self.examen_physique == '':
                cont += "<ul style='list-style-type: none;'>"
                cont += "<p><strong><h5>Evaluation générale</h5></strong></p></br>"
                cont += "<p><strong><h5>Examen de la peau</h5></strong></p></br>"
                cont += "<p><strong><h5>Tête et cou</h5></strong></p></br>"
                cont += "<p><strong><h5>Thorax et du système cardio-respiratoire</h5></strong></p></br>"
                cont += "<p><strong><h5>Abdomen</h5></strong></p></br>"
                cont += "<p><strong><h5>Système musculosquelettique</h5></strong></p></br>"
                cont += "<p><strong><h5>Système neurologique</h5></strong></p></br>"
                cont += "</ul>"
                
                #self.examen_physique = cont
            else:
                cont = self.examen_physique
                
            self.examen_physique = cont
            
        else:
            self.examen_physique = cont
    
    @api.depends('diagnostics_ids')
    def _get_last_diagnostics(self):
        #content =""
        for appointment_id in self:
            rhs = gp = ''
            list_diag = []
            diagnostics = self.env['module.diagnostics'].search([('patient_id','=',appointment_id.patient_id.id)])
            list_diag = []
            content =""
            if diagnostics:
                content += '<table class="table">'
                content += '<tr><th width="20%" style="text-align:center">DATE</th><th width="30%" style="text-align:center">DIAGNOSTICS</th>'
                content += '<th width="30%" style="text-align:center">COMMENTAIRE</th><th width="20%" style="text-align:center">MEDECIN</th></tr>'
                content += '<tr><th colspan="4" style="text-align:center;" class="table-info">Affichage limité aux 3 derniers diagnostics. Pour voir plus, cliquez sur le button "Diagnostics"</th>'
                list_diag = diagnostics[-3:]
                #raise UserError(diagnostics)
                for diag_id in list_diag:
                    content += '<tr><td>'+ str((diag_id.date_diagnostic).strftime("%d/%m/%Y")) +'</td>'
                    content += '<td>'+ str(diag_id.pathologie.name) +'</td>'
                    content += '<td>'+ str(diag_id.explication) +'</td>'
                    content += '<td>'+ str(diag_id.medecin_diag.partner_id.display_name) +'</td></tr>'
                
                content += '</table>'
                
            #appointment_id.write({'resume_diagn':content})
            
            #for diag in self:
            appointment_id.resume_diagnost = content

    def action_save_consultation(self):
        ## Examen medical générale
        content = ""
        atcde_vide = False
        diagn_vide = False
        for appointment_id in self:

            atcde_vide = appointment_id.atcd_medical.filtered(lambda atcd: atcd.etat == False)
            diagn_vide = appointment_id.diagnostics_ids.filtered(lambda diag: diag.saving_pathologie == False)

            if atcde_vide or diagn_vide:
                raise UserError("Veuillez confirmer tous les antécédents et diagnostics avant de sauvegarder la consultation")

            if appointment_id:
                content += '<h5 style="border: 1px solid #333;box-shadow: 8px 8px 5px #444;padding: 8px 12px;background-color:#CCCCCC;text-color:#ffffff; text-align:center">Vue par le '+ str(appointment_id.date) +' <b>Dr '+ str(appointment_id.doctor_id.name) +'</b> pour '+ str(appointment_id.product_id.name) +'</h5>'
                content += '<table width="100%" border=0>'
                #if appointment_id.anamnese or appointment_id.examen_physique:
                content += '<tr><td style="width:49%;vertical-align:top; padding:5px;"><p><b>Plaintes:</b><br/>'+ str(appointment_id.anamnese) +'</p></td>'
                content += '<td style="width:49%;vertical-align:top; padding:5px;"><p><b>Examen Physique:</b><br/>'+ str(appointment_id.examen_physique) +'</p></td></tr>'
                
                content += '<tr><td style="width:49%;vertical-align:top; padding:5px;"><p><b>Histoire de la maladie:</b><br/>'+ str(appointment_id.hstr_affection) +'</p></td>'
                content += '<td style="width:49%;vertical-align:top; padding:5px;"><p><b>Complèments d\'anamnèse:</b><br/>'+ str(appointment_id.cpm_anamnese) +'</p></td></tr>'
                
                content += '<tr><td style="width:49%;vertical-align:top; padding:5px;"><p><b>Traitement:</b><br/>'+ str(appointment_id.traitement) +'</p></td><td style="width:49%;"></td></tr>'
     
                content += '</table>'
              
            appointment_id.write({'resume_consult':content})
            #return content
        
    @api.onchange('is_diagnostic')
    def check_diagnistic_ligne(self):
        if self.is_diagnostic == True:
            if len(self.diagnostics_ids) >= 1 :
                self.check_diagnistic_ligne2()
              
    def check_diagnistic_ligne2(self):

        self.is_diagnostic = False
        raise UserError("Un diagnostic existe déjà, veillez retirer le diagnostic avant d'effectuer cette action")
    
    @api.onchange('salle_soins')
    def _get_salle_soins_tampon(self):
        for record in self:
            if record.salle_soins:
                record.salle_soins_tampon = record.salle_soins.id 

    ### Compute patient waiting time
    @api.model
    def get_waiting_time(self):
        for appoint in self:
            if appoint.validation_time:
                attente_time = appoint.date_diff_in_seconds(datetime.now(), appoint.validation_time)
                appoint.waiting_time = appoint.dhms_from_seconds_conditionnel(attente_time)
                if appoint.internal_status != 'attente':
                    appoint.waiting_time = ""
            else:
                appoint.waiting_time = ""

    def date_diff_in_seconds(self, dt2, dt1):
        timedelta = dt2 - dt1
        a = timedelta.days * 24 * 3600 + timedelta.seconds
        return a

    def dhms_from_seconds_conditionnel(self, seconds):

        if seconds > 0 and seconds < 60:
            # minutes, seconds = divmod(seconds, 60)
            remaining_time = str(seconds) + "Sec"

        elif seconds >= 60 and seconds < 3600:
            minutes, seconds = divmod(seconds, 60)
            res = minutes, seconds
            remaining_time = str(res[0]) + "M " + str(res[1]) + "S"

        elif seconds >= 3600 and seconds < 86400:
            minutes, seconds = divmod(seconds, 60)
            hours, minutes = divmod(minutes, 60)
            res = hours, minutes, seconds
            remaining_time = str(res[0]) + "H " + str(res[1]) + "M " + str(res[2]) + "S"

        elif seconds >= 86400:
            minutes, seconds = divmod(seconds, 60)
            hours, minutes = divmod(minutes, 60)
            days, hours = divmod(hours, 24)
            res = days, hours, minutes, seconds
            remaining_time = str(res[0]) + "J " + str(res[1]) + "H " + str(res[2]) + "M " + str(res[3]) + "S"
        else:
            remaining_time = seconds

        return remaining_time

    # Pour savoir si le patient est deja pris par le medecin
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        res = super(Appointment, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        #add here your condition
        #raise UserError(res)

        return res
        
        
    def open_list_appointment(self):
        if self:
            list_appoint = self.action_open_list_appointment(self.patient_id.id)
            return list_appoint
            
    def historique_appointment(self):
        if self:
            hist_appoint = self.action_historique_appointment(self.patient_id.id)
            return hist_appoint 
            
    def open_list_medicament(self):
        if self:
            list_medicmnt = self.action_open_list_medicament(self.patient_id)
            return list_medicmnt  
                
    def open_list_imagerie(self):
        if self:
            list_imagerie = self.action_open_list_imagerie(self.patient_id)
            return list_imagerie  
            
    def open_list_labo(self):
        if self:
            list_labo = self.action_open_list_labo(self.patient_id)
            return list_labo 
            
    def historique_diagnostic(self):
        if self:
            hist_diag = self.action_open_historique_diagnostic(self.id)
            return hist_diag 
                
    def open_list_surveillance(self):
        if self:
            list_surveillance = self.action_open_historique_feuillesurveillance(self.patient_id.id)
            return list_surveillance
                
    ## Function de présentation du dossier patient          
    def action_open_list_invoices(self):
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        action.update({'target': 'new','domain':[('partner_id','=',self.partner_id.id),('move_type','=','out_invoice')]})
        return action
    
    def action_open_list_appointment(self, patient):
        action = self.env.ref('ksoftmedical.action_dossierappointment_patient').read()[0]
        action.update({'target': 'new','domain':[('patient_id','=',patient)]})
        return action
        
    def action_historique_appointment(self, patient):
        action = self.env.ref('ksoftmedical.action_list_appointment').read()[0]
        action.update({'target': 'new','domain':[('patient_id','=',patient),('internal_status','in',('consult_gyneco','open','closed','transfered'))]})
        return action
        
    def action_open_historique_feuillesurveillance(self, patient):
        action = self.env.ref('ksoftmedical.action_feuille_signesvitaux_all').read()[0]
        action.update({'target': 'new','domain':[('patient_id','=',patient)]})
        return action
    
    def action_open_historique_diagnostic(self, patient):
        action = self.env.ref('ksoftmedical.action_diagnostic_view').read()[0]
        action.update({'target': 'new','domain':[('patient_id','=',patient)]})
        return action   
        
    def action_open_list_labo(self, patient):
        action = self.env.ref('ksoftmedical.action_resultat_all_view').read()[0]
        action.update({'target': 'new','domain':[('patient_id','=',patient),('internal_status','=','done')]})
        return action
        
    def action_open_list_medicament(self, patient):
        action = self.env.ref('ksoftmedical.action_hsitorique_medicament_prescris').read()[0]
        action.update({'target': 'new','domain':[('patient_id','=',patient)]})
        return action
        
    def action_open_sommaire_laboresult(self):
        action = self.env.ref('ksoftmedical.action_resultatlabo_all').read()[0]
        action.update({'target': 'new','domain':[('patient_id','=',self.patient_id.id),('internal_status','=','done')]})
        return action
        
    def action_open_sommaire_imagerieresult(self):
        action = self.env.ref('ksoftmedical.action_resultatimagerie_all').read()[0]
        action.update({'target': 'new','domain':[('patient_id','=',self.patient_id.id),('internal_status','=','done')]})
        return action
    
    def action_open_sommaire_feuillesurveillance(self):
        action = self.env.ref('ksoftmedical.action_feuille_signesvitaux_all').read()[0]
        action.update({'target': 'new','domain':[('patient_id','=',self.patient_id.id)]})
        return action

    def get_pre_exam_antecedents(self):
        #appointments = self.env['fertility.appointment'].search([('patient_id', '=', patient)], limit=1)
        content = ''
        content += '<table width="600" border=1>'
        content += '<tr style="background-color:#A2E6CC;text-align:center"><th width="600" colspan="6"><b>A.V.</b></th></tr>'
        content += '<tr style="background-color:#A2E6CC;text-align:center"><th width="300" colspan="3" ><b>OD<b/></td><th width="300" colspan="3"><b>OG</b></th></tr>'
        content += '<tr style="background-color:#A2E6CC;text-align:center"><th width="100" ><b>SC<b/></td><th width="100"><b>CC</b></th><th width="100"><b>TS</b></th><th width="100" ><b>SC<b/></td><th width="100"><b>CC</b></th><th width="100"><b>TS</b></th></tr>'
        content += '<tr style="text-align:center"><td>'+ str(self.od_sc) +'</td><td>' + str(self.od_cc) +'</td><td>'+ str(self.od_ts) +'</td><td>'+ str(self.os_sc) +'</td><td>'+ str(self.os_cc) +'</td><td>' + str(self.os_ts) + '</td></tr>'
        content += '</table>'
        content += '<table width="600" border=1>'
        content += '<tr style="background-color:#A2E6CC;text-align:center"><th width="600" colspan="6"><b>PIO</b></th></tr>'
        content += '<tr style="background-color:#A2E6CC;text-align:center"><th width="200" colspan="2"><b>MAX</b></th><th width="200" colspan="2"><b>AVANT</b></th><th width="200" colspan="2"><b>APRES</b></th></tr>'
        content += '<tr style="background-color:#A2E6CC;text-align:center"><th><b>OD<b/></td><th><b>OS</b></th><th><b>OD<b/></td><th><b>OS</b></th><th><b>OD<b/></td><th><b>OS</b></th></tr>'
        content += '<tr style="text-align:center"><td>' + str(self.od_pio_max) + '</td><td>' + str(self.os_pio_max) + '</td><td>' + str(self.od_pression)+ '</td><td>'+ str(self.os_pression)+'</td><td>' + str(self.od_pression_apres)+'</td><td>' + str(self.os_pression_apres)+'</td></tr>'
        content += '</table>'
        content += '<table width="600" border=1>'
        content += '<tr style="background-color:#A2E6CC;text-align:center"><th width="300" colspan="2"><b>PACHYMETRIE</b></th><th width="300" colspan="2"><b>VIS.COUL.</b></th></tr>'
        content += '<tr style="background-color:#A2E6CC;text-align:center"><th><b>OD<b/></td><th><b>OS</b></th><th><b>OD<b/></td><th><b>OS</b></th></tr>'
        content += '<tr style="text-align:center"><td>' + str(self.od_pachymetrie) + '</td><td>' + str(self.os_pachymetrie) + '</td><td>' + str(self.od_vision_coul)+ '</td><td>'+ str(self.os_vision_coul)+'</td></tr>'
        content += '</table>'
        content += '<table width="600" border=1>'
        content += '<tr style="background-color:#A2E6CC;text-align:center"><th width="300" colspan="2"><b>REFRACTION</b></th><th width="300" colspan="2"><b>TRANSPOSITION</b></th></tr>'
        content += '<tr style="background-color:#A2E6CC;text-align:center"><th><b>OD<b/></td><th><b>OS</b></th><th><b>OD<b/></td><th><b>OS</b></th></tr>'

        A = str(self.od_refs) if self.od_refs else ''
        B = str(self.od_refc) if self.od_refc else ''
        C = str(self.od_refa) if self.od_refa else ''
        D = str(self.og_refs) if self.og_refs else ''
        E = str(self.og_refc) if self.og_refc else ''
        F = str(self.og_refa) if self.og_refa else ''
        G = str(self.pod_refs) if self.pod_refs else ''
        H = str(self.pod_refc) if self.pod_refc else ''
        I = str(self.pod_refa) if self.pod_refa else ''
        J = str(self.pog_refs) if self.pog_refs else ''
        K = str(self.pog_refc) if self.pog_refc else ''
        L = str(self.pog_refa) if self.pog_refa else ''

        content += '<tr style="text-align:center"><td><ul><li>' + "S:" + A +'</li>' + '<li>' "C:" + B + '</li><li>' "A :" + C + '</li></ul></td><td><ul><li>' + "S:" + D + '</li><li>' + "C:" + E + '</li><li>' + "A:" + F + '</li></ul></td><td><ul><li>' + "S:" + G +'</li>' + '<li>' "C:" + H + '</li><li>' "A :" + I + '</li></ul></td><td><ul><li>' + "S:" + J + '</li><li>' + "C:" + K + '</li><li>' + "A:" + L + '</li></ul></td></tr>'
        content += '</table>'
        content += '<table width="600" border=1>'
        content += '<tr style="background-color:#A2E6CC;text-align:center"><th width="600" colspan="3"><b>DIST. PUPILLAIRE</b></th></tr>'
        content += '<tr style="background-color:#A2E6CC;text-align:center"><th width="200"><b>OD</b></th><th width="200"><b>OS</b></th><th width="200"><b>PD</b></th></tr>'
        content += '<tr style="text-align:center"><td>' + str(self.od_dist) + '</td><td>' + str(self.og_dist) + '</td><td>' + str(self.dist_pp)+ '</td></tr>'
        content += '</table>'
        return content

    # Actualiser pre_exam dans fich. Obs
    def refresh_pre_exam(self):
        self.pre_exam_antecedent = self.get_pre_exam_antecedents()

    # Pour Payer après
    def setInternalStatus(self):
        self.internal_status = 'triage'

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('fertility.appointment.name')
        return super(Appointment, self).create(vals)

    def unlink(self):
        self.ensure_one()
        # self.consult_move_id.unlink()
        # self.consult_triage_id.unlink()
        # self.consult_social_id.unlink()
        # self.consult_gyneco_id.unlink()
        # self.consult_labo_id.unlink()
        # self.consult_imagerie_id.unlink()
        #return super(Appointment, self).unlink()
        raise UserError(_("Vous ne pouvez pas effectuer cette action"))

    def action_validate_home(self):
        product_id = self.consultation_type.product_id
        line_section = self.appointment_type.name

        lines = [(0, 0,
                  {'display_type': 'line_section', 'name': line_section, 'debit': 0, 'credit': 0, 'account_id': False}),
                 (0, 0, {'product_id': self.product_id.id, 'price_unit': self.product_id.list_price, 'quantity': 1})]

        ctx = self.env.context.copy()
        ctx.update({'default_move_type': 'out_invoice', 'default_partner_id': self.patient_id.partner_id.id})
        self.consult_move_id.write({
            'move_type': 'out_invoice',
            # 'journal_id':self.appointment_type.journal_id.id,
            'partner_id': self.patient_id.partner_id.id,
            'ref': self.name,
            'invoice_line_ids': lines
        })
        # self.consult_move_id.with_context(ctx).write({        })

        self.internal_status = 'invoicing'

    @api.depends('od_dist', 'og_dist')
    def _action_compute_dpp(self):
        for app in self:
            app.dist_pp = app.od_dist + app.og_dist
            app.od_dist2 = app.od_dist
            app.og_dist2 = app.og_dist
            app.dist_pp2 = app.dist_pp

    @api.onchange('is_bmi')
    def action_compute_bmi(self):
        bmi = 0
        etat = ""
        if self.height > 0:
            bmi = self.weight * (self.height * self.height)

            if bmi < 18.5:
                etat = "sp"
            elif bmi < 25 and bmi > 18.5:
                etat = "normal"
            elif bmi < 30 and bmi > 25:
                etat = "srp"
            else:
                etat = "obez"
                self.is_alert = True

            self.bmi = bmi
            self.bmi_state = etat
        else:
            raise UserError(_("La Taille doit être superieur à 0"))

    def action_validate_triage(self):
        self.internal_status = 'attente'
        self.gyneco_datetime = fields.Datetime.now()
        self.date = fields.Date.today()
        self.infirmiere_id = self.env.user.id
        self.env['sh.announcement'].notifmedecins()
        self.pre_exam_antecedent = self.get_pre_exam_antecedents()
        self.validation_time = fields.Datetime.now()
        self.date_triage_2 = fields.Datetime.now()

    def action_launch_consultation(self):
        self.internal_status = 'consult_gyneco'
        self.date_cons_1 = fields.Datetime.now()
        self.attente_time = self.date_diff_in_seconds(datetime.now(), self.validation_time)

    def action_validate_social(self):
        self.internal_status = 'consult_gyneco'
        self.gyneco_datetime = fields.Datetime.now()

    def action_validate_gyneco(self):
        self.internal_status = 'open'
        
    def action_send_exam(self):
        imagerie_ids = self.consult_examen_id.imagerie_ids.filtered(lambda imagerie: imagerie.status == 'draft')
    
    def action_send_sanspayer_examimagerie(self):
        ## Check la categorie pour placer dans le journal qui convient
        journal_id = self.env['ksoft.appointment'].get_journal_type(self.categorie)

        # Recupération dans une liste des examens d'imagérie selectionnés dans le champs "imagerie_ids"
        imagerie_ids = self.consult_examen_id.imagerie_ids.filtered(lambda imagerie: imagerie.status == 'draft')

        # Recupération dans une liste des examens de laboratoire selectionnés dans le champs "labo_ids"
        labo_ids =  self.consult_examen_id.labo_ids.filtered(lambda labo: labo.status == 'draft')

        #{'move_line_id':[line.id for line in self.env['account.move'].browse(move_id.id).invoice_line_ids if line.ref_item == self.env['fertility.examen.imagerie'].browse(img.id).imagerie_name]}
        #raise UserError(_("#####  ERERER %s", ))
        if self.consult_examen_id:
        ## Creation facture laboratoire
            if labo_ids:
                lines = []
                lines = [(0, 0, {'display_type': 'line_section', 'name': 'Laboratoire', 'debit': 0, 'credit': 0,
                                 'account_id': False})]

                for labo in labo_ids:
                    #### Recuperer le prix selon la liste de prix defini
                    product_context = dict(
                        self.env.context,
                        partner_id=self.patient_id.partner_id.id,
                        date=fields.Date.today(),
                        uom=labo.analyse.uom_id.id,
                    )

                    prix, ruled = self.patient_id.partner_id.property_product_pricelist.with_context(
                        product_context).get_product_price_rule(
                        labo.analyse, 1,
                        self.patient_id.partner_id) if self.patient_id.partner_id.property_product_pricelist else self.product.list_price

                    # raise UserError(_("##### %s", product_context))

                    lines.extend((0, 0, {
                        'product_id': self.env['product.product'].search([('product_tmpl_id', '=', labo.analyse.id)]).id,
                        'price_unit': prix, 
                        'ref_item':labo.labo_name,
                        'quantity': 1}))


                move_id = self.env['account.move'].create({
                    'move_type': 'out_invoice',
                    'journal_id': journal_id,
                    'patient_id': self.patient_id.id,
                    'numero_billet': self.numero_billet,
                    
                    'convention_id': self.parent_id.id,
                    'matricule': self.matricule,
                    'categorie': self.categorie,
                    'classe': self.classe,
                    'libelle':'laboratoire',
                    
                    'service_id2': self.env['ksoft.services'].search([('type_rdv','=','labo')]).id,
                    'medecin_id2': self.doctor_id.id,

                    'partner_id': self.patient_id.partner_id.id,
                    'ref': self.name,
                    'invoice_line_ids': lines
                })


                ### màj de la demande d'examen de labo créée
                #raise UserError(_([line.id for line in self.env['account.move'].browse(move_id.id).invoice_line_ids if line.ref_item == self.env['fertility.examen.labo'].browse(labo.id).labo_name]))
                labo_ids.write({'move_id': move_id.id, 'internal_status': 'sample', 'patient_id': self.patient_id.id,
                                'medecin_demander': self.doctor_id.id,
                                })
                #'move_line_id':[line.id for line in self.env['account.move'].browse(move_id.id).invoice_line_ids if line.ref_item == self.env['fertility.examen.labo'].browse(labo.id).labo_name]
                #raise UserError(_("#####  ERERER %s", self.consult_examen_id))

                # Notification reception
                self.env['sh.announcement'].notifImagerieReception()

            ## Creation facture imagerie
            if imagerie_ids:
                lines = []
                lines = [(0, 0, {'display_type': 'line_section', 'name': 'Imagerie', 'debit': 0, 'credit': 0,
                                 'account_id': False})]

                for img in imagerie_ids:
                    #### Recuperer le prix selon la liste de prix defini
                    product_context = dict(
                        self.env.context,
                        partner_id=self.patient_id.partner_id.id,
                        date=fields.Date.today(),
                        uom=img.analyse.uom_id.id,
                    )

                    prix, ruled = self.patient_id.partner_id.property_product_pricelist.with_context(
                        product_context).get_product_price_rule(
                        img.analyse, 1,
                        self.patient_id.partner_id) if self.patient_id.partner_id.property_product_pricelist else self.product.list_price

                    # raise UserError(_("##### %s", product_context))

                    lines.extend((0, 0, {
                        'product_id': self.env['product.product'].search([('product_tmpl_id', '=', img.analyse.id)]).id,
                        'price_unit': prix, 
                        'ref_item':img.imagerie_name,
                        'quantity': 1}))

                move_id = self.env['account.move'].create({
                    'move_type': 'out_invoice',
                    'journal_id': journal_id,

                    'patient_id': self.patient_id.id,
                    'numero_billet': self.numero_billet,

                    'convention_id': self.parent_id.id,
                    'matricule': self.matricule,
                    'categorie': self.categorie,
                    'classe': self.classe,
                    'libelle':'imagerie',
                    
                    'service_id2': self.env['ksoft.services'].search([('type_rdv','=','img')]).id,
                    'medecin_id2': self.doctor_id.id,

                    'partner_id': self.patient_id.partner_id.id,
                    'ref': self.name,
                    'invoice_line_ids': lines
                })
                ### màj de la demande d'examen d'imagerie créée
                #raise UserError(_([line.id for line in self.env['account.move'].browse(move_id.id).invoice_line_ids if line.ref_item == self.env['fertility.examen.imagerie'].browse(img.id).imagerie_name]))
                imagerie_ids.write({'move_id': move_id.id, 'internal_status': 'protocol', 'patient_id': self.patient_id.id,
                                    'medecin_demander': self.doctor_id.id,
                                    })

                # Notification reception
                self.env['sh.announcement'].notifImagerieReception()
        else:
            raise UserError(_("Vous n'avez selectionné aucun examens d'imagerie et/ou de laboratoire"))
            print("Pas de imagerie_ids")

    
    def action_send_examimagerie(self):
        ## Check la categorie pour placer dans le journal qui convient
        journal_id = self.env['ksoft.appointment'].get_journal_type(self.categorie)

        # Recupération dans une liste des examens d'imagérie selectionnés dans le champs "imagerie_ids"
        imagerie_ids = self.consult_examen_id.imagerie_ids.filtered(lambda imagerie: imagerie.status == 'draft')

        # Recupération dans une liste des examens de laboratoire selectionnés dans le champs "labo_ids"
        labo_ids =  self.consult_examen_id.labo_ids.filtered(lambda labo: labo.status == 'draft')

        #{'move_line_id':[line.id for line in self.env['account.move'].browse(move_id.id).invoice_line_ids if line.ref_item == self.env['fertility.examen.imagerie'].browse(img.id).imagerie_name]}
        #raise UserError(_("#####  ERERER %s", ))
        if self.consult_examen_id:
        ## Creation facture laboratoire
            if labo_ids:
                lines = []
                lines = [(0, 0, {'display_type': 'line_section', 'name': 'Laboratoire', 'debit': 0, 'credit': 0,
                                 'account_id': False})]

                for labo in labo_ids:
                    #### Recuperer le prix selon la liste de prix defini
                    product_context = dict(
                        self.env.context,
                        partner_id=self.patient_id.partner_id.id,
                        date=fields.Date.today(),
                        uom=labo.analyse.uom_id.id,
                    )

                    prix, ruled = self.patient_id.partner_id.property_product_pricelist.with_context(
                        product_context).get_product_price_rule(
                        labo.analyse, 1,
                        self.patient_id.partner_id) if self.patient_id.partner_id.property_product_pricelist else self.product.list_price

                    # raise UserError(_("##### %s", product_context))

                    lines.extend((0, 0, {
                        'product_id': self.env['product.product'].search([('product_tmpl_id', '=', labo.analyse.id)]).id,
                        'price_unit': prix, 
                        'ref_item':labo.labo_name,
                        'quantity': 1}))


                move_id = self.env['account.move'].create({
                    'move_type': 'out_invoice',
                    'journal_id': journal_id,
                    'patient_id': self.patient_id.id,
                    'numero_billet': self.numero_billet,
                    
                    'convention_id': self.parent_id.id,
                    'matricule': self.matricule,
                    'categorie': self.categorie,
                    'classe': self.classe,
                    'libelle':'laboratoire',
                    
                    'service_id2': self.env['ksoft.services'].search([('type_rdv','=','labo')]).id,
                    'medecin_id2': self.doctor_id.id,

                    'partner_id': self.patient_id.partner_id.id,
                    'ref': self.name,
                    'invoice_line_ids': lines
                })


                ### màj de la demande d'examen de labo créée
                #raise UserError(_([line.id for line in self.env['account.move'].browse(move_id.id).invoice_line_ids if line.ref_item == self.env['fertility.examen.labo'].browse(labo.id).labo_name]))
                labo_ids.write({'move_id': move_id.id, 'internal_status': 'invoicing', 'patient_id': self.patient_id.id,
                                'medecin_demander': self.doctor_id.id,
                                })
                #'move_line_id':[line.id for line in self.env['account.move'].browse(move_id.id).invoice_line_ids if line.ref_item == self.env['fertility.examen.labo'].browse(labo.id).labo_name]
                #raise UserError(_("#####  ERERER %s", self.consult_examen_id))

                # Notification reception
                self.env['sh.announcement'].notifImagerieReception()

            ## Creation facture imagerie
            if imagerie_ids:
                lines = []
                lines = [(0, 0, {'display_type': 'line_section', 'name': 'Imagerie', 'debit': 0, 'credit': 0,
                                 'account_id': False})]

                for img in imagerie_ids:
                    #### Recuperer le prix selon la liste de prix defini
                    product_context = dict(
                        self.env.context,
                        partner_id=self.patient_id.partner_id.id,
                        date=fields.Date.today(),
                        uom=img.analyse.uom_id.id,
                    )

                    prix, ruled = self.patient_id.partner_id.property_product_pricelist.with_context(
                        product_context).get_product_price_rule(
                        img.analyse, 1,
                        self.patient_id.partner_id) if self.patient_id.partner_id.property_product_pricelist else self.product.list_price

                    # raise UserError(_("##### %s", product_context))

                    lines.extend((0, 0, {
                        'product_id': self.env['product.product'].search([('product_tmpl_id', '=', img.analyse.id)]).id,
                        'price_unit': prix, 
                        'ref_item':img.imagerie_name,
                        'quantity': 1}))

                move_id = self.env['account.move'].create({
                    'move_type': 'out_invoice',
                    'journal_id': journal_id,

                    'patient_id': self.patient_id.id,
                    'numero_billet': self.numero_billet,

                    'convention_id': self.parent_id.id,
                    'matricule': self.matricule,
                    'categorie': self.categorie,
                    'classe': self.classe,
                    'libelle':'imagerie',
                    
                    'service_id2': self.env['ksoft.services'].search([('type_rdv','=','img')]).id,
                    'medecin_id2': self.doctor_id.id,

                    'partner_id': self.patient_id.partner_id.id,
                    'ref': self.name,
                    'invoice_line_ids': lines
                })
                ### màj de la demande d'examen d'imagerie créée
                #raise UserError(_([line.id for line in self.env['account.move'].browse(move_id.id).invoice_line_ids if line.ref_item == self.env['fertility.examen.imagerie'].browse(img.id).imagerie_name]))
                imagerie_ids.write({'move_id': move_id.id, 'internal_status': 'invoicing', 'patient_id': self.patient_id.id,
                                    'medecin_demander': self.doctor_id.id,
                                    })

                # Notification reception
                self.env['sh.announcement'].notifImagerieReception()
        else:
            raise UserError(_("Vous n'avez selectionné aucun examens d'imagerie et/ou de laboratoire"))
            print("Pas de imagerie_ids")

    def action_creer_ordonnance(self):
        # Recupération de la liste des produits selectionnés (Ici, chaque ligne est une ordonnance)
        ordonnance_ids = self.done_ordonnance.filtered(lambda ordonnance: ordonnance.status == 'draft')

        #raise UserError(_(ordonnance_ids))
        if ordonnance_ids or self.cord_commentaire_pharma:
            ### Creation de l'ordonnance
            ordonn_id = self.env['module.ordonnance'].create({

                'patient_id': self.patient_id.id,
                'poids': self.poids,

                'parent_id2': self.patient_id.parent_id.id,
                'matricule': self.patient_id.matricule,
                'categorie2': self.patient_id.categorie,
                'classe': self.patient_id.classe,
                'function': self.patient_id.function,
                'email': self.patient_id.email,
                'phone': self.patient_id.phone,

                'numero_billet': self.numero_billet,
                'medecin': self.doctor_id.id,
                'commentaire_medecin': self.cord_commentaire_pharma,

            })
            ### MàJ de l'ordonnance créée
            ordonnance_ids.write(
                {'ordonnace_id': ordonn_id.id, 'status': 'invoicing', 'patient_id': self.patient_id.id})

            # Notification Pharmacie
            #self.env['sh.announcement'].notifPharmacie()
            


        else:
            print("Pas d'ordonnance_ids")

    def action_creer_dmde_shop(self):
        lunettes_ids = self.done_lunettes.filtered(lambda ordonnance: ordonnance.status == 'draft')

        ### Creation de la demande Shop Optique
        if lunettes_ids or self.cord_commentaire:
            ### Creation de l'ordonnance
            lunette_id = self.env['module.prescription'].create({

                'patient_id': self.patient_id.id,
                'numero_billet': self.numero_billet,
                'medecin': self.doctor_id.id,
                'parent_id': self.patient_id.parent_id.id,
                'matricule': self.patient_id.matricule,
                'categorie': self.patient_id.categorie,
                'classe': self.patient_id.classe,
                'function': self.patient_id.function,
                'email': self.patient_id.email,
                'phone': self.patient_id.phone,
                'cord_commentaire': self.cord_commentaire,
                'type_lunette': self.type_lunette.id,
                'od_dist': self.od_dist,
                'og_dist': self.og_dist,
                'dist_pp': self.dist_pp,

            })
            lunettes_ids.write(
                {'prescription_id': lunette_id.id, 'status': 'invoicing', 'patient_id': self.patient_id.id})

            # Notification shop
            self.env['sh.announcement'].NotifShop()
        else:
            print("Pas de lunettes_ids")

    def appointment_to_soinsambulatoire(self):
        lines = []
        lines_med = []
        lines_actes = []
        lines_mat = []
        lines_kine = []

        #kinesitheurapie = fields.One2many('module.kinesitheurapie', 'kine_id', string="Kinesitheurapie")
        traitement_ids = self.done_orientation.filtered(lambda traitement: traitement.internal_status == 'draft')
        kine_ids = self.request_kine.filtered(lambda kine: kine.internal_status == 'draft')

        if traitement_ids or kine_ids:
            if traitement_ids:
                for ordo in traitement_ids:
                    lines.append((0, 0, {'date_traitement':fields.Datetime.now(), 
                                         'produit' : ordo.medicament.id, 
                                         'posologie' : ordo.description,
                                         'actes_medicaux' : ordo.product.id,
                                         'materiels' : ordo.materiels.id,
                                    }
                            ))
                    
                    if ordo.medicament:
                        lines_med.append((0, 0, {'date_realisation':fields.Datetime.now(), 
                                         'produit' : ordo.medicament.id, 
                                         'qtity' : 1,
                                         #'actes_medicaux' : ordo.product.id,
                                         #'materiels' : ordo.materiels.id,
                                    }
                            ))
                    
                    if ordo.product:                    
                        lines_actes.append((0, 0, {'date_realisation':fields.Datetime.now(), 
                                         'actes' : ordo.product.id, 
                                         'qtity' : 1,
                                         #'actes_medicaux' : ordo.product.id,
                                         #'materiels' : ordo.materiels.id,
                                    }
                            ))
                            
                    if ordo.materiels:      
                        lines_mat.append((0, 0, {'date_realisation':fields.Datetime.now(), 
                                         'produit' : ordo.materiels.id, 
                                         'qtity' :1,
                                         #'actes_medicaux' : ordo.product.id,
                                         #'materiels' : ordo.materiels.id,
                                    }
                            ))
                #raise UserError(traitement_ids)
                hospi_id = self.env['module.hospitalisation'].create({
                    'patient_id': self.patient_id.id,
                    'medecin_tut': self.doctor_id.id,
                    'service_a': self.salle_soins.id,
                    'raison_admin':self.instruction_soins,
                    'type_hospitalisation':'obser',
                    'hospi_traitement_inf':lines,
                    'hospi_actes_fact':lines_actes,
                    'hospi_medic_fact':lines_med,
                    'hospi_materiel_fact':lines_mat,
                })
                
                if hospi_id:
                    traitement_ids.write({'internal_status':'ongoing'})

            if kine_ids:
                for kine in kine_ids:
                    for count_id in range(kine.nbre_seance):
                        kine_id = self.kinesitheurapie.create({
                                'patient_id': kine.patient_id.id,
                                'date_recorded':kine.date_recorded,
                                'internal_status':'invoicing', # Suivre le cas de patient conventionné
                                'product':kine.product.id,
                                'nbre_seance':1,
                                'is_physical_medecine':kine.is_physical_medecine,
                                'kine_id':self.id,

                        })
        
                message = "PATIENT ENVOYE AUX SOINS AMBULATOIRES"
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'type': 'danger',
                        'message': message,
                        'next': {'type': 'ir.actions.act_window_close'},
                    }
                }  

        else:
            raise UserError("Aucun actes, médicaments prescrits")
            
    def action_facturer_chirurgie(self):
        journal_id = self.env['ksoft.appointment'].get_journal_type(self.categorie)
        ordonnance_ids = self.done_orientation.filtered(lambda ordonnance: ordonnance.internal_status == 'draft')
        lines = []
        if ordonnance_ids:
            lines.append((0, 0, {'display_type': 'line_section', 'name': 'Actes chirurgicaux', 'debit': 0, 'credit': 0,
                                 'account_id': False}))
            for ordo in ordonnance_ids:
                #### Recuperer le prix selon la liste de prix defini
                product_context = dict(
                    self.env.context,
                    partner_id=self.patient_id.partner_id.id,
                    date=fields.Date.today(),
                    uom=ordo.product.uom_id.id,
                )
                prix, ruled = self.patient_id.partner_id.property_product_pricelist.with_context(
                    product_context).get_product_price_rule(
                    ordo.product, 1.0,
                    self.patient_id.partner_id) if self.patient_id.partner_id.property_product_pricelist else self.product.list_price

                lines.extend((0, 0, {'product_id':self.env['product.product'].search([('product_tmpl_id', '=', ordo.product.id)]).id, 'price_unit': prix, 'quantity': 1}))

            move_id = self.env['account.move'].create({
                'move_type': 'out_invoice',
                'journal_id': journal_id,
                'patient_id': self.patient_id.id,
                'numero_billet': self.numero_billet,
                'partner_id': self.patient_id.partner_id.id,
                'convention_id': self.parent_id.id,
                'matricule': self.matricule,
                'categorie': self.categorie,
                'classe': self.classe,
                'invoice_line_ids': lines
            })
            if move_id.id:
                ordonnance_ids.write({'internal_status': 'invoicing'})

        message = "FACTURE ENVOYEE"
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'danger',
                'message': message,
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }


    def action_close(self):
        
        if self.is_diagnostic == True or len(self.diagnostics_ids) >= 1:
            self.internal_status = 'closed'
            self.date_cons_2 = fields.Datetime.now()
            message = "CONSULTATION FERMEE"
            return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'danger',
                'message': message,
                'next': {'type': 'ir.actions.act_window_close'},
            }}

            
        else:
            raise UserError("Vous ne pouvez cloturer un rendez-vous sans mettre le diagnostic")

    def action_return(self):
        if self.internal_status == 'open':
            self.internal_status = 'consult_gyneco'
        # self.consult_examen_id.imagerie_ids.write({'internal_status':'draft'})
        # self.consult_examen_id.labo_ids.write({'internal_status':'draft'})
        elif self.internal_status == 'consult_social':
            self.internal_status = 'triage'

    def action_return_consult(self):
        self.internal_status = 'consult_gyneco'

    def action_open_again(self):
        if self.internal_status == 'closed':
            self.internal_status = 'open'
            self.is_re_ouvert = True
            self.re_ouver_par = self.env.user.id

    def _get_status(self):
        for exam in self:
            # continue
            if exam.internal_status == 'invoicing':
                if exam.status_moved == 'paid':
                    exam.internal_status = 'triage'
            exam.status = exam.internal_status

    def action_patient(self):
        try:
            form_view_id = self.env.ref("ksoftmedical.view_patient_antecedent_form").id

        except Exception as e:
            form_view_id = False
        return {
            'name': 'Patient',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'fertility.patient',
            'views': [(form_view_id, 'form')],
            'res_id': self.patient_id.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def action_prescription(self):
        try:
            form_view_id = self.env.ref("ksoftmedical.view_prescription_form").id

        except Exception as e:
            form_view_id = False
        return {
            'name': 'Prescription',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'fertility.appointment',
            'views': [(form_view_id, 'form')],
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
        
    def action_consultation(self):
        try:
            form_view_id = self.env.ref("ksoftmedical.view_consultation_form").id

        except Exception as e:
            form_view_id = False
        return {
            'name': 'Consultation',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'fertility.appointment',
            'views': [(form_view_id, 'form')],
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def action_prescription_send(self):
        # self.env.
        self.action_creer_ordonnance()
        self.action_creer_dmde_shop()

        # Alternative : Fermer proprement le dialogue courant
        return {'type': 'ir.actions.act_window_close'}


    def action_chirurgie(self):
        try:
            form_view_id = self.env.ref("ksoftmedical.view_traitement_form").id

        except Exception as e:
            form_view_id = False
        return {
            'name': 'Traitements',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'fertility.appointment',
            'views': [(form_view_id, 'form')],
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }


    def action_pma(self):
        self.ensure_one()
        return {
            'name': 'Dossier PMA',
            'view_mode': 'form',
            'res_model': 'fertility.pma',
            'type': 'ir.actions.act_window',
            # 'target': 'new',
            'context': {
                **self.env.context,
                'active_ids': self.ids,
                'default_doctor_id': self.doctor_id.id,
                'default_patient_id': self.patient_id.id,
                'default_partner_id': self.patient_id.partner_id.id,
                'default_journal_id': self.appointment_type.journal_id.id,
                'move_type': 'out_invoice',
                'default_appointment_id': self.id
            }
        }


class Notifications(models.Model):
    _inherit = 'sh.announcement'

    # @api.multi
    # def NotifShop(self):
    #   users = [(4, 11), (4, 6)]
    #   notif = self.create({
    #       'name': "Notification Shop",
    #       'date': fields.Date.today(),
    #       'is_popup_notification': True,
    #       'simple_text': True,
    #       'notification_type': 'warning',
    #       'description_text': "NOUVELLE DEMANDE",
    #       'user_ids': users
    #   })
    # notif.write()
    #   notif.notify_user()

    # raise Exception(_("##### %s", notif))

    def NotifShop(self):
        # users = [(4, 11), (4, 6)]
        # vals = {
        #   'name': 'Notification Shop',
        #   'date': fields.Date.today(),
        #   'is_popup_notification': True,
        #   'simple_text': True,
        #   'notification_type': 'warning',
        #   'description_text': "NOUVELLE DEMANDE",
        #   'user_ids': users
        # }
        # res = super(Notifications, self).create(vals)
        # res.notify_user()

        domain = [('name', '=', 'Notification Shop')]
        annonce = self.env['sh.announcement'].search(domain)
        for rec in annonce:
            rec.notify_user()

    def notifmedecins(self):
        domain = [('name', '=', 'Notification medecin')]
        annonce = self.env['sh.announcement'].search(domain)
        for rec in annonce:
            rec.notify_user()

    def notifTriage(self):
        domain = [('name', '=', 'Notification triage')]
        annonce = self.env['sh.announcement'].search(domain)
        for rec in annonce:
            rec.notify_user()

    def notifPharmacie(self):
        domain = [('name', '=', 'Notification pharmacie')]
        annonce = self.env['sh.announcement'].search(domain)
        for rec in annonce:
            rec.notify_user()

    def notifShopRec(self):
        domain = [('name', '=', 'Notification Shop Reception')]
        annonce = self.env['sh.announcement'].search(domain)
        for rec in annonce:
            rec.notify_user()

    def notifImagerieReception(self):
        domain = [('name', '=', 'Notification imagerie reception')]
        annonce = self.env['sh.announcement'].search(domain)
        for rec in annonce:
            rec.notify_user()


class PrescriptionAppointment(models.Model):
    """ Gestion des Prescriptions médicales dans le circuit ambulatoires"""

    _inherit = 'module.prescription'
    _description = 'Prescription Médicale'
    _order = 'date_prescription desc, id desc'

    pres_appointment_id = fields.Many2one('fertility.appointment', string='Consultations')
    ordo_appointment_id = fields.Many2one('fertility.appointment', string='Consultations')


class AnnotationsMedecin(models.Model):
    """ Gère les annotations faites par le medecin au niveau des pre-exams"""

    _name = 'module.annotation'
    _description = 'Annotations du médecin'
    # _order = 'date_prescription desc, id desc'

    date = fields.Datetime(string='Date/Heure', readonly=True, default=fields.Datetime.now)
    note_medecin = fields.Html(string='Note')
    medecin = fields.Many2one('res.users', readonly=True, string="Par")
    annotation_id = fields.Many2one('fertility.appointment', string="Consultation")

    @api.model
    def default_get(self, fields):
        res = super(AnnotationsMedecin, self).default_get(fields)
        res['medecin'] = self.env.user.id
        return res
    
class FeuilleDeSurveillanceSVModule(models.Model):
    """ Gestion de la feuille de surveillance  """

    _name = 'module.feuille.surveillance'
    _description = 'Feuille de surveillance Infirmieres'
    _order = 'date_surveillance desc, id desc'

    surveillance_name = fields.Char(string="ID Surveillance")
    patient_id = fields.Many2one('fertility.patient', string='Patient')
    nompatient = fields.Char(related='patient_id.nom', string="Nom")
    pnompatient = fields.Char(related='patient_id.postnom', string="Postnom")
    prnompatient = fields.Char(related='patient_id.prenom', string="Prenom")
    dob = fields.Date(related='patient_id.birth', string='Date Naiss', readonly=True, )
    sex = fields.Selection([('m', 'Masculin'), ('f', 'Féminin')], string='Sexe', readonly=True)
    age = fields.Integer(related='patient_id.age', string='Age', readonly=True)
    date_surveillance = fields.Datetime(string='Date', readonly=False, default=fields.Datetime.now())
    is_alert = fields.Boolean(string="Attention")
    infirmier = fields.Many2one('res.users', string="Infirmier",
                                default=lambda self: self.env.user)
    heure = fields.Char(string="Heure", required=False)

    # Parametres vitaux
    temperature = fields.Float(string="T°")
    tension = fields.Char(string="TA")
    respiration = fields.Integer(string="Fr (cpm )")
    pulsation = fields.Integer(string="Fc (bpm)")
    glycemie = fields.Integer(string="Glycemie (mg/dl )")
    saturation = fields.Integer(string="Oxygène (%)")
    is_print = fields.Boolean(string="#", default=True)
    taille = fields.Float(string=" Taille (m)")
    poids = fields.Float(string="Poids (kg)")

    imc = fields.Float(string="IMC (kg/m²)", store=True, compute="calc_imc")

    preleveur = fields.Many2one('res.users', readonly=True, string="Par")
    is_alert = fields.Boolean(string="Attention")

    ## Services
    service_id = fields.Many2one('ksoft.service', string="Service d'Origine")

    feuille_signesV_id = fields.Many2one('fertility.appointment', string="Consultation")


    # @api.model
    # def default_get(self, fields):
    #     res = super(SignesVitaux, self).default_get(fields)
    #     res['preleveur'] = self.env.user.id
    #     return res
    
    @api.depends('taille','poids')
    def calc_imc(self):
        for signes in self:
            if signes.taille > 0 and signes.poids > 0:
                signes.imc = (signes.poids) / (signes.taille * signes.taille)
            else:
                signes.imc = 0.0


class SignesVitaux(models.Model):
    """ Gère les signes vitaux du patient"""

    _name = 'module.signes.vitaux'
    _description = 'Signes vitaux du patient'
    # _order = 'date_prescription desc, id desc'

    date = fields.Datetime(string='Date/Heure', readonly=True, default=fields.Datetime.now)
    temperature = fields.Float(string='Temp.(°C)')
    ta = fields.Char(string="TA (mmHg)")
    glyc = fields.Char(string="Glycémie (mg/dl )", size=64)
    fr = fields.Integer(string="Fr (cpm )", size=64)
    fc = fields.Integer(string="Fc (bpm)", size=64)
    taille = fields.Float(string=" Taille (m)", size=64)
    poids = fields.Float(string="Poids (kg)", size=64)
    so = fields.Char(string="S en O2(%)", size=64)
    imc = fields.Float(string="IMC (kg/m²)", size=64)

    preleveur = fields.Many2one('res.users', readonly=True, string="Par")
    signesV_id = fields.Many2one('fertility.appointment', string="Consultation")

    
    # @api.depends('taille','poids')
    # def calcul_imc(self):
    #     for signes in self:
    #         if signes.taille > 0:
    #             signes.imc = (signes.poids) / (signes.taille * signes.taille)

