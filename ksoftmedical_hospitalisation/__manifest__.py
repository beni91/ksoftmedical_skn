# -*- coding: utf-8 -*-


{
	'name': "KsoftMedical Hospitalisation",
	'version': '1.0',
	'summary': """
		HealthCare
		""",
	'description': """
		Module Hospitalisation
	""",
	'author': "Kongo Soft",
	'depends': ['base', 'account', 'ksoftmedical', 'stock'],
	'data': [
		'security/fertility_hospitalisation_security.xml',
		'security/ir.model.access.csv',
		'data/data.xml',
        'data/sequence.xml',
		'views/views.xml',
        'wizard/wizard_views.xml',
		'wizard/transfert_patient_hospi_wizard.xml',
		'views/hospitalisation.xml',
        'views/salle_attente.xml',
		#'views/bloc_opreatoire.xml',
		'views/config.xml',

	],

	'license': 'LGPL-3',

}
