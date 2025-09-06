from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Email configuration from environment variables
SENDER_EMAIL = os.getenv('SENDER_EMAIL', 'emergencyresponsesystem1@gmail.com')
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL', 'shreyasksh5@gmail.com')

def send_contact_email(name, email, message):
    """Send contact form email"""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = f"📧 New Contact Form Message from {name}"
        
        # Email body
        body = f"""
        📧 New Contact Form Message
        
        From: {name}
        Email: {email}
        Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        Message:
        {message}
        
        ---
        This message was sent from your portfolio website contact form.
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        text = msg.as_string()
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, text)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/contact/', methods=['POST'])
def contact():
    """Handle contact form submissions"""
    try:
        data = request.get_json()
        name = data.get('name', 'Unknown')
        email = data.get('email', 'Unknown')
        message = data.get('message', 'No message')
        
        # Send email
        email_sent = send_contact_email(name, email, message)
        
        if email_sent:
            return jsonify({
                'success': True,
                'message': 'Message sent successfully!'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to send message. Please try again.'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error processing request: {str(e)}'
        }), 500

@app.route('/api/status/')
def status():
    """Check API status"""
    return jsonify({
        'status': 'operational',
        'timestamp': datetime.now().isoformat(),
        'email_service': 'configured'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
