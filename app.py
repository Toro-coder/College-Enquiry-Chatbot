
import flask
import os
from flask import Flask, request, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from flask_migrate import Migrate
from socket import gethostname
from datetime import datetime

# initialize the flask app
app = Flask(__name__)

app.config[
    'SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://Toroitich:toro1648@Toroitich.mysql.pythonanywhere-services.com/Toroitich$College'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

migrate = Migrate()
migrate.init_app(app, db)


class Notices(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.String(20), nullable=False)
    notice = db.Column(db.String(500), nullable= False)

class Student(db.Model):
    Reg_No = db.Column(db.String(20), primary_key=True)
    Name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(20), nullable=False)
    unit_registration = db.relationship('Unit_registration', backref='units_reg', lazy=True)


class Unit_registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unit_code = db.Column(db.String(20), db.ForeignKey('units.unit_code'), nullable=False)
    Reg_No = db.Column(db.String(20), db.ForeignKey('student.Reg_No'), nullable=False)
    academic_year = db.Column(db.String(20), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    Results = db.relationship('Results', backref='unit', lazy=True)


class Units(db.Model):
    unit_code = db.Column(db.String(20), primary_key=True)
    unit_title = db.Column(db.String(100), nullable=False)
    Sem = db.Column(db.String(20), nullable=False)
    year_of_study = db.Column(db.Integer, nullable=False)
    unit_registration = db.relationship('Unit_registration', backref='units', lazy=True)

class Results(db.Model):
    results_id = db.Column(db.Integer, primary_key=True)
    reg_id = db.Column(db.Integer, db.ForeignKey('unit_registration.id'), nullable=False)
    Grade = db.Column(db.String(10), nullable=False)


class Fees(db.Model):
    receipt_no = db.Column(db.Integer, primary_key=True)
    Reg_No = db.Column(db.String(20), db.ForeignKey('student.Reg_No'), nullable=False)
    date_paid = db.Column(db.Date, nullable=False)
    Total_paid = db.Column(db.String(20), nullable=False)
    Balance = db.Column(db.String(20), nullable=False)
    student = db.relationship('Student', backref='fees', lazy=True)



# default route
@app.route('/')
def get_request():
    req = request.get_json(force=True)
    return req


def get_action():
    action = get_request().get('queryResult').get('action')

    return action


# function for responses
def results():
    # build a request object
    query_result = get_request().get('queryResult')

    # fetch action from json
    fee_request = query_result.get('parameters').get('fee_request')


    Reg_no = query_result.get('parameters').get('Reg_no')

    # return a fulfillment response
    return {
        'fulfillmentText': fee_request,
        "source": "webhookdata"
    }

def get_fees():
    query_result = get_request().get('queryResult')
    fee_request = query_result.get('parameters').get('fee_request')
    Reg_no = query_result.get('parameters').get('Reg_no')

    fees = Fees.query.filter_by(Reg_No=Reg_no).first()
    Total_paid = fees.Total_paid
    Balance = fees.Balance

    if fee_request == 'balance':

        response=f'fee balance is Ksh.{Balance}'

    elif fee_request == 'paid':

        response= f'Total amount paid is Ksh.{Total_paid}'

    else:

        response=f'Balance:Ksh.{Balance} and  Total paid:Ksh.{Total_paid}'


    return {
        'fulfillmentText':response,
        "source": "webhookdata"

    }

def notices():
    query_result = get_request().get('queryResult')
    date = query_result.get('parameters').get('date-time')

    notices =  Notices.query.filter_by(day=date).all()

    for i in notices:
        response = f'{i.day} activity is {i.notice}'


    return {
        'fulfillmentText': response,
        "source": "webhookdata"
        }

def get_units():
    query_result = get_request().get('queryResult')
    semester =  query_result.get('parameters').get('semester')
    year_study = query_result.get('parameters').get('years')

    if semester == 'all':
        units = Units.query.filter_by(year_of_study=year_study).all()
    else:
        units = Units.query.filter_by(year_of_study=year_study, Sem=semester).all()

    response = ''

    for unit in units:
        response = response + f"{unit.unit_code} {unit.unit_title}\n"


    return {
        'fulfillmentText': response,
        "source": "webhookdata"
        }

'''def get_results():
    query_result = get_request().get('queryResult')
    Reg_no =  query_result.get('parameters').get('reg_no')
    password= query_result.get('parameters').get('password')
    academic_year = query_result.get('parameters').get('academic_year')


    password_check = Student.query.filter_by(Reg_No=Reg_no, password=password).all()
    if password_check:
        #registered = Unit_registration.query.filter_by(Reg_No=Reg_no, academic_year=academic_year).all()
        results = Results.query.filter_by(reg_id=Reg_no).all()
        responce = ''
        for r in results:

            responce = responce + f'The results is{r.unit_code} {r.Grade}'


    return {
        'fulfillmentText': responce,
        "source": "webhookdata"

    }
'''

def register_units():
    query_result = get_request().get('queryResult')
    Reg_no =  query_result.get('parameters').get('Reg_no')
    units = query_result.get('parameters').get('units')
    password = query_result.get('parameters').get('password')
    academic_year = query_result.get('parameters').get('academic_year')

    password_check = Student.query.filter_by(Reg_No=Reg_no, password=password).all()
    unit_check = Unit_registration.query.filter_by(unit_code=units, Reg_No=Reg_no, academic_year=academic_year, semester=1).all()
    if unit_check:
        response = f'Already registered'

    else:
        if password_check:

            reg = Unit_registration(unit_code=units, Reg_No=Reg_no, academic_year=academic_year, semester=1)
            db.session.add(reg)
            db.session.commit()

            response=f'{units} Registered successfully'
        else:
            response = f'Wrong password regestration number combination Try again later'


    return {
        'fulfillmentText': response,
        "source": "webhookdata"

    }

def check_units():
    query_result = get_request().get('queryResult')
    Reg_no =  query_result.get('parameters').get('Reg_no')
    password= query_result.get('parameters').get('password')
    academic_year = query_result.get('parameters').get('academic_year')


    password_check = Student.query.filter_by(Reg_No=Reg_no, password=password).all()

    if password_check:
        registered = Unit_registration.query.filter_by(academic_year=academic_year).all()

        response = ''

        for i in registered:

            response = response + f"{i.unit_code}  "

    else:
        response = f'Wrong password regestration number combination Try again'

    return {
        'fulfillmentText': response,
        "source": "webhookdata"
    }

# create a route for webhook
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if get_action() == 'Get_fees':
        return make_response(jsonify(get_fees()))
    elif get_action() == 'Get_units':
        return make_response(jsonify(get_units()))
    elif get_action() == 'Get_notices':
        return make_response(jsonify(notices()))
    elif get_action() == 'results.results-yes':
        return make_response(jsonify(get_results()))
    elif get_action() == 'unit-registration-yes':
        return make_response(jsonify(register_units()))
    elif get_action() == 'Registered_units':
        return make_response(jsonify( check_units()))


# run the app
if __name__ == '__main__':
    db.create_all()
    if 'liveconsole' not in gethostname():
        app.run()
