# A Rate Limit Bypass Lab
**`This is a dedicated laboratory developed using Python to bypass rate limits.⏳`**
This is a Flask-based web application that implements a two-factor authentication system using one-time passwords (OTP) and rate limiting to mitigate brute-force attacks. Users can enter their phone number to receive an OTP for verification. The system tracks the number of failed attempts and imposes a 10-minute lockout after three unsuccessful tries. It also employs rate limiting to restrict access for users attempting to bypass the system. This implementation provides a simple dashboard for user management and security.
![1](https://github.com/user-attachments/assets/c2e0d3ac-8020-45b9-ade9-fe4c828e6a80)

<h2>How to Use This Python Script:</h2>
<li>Install Python: If you don't already have Python, you'll need to install it. You can download the appropriate version for your operating system from the official Python website.</li>
<br>
<li>Install Dependencies: To run this application, you'll need the Flask library. You can install it using pip:</li>
<br>

**`pip install Flask`**
<br>
**`pip install flask-session`**
<li>Once the dependencies are installed, you can run the code:</li>
<br>

**`python app.py`**

![2](https://github.com/user-attachments/assets/0118301d-cd69-44d9-9f63-5bab948664f3)

<br>

>(Replace **app.py** with the actual name of your Python file.)

<br>

>After following these steps, your application should be running and accessible at **http://127.0.0.1:5000** in your web browser.

<br>

>To run this Python Flask application, ensure you have Python installed. Then, install Flask using pip install Flask. Finally, execute the script with python app.py. Access the application at **http://127.0.0.1:5000**

<h2>Method of bypassing the laboratory:</h2>

**`After running the script, enter your phone number to navigate to the OTP page. Subsequently, input incorrect OTPs three times to induce a rate limit on the number.`**
**`After applying the rate limit, capture the OTP request using Burp Suite. Then, modify the request in the repeater as follows: `**
![3](https://github.com/user-attachments/assets/6bc473eb-c9f9-49fb-85b7-76239381acc6)
**`Finally, click the send button to access the dashboard.`**
![4](https://github.com/user-attachments/assets/7fbca672-5ee0-4e9c-adda-9abfc8fd4692)
**`This laboratory has been developed for educational purposes. As a result, it does not connect to a database and is solely designed to teach rate limit bypass techniques. A Persian tutorial video has been published on the Telegram channel @rmsup.`**
