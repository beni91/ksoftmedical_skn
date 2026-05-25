# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class AnnulerRdvWizard(models.TransientModel):
    _name = 'annuler.appointement.wizard'
    _description = "Wizard pour annuler un rdv"

    motif = fields.Text(string='Motif Annulation', required=True)

    def valider_annulation(self):
        """
            annulation des RDV
        """
        active_id = self._context.get('active_id')                    #recupère l'id du record ouvert
        upd_var = self.env['ksoft.appointment'].browse(active_id)     #Objet tempo des var à màj
                                                                    # Ce dico fait la correspondance entre les champs du wizard et ceux du modèle
        vals = {'motannul':self.motif,
              'etat':'annul'}
        upd_var.write(vals)                                         # Application des màj aux varibles correspondantes

        # MARQUAGE DE LA FACTURE CORRESPONDANTE

        #ref_moved_appoint=self.env['ksoft.appointment'].browse(active_id).ref_moved #Recuperer la valeur de ref_moved depuis appointement

        #query ="""UPDATE account_move set etat_rdv_fac =%s WHERE name LIKE %s"""

        #tuple=("FAC ANNULEE", ref_moved_appoint)
        #self.env.cr.execute(query, tuple)
