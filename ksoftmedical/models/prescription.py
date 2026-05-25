# -*- coding: utf-8 -*-
#
# Auteur : BKM
# Date   : 11 Avril 22
################################
from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from datetime import datetime, date, timedelta
import logging
_logger = logging.getLogger(__name__)

class ModuleOrdonnanceModule(models.Model):

    """ Gestion des Ordonnances médicales dans le circuit ambulatoires"""

    _name = 'module.ordonnance'
    _description = 'Ordonnances Médicales'
    _order = 'date_ordonnance desc, id desc'

    def _get_services(self):
        return self.env['ksoft.services'].search([('type_rdv','=','pharma')]).id
    

    def _get_company_currency(self):
        for ordo in self:
            if ordo.patient_id.partner_id.company_id:
                ordo.currency_id = ordo.patient_id.partner_id.sudo().company_id.currency_id
                
            else:
                ordo.currency_id = self.env.company.currency_id
    

    pres_name = fields.Char(string="ID Ordo")
    client = fields.Many2one('res.partner', client="Patient", domain="[('is_company', '=', 'true')]")
    client_name = fields.Char(client="Patient")
    patient_id = fields.Many2one('fertility.patient', string='Patient')
    nompatient = fields.Char(related='patient_id.nom', string="Nom")
    pnompatient = fields.Char(related='patient_id.postnom', string="Postnom")
    prnompatient = fields.Char(related='patient_id.prenom', string="Prenom")
    dob = fields.Date(related='patient_id.birth', string='Date Naiss', readonly=True, )
    sex = fields.Selection([('m', 'Masculin'), ('f', 'Féminin')], string='Sexe',related='patient_id.gender', readonly=True)
    poids = fields.Float(string="Float")
    age = fields.Integer(related='patient_id.age', string='Age', readonly=True)
    parent_id = fields.Many2one(related='patient_id.parent_id', string="Convention")
    matricule = fields.Char(string="Matricule")
    categorie = fields.Selection(related='patient_id.categorie', string="Catégorie")

    categorie2 = fields.Selection([('prive','Privé'),('prive2','Ayant Droit'),('convention','Conventionné'),
                                 ], store=True, string="Catégorie")
    parent_id2 = fields.Many2one('res.partner', string="Convention", domain="[('is_company', '=', 'true')]")

    classe = fields.Selection([('agent','Agent'),('epoux','Epoux(se)'),('enf','Enfants')], string="Classe")

    numero_billet = fields.Char(string="Billet d'envoi")
    email = fields.Char(related='patient_id.email', string="Email")
    phone = fields.Char(related='patient_id.phone', string="Téléphone")
    function = fields.Char(related='patient_id.function', string="Profession")
    date_ordonnance = fields.Date(string='Date', readonly=True, default=fields.Date.today())
    medecin = fields.Many2one('fertility.doctor', required=True, store=True, string="Médecin prescripteur")
    internal_status = fields.Selection([('draft', 'Brouillon'), 
                                        ('invoicing','Facturation'),
                                        ('pret','Pret'),
                                        ('delivered','Livrer'),
                                        ('partiel', 'Partielle'),
                                        ('complte', 'Complete'),
                                        ('canced', 'Annuler')],
                                      default='draft', string='Status')

    status = fields.Selection([
        ('draft','Brouillon'),
        ('invoicing','Facturation'),
        ('pret','Pret'),
        ('partiel', 'Partielle'),
        ('complte', 'Complete'),
        ('delivered','Livrer'),
        ('canced', 'Annuler')], string='Status', compute='_get_status')

    origine = fields.Char(string="Origine")
    num_facture = fields.Char(string="N° Facture")
    # Line des produits
    produit_ids = fields.One2many('module.ordonnance.line','ordonnace_id', string="Produits")

    move_id = fields.Many2one('account.move')
    status_moved = fields.Selection(related='move_id.payment_state', string="Status Facturation", store=True)
    total_invoiced = fields.Monetary(compute='_compute_invoiced_total_amount', string="Montant Total", store=True)
    service_id = fields.Many2one('ksoft.services', string="Service", default=_get_services, store=True, )
    commentaire_medecin = fields.Text(string="Commentaire")

    currency_id = fields.Many2one('res.currency', compute='_get_company_currency', readonly=True,
        string="Currency", help='Utility field to express amount currency')
        
    
    ### Get info session du jour
    code_session= fields.Char(string="Code Session du jour", readonly=True,)
    

    def setInternalStatus(self):
        self.internal_status='pret'

    @api.onchange('patient_id')
    #@api.onchange('client')
    def _onchange_patient_id(self):
        vals = None
        #if self.client.id:
        #    self.onchange_patient_suite(self.client.id)
        
        if self.patient_id:
            self.onchange_patient_suite(self.patient_id)

    def onchange_patient_suite(self, client):
        pt = False
        if client.id:
            #raise UserError()
            pt = client.id

            self.patient_id = self.env['fertility.patient'].browse(pt).id
            self.matricule = self.env['fertility.patient'].browse(pt).matricule
            self.categorie2 = self.env['fertility.patient'].browse(pt).categorie
            self.classe = self.env['fertility.patient'].browse(pt).classe
            self.function = self.env['fertility.patient'].browse(pt).function
            self.parent_id2 = self.env['fertility.patient'].browse(pt).parent_id
            
        return True

    @api.depends('internal_status')
    def _get_status(self):
        for exam in self:   
            # if exam.internal_status == 'invoicing' and exam.status_moved =='paid' :
                # exam.write({'internal_status':'pret'})
            # exam.status = exam.internal_status
            
            if exam.internal_status == 'invoicing':
                _logger.info("################## %s",exam.categorie2)
                
                if exam.move_id and exam.categorie2 == 'convention':
                    if exam.move_id.state == 'posted':
                        exam.write({'internal_status':'pret'})
                
                if exam.move_id and exam.categorie2 != 'convention':
                    if exam.move_id.payment_state in ['partial', 'paid']:
                        exam.write({'internal_status':'pret'})
            exam.status = exam.internal_status

    def change_statut(self):
        self._get_status()
             
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
        
    def action_autoriser(self):
        
        ## Get Code Jour of Session
        today = fields.Datetime.now()
        date_format = '%Y-%m-%d %H:%M:%S'
           
        query = """
                select code_jour from account_journal_code 
                where date_ouverture <= '%s' and date_fermeture >= '%s'
                and internal_status = 'cours';
            """ % (today,today)
            
            
        #raise UserError(_((query1)))
        self.env.cr.execute(query)
        res = self.env.cr.fetchone()
        #dt_ouv = datetime.strptime(str(today), date_format)
        #test = self.env['account.journal.code'].browse(2).date_ouverture
        #raise UserError(res)
        #dt_ferme = datetime.strptime(str(date_ferm), date_format)
        #raise UserError(type(res))
        if self:
            
            # session=res[0]
            # #raise UserError(str(session))
            # self.write({'code_session':session})
           
            #self._get_session_day(res)
            move_id = False
            journal_id = self.env['ksoft.appointment'].get_journal_type(self.categorie2)
            ordonnance_ids = self.produit_ids.filtered(lambda ordonnance: ordonnance.internal_status == 'draft' and ordonnance.product.id != False)
            #ordonnance_ids =ordo_ids.filtered(lambda ordonnance: ordonnance.product.id != False)
            lines = []
            
            if ordonnance_ids:
                lines.append( (0,0,{'display_type':'line_section', 'name':'Pharmacie', 'debit':0, 'credit':0, 'account_id':False}) )
                for ordo in ordonnance_ids:
                    #### Recuperer le prix selon la liste de prix defini
                    product_context = dict(
                        self.env.context,
                        partner_id=self.patient_id.partner_id.id,
                        date=fields.Date.today(),
                        uom=ordo.product.uom_id.id,
                    )
                    # prix, ruled = self.patient_id.partner_id.property_product_pricelist.with_context(
                    #   product_context).get_product_price_rule(
                    #   ordo.product, ordo.quantity2,
                    #   self.patient_id.partner_id) if self.patient_id.partner_id.property_product_pricelist else self.product.list_price

                    lines.extend((0, 0, {'product_id': ordo.product.id, 'price_unit': ordo.product.lst_price, 'quantity': ordo.quantity2}))

                #lines.extend( ordonnance_ids.mapped(lambda ordo : (0,0,{'product_id': ordo.product.id, 'price_unit': ordo.product.list_price, 'quantity':ordo.quantity2 })) )
                move_id = self.env['account.move'].create({
                    'move_type':'out_invoice',
                    'journal_id':journal_id,
                    'patient_id':self.patient_id.id,
                    'client_name':self.client_name,
                    'numero_billet':self.numero_billet,
                    'prescription_id': self.id,
                    'libelle':'pharmacie',
                    'code_jour':self.code_session,
                    'partner_id':self.patient_id.partner_id.id,
                    'convention_id':self.parent_id2.id,
                    'matricule':self.matricule,
                    'service_id2': self.service_id.id,
                    #'rubrique_id':2,
                    'medecin_id2': self.medecin.id,
                    'categorie':self.categorie2,
                    'classe':self.classe,
                    'invoice_line_ids': lines
                    })
                
                # self.move_id.write({
                #   'invoice_line_ids': lines
                # })

                if move_id.id:
                    ordonnance_ids.write({'move_id':move_id.id})
                    self.write({'move_id':move_id.id})
            
                if self.categorie == 'convention':
                    self.internal_status = 'invoicing'
                else:
                    self.internal_status = 'invoicing'
                    
                    
                message = "ORDONNANCE AUTORISEE"
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
                raise UserError("Aucun produit à autoriser,")
            # message = "LIVRAISON DES PRODUITS AUTORISEE"
            # return {
                # 'type': 'ir.actions.client',
                # 'tag': 'display_notification',
                # 'params': {
                    # 'type': 'danger',
                    # 'message': message,
                    # 'next': {'type': 'ir.actions.act_window_close'},
                # }
            # }
        else:
            raise UserError("Aucune session ouverte ne correspond à cette période, veuillez ouvrir une nouvelle session ou contatez l'administrateur")
            
    def action_partielle_livraison(self):
        self.internal_status = 'partiel'

    def action_complete_livraison(self):
        self.internal_status = 'complte'

    def action_cancel(self):
        self.internal_status = 'complte'

    def unlink(self):
        #self.ensure_one()
        return super(ModuleOrdonnanceModule, self).unlink()


class ModuleOrdonnaceLine(models.Model):

    _name = "module.ordonnance.line"

    patient_id = fields.Many2one('fertility.patient', string='Patient')
    nompatient = fields.Char(related='patient_id.nom', string="Nom", store=True)
    pnompatient = fields.Char(related='patient_id.postnom', string="Postnom", store=True)
    prnompatient = fields.Char(related='patient_id.prenom', string="Prenom", store=True)
    dob = fields.Date(related='patient_id.birth', string='Date Naiss', readonly=True, store=True)
    sex = fields.Selection(related="patient_id.gender", string='Sexe', readonly=True, store=True)
    poids = fields.Float(string="Float")
    age = fields.Integer(related='patient_id.age', string='Age', readonly=True, store=True)

    parent_id = fields.Many2one(related='patient_id.parent_id', string="Convention", store=True)
    matricule = fields.Char(related='patient_id.matricule', string="Matricule", store=True)
    categorie = fields.Selection(related='patient_id.categorie', string="Catégorie", store=True)
    classe = fields.Selection(related='patient_id.classe', string="Classe")

    numero_billet = fields.Char(related='appointment_id.numero_billet',string="Billet d'envoi", store=True)
    email = fields.Char(related='patient_id.email', string="Email", store=True)
    phone = fields.Char(related='patient_id.phone', string="Téléphone", store=True)
    function = fields.Char(related='patient_id.function', string="Profession", store=True)
    
    code = fields.Char(size=256, string='Code')
    ordonnace_id = fields.Many2one('module.ordonnance', string='Ordonnace ID',)
    product = fields.Many2one('product.product', string='Produit', required=False,
                            domain=[('is_medicaments', '=', True)],
                            help='Product')
    unit_product = fields.Many2one('uom.uom', string="Unité")
    product_name = fields.Char(string='Autres Produits')
    is_print = fields.Boolean(string="Select", default=True)
    price_unit = fields.Float(string='Prix unitaire')
    # 'price_total' : fields.function(_amount_line,  string='Prix Total', type = "float", digits_compute=dp.get_precision('Prix Total')),
    #price_total = fields.Float(string="Prix Total")
    quantity = fields.Integer(string='Qtité demandée')
    quantity2 = fields.Integer(string='Qtité servie')
    note = fields.Html(string='Note')
    date_ordonnance = fields.Date(string="Date", default=fields.Date.today)
    medecin_id = fields.Many2one('res.users', readonly=True, string="Médecin")

    qtity_stock = fields.Integer(string="Stock Actuel", store=True, readonly=False,)

    #Ordonnance mise à jour
    #posologie = fields.Many2one('fertility.posologie', string="Posologie")
    posologie = fields.Char(string="Posologie")
    px = fields.Selection([('OD','OEIL DROIT'),('OG','OEIL GAUCHE'),('Yex','2 YEUX')], string='OEIL')
    appointment_id = fields.Many2one('fertility.appointment', ondelete="cascade", string="Consultations Médicales")
    product_uom = fields.Many2one('uom.uom', 'Unité de mesure',)
    internal_status = fields.Selection([('draft', 'Brouillon'), 
                                        ('invoicing','Facturation'),
                                        ('pret','Pret'),
                                        ('partiel', 'Partielle'),
                                        ('delivered','Livre'),
                                        ('complte', 'Complete'),
                                        ('canced', 'Annuler')], default="draft", string="Status de Livraison")

    status = fields.Selection([
        ('draft','Brouillon'),
        ('invoicing','Facturation'),
        ('delivered','Livre'),
        ('pret','Pret'),
        ('partiel', 'Partielle'),
        ('complte', 'Complete'),
        ('canced', 'Annuler')], string='Status',default="draft", )

    is_modify = fields.Boolean(string="Modifié")

    move_id = fields.Many2one('account.move')

    @api.model
    def default_get(self, fields):
        res = super(ModuleOrdonnaceLine, self).default_get(fields)
        res['medecin_id'] = self.env.user.id
        return res

    # def _get_product_mainstock_qty(self):
    #   location = self.env['ksoft.services'].search([('type_rdv','=','pharma')]).entrepot

    #   if location:
    #       for line in self:
    #           line.unit_product = self.env['product.product'].browse(line.product.id).uom_po_id.id
    #           if not line.product:
    #               continue
    #           if line.ordonnace_id.service_id:
    #               line.qtity_stock = self.env['stock.quant'].search([('product_id','=',line.product.id),('location_id','=',line.ordonnace_id.service_id.entrepot.id)]).quantity
                
    #           else:
    #               location = self.env['ksoft.services'].search([('type_rdv','=','pharma')]).entrepot
    #               line.qtity_stock = self.env['stock.quant'].search([('product_id','=',line.product.id),('location_id','=',location.id)]).quantity
                
    #           #line.product_uom = line.product.product_tmpl_id.uom_id.id
    #   else:
    #       raise UserError("Aucun dépot pharmaceutique n'a été config")

    @api.onchange('product')
    def _onchange_product_id(self):
        for line in self:
            line.unit_product = self.env['product.product'].browse(line.product.id).uom_po_id.id
            if not line.product:
                continue
            if line.ordonnace_id.service_id:
                line.qtity_stock = self.env['stock.quant'].search([('product_id','=',line.product.id),('location_id','=',line.ordonnace_id.service_id.entrepot.id)]).quantity
            
            else:
                location = self.env['ksoft.services'].search([('type_rdv','=','pharma')]).entrepot
                line.qtity_stock = self.env['stock.quant'].search([('product_id','=',line.product.id),('location_id','=',location.id)]).quantity
            
            line.product_uom = line.product.product_tmpl_id.uom_id.id

class Posologie(models.Model):
    """
    Modèle pour la gestion des posologies de manière automatique
    """
    _name = "fertility.posologie"

    name = fields.Char(string="Posologie")
    intitule_posologie=fields.Char(string="Intitulé posologie", readonly=True)

    #def name_get(self):
    #   result = []
    #   for rec in self:
    #       result.append((rec.id, "%s" %(rec.intitule_posologie)))
    #   return result


class AUtresProduits(models.Model):
    """
    Modèle pour la gestion des produits non existant à la pharmacie de manière automatique
    """
    _name = "fertility.autres.produits"

    #name = fields.Char(string="Posologie")
    intitule_produit = fields.Char(string="Posologie")

    def name_get(self):
        result = []
        for rec in self:
            #name=rec.intitule_posologie
            #result.append(name)
            result.append((rec.id, "%s" % (rec.intitule_produit)))
        return result


class TypesLunettes(models.Model):
    """
    Modèle pour la gestion des types de lunettes
    """
    _name = "fertility.types.lunettes"

    #name = fields.Char(string="Posologie")
    intitule_type_lunette = fields.Char(string="Type de lunette")

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, "%s" % (rec.intitule_type_lunette)))
        return result



    
class ModuleLunetteDetails(models.Model):
    """
    Module qui gère les elements prescriptions de lunettes
    """

    _name = "module.lunette.details"

    patient_id = fields.Many2one('fertility.patient', string='Patient')
    nompatient = fields.Char(related='patient_id.nom', string="Nom")
    pnompatient = fields.Char(related='patient_id.postnom', string="Postnom")
    prnompatient = fields.Char(related='patient_id.prenom', string="Prenom")
    dob = fields.Date(related='patient_id.birth', string='Date Naiss', readonly=True, )
    sex = fields.Selection([('m', 'Masculin'), ('f', 'Féminin')], string='Sexe', readonly=True)
    poids = fields.Float(string="Float")
    age = fields.Integer(related='patient_id.age', string='Age', readonly=True)
    is_print = fields.Boolean(string="Select", default=True)
    parent_id = fields.Many2one(related='patient_id.parent_id', string="Convention")
    matricule = fields.Char(related='patient_id.matricule', string="Matricule")
    categorie = fields.Selection(related='patient_id.categorie', string="Catégorie")
    classe = fields.Selection(related='patient_id.classe', string="Classe")

    numero_billet = fields.Char(string="Billet d'envoi")
    email = fields.Char(related='patient_id.email', string="Email")
    phone = fields.Char(related='patient_id.phone', string="Téléphone")
    function = fields.Char(related='patient_id.function', string="Profession")
    
    code = fields.Char(size=256, string='Code')

    date_prescription = fields.Date(string="Date", default=fields.Datetime.now())
    product = fields.Many2one('product.product', string='Produit', required=True,
                            domain=[('is_medicaments', '=', True)],
                            help='Product')
    appointment_id = fields.Many2one('fertility.appointment', ondelete="cascade", string="Consultations Médicales")
    status  = fields.Selection([('draft', 'Brouillon'), ('invoicing', 'Facturation'), 
                                ('pret', 'Pret'),('paid', 'Payé'), 
                                ('delivered', 'Livré'),
                                ('partiel', 'Partielle'),
                                ('complte', 'Complete'),
                                ('delivered','Livre'),
                                ('canced', 'Annuler')], 'Etat')
    internal_status  = fields.Selection([('draft', 'Brouillon'), ('invoicing', 'Facturation'),
                                         ('pret', 'Pret'),('paid', 'Payé'), ('delivered', 'Livré'),
                                         ('partiel', 'Partielle'),
                                         ('complte', 'Complete'),
                                         ('delivered','Livre'),
                                         ('canced', 'Annuler')], 
                                        'Etat', default='draft')
    is_modify = fields.Boolean(string="Modifié")  
    move_id = fields.Many2one('account.move')
    lunette_id = fields.Many2one('module.prescription', string='Prescription ID',)
    
    is_print = fields.Boolean(string="Select", default=True)
    price_unit = fields.Float(string='Prix unitaire')
    quantity = fields.Integer(string='Qtité demandée')

    qtity_stock = fields.Integer(string="Stock Actuel", readonly=True)
    product_uom = fields.Many2one('uom.uom', 'Unité de mesure',)

    @api.onchange('product')
    def _onchange_product_id(self):
        for line in self:
            if not line.product:
                continue
            if line.lunette_id.service_id:
                line.qtity_stock = self.env['stock.quant'].search([('product_id','=',line.product.id),('location_id','=',line.lunette_id.service_id.entrepot.id)]).quantity
            
            else:
                location = self.env['ksoft.services'].search([('type_rdv','=','shop')]).entrepot
                line.qtity_stock = self.env['stock.quant'].search([('product_id','=',line.product.id),('location_id','=',location.id)]).quantity
            
            line.product_uom = line.product.product_tmpl_id.uom_id.id



class ModulePrescriptionLunette(models.Model):
    """
    Module qui gère les prescriptions de lunettes
    """

    _name = "module.prescription.lunette"

    patient_id = fields.Many2one('fertility.patient', string='Patient')
    nompatient = fields.Char(related='patient_id.nom', string="Nom")
    pnompatient = fields.Char(related='patient_id.postnom', string="Postnom")
    prnompatient = fields.Char(related='patient_id.prenom', string="Prenom")
    dob = fields.Date(related='patient_id.birth', string='Date Naiss', readonly=True, )
    sex = fields.Selection([('m', 'Masculin'), ('f', 'Féminin')], string='Sexe', readonly=True)
    poids = fields.Float(string="Float")
    age = fields.Integer(related='patient_id.age', string='Age', readonly=True)
    is_print = fields.Boolean(string="Select", default=True)
    parent_id = fields.Many2one(related='patient_id.parent_id', string="Convention")
    matricule = fields.Char(related='patient_id.matricule', string="Matricule")
    categorie = fields.Selection(related='patient_id.categorie', string="Catégorie")
    classe = fields.Selection(related='patient_id.classe', string="Classe")

    numero_billet = fields.Char(related='appointment_id.numero_billet',string="Billet d'envoi")
    email = fields.Char(related='patient_id.email', string="Email")
    phone = fields.Char(related='patient_id.phone', string="Téléphone")
    function = fields.Char(related='patient_id.function', string="Profession")
    
    code = fields.Char(size=256, string='Code')
    
    px = fields.Selection([('OD','OD'),('OG','OG'),('Yex','2 YEUX')], size=256, string='PX')
    sphere = fields.Char(size=256, string='Sphere')
    cylindre = fields.Char(size=256, string='Cylindre')
    axe = fields.Char(size=256, string='Axe')
    addition = fields.Char(size=256, string='Addition')
    prescription_id = fields.Many2one('module.prescription', string='Prescription ID',)
    av1 = fields.Char(size=256, string='AV')
    av2 = fields.Char(size=256, string='AV')
    note = fields.Html(string='Observation')
    date_prescription = fields.Date(string="Date", default=fields.Date.today)
    medecin_id = fields.Many2one('res.users', readonly=True, string="Médecin")

    appointment_id = fields.Many2one('fertility.appointment', ondelete="cascade", string="Consultations Médicales")
    status = fields.Selection([('draft', 'Brouillon'), ('invoicing', 'Facturation'),
                                ('pret', 'Pret'),('paid', 'Payé'),
                                ('partiel', 'Partielle'),
                                ('complte', 'Complete'),
                                ('delivered','Livre'),
                                ('canced', 'Annuler'), 
                                ('delivered', 'Livré')], 'Etat', default='draft')
    internal_status  = fields.Selection([('draft', 'Brouillon'), ('invoicing', 'Facturation'),
                                         ('pret', 'Pret'),('paid', 'Payé'), 
                                          ('partiel', 'Partielle'),
                                         ('complte', 'Complete'),
                                         ('delivered','Livre'),
                                         ('canced', 'Annuler'),
                                         ('delivered', 'Livré')], 
                                        'Etat', default='draft')
    is_modify = fields.Boolean(string="Modifié")  
    move_id = fields.Many2one('account.move')
    #produit_ids = fields.One2many('module.lunette.details','lunette_id', string="Details elements")

    @api.model
    def default_get(self, fields):
        res = super(ModulePrescriptionLunette, self).default_get(fields)
        res['medecin_id'] = self.env.user.id
        return res


class PrescriptionModule(models.Model):
    """ Gestion des Prescriptions médicales dans le circuit hospitalisation"""

    _name = 'module.prescription'
    _description = 'Prescription Médicale'
    _order = 'date_prescription desc, id desc'


    def _get_services(self):
        return self.env['ksoft.services'].search([('type_rdv','=','shop')]).id

    pres_name = fields.Char(string="ID Prescr")
    patient_id = fields.Many2one('fertility.patient', string='Patient')
    nompatient = fields.Char(related='patient_id.nom', string="Nom")
    pnompatient = fields.Char(related='patient_id.postnom', string="Postnom")
    prnompatient = fields.Char(related='patient_id.prenom', string="Prenom")
    age = fields.Integer(related='patient_id.age', string='Age', readonly=True)
    parent_id = fields.Many2one(related='patient_id.parent_id', string="Convention")
    matricule = fields.Char(related='patient_id.matricule', string="Matricule")
    categorie = fields.Selection(related='patient_id.categorie', string="Catégorie")
    classe = fields.Selection(related='patient_id.classe', string="Classe")

    numero_billet = fields.Char(string="Billet d'envoi")
    email = fields.Char(related='patient_id.email', string="Email")
    phone = fields.Char(related='patient_id.phone', string="Téléphone")
    function = fields.Char(related='patient_id.function', string="Profession")
    date_prescription = fields.Datetime(string='Date', readonly=True, default=fields.Datetime.now())
    medecin = fields.Many2one('fertility.doctor', readonly=True, string="Médecin")

    internal_status = fields.Selection([('draft', 'Brouillon'),
                                        ('invoicing', 'Facturation'),
                                        ('pret', 'Pret'),
                                        ('delivered', 'Livre'),
                                        ('partiel', 'Partielle'),
                                        ('complte', 'Complete'),
                                        ('delivered', 'Livre'),
                                        ('canced', 'Annuler'),
                                        ('canced', 'Annuler')],
                                       default='draft', string='Status')

    status = fields.Selection([
        ('draft', 'Brouillon'),
        ('invoicing', 'Facturation'),
        ('pret', 'Pret'),
        ('partiel', 'Partielle'),
        ('complte', 'Complete'),
        ('delivered', 'Livre'),
        ('canced', 'Annuler'),
        ('delivered', 'Livre'), ('canced', 'Annuler')], compute='_get_status', string='Status', )

    origine = fields.Char(string="Origine")
    num_facture = fields.Char(string="N° Facture")
    description = fields.Char(string="Posologie")
    is_select = fields.Char(string="Select")
    medicament = fields.Many2one('product.product', string="Produits")
    is_print = fields.Boolean(string="#", default=True)
    move_id = fields.Many2one('account.move')
    # Line des produits
    produit_ids = fields.One2many('module.prescription.lunette','prescription_id', string="Prescription")
    invoice_prd_ids = fields.One2many('module.lunette.details','lunette_id', string="Details elements")

    status_moved = fields.Selection(related='move_id.payment_state', string="Status Facturation", store=True)
    service_id = fields.Many2one('ksoft.services', string="Service", default=_get_services, store=True,)
    type_lunette = fields.Many2one('fertility.types.lunettes', string="Type de lunette", readonly=True)
    cord_commentaire=fields.Text(string="Commentaire")
    od_dist = fields.Float(string="OD")
    og_dist = fields.Float(string="OG")
    dist_pp = fields.Float(string="PD")



    @api.onchange('patient_id')
    def _onchange_patient_id(self):
        if self.patient_id.id:
            self.onchange_patient_suite(self.patient_id.id)

    def _get_status(self):
        for exam in self:
            if exam.internal_status == 'invoicing' and exam.status_moved =='paid' :
                exam.write({'internal_status':'pret'})
            exam.status = exam.internal_status

    def onchange_patient_suite(self, patient):
        pt = False
        if patient:
            pt = patient
            self.patient_id = self.env['fertility.patient'].browse(pt).id
            self.parent_id = self.env['fertility.patient'].browse(pt).parent_id
            self.matricule = self.env['fertility.patient'].browse(pt).matricule
            self.categorie = self.env['fertility.patient'].browse(pt).categorie
            self.classe = self.env['fertility.patient'].browse(pt).classe
            self.function = self.env['fertility.patient'].browse(pt).function
    
    # def action_autoriser(self):
        # self.internal_status = 'invoicing'

    def action_complete_livraison(self):
        self.internal_status = 'delivered'

    def action_cancel(self):
        self.internal_status = 'canced'

    def action_retour_brouillon(self):
        self.internal_status = 'draft'

    def action_retour_pret(self):
        self.internal_status = 'pret'

    def unlink(self):
        #self.ensure_one()

        return super(PrescriptionModule, self).unlink()


    def action_autoriser(self):
        move_id = False
        journal_id = self.env['ksoft.appointment'].get_journal_type(self.categorie)
        ordonnance_ids = self.invoice_prd_ids.filtered(lambda ordonnance: ordonnance.internal_status == 'draft')

        lines = []
        
        if ordonnance_ids:
            lines.append( (0,0,{'display_type':'line_section', 'name':'Shop Optique', 'debit':0, 'credit':0, 'account_id':False}) )

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
                    ordo.product, ordo.quantity,
                    self.patient_id.partner_id) if self.patient_id.partner_id.property_product_pricelist else self.product.list_price

                lines.extend((0, 0, {'product_id': ordo.product.id, 'price_unit': prix, 'quantity': ordo.quantity}))

            #lines.extend( ordonnance_ids.mapped(lambda ordo : (0,0,{'product_id': ordo.product.id, 'price_unit': ordo.product.list_price, 'quantity':ordo.quantity, 'date_realisation':ordo.date_prescription })) )

            move_id = self.env['account.move'].create({

                'move_type':'out_invoice',
                'journal_id':journal_id,

                'patient_id':self.patient_id.id,
                'numero_billet':self.numero_billet,
                'lunettes_id': self.id,
                'libelle':'shop_optique',

                'partner_id':self.patient_id.partner_id.id,
                'convention_id':self.parent_id.id,
                'matricule':self.matricule,
                'categorie':self.categorie,
                'classe':self.classe,
                'invoice_line_ids': lines
                })
            #move_id.write({'invoice_line_ids':lines})
            if move_id.id:
                ordonnance_ids.write({'move_id':move_id.id, 'internal_status':'invoicing'})
                self.write({'move_id':move_id.id, 'internal_status':'invoicing'})

            if self.categorie == 'convention':
                self.internal_status = 'pret'
            else:
                self.internal_status = 'invoicing'

            #self.env['sh.announcement'].notifShopRec()
        else:
            raise UserError("Eléments à facturer manquants")

    def setInternalStatus(self):
        self.internal_status = 'pret'

