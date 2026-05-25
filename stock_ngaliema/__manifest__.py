# -*- coding: utf-8 -*-
#############################################################################
#
#
#############################################################################

{
    'name': 'Stock Ngaliema',
    'version': '15.0.1.0.0',
    'summary': "Gestion de stock",
    'description': "Gestion de stock",
    'category': 'Warehouse',
    'author': 'Beni KIALA',
    'maintainer': 'Adamo MABALUKA',
    'company': 'Clinique Ngaliema',
    'depends': [
                'base',
                'stock',
                ],
    'data': [
            #'views/stock_view.xml',
            'security/ir.model.access.csv',
            'wizard/report_move_stock.xml',
            'report/template_move_stock.xml',
            ],
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'auto_install': False,
}
