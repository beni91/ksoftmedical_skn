from odoo import api, fields, models
import logging
_logger = logging.getLogger(__name__)

class WizardDossierPatient(models.TransientModel):
    _name = 'fertility.wizard.dossier.medical.patient'
    _description = 'Wizard dossier medical patient'

    def get_examen_labo(self, lab_request_id):
        lab_exams = self.env['fertility.examen.labo'].search([('examen_id', '=', lab_request_id)])
        content = "" 

        #if lab_exams
        content += '<div>'
        
        content += '<table width="100%" border="1">'
        content += '<tr><th colspan="5" style="background-color:#52be80;text-align:center"><b>LABORATOIRE</b></th></tr>'

        content += '<tr style="text-align:center"><th width="30"><b>Analyses</b></th><th width="25"><b>Résultat</b></th>'
        content += '<th width="20"><b>V.N</b></th><th width="20"><b>Cliniques</b></th></tr>'
        for lab in lab_exams:
            exam = result = vn = ""
            analyse_name =  str(lab.analyse.name) if lab.analyse.name else ''
            exam =  str(lab.examen_text) 
            result =  str(lab.description) 
            vn = str(lab.valeur_normale)
            content += '<tr><td>'+analyse_name + '</td><td style="text-align:center"><b>'+ result + '</b></td><td style="text-align:center">'+ vn + '</td><td>'+str(lab.examen_text)+ '</td></tr>'

        content += '</table>'
        content += '</div></br>'

        return content

    def get_diagnostic(self, appointment_id):
        diagnostic_ids = self.env['module.diagnostics'].search([('appointment_id', '=', appointment_id)])
        content = "" 

        content += '<div>'
        content += '<table width="100%" border="1">'
        content += '<tr><th colspan="5" style="background-color:#52be80;text-align:center"><b>DIAGNOSTICS</b></th></tr>'

        content += '<tr style="text-align:center"><th width="35"><b>Pathologie</b></th><th width="20"><b>Observation</b></th></tr>'
        for diag in diagnostic_ids:
            diagn_name =observ= ""
            diagn_name =  str(diag.pathologie.name)
            observ =  str(diag.description) 
            content += '<tr><td>'+diagn_name + '</td><td><b>'+observ + '</b></td></tr>'

            content += '</table>'
            content += '</div>'

        return content
        
    def get_traitement(self, appointment_id):
        ## 
        content = ""
        if appointment_id.traitement:
            content += '<div>'
            content += '</br>'
            content += '<table width="100%" border=0>'
            content += '<tr style="background-color:#52be80;text-align:center" ><th><b>TRAITEMENT</b></th></tr>'
           
            content += '<tr><td style="text-align:justify; padding:5px !important">'+ str(appointment_id.traitement) +'</td></tr>'
        return content
        
    def get_motif(self, appointment_id):
        ## 
        content = ""
        if appointment_id.motif_rdv:
            content += '<div>'
            content += '</br>'
            content += '<table width="100%" border=0>'
            content += '<tr style="background-color:#52be80;text-align:center" ><th><b>MOTIF DE CONSULTATION</b></th></tr>'
           
            content += '<tr><td style="text-align:justify; padding:5px !important">'+ str(appointment_id.motif_rdv) +'</td></tr>'
        return content
                
    def get_anamnèse(self, appointment_id):
        ## Examen medical générale
        content = ""
        if appointment_id:
            content += '<div>'
            content += '</br>'
            content += '<table width="100%" border=0>'
            content += '<tr style="background-color:#52be80;text-align:center" ><th><b>ANAMNESE</b></th></tr>'
            if appointment_id.anamnese:
                content += '<tr style="text-align:left" ><th><b>Plaintes:</b></th></tr>'
                content += '<tr style="text-align:justify; padding:5px !important"><td>'+ str(appointment_id.anamnese) +'</td></tr>'
            
            if appointment_id.hstr_affection:
                content += '<tr style="text-align:left" ><th><b>Histoire de la maladie</b></th></tr>'
                content += '<tr style="text-align:justify; padding:5px !important"><td>'+ str(appointment_id.hstr_affection) +'</td></tr>'
            
            if appointment_id.allergie or appointment_id.atcd_medical:
                content += '<tr style="text-align:left" ><th><b>Antécédents</b></th></tr>'
                content += '<tr><td>'
                content += '<table width="100%" border=1>'
                
                content += '<tr style="text-align:center" ><th><b>ATCD</b></th><th><b>Allergie</b></th></tr>'
                # for allergie_id in appointment_id.allergie:
                content += '<tr>'
                content += '<td><ul>'
                for atcd_id in appointment_id.atcd_medical:
                    content += '<li>'+ str(atcd_id.allergie.name) +'</li>'
                content += '</ul></td>'  
                
                content += '<td><ul>'
                for allergie_id in appointment_id.allergie:
                    content += '<li>'+ str(allergie_id.allergie_details.name) +'</li>'
                content += '</ul></td>'  
                content += '</tr>'
                    # content += '<table width="100%" border=1>'
                    # content += '<tr style="text-align:center" ><th><b>Allergie</b></th><th><b>Commentaire</b></th></tr>'
                    # for allergie_id in appointment_id.allergie:
                        # content += '<tr><td width="50%">'+ str(allergie_id.allergie_details.name) +'</td><td width="50%">'+ str(allergie_id.comment) +'</td></tr>'
                    
                    # content += '</table></br>'
                
                # if appointment_id.atcd_medical:
                    # content += '<table width="100%" border=1>'
                    # content += '<tr style="text-align:center" ><th><b>ATCD</b></th><th><b>Type ATCD</b></th></tr>'
                    # for atcd_id in appointment_id.atcd_medical:
                        # content += '<tr><td width="50%">'+ str(atcd_id.allergie.name) +'</td><td width="50%">'+ str(atcd_id.type_atcd) +'</td></tr>'
                    
                content += '</table></br>'
                content += '</td></tr>'

            if appointment_id.cpm_anamnese:
                content += '<tr style="text-align:left; padding:5px !important" ><th><b>Complément d\'anamnèse</b></th></tr>'
                content += '<tr style="text-align:justify"><td>'+ str(appointment_id.cpm_anamnese) +'</td></tr>'
                
            content += '</table>'
            content += '</div>'
            content += '</br>'

        return content
    
    def get_examen_medical(self, appointment_id):
        ## Examen medical générale
        content = ""
        if appointment_id.type_consultation == "stand":
            content += '<div>'
            content += '<table width="100%" border=0>'
            content += '<tr style="background-color:#52be80;text-align:center" ><th colspan="7"><b>EXAMEN MEDICAL</b></th></tr>'
            content += '<tr style="text-align:center" ><th colspan="7"><b>EXAMEN MEDICAL GENERAL</b></th></tr>'
            content += '<tr><td>'
            if appointment_id.done_feuille_signes_vitaux:
                content += '<table width="100%" border=0>'
                content += '<tr style="text-align:left" ><th><b>Signes Vitaux</b></th></tr>'
                content += '</table>'
                content += '<table width="100%" border=1>'
                content += '<tr style="text-align:center"><th><b>T°<b/></th><th><b>TA</b></th><th><b>Glyc.</b></th><th><b>FC</b></th><th><b>FR</b></th><th><b>Taille</b></th><th><b>Poids</b></th></tr>'
                for signes in appointment_id.done_feuille_signes_vitaux:
                    
                    # bmp =  float(signes.bmi) if signes.bmi else ''
                    # etat = ""
                    # if signes.bmi_state == "sp":
                        # etat = "SousPoids"
                    # elif signes.bmi_state  == "normal" :
                        # etat = "Normal"
                    # elif signes.bmi_state == "srp":
                        # etat = "Surpoids"
                    # elif signes.bmi_state == "obez1" :
                        # etat = "Obèsité modérée"
                    # elif signes.bmi_state == "obez2" :
                        # etat = "Obèsité sévère"
                    # else:
                        # etat = "Obèsité morbide"
                    
                    content += '<tr style="text-align:center"><td>'+str(signes.temperature)+'</td><td>'+str(signes.tension)+'</td>'
                    content += '<td>'+str(signes.pulsation)+'</td><td>'+str(signes.glycemie)+'</td><td>'+str(signes.saturation)+'</td>'
                    content += '<td>'+str(signes.taille)+'</td><td>'+str(signes.poids)+'</td></tr>'
                content += '</td></tr></table></br>'   
                
            content += '<tr style="text-align:left" ><th><b>Evaluation Générale</b></th></tr>'
            content += '<tr style="text-align:justify; padding:5px !important;"><td>'+ str(appointment_id.examen_physique) +'</td></tr>'
            content += '</table>'
            content += '</div>'
            content += '</br>'

        return content
        
    def get_signes_vitaux(self, signes_id):
        signes_id = self.env['module.feuille.surveillance'].search([('feuille_signesV_id', '=', signes_id)])
        content = ""

        content += '<div>'
        content += '</br>'
        content += '<table width="100%" border=1>'
        content += '<tr style="background-color:#CCCCCC;text-align:center" ><th colspan="7"><b>SIGNES VITAUX</b></th></tr>'
        content += '<tr style="text-align:center"><th><b>T°<b/></th><th><b>TA</b></th><th><b>Glyc.</b></th><th><b>FC</b></th><th><b>FR</b></th><th><b>Taille</b></th><th><b>Poids</b></th></tr>'
        for signes in signes_id:
            content += '<tr style="text-align:center"><td>'+str(signes.temperature)+'</td><td>'+str(signes.tension)+'</td>'
            content += '<td>'+str(signes.pulsation)+'</td><td>'+str(signes.glycemie)+'</td><td>'+str(signes.saturation)+'</td>'
            content += '<td>'+str(signes.taille)+'</td><td>'+str(signes.poids)+'</td></tr>'
        content += '</table>'
        content += '</div>'
        content += '</br>'

        return content

    def get_examen_imagerie2(self, lab_request_id):
        lab_exams = self.env['fertility.examen.imagerie2'].search([('examen_id', '=', lab_request_id)])
        content = ""
        content += '<table width="900" border=1>'
        content += '<tr style="text-align:center"><td width="900" colspan="14"><b>EXAMENS IMAGERIE</b></td></tr>'
        content += '<tr style="text-align:center"><td width="100"><b>Date demande</b></td><td width="400"><b>Examen</b></td></tr>'
        #content += '<tr><td width="900" colspan="4">Cliniques: </br>' + lab_exams.cliniques + '<td></tr>'
        for lab in lab_exams:
            #analyse_name =  str(lab.analyse.name) if lab.analyse.name else ''
            #exam =  str(lab.examen_text) if lab.examen_text else ''
            #result =  str(lab.description) if lab.description else ''
            #vn = str(lab.valeur_normale) if lab.valeur_normale else s''
            content += '<tr><td width="100">' + lab.date_request.strftime('%Y-%m-%d') + '</td><td>'+str(lab.examen_text)+ '</td></tr>'
            content += '</table>'

        return content

    def get_pharmacie(self, lab_request_id):
        lab_exams = self.env['module.ordonnance.line'].search([('appointment_id', '=', lab_request_id)])
        #print(lab_exams)

        content = ""
        content += '</br>'
        content += '<div>'
        content += '<table width="100%" border="1">'
        content += '<tr><th colspan="5" style="background-color:#52be80;text-align:center"><b>PHARMACIE</b></th></tr>'
        content += '<tr style="text-align:center">'
        content += '<td width="20"><b>Produits</b></td><td width="20"><b>Posologie</b></td><td width="10"><b>Demandeur</b></td></tr>'

        for lab in lab_exams:
            posologie = str(lab.posologie) 
            produit = str(lab.product.name) 

            content += '<tr><td>' + produit + '</td><td style="text-align:center">' + posologie + '</td><td style="text-align:center">' + str(lab.medecin_id.display_name) + '</td></tr>'
        content += '</table>'
        content += '</div>'
        content += '</br>'

        return content

    def get_examen_imagerie(self, lab_request_id):
        lab_exams = self.env['fertility.examen.imagerie'].search([('examen_id', '=', lab_request_id)])
        print(lab_exams)

        content = ""
        content += '<div>'
        #if lab_exams:
        content += '<table width="100%" border="1">'
        content += '<tr><th style="background-color:#52be80;text-align:center"><b>IMAGERIE</b></th></tr>'
        

        for lab in lab_exams:
            content += '<tr><td>'
            if lab.analyse.name:
                content += '<p><b>Analyse : </b>'+ str(lab.analyse.name) +'</p>'
                
            if lab.clinique:
                content += '<p><b>Clinique : </b>'+ str(lab.clinique) +'</p>'
                
            if lab.protocol:
                content += '<p><b>Protocole : </b></p>'
                content += '<p>'+ str(lab.protocol) +'</p>'
            content += '</td></tr>'
            
            # content += '<table width="100%" border="1">'
            # content += '<tr style="text-align:center">'
            # content += '<td><b>Analyse :'+ str(lab.analyse.name) +'</b></td><td><b>Clinique:'+ str(lab.clinique) +'</b></td></tr>'
            
            # content += '<tr><td colspan="2">' + str(lab.protocol)  + '</td></tr>'
        content += '</table>'
        content += '</div>'
        content += '</br>'

        return content
          
    def get_appointment_report(self):
        # context = self.env.context
        # return '<h1>'+  str(context.get('patient_id')) + '</p>'
        # load patient consultation

        active_id = self._context.get('active_id')
        brw_id = self.env['fertility.appointment'].browse(int(active_id))
        patient_id = brw_id.patient_id.id
        #patient_id = self.env.context.get('patient_id')
        #patient_id = 33
        #print("ID du Patient",patient_id)

        appointments = self.env['fertility.appointment'].search([('patient_id','=',patient_id)])
       
        content = ""
        content += '<table width="900" border=0>'
        content += '<tr><td width="900"><b><h4 style="text-align:center">RAPPORT DE CONSULTATION<h4></b></td></tr>'
        content += '</table>'
        
        content += '<div style="margin-bottom:2px;height:150px !important; padding:10px; border: 1px solid gray;">'
        content += '<table width="49%" border="0" style="float:left; width:49%">'
        content += '<tr><td width="200"><b>Patient</b></td><td width="600">' + str(brw_id.patient_id.partner_id.display_name) + '</td></tr>'
        content += '<tr><td width="200"><b>Sexe</b></td><td width="600">' + str(brw_id.patient_id.gender) + '</td></tr>'
        content += '<tr><td width="200"><b>Date Naiss.</b></td><td width="600">' + brw_id.patient_id.birth.strftime('%d-%m-%Y') + '</td></tr>'
        content += '<tr><td width="200"><b>Tél.</b></td><td width="600">' + str(brw_id.patient_id.partner_id.phone) + '</td></tr>'
        content += '<tr><td width="200"><b>Adresse</b></td><td width="600">' + str(brw_id.patient_id.partner_id.street) + '</td></tr>'
        content += '<tr><td width="200"><b>Profession</b></td><td width="600">' + str(brw_id.patient_id.partner_id.function) + '</td></tr>'
        content += '</table>'
           

        content += '<table width="49%" border="0" style="float:right; width:49%">'
        content += '<tr><td width="200"><b>Catégorie</b></td><td width="600">' + str(brw_id.patient_id.categorie) + '</td></tr>'
        content += '<tr><td width="200"><b>Convention</b></td><td width="600">' + str(brw_id.patient_id.parent_id.display_name) + '</td></tr>'

        content += '</table>'
        content += '</div>'
      

        content += '</br>'
        for appointment in appointments:
            content += '</br>'
            content += '<center><table width="800" border=1 class="center">'
            content += '<tr><td width="200"><b>Date et Heure</b></td><td width="600" style="text-align:center">' + appointment.date.strftime('%Y-%m-%d') + '</td></tr>'
            content += '<tr><td width="200"><b>Consultation</b></td><td width="600" style="text-align:center">' + str(appointment.product_id.name) + '</td></tr>'
            content += '<tr><td width="200" ><b>Docteur</b></td><td width="600" style="text-align:center">' + str(appointment.doctor_id.name) + '</td></tr>'
            content += '<tr><td width="200" ><b>Motif</b></td><td width="600" style="text-align:center">' + str(appointment.motif_rdv) + '</td></tr>'
            content += '</table></center>'

            # add vital sign
            content += '</br>'
            
            ## Motif de la consultation
            if appointment.motif_rdv:
                content += self.get_motif(appointment) 
            
            ## Anamnèse
            if appointment:
                content += self.get_anamnèse(appointment) 
            
            ## Examen médical
            if appointment.type_consultation:
                content += self.get_examen_medical(appointment) 
            
            ## Examen laboratoire
            if appointment.labo_ids:
                content += self.get_examen_labo(appointment.consult_examen_id.id)
           
            ## Examen imagerie    
            if appointment.imagerie_ids:
                content += self.get_examen_imagerie(appointment.consult_examen_id.id)
            
            ## Autres examen et tests
            
            ## Diagnostics
            if appointment.diagnostics_ids:
                content += self.get_diagnostic(appointment.id)
                
            ## Traitements
            if appointment.traitement:
                content += self.get_traitement(appointment)
                
            ## Prescriptions
            if appointment.done_ordonnance:
                content += self.get_pharmacie(appointment.id)
                
            ## Suivelllance
            ## Suivi ambulatoire
            ## Suivi hospitalier
            ## Recommandations
                
            
        return content
    
    def get_dossier_content(self):
        # context = self.env.context
        # return '<h1>'+  str(context.get('patient_id')) + '</p>'
        # load patient consultation

        active_id = self._context.get('active_id')
    
    content = fields.Html(default=get_appointment_report, string="", readonly=True)
    nbre_ligne = fields.Integer(string="Nbre de ligne", default=5)
    service = fields.Many2one('product.template', domain="[('is_consultation','=',True)]", string="Consultations")  
    medecin = fields.Many2one('fertility.doctor', string="Médecin")
    speciality = fields.Many2one('fertility.doctor.speciality', string="Spécialité")
    appointment_id = fields.Many2one('fertility.appointment', string="Consultation ID")
    
    type_consultation = fields.Selection([('stand', 'Standard'),('ophta', 'Ophtamologie'),('dent', 'Dentiste'),
                                            ('gync', 'Gynéco-Obstétrique'),('vasc', 'Vasculaire'),('nephr', 'Nephrologue'),
                                            ('autres', 'Autres'),], default='stand',string="Type de consultation")


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
         