from odoo import api, fields, models
import logging
_logger = logging.getLogger(__name__)

class WizardDossierPatientReception(models.TransientModel):
     _name = 'fertility.wizard.dossier.medical.patient.reception'
     _description = 'Wizard dossier medical patient pour la reception'

     # def get_examen_labo(self, lab_request_id):
       # lab_exams = self.env['fertility.examen.labo'].search([('examen_id', '=', lab_request_id)])
       # content = ""
       # content += '<table width="900" border=1>'
       # content += '<tr style="background-color:#87CEFA;text-align:center"><td width="900" colspan="14"><b>EXAMENS LABO</b></td></tr>'
       # content += '<tr style="background-color:#87CEFA;text-align:center"><td width="100"><b>Date demande</b></td><td width="400"><b>Examen</b></td></tr>'
       # #content += '<tr><td width="900" colspan="4">Cliniques: </br>' + lab_exams.cliniques + '<td></tr>'
       # for lab in lab_exams:
         # analyse_name =  str(lab.analyse.name) if lab.analyse.name else ''
         # exam =  str(lab.examen_text) if lab.examen_text else ''
         # result =  str(lab.description) if lab.description else ''
         # vn = str(lab.valeur_normale) if lab.valeur_normale else ''
         # content += '<tr><td width="100">' + lab.date_request.strftime('%Y-%m-%d') + '</td><td>'+str(lab.examen_text)+ '</td></tr>'
       # content += '</table>'

       # return content

     # def get_examen_imagerie2(self, lab_request_id):
       # lab_exams = self.env['fertility.examen.imagerie2'].search([('examen_id', '=', lab_request_id)])
       # content = ""
       # content += '<table width="900" border=1>'
       # content += '<tr style="background-color:#87CEFA;text-align:center"><td width="900" colspan="14"><b>EXAMENS IMAGERIE</b></td></tr>'
       # content += '<tr style="background-color:#87CEFA;text-align:center"><td width="100"><b>Date demande</b></td><td width="400"><b>Examen</b></td></tr>'
       # #content += '<tr><td width="900" colspan="4">Cliniques: </br>' + lab_exams.cliniques + '<td></tr>'
       # for lab in lab_exams:
         # #analyse_name =  str(lab.analyse.name) if lab.analyse.name else ''
         # #exam =  str(lab.examen_text) if lab.examen_text else ''
         # #result =  str(lab.description) if lab.description else ''
         # #vn = str(lab.valeur_normale) if lab.valeur_normale else ''
         # content += '<tr><td width="100">' + lab.date_request.strftime('%Y-%m-%d') + '</td><td>'+str(lab.examen_text)+ '</td></tr>'
       # content += '</table>'
       # return content

     # def get_examen_imagerie(self, lab_request_id):
         # lab_exams = self.env['fertility.examen.imagerie'].search([('examen_id', '=', lab_request_id)])
         # print(lab_exams)

         # content = ""
         # content += '<table width="900" border=1>'
         # content += '<tr style="background-color:#87CEFA;text-align:center"><td width="900" colspan="14"><b>TESTS COMPLEMENTAIRES</b></td></tr>'
         # content += '<tr style="background-color:#87CEFA;text-align:center"><td width="100"><b>Date demande</b></td><td width="150"><b>Analyse</b></td><td width="200"><b>Clinique</b></td><td width="450"><b>Protocole</b></td><td width="100"><b>Demandeur</b></td></tr>'

         # for lab in lab_exams:
            # clinique = str(lab.clinique) if lab.clinique else ''
            # protocol = str(lab.protocol) if lab.protocol else ''
            # analyse = str(lab.analyse.name) if lab.analyse.name else ''

            # content += '<tr><td width="100">' + lab.date_request.strftime('%Y-%m-%d') + '</td><td>' + analyse + '</td><td>' + clinique + '</td><td>' + protocol + '</td><td>' + str(lab.demandeur.name) + '</td></tr>'
         # content += '</table>'

         # return content

     # def get_dossier_content(self):
        # # context = self.env.context
        # # return '<h1>'+  str(context.get('patient_id')) + '</p>'
        # # load patient consultation

        # patient_id = self._context.get('active_id')
        # print("ID du Patient RECEPTION", patient_id)

        # appointments = self.env['fertility.appointment'].search([('patient_id','=',patient_id)])

        # content = ""
        # content += '<table width="900" border=0>'
        # content += '<tr><td width="900"><b><h1 style="text-align:center">HISTORIQUE DU PATIENT<h1></b></td></tr>'
        # content += '</table>'
        # for appointment in appointments:
            # content += '<br/>'
            # content += '<table width="900" border=0>'
            # content += '<tr><td width="900" style="text-align:center"><b>-------------------------------------------------------------------------------------------------------------------------------------------------------------------</b></td></tr>'
            # content += '<tr><td width="900" style="text-align:center"><b><font color="#3890FF">#############################################################################################</font></b></td></tr>'
            # content += '<tr><td width="900" style="text-align:center"><b>------------------------------------------------------------------------------------------------------------------------------------------------------------------</b></td></tr>'
            # content += '</table>'
            # content += '</br>'
            # content += '<table width="900" border=1>'
            # content += '<tr><td width="200"><b>Date et Heure</b></td><td width="600" style="text-align:center">' + appointment.date.strftime('%Y-%m-%d') + '</td></tr>'
            # content += '<tr><td width="200"><b>Consultation</b></td><td width="600" style="text-align:center">' + str(appointment.product_id.name) + '</td></tr>'
            # content += '<tr><td width="200" ><b>Docteur</b></td><td width="600" style="text-align:center">' + str(appointment.doctor_id.name) + '</td></tr>'
            # content += '<tr><td width="200" ><b>Motif</b></td><td width="600" style="text-align:center">' + str(appointment.motif_rdv) + '</td></tr>'
            # content += '</table>'

            # # add vital sign
            # content += '</br>'
            # systolic =  str(appointment.systolic) if appointment.systolic else ''
            # bmp =  float(appointment.bmi) if appointment.bmi else ''
            # etat = ""
            # if appointment.bmi_state == "sp":
                # etat = "SousPoids"
            # elif appointment.bmi_state  == "normal" :
                # etat = "Normal"
            # elif appointment.bmi_state == "srp":
                # etat = "Surpoids"
            # elif appointment.bmi_state == "obez1" :
                # etat = "Obèsité modérée"
            # elif appointment.bmi_state == "obez2" :
                # etat = "Obèsité sévère"
            # else:
                # etat = "Obèsité morbide"


            # content += '<table width="900" border=1>'
            # content += '<tr style="background-color:#87CEFA;text-align:center"><th width="900" colspan="14"><b>ACUITE VISUELLE (AV)</b></th></tr>'
            # #content += '<tr style="background-color:#87CEFA;text-align:center"><td><b>T°</b></td><td><b>P.<b/></td><td><b>Taille</b></td><td><b>IMC</b></td><td><b>TA</b></td><td><b>Fc</b></td><td><b>FR</b></td><td><b>Glycémie<b/></td><td><b>Sat. en Oxygène</b></td><td><b>P. Crânien</b></td><td><b>P. Brachial</b></td><td><b>P. Abdominal</b></td><td><b>P. Pelvien</b></td></tr>'
            # #content += '<tr style="background-color:#87CEFA;text-align:center"><td><b>TA</b></td><td><b>Fc</b></td><td><b>FR</b></td><td><b>Glycémie<b/></td><td><b>Sat. en Oxygène</b></td>'
            # content += '<tr style="background-color:#87CEFA;text-align:center"><th colspan="3"><b>Oeil droit<b/></td><th colspan="3"><b>Oeil gauche</b></th></tr>'
            # content += '<tr style="background-color:#87CEFA;text-align:center"><td><b>S.C.</b></td><td><b>C.C.</b></td><td><b>T.S.</b></td><td><b>S.C.<b/></td><td><b>C.C.</b></td><td><b>T.S.</b></td></tr>'

            # #if appointment.is_alert == False:
            # #content += '<tr style="text-align:center"><td>' + str(appointment.ta) + '</td><td>' + str(appointment.fc) +'</td><td>' + str(appointment.fr) + '</td><td>' + str(appointment.glyc) + '</td><td>' + str(appointment.so) + '</td></tr>'
            # content += '<tr style="text-align:center"><td>' + str(appointment.od_sc) + '</td><td>' + str(appointment.od_cc) +'</td><td>' + str(appointment.od_ts) + '</td><td>' + str(appointment.os_sc) + '</td><td>' + str(appointment.os_cc) + '</td><td>' + str(appointment.os_ts) + '</td></tr>'
           # # if appointment.is_alert == True:
           # #     content += '<tr style="color:#FF5733;text-align:center"><td style="color:#FF5733;">'+ str(appointment.temp) + '</td><td>'+ str(appointment.weight) + '</td><td>'+ str(appointment.height) + '</td><td>'+ str(bmp) + '</br>Etat : '+ str(etat)+'</td><td>'+ systolic + '</td><td>'+ str(appointment.bpm) + '</td><td>'+ str(appointment.respiratory_rate) + '</td><td>'+ str(appointment.glycemia) + '</td><td>'+ str(appointment.osat) + '</td><td>'+ str(appointment.pc) + '</td><td>'+ str(appointment.pb) + '</td><td>'+ str(appointment.abdominal_circ) + '</td><td>'+ str(appointment.hip) + '</td></tr>'
            # content += '</table>'

            # content += '</br>'
            # content += '<table width="900" border=1>'
            # content += '<tr style="background-color:#87CEFA;text-align:center"><th width="900" colspan="14"><b>PRESSION INTRA-OCULAIRE</b></th></tr>'
            # content += '<tr style="background-color:#87CEFA;text-align:center"><th colspan="2"><b>Max<b/></td><th colspan="2"><b>Avant</b></th><th colspan="2"><b>Après</b></th></tr>'
            # content += '<tr style="background-color:#87CEFA;text-align:center"><th><b>OD<b/></td><th><b>OS</b></th><th><b>OD</b></th><th><b>OS</b></th><th><b>OD</b></th><th><b>OS</b></th></tr>'
            # content += '<tr style="text-align:center"><td>' + str(appointment.od_pio_max) + '</td><td>' + str(appointment.os_pio_max) +'</td><td>' + str(appointment.od_pression) + '</td><td>' + str(appointment.os_pression) + '</td><td>' + str(appointment.od_pression_apres) + '</td><td>' + str(appointment.os_pression_apres) + '</td></tr>'
            # content += '</table>'

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
                # og_gon = "1/4"
            # elif appointment.gonioscopie_og == '2':
                # og_gon = "2/4"
            # elif appointment.gonioscopie_og == '3':
                # og_gon = "3/4"
            # elif appointment.gonioscopie_og == '4':
                # og_gon = "4/4"

            # if appointment.gonioscopie_od == '1':
                # od_gon = "1/4"
            # elif appointment.gonioscopie_od == '2':
                # od_gon = "2/4"
            # elif appointment.gonioscopie_od == '3':
                # od_gon = "3/4"
            # elif appointment.gonioscopie_od == '4':
                # od_gon = "4/4"

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
            # content += '<table width="900" border=1>'

            # #content += '<tr style="background-color:#87CEFA;text-align:center"><td width="900" colspan="2"><b>ANAMNESE</b></td></tr>'
            # #if appointment.anamnese:
            # #    content += '<tr><td width="200" ><b>Anamnèse</b></td><td>' + str(appointment.anamnese) + '</td></tr>'
            # #if douleur_pelvienne:
            # #    content += '<tr><td width="200"><b>Douleurs pelviennes</b></td><td>' + douleur_pelvienne + '</td></tr>'
            # #if dysmnonrhee:
            # #    content += '<tr><td width="200" ><b>Dysménorrhée<b/></td><td>' + dysmnonrhee +  '</td></tr>'
            # #if dyspareunie:
            # #    content += '<tr><td width="200" ><b>Dyspareunie</b></td><td>' + dyspareunie +  '</td></tr>'
            # #if menometrorragie:
            # #    content += '<tr><td width="200" ><b>Ménométrorragie</b></td><td>' + menometrorragie +  '</td></tr>'
            # #if duree_regle:
            # #    content += '<tr><td width="200" ><b>Durée des règles</b></td><td>' + duree_regle + '</td></tr>'
            # #if durree_cycle:
            # #    content += '<tr><td width="200"><b>Durée des cycles</b></td><td>' + durree_cycle + '</td></tr>'
            # #if appointment.physique:
            # #    content += '<tr><td width="200" ><b>Examen Physique</b></td><td>' + str(appointment.physique) + '</td></tr>'
            # #content += '</table>'

            # if appointment.diagnostics_ids:
                # content += '</br>'
                # # content += '<table><tr><td><h3><b>Diagnostics</b></h3></td></tr></table>'
                # content += '<table width="900" border=1>'
                # content += '<tr style="background-color:#87CEFA;text-align:center"><td width="900" colspan="7"><b>DIAGNOSTICS</b></td></tr>'
                # content += '<tr style="background-color:#87CEFA;text-align:center"><td><b>Date</b></td><td><b>Pathologie</b></td><td><b>Observation</b></td><td><b>Médecin<b/></td></tr>'

                # for diagnostic in appointment.diagnostics_ids:
                    # description = str(diagnostic.description) if diagnostic.description else ''
                    # explication = str(diagnostic.explication) if diagnostic.explication else ''
                    # origin = ''
                    # if diagnostic.origine == 'homme':
                        # origin = 'Masculine'
                    # elif diagnostic.origine == 'femme':
                        # origin = 'Feminine'
                    # elif diagnostic.origine == 'mixte':
                        # origin = 'Mixte'

                    # status = ''
                    # if diagnostic.internal_status == 'hypo':
                        # status = 'Hypothèse'
                    # elif diagnostic.internal_status == 'def':
                        # status = 'Définitive'

                    # content += '<tr ><td width="100">' + str(
                        # diagnostic.date_diagnostic.strftime('%Y-%m-%d')) + '</td><td width="150">' + str(
                        # diagnostic.pathologie.name) + '</td><td>' + explication + '</td><td>' + str(
                        # diagnostic.medecin_diag.name) + '</td></tr>'

                # content += '</table>'
            # #content += '<tr><td width="100">' + '<b><font color="#3890FF"> Commentaire : </font></b>' + str(appointment.commentaire) + '</td></tr>'

            # if appointment.consult_examen_id:
               # if self.get_examen_labo(appointment.consult_examen_id.id):
                   # content += '</br>'
                   # content += self.get_examen_labo(appointment.consult_examen_id.id)

               # if self.get_examen_imagerie2(appointment.consult_examen_id.id):
                   # content += '</br>'
                   # content += self.get_examen_imagerie2(appointment.consult_examen_id.id)

               # if self.get_examen_imagerie(appointment.consult_examen_id.id):
                   # content += '</br>'
                   # content += self.get_examen_imagerie(appointment.consult_examen_id.id)
                                        # ##Traitement
            # if appointment.done_orientation:
                # content += '</br>'
                # # content += '<table><tr><td><h3><b>Diagnostics</b></h3></td></tr></table>'
                # content += '<table width="900" border=1>'
                # content += '<tr style="background-color:#87CEFA;text-align:center"><td width="900" colspan="7"><b>TRAITEMENTS</b></td></tr>'
                # content += '<tr style="background-color:#87CEFA;text-align:center"><td width="100"><b>Date</b></td><td width="225"><b>Actes</b></td><td width="225"><b>Protocol</b></td><td width="225"><b>Orientation</b></td><td width="150"><b>Médecin</b></td></tr>'

                # for diagnostic in appointment.done_orientation:
                    # content += '<tr ><td width="100">' + str(diagnostic.date_orientation.strftime('%Y-%m-%d')) + '</td><td width="150">' + str(diagnostic.product.name) + '</td><td width="100">' + str(diagnostic.protocole) + '</td><td width="100">' + str(diagnostic.orientation) + '</td><td>' + str(diagnostic.medecin_.name) + '</td></tr>'
                # content += '</table>'

            # # check ordonance
            # ordonance_lines = self.env['module.ordonnance.line'].search([('appointment_id', '=', appointment.id)])
            # if ordonance_lines:
               # content += '</br>'

               # content += '<table width="900" border=1>'
               # content += '<tr style="background-color:#87CEFA;text-align:center"><td width="900" colspan="7"><b>PRESCRIPTIONS MEDICALES</b></td></tr>'
               # content += '<tr style="background-color:#87CEFA;text-align:center"><td width="100"><b>Date</b></td><td width="250"><b>Produit</b></td><td width="150"><b>Autres Produit</b></td><td width="200"><b>Posologie</b></td><td width="50"><b>Qtité</b></td><td width="100"><b>Médecin</b></td></tr>'

               # for line in ordonance_lines:
                  # product_name = str(line.product.name) if line.product.name else ''
                  # product = str(line.product_name) if line.product_name else ''
                  # #if line.posologie.name:
                  # posology = str(line.posologie) or ""
                  # #else:
                  # #posology = str(line.posologie.intitule_posologie) if line.posologie.intitule_posologie else ''

                  # #note = str(line.note) if line.note else ''

                  # content += '<tr><td width="100">' + str(line.create_date.strftime('%Y-%m-%d')) + '</td><td width="150">' + product_name + '</td><td width="100">' + product + '</td><td width="50">' + posology + '</td><td width="50">' + str(line.quantity) + '</td><td width="100">' + str(line.medecin_id.name) + '</td></tr>'

               # content += '</table>'
               # content += '<tr><td width="100">' + '<b><font color="#3890FF"> Commentaire : </font></b>' + str(appointment.cord_commentaire_pharma) + '</td></tr>'

               # # check prescription lunettes
            # presc_lunette_lines = self.env['module.prescription.lunette'].search([('appointment_id', '=', appointment.id)])
            # if presc_lunette_lines:
               # content += '</br>'

               # content += '<table width="900" border=1>'
               # content += '<tr style="background-color:#87CEFA;text-align:center"><td width="900" colspan="10"><b>PRESCRIPTIONS POUR LUNETTES</b></td></tr>'
               # content += '<tr style="background-color:#87CEFA;text-align:center"><td width="100"><b>Date</b></td><td width="100"><b>PX</b></td><td width="100"><b>Sphere</b></td><td width="100"><b>Cylindre</b></td><td width="50"><b>Axe</b></td><td width="50"><b>AV</b></td><td width="100"><b>Addition<b/></td><td width="50"><b>AV</b></td><td width="150"><b>Médecin</b></td></tr>'
               # for line in presc_lunette_lines:
                   # if line.px == 'OD':
                       # oeil = "Oeil droit"
                   # elif line.px == 'OG':
                       # oeil = "Oeil gauche"
                   # else:
                       # oeil = "2 Yeux"
                   # oeil_position = oeil
                   # sphere = line.sphere if line.sphere else ''
                   # cylindre = line.cylindre if line.cylindre else ''
                   # axe = line.axe if line.axe else ''
                   # av1 = line.av1 if line.av1 else ''
                   # av2 = line.av2 if line.av2 else ''
                   # addition = line.addition if line.addition else ''

                   # content += '<tr><td width="100">' + str(line.create_date.strftime('%Y-%m-%d')) + '</td><td width="50">' + oeil_position + '</td><td width="100">' + sphere + '</td><td width="50">' + cylindre + '</td><td width="50">' + axe + '</td><td width="50">' + av1 + '</td><td width="50">' + addition + '</td><td>' + av2 + '</td><td>' + str(line.medecin_id.name) + '</td></tr>'

               # content += '</table>'
               # content += '<tr><td width="100">' + '<b><font color="#3890FF"> Commentaire : </font></b>' + str(appointment.cord_commentaire) + '</td></tr>'
        # return content
        
     def get_examen_labo(self, lab_request_id):
       lab_exams = self.env['fertility.examen.labo'].search([('examen_id', '=', lab_request_id)])
       content = "" 
       
       content += '<div style="float:left; width:49%;margin-top:5px;margin-bottom:5px;">'
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
       
       
     def get_diagnostic(self, appointment_id):
       diagnostic_ids = self.env['module.diagnostics'].search([('appointment_id', '=', appointment_id)])
       content = "" 
       
       content += '<div>'
       content += '<table width="100%" border="1">'
       content += '<tr><th colspan="5" style="background-color:#CCCCCC;text-align:center"><b>DIAGNOSTICS</b></th></tr>'
       
       content += '<tr style="text-align:center"><th width="15"><b>Date<b/></th><th width="20"><b>Pathologie</b></th><th width="20"><b>Observation</b></th></tr>'
       for diag in diagnostic_ids:
         diagn_name =observ= ""
         diagn_name =  str(diag.pathologie.name)
         observ =  str(diag.description) 
         content += '<tr><td>' + diag.date_diagnostic.strftime('%Y-%m-%d') + '</td><td>'+diagn_name + '</td><td><b>'+observ + '</b></td></tr>'
      
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
         #vn = str(lab.valeur_normale) if lab.valeur_normale else ''
         content += '<tr><td width="100">' + lab.date_request.strftime('%Y-%m-%d') + '</td><td>'+str(lab.examen_text)+ '</td></tr>'
       content += '</table>'

       return content
    
     def get_pharmacie(self, lab_request_id):
         lab_exams = self.env['module.ordonnance.line'].search([('appointment_id', '=', lab_request_id)])
         print(lab_exams)

         content = ""
         content += '</br>'
         content += '<div style="float:right; width:49%;margin-top:5px;margin-bottom:5px;">'
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
         content += '<div style="float:right; width:49%;margin-top:5px;margin-bottom:5px;">'
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
        brw_id = self.env['fertility.patient'].browse(int(active_id))
        #patient_id = brw_id.patient_id.id
        patient_id = self.patient_id.id
        #patient_id = self.env.context.get('patient_id')
        #patient_id = 33
        #print("ID du Patient",patient_id)

        appointments = self.env['fertility.appointment'].search([('patient_id','=',brw_id.id)])
       
        content = ""
        content += '<table width="900" border=0>'
        content += '<tr><td width="900"><b><h3 style="text-align:center">ANTECEDANT ET ALLERGIE DU PATIENT<h3></b></td></tr>'
        content += '</table>'
        

        
        #content += '<div style="margin-bottom:2px;height:150px !important; padding:10px; border: 0px solid gray;">'+ str(appointments) +'</div>'
        # content += '<table width="49%" border="1" style="float:left; width:49%">'
        # content += '<tr><td width="200"><b>Patient</b></td><td width="600">' + str(brw_id.patient_id.partner_id.display_name) + '</td></tr>'
        # content += '<tr><td width="200"><b>Sexe</b></td><td width="600">' + str(brw_id.patient_id.gender) + '</td></tr>'
        # content += '<tr><td width="200"><b>Date Naiss.</b></td><td width="600">' + brw_id.patient_id.birth.strftime('%d-%m-%Y') + '</td></tr>'
        # content += '<tr><td width="200"><b>Tél.</b></td><td width="600">' + str(brw_id.patient_id.partner_id.phone) + '</td></tr>'
        # content += '<tr><td width="200"><b>Adresse</b></td><td width="600">' + str(brw_id.patient_id.partner_id.street) + '</td></tr>'
        # content += '<tr><td width="200"><b>Profession</b></td><td width="600">' + str(brw_id.patient_id.partner_id.function) + '</td></tr>'
        # content += '</table>'
           

        # content += '<table width="49%" border="1"style="float:right; width:49%">'
        # content += '<tr><td width="200"><b>Catégorie</b></td><td width="600">' + str(brw_id.patient_id.categorie) + '</td></tr>'
        # content += '<tr><td width="200"><b>Convention</b></td><td width="600">' + str(brw_id.patient_id.parent_id.display_name) + '</td></tr>'

        # content += '</table>'
        # content += '</div>'
      

        content += '</br>'
        content += '<table width="900" border=0>'
        content += '<tr><td width="900"><b><h3 style="text-align:center">HISTORIQUE DES CONSULTATIONS<h3></b></td></tr>'
        content += '</table>'
        for appointment in appointments:

            content += '<table width="900" border=0>'
            #content += '<tr><td width="900" style="text-align:center"><b>---------------------------------------------------------------------------------------------------------------------</b></td></tr>'
            content += '<tr><td width="900" style="text-align:center"><b><font color="#3890FF">############################################################################</font></b></td></tr>'
            #content += '<tr><td width="900" style="text-align:center"><b>----------------------------------------------------------------------------------------------------------------</b></td></tr>'
            content += '</table>'
            content += '</br>'
            content += '<center><table width="900" border=1 class="center">'
            content += '<tr><td width="150"><b>Date et Heure</b></td><td width="300" style="text-align:center">' + appointment.date.strftime('%Y-%m-%d') + '</td>'
            content += '<td width="150"><b>Docteur</b></td><td width="300" style="text-align:center">' + str(appointment.doctor_id.name) + '</td></tr>'
            content += '<tr><td width="150" ><b>Consultation</b></td><td width="300" style="text-align:center">' + str(appointment.product_id.name) + '</td>'
            content += '<td width="150" ><b>Motif</b></td><td width="300" style="text-align:center">' + str(appointment.motif_rdv) + '</td></tr>'
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

              
            
            if appointment.done_feuille_signes_vitaux:
                content += self.get_signes_vitaux(appointment.id)
   
            if appointment.anamnese or appointment.examen_physique:
                content += '<div>'
                content += '<table width="100%" border=1>'
                content += '<tr style="background-color:#CCCCCC;text-align:center"><th colspan="2"><b>CONSULTATIONS</b></th></tr>'
                if appointment.anamnese or appointment.examen_physique:
                    content += '<tr style="text-align:left;"><td style="width:50%;text-align:left;"><b>Anamnèse:<b/></br><p>'+ str(appointment.anamnese) +'</p></td>'
                
              
                    content += '<td style="width:50%;text-align:left;"><b>Examen Physique:<b/></br><p>'+ str(appointment.examen_physique) +'</p></td><tr>'
                content += '</table>'
                content += '</div>'
                content += '</br>'
                
            if appointment.diagnostics_ids:
                content += self.get_diagnostic(appointment.id)


            if appointment.labo_ids:
                content += self.get_examen_labo(appointment.id)
           
                
            if appointment.imagerie_ids:
                content += self.get_examen_imagerie(appointment.id)
                
            if appointment.done_ordonnance:
                content += self.get_pharmacie(appointment.id)
                
        self.write({'content':content})
        #return 


     content = fields.Html(string="Resumé", readonly=True)
     nbre_ligne = fields.Integer(string="Nbre de ligne", default=5)
     service = fields.Many2one('product.template', domain="[('is_consultation','=',True)]", string="Consultations")  
     medecin = fields.Many2one('fertility.doctor', string="Médecin")
     speciality = fields.Many2one('fertility.doctor.speciality', string="Spécialité")
     patient_id = fields.Many2one('fertility.patient', string="Patient")
     see_resume = fields.Boolean(string="Actualiser le dossier")
     
     

