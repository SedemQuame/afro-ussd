import json
from flask import make_response
from session_manager import SessionManager
import pprint

# global
sender = "sedem.amekpewu.3@gmail.com"
password = "__"

def random_otp_generator():
    import string
    import random
    str_len = 6
    ran = ''.join(
        random.choices(
            string.ascii_uppercase +
            string.digits,
            k=str_len))
    return str(ran)

    # --------------------------------------------------------------------------------------------------------------------------------------------------------
def mail_random_string_to_(sender, receiver, password, intent, phone_number):
    import smtplib
    # generate random otp and inject into message.
    random_otp = random_otp_generator()
    mail_content = f"You are receiving this email because there was a {intent} for you AFROUSSD account.\nEnter this OTP to verify your identity {random_otp}"

    email_text = """\
    From: %s
    To: %s
    Subject: %s

    %s
    """ % (sender, ", ".join(receiver), intent, mail_content)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, ", ".join(receiver), email_text)
        server.quit()

        print('Email sent!')

        # store generated random otp, using phone number as key in redis.
        # use SET to create pair, EXPIRE to delete after X seconds.
        SessionManager().set_and_expire_keys(phone_number, random_otp)
    except Exception as exception:
        print(exception)

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
        menu_text += '4. Account Balance\n'
        menu_text += '5. Password Reset\n'
        return self.session.ussd_proceed(menu_text, _id, '1')

    def register_account(self, _id, phase_str):
        menu_text = "Register Bank Account\n"
        menu_text += phase_str
        return self.session.ussd_proceed(menu_text, _id, '44')

    def unavailable(self, _id):
        menu_text = "Service Unavailable"
        return self.session.ussd_end(menu_text)
    # --------------------------------------------------------------------------------------------------------------------------------------------------------
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

    def transfer_money_sequence(
            self,
            menu_text,
            _id,
            Accounts,
            db,
            sender_phone_number):
        phase_str = ''
        sender_account = Accounts.query.filter_by(phone=sender_phone_number).all()
        receiver_account = None
        if len(menu_text.split('*')) == 2:
            # save sender_phone_number in redis session dict object
            starting_dict = dict()
            self.session.save_session_dict(
                sender_phone_number, str(starting_dict))
            phase_str = 'Enter phone number.\n'
        elif len(menu_text.split('*')) == 3:
            recipient_phone_number = menu_text.split('*')[-1]
            # check number validity, todo: perform some complex checks here.
            if recipient_phone_number.isdigit():
                try:
                    # save in redis session dict object, using phone number as
                    # key
                    stored_transfer_session = eval(
                        self.session.get_session_dict(sender_phone_number))
                    stored_transfer_session['recipient'] = recipient_phone_number
                    self.session.save_session_dict(
                        sender_phone_number, str(stored_transfer_session))
                    phase_str = 'Confirm phone number.\n'
                except TypeError as e:
                    phase_str = "An Error Ocurred."
                    print(e)
                    return self.session.ussd_end(phase_str)
            else:
                # delete redis cache using key
                self.session.delete_id(sender_phone_number)
                # set phase_str to "number invalid" message
                phase_str = "Number is not valid"
                return self.session.ussd_end(phase_str)
        elif len(menu_text.split('*')) == 4:
            confirm_phone_number = menu_text.split('*')[-1]
            stored_transfer_session = eval(
                self.session.get_session_dict(sender_phone_number))

            # recipient_phone_number is invalid or doesn't match stored number
            if confirm_phone_number.isdigit(
            ) and confirm_phone_number == stored_transfer_session['recipient']:
                global receiver
                receiver_account = Accounts.query.filter_by(phone=confirm_phone_number).all()
                phase_str = 'Enter Amount.\n'
            else:
                # delete redis cache using key
                self.session.delete_id(sender_phone_number)
                # return phase_str is "number invalid" message
                phase_str = "Numbers don't match"
        elif len(menu_text.split('*')) == 5:
            amount = menu_text.split('*')[-1]

            # save in redis dict.
            stored_transfer_session = eval(
                self.session.get_session_dict(sender_phone_number))
            stored_transfer_session['amount'] = amount
            self.session.save_session_dict(
                sender_phone_number, str(stored_transfer_session))

            phase_str = 'Enter Reference ID.\n'
        elif len(menu_text.split('*')) == 6:
            reference_id = menu_text.split('*')[-1]

            # save in redis dict.
            stored_transfer_session = eval(
                self.session.get_session_dict(sender_phone_number))
            stored_transfer_session['reference'] = reference_id
            self.session.save_session_dict(
                sender_phone_number, str(stored_transfer_session))

            phase_str = 'Enter your PIN number.\n'
        elif len(menu_text.split('*')) == 7:
            pin = menu_text.split('*')[-1]
            stored_transfer_session = eval(
                self.session.get_session_dict(sender_phone_number))
            amount_to_transfer = int(stored_transfer_session['amount'])

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

                if pin == sender_account[0].pin:
                    # store redis dict object in transactions database
                    if ((int(sender_account[0].balance) -
                            amount_to_transfer) < 0):
                        phase_str = "Account balance is not enough to continue transaction."
                        return self.session.ussd_end(phase_str)
                    else:
                        sender_new_balance = str(
                            (int(sender_account[0].balance) - amount_to_transfer))
                        sender_account[0].balance = sender_new_balance

                        stored_transfer_session = eval(self.session.get_session_dict(sender_phone_number))
                        receiver_number = stored_transfer_session['recipient']
                        receiver_account = Accounts.query.filter_by(phone=receiver_number).all()

                        if len(receiver_account) == 0:
                            phase_str = "Receiving account is not registered for AFROUSSD service."
                            return self.session.ussd_end(phase_str)

                        receiver_new_balance = str(
                            (int(receiver_account[0].balance) + amount_to_transfer))
                        receiver_account[0].balance = receiver_new_balance
                        db.session.commit()

                        phase_str = f"Amount {stored_transfer_session['amount']} sent to {sender_account[0].name}, with reference id {stored_transfer_session['reference']}."
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
    def withdrawal_sequence(
            self,
            menu_text,
            _id,
            Accounts,
            db,
            sender_phone_number):
        phase_str = "Cash Withdrawal\n"
        sender_account = Accounts.query.filter_by(phone=sender_phone_number).all()
        withdrawal_sequence_type = menu_text.split('*')[-1]
        if len(menu_text.split('*')) == 1:
            phase_str += f"1.Cash withdrawal through an Agent\n"
            phase_str += f"2.Cash withdrawal using an ATM\n"
            return self.session.ussd_proceed(phase_str, _id, '2')
        elif len(menu_text.split('*')) == 2:
            if withdrawal_sequence_type == '1' or withdrawal_sequence_type == '2':
                phase_str = f"Cash withdrawal through an Agent\n"
                phase_str += f"Enter amount\n"
                return self.session.ussd_proceed(phase_str, _id, '21')
            else:
                phase_str = f"Unknown input, please try again"
                return self.session.ussd_end(phase_str)
        elif len(menu_text.split('*')) == 3:
            withdrawal_amount = menu_text.split('*')[-1]
            current_balance = sender_account[0].balance
            if ((int(current_balance) - int(withdrawal_amount)) < 0):
                phase_str = "Your balance is not enough to perform this transaction."
            else:
                amount_left = str(
                    int(current_balance) -
                    int(withdrawal_amount))
                sender_account[0].balance = amount_left
                db.session.commit()
                phase_str = f"GHS {withdrawal_amount}.00 was withdrawn from your account, current balance is GHS {amount_left}.00"
        else:
            phase_str = f"An error occurred during the money withdrawal process, please try again."
        return self.session.ussd_end(phase_str)
    # --------------------------------------------------------------------------------------------------------------------------------------------------------
    def payment_sequence(
            self,
            menu_text,
            _id,
            Accounts,
            db,
            sender_phone_number):
        phase_str = ''
        if menu_text == '3':
            phase_str = "Make Payment\n"
            phase_str += "1. Utilities\n"
            phase_str += "2. School Fees\n"
            return self.session.ussd_proceed(phase_str, _id, '13')
        elif len(menu_text.split('*')) == 2:
            if menu_text.split('*')[-1] == '1':
                phase_str = "Utilities\n"
                phase_str += "1. ECG\n"
                phase_str += "2. Ghana Water\n"
            elif menu_text.split('*')[-1] == '2':
                phase_str = "School Fees Payment Service\n"
                phase_str += "Search for school"
            else:
                phase_str = f"Unknown input, please try again."
                return self.session.ussd_end(phase_str)
        elif len(menu_text.split('*')) == 3:
            if menu_text[2:] == "1*1":
                phase_str = "ECG\n"
                phase_str += "Enter meter ID"
            elif menu_text[2:] == "1*2":
                phase_str = "Ghana Water Company\n"
                phase_str += "Enter meter ID"
            elif menu_text.split('*')[1] == '2':
                school_name = menu_text.split('*')[-1]
                phase_str = "School Fees\n"
                phase_str += f"Enter amount to pay "
            else:
                phase_str = f"Unknown input, please try again"
                return self.session.ussd_end(phase_str)
        elif len(menu_text.split('*')) == 4:
            if menu_text.split('*')[1] == 2:
                withdrawal_amount = menu_text[-1]
                # start amount withdrawal process, to simullate transfer.
                sender_account = Accounts.query.filter_by(phone=sender_phone_number).all()
                current_balance = sender_account[0].balance
                amount_left = str(
                    int(current_balance) -
                    int(withdrawal_amount))
                sender_account[0].balance = amount_left
                db.session.commit()
                phase_str = f"GHS {withdrawal_amount}.00 was withdrawn from your account, current balance is GHS {amount_left}.00 "
                institution = menu_text.split('*')[3]
                phase_str += f"for payment to {institution}"
                return self.session.ussd_end(phase_str)
            else:
                # get meter id and get amount to pay.
                meter_id = menu_text.split('*')[-1]
                if menu_text[2:] == "1*1":
                    phase_str = "ECG\n"
                    # store meter_id in redis
                elif menu_text[2:] == "1*2":
                    phase_str = "Ghana Water Company\n"
                    # store meter_id in redis
                phase_str += f"Enter amount to pay "
        elif len(menu_text.split('*')) == 5:
            withdrawal_amount = menu_text.split('*')[4]
            # start amount withdrawal process, to simullate transfer.
            sender_account = Accounts.query.filter_by(phone=sender_phone_number).all()
            current_balance = sender_account[0].balance
            amount_left = str(
                int(current_balance) -
                int(withdrawal_amount))
            sender_account[0].balance = amount_left
            db.session.commit()
            phase_str = f"GHS {withdrawal_amount}.00 was withdrawn from your account, current balance is GHS {amount_left}.00 "
            institution = menu_text.split('*')[3]
            phase_str += f"for payment to {institution}"
            return self.session.ussd_end(phase_str)
        else:
            phase_str = f"Service is currently unavailable."
            return self.session.ussd_end(phase_str)
        return self.session.ussd_proceed(phase_str, _id, '12')
    # --------------------------------------------------------------------------------------------------------------------------------------------------------
    def account_balance(self, text, _id, Accounts, db, sender_phone_number):
        phase_str = ''
        user_account = Accounts.query.filter_by(
            phone=sender_phone_number).all()
        if text == '4':
            phase_str += "Account Balance\n"
            phase_str += f"Your account balance is GHS{user_account[0].balance}.00"
        return self.session.ussd_end(phase_str)
    # --------------------------------------------------------------------------------------------------------------------------------------------------------
    def pin_change_sequence(
            self,
            menu_text,
            _id,
            Accounts,
            db,
            sender_phone_number):
        phase_str = ''
        sender_account = Accounts.query.filter_by(
            phone=sender_phone_number).all()
        if menu_text == '5':
            phase_str = "Enter your current Pin.\n"
            return self.session.ussd_proceed(phase_str, _id, '')
        elif len(menu_text.split('*')) == 2:
            # get current pin value and compare it to the stored pin value
            # if the pins match, proceed to generating the OTP
            # else return message that pin is wrong and end process.
            entered_pin = menu_text.split('*')[-1]
            stored_pin = sender_account[0].pin
            if entered_pin == stored_pin:
                # match, ask to send
                # change account to accept email address.
                receiver = sender_account[0].email
                intent = "PIN change request"
                mail_random_string_to_(sender, receiver, password, intent)
                phase_str = "Please enter the OTP sent to your email address."
                return self.session.ussd_proceed(phase_str, _id, '')
            else:
                phase_str = "Wrong PIN."
                return self.session.ussd_end(phase_str)
        elif len(menu_text.split('*')) == 3:
            entered_otp = menu_text.split('*')[-1]
            id_otp = f"{sender_phone_number}_otp"
            if entered_otp == self.session.read_value(id_otp):
                # otp entered by user matches, saved otp.
                phase_str = "Please enter your new PIN."
                return self.session.ussd_proceed(phase_str, _id, '')
            else:
                phase_str = "Wrong OTP"
                return self.session.ussd_end(phase_str)
        elif len(menu_text.split('*')) == 4:
            new_pin = menu_text.split('*')[-1]
            sender_account[0].pin = new_pin
            db.session.commit()
            phase_str = "Pin Changed."
            return self.session.ussd_end(phase_str)
        else:
            phase_str = "Input is unknown."
            return self.session.ussd_end(phase_str)
    # --------------------------------------------------------------------------------------------------------------------------------------------------------

# mail_random_string_to_(sender, ["sedemquame@gmail.com"], password, "PIN Change Request", "0546744163")
# *384*26678#
# *384*566645#
