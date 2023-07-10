from odoo import _, models, fields, api
import asyncio


class ChannelAdd(models.Model):
    _inherit = 'mail.channel'

    telegram_dialog_id = fields.Char(string='Telegram dialog ID')
    is_telegram = fields.Boolean(string='Is a telegram channel')
    channel_type = fields.Selection([
            ('chat', 'Chat'),
            ('telegram', 'Telegram'),
            ('channel', 'Channel'),
            ('group', 'Group')],
            string='Channel Type', required=True, default='channel', readonly=False, help="Chat is private and unique between 2 persons. Group is private among invited persons. Channel can be freely joined (depending on its configuration).")


    # CREATE NEW CHANNEL
    # Adds broadcast in order to update UI and make newly created channel to show up
    @api.model
    def channel_create_broadcast(self, vals):
        group_id = 1
        new_channel = self.create(vals)
        print(f'========= MY INFO: NEW CHANNEL CREATED {new_channel}')
        group = self.env['res.groups'].search([('id', '=', group_id)]) if group_id else None
        new_channel.group_public_id = group.id if group else None
        notification = _('<div class="o_mail_notification">created <a href="#" class="o_channel_redirect" data-oe-id="%s">#%s</a></div>', new_channel.id, new_channel.name)
        new_channel.message_post(body=notification, message_type="notification", subtype_xmlid="mail.mt_comment")
        channel_info = new_channel.channel_info()[0]
        print(f'========= MY INFO: NEW CHANNEL INFO {channel_info}')
        self.env['bus.bus']._sendone(self.env.user.partner_id, 'mail.channel/legacy_insert', channel_info)
        print(f'========= MY INFO: BUS.BUS is OK')
        return new_channel.id


    # ============== CREATE NEW MESSAGE ===================
    @api.model
    def create_new_message(self, telegram_message_id, body):
        # Create via 'mail.channel' 'message_post' method
        channel_id = 39  # Replace with the actual mail channel ID
        #body = 'my tg message 4'
        author_id = 51
        channel = self.env['mail.channel'].browse(channel_id)
        new_message = channel.message_post(
            body=body,
            message_type='telegram',
            author_id=author_id,
            telegram_dialog_id = 123456)
        print(f'=============NEW RECORD CREATED===========')
        return new_message

