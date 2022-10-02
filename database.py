import flask
import os
from flask import Flask, request, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from flask_migrate import Migrate

# initialize the flask app
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:''@127.0.0.1:3306/lapd'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

migrate = Migrate()
migrate.init_app(app, db)


class student(db.Model):
    Reg_No = db.Column(db.String(20), primary_key=True)
    Name = db.Column(db.String(100), nullable=False)
    Academic_year = db.Column(db.Integer(), db.ForeignKey('year.Year_of_study'), nullable=False)


class year(db.Model):
    Reg_No = db.Column(db.String(20), primary_key=True)
    Year_of_study = db.Column(db.Integer(), nullable=False)
    Semester = db.Column(db.Integer(), nullable=False)
    Academic_year = db.Column(db.Integer(), nullable=False)


class results(db.Model):
    unit_code = db.Column(db.String(20), primary_key=True)
    unit_title = db.Column(db.String(100), db.ForeignKey('units.unit_title'), nullable=False)
    Grade = db.Column(db.String(10), nullable=False)
    Reg_No = db.Column(db.String(20), db.ForeignKey('student.Reg_No'), nullable=False)
    units = db.relationship('units', backref='results_lookup', lazy=True)


class fees(db.Model):
    Reg_No = db.Column(db.String(20), primary_key=True)
    Name = db.Column(db.String(100), db.ForeignKey('student.Name'), nullable=False)
    Total_billed = db.Column(db.Integer(), nullable=False)
    Total_paid = db.Column(db.Integer(), nullable=False)
    Balance = db.Column(db.Integer(), nullable=False)
    student = db.relationship('Student', backref='fees_lookup', lazy=True)


class units(db.Model):
    unit_code = db.Column(db.String(20), primary_key=True)
    unit_title = db.Column(db.String(100), nullable=False)
    Year_of_study = db.Column(db.Integer(), db.ForeignKey('year.Year_of_study'), nullable=False)
    Semester = db.Column(db.Integer(), db.ForeignKey('year.Semester'), nullable=False)


class unit_registration(db.Model):
    unit_code = db.Column(db.String(20), primary_key=True)
    unit_title = db.Column(db.String(100), db.ForeignKey('units.unit_title'), nullable=False)
    Reg_No = db.Column(db.String(20), db.ForeignKey('student.Reg_No'), nullable=False)
    Name = db.Column(db.String(100), db.ForeignKey('student.Name'), nullable=False)
    units = db.relationship('units', backref='Registration_lookup', lazy=True)


def get_request():
    req = request.get_json(force=True)
    return req

def get_action():
    action = get_request().get('queryResult').get('action')
    return action


# default route
@app.route('/')
# function for responses
def results():
    # build a request object
    req = request.get_json(force=True)

    # fetch action from json
    action = req.get('queryResult').get('action')
    print(req)

    # return a fulfillment response
    return {
        'fulfillmentText': 'We received your request. please wait as it processes'
    }



def show_units():
    fees = Fees.query.filter_by(Reg_No).first()
    Total_paid = fees.Total_paid
    Balance = fees.Balance

    if fees == 'balance':

        response = Balance

    elif fees == 'paid':

        response = Total_paid

    else:

        response = f'Balance:{Balance} and  Total paid:{Total_paid}'



# create a route for webhook
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    # return response
    return make_response(jsonify(results()))


# run the app
if __name__ == '__main__':
    db.create_all()