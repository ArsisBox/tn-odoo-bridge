{
    'name': 'Tiendanube Odoo Bridge',
    'version': '18.0.1.0.0',
    'summary': 'Conector entre Tiendanube y Odoo',
    'author': 'ArsisBox',
    'website': 'https://github.com/ArsisBox/tn-odoo-bridge',
    'category': 'Connector',
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/tiendanube_config_views.xml',
        'views/menus.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}