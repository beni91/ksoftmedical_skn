# -*- coding: utf-8 -*-
from html import escape as html_escape, unescape as html_unescape
import logging
import re

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import html_sanitize

_logger = logging.getLogger(__name__)


class WizardDossierPatient(models.TransientModel):
    _name = 'fertility.wizard.dossier.medical.patient'
    _description = 'Wizard dossier medical patient'

    @api.model
    def _default_source_appointment(self):
        context = self.env.context
        if context.get('active_model') not in (None, 'fertility.appointment'):
            return False
        active_id = context.get('active_id')
        if not active_id:
            return False
        try:
            active_id = int(active_id)
        except (TypeError, ValueError):
            return False
        return self.env['fertility.appointment'].browse(active_id).exists().id

    source_appointment_id = fields.Many2one(
        'fertility.appointment', readonly=True,
        default=_default_source_appointment, string='Consultation source')
    content = fields.Html(
        compute='_compute_content', string='', readonly=True,
        sanitize=True, strip_style=False, strip_classes=False)
    nbre_ligne = fields.Integer(string='Consultations par page', default=5)
    service = fields.Many2one(
        'product.template', domain="[('is_consultation','=',True)]",
        string='Consultations')
    medecin = fields.Many2one('fertility.doctor', string='Médecin')
    speciality = fields.Many2one('fertility.doctor.speciality', string='Spécialité')
    appointment_id = fields.Many2one('fertility.appointment', string='Consultation ID')
    type_consultation = fields.Selection([
        ('stand', 'Standard'), ('ophta', 'Ophtalmologie'), ('dent', 'Dentiste'),
        ('gync', 'Gynéco-Obstétrique'), ('vasc', 'Vasculaire'),
        ('nephr', 'Néphrologue'), ('autres', 'Autres')],
        string='Type de consultation')
    # Un filtre vide conserve tous les types dans l'historique initial.
    page = fields.Integer(default=1, string='Page')
    total_count = fields.Integer(compute='_compute_content', string='Consultations')
    has_previous = fields.Boolean(compute='_compute_content')
    has_next = fields.Boolean(compute='_compute_content')
    page_label = fields.Char(compute='_compute_content', string='Affichage')

    @api.constrains('nbre_ligne', 'page')
    def _check_pagination(self):
        for wizard in self:
            if wizard.nbre_ligne < 1 or wizard.page < 1:
                raise ValidationError(_('Le nombre de consultations et la page doivent être positifs.'))

    @api.onchange('service', 'medecin', 'speciality', 'appointment_id',
                  'type_consultation', 'nbre_ligne', 'source_appointment_id')
    def _onchange_filters(self):
        self.page = 1

    @api.depends('source_appointment_id', 'service', 'medecin', 'speciality',
                 'appointment_id', 'type_consultation', 'nbre_ligne', 'page')
    def _compute_content(self):
        for wizard in self:
            wizard.total_count = 0
            wizard.has_previous = False
            wizard.has_next = False
            wizard.page_label = ''
            wizard.content = wizard.get_appointment_report()

    def _speciality_domain(self):
        """Utilise une relation réelle, sans inventer son nom dans les modèles métier."""
        if not self.speciality:
            return []
        Doctor = self.env['fertility.doctor']
        candidates = [name for name, field in Doctor._fields.items()
                      if field.type in ('many2one', 'many2many')
                      and getattr(field, 'comodel_name', None) == 'fertility.doctor.speciality']
        if len(candidates) != 1:
            raise UserError(_(
                'Le filtre Spécialité nécessite de préciser la relation du modèle '
                'fertility.doctor vers fertility.doctor.speciality. '
                'Aucune relation unique ne peut être déterminée.'))
        return [('doctor_id.' + candidates[0], 'in', self.speciality.ids)]

    def _appointment_domain(self, patient):
        domain = [('patient_id', '=', patient.id)]
        if self.service:
            domain.append(('product_id', '=', self.service.id))
        if self.medecin:
            domain.append(('doctor_id', '=', self.medecin.id))
        if self.appointment_id:
            domain.append(('id', '=', self.appointment_id.id))
        if self.type_consultation:
            domain.append(('type_consultation', '=', self.type_consultation))
        return domain + self._speciality_domain()

    def _text(self, value, empty='—'):
        if value is False or value is None or value == '':
            return html_escape(empty)
        return html_escape(str(value), quote=True)

    def _field_html(self, record, name, empty='Non renseigné'):
        value = record[name]
        if value is False or value is None or value == '':
            return self._text(None, empty)
        text = str(value)
        # Certains champs Text/Char contiennent aussi du contenu d'editeur HTML.
        html_tags = r'</?(?:p|div|span|br|strong|b|em|i|u|s|ul|ol|li|table|thead|tbody|tfoot|tr|td|th|h[1-6]|a|img|blockquote|pre|code|font|hr|script|style)\b[^>]*>'
        if record._fields[name].type == 'html' or re.search(html_tags, text, re.I):
            return str(html_sanitize(text))
        decoded = html_unescape(text)
        if re.search(html_tags, decoded, re.I):
            return str(html_sanitize(decoded))
        return self._text(value).replace('\n', '<br/>')

    def _date_html(self, record, name):
        value = record[name]
        if not value:
            return '—'
        if record._fields[name].type == 'datetime':
            local_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(value))
            return self._text(local_date.strftime('%d/%m/%Y à %H:%M'))
        return self._text(fields.Date.to_date(value).strftime('%d/%m/%Y'))

    def _selection_html(self, record, name):
        labels = record.fields_get([name])[name].get('selection', [])
        return self._text(dict(labels).get(record[name], record[name]))

    def _card(self, title, body, alert=False):
        if not body:
            return ''
        color = '#9a5353' if alert else '#3f6869'
        background = '#fcf6f6' if alert else '#ffffff'
        return (
            '<div style="margin-bottom:8px;border:1px solid #dce4e8;'
            'border-radius:7px;background:%s;overflow-wrap:break-word;">'
            '<div style="padding:7px 10px;border-bottom:1px solid #e7ecef;'
            'color:%s;font-weight:600;font-size:12px;">%s</div>'
            '<div style="padding:8px 10px;">%s</div></div>'
        ) % (background, color, self._text(title), body)

    def _columns(self, left, right):
        if not left or not right:
            return left or right
        return (
            '<div class="row" style="margin-left:-4px;margin-right:-4px;">'
            '<div class="col-12 col-md-6" style="padding-left:4px;padding-right:4px;min-width:0;">%s</div>'
            '<div class="col-12 col-md-6" style="padding-left:4px;padding-right:4px;min-width:0;">%s</div>'
            '</div>'
        ) % (left, right)

    def _render_html_table(self, headings, rows):
        if not rows:
            return ''
        header = ''.join('<th style="padding:6px;text-align:left;background:#f2f5f7;'
                         'border-bottom:1px solid #dce4e8;">%s</th>' % self._text(h) for h in headings)
        body = ''.join('<tr>%s</tr>' % ''.join(
            '<td style="padding:6px;vertical-align:top;border-bottom:1px solid #edf0f2;'
            'overflow-wrap:anywhere;">%s</td>' % cell for cell in row) for row in rows)
        return ('<table style="width:100%%;table-layout:fixed;border-collapse:collapse;font-size:12px;">'
                '<thead><tr>%s</tr></thead><tbody>%s</tbody></table>') % (header, body)

    def _group_records(self, model, field, ids):
        grouped = {}
        if ids:
            for record in self.env[model].search([(field, 'in', ids)]):
                key = record[field].id
                grouped.setdefault(key, self.env[model])
                grouped[key] |= record
        return grouped

    def get_examen_labo(self, lab_request_id, records=None):
        if records is None:
            records = self.env['fertility.examen.labo'].search([('examen_id', '=', lab_request_id)]) if lab_request_id else self.env['fertility.examen.labo']
        rows = [[self._text(lab.analyse.name), self._field_html(lab, 'description', '—'),
                 self._field_html(lab, 'valeur_normale', '—'), self._field_html(lab, 'examen_text', '—')]
                for lab in records]
        return self._card('Laboratoire', self._render_html_table(['Analyse', 'Résultat', 'V.N.', 'Clinique'], rows))

    def get_diagnostic(self, appointment_id, records=None):
        if records is None:
            records = self.env['module.diagnostics'].search([('appointment_id', '=', appointment_id)]) if appointment_id else self.env['module.diagnostics']
        rows = [[self._text(diag.pathologie.name), self._field_html(diag, 'description', '—')]
                for diag in records]
        return self._card('Diagnostics', self._render_html_table(['Pathologie', 'Observation'], rows))

    def get_traitement(self, appointment_id):
        return self._card('Traitement', self._field_html(appointment_id, 'traitement')) if appointment_id.traitement else ''

    def get_motif(self, appointment_id):
        if not appointment_id.motif_rdv:
            return ''
        return '<div style="margin-top:5px;"><strong>Motif : </strong>%s</div>' % self._field_html(appointment_id, 'motif_rdv')

    def _antecedents(self, appointment):
        atcd = '<ul style="margin:0;padding-left:18px;">%s</ul>' % ''.join(
            '<li>%s</li>' % self._text(record.allergie.name) for record in appointment.atcd_medical
        ) if appointment.atcd_medical else 'Non renseignés'
        allergies = '<ul style="margin:0;padding-left:18px;">%s</ul>' % ''.join(
            '<li>%s</li>' % self._text(record.allergie_details.name) for record in appointment.allergie
        ) if appointment.allergie else 'Non renseignées'
        return self._columns(self._card('Antécédents de la consultation', atcd),
                             self._card('Allergies de la consultation', allergies, alert=bool(appointment.allergie)))

    def get_anamnèse(self, appointment_id, include_antecedents=True):
        blocks = []
        for name, label in [('anamnese', 'Plaintes'), ('hstr_affection', 'Histoire de la maladie'),
                            ('cpm_anamnese', "Complément d’anamnèse")]:
            if appointment_id[name]:
                blocks.append(self._card(label, self._field_html(appointment_id, name)))
        # Compatibilité avec les appels externes de la méthode existante.
        if include_antecedents:
            blocks.append(self._antecedents(appointment_id))
        return ''.join(blocks)

    def _vitals_table(self, records):
        # Aucun champ de fréquence respiratoire ni unité non confirmée n'est inventé.
        columns = [('temperature', 'T°'), ('tension', 'TA'), ('glycemie', 'Glycémie'),
                   ('pulsation', 'FC'), ('saturation', 'Saturation'),
                   ('taille', 'Taille'), ('poids', 'Poids')]
        rows = [[self._text(record[name]) for name, label in columns] for record in records]
        return self._card('Signes vitaux', self._render_html_table([label for name, label in columns], rows))

    def get_examen_medical(self, appointment_id, include_vitals=True):
        if appointment_id.type_consultation != 'stand':
            return ''
        content = self._vitals_table(appointment_id.done_feuille_signes_vitaux) if include_vitals else ''
        if appointment_id.examen_physique:
            content += self._card('Examen physique', self._field_html(appointment_id, 'examen_physique'))
        return content

    def get_signes_vitaux(self, signes_id):
        records = self.env['module.feuille.surveillance'].search([
            ('feuille_signesV_id', '=', signes_id)]) if signes_id else self.env['module.feuille.surveillance']
        return self._vitals_table(records)

    def get_examen_imagerie2(self, lab_request_id):
        records = self.env['fertility.examen.imagerie2'].search([
            ('examen_id', '=', lab_request_id)]) if lab_request_id else self.env['fertility.examen.imagerie2']
        rows = [[self._date_html(lab, 'date_request'), self._field_html(lab, 'examen_text', '—')] for lab in records]
        return self._card('Examens d’imagerie', self._render_html_table(['Date de demande', 'Examen'], rows))

    def get_pharmacie(self, lab_request_id, records=None):
        if records is None:
            records = self.env['module.ordonnance.line'].search([
                ('appointment_id', '=', lab_request_id)]) if lab_request_id else self.env['module.ordonnance.line']
        rows = [[self._text(line.product.name), self._field_html(line, 'posologie', '—'),
                 self._text(line.medecin_id.display_name)] for line in records]
        return self._card('Prescriptions', self._render_html_table(['Produit', 'Posologie', 'Demandeur'], rows))

    def get_examen_imagerie(self, lab_request_id, records=None):
        if records is None:
            records = self.env['fertility.examen.imagerie'].search([
                ('examen_id', '=', lab_request_id)]) if lab_request_id else self.env['fertility.examen.imagerie']
        parts = []
        for lab in records:
            body = []
            if lab.analyse.name:
                body.append('<div><strong>%s</strong></div>' % self._text(lab.analyse.name))
            if lab.clinique:
                body.append('<div style="margin-top:4px;"><strong>Clinique : </strong>%s</div>' % self._field_html(lab, 'clinique'))
            if lab.protocol:
                body.append('<div style="margin-top:4px;"><strong>Protocole</strong></div><div>%s</div>' % self._field_html(lab, 'protocol'))
            parts.append('<div style="padding:5px 0;border-bottom:1px solid #edf0f2;">%s</div>' % (''.join(body) or 'Non renseigné'))
        return self._card('Imagerie', ''.join(parts))

    def _patient_header(self, patient):
        partner = patient.partner_id
        details = [
            ('Sexe', self._selection_html(patient, 'gender')),
            ('Naissance', self._date_html(patient, 'birth')),
            ('Téléphone', self._text(partner.phone)),
            ('Catégorie', self._selection_html(patient, 'categorie')),
            ('Convention', self._text(patient.parent_id.display_name)),
            ('Adresse', self._text(partner.street)),
            ('Profession', self._text(partner.function))]
        items = ''.join('<span style="display:inline-block;margin:3px 16px 3px 0;">'
                        '<span style="color:#697b88;">%s : </span>%s</span>' % (label, value)
                        for label, value in details)
        return ('<div style="background:#fff;border:1px solid #dce4e8;border-left:4px solid #5f8b88;'
                'border-radius:8px;padding:12px;margin-bottom:10px;">'
                '<div style="font-size:11px;color:#697b88;">DOSSIER MÉDICAL · HISTORIQUE DES CONSULTATIONS</div>'
                '<div style="font-size:21px;font-weight:600;color:#294751;margin:3px 0;">%s</div>'
                '<div>%s</div></div>') % (self._text(partner.display_name), items)

    def get_appointment_report(self):
        self.ensure_one()
        source = self.source_appointment_id.exists()
        if not source or not source.patient_id:
            return self._card('Dossier médical', 'Ouvrez le dossier depuis une consultation disposant d’un patient.')
        patient = source.patient_id
        Appointment = self.env['fertility.appointment']
        domain = self._appointment_domain(patient)
        total = Appointment.search_count(domain)
        limit = max(self.nbre_ligne or 5, 1)
        last_page = max((total + limit - 1) // limit, 1)
        current_page = min(max(self.page or 1, 1), last_page)
        offset = (current_page - 1) * limit
        appointments = Appointment.search(domain, order='date desc, id desc', limit=limit, offset=offset)
        self.total_count = total
        self.has_previous = current_page > 1
        self.has_next = current_page < last_page
        self.page_label = _('Consultations %s–%s sur %s · Page %s/%s') % (
            offset + 1 if total else 0, offset + len(appointments), total, current_page, last_page)

        # Une recherche par rubrique pour la page, sans sudo ni SQL direct.
        request_ids = appointments.mapped('consult_examen_id').ids
        labs = self._group_records('fertility.examen.labo', 'examen_id', request_ids)
        imaging = self._group_records('fertility.examen.imagerie', 'examen_id', request_ids)
        diagnoses = self._group_records('module.diagnostics', 'appointment_id', appointments.ids)
        prescriptions = self._group_records('module.ordonnance.line', 'appointment_id', appointments.ids)
        # Le resume provient toujours de la derniere consultation du patient,
        # independamment des filtres et de la page de l'historique.
        latest_appointment = Appointment.search(
            [('patient_id', '=', patient.id)], order='date desc, id desc', limit=1)
        antecedents = self._field_html(latest_appointment, 'resume_atcd') if latest_appointment else 'Non renseigné'

        antecedents_card = (
            '<div style="margin-bottom:10px;border:1px solid #dc3545;'
            'border-radius:7px;overflow:hidden;background:#fff;">'

            '<div style="background:#dc3545;color:#fff;'
            'padding:9px 12px;font-weight:700;font-size:14px;">'
            'ANTÉCÉDENTS'
            '</div>'

            '<div style="padding:10px 12px;">%s</div>'
            '</div>'
        ) % antecedents

        parts = [
            self._patient_header(patient),
            antecedents_card,
            '<div style="color:#697b88;margin:0 0 8px;">%s</div>'
            % self._text(self.page_label),
        ]
        if not appointments:
            parts.append(self._card('Historique', 'Aucune consultation ne correspond aux filtres sélectionnés.'))
        for appointment in appointments:
            header = ('<div style="background:#edf3f4;padding:10px 12px;border-bottom:1px solid #dce4e8;">'
                      '<strong style="color:#294751;">%s · %s</strong>'
                      '<span style="display:inline-block;margin-left:12px;color:#566d78;">%s</span>%s</div>') % (
                          self._date_html(appointment, 'date'), self._text(appointment.product_id.name),
                          self._text(appointment.doctor_id.name), self.get_motif(appointment))
            body = ''
            if appointment.type_consultation == 'stand':
                body += self._vitals_table(appointment.done_feuille_signes_vitaux)
            left = self.get_anamnèse(appointment, include_antecedents=False)
            right = self.get_examen_medical(appointment, include_vitals=False)
            if appointment.diagnostics_ids:
                right += self.get_diagnostic(appointment.id, diagnoses.get(appointment.id, self.env['module.diagnostics']))
            right += self.get_traitement(appointment)
            body += self._columns(left, right)
            request_id = appointment.consult_examen_id.id
            lab_content = self.get_examen_labo(request_id, labs.get(request_id, self.env['fertility.examen.labo'])) if appointment.labo_ids else ''
            image_content = self.get_examen_imagerie(request_id, imaging.get(request_id, self.env['fertility.examen.imagerie'])) if appointment.imagerie_ids else ''
            body += self._columns(lab_content, image_content)
            if appointment.done_ordonnance:
                body += self.get_pharmacie(appointment.id, prescriptions.get(appointment.id, self.env['module.ordonnance.line']))
            parts.append('<div style="border:1px solid #dce4e8;border-radius:8px;background:white;'
                         'margin-bottom:14px;">%s<div style="padding:10px;">%s</div></div>' % (header, body))
        return '<div style="width:100%%;background:#f5f7f9;padding:10px;color:#334651;font-size:13px;line-height:1.45;">%s</div>' % ''.join(parts)

    def _reopen_dossier(self):
        self.ensure_one()
        view = self.env['ir.ui.view'].search([
            ('model', '=', self._name), ('type', '=', 'form'),
            ('name', '=', 'fertility.wizard.dossier.medical.patient.modern.form')], limit=1)
        return {'name': _('Dossier médical du patient'), 'type': 'ir.actions.act_window',
                'res_model': self._name, 'res_id': self.id, 'view_mode': 'form',
                'views': [(view.id or False, 'form')], 'target': 'current',
                'context': dict(self.env.context)}

    def get_dossier_content(self):
        self.ensure_one()
        self.page = 1
        self._compute_content()
        return self._reopen_dossier()

    def action_previous_page(self):
        self.ensure_one()
        limit = max(self.nbre_ligne or 5, 1)
        last_page = max((self.total_count + limit - 1) // limit, 1)
        self.page = max(min(self.page or 1, last_page) - 1, 1)
        return self._reopen_dossier()

    def action_next_page(self):
        self.ensure_one()
        limit = max(self.nbre_ligne or 5, 1)
        last_page = max((self.total_count + limit - 1) // limit, 1)
        self.page = min(max(self.page or 1, 1) + 1, last_page)
        return self._reopen_dossier()


class WizardReservationDuJour(models.TransientModel):
    _name = 'fertility.wizard.appointment.reservation.day'
    _description = 'Liste des reservations du jour'


    def get_dossier_content(self):
        # context = self.env.context
        # return '<h1>'+  str(context.get('patient_id')) + '</p>'
        # load patient consultation

        active_id = self._context.get('active_id')
        brw_id = self.env['ksoft.appointment'].browse(int(active_id))
        patient_id = brw_id.patient_id.id
        date_reservation = brw_id.date_rdv
        etat = ""


        query = """
              SELECT appointment.date_rdv, appointment.time_rdv, patient_info.name_patient, appointment.categorie, doctor.name, appointment.ref_moved, appointment.internal_status FROM ksoft_appointment AS appointment
              INNER JOIN (SELECT res.display_name AS name_patient, patient.id AS id_patient FROM res_partner AS res, fertility_patient AS patient WHERE res.id = patient.partner_id) AS patient_info
              ON appointment.patient_id = patient_info.id_patient
              INNER JOIN fertility_doctor AS doctor ON appointment.medecin = doctor.id AND appointment.date_rdv BETWEEN '%s' AND '%s'


            """ % (date_reservation.strftime('%Y-%m-%d 00:00:00'), date_reservation.strftime('%Y-%m-%d 23:59:59'))
            #self.env.cr.execute(query, {tuple(self.start_date),tuple(self.end_date),tuple(self.journal_payement.id)})
        self.env.cr.execute(query)
        appointments = self.env.cr.fetchall()
        #patient_id = self.env.context.get('patient_id')
        #patient_id = 33  ('date_heure_rdv','&lt;=',time.strftime('%Y-%m-%d 23:59:59')),('date_heure_rdv','&gt;',time.strftime('%Y-%m-%d 00:00:00'))
        #print("ID du Patient",patient_id) ('invoice_date', '>=', self.start_date)

        #sappointments = self.env['ksoft.appointment'].search([('date_rdv','>=', date_reservation.strftime('%Y-%m-%d 23:59:59')),('date_rdv','<=', date_reservation.strftime('%Y-%m-%d 00:00:00'))])
        #appointments = self.env['fertility.appointment'].search([])
        content = ""
        content += '<table width="900" border=0>'
        content += '<tr><td width="900"><b><h3 style="text-align:center">RESERVATION RDV DU '+ str(date_reservation.strftime('%d-%m-%Y')) +'<h3></b></td></tr>'
        content += '<tr><td width="900" style="text-align:right;color:red;">Il y a au total '+ str(len(appointments)) +' reservations à ce jour</td></tr>'
        content += '</table>'

        content += '<br/>'
        content += '<table width="900" border=1 class="table">'
        content += '<thead><tr class="table-active" style="text-transform:uppercase;text-align:center;">'
        content += '<th class="text-primary">Date de rdv</th>'
        content += '<th class="text-primary">Type rdv</th>'
        content += '<th class="text-primary">Patient</th>'
        content += '<th class="text-primary">Catég.</th>'
        content += '<th class="text-primary">docteur</th>'
        content += '<th class="text-primary">N° Facturation</th>'
        content += '<th class="text-primary">Etat</th>'
        content += '</tr></thead>'

        for appointment in appointments:
            if str(appointment[6]) == 'valid':
                etat = "confirmé"
            else:
                etat = "Non confirmé"
             
            content += '<tbody><tr><td>'+ str(appointment[0].strftime('%d-%m-%Y %H:%M:%S')) +'</td>'
            content += '<td>'+ str(appointment[1]) +'</td>'
            content += '<td>'+ str(appointment[2]) +'</td>'
            content += '<td>'+ str(appointment[3]) +'</td>'
            content += '<td>'+ str(appointment[4]) +'</td>'
            content += '<td>'+ str(appointment[5]) +'</td>'
            content += '<td>'+ etat  +'</td>'
            content += '</tbody></tr>'
            etat = ""
        content += '</table>'
        content += '</br>'
         
        return content

    content = fields.Html(default=get_dossier_content, string="", readonly=True)
         