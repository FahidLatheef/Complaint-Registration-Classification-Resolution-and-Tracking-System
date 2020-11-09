"""
Project: Complaint Management System Flask Webapp
Created by: Fahid Latheef A
Date created : 01-Nov-2020
Purpose:
To reduce the bottleneck and ease the registering and resolving of complaints
Features:
1. Online submission of complaints
2. Classify the complaints in different classes using a machine learning model
3. Storing the complaint data in SQL database
4. Generate an Customer-ID
5. Place where the product-admin can put up the solution to the complaint
6. Place for Customer to check and dispute the complaint
"""

from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import yaml
import model # model.py
import password # password.py
from datetime import date

# REST API service

app = Flask(__name__)


@app.route('/home', methods=['POST', 'GET'])
def home():
    print(url_for('home'))
    return render_template('home.html')


# Configure db
db = yaml.load(open('db.yaml'), Loader=yaml.FullLoader)
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
# app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

mysql = MySQL(app)


@app.route('/')
def redirected():
    print(url_for('home'))
    return redirect(url_for('home'))


@app.route('/complaint_form', methods=['GET', 'POST'])
def complaint_form():
    print(url_for('complaint_form'))
    if request.method == 'POST':
        # Fetch form data
        user_details = request.form
        name = user_details['Name']
        email = user_details['Email']
        date_today = date.today().strftime("%Y-%m-%d")
        issue = user_details['Issue']
        sub_issue = user_details['Sub-issue']
        narrative = user_details['Consumer complaint narrative']
        product = model.prediction_category([model.preprocessing(issue, sub_issue, narrative)])[0]
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO users(Name, Email, `Date received`, Issue, `Sub-issue`, `Consumer complaint narrative`, Product) VALUES(%s,%s,%s,%s,%s,%s,%s)",
            (name, email, date_today, issue, sub_issue, narrative, product))
        mysql.connection.commit()

        model.send_the_email(recipient='your_email@gmail.com',
                             subject='A new complaint registered under the category: {}'.format(product),
                             body='Hi, \nHope you are doing well. There has been a new complaint in your category: {}'.format(
                                 product) + '\nHave a nice day.\n\nThanks and Regards,\nXXXCRP.')

        cur.execute(
            "SELECT * FROM users ORDER BY Id DESC LIMIT 1"
        )
        user_details = cur.fetchall()
        cur.close()

        return render_template('thank_you.html', user_details=user_details)
    return render_template('complaint_form.html')


# secret key is needed for session
app.secret_key = 'dljsaklqk24e21cjn!Ew@@dsa5'


# Route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    print(url_for('login'))
    error = None
    if request.method == 'POST':
        user = request.form['username']
        passcode = request.form['password']
        merged_credentials = [user, passcode]
        session["user"] = user
        session["cred"] = merged_credentials
        if merged_credentials not in password.user_credentials.values():
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect(url_for('category_assistant'))
    return render_template('login.html', error=error)


@app.route('/category_assistant', methods=['GET', 'POST'])
def category_assistant():
    print(url_for('category_assistant'))
    if request.method == 'GET':
        user = session.get("user", None)
        for key, value in password.user_credentials.items():
            if session.get("cred", None) == value:
                product = key
        cur = mysql.connection.cursor()
        value = cur.execute(
            "SELECT * FROM users WHERE (Product = '{}' AND `Response narrative` IS NULL) ORDER BY Id LIMIT 1".format(
                product))
        if value > 0:
            user_details = cur.fetchall()
            cur.close()
            return render_template('category_assistant.html', user=user, user_details=user_details, product=product)
        else:
            return render_template('no_complaints.html', user=user, product=product)
    elif request.method == 'POST':
        response_ = request.form['resolution']
        mail = request.form['Email']
        id_ = request.form['Id']
        date_today = date.today().strftime("%Y-%m-%d")
        cur = mysql.connection.cursor()
        cur.execute(
            """UPDATE users
            SET `Response narrative` = %s,
                `Date of response` = %s
            WHERE `Id` = %s""", (response_, date_today, id_)
        )
        mysql.connection.commit()
        cur.close()
        model.send_the_email(recipient=mail,
                             subject="An update to your Complaint registered at XXX Complaint Registration Platform",
                             body="""Hi,\nThanks for registering the complaint in our platform. 
                             \nWe have updated your status of your complaint. Check it here at <a href="http://127.0.0.1:5000/complaint_status">this link.</a>""")
        return redirect('/category_assistant')


@app.route('/complaint_status', methods=['GET', 'POST'])
def complaint_status():
    print(url_for('complaint_status'))
    error = None
    if request.method == 'POST':
        id_ = request.form['Id']
        mail = request.form['Email']
        cur = mysql.connection.cursor()
        value = cur.execute(
            """SELECT * FROM users 
            WHERE Id = %s AND Email = %s""", (id_, mail)
        )
        if value == 0:
            error = 'No complaints found!!!'
            return render_template('complaint_status.html', error=error)
        else:
            value2 = cur.execute(
                """SELECT * FROM users 
            WHERE Id = %s AND Email = %s AND `Response narrative` IS NOT NULL""", (id_, mail)
            )
            mysql.connection.commit()
            if value2 == 0:
                error = 'No response yet!!!'
                return render_template('complaint_status.html', error=error)
            else:
                details = cur.fetchall()
                cur.close()
                return render_template('response.html', details=details, id_=id_)
    return render_template('complaint_status.html', error=error)


@app.route('/final', methods=['GET', 'POST'])
def final():
    if request.method == 'POST':
        print('/final')
        satisfy = request.form['response']
        id_ = request.form['id']
        dispute = 'No'
        if satisfy == 'No':
            dispute = 'Yes'
        cur = mysql.connection.cursor()
        cur.execute(
            """UPDATE users
            SET `Consumer disputed?` = %s
            WHERE `Id` = %s""", (dispute, id_)
        )
        mysql.connection.commit()
        cur.close()
        return redirect('/home')


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
