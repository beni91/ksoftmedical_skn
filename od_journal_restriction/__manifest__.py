# -*- coding: utf-8 -*-

{
    'name': 'Odoo Journal Restriction For Users',
    'version': '14.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Journal Restriction For Users Odoo 14',
    'description': 'Journal Security, Journal Restricted Users, Access journal restriction By users, '
                   'User Journal Restriction, Journal Restriction For Users Odoo 14, User Journal Restriction, Journal Sequence,'
                   'Configure journals by users, journal allowed users, Journals by users, allowed journal for users,'
                   'journal restriction, odoo journal restriction, journal entry restriction, Journal Security In Odoo',
    'sequence': '1',
    'author': 'Odoo Developers',
    'support': 'developersodoo@gmail.com',
    'live_test_url': 'https://www.youtube.com/watch?v=p3jnxqkWtXQ',
    'depends': ['account','ksoftmedical'],
    'demo': [],
    'data': [
        'views/account_journal.xml',
        'views/res_users.xml',
    ],
    'qweb': [],
    'license': 'OPL-1',
    'price': 13,
    'currency': 'USD',
    'installable': True,
    'application': False,
    'auto_install': False,
    'images': ['static/description/banner.gif'],
}
