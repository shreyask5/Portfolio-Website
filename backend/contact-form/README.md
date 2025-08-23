# Contact Form Backend

A simple Flask backend that handles contact form submissions and sends emails using Gmail SMTP.

## Features

- Contact form email processing
- Gmail SMTP integration
- CORS enabled for frontend integration
- JSON API endpoints
- Error handling and logging

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Gmail:**
   - The app uses the provided Gmail credentials:
     - Email: `emergencyresponsesystem1@gmail.com`
     - Password: `qsdu vnit fbpt okjw`
   - Make sure 2-factor authentication is enabled on the Gmail account
   - Generate an App Password if needed

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Access the API:**
   - Main endpoint: `http://localhost:5001/`
   - Contact API: `http://localhost:5001/api/contact`
   - Status API: `http://localhost:5001/api/status`

## API Endpoints

### POST /api/contact
Handles contact form submissions.

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "message": "Hello, I'd like to discuss a project."
}
```

**Response:**
```json
{
  "success": true,
  "message": "Message sent successfully!"
}
```

### GET /api/status
Returns the current status of the API and email service.

## Frontend Integration

The frontend should send POST requests to `/api/contact` with the contact form data. The backend will automatically send emails to `shreyasksh5@gmail.com`.

## Security Notes

- In production, consider using environment variables for email credentials
- Implement rate limiting to prevent spam
- Add input validation and sanitization
- Use HTTPS in production

## Troubleshooting

- **Email not sending:** Check Gmail credentials and 2FA settings
- **CORS issues:** Ensure the frontend domain is allowed
- **Port conflicts:** Change the port in `app.py` if 5001 is already in use
