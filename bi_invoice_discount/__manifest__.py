
################################################################################
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
################################################################################
{
    'name': 'Invoice and Vendor Bills Discount',
    'version': '15.0.0.1',
    'category': 'Invoicing',
    'summary': 'Sale invoices discount sales discount vendor bill discount purchase invoice discount percentage based discount fixed discount on invoice line customer invoice discount customer discount vendor discount on purchase vendor bill discount All in one Discount',
    'description': """
                This odoo app helps user to apply discount on customer invoice and vendor bill with two type of fix discount and percent discount and this discount will also printed on invoice and bill report, this will also generate journal entry for discount account.
                """,
    'author': 'BrowseInfo',
    'website': 'https://www.browseinfo.in',
    'price': 15,
    'currency': "EUR",
    'depends': ['sale_management', 'purchase', 'account'],
    'data': [
            'security/ir.model.access.csv',
            'views/discount_type_view.xml',
            'views/account_move_view.xml',
            'reports/inherit_account_report.xml',

    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'live_test_url':'https://youtu.be/9oUGuCks0sE',
    "images":['static/description/Banner.png'],
    'license': 'OPL-1',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
