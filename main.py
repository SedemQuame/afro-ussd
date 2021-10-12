# Your code goes here
import os
from flask import Flask, request, make_response
app = Flask(__name__)

# from menu import Registration
from session_manager import SessionManager
from menu import Menu

response = ""
session = SessionManager()
menu = Menu(session)

@app.route('/', methods=['POST', 'GET'])
def index():
    response = make_response("END connection ok")
    response.headers['Content-Type'] = "text/plain"
    return response

@app.route('/ussd/callback', methods=['POST', 'GET'])
def ussd_callback():
    global response
    _id = request.values.get("sessionId", None)
    service_code = request.values.get("serviceCode", None)
    phone_number = request.values.get("phoneNumber", None)
    text = request.values.get("text", 'default')

    print("Service code", service_code)
    print("Text", text)

    # check if the session id has already been saved
    if not session.checker(_id):
        session.save(_id)
        return menu.registration()
    else:
        if text == '1':
            return menu.home(_id)
        elif text == '1*1':
            return menu.transfer(_id)
# ===========================================
        elif text == '1*1*1':
            return menu.unavailable(_id)
        elif text == '1*1*2':
            return menu.unavailable(_id)
        elif text == '1*1*3':
            return menu.unavailable(_id)
        elif text == '1*1*4':
            return menu.unavailable(_id)
        elif text == '1*1*5':
            return menu.unavailable(_id)
        elif text == '1*1*6':
            return menu.unavailable(_id)
        elif text == '1*1*7':
            return menu.unavailable(_id)
# ===========================================
        elif text == '1*2':
            return menu.withdrawal(_id)
        elif text == '1*2*1':
            return menu.unavailable(_id)
        elif text == '1*2*2':
            return menu.unavailable(_id)            
# ===========================================
        elif text == '1*3':
            return menu.payment(_id)
        elif text == '1*3*1':
            return menu.unavailable(_id)
        elif text == '1*3*2':
            return menu.unavailable(_id)
        elif text == '1*3*3':
            return menu.unavailable(_id)
# ===========================================
        elif text == '1*4':
            return menu.my_bank(_id)
        elif text == '1*4*1':
            return menu.unavailable(_id)
        elif text == '1*4*2':
            return menu.unavailable(_id)
        elif text == '1*4*3':
            return menu.unavailable(_id)
# ===========================================
        else:
            return 'simple response'

# creating application port.
if __name__ == '__main__':
    # run application on localhost, using port stored as PORT in env variables.
    app.run(host="0.0.0.0", port=os.environ.get('PORT'))