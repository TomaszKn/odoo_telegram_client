from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    telegram_number = fields.Char(string='Telegram Number')
    telegram_username = fields.Char(string='Telegram Username')
    telegram_id = fields.Char(string='Telegram Id')

