from odoo import models, fields, api, exceptions
from odoo.exceptions import UserError


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
        try:
            if vals.get('model') != 'mail.channel':
                message = super().create(vals)
                return message
                
            print(vals)
            channel_id = vals.get('res_id')
            print(f'=======INFO 1 (extend_mail_message.py): channel_id = {channel_id}')
            channel = self.env['mail.channel'].browse(channel_id)
            print(f'=======INFO 2 (extend_mail_message.py): channel = {channel}')
            print(f'=======INFO 3 (extend_mail_message.py): vals["message_type"] = {vals.get("message_type")}')
            print(f'=======INFO 3.1 (extend_mail_message.py): channel.is_telegram = {channel.is_telegram}')
            if channel.is_telegram and vals.get("message_type") == 'comment':
                print(f'=======INFO 4 (extend_mail_message.py):channel = {channel.is_telegram}')
                try:
                    print(f'=======INFO 7 (extend_mail_message.py): TRYING TO GET telegram client')
                    vals['telegram_dialog_id'] = channel.telegram_dialog_id
                    print(f'=======INFO 8 (extend_mail_message.py): vals[telegram_dialog_id] = {vals["telegram_dialog_id"]}')
                    telegram_client = self.env['telegram.client']
                    send_result = telegram_client.send_telegram_message(vals)
                    print(f'=======INFO 8.1   {send_result}')
                    if not send_result.get('telegram_api'):
                        text_message = vals.get('body')
                        vals['body'] = 'PROBLEM: this massage was not send to a person. You need to log in intro Telegram first. ' + 'Your message: ' + '"' + text_message + '"'
                        message = super().create(vals)
                        return message

                    else:
                        print(f'=======INFO 9 (extend_mail_message.py): IS CALLED - telegram_client.send_telegram_message()')
                        message = super().create(vals)
                        print(f'=======INFO 10 (extend_mail_message.py): MESSAGE SENT TO TG AND CREATED IN ODOO')
                        return message
                
                except Exception as e:
                    print(f'Error in send_telegram_message():')
            else:
                print('Channel is not a Telegram')
                message = super().create(vals)
                return message
           
        except Exception as e:
            message = super().create(vals)
            return message





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