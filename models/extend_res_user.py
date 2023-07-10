from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.users'

    telegram_client_id = fields.Many2one('telegram.client', string='Telegram Client Account')
