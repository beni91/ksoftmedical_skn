# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import AccessError, UserError, ValidationError

categorie_patient = [('prive','Standard'),('vip','VIP'),
             ('convention','Conventionné'),('social','Social'),
             ('prive2','Ayant Droit')
]



class AllergiesPatientListe(models.Model):

    _name = 'ksfot.allergie'

    name = fields.Text(string="Allergie")
    
class AntecedentsPatients(models.Model):

    _name = 'ksfot.allergie.details'

    name = fields.Text(string="Antécedents")
    
class AllergiesPatient(models.Model):

    _name = 'ksfot.patient.allergie'

    #name = fields.Char(string="Allergie")
    code = fields.Char(string="Code")
    etat = fields.Boolean(string="Actif", default=True)
    select = fields.Boolean(string="Select")
    date_detection = fields.Date(string="Date", required=True)
    comment = fields.Text(string="Commentaire")
    allergie = fields.Many2one('ksfot.allergie', string="ATCD")
    allergie_details = fields.Many2one('ksfot.allergie.details', string="Allergie")
    #atcd = fields.Many2one('fertility.patient.antecedent', string="ATCD")
    atcd = fields.Many2one('fertility.patient', string="ATCD")
    user_id = fields.Many2one('res.users', string='Par')

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, "%s" % (rec.allergie_details.name)))       
        return result

    @api.model
    def default_get(self, fields):
        res = super(AllergiesPatient, self).default_get(fields)
        res['user_id'] = self.env.user.id
        return res
    
class AtcdMedicauxPatient(models.Model):

    _name = 'ksfot.patient.atcd.medicaux'

    #name = fields.Char(string="ATCD")
    code = fields.Char(string="Code")
    etat = fields.Boolean(string="Confirmé", default=False)
    date_detection = fields.Date(string="Date", required=True)
    type_atcd = fields.Selection([('alim','Alimentaire'),('chir','Chirurgical'),('med','Médical'),('gyneco','Gynéco-Obstetrique'),
                                 ('fam','Familial'),('autres','Autres')], string="Type", required=True)
    select = fields.Boolean(string="Select")
    comment = fields.Text(string="Commentaire")
    allergie = fields.Many2one('ksfot.allergie', string="ATCD")
    #atcd = fields.Many2one('fertility.patient.antecedent', string="ATCD")
    atcd = fields.Many2one('fertility.patient', string="ATCD")
    user_id = fields.Many2one('res.users', string='Par')
    etat_atcd = fields.Selection([('draft','Brouillon'),('conf','Confirmer')], default='draft',string="Etat")

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, "%s" % (rec.allergie.name)))       
        return result
    
    @api.onchange('etat')
    def get_patient_atcd_medical(self):
        if self.etat:
            atcd = self.create({
                'type_atcd': self.type_atcd,
                'allergie': self.allergie.id,
                'user_id':  self.env.user.id,
                'comment': self.comment,
                'etat_atcd':'conf',
                'etat':True,
                'date_detection': fields.Datetime.now(),
            })

            if atcd:
                # self.env['fertility.patient'].browse(self.atcd.id).action_save_atcd()
                self.atcd.action_save_atcd()

                logging.info(" #### Texte %s",self.atcd)

    @api.model
    def default_get(self, fields):
        res = super(AtcdMedicauxPatient, self).default_get(fields)
        res['user_id'] = self.env.user.id
        return res

class MvtAdministratifPatient(models.Model):

    _name = 'ksfot.patient.mvtadministrif'

    # #name = fields.Char(string="ATCD")
    datemodif = fields.Date(string="Date de modification")
    # actuel = fields.Boolean(string="Situation actuel", default=False)
    # categorie = fields.Selection([('prive','Privé'),('convention','Abonné')], string="Catégorie", required=False)
    # classe = fields.Selection([('agent','Agent'),('epoux','Epoux(se)'),('enf','Enfants')], string="Classe")
    # matricule = fields.Char(string="Matricule")
    # convention = fields.Many2one('res.partner', domain="[('is_company', '=', True)]")
    # user_id = fields.Many2one('res.users', string='Modifié par')
    # patient_id = fields.Many2one('fertility.patient', string="Patient")
    etat = fields.Selection([('archived','Archived'),('encours','En cours')], string="Statut")

class PatientAntecedent(models.Model):
    _name = "fertility.patient.antecedent"
    _description = "hospital.patient.antecedent"
    _order = "patient_id, date"
    _inherit = ['mail.thread']

    # # patient_id= fields.Many2one('fertility.patient', ondelete='cascade')

    # antecedent_name = fields.Char(string='ID')

    # def name_get(self):
        # result = []
        # for rec in self:
            # result.append((rec.id, "%s" % (rec.antecedent_name)))       
        # return result



    # # Obstétricaux et Gynécologiques
    # gestite = fields.Char(string='Gestité',tracking=True)
    # parite = fields.Char(string='Parité',tracking=True)
    # enfant_vivant = fields.Char(string='Enfants vivants',tracking=True)
    # age_dernier_accouchement = fields.Char(string='Age du dernier accouchement',tracking=True)
    # total_accouchement = fields.Text(string='Nombre total d’Accouchements',tracking=True)
    # total_accouchement_spontane = fields.Text(string='Vaginal spontané',tracking=True)
    # total_accouchement_instru = fields.Text(string='Vaginal Instrum',tracking=True)
    # total_accouchement_cesarienne = fields.Text(string='Césarienne : Interruption Volontaire de grossesse',tracking=True)
    # fausse_spontane = fields.Text(string='Fausse Couche Spontanée',tracking=True)
    # fausse_tardive = fields.Text(string='Fausse Couche Tardive',tracking=True)
    # grossesse_ectopique = fields.Text(string='Grossesse Ectopique',tracking=True)
    # interrupt_med_grossesse = fields.Text(string='Interruption médicale de la grossesse',tracking=True)
    # enfant_autres = fields.Text(string='Enfants avec autre partenaire',tracking=True)
    # ddr = fields.Char(string='DDR',tracking=True)
    # age_premiere_regles = fields.Text(string='Age aux premières règles',tracking=True)
    # # Familiaux et héréditairesBoolean
    # infertilite = fields.Text(string='Notion d’infertilité dans la famille',tracking=True)
    # # Médicaux (si oui, préciser la durée et le traitement en cours,tracking=True)
    # diabete = fields.Text(string='Diabète',tracking=True)
    # hypertension = fields.Text(string='Hypertension artérielle',tracking=True)
    # obesite = fields.Text(string='Obésité',tracking=True)
    # asthme = fields.Text(string='Asthme',tracking=True)
    # dysthyroidie = fields.Text(string='Dysthyroidie',tracking=True)
    # med_description = fields.Text(string='Autre (à préciser)',tracking=True)
    # # Chirurgicaux(Si OUI, préciser l’année,tracking=True)
    # coelioscopie = fields.Text(string='Coelioscopie',tracking=True)
    # myomectomie = fields.Text(string='Myomectomie',tracking=True)
    # kystectomie = fields.Text(string='Kystectomie',tracking=True)
    # curetage = fields.Text(string='Curetage',tracking=True)
    # cicatrice_sous = fields.Text(string='Cicatrice Médiane sous ombilicale',tracking=True)
    # retention_placentaire = fields.Text(string='Rétention placentaire',tracking=True)
    # cicatrice_sus = fields.Text(string='Cicatrice Médiane sus ombilicale',tracking=True)
    # appendicectomie = fields.Text(string='Appendicectomie',tracking=True)
    # pfannestiel = fields.Text(string='Pfannestiel',tracking=True)
    # chr_description = fields.Text(string='Autre (à préciser)',tracking=True)
    # # Autres antécédents
    # autres_tabac = fields.Text(string='Tabac',tracking=True)
    # autres_alcool = fields.Text(string='Alcool',tracking=True)
    # autres_description = fields.Text(string='Autres',tracking=True)
    # # ATCD
    # atcd_grossesse = fields.Text(string='Nombre de Grossesses obtenues',tracking=True)
    # atcd_fiv = fields.Text(string='FIV-ICSI (nombre)',tracking=True)
    # atcd_don = fields.Text(string='Don (nombre)',tracking=True)
    # atcd_embryontransfert = fields.Text(string='Transfert Embryon(nombre)',tracking=True)
    # atcd_embryonj3 = fields.Text(string='Embryon J3 (nombre)',tracking=True)
    # atcd_blastocyste = fields.Text(string='Blastocyste (nombre,)',tracking=True)
    # atcd_echec = fields.Text(string='Echec (nombre)',tracking=True)
    # atcd_embryonrestant = fields.Text(string='Embryons congelés restants (nombre)',tracking=True)
    # atcd_description = fields.Text(string='Autres informations',tracking=True)

    # ### ATCD Ophtalmologique
    # ### Allergie
    # allergie = fields.One2many('ksfot.patient.allergie', 'atcd', string="Allergie")
    # atcd_medical = fields.One2many('ksfot.patient.atcd.medicaux', 'atcd', string="ATCD Médicaux")
    # histoire_occ = fields.Text(string="Hist. Famil. Occulaire")

    lunettes = fields.Selection([('oui','OUI'),('non','NON')], string="Port des lunettes")
    derniere_consult = fields.Date(string="Derniere consul. Ophta")
    lunettes_comm = fields.Text(string='Commentaires',tracking=True)
    atcd_description = fields.Text(string='Autres informations',tracking=True)
    lst_produit = fields.Text(string='Liste de médicaments',tracking=True)
    
class Patient(models.Model):
    _name = 'fertility.patient'
    _inherits = {
        'res.partner':'partner_id',
        #'fertility.patient.antecedent': 'antecedent_id',
        #'ksfot.patient.mvtadministrif': 'mvtadmin_id',
        }
        
    
    def _get_company_currency(self):
        for ordo in self:
            if ordo.partner_id.company_id:
                ordo.currency_id = ordo.partner_id.sudo().company_id.currency_id
                
            else:
                ordo.currency_id = self.env.company.currency_id

    ID = fields.Char(string='ID')
    idpat = fields.Char(string='ID Patient')
    nom = fields.Char(index=True)
    postnom = fields.Char(index=True)
    prenom = fields.Char(index=True)
    pseudo = fields.Char(index=True, string="Pseudonyme")
    birth = fields.Date('Date de naissance')
    age = fields.Integer(compute='_get_age', store=True)
    gender = fields.Selection([('M','Masculin'),('F','Féminin')], 'Genre')
    blood_type = fields.Selection([('A', 'A'), ('B', 'B'), ('AB', 'AB'), ('O', 'O'), ], string='Groupe sanguin')

    photo = fields.Binary(string="Photo")
    quartier = fields.Char('Quartier')
    commune = fields.Selection([
        ('Bandalungwa','Bandalungwa'),('Barumbu','Barumbu'),('Bumbu','Bumbu'),('Gombe','Gombe'),('Kalamu','Kalamu'),('Kasa-Vubu','Kasa-Vubu'),
        ('Kimbanseke','Kimbanseke'),('Kinshasa','Kinshasa'),('Kintambo','Kintambo'),('Kisenso','Kisenso'),('Lemba','Lemba'),('Limete','Limete'),
        ('Lingwala','Lingwala'),('Makala','Makala'),('Maluku','Maluku'),('Masina','Masina'),('Matete','Matete'),('Mont-Ngafula','Mont-Ngafula'),
        ('Ndjili','Ndjili'),('Ngaba','Ngaba'),('Ngaliema','Ngaliema'),('Ngiri-Ngiri','Ngiri-Ngiri'),('Nsele','Nsele'),('Selembao','Selembao')], 
        string='Commune') 

    zone = fields.Selection([('hors_zone','Hors Zone'),('zone','Zone')], 'Zone')  
    etat_civil = fields.Selection([('celibataire','Célibataire'),('marie','Marié(e)'),('divorce','Divorcé(e)'),('veuf','Veuf(ve)')], 'Etat Civil') 
    adresse = fields.Char(string="Adresse")
    # appointment_history = fields.One2many('fertility.appointment','patient_id')

    partner_id = fields.Many2one('res.partner', required=True, ondelete="cascade", readonly=True)
    pma_id = fields.Many2one('fertility.pma')
    #antecedent_id = fields.Many2one('fertility.patient.antecedent', required=True, ondelete="cascade")
    conjoint = fields.Many2one('fertility.patient', string="Conjoint(e)")

    ### Informations administratifs du patient
    matricule = fields.Char(string="Matricule", readonly=False)
    categorie = fields.Selection(categorie_patient, string="Catégorie", readonly=False)
    is_diaspora = fields.Boolean(string="Patient Diaspora", default=False)
    garant = fields.Char(string="Garant")
    classe = fields.Selection([('agent','Agent'),('epoux','Epoux(se)'),('enf','Enfants')], string="Classe", readonly=False)
    #mvt_patient = fields.One2many('ksfot.patient.mvtadministrif', 'patient_id', string="Mvt Administratif")

    #Info Medicale
    od_pio_max = fields.Float(string="OD (mmHg)", size=64)
    os_pio_max = fields.Float(string="OS (mmHg)", size=64)
    
    ## Frais d'identification
    
    type_identification = fields.Selection([('provisoire','Provisoire'),('definitif','Définitif')], default="provisoire", string="Type d'identité")
    num_piece = fields.Char(string="N° Pièce d'identité")
    piece_identite = fields.Selection([("electeur","Carte d'electeur"),("permis","Permis de conduire"),
                                        ("passeport","Passe port"),("attestation","Attestion de perte des pièces"),
                                        ("carte","Carte de service"),("autres","Autres"),], string="Pièce d'identité")
                                        
    
    # ## Vue facturation
    currency_id = fields.Many2one('res.currency', compute='_get_company_currency', readonly=True,
        string="Currency", help='Utility field to express amount currency')
        
    total_invoiced = fields.Monetary(compute='_compute_invoiced_total_amount', string="Montant Total", store=False)
    #total_dette = fields.Monetary(compute='_compute_total_du_amount', string="Total Dette", store=False)
    total_rdv = fields.Integer(compute='_compute_nbre_rdv', string="Nbre Rdv", store=False)
    total_laboratoire = fields.Integer(compute='_compute_nbre_rdv', string="Nbre Labo", store=False)
    total_imagerie = fields.Integer(compute='_compute_nbre_rdv', string="Nbre Imagerie", store=False)
    total_prescription = fields.Integer(compute='_compute_nbre_rdv', string="Nbre Prescription", store=False)
    
    allergie = fields.One2many('ksfot.patient.allergie', 'atcd', string="Allergie")
    atcd_medical = fields.One2many('ksfot.patient.atcd.medicaux', 'atcd', string="ATCD Médicaux")
    lunettes = fields.Selection([('oui','OUI'),('non','NON')], string="Port des lunettes")
    
    ### Résumé antécédents
    resume_atcd = fields.Html(string="Résumé Antécédent")
    
    # def action_save_atcd(self):
    #     ## Examen medical générale
    #     content =""
    #     for appointment_id in self:
    #         if appointment_id.allergie or appointment_id.atcd_medical:
    #             content += '<center><table width="80%" border=1>'
    #             content += '<tr><th width="50%" style="text-align:left"><b>ANTECEDENTS</b></th><th width="50%" style="text-align:left"><b>ALLERGIE</b></th></tr>'
    #             content += '<tr>'
    #             content += '<td><ul>'
    #             for atcd_id in appointment_id.atcd_medical:
    #                 content += '<li>'+ str(atcd_id.allergie.name) +'</li>'
    #             content += '</ul></td>'  
                
    #             content += '<td><ul>'
    #             for allergie_id in appointment_id.allergie:
    #                 content += '<li>'+ str(allergie_id.allergie_details.name) +'</li>'
    #             content += '</ul></td>'  
    #             content += '</tr>'
                  
    #             content += '</table></center></br>'
                
    #         appointment_id.write({'resume_atcd':content})

    def action_save_atcd(self):
        """
        Génère un résumé HTML structuré et moderne des antécédents 
        et allergies du patient, digne d'un grand SIH.
        """
        for appointment_id in self:
            if not appointment_id.atcd_medical:
                appointment_id.write({'resume_atcd': ''})
                continue

            # Structure CSS moderne intégrée (compatible avec le moteur de rendu d'Odoo)
            content = """
            <div style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; margin: 15px 0; color: #1a1a1a;">
                <table style="width: 100%; border-collapse: collapse; border: 1px solid #e2e8f0; border-radius: 6px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                    <thead>
                        <tr style="background-color: #011027; color: #ffffff; text-align: left;">
                            <th style="padding: 12px 16px; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; width: 40%;">Type / Diagnostic</th>
                            <th style="padding: 12px 16px; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; width: 60%;">Commentaires / Observations</th>
                            
                        </tr>
                    </thead>
                    <tbody>
            """

            # Parcours des lignes d'antécédents
            for index, atcd_id in enumerate(appointment_id.atcd_medical):
                # Alternance des couleurs de lignes pour une meilleure scannabilité visuelle
                bg_color = "#ffffff" if index % 2 == 0 else "#f8fafc"
                
                # Sécurité sur les chaînes de caractères (évite les écritures 'False')
                name = atcd_id.allergie.name if atcd_id.allergie else "Non spécifié"
                comment = atcd_id.comment if atcd_id.comment else "-"
                
                # Gestion élégante du type (Allergie, Médical, Chirurgical...)
                type_label = f"[{atcd_id.type_atcd.upper()}] " if hasattr(atcd_id, 'type_atcd') and atcd_id.type_atcd else ""
                
                # Gestion du badge de statut (Confirmé ou Brouillon)
                status_badge = ""
                if hasattr(atcd_id, 'etat'):
                    if atcd_id.etat == 'conf':
                        status_badge = '<span style="background-color: #def7ec; color: #03543f; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: 600;">Actif</span>'
                    else:
                        status_badge = '<span style="background-color: #fef3c7; color: #92400e; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: 600;">En cours</span>'

                content += f"""
                        <tr style="background-color: {bg_color}; border-bottom: 1px solid #e2e8f0;">
                            <td style="padding: 12px 16px; font-size: 13px; font-weight: 600; color: #011027;">
                                <p><span style="color: #00A09D; font-size: 11px; font-weight: 700;">{type_label}</span>
                                {name}</p>
                            </td>
                            <td style="padding: 12px 16px; font-size: 13px; color: #4a5568; line-height: 1.5;">
                                {comment}
                            </td>
                        </tr>
                """

            content += """
                    </tbody>
                </table>
            </div>
            """
            
            # Sauvegarde dans le champ HTML
            appointment_id.write({'resume_atcd': content})
            
    def _compute_invoiced_total_amount(self):
        AccountMove = self.env['account.move']
        for ab in self:
            invoiced_ids = AccountMove.search([('partner_id','=', ab.partner_id.id),('move_type','=','out_invoice')])
            if invoiced_ids:
                for ordo in invoiced_ids:
                    ab.total_invoiced += ordo.amount_total
            else:
                ab.total_invoiced = 0.0
    
    def _compute_nbre_rdv(self):
        appointment_obj = self.env['ksoft.appointment'] 
        labo_obj = self.env['fertility.examen.labo'] 
        imagerie_obj = self.env['fertility.examen.imagerie']
        prescription_obj = self.env['module.ordonnance']
        for ab in self:
            appointment_ids = appointment_obj.search([('patient_id','=', ab.id)])
            labo_ids = labo_obj.search([('patient_id','=', ab.id),('internal_status','=','done')])
            imagerie_ids = imagerie_obj.search([('patient_id','=', ab.id),('internal_status','=','done')])
            prescription_ids = prescription_obj.search([('patient_id','=', ab.id)])
            
            #raise UserError(invoiced_ids)
            ab.write({'total_rdv':len(appointment_ids), 'total_laboratoire':len(labo_ids), 'total_imagerie':len(imagerie_ids), 'total_prescription':len(prescription_ids)}) 
                
    def open_list_appointment(self):
        if self:
            list_appoint = self.action_open_list_appointment(self.id)
            return list_appoint
            
    def historique_appointment(self):
        if self:
            hist_appoint = self.action_historique_appointment(self.id)
            return hist_appoint 
            
    def historique_diagnostic(self):
        if self:
            hist_diag = self.action_open_historique_diagnostic(self.id)
            return hist_diag 
            
    def open_list_medicament(self):
        if self:
            list_medicmnt = self.action_open_list_medicament(self.id)
            return list_medicmnt  
                
    def open_list_imagerie(self):
        if self:
            list_imagerie = self.action_open_list_imagerie(self.id)
            return list_imagerie  
            
    def open_list_labo(self):
        if self:
            list_labo = self.action_open_list_labo(self.id)
            return list_labo 
                
    def open_list_surveillance(self):
        if self:
            list_surveillance = self.action_open_historique_feuillesurveillance(self.id)
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
        
    def action_open_list_imagerie(self, patient):
        action = self.env.ref('ksoftmedical.action_dossierimagerie_patient').read()[0]
        action.update({'target': 'new','domain':[('patient_id','=',patient),('internal_status','=','done')]})
        return action
    
    def make_quick_appointment(self):
        try:
            form_view_id = self.env.ref("ksoftmedical.view_appointment_quick_patient_form").id

        except Exception as e:
            form_view_id = False
        
        return {
            'name': 'Quick Rendez-vous',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'ksoft.appointment',
            'type': 'ir.actions.act_window',
            'views': [(form_view_id, 'form')],
            'target': 'new',
            'context': {
                **self.env.context,
                #'active_ids': self.ids,
                'default_patient_id': self.id,
                #'default_protocol': self.protocol,
            }
        }

    def last_cons(self, patient):
        appointments = self.env['fertility.appointment'].search([('patient_id', '=', patient)], limit=1)
        content = ''
        if appointments:
            for appointment in appointments:
                content += appointment.date.strftime('%d-%m-%Y')
                content += '<table width="900" border=1>'
                content += '<tr style="background-color:#A2E6CC;text-align:center"><th width="900" colspan="14"><b>ACUITE VISUELLE (AV)</b></th></tr>'
                content += '<tr style="background-color:#A2E6CC;text-align:center"><th colspan="3"><b>Oeil droit<b/></td><th colspan="3"><b>Oeil gauche</b></th></tr>'
                content += '<tr style="background-color:#A2E6CC;text-align:center"><td><b>S.C.</b></td><td><b>C.C.</b></td><td><b>T.S.</b></td><td><b>S.C.<b/></td><td><b>C.C.</b></td><td><b>T.S.</b></td></tr>'

                content += '<tr style="text-align:center"><td>' + str(appointment.od_sc) + '</td><td>' + str(
                    appointment.od_cc) + '</td><td>' + str(appointment.od_ts) + '</td><td>' + str(
                    appointment.os_sc) + '</td><td>' + str(appointment.os_cc) + '</td><td>' + str(
                    appointment.os_ts) + '</td></tr>'
                content += '</table>'

                content += '</br>'
                content += '<table width="900" border=1>'
                content += '<tr style="background-color:#A2E6CC;text-align:center"><th width="900" colspan="14"><b>PRESSION INTRA-OCULAIRE</b></th></tr>'
                content += '<tr style="background-color:#A2E6CC;text-align:center"><th colspan="2"><b>Max<b/></td><th colspan="2"><b>Avant</b></th><th colspan="2"><b>Après</b></th></tr>'
                content += '<tr style="background-color:#A2E6CC;text-align:center"><th><b>OD<b/></td><th><b>OS</b></th><th><b>OD</b></th><th><b>OS</b></th><th><b>OD</b></th><th><b>OS</b></th></tr>'
                content += '<tr style="text-align:center"><td>' + str(appointment.od_pio_max) + '</td><td>' + str(
                    appointment.os_pio_max) + '</td><td>' + str(appointment.od_pression) + '</td><td>' + str(
                    appointment.os_pression) + '</td><td>' + str(appointment.od_pression_apres) + '</td><td>' + str(
                    appointment.os_pression_apres) + '</td></tr>'
                content += '</table>'

                if appointment.diagnostics_ids:
                    content += '</br>'
                    content += '<table width="900" border=1>'
                    content += '<tr style="background-color:#A2E6CC;text-align:center"><td width="900" colspan="7"><b>DIAGNOSTICS</b></td></tr>'
                    content += '<tr style="background-color:#A2E6CC;text-align:center"><td><b>Date</b></td><td><b>Pathologie</b></td><td><b>Observation</b></td><td><b>Médecin<b/></td></tr>'

                    for diagnostic in appointment.diagnostics_ids:
                        description = str(diagnostic.description) if diagnostic.description else ''
                        explication = str(diagnostic.explication) if diagnostic.explication else ''
                        origin = ''
                        if diagnostic.origine == 'homme':
                            origin = 'Masculine'
                        elif diagnostic.origine == 'femme':
                            origin = 'Feminine'
                        elif diagnostic.origine == 'mixte':
                            origin = 'Mixte'

                        status = ''
                        if diagnostic.internal_status == 'hypo':
                            status = 'Hypothèse'
                        elif diagnostic.internal_status == 'def':
                            status = 'Définitive'

                        content += '<tr ><td width="100">' + str(
                            diagnostic.date_diagnostic.strftime('%Y-%m-%d')) + '</td><td width="150">' + str(
                            diagnostic.pathologie.name) + '</td><td>' + explication + '</td><td>' + str(
                            diagnostic.medecin_diag.name) + '</td></tr>'
                    content += '</table>'
        else:
            #content = '<p style="font-color:#A2E6CC>Aucune consultation précédente</p>'
            content = '<p><FONT COLOR="#A2E6CC">Aucune consultation précédente</FONT></p>'
        return content

    def name_get(self):
        result = []
        for rec in self.filtered(lambda partner : partner.is_company==False) :
            result.append((rec.id, "%s - %s %s %s" % (rec.idpat, rec.nom, rec.postnom, rec.prenom)))        
        return result

    @api.depends('birth')
    def _get_age(self):
        today = fields.Date.today()
        for patient in self:
            patient.age = today.year - patient.birth.year - ((today.month, today.day) < (patient.birth.month, patient.birth.day)) if patient.birth else 0
    
    @api.onchange('nom','postnom','prenom')
    def get_nom(self):
        #today = fields.Date.today()
        if self:
            postnom = self.postnom if self.postnom else ""
            prenom = self.prenom if self.prenom else ""
            nom = self.nom if self.nom else ""
            ID = self.idpat if self.idpat else ""
            self.name = ID +" - "+nom +" "+postnom+" "+prenom


    #@api.multi
    def write(self, vals):
        #_logger.info("############### eeeu ############### %s %s", vals['postnom'], vals['prenom'])
        if self:
            if self.is_company == False :
                postnom = vals['postnom'] if vals.get('postnom') else self.postnom
                prenom = vals['prenom'] if vals.get('prenom') else self.prenom
                nom = vals['nom'] if vals.get('nom') else self.nom
                ID = vals['idpat'] if vals.get('idpat') else self.idpat
                vals['name'] = str(ID) +" - "+str(nom) +" "+str(postnom)+" "+str(prenom)
              
            else :
                vals['name'] = "%s" % (vals['name'] if vals.get('name') else self.name)

        return super(Patient, self).write(vals)

    @api.model
    def create(self, vals):
        #_logger.info(vals)
        vals['idpat'] = self.env['ir.sequence'].next_by_code('fertility.patient.name')
        if vals['is_company']==False :
            vals['idpat'] = self.env['ir.sequence'].next_by_code('fertility.patient.name')
            postnom = vals['postnom'] if vals.get('postnom') else ""
            prenom = vals['prenom'] if vals.get('prenom') else ""
            nom = vals['nom'] if vals.get('nom') else ""
            ID = vals['idpat'] 
            patient = str(vals['idpat'])+" - "+str(nom)+" "+str(postnom)+" "+str(prenom)
            # patient = vals['ID']+" - "+vals['nom']+" "+vals['postnom']+" "+vals['prenom']
            # vals['name'] = patient

        else :
            vals['name'] = "%s" % (vals['name'])

        return super(Patient, self).create(vals)


    def action_pma (self):
        self.ensure_one()
        if self.pma_id :
            return {
                'name': 'Dossier PMA',
                'view_mode': 'form',
                'res_model': 'fertility.pma',
                'res_id': self.pma_id.id,
                'type': 'ir.actions.act_window'
            }
        else:
            raise ValidationError("Pas de dossier PMA")

    def action_historique_patient(self):
        print("HISTORIQUE")
        # Recuperation de l'id du patient
        active_id = self.env.context.get('active_id')
        #brw_id=self.env['fertility.appointment'].browse(int(active_id))
        #patient_id = brw_id.patient_id.id
        print("ID du patient : ",active_id)
        a = self.env['fertility.wizard.dossier.medical.patient'].get_dossier_content2(19)
        content = fields.Html(default=a, string="", readonly=True)

        return content