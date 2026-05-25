# -*- coding: utf-8 -*-
#
# Auteur : BKM
# Date   : 11 Avril 22
################################
from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
import logging
_logger = logging.getLogger(__name__)

mode_admission = [
                    ('iv', 'I.V'), ('im', 'I.M'),
                    ('sc', 'S.C'), ('peros', 'Peros'),
                    ('ir', 'I.R')
                ]

class HospitalisationModule(models.Model):
    _name = 'module.hospitalisation'
    _description = 'Hospitalisation'
    _inherits = {
        'fertility.examen': 'hospi_examen_id'
    }
    
    
    def _get_company_currency(self):
        for ordo in self:
            if ordo.patient_id.partner_id.company_id:
                ordo.currency_id = ordo.patient_id.partner_id.sudo().company_id.currency_id
            else:
                ordo.currency_id = self.env.company.currency_id
                
    hospi_name = fields.Char(size=64, string='ID Hospi')
    patient_id = fields.Many2one('fertility.patient', string='Patient', required=True)
    nompatient = fields.Char(related='patient_id.nom', store=True, string="Nom")
    pnompatient = fields.Char(related='patient_id.postnom', store=True, string="Postnom")
    prnompatient = fields.Char(related='patient_id.prenom', store=True, string="Prenom")
    dob = fields.Date(related='patient_id.birth', string='Date Naiss', readonly=True, )
    sex = fields.Selection([('m', 'Masculin'), ('f', 'Féminin')], related='patient_id.gender', store=True, string='Sexe', readonly=True)
    rh = fields.Char(size=64, string='Rhésus', readonly=True)
    age = fields.Integer(related='patient_id.age', string='Age', store=True,readonly=True)

    parent_id = fields.Many2one(related='patient_id.parent_id', string="Convention")
    matricule = fields.Char(related='patient_id.matricule', string="Matricule")
    categorie = fields.Selection(related='patient_id.categorie', string="Catégorie")
    classe = fields.Selection(related='patient_id.classe', string="Classe")

    numero_billet = fields.Char(string="Billet d'envoi")
    email = fields.Char(related='patient_id.email', string="Email")

    # 'category': fields.Char(string='Categorie',select=True, readonly=True),
    numerodossier = fields.Char(related='patient_id.ID',string='N° Dossier', store=True, readonly=True)
    # 'convention':fields.Many2one('oemedical.patient.convention', string='Convention'),
    street = fields.Char('Adresse', size=128, readonly=True)
    telephone = fields.Char(related='patient_id.phone', store=True, size=128, string='N° Téléphone', readonly=True)
    religion = fields.Many2one('oemedical.patient.religion', store=True, string='Réligion', readonly=True)
    function = fields.Char(related='patient_id.function', store=True, string='Profession', size=128, readonly=True)
    # fin Remplissage automatique

    date_entree = fields.Datetime(string="Date d'Admission", required=True, default=fields.Datetime.now)
    #date_sortie = fields.Date(string="Date de sortie")

    raison_admin = fields.Text(string="Raison d'admission")
    medecin_tut = fields.Many2one('fertility.doctor', string='Médecin traitant',
                                  required=True, select=True, help='Médecin traitant')
    state = fields.Selection([('in', 'Hospitalisé'), ('atts', 'Peut sortir'),('invoiced', 'Facturé'),
                              ('out', 'Sorti'), ('cancel', 'Supprimé')],
                             default="in", string="Etat")
    lit = fields.Many2one('ksoft.chambre', required=False, string="Chambre")

    state_ambul = fields.Selection([('not_done', 'Non Fait'), ('invoiced', 'Facturé'), ('done', 'Fait')],
                             default="not_done", string="Etat")
    #DOSSIER MEDICAL
    # ANAMNESE
    anamnese = fields.Text(string='Anamnèse')
    diagnostic = fields.Text(string="Diagnostic")
    hospi_diagnostic = fields.One2many('module.diagnostics', 'diagnostic_hospi', string="Diagnostic")

    # Prescriptions médicales
    hospi_prescription = fields.One2many('module.prescription', 'prescr_hospi', string="Prescriptions Médicales")

    # Actes médicaux // Bloc Opératoire
    hospi_actes = fields.One2many('module.actes.medicaux', 'actes_hospi', string="Actes Médicales")
    # Observation médicales
    hospi_evolution = fields.One2many('module.evolutions.medicaux', 'evolution_hospi', string="Evolutions Médicales")
    # Bloc Operatoire
    #hospi_bloc = fields.One2many('module.blocoperatoire', 'bloc_hospi', string="Bloc Opératoire")
    
    ### Type d'hospitalisation
    type_hospitalisation = fields.Selection([('normal','Normal'),('amb','Ambulatoire'),('obser','Observation')], default='normal', 
                            required=True, string="Type d'Hospitalisation")

    # Services paracliniques
    hospi_examen_id = fields.Many2one('fertility.examen', required=True, ondelete="cascade", string="Examens")
    # 'imageries': fields.One2many('oemedical.imagerie.analysis', 'hospitalis_id', 'Imageries'),
    # 'medicaments': fields.One2many('oemedical.prescription', 'evaluation_ids', 'Medicaments'),

    # Facturations

    plan_nursing = fields.Text(string='Plan de nursing')
    plan_conge = fields.Text(string='Plan de congé')

    service_a = fields.Many2one('ksoft.services',string="Service")
    type_service = fields.Selection([('adm','Administration'),
                                 ('cons','Consultation'),
                                 ('urg','Urgence'),('rea','Réanimation'),('hospi','Hospitalisation'),
                                 ('soins','Soins ambulatoires'),('labo','Laboratoire'),
                                 ('pharma','Pharmacie'),('shop','Shop Optique'),
                                 ('img','Imagerie'),('vac','Vaccination'),('chi','Chirurgie'),
                                 ('dial','Dialyse')],
                                related='service_a.type_rdv',
                                readonly="True", string="Type de service")
    unite_a = fields.Many2one('ksoft.unite.soins',string="Unité de soins")

    jr_fact = fields.Integer(string='Nombre jours à facturer')
    active = fields.Boolean(string="Activer", default=True)
    # 'block':fields.Many2one('res.users', string="Hospitalisation:", required=True),

    # Mvt patient
    date_autorisation = fields.Datetime(string="Date autorisation sortie:", )
    user_autorisation = fields.Many2one('res.users', string="Autorisé par:")
    date_sortie = fields.Datetime(string="Date sortie:")
    user_autoriser = fields.Many2one('res.users', string="Sortie par:")
    create_par = fields.Many2one('res.users', string="Par:", )
    cancel_par = fields.Many2one('res.users', string="Annulé Par:")
    
    anamnese = fields.Text(string="Plaintes")
    hstr_affection = fields.Text(string="Histoire de l'affection")
    cpm_anamnese = fields.Text(string="Compléments d’anamnèse")
    examen_physique = fields.Text(string="Examen physique")
    
    
    total_invoiced = fields.Monetary(compute='_compute_invoiced_total_amount', string="Montant Total", store=True)

    currency_id = fields.Many2one('res.currency', compute='_get_company_currency', readonly=True,
        string="Currency", help='Utility field to express amount currency')
    
    hospi_move_id = fields.Many2one('account.move', ondelete="cascade")
    hospi_move_statut = fields.Selection(related='hospi_move_id.payment_state', string="Status Facturation", store=True)
    
    ##Transfert
    destination = fields.Many2one('ksoft.unite.soins', string="Destination")
    origine = fields.Many2one('ksoft.unite.soins', string="Origine")
    
    @api.depends('hospi_move_id')
    def _compute_invoiced_total_amount(self):
        AccountMove = self.env['account.move']
        for ordo in self:
            ordo.total_invoiced = AccountMove.browse(ordo.hospi_move_id.id).amount_total
            
    def action_view_partner_hospi_invoices(self):
        self.ensure_one()
        action = self.env.ref('account.action_move_out_invoice_type')
        result = action.read()[0]
        result.pop('id', None)
        result['context'] = {}
        result['domain'] = [('id', '=', self.hospi_move_id.id)]
        pick_ids = sum([self.hospi_move_id.id])
        if pick_ids:
            res = self.env.ref('account.view_out_invoice_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = pick_ids or False
        return result
        
    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, "%s" % (rec.hospi_name)))
        return result
        
    def calcul_sejour(self, date_entre, date_sortie):
        for sejour_hospi in self:
            remain_day = 0
            return_day = 0
            date_format = '%Y-%m-%d'
            if date_entre <= date_sortie:
                end_date = date_entre
                lelo = date_sortie
                timedelta = lelo - end_date
                remain_day = timedelta.days
                _logger.info("**** Day remaining %s ******", remain_day)
                
                return remain_day 
            else:
                raise UserError(_("La date d'admission ne peut être supérieur à la date de sortie"))
                

    @api.model
    def create(self, vals):
        vals['hospi_name'] = self.env['ir.sequence'].next_by_code('module.hospitalisation.name')

        return super(HospitalisationModule, self).create(vals)

    def action_open_sommaire_laboresult_fromhospi(self):
        action = self.env.ref('ksoftmedical.action_resultatlabo_all').read()[0]
        action.update({'target': 'new','domain':[('patient_id','=',self.patient_id.id),('internal_status','=','done')]})
        return action
    

    def action_open_sommaire_imagerieresult_fromhospi(self):
        action = self.env.ref('ksoftmedical.action_resultatimagerie_all').read()[0]
        action.update({'target': 'new','domain':[('patient_id','=',self.patient_id.id),('internal_status','=','done')]})
        return action
    

    def action_open_sommaire_feuillesurveillance_fromhospi(self):
        action = self.env.ref('ksoftmedical.action_feuille_signesvitaux_all').read()[0]
        action.update({'target': 'new','domain':[('patient_id','=',self.patient_id.id)]})
        return action

    def action_send_examimagerie_from_hospi(self):
        ## Check la categorie pour placer dans le journal qui convient
        journal_id = self.env['ksoft.appointment'].get_journal_type(self.patient_id.categorie)

        # Recupération dans une liste des examens d'imagérie selectionnés dans le champs "imagerie_ids"
        imagerie_ids = self.hospi_examen_id.imagerie_ids.filtered(lambda imagerie: imagerie.status == 'draft')

        # Recupération dans une liste des examens de laboratoire selectionnés dans le champs "labo_ids"
        labo_ids =  self.hospi_examen_id.labo_ids.filtered(lambda labo: labo.status == 'draft')

        #{'move_line_id':[line.id for line in self.env['account.move'].browse(move_id.id).invoice_line_ids if line.ref_item == self.env['fertility.examen.imagerie'].browse(img.id).imagerie_name]}

        if self.hospi_examen_id:
        ## Creation facture laboratoire
            if labo_ids:
                #labo_ids.write({'internal_status': 'sample', 'patient_id': self.patient_id.id, })
                lines = []
                lines = [(0, 0, {'display_type': 'line_section', 'name': 'Hospitalisation:Laboratoire', 'debit': 0, 'credit': 0,
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
                    # 'numero_billet': self.numero_billet,
                    
                    'convention_id': self.patient_id.parent_id.id,
                    'matricule': self.patient_id.matricule,
                    'categorie': self.patient_id.categorie,
                    'classe': self.patient_id.classe,
                    'libelle':'laboratoire',
                    'partner_id': self.patient_id.partner_id.id,
                    'service_id2': self.env['ksoft.services'].search([('type_rdv','=','labo')]).id,
                    #'medecin_id2': self.doctor_id.id,



                    'invoice_line_ids': lines
                    
                    
                })


                # ### màj de la demande d'examen de labo créée
                # #raise UserError(_([line.id for line in self.env['account.move'].browse(move_id.id).invoice_line_ids if line.ref_item == self.env['fertility.examen.labo'].browse(labo.id).labo_name]))
                labo_ids.write({'move_id': move_id.id, 'internal_status': 'invoicing', 'patient_id': self.patient_id.id,
                                #'medecin_demander': self.doctor_id.id,
                                })
                # #'move_line_id':[line.id for line in self.env['account.move'].browse(move_id.id).invoice_line_ids if line.ref_item == self.env['fertility.examen.labo'].browse(labo.id).labo_name]
                # #raise UserError(_("#####  ERERER %s", self.consult_examen_id))

                # Notification reception
                self.env['sh.announcement'].notifImagerieReception()

            ## Creation facture imagerie
            if imagerie_ids:
                #imagerie_ids.write({ 'internal_status': 'protocol', 'patient_id': self.patient_id.id})
                lines = []
                lines = [(0, 0, {'display_type': 'line_section', 'name': 'Hospitalisation:Imagerie', 'debit': 0, 'credit': 0,
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
                    # 'numero_billet': self.numero_billet,

                    'convention_id': self.patient_id.parent_id.id,
                    'matricule': self.patient_id.matricule,
                    'categorie': self.patient_id.categorie,
                    'classe': self.patient_id.classe,
                    'libelle':'imagerie',
                    'service_id2': self.env['ksoft.services'].search([('type_rdv','=','img')]).id,

                    'partner_id': self.patient_id.partner_id.id,
                    #'ref': self.name,
                    'invoice_line_ids': lines
                })
                # ### màj de la demande d'examen d'imagerie créée
                # #raise UserError(_([line.id for line in self.env['account.move'].browse(move_id.id).invoice_line_ids if line.ref_item == self.env['fertility.examen.imagerie'].browse(img.id).imagerie_name]))
                imagerie_ids.write({'move_id': move_id.id, 'internal_status': 'invoicing', 'patient_id': self.patient_id.id,
                                    #'medecin_demander': self.doctor_id.id,
                                    })

                # Notification reception
                self.env['sh.announcement'].notifImagerieReception()
        else:
            raise UserError(_("Vous n'avez selectionné aucun examens d'imagerie et/ou de laboratoire"))
            print("Pas de imagerie_ids")


    def action_autoriser_sortie(self):
        #self.state = 'atts'
        self.state = 'out'
        self.date_autorisation = fields.Datetime.now()
        self.user_autorisation = self.env.user
        
    def action_terminer_soins(self):
        self.date_autorisation = fields.Datetime.now()
        self.user_autorisation = self.env.user
        self.state_ambul = "done"
    

    def action_sortir(self):
        self.state = 'out'
        self.date_sortie = fields.Datetime.now()
        self.user_autoriser = self.env.user

    def action_return(self):
        self.state = 'in'

    # def unlink(self):
    #     self.ensure_one()
    #     if self.hospi_name:
    #         raise UserError(_("Vous ne pouvez pas supprimer un patient hospitalisé, contacter l'administrateur"))
    #     return False


class PrescriptionHospitalisation(models.Model):
    """ Gestion des Prescriptions médicales dans le circuit hospitalisation"""

    _inherit = 'module.prescription'

    prescr_hospi = fields.Many2one('module.hospitalisation', string="Hospitalisation")

    @api.model
    def create(self, vals):
        vals['origine'] = "Hospitalisation"
        return super(PrescriptionHospitalisation, self).create(vals)


class ActesMedicauxHospitalisation(models.Model):
    """ Gestion des actes médicaux dans le circuit hospitalisation"""

    _inherit = 'module.actes.medicaux'

    actes_hospi = fields.Many2one('module.hospitalisation', string="Hospitalisation")

    @api.model
    def create(self, vals):
        vals['origine'] = "Hospitalisation"
        
        return super(ActesMedicauxHospitalisation, self).create(vals)
        #raise UserError(_(obj_doctors))


class EvolutionMedHospitalisation(models.Model):
    """ Gestion des evolutions médicales dans le circuit hospitalisation"""

    _inherit = 'module.evolutions.medicaux'

    evolution_hospi = fields.Many2one('module.hospitalisation', string="Hospitalisation")

    @api.model
    def create(self, vals):
        vals['origine'] = "Hospitalisation"

        return super(EvolutionMedHospitalisation, self).create(vals)
        #raise UserError(_(obj_doctors))


class DiagnosticHospitalisation(models.Model):
    """ Gestion des diagnostics dans le circuit hospitalisation"""

    _inherit = 'module.diagnostics'

    diagnostic_hospi = fields.Many2one('module.hospitalisation', string="Hospitalisation")

    @api.model
    def create(self, vals):
        #vals['origine'] = "Hospitalisation"
        return super(DiagnosticHospitalisation, self).create(vals)


# class BlocHospitalisation(models.Model):
    # """ Gestion des activités du bloc operatoire dans le circuit hospitalisation"""

    # _inherit = 'module.blocoperatoire'

    # bloc_hospi = fields.Many2one('module.hospitalisation', string="Hospitalisation")


