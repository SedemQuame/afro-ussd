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
    text = request.values.get("text", '')

    # string matching
    if text == '':
        # represents the start of the ussd_session, show the menu.
        # CON is intentionally placed at the start of the text.
        # to represent the continuation of the given string.
        # to END the ussd session, append END to the ussd text.
        response = 'CON Menu \n'
        response += '1. Transfer Money \n'
        response += '2. MoMoPay & Pay Bill \n'
        response += '3. Airtime & Bundles \n'
        response += '4. Allow Cash Out \n'
        response += '5. MoMoPay & Pay Bill \n'
        response += '6. Airtime & Bundles \n'
    elif text == '1':
        response = "CON Transfer Money \n"
        response += "1. MoMo User \n"
        response += "2. Non MoMo User \n"
        response += '3. Send with Care \n'
        response += '4. Other Networks \n'
        response += '5. Bank Account \n'
        response += '0. Airtime & Bundles \n'        
    elif text == '1*1':
        response = "CON Enter mobile number "
    elif text == '1*1*continued':
        response = "CON Confirm mobile number "
    elif text == '1*1*continued':
        response = "CON Enter Amount "
    elif text == '1*1*continued':
        response = "CON Enter Reference "
    elif text == '1*1*continued':
        # get data from database on user amouunt.
        response = "CON Transfer <amount> to <user_name> of number <user_number_from_session> with reference. <text_response>."  

    elif text == '2':
        response = "CON MoMoPay & Pay Bill \n"
        response += "1. MoMoPay \n"
        response += "2. Pay Bill \n"
        response += "0. Back"
    elif text == '2*1':
        response = "END Enter Merchant id/Payment Reference\n"
        response += "Service still under construction."
    elif text == '2*2':
        response = "CON Pay Bill \n"
        response += "1. Utilities \n"
        response += "2. TV & Entertainment \n"
        response += "3. School Fees \n"
        response += "4. MTN Bills \n"
        response += "0. Back"
    elif text == '2*2*1':
        response = "CON Utilities \n"
        response += "1. ECG \n"
        response += "2. Ghana Water \n"
        response += "0. Back"
    elif text == '2*2*2':
        response = "CON TV & Entertainment \n"
        response += "1. DStv/GOtv \n"
        response += "2. Startimes \n"
        response += "3. GCNET Payment \n"
        response += "0. Back"
    elif text == '2*2*3':
        response = "CON School Fees Payment Service \n"
        response += "Select an option \n"
        response += "1. Search for school \n"
        response += "0. Back"
    elif '2*2*3' in text or '2*2*2' in text:
        response = "Service still under construction. \n"      

    elif text == '3':
        response = "CON Airtime & Bundles \n"
        response += "1. Airtime \n"
        response += "2. Internet Bundles \n"
        response += "3. Fixed Broadband \n"
        response += "0. Back"
    elif text == '3*1':
        response = "CON Airtime \n"
        response += "1. Self \n"
        response += "2. Others \n"
        response += "3. Welcome Pack \n"
        response += "4. Other Networks \n"
        response += "0. Back"
    elif text == '3*2':
        response = "CON Welcome to Bundle Portal. Please select your bundle. \n"
        response += "1. Buy Data Bundle \n"
        response += "2. Midnight Bundles \n"
        response += "3. Kokrokoo Bundle \n"
        response += "4. Social Media Bundles \n"
        response += "5. Video Bundles \n"
        response += "6. More \n"
        response += "0. Back"
    elif '3*1*' in text or '3*2*' in text:
        response = "Service still under construction. \n"

    return response


# creating application port.
if __name__ == '__main__':
    # run application on localhost, using port stored as PORT in env variables.
    app.run(host="0.0.0.0", port=os.environ.get('PORT'))