# -*- coding: utf-8 -*-

{
	'name': "KsoftMedical",
	'version': '1.0',
	'summary': """
		HealthCare
		""",
	'description': """
		Module de gestion médicale
	""",
	'author': "Kongo Soft",
	'depends': ['base','account','stock', 'prevelement_frais_informatique'],  #,'l10n_syscohada'
	'data': [
		'security/fertility_security.xml',
		'security/ir.model.access.csv',
		'data/data.xml',
		'data/sequence.xml',
		'data/cron.xml',
		'wizard/AnnulRdv.xml',
		'wizard/Next_RDV.xml',
		'wizard/wizard_dossier_patient.xml',
		'wizard/wizard_dossier_patient_reception.xml',
		'wizard/wizard_transfert_patient.xml',
		#'wizard/wizard_consultation.xml',
		'wizard/wizard_appointment_reporting.xml',
		'views/doctor.xml',
        'views/account.xml',
        'views/transfert_patient.xml',
		'views/patient.xml',
		'views/consultation.xml',
        
		
		#'views/res_partner.xml',
		'views/triage.xml',
		#'views/pma.xml',
		'views/product.xml',
		'views/config.xml',
		'views/appointment.xml',
		'views/dossier_patient.xml',
		
		#'views/account_generate_code.xml',
		'views/labo.xml',
		'views/imagerie.xml',
		'views/pharmacie.xml',
        'views/stock_views.xml',
		'views/shop_optique.xml',
        'views/res_partner.xml',
        'views/rapport_medical.xml',
        
		'report/template_laboratoire_views.xml',
        'report/template_imagerie_views.xml',
        'report/template_imagerie2_views.xml',
        'report/template_orientation_views.xml',
        'report/template_pharmacie_views.xml',
        'report/appointment_report_views.xml',
        'report/template_protocoleimag_views.xml',
        'report/template_resultat_labo_views.xml',
        'report/template_lunettes_views.xml',
        'report/rapport_caisse_ksoft.xml',
        'report/template_rapport_caisse_views.xml',
		'report/report_consultation.xml',
        'views/views_menu.xml',
	],

	'license': 'LGPL-3',

}
