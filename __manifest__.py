{
    'name': 'Pedimento Tracking',
    'version': '18.0.1.0.0',
    'category': 'Inventory',
    'summary': 'Track Customs Pedimento Number from Purchase to Stock',
    'author': 'ALPHAQUEB CONSULTING',
    'website': 'https://alphaqueb.com',
    'company': 'ALPHAQUEB CONSULTING S.A.S.',
    'maintainer': 'ANTONIO QUEB',
    'depends': ['purchase', 'stock'],
    'data': [
        'views/stock_picking_views.xml',
        'views/stock_quant_views.xml',
        'views/stock_move_line_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
