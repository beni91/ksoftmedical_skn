# -*- coding: utf-8 -*-
#############################################################################
#
#
#############################################################################

{
    'name': 'Rapport Médical',
    'version': '15.0.1.0.0',
    'summary': "Rapports",
    'description': "Les Rapports de tous les service ",
    'category': '',
    'author': 'Adamo MABALUKA',
    'maintainer': 'Adamo MABALUKA',
    'company': '',
    'depends': [
                'ksoftmedical',
                ],
    'data': [
            #'views/stock_view.xml',
            'security/ir.model.access.csv',
			'wizard/rapport_finance_ksoft.xml',
            'wizard/report_move_stock.xml',
            'views/view.xml',
			

            'report/template_move_stock.xml',
            ],
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'auto_install': False,
}
