# -*- coding: utf-8 -*-
{
    'name': "my_module",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'project'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',    
        'views/listing.xml',    
        'views/my_module_index_template.xml',
        'views/my_module_local_template.xml',
        'views/my_module_my_files.xml',  
        'views/my_module_detail_template.xml',  

        ],
    
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}