from odoo import models, fields, api, exceptions


# This module adds few new fields to 'mail.message' model
class TelegramMessage(models.Model):
    _inherit = 'mail.message'

    # Reffer to a field telegram.number in res.partner model viea M2O filed author_id
    #telegram_user_number_id = fields.Char(string='Telegram Number', related='author_id.telegram_number')
    channel_id = fields.Many2one('mail.channel', string='Channel')
    telegram_dialog_id = fields.Char(string='Telegram Dialog', related='channel_id.telegram_dialog_id')
    telegram_message_id = fields.Char(string='Telegram Message ID')
    message_type = fields.Selection([
            ('email', 'Email'),
            ('telegram', 'Telegram'),
            ('comment', 'Comment'),
            ('notification', 'System notification'),
            ('user_notification', 'User Specific Notification')],
            'Type', required=True, default='email',
            help="Message type: email for email message, notification for system "
                "message, comment for other messages such as user replies",
            )

    # Modify create(): 
    # set 'message_type' as 'telegram' for outgoing messages (if channel is telegram)
    #  and call send_telegram_message()   
    @api.model
    def create(self, vals):
        print(vals)
        channel_id = vals.get('res_id')
        channel = self.env['mail.channel'].browse(channel_id)
        print(f'=======INFO(extend_mail_message.py): vals["message_type"] = {vals.get("message_type")}')
        if channel.is_telegram:
            print(f'=======INFO(extend_mail_message.py):channel = {channel.is_telegram}')

            # Check if message_type is 'telegram' then it's incoming from Telegram
            # So regular create() should be start, no need to post this message to Telegram again
            if vals.get("message_type") == 'telegram' or vals.get("message_type") == 'notification':
                print(f'=======INFO(extend_mail_message.py): vals.get("message_type") = telegram. Call regular create method')
                message = super().create(vals)
                print(f'=======INFO(extend_mail_message.py): Create has been called')
                return message

            try:
                print(f'=======INFO(extend_mail_message.py): TRYING TO GET telegram client')
                vals['telegram_dialog_id'] = channel.telegram_dialog_id
                print(f'=======INFO(extend_mail_message.py): vals[telegram_dialog_id] = {vals["telegram_dialog_id"]}')
                telegram_client = self.env['telegram.client']
                telegram_client.send_telegram_message(vals)
                print(f'=======INFO(extend_mail_message.py): IS CALLED - telegram_client.send_telegram_message()')
                message = super().create(vals)
                print(f'=======INFO(extend_mail_message.py): MESSAGE SENT TO TG AND CREATED IN ODOO')
                return message
            
            except Exception as e:
                print(f'Error in send_telegram_message():')
        else:
            print('Hello')
            message = super().create(vals)
            return message

            
            #print(f'=======INFO(extend_mail_message.py): vals["message_type"] = {vals["message_type"]}')

    # @api.constrains('telegram_message_id', 'channel_id')
    # def _check_unique_pair(self):
    #     for record in self:
    #         if record.telegram_message_id and record.channel_id:
    #             domain = [
    #                 ('telegram_message_id', '=', record.telegram_message_id),
    #                 ('channel_id', '=', record.channel_id.id),
    #                 ('id', '!=', record.id)  # Exclude the current record from the domain
    #             ]
    #             duplicate_records = self.search(domain, limit=1)
    #             if duplicate_records:
    #                 raise exceptions.ValidationError(
    #                     "A record with the same Telegram message ID and channel ID already exists."
    #                 )