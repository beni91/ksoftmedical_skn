# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2021-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
{
    'name': "Stock KsoftMedical",
    'version': '15.0.1.0.0',
    'summary': """Stock Picking From Pharmacie/Shop Optique""",
    'description': """Ce module permet de sortir le stock depuis la pharmacie ou le shop optique""",
    'author': "Kongo Soft",
    'company': 'Kongo Soft',
    'category': 'Stock',
    'depends': ['base', 'account', 'stock', 'payment', 'base_accounting_kit'],
    'data': [
            #'views/invoice_stock_move_view.xml',
            'views/pharmacie_stock_move_view.xml', 
            #'views/shop_stock_move_view.xml'
            ],
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
