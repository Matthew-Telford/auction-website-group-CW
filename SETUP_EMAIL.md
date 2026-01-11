# Email Setup Guide for Auction Website

This guide will help you configure email sending for the auction winner notifications.

## Quick Setup (5 minutes)

### Step 1: Get Gmail App Password

1. Go to https://myaccount.google.com/security
2. Make sure **2-Step Verification** is enabled
3. Scroll down to **App passwords**
4. Click **App passwords** → Select **Mail** → Generate
5. Copy the 16-character password (e.g., `xxxx xxxx xxxx xxxx`)

### Step 2: Create .env File

Create a file named `.env` in your project root (same directory as `manage.py`):

```bash
EMAIL_HOST_USER=matthewtelford93@gmail.com
EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx
```

Replace `xxxx xxxx xxxx xxxx` with your actual App Password from Step 1.

### Step 3: Verify Configuration

Your `project/settings.py` is already configured! It should have:

```python
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = os.environ.get("EMAIL_HOST_USER", "noreply@auction.com")
```

✅ This is already set up correctly!

## Test Your Configuration

Run the test suite to verify everything works:

```bash
python manage.py test api.test_cron_email --verbosity=2
```

This will:
- ✅ Send a real test email to `matthewtelford93@gmail.com`
- ✅ Save a copy to `~/Downloads/auction_emails/`
- ✅ Show detailed results in console

## What Gets Sent

When an auction ends, the winner receives an email with:
- **Subject**: "Congratulations! You won [item title]"
- **Body**: (You'll write this later - currently blank)
- **From**: `matthewtelford93@gmail.com`

## Production Deployment

For production, you should:
1. Use environment variables (already set up via `.env`)
2. Consider using a dedicated email service (SendGrid, Mailgun, etc.)
3. Write a proper email body with auction details
4. Add your company branding

## Troubleshooting

### "Authentication failed" error
- Make sure you're using the **App Password**, not your regular Gmail password
- Check that 2-Step Verification is enabled on your Google account

### Email not received
- Check spam folder
- Verify the `.env` file is in the correct location (project root)
- Make sure there are no extra spaces in the `.env` file
- Try sending a test email:
  ```bash
  python manage.py shell
  ```
  ```python
  from django.core.mail import send_mail
  send_mail('Test', 'Test message', 'matthewtelford93@gmail.com', ['matthewtelford93@gmail.com'])
  ```

### "No module named 'dotenv'" error
- Install python-dotenv:
  ```bash
  pip install python-dotenv
  ```

## Security Notes

⚠️ **Important**: Never commit your `.env` file to git!

Make sure `.env` is in your `.gitignore`:
```bash
echo ".env" >> .gitignore
```

## Cron Job Schedule

The cron job is configured to run daily at midnight:

In `project/settings.py`:
```python
CRONJOBS = [
    ('0 0 * * *', 'api.cron.process_auction_winners'),
]
```

To activate the cron job (when deploying):
```bash
python manage.py crontab add
python manage.py crontab show  # Verify it was added
```

---

Need help? Check `api/TEST_CRON_README.md` for more detailed testing instructions.
