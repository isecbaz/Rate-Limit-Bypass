import random
import time
from flask import Flask, render_template_string, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "your_secret_key"
attempts_dict = {}
lockout_dict = {}

def generate_otp():
    return str(random.randint(1000, 9999))

def is_rate_limited(phone):
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    print(f"Client IP: {ip}") 
    
    if ip == "8.8.8.8":
        return False 
    if lockout_dict.get(phone) and time.time() < lockout_dict[phone]:
        return True 
    return False

def save_attempts(phone, attempts, lockout_time):
    attempts_dict[phone] = attempts
    lockout_dict[phone] = lockout_time

def get_attempts(phone):
    attempts = attempts_dict.get(phone, 0)
    lockout_time = lockout_dict.get(phone, 0)
    return attempts, lockout_time

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        phone = request.form['phone']
        if len(phone) != 11 or not phone.startswith("09"):
            return render_template_string(HTML_TEMPLATE, error="Please enter a valid phone number (starting with 09).")
        attempts, lockout_time = get_attempts(phone)
        if attempts >= 3:
            if time.time() < lockout_time:
                remaining_lockout_time = lockout_time - time.time()
                return render_template_string(HTML_TEMPLATE, error=f"Too many failed attempts. Please try again after {int(remaining_lockout_time)} seconds.")
            else:
                save_attempts(phone, 0, 0)
        otp = generate_otp()
        otp_time = time.time() + 120 
        session['phone'] = phone
        session['otp'] = otp
        session['otp_time'] = otp_time
        session['otp_verified'] = False 
        print(f"Generated OTP: {otp} for {phone}")
        return redirect(url_for('otp'))  
    
    return render_template_string(HTML_TEMPLATE)

@app.route('/otp', methods=['GET', 'POST'])
def otp():
    phone = session.get('phone')
    if not phone:
        return redirect(url_for('index'))
    
    remaining_time = max(0, int(session['otp_time'] - time.time()))
    otp = session.get('otp')
    attempts, lockout_time = get_attempts(phone)

    if request.method == 'POST':
        otp_input = request.form['otp']
        
        if not otp_input or not otp_input.isdigit() or len(otp_input) != 4:
            return render_template_string(OTP_TEMPLATE, error="Please enter a valid 4-digit OTP.", remaining_time=remaining_time, otp=otp, attempts=attempts)
        
        otp_time = session['otp_time']
        if time.time() > otp_time:
            return render_template_string(OTP_TEMPLATE, error="OTP expired. Please request a new one.", remaining_time=remaining_time, otp=otp, attempts=attempts)
        
        if otp == otp_input:
            session['otp_verified'] = True
            print(f"OTP Verified: {session['otp_verified']}")  # https://t.me/rmsup
            if is_rate_limited(phone):
                remaining_time = lockout_dict[phone] - time.time()
                return render_template_string(OTP_TEMPLATE, error=f"Rate limit applied. Please try again after {int(remaining_time)} seconds.", remaining_time=remaining_time, otp=otp, attempts=attempts)
            return redirect(url_for('dashboard'))
        
        attempts += 1
        if attempts >= 3:
            lockout_time = time.time() + 600 
        save_attempts(phone, attempts, lockout_time)
        
        warning_message = "Incorrect OTP. Please try again."
        if attempts == 2:
            warning_message = "You have 1 more incorrect attempt before being rate-limited for 10 minutes."
        elif attempts == 3:
            warning_message = "Rate limit applied. You are blocked for 10 minutes."
        
        return render_template_string(OTP_TEMPLATE, error=warning_message, remaining_time=remaining_time, otp=otp, attempts=attempts)
    
    return render_template_string(OTP_TEMPLATE, remaining_time=remaining_time, otp=otp, attempts=attempts)

@app.route('/dashboard')
def dashboard():
    phone = session.get('phone')
    print(f"Dashboard Access - Session: {session}") 
    
    if not phone or not session.get('otp_verified'):
        return redirect(url_for('otp'))  
    if is_rate_limited(phone):
        remaining_time = max(0, int(lockout_dict[phone] - time.time()))
        return render_template_string(OTP_TEMPLATE, error=f"Rate limit applied. Please try again after {remaining_time} seconds.")
    
    user_info = {
        'name': 'John Doe',
        'location': 'New York',
        'role': 'User',
        'email': 'johndoe@example.com',
        'birth_date': '1990-01-01',
        'telegram': '@rmsup'
    }
    
    return render_template_string(DASHBOARD_TEMPLATE, user_info=user_info)

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('phone', None)
    session.pop('otp_verified', None)
    return redirect(url_for('index'))

# https://t.me/rmsup
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OTP Verification | Telegram: @rmsup</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .container {
            background-color: white;
            padding: 40px 77px;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            width: 100%;
            max-width: 400px;
        }
        h2 {
            text-align: center;
            margin-bottom: 20px;
            color: #333;
        }
        label {
            font-size: 1rem;
            margin-bottom: 10px;
            display: block;
            color: #555;
        }
        input {
            width: 100%;
            padding: 15px;
            margin: 10px 0;
            border-radius: 4px;
            border: 1px solid #ccc;
            font-size: 1rem;
            text-align: center;
            box-sizing: border-box;
        }
        input:focus {
            border-color: #28a745;
            outline: none;
        }
        button {
            width: 100%;
            padding: 15px;
            background-color: #a72828;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 1rem;
        }
        button:hover {
            background-color: #218838;
        }
        .error {
            color: red;
            font-size: 1rem;
            text-align: center;
            margin-bottom: 10px;
        }
        @media (max-width: 600px) {
            .container {
                padding: 20px;
                max-width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>OTP Verification</h2>
        <form method="POST">
            <label for="phone">Enter your phone number:</label>
            <input type="text" id="phone" name="phone" placeholder="09XXXXXXXXX" required>
            {% if error %}
                <p class="error">{{ error }}</p>
            {% endif %}
            <button type="submit">Send OTP</button>
        </form>
    </div>
</body>
</html>
'''

OTP_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OTP Verification | Telegram: @rmsup</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f9f9f9;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .container {
            background-color: white;
            padding: 40px 77px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            width: 100%;
            max-width: 400px;
        }
        h2 {
            text-align: center;
            color: #333;
            font-size: 1.5rem;
            margin-bottom: 20px;
        }
        label {
            font-size: 1rem;
            margin-bottom: 10px;
            display: block;
            color: #555;
        }
        input {
            width: 100%;
            padding: 15px;
            margin: 10px 0;
            border-radius: 4px;
            border: 1px solid #ccc;
            font-size: 1rem;
            color: #333;
            text-align: center;
            box-sizing: border-box;
            transition: border-color 0.3s ease;
        }
        input:focus {
            border-color: #007bff;
            outline: none;
        }
        button {
            width: 100%;
            padding: 16px;
            background-color: #28a745;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 1rem;
            transition: background-color 0.3s ease;
        }
        button:hover {
            background-color: #882121;
        }
        .error {
            color: #e74c3c;
            font-size: 1rem;
            text-align: center;
            margin-bottom: 10px;
        }
        .success {
            color: green;
            font-size: 1rem;
            text-align: center;
            margin-bottom: 10px;
        }
        @media (max-width: 600px) {
            .container {
                padding: 20px;
                max-width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>Enter OTP</h2>
        <form method="POST">
            <label for="otp">Please enter the OTP sent to your phone:</label>
            <input type="text" id="otp" name="otp" placeholder="Enter OTP" required pattern="\d{4}" minlength="4" maxlength="4">
            {% if error %}
                <p class="error">{{ error }}</p>
            {% endif %}
            <p>Your OTP: <strong>{{ otp }}</strong></p>
            <button type="submit">Verify OTP</button>
        </form>
        <p>Remaining time: <strong>{{ remaining_time }}</strong> seconds</p>
    </div>
</body>
</html>
'''

DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard | Telegram: @rmsup</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #fafafa;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .container {
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            width: 100%;
            max-width: 400px;
        }
        h2 {
            text-align: center;
            color: #333;
            font-size: 1.5rem;
            margin-bottom: 20px;
        }
        p {
            font-size: 1rem;
            margin: 10px 0;
        }
        button {
            width: 100%;
            padding: 16px;
            background-color: #dc3545;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 1rem;
            transition: background-color 0.3s ease;
        }
        button:hover {
            background-color: #c82333;
        }
        @media (max-width: 600px) {
            .container {
                padding: 20px;
                max-width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>Welcome, {{ user_info.name }}</h2>
        <p><strong>Location:</strong> {{ user_info.location }}</p>
        <p><strong>Role:</strong> {{ user_info.role }}</p>
        <p><strong>Email:</strong> {{ user_info.email }}</p>
        <p><strong>Birthdate:</strong> {{ user_info.birth_date }}</p>
        <p><strong>Telegram:</strong> {{ user_info.telegram }}</p>
        <form method="POST" action="{{ url_for('logout') }}">
            <button type="submit">Logout</button>
        </form>
    </div>
</body>
</html>
'''

if __name__ == '__main__':
    app.run(debug=True)
