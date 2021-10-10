import json
from flask import make_response
from session_manager import SessionManager

class Menu():
    # class attributes
    def __init__(self, session):
        self.session = session

    def execute(self):
        raise NotImplementedError

    def registration(self):
        menu_text = 'Service Registration \n'
        menu_text += 'You are not registered for this service. \n'
        menu_text += 'To register, please enter your name & email. \n'
        return self.session.ussd_proceed(menu_text, '0')

    def home(self, _id):
        """serves the home menu"""
        menu_text = 'Main Menu \n'  
        menu_text += '1. Transfer Money\n'
        menu_text += '2. Cash Withdrawal\n'
        menu_text += '3. Make Payment\n'
        menu_text += '4. My Bank\n'
        return self.session.ussd_proceed(menu_text, _id, '1')

    def transfer(self, _id):
        menu_text = "Transfer Money \n"
        menu_text += "1. Vodafone Network\n"
        menu_text += "2. MTN Network \n"
        menu_text += '3. AirtelTigo \n'
        menu_text += '4. Bank Account \n'
        menu_text += '5. E-Zwich \n'
        menu_text += '6. G-money \n'
        menu_text += '7. ZeePay'
        return self.session.ussd_proceed(menu_text, _id, '11')

    def withdrawal(self, _id):
        menu_text = "Cash Withdrawal\n"
        menu_text += "1. Agent\n"
        menu_text += "2. ATM\n"
        return self.session.ussd_proceed(menu_text, _id, '12')

    def payment(self, _id):
        menu_text = "Make Payment\n"
        menu_text += "1. Pay Bill\n"
        menu_text += "2. Buy goods\n"
        menu_text += "3. School Payment\n"
        return self.session.ussd_proceed(menu_text, _id, '13')

    def my_bank(self, _id):
        menu_text = "My Bank\n"
        menu_text += "1. Check Balance\n"
        menu_text += "2. Account Statement\n"
        menu_text += "2. Change and reset pin\n"
        return self.session.ussd_proceed(menu_text, _id, '14')

    def unavailable(self, _id):
        menu_text = "Service Unavailable"
        return self.session.ussd_proceed(menu_text, _id, '14')

# *384*26678#