import os
from flask import Flask, make_response, request, flash, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

# from menu import Registration
from util import generate_random_acc, choose_random_bank_branch
from session_manager import SessionManager
from menu import Menu

file_path = os.path.abspath(os.getcwd())+"\accounts.sqlite3"
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///accounts.sqlite3'
app.config['SECRET_KEY'] = "random string"

db = SQLAlchemy(app)

response = ""
session = SessionManager()
menu = Menu(session)

class accounts(db.Model):
   id = db.Column('account_id', db.Integer, primary_key = True)
   account_number = db.Column(db.String(30)) #program generated
   bank_branch = db.Column(db.String(50)) # program generated
   name = db.Column(db.String(50)) # user input
   pin = db.Column(db.String(6)) # user input
   phone = db.Column(db.String(15)) # user input
   balance = db.Column(db.String(200)) # default 0, user input (teller)
   retry_chances = db.Column(db.Integer) # default 3
   creation_date = db.Column(db.String(10)) # progam generated

def __init__(self, account_number, phone, balance, bank_branch, name, pin, retry_chances, creation_date):
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

@app.route('/new', methods = ['GET', 'POST'])
def new():
   if request.method == 'POST':
      if not request.form['name'] or not request.form['phone'] or not request.form['balance'] or not request.form['pin']:
         flash('Please enter all the fields', 'error')
      else:
         default_pin_retry_chances = 3
         account = accounts(account_number = generate_random_acc(), phone = request.form['phone'],
            balance = request.form['balance'], bank_branch = choose_random_bank_branch(), name = request.form['name'], pin = request.form['pin'],
            retry_chances = default_pin_retry_chances, creation_date = '')
         db.session.add(account)
         db.session.commit()
         flash('Record was successfully added')
         return redirect(url_for('show_all'))
   return render_template('new.html')

@app.route('/delete', methods = ['POST'])
def delete():
   if request.method == 'POST':
      if not request.form['id']:
         flash('Please enter all the fields', 'error')
      else:
         accounts.query.filter_by(id=request.form['id']).delete()
         db.session.commit()
         return redirect(url_for('show_all'))

@app.route('/all')
def show_all():
   return render_template('show_all.html', accounts = accounts.query.all() )

@app.route('/ussd/callback', methods=['POST', 'GET'])
def ussd_callback():
    global response
    _id = request.values.get("sessionId", None)
    service_code = request.values.get("serviceCode", None)
    phone_number = request.values.get("phoneNumber", None)
    text = request.values.get("text", '')

    if text == '':
        return menu.home(_id)
    elif text == '1':
        return menu.transfer(_id)
    elif text == '1*1':
        return menu.unavailable(_id)
    elif text == '1*2':
        return menu.unavailable(_id)
    elif text == '1*3':
        return menu.unavailable(_id)
    elif text == '1*4':
        return menu.unavailable(_id)
    elif text == '1*5':
        return menu.unavailable(_id)
    elif text == '1*6':
        return menu.unavailable(_id)
    elif text == '1*7':
        return menu.unavailable(_id)
    elif text == '2':
        return menu.withdrawal(_id)
    elif text == '2*1':
        return menu.unavailable(_id)
    elif text == '2*2':
        return menu.unavailable(_id)            
    elif text == '3':
        return menu.payment(_id)
    elif text == '3*1':
        return menu.unavailable(_id)
    elif text == '3*2':
        return menu.unavailable(_id)
    elif text == '3*3':
        return menu.unavailable(_id)
    elif text == '4':
        return menu.my_bank(_id)
    elif text == '4*1':
        return menu.unavailable(_id)
    elif text == '4*2':
        return menu.unavailable(_id)
    elif text == '4*3':
        return menu.unavailable(_id)
    elif text == '4*4':
        return menu.register_account_name(_id)
    elif text == '4*4*1':
        return menu.register_account_pin(_id)
    else:
        return 'END Unknown User Input.'

# creating application port.
if __name__ == '__main__':
    # run application on localhost, using port stored as PORT in env variables.
    app.run(host="0.0.0.0", port=os.environ.get('PORT'))