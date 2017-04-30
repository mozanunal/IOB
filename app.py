from flask import Flask, render_template, redirect, jsonify, session, url_for
from flask.globals import request
from flask_mysqldb import MySQL
import pyowm, json, os, time



## config
app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'admin'
app.config['MYSQL_PASSWORD'] = '1a8d1617ae69a5ece240e42cdd0bdc3494f2a7e8d0202bd6'
app.config['MYSQL_DB'] = 'iob'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

OWM_Key = '98dbc45494eae862db0ce92a2fc87e09'

mysql = MySQL()
mysql.init_app(app)

####Classes

class device:
    def __init__(self):
        print "new device"

class user:
    def __init__(self):
        print "new user"



############Pages####################3

#User
@app.route("/")
def index():
    if 'userUUID' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT name, surName, email, userType FROM user WHERE userUUID = '{}' ".format(session['userUUID']))
        userInfo = cur.fetchone()
        return render_template('user.html', userInfo=userInfo)
    else:
        return render_template('login.html')

#device
@app.route("/device", methods=['GET'])
def device():
    if 'userUUID' in session:
        cur = mysql.connection.cursor()
        #get users device
        cur.execute("SELECT deviceId FROM user_device WHERE userId = '{}' ".format(session['id']))
        device = cur.fetchone()
        # get device data
        sql1 ='''select keyName, value from log 
        where id in (SELECT Max(id) as id 
        FROM log
        use index(xxcc) 
        Where device = {}
        GROUP BY keyName)'''.format(device['deviceId'])
        cur.execute(sql1)
        devicesInfo = cur.fetchall()
        labels = ["8:00","9:00","10:00","11:00","12:00","13:00","14:00","15:00","16:00","17:00"]
        values = [6,9,8,10,6,4,7,2,5,4]
        labels2 = ["ReceivedUV", "Normal", "Danger"]
        values2 = [80,70,20]
        colors2 = [ "#FDB45C", "#46BFBD","#F7464A" ]
        return render_template('device.html', devicesInfo = devicesInfo, values=values, labels=labels, set=zip(values2, labels2, colors2))
    else:
        return render_template('login.html')


#beaches
@app.route("/beaches", methods=['GET'])
def beaches():
    if 'userUUID' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, UUID, name, latitude, longitude FROM beach ")
        beaches = cur.fetchall()
        return render_template('beaches.html', beaches=beaches)
    else:
        return render_template('login.html')

@app.route("/beach/<UUID>", methods=['GET'])
def beach(UUID):
    if 'userUUID' in session:
        return render_template('beach.html')
    else:
        return render_template('login.html')

#beaches
@app.route("/beach/<UUID>/we", methods=['GET'])
def beach_we(UUID):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name, latitude, longitude FROM beach WHERE UUID = '{}' ".format(UUID))
    beach = cur.fetchone()
    latitude = beach['latitude']
    longitude = beach['longitude']
    owm = pyowm.OWM('98dbc45494eae862db0ce92a2fc87e09')
    weather = owm.weather_at_coords(latitude,longitude)
    data = json.loads( weather.to_JSON())
    #data['ozone']=owm.ozone_around_coords(latitude,longitude).get_du_value()
    data['latitude'] = latitude
    data['longitude'] = longitude
    data['name'] = beach['name']
    return jsonify(data)

#beaches
@app.route("/beach/<UUID>/uv", methods=['GET'])
def beach_uv(UUID):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name, latitude, longitude FROM beach WHERE UUID = '{}' ".format(UUID))
    beach = cur.fetchone()
    latitude = beach['latitude']
    longitude = beach['longitude']
    owm = pyowm.OWM('98dbc45494eae862db0ce92a2fc87e09')
    print latitude,longitude, "9999999999999999999999999999999"
    uv = owm.uvindex_around_coords(latitude,longitude)
    print uv.to_JSON()
    return str(uv)

############Actions####################3

@app.route("/login", methods=['POST'])
def login():
    cur = mysql.connection.cursor()
    sql = "SELECT id,userUUID FROM user WHERE username = '{}' AND password = '{}' ".format(request.form['username'], request.form['password'])
    cur.execute(sql)
    row = cur.fetchone()
    if row is not None:
        session['userUUID'] = row.get('userUUID')
        session['id'] = row.get('id')
        session['logged_in'] = True
        return redirect(url_for('index'))
    else: 
        session.pop('userUUID', None)
        session.pop('id', None)
        session['logged_in'] = False
        return render_template("login.html", message = 'wrong password!')


@app.route("/logout", methods=['GET'])
def logout():
    session.pop('userUUID', None)
    session.pop('userid', None)
    return redirect(url_for('index'))


############Rest Api####################

@app.route("/rest", methods=['POST'])
def rest():
    content = request.json
    UUID = content.get('UUID') 
    dataArr = content.get('data') 
    for data in dataArr:
        print "****",data[0],data[1]
    print UUID
    return "Success"


################################################################





@app.route("/chart")
def chart():
    labels2 = ["ReceivedUV", "Normal", "Danger"]
    values2 = [80,70,20]
    colors2 = [ "#FDB45C", "#46BFBD","#F7464A" ]
    return render_template('chart.html', set=zip(values2, labels2, colors2))


#main
if __name__ == "__main__":
    app.secret_key = os.urandom(24)
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
