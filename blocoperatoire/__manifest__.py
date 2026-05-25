# -*- coding: utf-8 -*-


{
	'name': "Bloc Opératoire",
	'version': '1.0',
	'summary': """
		Summary
		""",
	'description': """
		Module qui gère le bloc Opératoire
	""",
	'author': "",
	'depends': ['base','account','stock', 'fertility', 'fertility_hospitalisation'],  #,'l10n_syscohada'
	'data': [
		'security/security.xml',
		'security/ir.model.access.csv',
		#'data/data.xml',
		'data/sequence.xml',
		'views/views_blocoperatoire.xml',
        'views/services_blocoperatoire.xml',
	],

	'license': 'LGPL-3',

}
