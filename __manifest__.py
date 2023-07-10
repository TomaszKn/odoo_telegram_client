# -*- coding: utf-8 -*-
{
    'name': "Telegram Client",

    'summary': """
        This module provides a Telegram client experience in the Odoo Discuss module.""",

    'description': """
        Long description of module's purpose
    """,

    'author': "erlit007@gmail.com",
    'website': "",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'mail'],
    'external_dependencies': {'python': ['requests',],},
                              
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/tree_telegram_channel.xml',
        'views/form_telegram_channel.xml',
        'views/partner_view_extension.xml',
        'views/views.xml',
        'views/tree_telegram_client.xml',
        'views/form_telegram_client.xml',
        'views/extend_res_users_form.xml',
        'views/extend_mail_message_form.xml',
        'wizard/form_auth_wizard.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
    'license': 'AGPL-3',
    'application': True,
}
