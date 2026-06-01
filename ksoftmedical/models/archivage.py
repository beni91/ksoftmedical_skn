# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ArchiveDossierPatient(models.Model):
    _name = 'fertility.archive.patient'
    _description = 'Dossier Archivé de patient'

    date_consult = fields.Date('Date de consultation')
    date_entree = fields.Date('Date Entrée')
    date_sortie = fields.Date('Date Sortie')    
    medecin = fields.Char('Médecin')
    type_consult = fields.Char('Consultation')   
    resume_consult = fields.Html('Résumé consultation')
    resume_hospi = fields.Html('Résumé Hospitalisation')
    patient = fields.Char('Patient')
    patient_id = fields.Many2one('fertility.patient', string='Patient')
    societe = fields.Char('Société')
    type_archive = fields.Selection([('consultation','Consultation'),('hospitalisation','Hospitalisation')], string='Type Archive')


