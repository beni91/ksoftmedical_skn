# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class NextRdvWizard(models.TransientModel):
    _name = 'next.appointement.wizard'
    _description = "Wizard pour le next rdv"

    patient = fields.Many2one('fertility.patient', string='Patient', required=True)
    medecin = fields.Many2one('fertility.doctor', string='Medecin', required=True)
    date_heure = fields.Datetime(string='Date et heure', required=True)
    receptioniste = fields.Many2one('res.users',required=False, string='Receptioniste')
    motif_rdv = fields.Text(string='Motif du RDV')
    #Pour le notification
    message =fields.Char('Nouveau follow up')
    state = fields.Selection([('to_send', 'To Send'),
                              ('sent', 'Sent')],
                             string="Status notification", required=True, default='to_send')

    def create_notify_followUp(self):
        """
            Creation et notification du prochain rdv à la reception
        """
                ##Creation du follow Up
        followUp={
            'patient_id':self.patient.id,
            'date_rdv':self.date_heure,
            'medecin':self.medecin.id,
            'motif':self.motif_rdv,
            #'is_followUp_Destinataire':self.receptioniste.id,
            'is_followUp':True
        }
        self.env['ksoft.appointment'].create(followUp)

            ## Notification de follow up à la reception

        #notifications = self.env['next.appointement.wizard'].search(
        #    [('receptioniste', '=', self.receptioniste.id), ('state', '=', 'to_send')])
        #notify=self.env['ksoft.appointment'].search([('is_followUp','=',True),('is_followUp_Destinataire','=',10)])
        #names = notifications.mapped('message')
        #names = notify.mapped('message')
        #for rec in notifications:
        #    rec.state = 'sent'
        #return names
        #for rec in self.env['ksoft.appointment'] :
        #    rec.medecin.is_followUp_Destinataire.notify_danger("New followUp")

                ##Notification de creation au medecin
        msg=("Vous avez notifié un prochain RDV à la Reception")
        return {
           'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'warning',
                'message': msg,
                'user_id': 10,
                'next': {'type': 'ir.actions.act_window_close'},
                'sticky': False,
            }
        }


    @api.model
    def default_get(self, fields):
        res = super(NextRdvWizard, self).default_get(fields)
        active_id=self._context.get('active_id')
        brw_id=self.env['fertility.appointment'].browse(int(active_id))

        if active_id :
            res['patient']=brw_id.patient_id.id
            res['medecin']=brw_id.doctor_id.id

        return res