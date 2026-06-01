# -*- coding: utf-8 -*-
# Auteur : BKM
# Date   : 11 Avril 22
################################
from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
import logging
_logger = logging.getLogger(__name__)

class ProductTemplateModule(models.Model):
    """ Produit template """

    _inherit = 'product.template'

    is_consultation = fields.Boolean('Consultations', default=False)
    is_chirurgie = fields.Boolean('Chirurgies', default=False)
    is_labo = fields.Boolean('Examen de Laboratoire', default=False)
    is_imagerie = fields.Boolean('Examen Imagerie', default=False)
    is_actes_medicaux = fields.Boolean('Actes Médicaux', default=False)
    is_shop = fields.Boolean('Shop Optique', default=False)
    is_actes_inf = fields.Boolean('Actes Infirmiers', default=False)
    is_medicaments = fields.Boolean('Médicaments', default=False)
    is_materiels = fields.Boolean('Materiels', default=False)
    is_autres = fields.Boolean('Autres', default=False)
    is_chambre = fields.Boolean('Chambres', default=False)

class CategoryProductTemplateModule(models.Model):
    """ Categorie Produit template """

    _inherit = 'product.category'

    code_service = fields.Char(string='Code Service')