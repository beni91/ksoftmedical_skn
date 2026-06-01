from odoo import api, fields, models
import logging
_logger = logging.getLogger(__name__)

class WizardDossierPatient(models.TransientModel):
     _name = 'fertility.wizard.dossier.medical.patient'
     _description = 'Wizard dossier medical patient'

     def get_examen_labo(self, lab_request_id):
       lab_exams = self.env['fertility.examen.labo'].search([('examen_id', '=', lab_request_id)])
       content = "" 
       content += '<div style="margin-bottom:15px;">'
       content += '<div style="float:left; width:49%">'
       content += '<table width="100%" border="1">'
       content += '<tr><th colspan="5" style="background-color:#CCCCCC;text-align:center"><b>LABORATOIRE</b></th></tr>'
       
       content += '<tr style="text-align:center"><th width="15"><b>Date<b/></th><th width="20"><b>Analyses</b></th><th width="20"><b>Résultat</b></th>'
       content += '<th width="20"><b>V.N</b></th><th width="20"><b>Cliniques</b></th></tr>'
       for lab in lab_exams:
         exam = result = vn = ""
         analyse_name =  str(lab.analyse.name) if lab.analyse.name else ''
         exam =  str(lab.examen_text) 
         result =  str(lab.description) 
         vn = str(lab.valeur_normale)
         content += '<tr><td>' + lab.date_request.strftime('%Y-%m-%d') + '</td><td>'+analyse_name + '</td><td><b>'+result + '</b></td><td>'+vn + '</td><td>'+str(lab.examen_text)+ '</td></tr>'
      
       content += '</table>'
       content += '</div>'

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
           content += '<tr style="text-align:center"><td>'+str(signes.temperature)+'</td><td>'+str(signes.tension)+'</td><td>'+str(signes.pulsation)+'</td><td>'+str(signes.glycemie)+'</td><td>'+str(signes.saturation)+'</td><td>'+str(signes.taille)+'</td><td>'+str(signes.poids)+'</td></tr>'
           content += '</table>'
           content += '</div>'
           content += '</br>'
       content += '</table>'

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
         #vn = str(lab.valeur_normale) if lab.valeur_normale else ''
         content += '<tr><td width="100">' + lab.date_request.strftime('%Y-%m-%d') + '</td><td>'+str(lab.examen_text)+ '</td></tr>'
       content += '</table>'

       return content
    
     def get_pharmacie(self, lab_request_id):
         lab_exams = self.env['module.ordonnance.line'].search([('appointment_id', '=', lab_request_id)])
         print(lab_exams)

         content = ""
         content += '</br>'
         content += '<div style="float:right; width:49%">'
         content += '<table width="100%" border="1">'
         content += '<tr><th colspan="5" style="background-color:#CCCCCC;text-align:center"><b>PHARMACIE</b></th></tr>'
         content += '<tr style="text-align:center"><td width="15"><b>Date demande</b></td>'
         content += '<td width="20"><b>Produits</b></td><td width="20"><b>Posologie</b></td><td width="10"><b>Demandeur</b></td></tr>'

         for lab in lab_exams:

            posologie = str(lab.posologie) 
            produit = str(lab.product.name) 

            content += '<tr><td>' + lab.date_ordonnance.strftime('%Y-%m-%d') + '</td><td>' + produit + '</td><td>' + posologie + '</td><td>' + str(lab.medecin_id.display_name) + '</td></tr>'
         content += '</table>'
         content += '</div>'
         content += '</br>'
         
         return content

     def get_examen_imagerie(self, lab_request_id):
         lab_exams = self.env['fertility.examen.imagerie'].search([('examen_id', '=', lab_request_id)])
         print(lab_exams)

         content = ""
         content += '<div style="float:right; width:49%">'
         content += '<table width="100%" border="1">'
         content += '<tr><th colspan="5" style="background-color:#CCCCCC;text-align:center"><b>IMAGERIE</b></th></tr>'
         content += '<tr style="text-align:center"><td width="15"><b>Date demande</b></td>'
         content += '<td width="20"><b>Analyse</b></td><td width="20"><b>Clinique</b></td><td width="40"><b>Protocole</b></td><td width="10"><b>Demandeur</b></td></tr>'

         for lab in lab_exams:
            clinique = str(lab.clinique)
            protocol = str(lab.protocol) 
            analyse = str(lab.analyse.name) 

            content += '<tr><td>' + lab.date_request.strftime('%Y-%m-%d') + '</td><td>' + analyse + '</td><td>' + clinique + '</td><td>' + protocol + '</td><td>' + str(lab.demandeur.name) + '</td></tr>'
         content += '</table>'
         content += '</div>'
         content += '</br>'
         
         return content
         
     
     def get_dossier_content(self):
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
        content += '<tr><td width="900"><b><h1 style="text-align:center">HISTORIQUE DU PATIENT<h1></b></td></tr>'
        content += '</table>'
        for appointment in appointments:
            content += '</br></br>'
            content += '<table width="900" border=0>'
            content += '<tr><td width="900" style="text-align:center"><b>---------------------------------------------------------------------------------------------------------------------</b></td></tr>'
            content += '<tr><td width="900" style="text-align:center"><b><font color="#3890FF">############################################################################</font></b></td></tr>'
            content += '<tr><td width="900" style="text-align:center"><b>----------------------------------------------------------------------------------------------------------------</b></td></tr>'
            content += '</table>'
            content += '</br>'
            content += '<center><table width="600" border=1 class="center">'
            content += '<tr><td width="200"><b>Date et Heure</b></td><td width="600" style="text-align:center">' + appointment.date.strftime('%Y-%m-%d') + '</td></tr>'
            content += '<tr><td width="200"><b>Consultation</b></td><td width="600" style="text-align:center">' + str(appointment.product_id.name) + '</td></tr>'
            content += '<tr><td width="200" ><b>Docteur</b></td><td width="600" style="text-align:center">' + str(appointment.doctor_id.name) + '</td></tr>'
            content += '<tr><td width="200" ><b>Motif</b></td><td width="600" style="text-align:center">' + str(appointment.motif_rdv) + '</td></tr>'
            content += '</table></center>'

            # add vital sign
            content += '</br>'
            systolic =  str(appointment.systolic) if appointment.systolic else ''
            bmp =  float(appointment.bmi) if appointment.bmi else ''
            etat = ""
            if appointment.bmi_state == "sp":
                etat = "SousPoids"
            elif appointment.bmi_state  == "normal" :
                etat = "Normal"
            elif appointment.bmi_state == "srp":
                etat = "Surpoids"
            elif appointment.bmi_state == "obez1" :
                etat = "Obèsité modérée"
            elif appointment.bmi_state == "obez2" :
                etat = "Obèsité sévère"
            else:
                etat = "Obèsité morbide"

            content += '<div style="margin-bottom:15px;">'
            content += '<div style="float:left; width:49%">'
            content += '<table width="100%" border="1">'
            content += '<tr><th colspan="4" style="background-color:#CCCCCC;text-align:center"><b>ANTECEDENTS</b></th></tr>'
            content += '<tr style="text-align:center"><th><b>Date<b/></th><th><b>ATCD</b></th><th><b>Descript.</b></th><th><b>Etat</b></th></tr>'
            content += '</table>'
            content += '</div>'
           
                
            content += '<div style="float:right; width:49%">'
            content += '<table width="100%" border="1">'
            content += '<tr><th colspan="4" style="background-color:#CCCCCC;text-align:center"><b>ALLERGIES</b></th></tr>'
            content += '<tr style="text-align:center"><th><b>Date<b/></th><th><b>ALLERGIE</b></th><th><b>Descript.</b></th><th><b>Etat</b></th></tr>'
            content += '</table>'
            content += '</div>'
            content += '</div>'
            content += '</br>'   
            
            if appointment.done_feuille_signes_vitaux:
                content += self.get_signes_vitaux(appointment.id)
   
            if appointment.anamnese or appointment.examen_physique:
                content += '<div>'
                content += '<table width="100%" border=1>'
                content += '<tr style="background-color:#CCCCCC;text-align:center"><th colspan="2"><b>CONSULTATIONS</b></th></tr>'
                if appointment.anamnese:
                    content += '<tr style="text-align:left;"><td style="width:150px;text-align:center;"><b>Anamnèse:<b/></td><td><p>'+ str(appointment.anamnese) +'</p></td><tr>'
                
                if appointment.examen_physique:
                    content += '<tr style="text-align:left;"><td style="width:150px;text-align:center;"><b>Examen Physique:<b/></td><td><p>'+ str(appointment.examen_physique) +'</p></td><tr>'
                content += '</table>'
                content += '</div>'
                content += '</br>'


            if appointment.labo_ids:
                content += self.get_examen_labo(appointment.id)
           
                
            if appointment.imagerie_ids:
                content += self.get_examen_imagerie(appointment.id)
                
            if appointment.done_ordonnance:
                content += self.get_pharmacie(appointment.id)

            # content += '</br>'
            # content += '<table width="900" border=1>'
            # content += '<tr style="background-color:#87CEFA;text-align:center"><th width="900" colspan="14"><b>PACHYMETRIE</b></th></tr>'
            # content += '<tr style="background-color:#87CEFA;text-align:center"><th><b>OD<b/></th><th><b>OS</b></th></tr>'
            # content += '<tr style="text-align:center"><td>' + str(appointment.od_pachymetrie) + '</td><td>' + str(appointment.os_pachymetrie) +'</td></tr>'
            # content += '</table>'

            # content += '</br>'
            # content += '<table width="900" border=1>'
            # content += '<tr style="background-color:#87CEFA;text-align:center"><th width="900" colspan="14"><b>VISION DES COULEURS</b></th></tr>'
            # content += '<tr style="background-color:#87CEFA;text-align:center"><th><b>OD<b/></th><th><b>OS</b></th></tr>'
            # content += '<tr style="text-align:center"><td>' + str(appointment.od_vision_coul) + '</td><td>' + str(appointment.os_vision_coul) +'</td></tr>'
            # content += '</table>'

            # content += '</br>'
            # content += '<table width="900" border=1>'
            # content += '<tr style="background-color:#87CEFA;text-align:center"><th width="900" colspan="6"><b>FICHE OBS MEDECIN</b></th></tr>'
            # content += '<tr style="background-color:#87CEFA;text-align:center"><th colspan="3"><b>Oeil droit<b/></th><th colspan="3"><b>Oeil gauche</b></th></tr>'
            # content += '<tr style="background-color:#87CEFA;text-align:center"><th><b>Laf<b/></th><th><b>Fo</b></th><th><b>Gonioscopie</b></th><th><b>Laf<b/></th><th><b>Fo</b></th><th><b>Gonioscopie</b></th></tr>'
            # #od_gon = dict(appointment._fields['self.gonioscopie_od'].selection).get(appointment.gonioscopie_od)
            # #og_gon = dict(appointment._fields['appointment.gonioscopie_og'].selection).get(appointment.gonioscopie_og)
            # og_gon = ""
            # od_gon = ""
            # if appointment.gonioscopie_og == '1':
            #     og_gon = "1/4"
            # elif appointment.gonioscopie_og == '2':
            #     og_gon = "2/4"
            # elif appointment.gonioscopie_og == '3':
            #     og_gon = "3/4"
            # elif appointment.gonioscopie_og == '4':
            #     og_gon = "4/4"

            # if appointment.gonioscopie_od == '1':
            #     od_gon = "1/4"
            # elif appointment.gonioscopie_od == '2':
            #     od_gon = "2/4"
            # elif appointment.gonioscopie_od == '3':
            #     od_gon = "3/4"
            # elif appointment.gonioscopie_od == '4':
            #     od_gon = "4/4"

            # content += '<tr style="text-align:center"><td>' + str(appointment.laf) + '</td><td>' + str(appointment.fo) +'</td><td>' + od_gon + '</td><td>' + str(appointment.laf2) +'</td><td>' + str(appointment.fo2) + '</td><td>' + og_gon +'</td></tr>'
            # content += '</table>'
            # content += '<table width="900" border=1>'
            # content += '<tr><td width="150"><b>Commentaire</b></td><td>' + str(appointment.commentaire) +'</td></tr>'
            # content += '</table>'

            # # anamnese

            # duree_regle =str(appointment.duree_regle) if appointment.duree_regle else ''
            # durree_cycle = str(appointment.duree_cycle) if appointment.duree_cycle else ''
            # douleur_pelvienne = '<input type="checkbox"  checked onclick="return false;">' if appointment.douleurs_pelviennes else ''
            # dysmnonrhee = '<input type="checkbox"  checked onclick="return false;">' if appointment.dysmenorrhee else ''
            # dyspareunie = '<input type="checkbox"  checked onclick="return false;">' if appointment.dyspareunie else ''
            # menometrorragie = '<input type="checkbox"  checked onclick="return false;">' if appointment.menometrorragie else ''
            # content += '</br>'
            #content += '<table width="900" border=1>'

            #content += '<tr style="background-color:#87CEFA;text-align:center"><td width="900" colspan="2"><b>ANAMNESE</b></td></tr>'
            #if appointment.anamnese:
            #    content += '<tr><td width="200" ><b>Anamnèse</b></td><td>' + str(appointment.anamnese) + '</td></tr>'
            #if douleur_pelvienne:
            #    content += '<tr><td width="200"><b>Douleurs pelviennes</b></td><td>' + douleur_pelvienne + '</td></tr>'
            #if dysmnonrhee:
            #    content += '<tr><td width="200" ><b>Dysménorrhée<b/></td><td>' + dysmnonrhee +  '</td></tr>'
            #if dyspareunie:
            #    content += '<tr><td width="200" ><b>Dyspareunie</b></td><td>' + dyspareunie +  '</td></tr>'
            #if menometrorragie:
            #    content += '<tr><td width="200" ><b>Ménométrorragie</b></td><td>' + menometrorragie +  '</td></tr>'
            #if duree_regle:
            #    content += '<tr><td width="200" ><b>Durée des règles</b></td><td>' + duree_regle + '</td></tr>'
            #if durree_cycle:
            #    content += '<tr><td width="200"><b>Durée des cycles</b></td><td>' + durree_cycle + '</td></tr>'
            #if appointment.physique:
            #    content += '<tr><td width="200" ><b>Examen Physique</b></td><td>' + str(appointment.physique) + '</td></tr>'
            #content += '</table>'

            # if appointment.diagnostics_ids:
            #    content += '</br>'
            #    #content += '<table><tr><td><h3><b>Diagnostics</b></h3></td></tr></table>'
            #    content += '<table width="900" border=1>'
            #    content += '<tr style="background-color:#CCCCCC;text-align:center"><td width="900" colspan="7"><b>DIAGNOSTICS</b></td></tr>'
            #    content += '<tr style="text-align:center"><td><b>Date</b></td><td><b>Pathologie</b></td><td><b>Observation</b></td><td><b>Médecin<b/></td></tr>'
               
            #    for diagnostic in appointment.diagnostics_ids:
            #       description = str(diagnostic.description) if diagnostic.description else ''
            #       explication = str(diagnostic.explication) if diagnostic.explication else ''
            #       origin = ''
            #       if diagnostic.origine ==  'homme':
            #          origin = 'Masculine'
            #       elif diagnostic.origine == 'femme':
            #          origin ='Feminine'   
            #       elif diagnostic.origine == 'mixte':
            #          origin = 'Mixte'

            #       status = ''
            #       if diagnostic.internal_status == 'hypo':
            #          status = 'Hypothèse'
            #       elif diagnostic.internal_status == 'def':
            #          status = 'Définitive'   

            #       content += '<tr ><td width="100">' + str(diagnostic.date_diagnostic.strftime('%Y-%m-%d')) + '</td><td width="150">' + str(diagnostic.pathologie.name) + '</td><td>' + explication + '</td><td>' + str(diagnostic.medecin_diag.name) + '</td></tr>'

            #    content += '</table>'
            #    #content += '<tr><td width="100">' + '<b><font color="#3890FF"> Commentaire : </font></b>' + str(appointment.commentaire) + '</td></tr>'
            
            # if appointment.consult_examen_id:
            #    if self.get_examen_labo(appointment.consult_examen_id.id):
            #        content += '</br>'
            #        content += self.get_examen_labo(appointment.consult_examen_id.id)

            #    if self.get_examen_imagerie2(appointment.consult_examen_id.id):
            #        content += '</br>'
            #        content += self.get_examen_imagerie2(appointment.consult_examen_id.id)

            #    if self.get_examen_imagerie(appointment.consult_examen_id.id):
            #        content += '</br>'
            #        content += self.get_examen_imagerie(appointment.consult_examen_id.id)
            #                             ##Traitement
            # if appointment.done_orientation:
            #     content += '</br>'
            #     # content += '<table><tr><td><h3><b>Diagnostics</b></h3></td></tr></table>'
            #     content += '<table width="900" border=1>'
            #     content += '<tr style="background-color:#CCCCCC;text-align:center"><td width="900" colspan="7"><b>TRAITEMENTS</b></td></tr>'
            #     content += '<tr style="text-align:center"><td width="100"><b>Date</b></td><td width="225"><b>Actes</b></td><td width="225"><b>Protocol</b></td><td width="225"><b>Orientation</b></td><td width="150"><b>Médecin</b></td></tr>'

            #     for diagnostic in appointment.done_orientation:
            #         content += '<tr ><td width="100">' + str(diagnostic.date_orientation.strftime('%Y-%m-%d')) + '</td><td width="150">' + str(diagnostic.product.name) + '</td><td width="100">' + str(diagnostic.protocole) + '</td><td width="100">' + str(diagnostic.orientation) + '</td><td>' + str(diagnostic.medecin_.name) + '</td></tr>'
            #     content += '</table>'

            # # check ordonance
            # ordonance_lines = self.env['module.ordonnance.line'].search([('appointment_id', '=', appointment.id)])
            # if ordonance_lines:
            #    content += '</br>'
               
            #    content += '<table width="900" border=1>'
            #    content += '<tr style="background-color:#CCCCCC;text-align:center"><td width="900" colspan="7"><b>PRESCRIPTIONS MEDICALES</b></td></tr>'
            #    content += '<tr style=";text-align:center"><td width="100"><b>Date</b></td><td width="250"><b>Produit</b></td><td width="150"><b>Autres Produit</b></td><td width="200"><b>Posologie</b></td><td width="50"><b>Qtité</b></td><td width="100"><b>Médecin</b></td></tr>'
                 
            #    for line in ordonance_lines:
            #       product_name = str(line.product.name) if line.product.name else ''
            #       product = str(line.product_name) if line.product_name else ''
            #       #if line.posologie.name:
            #       posology = str(line.posologie) or ''
            #       #else:
            #       #posology = str(line.posologie.intitule_posologie) if line.posologie.intitule_posologie else ''

            #       #note = str(line.note) if line.note else ''
            #       content += '<tr><td width="100">' + str(line.create_date.strftime('%Y-%m-%d')) + '</td><td width="150">' + product_name + '</td><td width="100">' + product + '</td><td width="50">' + posology + '</td><td width="50">' + str(line.quantity) + '</td><td width="100">' + str(line.medecin_id.name) + '</td></tr>'

            #    content += '</table>'
            #    content += '<tr><td width="100">' + '<b><font color="#3890FF"> Commentaire : </font></b>' + str(appointment.cord_commentaire_pharma) + '</td></tr>'

            #    # check prescription lunettes
            # presc_lunette_lines = self.env['module.prescription.lunette'].search([('appointment_id', '=', appointment.id)])
            # if presc_lunette_lines:
            #    content += '</br>'

            #    content += '<table width="900" border=1>'
            #    content += '<tr style="background-color:#CCCCCC;text-align:center"><td width="900" colspan="10"><b>PRESCRIPTIONS POUR LUNETTES</b></td></tr>'
            #    content += '<tr style="text-align:center"><td width="100"><b>Date</b></td><td width="100"><b>PX</b></td><td width="100"><b>Sphere</b></td><td width="100"><b>Cylindre</b></td><td width="50"><b>Axe</b></td><td width="50"><b>AV</b></td><td width="100"><b>Addition<b/></td><td width="50"><b>AV</b></td><td width="150"><b>Médecin</b></td></tr>'
            #    for line in presc_lunette_lines:
            #        if line.px == 'OD':
            #            oeil = "Oeil droit"
            #        elif line.px == 'OG':
            #            oeil = "Oeil gauche"
            #        else:
            #            oeil = "2 Yeux"
            #        oeil_position = oeil
            #        sphere = line.sphere if line.sphere else ''
            #        cylindre = line.cylindre if line.cylindre else ''
            #        axe = line.axe if line.axe else ''
            #        av1 = line.av1 if line.av1 else ''
            #        av2 = line.av2 if line.av2 else ''
            #        addition = line.addition if line.addition else ''

            #        content += '<tr><td width="100">' + str(line.create_date.strftime('%Y-%m-%d')) + '</td><td width="50">' + oeil_position + '</td><td width="100">' + sphere + '</td><td width="50">' + cylindre + '</td><td width="50">' + axe + '</td><td width="50">' + av1 + '</td><td width="50">' + addition + '</td><td>' + av2 + '</td><td>' + str(line.medecin_id.name) + '</td></tr>'

            #    content += '</table>'
            #    content += '<tr><td width="100">' + '<b><font color="#3890FF"> Commentaire : </font></b>' + str(appointment.cord_commentaire) + '</td></tr>'
        return content

     content = fields.Html(default=get_dossier_content, string="", readonly=True)



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
    
