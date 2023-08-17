# Import Flask Library
import pypyodbc as odbc

from flask import Flask, render_template, request, session, url_for, redirect, flash

# Initialize the app from Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = '114514'

# Configure MySQL
DRIVER_NAME='SQL SERVER'
SERVER_NAME='DESKTOP-WOOO\SQLEXPRESS'
DATABASE_NAME='airlinedb'
 
connection_string = f"""
DRIVER={{{DRIVER_NAME}}};
SERVER={SERVER_NAME};
DATABASE={DATABASE_NAME};
Trust_Connection-yes;
"""

conn = odbc.connect(connection_string)


@app.route('/')
def hello():
    error = request.args.get('error')
    return render_template('index.html', error=error)


# Define route to login
@app.route('/login')
def login():
    return render_template('login.html')


def check_permission(username):
    cursor = conn.cursor()
    query = "SELECT * FROM permission WHERE username = '%s' and permission_type = 'admin'"
    cursor.execute(query % username)
    return bool(cursor.fetchone())


# Authenticate the login
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
    # grabs information from the forms
    username = request.form['username']
    password = request.form['password']
    usrtype = request.form['usrtype']

    # cursor used to send queries
    cursor = conn.cursor()

    if usrtype == 'customer':
        query = 'SELECT * FROM customer WHERE email = \'{}\' and password = \'{}\''
    elif usrtype == 'agent':
        query = 'SELECT * FROM booking_agent WHERE email = \'{}\' and password = \'{}\''
    elif usrtype == 'staff':
        query = 'SELECT * FROM airline_staff WHERE username = \'{}\' and password = \'{}\''

    cursor.execute(query.format(username, password))
    data = cursor.fetchone()
    cursor.close()
    error = None
    if (data):
        session['username'] = username
        session['usrtype'] = usrtype
        if usrtype == 'staff':
            # check permission
            session['admin'] = check_permission(username)
            return redirect(url_for('staffHome'))
        elif usrtype == 'customer':
            return redirect(url_for('homeCustomer'))
        else:
            return redirect(url_for('homeAgent'))
    else:
        error = 'Invalid login or username'
        return render_template('login.html', error=error)


# Define route for customer register
@app.route('/registerCustomer')
def registerCustomer():
    return render_template('registerCustomer.html')


# Authenticates the register for customer
@app.route('/registerAuthCustomer', methods=['GET', 'POST'])
def registerAuthCustomer():
    # grabs information from the forms
    username = request.form['username']
    name = request.form['name']
    password = request.form['password']
    building_number = request.form['Building_number']
    street = request.form['street']
    city = request.form['city']
    state = request.form['state']
    phone_number = request.form['phone_number']
    passport_number = request.form['passport_number']
    passport_expiration = request.form['passport_expiration']
    passport_country = request.form['passport_country']
    date_of_birth = request.form['date_of_birth']

    # cursor used to send queries
    cursor = conn.cursor()
    # executes query
    query = "SELECT * FROM customer WHERE email = \'{}\'"
    cursor.execute(query.format(name))
    # stores the results in a variable
    data = cursor.fetchone()
    # use fetchall() if you are expecting more than 1 data row
    error = None
    if (data):
        # If the previous query returns data, then user exists
        error = "This user already exists"
        return render_template('registerCustomer.html', error=error)
    else:
        ins = "INSERT INTO customer VALUES(\'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\')"
        cursor.execute(
            ins.format(username, name, password, building_number, street, city, state, phone_number, passport_number,
                       passport_expiration, passport_country, date_of_birth))
        conn.commit()
        cursor.close()
        flash("You are logged in")
        return render_template('index.html')


# Define route for booking agent register
@app.route('/registerAgent')
def registerAgent():
    return render_template('registerAgent.html')


# Authenticates the register for agent
@app.route('/registerAuthAgent', methods=['GET', 'POST'])
def registerAuthAgent():
    # grabs information from the forms
    email = request.form['username']
    password = request.form['password']
    booking_agent_id = request.form['booking_agent_id']

    # cursor used to send queries
    cursor = conn.cursor()
    # executes query
    query = "SELECT * FROM booking_agent WHERE email = \'{}\'"
    cursor.execute(query.format(email))
    # stores the results in a variable
    data = cursor.fetchone()
    # use fetchall() if you are expecting more than 1 data row
    error = None
    if (data):
        # If the previous query returns data, then user exists
        error = "This user already exists"
        return render_template('registerAgent.html', error=error)
    else:
        ins = "INSERT INTO booking_agent VALUES(\'{}\', \'{}\', \'{}\')"
        cursor.execute(ins.format(email, password, booking_agent_id))
        conn.commit()
        cursor.close()
        flash("You are logged in")
        return render_template('index.html')


# Define route for staff register
@app.route('/registerStaff')
def registerStaff():
    return render_template('registerStaff.html')


# Authenticates the register for staff
@app.route('/registerAuthStaff', methods=['GET', 'POST'])
def registerAuthStaff():
    # grabs information from the forms
    username = request.form['username']
    password = request.form['password']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    date_of_birth = request.form['date_of_birth']
    airline_name = request.form['airline_name']

    # cursor used to send queries
    cursor = conn.cursor()
    # executes query
    query = "SELECT * FROM airline_staff WHERE username = \'{}\'"
    cursor.execute(query.format(username))
    # stores the results in a variable
    data = cursor.fetchone()
    # use fetchall() if you are expecting more than 1 data row
    error = None
    if (data):
        # If the previous query returns data, then user exists
        error = "This user already exists"
        return render_template('registerStaff.html', error=error)
    else:
        ins = "INSERT INTO airline_staff VALUES(\'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\')"
        cursor.execute(ins.format(username, password, first_name, last_name, date_of_birth, airline_name))
        conn.commit()
        cursor.close()
        flash("You are logged in")
        return render_template('index.html')


# ------------------------------------------------------------------------------------------------------------
@app.route('/homeCustomer')
def homeCustomer():
    username = session['username']
    cursor = conn.cursor()
    query = 'SELECT purchases.ticket_id, ticket.airline_name, ticket.flight_num, departure_airport, departure_time, arrival_airport, arrival_time \
				FROM purchases, ticket, flight \
				WHERE purchases.ticket_id = ticket.ticket_id \
				AND ticket.airline_name = flight.airline_name \
				AND ticket.flight_num = flight.flight_num \
				AND customer_email = \'{}\' AND departure_time > CAST(GETDATE() AS DATE)'
    cursor.execute(query.format(username))
    data = cursor.fetchall()
    cursor.close()
    message = request.args.get('message')
    return render_template('homeCustomer.html', username=username, posts=data, message=message)



@app.route("/homeCustomer/purchasePageCustomer")
def purchasePageCustomer():
    return render_template('purchaseCustomer.html')


@app.route('/homeCustomer/purchaseCustomer', methods=['POST'])
def purchaseCustomer():
    cursor = conn.cursor()
    username = session['username']
    airline_name = request.form['airline_name']
    flight_num = request.form['flight_num']
    # generate ticket id
    queryCount = 'SELECT COUNT(*) as count FROM ticket'
    cursor.execute(queryCount)
    ticketCount = cursor.fetchone()
    ticket_id = ticketCount[0] + 1
    # Create the new ticket
    queryNewTicket = 'INSERT INTO ticket VALUES(\'{}\', \'{}\', \'{}\')'
    cursor.execute(queryNewTicket.format (ticket_id, airline_name, flight_num))
    conn.commit()
    # Finalize the purchase
    queryPurchase = 'INSERT INTO purchases VALUES(\'{}\' ,\'{}\',NULL,CAST(GETDATE() AS DATE))'
    cursor.execute(queryPurchase.format(ticket_id, username))
    conn.commit()
    cursor.close()
    return redirect(url_for('homeCustomer', message='Successfully Purchased a Ticket!'))





# ------------------------------------------------------------------------------------------------------------
@app.route('/homeAgent')
def homeAgent():
    username = session['username']
    cursor = conn.cursor()
    query = 'SELECT purchases.customer_email, purchases.ticket_id, ticket.airline_name, ticket.flight_num, departure_airport, departure_time, arrival_airport, arrival_time \
				FROM purchases, ticket, flight, booking_agent \
				WHERE purchases.ticket_id = ticket.ticket_id \
				AND ticket.airline_name = flight.airline_name \
				AND ticket.flight_num = flight.flight_num \
                AND booking_agent.booking_agent_id = purchases.booking_agent_id \
				AND booking_agent.email = \'{}\'\
				AND departure_time > CAST(GETDATE() AS DATE) \
				ORDER BY customer_email'
    cursor.execute(query.format(username))
    data = cursor.fetchall()
    cursor.close()
    message = request.args.get('message')
    return render_template('homeAgent.html', username=username, posts=data, message=message)



@app.route('/publicsearch')
def searchpage():
    error = request.args.get('error')
    return render_template('publicsearch.html', error=error)


@app.route('/searchresult/flight', methods=['POST'])
def searchUpcomingFlights():
    cursor = conn.cursor()
    searchtext1 = request.form['departurecity']
    searchtext2 = request.form['arrivalcity']
    searchtext3 = request.form['departuredate']
    query = 'select * from flight\
             where (departure_airport = \'{}\' \
                    or departure_airport in (select airport_name from airport where airport_city = \'{}\'))\
                    and (arrival_airport = \'{}\' \
                    or arrival_airport in (select airport_name from airport where airport_city = \'{}\' ))\
                    and convert(datetime,departure_time) = \'{}\' \
                    and status = \'Upcoming\' \
                    and (departure_time >= CAST(GETDATE() AS DATE)  or arrival_time >= CAST(GETDATE() AS DATE))'
    cursor.execute(query.format(searchtext1, searchtext1, searchtext2, searchtext2, searchtext3))
    data = cursor.fetchall()
    cursor.close()
    error = None
    if data:
        return render_template('searchresult.html', results=data)
    else:
        error = 'No results found'
        return redirect(url_for('hello', error=error))


@app.route('/searchresult/status', methods=['POST'])
def searchForStatus():
    flightnumber = request.form['flightnumberbox']
    doradate = request.form['doradate']

    cursor = conn.cursor()
    query = 'select airline_name,flight_num, status, departure_time, arrival_time from flight\
             where flight_num=\'{}\' \
             and (convert(datetime,departure_time)=\'{}\' or convert(datetime,arrival_time)=\'{}\' )\
             and (departure_time >= CAST(GETDATE() AS DATE) or arrival_time >= CAST(GETDATE() AS DATE))'
    cursor.execute(query.format(flightnumber, doradate, doradate))
    data = cursor.fetchall()
    print(data)
    cursor.close()
    error = None
    if data:
        return render_template('statusresult.html', results=data)
    else:
        error = 'No results found'
        return redirect(url_for('hello', error=error))


def staffvalidation():
    username = session.get('username')
    if not username:
        return False

    cursor = conn.cursor()
    query = 'select * from airline_staff where username= \'{}\' '
    cursor.execute(query.format(username))
    data = cursor.fetchall()
    cursor.close()
    if data:
        return True
    else:
        # Logout before returning error message
        session.pop('username')
        return False


def staffairline():
    username = session['username']
    cursor = conn.cursor()
    query = 'select airline_name from airline_staff where username = \'{}\' '
    cursor.execute(query.format(username))
    # fetchall returns an array, each element is a dictionary
    airline = cursor.fetchone()[0]
    cursor.close()

    return airline

@app.route('/staffHome')
def staffHome():
    if staffvalidation():
        username = session['username']
        cursor = conn.cursor()
        airline = staffairline()
        query = 'select * from flight where airline_name = \'{}\' \
                 and status = \'Upcoming\' \
                 and ((departure_time between CAST(GETDATE() AS DATE)  and DATEADD(day,30,CAST(GETDATE() AS DATE))) or (arrival_time between CAST(GETDATE() AS DATE) and DATEADD(day,30,CAST(GETDATE() AS DATE))))'
        # and departure_time between "2020-12-12" and "2021-01-12"'
        cursor.execute(query.format(airline))
        data = cursor.fetchall()
        cursor.close()

        error = request.args.get('error')
        message2 = request.args.get('message2')
        return render_template('staffsearchflight.html', username=username, error=error, results=data,
                               message2=message2, message='Upcoming flights for the next 30 days:')
    else:
        error = 'Invalid credentials, please login again!!'
        return redirect(url_for('hello', error=error))



@app.route('/staffHome/addAirplane')
def addairplane():
    if staffvalidation():
        error = request.args.get('error')
        return render_template('addairplane.html', error=error)
    else:
        error = 'Invalid credentials, please login again!!'
        return redirect(url_for('hello', error=error))


@app.route('/staffHome/addAirplane/confirmation', methods=['POST'])
def addairplaneconfirm():
    if staffvalidation():
        cursor = conn.cursor()
        airplaneid = request.form['id']
        seats = request.form['seats']
        airline = staffairline()

        query = 'select * from airplane where airplane_id = \'{}\' '
        cursor.execute(query.format (airplaneid))
        data = cursor.fetchall()

        if data:
            return redirect(url_for('addairplane', error='This airplane already existed'))

        query1 = 'insert into airplane values (\'{}\', \'{}\', \'{}\')'
        cursor.execute(query1.format (airline, airplaneid, seats))
        conn.commit()

        query2 = 'select * from airplane where airline_name =\'{}\''
        cursor.execute(query2.format (airline))
        data = cursor.fetchall()
        cursor.close()
        flash('Successfully add!')
        return render_template('addairplaneresult.html', results=data)
    else:
        error = 'Invalid credentials, please login again!!'
        return redirect(url_for('hello', error=error))


@app.route('/staffHome/addAirport')
def addairport():
    if staffvalidation():
        error = request.args.get('error')
        return render_template('addairport.html', error=error)
    else:
        error = 'Invalid credentials, please login again!!'
        return redirect(url_for('hello', error=error))


@app.route('/staffHome/addAirport/confirmation', methods=['POST'])
def addairportconfirm():
    if staffvalidation():
        cursor = conn.cursor()
        airport = request.form['airport']
        city = request.form['city']

        query = 'select * from airport where airport_name = \'{}\''
        cursor.execute(query.format(airport))
        data = cursor.fetchall()

        if data:
            return redirect(url_for('addairport', error='This airport already existed'))

        query1 = 'insert into airport values (\'{}\', \'{}\')'
        cursor.execute(query1.format(airport, city))
        conn.commit()
        cursor.close()

        flash('Successfully add!')
        return redirect(url_for('staffHome', message2='Successfully add an airport!'))
    else:
        error = 'Invalid credentials, please login again!!'
        return redirect(url_for('hello', error=error))





@app.route('/AddAuthAgent')
def AddAuthAgent():
    return render_template('AddAuthAgent.html')


@app.route('/logout')
def logout():
    session.pop('username')
    return redirect('/login')


if __name__ == "__main__":
    app.run( )

