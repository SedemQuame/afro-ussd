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
        menu_text += '1. Create an account \n'
        menu_text += '2. Exit \n'
        return self.session.ussd_proceed(menu_text, '0')

    def home(self, _id):
        """serves the home menu"""
        menu_text = 'Main Menu \n'  
        menu_text += '1. Transfer Money\n'
        menu_text += '2. Cash Withdrawal\n'
        menu_text += '3. Make Payment\n'
        menu_text += '4. My Bank\n'
        return self.session.ussd_proceed(menu_text, _id, '1')

    def my_bank(self, _id):
        menu_text = "My Bank\n"
        menu_text += "1. Check Balance\n"
        menu_text += "2. Account Statement\n"
        menu_text += "3. Change and reset pin\n"
        menu_text += "4. Register Account\n"
        return self.session.ussd_proceed(menu_text, _id, '14')

    def register_account(self, _id, phase_str):
        menu_text = "Register Bank Account\n"
        menu_text += phase_str
        return self.session.ussd_proceed(menu_text, _id, '44')

    def unavailable(self, _id):
        menu_text = "Service Unavailable"
        return self.session.ussd_end(menu_text)

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

    def transfer_money_sequence(self, menu_text, _id, Accounts, db, sender_phone_number):
        phase_str = ''
        if len(menu_text.split('*')) == 2:
            # save sender_phone_number in redis session dict object
            starting_dict = dict()
            self.session.save_session_dict(sender_phone_number, str(starting_dict))
            phase_str = 'Enter phone number.\n'
        elif len(menu_text.split('*')) == 3:
            recipient_phone_number = menu_text.split('*')[-1]

            if recipient_phone_number.isdigit(): #check number validity, todo: perform some complex checks here.
                try:
                    # save in redis session dict object, using phone number as key
                    stored_transfer_session = eval(self.session.get_session_dict(sender_phone_number))
                    stored_transfer_session['recipient'] = recipient_phone_number
                    self.session.save_session_dict(sender_phone_number, str(stored_transfer_session))
                    phase_str = 'Confirm phone number.\n'
                except TypeError as e:
                    phase_str = "Service is currently unavailable"
                    return self.session.ussd_end(phase_str)
            else:
                # delete redis cache using key
                self.session.delete_id(sender_phone_number)
                # set phase_str to "number invalid" message
                phase_str = "Number is not valid"
                return self.session.ussd_end(phase_str)
        elif len(menu_text.split('*')) == 4:
            confirm_phone_number = menu_text.split('*')[-1]
            stored_transfer_session = eval(self.session.get_session_dict(sender_phone_number))

            if confirm_phone_number.isdigit() and confirm_phone_number == stored_transfer_session['recipient']: #recipient_phone_number is invalid or doesn't match stored number
                phase_str = 'Enter Amount.\n'
            else:
                # delete redis cache using key
                self.session.delete_id(sender_phone_number)

                # return phase_str is "number invalid" message
                phase_str = "Numbers don't match"
        elif len(menu_text.split('*')) == 5:
            amount = menu_text.split('*')[-1]

            # save in redis dict.
            stored_transfer_session = eval(self.session.get_session_dict(sender_phone_number))
            stored_transfer_session['amount'] = amount
            self.session.save_session_dict(sender_phone_number, str(stored_transfer_session))

            phase_str = 'Enter Reference ID.\n'
        elif len(menu_text.split('*')) == 6:
            reference_id = menu_text.split('*')[-1]

            # save in redis dict.
            stored_transfer_session = eval(self.session.get_session_dict(sender_phone_number))
            stored_transfer_session['reference'] = reference_id
            self.session.save_session_dict(sender_phone_number, str(stored_transfer_session))

            phase_str = 'Enter your PIN number.\n'
        elif len(menu_text.split('*')) == 7:
            pin = menu_text.split('*')[-1]
            sender_account = Accounts.query.filter_by(phone=sender_phone_number).all()

            if sender_account[0].retry_chances == 0:
                phase_str = f"Account locked, please manually verify your identity by talking with our admin to regain access."
                return self.session.ussd_end(phase_str)

            if len(sender_account) < 1:
                phase_str = "Account not found."
                return self.session.ussd_end(phase_str)

            try:
                if not(pin == sender_account[0].pin):
                    chances_left = sender_account[0].retry_chances - 1
                    sender_account[0].retry_chances = chances_left
                    db.session.commit()

                    if chances_left > 0:
                        phase_str = f"Incorrect pin, retry chances till account is locked is {chances_left}"
                    else:
                        phase_str = f"Account locked, please manually verify your identity by talking with our admin to regain access."
                    return self.session.ussd_end(phase_str)

                if pin == sender_account[0].pin: #pin entered matches pin stored in database
                    stored_transfer_session = eval(self.session.get_session_dict(sender_phone_number))
                    phase_str = f"Amount {stored_transfer_session['amount']} sent to {sender_account[0].name}, with reference id {stored_transfer_session['reference']}."
                    # store redis dict object in transactions database
            except Exception as e:
                phase_str = "An error occurred, please try again later."
                # log  error that ocurred.
                print(e)
            finally:
                self.session.delete_id(sender_phone_number)
                return self.session.ussd_end(phase_str)
        else:
            phase_str = f"Unknown input, please try again"  
            return self.session.ussd_end(phase_str)
        return self.session.ussd_proceed(phase_str, _id, '11')

# --------------------------------------------------------------------------------------------------------------------------------------------------------
    def withdrawal(self, _id):
        menu_text = "Cash Withdrawal\n"
        menu_text += "1. Agent\n"
        menu_text += "2. ATM\n"
        return self.session.ussd_proceed(menu_text, _id, '12')

    def withdrawal_sequence(self, menu_text, _id):
        phase_str = ""
        print('withdrawal sequence')
        print(len(menu_text.split('*')))
        if len(menu_text.split('*')) == 2:
            print("simp")
            phase_str = ""
            withdrawal_sequence_type = menu_text.split('*')[-1]
            if withdrawal_sequence_type == '1':
                # cash withdrawal using an agent
                phase_str = f"Cash withdrawal through an Agent"
            elif withdrawal_sequence_type == '2':
                #  cash withdrawal using the ATM
                phase_str = f"Cash withdrawal using an ATM"
            else:
                phase_str = f"Unknown input, please try again 1"
        else:
            phase_str = f"Unknown input, please try again 2"
        phase_str +=  "\nis currently unavailable"
        return self.session.ussd_end(phase_str)
# --------------------------------------------------------------------------------------------------------------------------------------------------------

    def payment(self, _id):
        menu_text = "Make Payment\n"
        menu_text += "1. Pay Bills\n"
        menu_text += "2. Buy Goods\n"
        return self.session.ussd_proceed(menu_text, _id, '13')

    def payment_sequence(self, menu_text, _id):
        phase_str = ''
        payment_sequence_type = menu_text.split('*')[-1]

        if len(menu_text.split('*')) == 2:
            if payment_sequence_type == '1':
                #   pay bills
                phase_str = "Pay Bills\n"
                phase_str += "1. Utilities\n"
                phase_str += "2. TV & Entertainment\n"
                phase_str += "3. School Fees\n"
                phase_str += "4. General Payment\n"
            elif payment_sequence_type == '2':
                #   buy goods
                phase_str = "Buy Goods\n"
                phase_str += "Service is currently unavailable"
                return self.session.ussd_end(phase_str)
            else:
                #   unknown input
                phase_str = f"Unknown input, please try again"
                return self.session.ussd_end(phase_str)

        if len(menu_text.split('*')) == 3:
            if payment_sequence_type == '1':
                # utilities
                phase_str = "Utilities\n"
                phase_str += "1. ECG\n"
                phase_str += "2. Ghana Water\n"
            elif payment_sequence_type == '2':
                phase_str = "TV & Entertainment\n"
                phase_str += "1. DStv/GOtv\n"
                phase_str += "2. DStv/GOtv\n"
                phase_str += "3. DStv/GOtv\n"
            elif payment_sequence_type == '3':
                phase_str = "School Fees Payment Service\n"
                phase_str += "1. Search for school"
            elif payment_sequence_type == '4':
                phase_str = "General Payment\n"
                phase_str += "Enter Payment Code"
            else:
                #unknown input
                phase_str = f"Unknown input, please try again"
                return self.session.ussd_end(phase_str)

        if len(menu_text.split('*')) == 4:
            phase_str = f"Service is currently unavailable"
            return self.session.ussd_end(phase_str)
        
        return self.session.ussd_proceed(phase_str, _id, '12')

# *384*26678#
# *384*566645#