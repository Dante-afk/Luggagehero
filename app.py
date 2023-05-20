from flask import Flask, render_template, request, session, url_for, redirect
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from flask_bcrypt import Bcrypt
import os
from datetime import date
from datetime import datetime
import time

app = Flask(__name__)
app.secret_key = "super secret key"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'myluggage'
app.config['UPLOAD_FOLDER'] = 'static/'


db = MySQL(app)

obj_bcrpt = Bcrypt(app)

@app.route('/', methods = ['GET', 'POST'])
def home():
    if request.method == 'POST' and 'location' in request.form :
        location = request.form['location']
        session['location'] = location
        date = request.form['date']
        session['date'] = date
        print(session['userid'])
        return redirect(url_for('index'))

    return render_template('home.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    #checking if proper post request with all credientials
    if request.method == "POST" and "useremail" in request.form and "password" in request.form:
        useremail = request.form['useremail']
        password = request.form['password']

        # connecting with database
        cursor = db.connection.cursor()
        cursor.execute('''SELECT * FROM User WHERE userEmail = %s''', [useremail])
        account = cursor.fetchone()
        cursor.close()

        # check is the account with credientials given is exist or not
        if(account):
            if(obj_bcrpt.check_password_hash(account[3], password)):
                session['userName'] = account[1]
                session['userid'] = account[0]
                print(session['userid'])
                return render_template("home.html", userName = session['userName']) 
        
    return render_template("login.html")

@app.route('/profile')
def profile():
    render_template("home.html")

@app.route('/register', methods = ['GET', 'POST'])
def register():
    msg = "" 
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form and 'username' in request.form and "userphone" in request.form and "useraddress" in request.form :
        userName = request.form['username']
        userPhone = request.form['userphone']
        userEmail = request.form['email'] 
        userPassword = request.form['password']
        confirmPassword = request.form['confirmpassword']
        hashPassword = obj_bcrpt.generate_password_hash(userPassword)
        userAddress = request.form['useraddress']

        # connecting to database
        cursor = db.connection.cursor()
        cursor.execute(''' SELECT * FROM User WHERE userEmail = %s AND userPhone = %s''', (userEmail, userPhone))
        account = cursor.fetchone()
        
        # checking whether there exist account with the given credientials
        if account:
            msg = "Account Already Exist"
        elif not re.match(r"[A-Za-z0-9]+", userName):
            msg = "Username must contain only characters and numbers !"
        elif userPassword != confirmPassword:
            msg = "Please Confirm your Password !"
        elif not userName or not userPassword or not userEmail or not userAddress:
            msg = "please Fill all the necessary field !"
        else:
            cursor.execute(''' INSERT INTO User VALUES (NULL, %s, %s, %s, %s, %s)''', (userName, userEmail, hashPassword, userPhone, userAddress))
            db.connection.commit()
            cursor.close()
            session['userName'] = userName
            return render_template("home.html", userName = session['userName'])
        ## otp fill karwana he successfully registration ke baad
    elif request.method == "POST":
        msg = "Please Fill out form! For getting a better experince"
        return render_template("register.html", msg = msg)
    
    else:
        return render_template("register.html")

@app.route('/index')
def index():
    if request.method == 'POST' :
        print("index page se city name lena he")
    else :
        location = session.get('location')
        city = "%"+location+"%"
        
        cursor = db.connection.cursor()
        cursor.execute(" SELECT * FROM store WHERE store.City LIKE %s", [city])  
        store_list = cursor.fetchall()
        
        store_phone = []

        for data in store_list:
            ownerid = data[1]
            cursor.execute(''' SELECT storeKeeperPhone FROM storeowner WHERE storeOwnerId = %s ''', [ownerid])
            store_phone.append(cursor.fetchone())

        db_store = []
        for data in store_list:
            data = list(data)
            db_store.append(data)
        
        for i in range(len(db_store)):
            db_store[i].append(store_phone[i][0])
            print(db_store[i])
            
        # for i in range(len(store_list)):
        #     db_store.append(list(store_list[i]))
        # for i in range(len(db_store)):
        #     for j in range(2,9):
        #         db_store[i][j] = str(db_store[i][j])
        
        # for i in db_store:
        #     print(i)


    return render_template('index.html', store = db_store)

@app.route('/store', methods = ['GET', 'POST'])
def store_registration():
    print("store_regestration backend!!")
    if request.method == 'POST' and 'email' in request.form and 'bussinessaddress' in request.form:

        print("Form Reached Backend")
        # Here, we are going to store all the data given by store keeper into our database

        # storeowner table data
        storeKeeperName = request.form['shopkeepername']
        storeKeeperPhone = request.form['shopkeeperphone']
        storeKeeperEmail = request.form['email']
        password = request.form['password']
        hash_password = obj_bcrpt.generate_password_hash(password)


        # store table data
        storename = request.form['bussinessname']
        storetype = request.form['bussinesstype']
        storeaddress = request.form['bussinessaddress']
        storecity = request.form['city']
        storecountry = request.form['country']
        storestate = request.form['state']
        storepincode = int(request.form['pincode'])
        store_longi = float(request.form['Longitude'])
        store_lati = float(request.form['Latitude'])
        # store_photo = request.files['image']

        #print(store_photo.filename)
        # store_photo.save(os.path.join(app.config['UPLOAD_FOLDER'], store_photo.filename))
        cursor = db.connection.cursor()
        cursor.execute(''' INSERT INTO storeowner VALUES(NULL, %s, %s, %s, %s) ''', (storeKeeperName, storeKeeperPhone, storeKeeperEmail, hash_password))
        db.connection.commit()
        cursor.close()
        # # storeing the store details into database
        # # store_owner = StoreOwner(storeKeeperName = storeKeeperName, storeKeeperPhone = storeKeeperPhone, storeKeeperEmail = storeKeeperEmail, Password = hash_password)
        # # db.session.add(store_owner)
        # # db.session.commit()
        
        cursor = db.connection.cursor()
        cursor.execute(''' SELECT storeOwnerId FROM storeowner WHERE storeKeeperEmail = %s AND Password = %s ''', (storeKeeperEmail, hash_password))
        storeOwnerId = cursor.fetchone()
        
        # # store_ownerdetails = StoreOwner.query.filter_by(storeKeeperEmail = storeKeeperEmail, Password = hash_password)
        # # storeOwnerId = store_ownerdetails.storeOwnerId
        print(storeOwnerId[0], storeKeeperName, storeKeeperPhone, storeKeeperEmail, store_lati, store_longi, storeaddress, storecountry, storecity)

        cursor.execute(''' INSERT INTO store VALUES(NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ''', (storeOwnerId, storename, storetype, "NULL", storeaddress, storecity, storestate, storecountry, storepincode, store_longi, store_lati))
        db.connection.commit()

        # # store = Store(storeOwnerId = storeOwnerId, storeName = storename, storeType = storetype, storeAddress = storeaddress, City = storecity, State = storestate, Country = storecountry, Pincode = storepincode, Longitude = store_longi, Latitude = store_lati)
        # # db.session.add(store)
        # # db.session.commit()
        cursor.close()
        
    return render_template("store.html")

@app.route("/booking", methods = ['POST', 'GET'])
def storebooking():
    store_name = ""
    if request.method == 'POST' and 'storeId' in request.form :
        storeid = request.form['storeId']
        session['storeId'] = storeid
        cursor = db.connection.cursor()
        cursor.execute(''' SELECT storeName FROM store WHERE storeId = %s ''', (storeid))
        store_name = cursor.fetchone()
        cursor.close()
        print(session['userid'])

        # session['bagCount'] = bagCount
        # session['orderDuration'] = orderDuration
        # session['bookingdate'] = bookingdate
        # session['orderdate'] = orderdate
        # session['billAmount'] = billAmount
        # print("data reached backend")

    return render_template("booking.html", storename = store_name)

@app.route("/invoice", methods = ['POST', 'GET'])
def invoice():
    if request.method == 'POST' and 'bag_Count' in request.form and 'day_Count' in request.form and 'date' in request.form :
        userId = session['userid']
        storeId = int(session['storeId'])
        bagCount = int(request.form['bag_Count'])
        orderDuration = int(request.form['day_Count'])
        bookingdate = request.form['date']
        print(bookingdate)
        print(type(bookingdate))
        orderdate = str(date.today())
        print(orderdate)
        print(type(orderdate))
        billAmount = int(bagCount) * int(orderDuration) * 80
        
        cursor = db.connection.cursor()
        cursor.execute('''INSERT INTO `Order` VALUES (NULL,%s,%s,%s,%s,%s,%s,%s)''', (userId,storeId,bagCount,orderDuration,orderdate,bookingdate,billAmount))
        db.connection.commit()
        
        cursor.execute(''' SELECT storeName FROM store WHERE storeId = %s ''', (session['storeId']))
        store_Name = cursor.fetchone()
        
        cursor.execute(''' SELECT Order_ID FROM `order` WHERE storeId = %s ''', (session['storeId']))
        order_Id = cursor.fetchone()

        cursor.close()

        bill = {
            "billed" : session['userName'],
            "Date" : bookingdate,
            "OrderId" : order_Id,
            "Unit" : bagCount,
            "Days" : orderDuration,
            "billAmount" : billAmount
        }
        print(store_Name)
        print(order_Id)

    return render_template("invoice.html", bill = bill)

@app.route('/payment')
def payment():
    return render_template("payment.html")


if __name__ == "__main__" :
    app.run(debug = True)