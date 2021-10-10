import json
from flask import make_response
from session_manager import SessionManager

class Menu():
    # class attributes
    def __init__(self, session):
        self.session = session

    def execute(self):
        raise NotImplementedError

    def registration(self, phone_number):
        menu_text = 'Service Registration \n'
        menu_text += 'You are not registered for this service. \n'
        menu_text += 'To register please enter your name & email. \n'
        menu_text += 'and email. \n'
        return self.session.ussd_proceed(menu_text, '00')

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


    # # string matching
    # if text == '':
    #     # represents the start of the ussd_session, show the menu.
    #     # CON is intentionally placed at the start of the text.
    #     # to represent the continuation of the given string.
    #     # to END the ussd session, append END to the ussd text.
    #     response = 'CON Menu \n'
    #     response += '1. Transfer Money \n'
    #     response += '2. Cash Withdrawal \n'
    #     response += '3. Make payment \n'
    #     response += '4. My Bank \n'
    # elif text == '1':
    #     response = "CON Transfer Money \n"
    #     response += "1. Vodafone \n"
    #     response += "2. AirtelTigo \n"
    #     response += '3. Bank Account \n'
    #     response += '4. E-Zwich \n'
    #     response += '5. G-money \n'
    #     response += '6. ZeePay'      
    # elif text == '1*1':
    #     response = "CON Enter mobile number "
    # elif text == '1*1*continued':
    #     response = "CON Confirm mobile number "
    # elif text == '1*1*continued':
    #     response = "CON Enter Amount "
    # elif text == '1*1*continued':
    #     response = "CON Enter Reference "
    # elif text == '1*1*continued':
    #     # get data from database on user amouunt.
    #     response = "CON Transfer <amount> to <user_name> of number <user_number_from_session> with reference. <text_response>."  

    # elif text == '2':
    #     response = "CON Cash Withdrawal \n"
    #     response += "1. Agent \n"
    #     response += "2. ATM \n"
    #     response += "0. Back"
    # elif text == '2*1':
    #     response = "END Enter Merchant id/Payment Reference\n"
    #     response += "Service still under construction."
    # elif text == '2*2':
    #     response = "CON Pay Bill \n"
    #     response += "1. Utilities \n"
    #     response += "2. TV & Entertainment \n"
    #     response += "3. School Fees \n"
    #     response += "4. MTN Bills \n"
    #     response += "0. Back"
    # elif text == '2*2*1':
    #     response = "CON Utilities \n"
    #     response += "1. ECG \n"
    #     response += "2. Ghana Water \n"
    #     response += "0. Back"
    # elif text == '2*2*2':
    #     response = "CON TV & Entertainment \n"
    #     response += "1. DStv/GOtv \n"
    #     response += "2. Startimes \n"
    #     response += "3. GCNET Payment \n"
    #     response += "0. Back"
    # elif text == '2*2*3':
    #     response = "CON School Fees Payment Service \n"
    #     response += "Select an option \n"
    #     response += "1. Search for school \n"
    #     response += "0. Back"
    # elif '2*2*3' in text or '2*2*2' in text:
    #     response = "Service still under construction. \n"      

    # elif text == '3':
    #     response = "CON Make Payment \n"
    #     response += "1. Pay Bill \n"
    #     response += "2. Buy goods \n"
    #     response += "3. School Payment \n"
    #     response += "0. Back"
    # elif text == '3*1':
    #     response = "CON Airtime \n"
    #     response += "1. Self \n"
    #     response += "2. Others \n"
    #     response += "3. Welcome Pack \n"
    #     response += "4. Other Networks \n"
    #     response += "0. Back"
    # elif text == '3*2':
    #     response = "CON Welcome to Bundle Portal. Please select your bundle. \n"
    #     response += "1. Buy Data Bundle \n"
    #     response += "2. Midnight Bundles \n"
    #     response += "3. Kokrokoo Bundle \n"
    #     response += "4. Social Media Bundles \n"
    #     response += "5. Video Bundles \n"
    #     response += "6. More \n"
    #     response += "0. Back"
    # elif '3*1*' in text or '3*2*' in text:
    #     response = "Service still under construction. \n"

    # elif text == '4':
    #         response = "CON My Bank \n"
    #         response += "1. Check Balance \n"
    #         response += "2. Account Statement \n"
    #         response += "3. Pin Reset \n"
    #         response += "0. Back"
    # return response