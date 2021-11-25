import os
from flask import Flask, make_response, request, flash, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from util import generate_random_acc, choose_random_bank_branch
from session_manager import SessionManager
from menu import Menu
import pprint

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///accounts.sqlite3'
app.config['SECRET_KEY'] = "random string"

db = SQLAlchemy(app)
session = SessionManager()
menu = Menu(session)
response = ""


class Accounts(db.Model):
    id = db.Column('account_id', db.Integer, primary_key=True)
    id_type = db.Column(db.String(30))
    national_id_number = db.Column(db.String(20))
    name = db.Column(db.String(50))  # user input
    phone = db.Column(db.String(15))  # user input or from ussd_session
    email = db.Column(db.String(100))  # user input
    pin = db.Column(db.String(6))  # user input
    bank = db.Column(db.String(100)) #user input
    account_number = db.Column(db.String(30)) #user input
    bank_branch = db.Column(db.String(50)) #user input
    balance = db.Column(db.String(200))  # default 0, user input (teller)
    retry_chances = db.Column(db.Integer)  # default 3
    creation_date = db.Column(db.String(10))  # progam generated


class Transactions(db.Model):
    id = db.Column('transaction_id', db.Integer, primary_key=True)
    sender = db.Column(db.String(50))
    recipient = db.Column(db.String(50))
    amount = db.Column(db.Integer)
    reference = db.Column(db.String(100))
    timestamp = db.Column(db.String(50))


def __init__(
        self,
        account_number,
        phone,
        balance,
        bank_branch,
        name,
        pin,
        retry_chances,
        creation_date):
    self.account_number = account_number
    self.phone = phone
    self.balance = balance
    self.bank_branch = bank_branch
    self.name = name
    self.pin = pin
    self.retry_chances = retry_chances
    self.creation_date = creation_date


@app.route('/', methods=['POST', 'GET'])
def index():
    response = make_response("END connection ok")
    response.headers['Content-Type'] = "text/plain"
    return response


def sanitize(phone_number):
    if '233' in phone_number:
        if phone_number.index('233') == 0 or phone_number.index('+233') == 0:
            phone_number = phone_number.replace('233', '0').replace('+', '')
    return phone_number


@app.route('/new', methods=['GET', 'POST'])
def new():
    default_pin_retry_chances = 3
    # check if pin is alphanumberic contains numbers and letters.
    # check if pin has length greater than or equal to 6

    if request.method == 'POST':
        # if len(request.form['pin']) != 6:
        #     flash('Account PIN must be of length 6.')
        #     return redirect(url_for('new'))

        # if not (request.form['pin']).isalpha():
        #     flash('Account PIN must be alpha numeric.')
        #     return redirect(url_for('new'))
            
        pprint.pprint(request.form)
        account = Accounts(
            name=request.form['name'],
            phone=sanitize(
                request.form['phone']),
            email=request.form['email_address'],
            id_type=request.form['id_type'],
            national_id_number=request.form['national_id_number'],
            pin=request.form['pin'],
            bank=request.form['bank'],
            account_number=request.form['account_number'],
            bank_branch=request.form['bank_branch'],
            balance=request.form['balance'],
            retry_chances=default_pin_retry_chances,
            creation_date='')
        db.session.add(account)
        db.session.commit()
        flash('Record was successfully added')
        return redirect(url_for('show_all'))
    return render_template('new.html')


@app.route('/delete', methods=['POST'])
def delete():
    if request.method == 'POST':
        if not request.form['id']:
            flash('Please enter all the fields', 'error')
        else:
            Accounts.query.filter_by(id=request.form['id']).delete()
            db.session.commit()
            return redirect(url_for('show_all'))

@app.route('/all')
def show_all():
    return render_template('show_all.html', accounts=Accounts.query.all())


@app.route('/restore', methods=['POST'])
def restore_account_chances():
    if request.method == 'POST':
        if request.form['id']:
            Accounts.query.filter_by(
                id=request.form['id']).first().retry_chances = 3
            db.session.commit()
            return redirect(url_for('show_all'))

@app.route('/ussd/callback', methods=['POST', 'GET'])
def ussd_callback():
    global response
    _id = request.values.get("sessionId", None)
    service_code = request.values.get("serviceCode", None)
    phoneNumber = sanitize(request.values.get("phoneNumber", None))
    text = request.values.get("text", '')

    print(text)
    if text == '':
        return menu.home(_id)
    elif text == '1':
        return menu.transfer(_id)
    elif '1*' == text[0:2]:
        return menu.transfer_money_sequence(text, _id, Accounts, db, phoneNumber)
    # ----------------------------------------
    elif text[0] == '2' or '2*' == text[0:2]:
        return menu.withdrawal_sequence(text, _id, Accounts, db, phoneNumber)
    # ----------------------------------------
    elif text[0] == '3' or '3*' == text[0:2]:
        return menu.payment_sequence(text, _id, Accounts, db, phoneNumber)
    # ----------------------------------------
    elif text[0] == '4' or '4*' == text[0:2]:
        return menu.account_balance(text, _id, Accounts, db, phoneNumber)
    # ----------------------------------------
    elif text[0] == '5' or '5*' == text[0:2]:
        return menu.pin_change_sequence(text, _id, Accounts, db, phoneNumber)
    # ----------------------------------------
    else:
        return "END"


# creating application port.
if __name__ == '__main__':
    # run application on localhost, using port stored as PORT in env variables.
    db.create_all()
    app.run(host="0.0.0.0", port=os.environ.get('PORT'))