from datetime import date, timedelta
from flask import Flask, render_template, request, redirect, url_for, session
from functools import wraps
from flask_mysqldb import MySQL

app = Flask(__name__)
app.debug = True


app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Swe21tha07$'
app.config['MYSQL_DB'] = 'bloodbank'

app.secret_key = 'super_secret_blood_bank_key'

mysql = MySQL(app)



def check_eligibility(last_date):
    today = date.today()
    if last_date is None:
        return "Eligible"
    if isinstance(last_date, str):
        last_date = date.fromisoformat(last_date)

    return "Eligible" if (today - last_date).days >= 90 else "Not Eligible"


def build_donors_with_status(donors_list):
    """Build donor list with eligibility status for rendering"""
    donors_with_status = []
    today = date.today()
    
    for donor in donors_list:
        try:
            donorid, name, age, gender, bloodgroup, lastdate, units, phone = donor
        except (ValueError, TypeError):
            continue
        
        if lastdate is None or lastdate == '' or lastdate == '0000-00-00':
            status = "✓ First-time donor"
            eligible = True
        else:
            if isinstance(lastdate, str):
                try:
                    lastdate_obj = date.fromisoformat(lastdate)
                except ValueError:
                    status = "Invalid date"
                    eligible = False
                    donors_with_status.append((donor, status, eligible))
                    continue
            else:
                lastdate_obj = lastdate
            
            days_since = (today - lastdate_obj).days
            if days_since >= 90:
                status = "✓ Eligible now"
                eligible = True
            else:
                status = f"✗ Not eligible ({90 - days_since} days left)"
                eligible = False
        
        donors_with_status.append((donor, status, eligible))
    
    return donors_with_status


def update_stock(bloodgroup, units, mode):
    cur = mysql.connection.cursor()

    if mode == "ADD":
        cur.execute("""
            UPDATE bloodstock 
            SET unitsavailable = unitsavailable + %s
            WHERE bloodgroup = %s
        """, (units, bloodgroup))

    elif mode == "SUB":
        cur.execute("""
            UPDATE bloodstock 
            SET unitsavailable = unitsavailable - %s
            WHERE bloodgroup = %s
        """, (units, bloodgroup))

    mysql.connection.commit()
    cur.close()


def add_expiry(bloodgroup, units, donation_date):
    expiry_date = donation_date + timedelta(days=35)
    cur = mysql.connection.cursor()

    cur.execute("""
        UPDATE bloodstock 
        SET expirydate=%s
        WHERE bloodgroup=%s
    """, (expiry_date, bloodgroup))

    mysql.connection.commit()
    cur.close()

def fulfill_pending_requests(bloodgroup):
    cur = mysql.connection.cursor()
    
    cur.execute("""
        SELECT requestid, units 
        FROM bloodrequest 
        WHERE bloodgroupreq=%s AND status='Not Available'
        ORDER BY requestid ASC
    """, (bloodgroup,))
    
    pending_requests = cur.fetchall()
    
    for req in pending_requests:
        req_id = req[0]
        req_units = req[1]
        
        cur.execute("SELECT unitsavailable FROM bloodstock WHERE bloodgroup=%s", (bloodgroup,))
        stock_row = cur.fetchone()
        
        if stock_row and int(stock_row[0]) >= int(req_units):
            cur.execute("""
                UPDATE bloodstock 
                SET unitsavailable = unitsavailable - %s 
                WHERE bloodgroup=%s
            """, (req_units, bloodgroup))
            
            cur.execute("""
                UPDATE bloodrequest 
                SET status='Available' 
                WHERE requestid=%s
            """, (req_id,))
            
    mysql.connection.commit()
    cur.close()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session or session['role'] != 'admin':
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin123':
            session['role'] = 'admin'
            session['username'] = 'Admin'
            return redirect(url_for('dashboard'))
        cur = mysql.connection.cursor()
        cur.execute("SELECT hospitalid, hospitalname FROM hospital WHERE username=%s AND password=%s", (username, password))
        hospital = cur.fetchone()
        cur.close()
        
        if hospital:
            session['role'] = 'hospital'
            session['hospitalid'] = hospital[0]
            session['hospitalname'] = hospital[1]
            return redirect(url_for('hospital_dashboard'))
            
        return render_template('login.html', error='Invalid credentials')
        
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        hospitalname = request.form['hospitalname']
        username = request.form['username']
        password = request.form['password']
        phone = request.form['phone']
        address = request.form['address']
        
        # Validate phone number (must be exactly 10 digits)
        if not phone or not phone.isdigit() or len(phone) != 10:
            return render_template('signup.html', error='Phone number must be exactly 10 digits (Indian standard).')
        
        # Validate address is not empty
        if not address or not address.strip():
            return render_template('signup.html', error='Address is required.')
        
        # Store phone with +91 prefix
        phone_with_code = f"+91{phone}"
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM hospital WHERE username=%s", (username,))
        if cur.fetchone():
            cur.close()
            return render_template('signup.html', error='Username already exists!')
            
        cur.execute("INSERT INTO hospital(hospitalname, username, password, phone, address) VALUES (%s, %s, %s, %s, %s)", 
                   (hospitalname, username, password, phone_with_code, address))
        mysql.connection.commit()
        cur.close()
        
        return redirect(url_for('login', message='Account created successfully! Please log in.'))
        
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
def index():
    if 'role' in session:
        if session['role'] == 'admin':
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('hospital_dashboard'))
    return redirect(url_for('login'))

@app.route('/donors')
@admin_required
def donors():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM donor")
    data = cur.fetchall()
    cur.close()
    
    donors_with_status = build_donors_with_status(data)
    
    return render_template('donors.html', donors_with_status=donors_with_status)


@app.route('/add', methods=['GET', 'POST'])
@admin_required
def add_donor():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        bloodgroup = request.form['bloodgroup'].strip().replace(" ", "").upper()
        lastdate = request.form['lastdonationdate']
        units = int(request.form['units'])
        phone = request.form['phone']
        
        # Validate phone number (must be exactly 10 digits)
        if not phone or not phone.isdigit() or len(phone) != 10:
            return render_template('adddonor.html', error='Phone number must be exactly 10 digits (Indian standard).')

        cur = mysql.connection.cursor()
        cur.execute("SELECT donorid, lastdonationdate FROM donor WHERE name=%s", (name,))
        existing_donor = cur.fetchone()

        if existing_donor:
            existing_last_date = existing_donor[1]
            if isinstance(existing_last_date, str) and existing_last_date:
                try:
                    existing_last_date = date.fromisoformat(existing_last_date)
                except ValueError:
                    pass
            
            if isinstance(existing_last_date, date):
                days_since = (date.today() - existing_last_date).days
                if days_since < 90:
                    error_msg = f"Donation Rejected: Donor '{name}' already exists and only {days_since} days have passed since their last donation on {existing_last_date} (90 days required)."
                    cur.close()
                    return render_template('adddonor.html', error=error_msg)
            
            error_msg = f"Donor '{name}' already exists! Please use the 'Record Donation' portal to add a new donation for this person instead of creating a duplicate."
            cur.close()
            return render_template('adddonor.html', error=error_msg)

        # Store phone with +91 prefix
        phone_with_code = f"+91{phone}"
        
        cur.execute("""
            INSERT INTO donor(name, age, gender, bloodgroup, lastdonationdate, units, phone)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (name, age, gender, bloodgroup, lastdate, units, phone_with_code))

        cur.execute("SELECT unitsavailable FROM bloodstock WHERE bloodgroup=%s", (bloodgroup,))
        existing = cur.fetchone()

        if existing:
            cur.execute("""
                UPDATE bloodstock 
                SET unitsavailable = unitsavailable + %s 
                WHERE bloodgroup=%s
            """, (units, bloodgroup))
        else:
            cur.execute("""
                INSERT INTO bloodstock (bloodgroup, unitsavailable)
                VALUES (%s, %s)
            """, (bloodgroup, units))

        mysql.connection.commit()
        cur.close()

        fulfill_pending_requests(bloodgroup)

        return redirect(url_for('donors'))

    return render_template('adddonor.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_donor(id):
    cur = mysql.connection.cursor()

    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        bloodgroup = request.form['bloodgroup'].replace(" ", "").upper()
        lastdate = request.form['lastdonationdate']
        phone = request.form['phone']
        
        # Validate phone number (must be exactly 10 digits)
        if not phone or not phone.isdigit() or len(phone) != 10:
            cur.close()
            return render_template('editdonor.html', error='Phone number must be exactly 10 digits (Indian standard).', donor=(0, name, age, gender, bloodgroup, lastdate, 0, phone))

        # Store phone with +91 prefix
        phone_with_code = f"+91{phone}"

        cur.execute("""
            UPDATE donor 
            SET name=%s, age=%s, gender=%s, bloodgroup=%s, lastdonationdate=%s, phone=%s
            WHERE donorid=%s
        """, (name, age, gender, bloodgroup, lastdate, phone_with_code, id))

        mysql.connection.commit()
        cur.close()

        return redirect(url_for('donors'))

    cur.execute("SELECT * FROM donor WHERE donorid=%s", (id,))
    data = cur.fetchone()
    cur.close()

    return render_template('editdonor.html', donor=data)

@app.route('/delete/<int:id>')
@admin_required
def delete_donor(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM donor WHERE donorid=%s", (id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('donors'))

@app.route('/bloodstock')
@admin_required
def bloodstock():
    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT stockid, bloodgroup, unitsavailable 
        FROM bloodstock 
        WHERE bloodgroup IS NOT NULL
        ORDER BY stockid
    """)

    data = cur.fetchall()

    cur.close()

    return render_template('bloodstock.html', stock=data)

@app.route('/hospitals')
@admin_required
def hospitals():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM hospital")
    data = cur.fetchall()
    cur.close()
    return render_template('hospitals.html', hospitals=data)


@app.route('/add_hospital', methods=['GET', 'POST'])
@admin_required
def add_hospital():
    if request.method == 'POST':
        name = request.form['hospitalname']
        username = request.form['username']
        password = request.form['password']
        phone = request.form['phone']
        address = request.form['address']
        
        # Validate phone number (must be exactly 10 digits)
        if not phone or not phone.isdigit() or len(phone) != 10:
            return render_template('addhospital.html', error='Phone number must be exactly 10 digits (Indian standard).')
        
        # Validate address is not empty
        if not address or not address.strip():
            return render_template('addhospital.html', error='Address is required.')
        
        # Store phone with +91 prefix
        phone_with_code = f"+91{phone}"

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO hospital(hospitalname, username, password, phone, address) VALUES (%s, %s, %s, %s, %s)", 
                   (name, username, password, phone_with_code, address))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('hospitals'))

    return render_template('addhospital.html')

@app.route('/requests')
@admin_required
def requests_page():
    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT br.requestid, br.bloodgroupreq, br.units, br.status, h.hospitalname, br.requestdate, br.stockid
        FROM bloodrequest br
        JOIN hospital h ON br.hospitalid = h.hospitalid
    """)
    data = cur.fetchall()

    cur.close()

    return render_template('requests.html', requests=data)

@app.route('/add_request', methods=['GET', 'POST'])
@login_required
def add_request():
    if session.get('role') != 'hospital':
        return redirect(url_for('dashboard'))

    hospitalid = session['hospitalid']
    
    cur = mysql.connection.cursor()

    if request.method == 'POST':
        bloodgroup = request.form['bloodgroup'].strip().replace(" ", "").upper()
        units = int(request.form['units'])

        cur.execute("SELECT stockid, unitsavailable FROM bloodstock WHERE bloodgroup=%s", (bloodgroup,))
        stock = cur.fetchone()

        stock_id = None
        if stock is not None and int(stock[1]) >= int(units):
            status = "Available"
            stock_id = stock[0]

            cur.execute("""
                UPDATE bloodstock 
                SET unitsavailable = unitsavailable - %s 
                WHERE bloodgroup=%s
            """, (units, bloodgroup))
        else:
            status = "Not Available"
            if stock is not None:
                stock_id = stock[0]

        cur.execute("""
            INSERT INTO bloodrequest (bloodgroupreq, units, requestdate, status, hospitalid, stockid)
            VALUES (%s, %s, CURDATE(), %s, %s, %s)
        """, (bloodgroup, units, status, hospitalid, stock_id))

        mysql.connection.commit()
        cur.close()

        return redirect(url_for('hospital_dashboard'))

    return render_template('addrequest.html')

@app.route('/hospital_dashboard')
@login_required
def hospital_dashboard():
    if session.get('role') != 'hospital':
        return redirect(url_for('dashboard'))
        
    cur = mysql.connection.cursor()
    cur.execute("SELECT requestid, bloodgroupreq, units, status, requestdate, stockid FROM bloodrequest WHERE hospitalid=%s", (session['hospitalid'],))
    data = cur.fetchall()
    cur.close()
    
    return render_template('hospital_dashboard.html', requests=data)

@app.route('/donate', methods=['GET', 'POST'])
@admin_required
def donate():
    if request.method == 'POST':
        try:
            donorid = request.form.get('donorid')
            bloodgroup = request.form.get('bloodgroup', '').strip().replace(" ", "").upper()
            units = int(request.form.get('units', 1))
            donation_date = date.today()
            if not donorid:
                cur = mysql.connection.cursor()
                cur.execute("SELECT * FROM donor")
                donors = cur.fetchall()
                cur.close()
                donors_with_status = build_donors_with_status(donors)
                return render_template('donate.html', donors_with_status=donors_with_status, error="Please select a donor.")
            if not bloodgroup:
                cur = mysql.connection.cursor()
                cur.execute("SELECT * FROM donor")
                donors = cur.fetchall()
                cur.close()
                donors_with_status = build_donors_with_status(donors)
                return render_template('donate.html', donors_with_status=donors_with_status, error="Please select a blood group.")
            if units > 1 or units < 1:
                cur = mysql.connection.cursor()
                cur.execute("SELECT * FROM donor")
                donors = cur.fetchall()
                cur.close()
                
                donors_with_status = build_donors_with_status(donors)
                error_msg = f"Donation Rejected: Maximum 1 unit allowed per donation. You entered {units} units."
                return render_template('donate.html', donors_with_status=donors_with_status, error=error_msg)
            cur = mysql.connection.cursor()
            cur.execute("SELECT name, lastdonationdate FROM donor WHERE donorid=%s", (donorid,))
            donor_data = cur.fetchone()
            
            if not donor_data:
                cur.close()
                cur = mysql.connection.cursor()
                cur.execute("SELECT * FROM donor")
                donors = cur.fetchall()
                cur.close()
                donors_with_status = build_donors_with_status(donors)
                return render_template('donate.html', donors_with_status=donors_with_status, error="Invalid donor selected.")
            
            donor_name = donor_data[0]
            last_date = donor_data[1]
            if last_date and last_date != '0000-00-00':
                if isinstance(last_date, str):
                    try:
                        last_date = date.fromisoformat(last_date)
                    except ValueError:
                        pass
                
                if isinstance(last_date, date):
                    days_since = (donation_date - last_date).days
                    if days_since < 90:
                        cur.close()
                        cur = mysql.connection.cursor()
                        cur.execute("SELECT * FROM donor")
                        donors = cur.fetchall()
                        cur.close()
                        
                        next_eligible_date = last_date + timedelta(days=90)
                        error_msg = f"Donation Rejected: {donor_name} is not medically eligible yet. Only {days_since} days have passed since their last donation on {last_date}. They will be eligible again on {next_eligible_date} (90 days required)."
                        donors_with_status = build_donors_with_status(donors)
                        return render_template('donate.html', donors_with_status=donors_with_status, error=error_msg)
            cur.execute("""
                UPDATE donor 
                SET lastdonationdate=%s, units = units + %s 
                WHERE donorid=%s
            """, (donation_date, units, donorid))
            cur.execute("""
                INSERT INTO donation(donorid, bloodgroup, unitsdonated, donationdate)
                VALUES (%s, %s, %s, %s)
            """, (donorid, bloodgroup, units, donation_date))

            mysql.connection.commit()
            cur.close()
            update_stock(bloodgroup, units, "ADD")
            add_expiry(bloodgroup, units, donation_date)
            fulfill_pending_requests(bloodgroup)

            return redirect(url_for('donors'))

        except Exception as e:
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM donor")
            donors = cur.fetchall()
            cur.close()
            donors_with_status = build_donors_with_status(donors)
            error_msg = f"Error recording donation: {str(e)}"
            return render_template('donate.html', donors_with_status=donors_with_status, error=error_msg)
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM donor")
    donors = cur.fetchall()
    cur.close()
    donors_with_status = build_donors_with_status(donors)

    return render_template('donate.html', donors_with_status=donors_with_status)

@app.route('/dashboard')
@admin_required
def dashboard():
    cur = mysql.connection.cursor()

    cur.execute("SELECT COUNT(*) FROM donor")
    total_donors = cur.fetchone()[0]

    cur.execute("SELECT SUM(unitsavailable) FROM bloodstock")
    total_stock = cur.fetchone()[0] or 0

    cur.execute("SELECT COUNT(*) FROM bloodrequest WHERE status='Not Available'")
    pending = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM bloodrequest WHERE status='Available'")
    approved = cur.fetchone()[0]

    cur.close()

    return render_template(
        "dashboard.html",
        donors=total_donors,
        stock=total_stock,
        pending=pending,
        approved=approved
    )
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)