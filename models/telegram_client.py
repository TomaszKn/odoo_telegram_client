from odoo import models, fields, api, exceptions
from odoo.exceptions import UserError
import logging
import requests



# For logging
logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s', level=logging.WARNING)

class telegram_client(models.Model):
    _name = 'telegram.client'
    _description = 'telegram client'

    name = fields.Char(string='Telegram account name')
    api_id = fields.Integer(string='Api ID', required=True)
    api_hash = fields.Char(string='Api Hash', required=True)
    phone_number = fields.Char(string='Telegram Phone Number', required=True)
    session_name = fields.Char(string='The name of the session file', required=True, readonly=True, default='telegram1')
    username = fields.Char(string='The Telegram Username', readonly=True)
    users = fields.One2many('res.users', 'telegram_client_id', string='Associated Partners', required=True)
    server_url = fields.Char(string='Remote API server', required=True)
    auth_status = fields.Boolean(string='Auth status')



    # GET AUTH STATUS
    def check_tg_auth(self):
        try:
            url = self.server_url + 'check_auth'
            payload = {
                "api_id": self.api_id,
                "api_hash": self.api_hash,
                "phone_number": self.phone_number,
                "session_name": self.session_name,
                "message_text": 'blank',
                "recipient": 123
            }
            headers = {"Content-Type": "application/json"}
            response = requests.post(url, json=payload, headers=headers)
            data = response.json()
            print(f'----------{data}----------')
            if data.get('auth_status'):
                status = True
                print(f'-----1---{status}')
            else:
                status = False
                print(f'-----2---{status}')
                message = {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': ('Warning'),
                        'message': 'FastApi server is responding but no Telegram account is connected',
                        'sticky': False
                    }
                }
                return message
            
        except Exception as e:
            status = False
            print(f'-----3---{status}')
            message = {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': ('Warning'),
                        'message': 'Something is wrong. Check your credentials or connection',
                        'sticky': False
                    }
                }
            self.auth_status = status
            return message
        print(f'-----4---{self.auth_status}')





    # GET INFO ABOUT MYSELF FROM TELEGRAM
    def get_me(self):
        try:
            url = self.server_url + 'get_my_tg'
            payload = {
                "api_id": self.api_id,
                "api_hash": self.api_hash,
                "phone_number": self.phone_number,
                "session_name": self.session_name,
                "message_text": 'blank',
                "recipient": 123
            }

            headers = {"Content-Type": "application/json"}
            response = requests.post(url, json=payload, headers=headers)
            data = response.json()
            print(f'----------{data}----------')
            if data:
                self.username = data['username']
        except:
            raise UserError(f"Something is wrong. Check your credentials or connection")


    # START EVENT LOOP
    # This method gets all the current user telegram api keys and send POST request to
    # FastApi service which should run a infinite loop to listen any new messages 
    def start_event_loop(self):
        try:
            print(f'-----api_id, api_hash: {self.api_id, self. api_hash}')
            url = self.server_url + 'start_event_loop' #URL for POST request
                # Sending all Telegram keys in the body of POST request
            payload = {
                "api_id": self.api_id,
                "api_hash": self.api_hash,
                "phone_number": self.phone_number,
                "session_name": self.session_name,
                "message_text": 'blank',
                "recipient": 123
            }
            headers = {"Content-Type": "application/json"}
            response = requests.post(url, json=payload, headers=headers)
            data = response.json()
            print(f'----------{data}----------')
            print(f"You've started a Telegram session loop succesfully")

            # Check the response from FastApi server if loop started or not
            if data.get('auth_status'):
                self.write({'auth_status': True})
                message = {
                    'effect': {
                        'fadeout': 'slow',
                        'message': 'You are connected to Telegram',
                        'type': 'rainbow_man'
                    }
                }
                
                print(f'------1-------self.auth_status = {self.auth_status}')
                return {'type': 'ir.actions.client', 'tag': 'reload'}, message
            else:
                self.auth_status = False
                message = {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': ('FastApi Server is available but Telegram Session is not started. Something wrong with creadentials or authentication process.'),
                        'message': 'You are connected to Telegram',
                        'sticky': False
                    }
                }
                return message
        except Exception as e:
            status = False
            message = {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': ('Warning'),
                        'message': 'Something is wrong. Check your credentials or connection',
                        'sticky': False
                    }
                }
            self.auth_status = status
            return message



    # SEND MESSAGE TO TELEGRAM
    # This method gets all the current user telegram api keys and send POST request to
    # FastApi service which should call 'send_message' function 
    def send_telegram_message(self, vals):
        # Get a current User telegram record 
        # The structure: 'telegram_client_id' is M2O field in 'telegram.client'
        current_user = self.env.user.telegram_client_id
        print(f'======= INFO(model.py): TRYING TO SEND TELEGRAM MESSAGE--- api_id: {current_user.api_id}')
        # Check if user has telegram credentials
        if current_user:
            try:
                url = current_user.server_url + 'send_new_message' #URL for POST request
                # Sending all Telegram keys in the body of POST request
                payload = {
                    "api_id": current_user.api_id,
                    "api_hash": current_user.api_hash,
                    "phone_number": current_user.phone_number,
                    "session_name": current_user.session_name,
                    "message_text": vals['body'],
                    "recipient": vals['telegram_dialog_id']
                }
                headers = {"Content-Type": "application/json"}
                print(f'======= INFO(model.py): TRYING TO MAKE POST RQUEST with json = {payload}')
                response = requests.post(url, json=payload, headers=headers)
                #response.raise_for_status()  # Raise an exception if the request was not successful (status code >= 400)
                data = response.json()
                if data.get('telegram_api'):
                    print(f'======= INFO(model.py): MESSAGE SENT----------{data}----------')
                    return{'telegram_api': 'OK'}
                else:
                    print(f'======= INFO(model.py): data.get(telegram_api) = {data.get("telegram_api")}')
                    print(f'======= INFO(model.py): telegram_api is None')
                    return {'telegram_api': None}
            except requests.exceptions.RequestException as e:
                error_message = f"INFO(model.py) An error occurred while making the POST request: {e}"
                raise exceptions.UserError(error_message)  # Raise a UserError exception to display the error in a dialog box
        else:
            raise exceptions.UserError("No Telegram credentials found for the current user.")
        

    def open_telegram_auth_wizard(self):
        # Assuming you want to open the wizard for the current record
        # If you want to open it for a specific record, you can pass the record's ID as a parameter

        # Create an action record for the wizard view
        action = self.env.ref('odoo_telegram_client.telegram_auth_wizard').read()[0]
        print(f'===== WIZARD {action}')
        # Modify the context as needed (e.g., pass additional values)
        context = {
            'default_phone_number': self.phone_number,  # Example field to set a default value
            # Add more context values if needed
        }

        # Set the context in the action
        action['context'] = context

        # Open the wizard view as a new window
        return action