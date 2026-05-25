# -*- coding: utf-8 -*-

{
	"name" : "Prelevement de frais informatique",
	"version" : "13.0",
	"category" : "",
	'summary': 'Collecte de frais informatique',
	"description": """
	Collecte de frais informatique	
	""",
	'author': "Adamo",
    'website': "",
    'version': '15.0.0.0',
	'license': 'LGPL-3',
	'category': 'Accounting/Accounting',

	# any module necessary for this one to work correctly
	'depends': ['base', 'l10n_syscohada'],
	"data": [
		'security/ir.model.access.csv',
		'views/res_config_settings_views.xml',
		'views/categorie_article.xml',
		'views/account_move.xml',
		'views/sequence.xml',
		'views/frais_informatique.xml',
	],

    'installable': True,

}
