# Your code goes here
import os
from flask import Flask, request
app = Flask(__name__)

response = ""

@app.route('/', methods=['POST', 'GET'])
def ussd_callback():
    global response
    session_id = request.values.get("sessionId", None)
    service_code = request.values.get("serviceCode", None)
    phone_number = request.values.get("phoneNumber", None)
    text = request.values.get("text", "default")

    # string matching
    if text == '':
        # represents the start of the ussd_session, show the menu.
        # CON is intentionally placed at the start of the text.
        # to represent the continuation of the given string.
        # to END the ussd session, append END to the ussd text.
        response = 'CON What would you want to check \n'
        response += '1. My Account \n'
        response += '2. My phone number'

    # string matching
    elif text == '1':
        response = "CON Choose account information you want to view \n"
        response += "1. Account number \n"
        response += "2. Account balance"

    # string matching
    elif text == '1*1':
        accountNumber = 'ACC1001'
        response = "END Your account number is " + accountNumber

    # string matching
    elif text == '1*2':
        balance = "KES 10,000"
        response = "END Your balance is " + balance

    # string matching
    elif text == '2':
        response = "END This is your phone number " + phone_number

    return response


# creating application port.
if __name__ == '__main__':
    # run application on localhost, using port stored as PORT in env variables.
    app.run(host="0.0.0.0", port=os.environ.get('PORT'))