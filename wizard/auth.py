from odoo import api, exceptions, fields, models
import logging
import requests


_logger = logging.getLogger(__name__)

class TelegramAuth(models.TransientModel):
    _name = "telegram.auth"
    _description = "Allow to pass Telegram phone and code to authenticate"

    phone_number = fields.Char(string='Phone Number', readonly=True)
    code = fields.Char(string='Code')
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done'), ('connected', 'Connected')], string='State', default='draft')
    api_id = fields.Integer(string='Api ID', readonly=True,)
    api_hash = fields.Char(string='Api Hash', readonly=True,)
    session_name = fields.Char(string='The name of the session file', readonly=True)
    server_url = fields.Char(string='Remote API server', readonly=True)
    phone_hash = fields.Char(string='Telegram Auth Hash', readonly=True)
    username = fields.Char(string='Telegram Username', readonly=True)


    def default_get(self, field_names):
        defaults = super(TelegramAuth, self).default_get(field_names)
        app_id=self.env.context['active_id'] 
        telegram_client = self.env['telegram.client'].search([ ('id', '=', app_id)])
        defaults['phone_number'] = telegram_client.phone_number
        defaults['api_id'] = telegram_client.api_id
        defaults['api_hash'] = telegram_client.api_hash
        defaults['session_name'] = telegram_client.session_name
        defaults['server_url'] = telegram_client.server_url
        return defaults


    # THIS METHOD ALLOW TO REMAIN WIZARD FORM STAY CLOSED AFTER BUTTON CLICK
    # return self._reopen_form() should be used in a method of the button
    def _reopen_form(self):
        self.ensure_one()        
        print(f'************************************')
        return {
        'name': "Paste an SMS or PUSH notification code you've recieved",
        'type': 'ir.actions.act_window',
        'view_type': 'form',
        'view_mode': 'form',
        'res_model': self._name,
        'target': 'new',
        'res_id': self.id,
        'context': self.env.context,
    }

    def get_code(self):
        try:
            self.ensure_one()
            self.state = 'done'
            url = self.server_url + 'sms_code_request' #URL for POST request
            # Sending all Telegram keys in the body of POST request
            params = {
                "session_name": self.session_name,
                "api_id": self.api_id,
                "api_hash": self.api_hash,
                "phone_number": self.phone_number,
                
            }
            print(f'----INFO[get_code(self)]: {url}------{params}')
            headers = {"Content-Type": "application/json"}
            response = requests.post(url, params=params, headers=headers)
            data = response.json()
            print(f'----INFO[get_code(self)]: {data}')
            self.phone_hash = data.get('phone_hash', '')
        except:
            print(f'MORE THEN ONE RECORD SELECTED')
        return self._reopen_form()
    
    
    def send_code(self):
        try:
            self.ensure_one()
            print(f'----INFO[send_code(self)]: {self.phone_hash}')
            url = self.server_url + 'send_code' #URL for POST request
            # Sending all Telegram keys in the body of POST request
            params = {
                "session_name": self.session_name,
                "api_id": self.api_id,
                "api_hash": self.api_hash,
                "phone_number": self.phone_number,
                'sms_code': self.code,
                'phone_hash': self.phone_hash,                
            }

            print(f'----INFO[send_code(self)]: {url}------{params}')
            headers = {"Content-Type": "application/json"}
            response = requests.post(url, params=params, headers=headers)
            data = response.json()
            print(f'----INFO[send_code(self)]: {data}')
            self.phone_hash = data.get('phone_hash', '')
            self.state = 'connected'
            self.username = data.get('username', '')
        except:
            print(f'MORE THEN ONE RECORD SELECTED')
        return self._reopen_form()

