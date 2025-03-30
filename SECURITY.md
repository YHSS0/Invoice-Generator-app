# 🔒 Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.x     | ✅ Yes    |

---

## 📢 Reporting a Vulnerability

If you discover a security vulnerability, please help us keep the project safe by reporting it **privately**:


- GitHub Issues: Please avoid posting sensitive issues publicly.

We will respond as quickly as possible and address any verified vulnerabilities with urgency.

---

## 🔐 Security Best Practices for Users

If you're running this app on your own server or publicly, please follow these recommendations:

### 🧰 General

- **Keep Python and Flask up to date** to prevent vulnerabilities.
- Set `debug=False` in production (`app.run(debug=False)`).

### 🖼️ File Uploads

- The app uses `secure_filename()` to sanitize uploaded filenames.
- Only image files should be allowed for upload (PNG, JPG, JPEG).
- Do not allow executable file uploads.

### 📁 Directories

- Uploaded files go to `/uploads`, and invoices to `/invoices`.
- Consider using temporary storage or adding auto-cleanup logic.

### 🌐 Deployment

- Use HTTPS in production.
- Deploy behind a firewall/reverse proxy like Nginx or Caddy.
- Run Flask via a WSGI server like Gunicorn or uWSGI.

### 🧪 Validate Inputs

- Ensure all user inputs are validated and escaped.
- Consider integrating Flask-WTF or similar for form validation.

---

## 🛡️ Future Enhancements

- Authentication system for multi-user support
- Role-based access control (RBAC)
- Rate limiting and CAPTCHA to prevent spam
- Logging of suspicious activity

---

Thank you for helping make this project secure! 🙌
