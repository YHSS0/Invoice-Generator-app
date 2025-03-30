from flask import Flask, render_template, request, send_file
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from datetime import datetime
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['INVOICE_FOLDER'] = 'invoices'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['INVOICE_FOLDER'], exist_ok=True)

class InvoiceItem:
    def __init__(self, description, quantity, unit_price):
        self.description = description
        self.quantity = int(quantity)
        self.unit_price = float(unit_price)

    def total_price(self):
        return self.quantity * self.unit_price

class Invoice:
    def __init__(self, sender, recipient, items, logo_path=None, note=None,
                 address=None, payment_method=None, paid_status=None, deposit=None,
                 discount=0, invoice_title=None, due_date=None):
        self.sender = sender
        self.recipient = recipient
        self.items = items
        self.logo_path = logo_path
        self.note = note
        self.address = address
        self.payment_method = payment_method
        self.paid_status = paid_status
        self.deposit = float(deposit) if deposit else 0
        self.discount = float(discount) if discount else 0
        self.invoice_title = invoice_title
        self.due_date = due_date
        self.date = datetime.now().strftime('%Y-%m-%d')
        self.invoice_number = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    def generate_pdf(self, filename):
        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4

        y_position = height - 30 * mm

        if self.logo_path and os.path.exists(self.logo_path):
            c.drawImage(self.logo_path, 15 * mm, y_position, width=40 * mm, preserveAspectRatio=True)

        c.setFont("Helvetica-Bold", 14)
        title = self.invoice_title if self.invoice_title else "INVOICE"
        c.drawString(60 * mm, y_position, title)

        y_position -= 15 * mm

        c.setFont("Helvetica", 10)
        c.drawString(15 * mm, y_position, f"Invoice #: {self.invoice_number}")
        y_position -= 5 * mm
        c.drawString(15 * mm, y_position, f"Date: {self.date}")
        if self.due_date:
            c.drawString(100 * mm, y_position + 5 * mm, f"Due Date: {self.due_date}")

        if self.address:
            y_position -= 10 * mm
            c.drawString(15 * mm, y_position, "Address:")
            y_position -= 5 * mm
            for line in self.address.split('\n'):
                c.drawString(15 * mm, y_position, line)
                y_position -= 5 * mm

        y_position -= 5 * mm
        c.drawString(15 * mm, y_position, "From:")
        y_position -= 5 * mm
        for line in self.sender.split('\n'):
            c.drawString(15 * mm, y_position, line)
            y_position -= 5 * mm

        y_position -= 5 * mm
        c.drawString(15 * mm, y_position, "To:")
        y_position -= 5 * mm
        for line in self.recipient.split('\n'):
            c.drawString(15 * mm, y_position, line)
            y_position -= 5 * mm

        y_position -= 10 * mm
        c.setFont("Helvetica-Bold", 10)
        c.drawString(15 * mm, y_position, "Description")
        c.drawString(100 * mm, y_position, "Quantity")
        c.drawString(130 * mm, y_position, "Unit Price")
        c.drawString(170 * mm, y_position, "Total")
        c.setLineWidth(0.5)
        c.line(15 * mm, y_position - 2, 195 * mm, y_position - 2)
        y_position -= 7 * mm
        c.setFont("Helvetica", 10)

        total_amount = 0
        for item in self.items:
            c.drawString(15 * mm, y_position, item.description)
            c.drawRightString(115 * mm, y_position, str(item.quantity))
            c.drawRightString(145 * mm, y_position, f"${item.unit_price:.2f}")
            c.drawRightString(195 * mm, y_position, f"${item.total_price():.2f}")
            total_amount += item.total_price()
            y_position -= 6 * mm

        y_position -= 5 * mm
        if self.discount:
            c.drawRightString(195 * mm, y_position, f"Discount: -${self.discount:.2f}")
            total_amount -= self.discount
            y_position -= 6 * mm

        if self.deposit:
            c.drawRightString(195 * mm, y_position, f"Deposit Paid: ${self.deposit:.2f}")
            y_position -= 6 * mm

        c.setFont("Helvetica-Bold", 10)
        c.drawRightString(195 * mm, y_position, f"Total Due: ${total_amount - self.deposit:.2f}")

        if self.payment_method or self.paid_status:
            y_position -= 10 * mm
            c.setFont("Helvetica", 10)
            if self.payment_method:
                c.drawString(15 * mm, y_position, f"Payment Method: {self.payment_method}")
                y_position -= 5 * mm
            if self.paid_status:
                c.drawString(15 * mm, y_position, f"Payment Status: {self.paid_status}")
                y_position -= 5 * mm

        if self.note:
            y_position -= 10 * mm
            c.setFont("Helvetica-Oblique", 10)
            c.drawString(15 * mm, y_position, "Note:")
            y_position -= 5 * mm
            for line in self.note.split('\n'):
                c.drawString(15 * mm, y_position, line)
                y_position -= 5 * mm

        c.save()
        return filename
@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')


@app.route('/InvoiceGenerator', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        sender = request.form['sender']
        recipient = request.form['recipient']
        invoice_title = request.form.get('invoice_title')
        due_date = request.form.get('due_date')
        address = request.form.get('address')
        payment_method = request.form.get('payment_method')
        paid_status = request.form.get('paid_status')
        deposit = request.form.get('deposit')
        discount = request.form.get('discount')
        note = request.form.get('note')

        descriptions = request.form.getlist('description')
        quantities = request.form.getlist('quantity')
        prices = request.form.getlist('price')

        items = [InvoiceItem(d, q, p) for d, q, p in zip(descriptions, quantities, prices)]

        logo_file = request.files.get('logo')
        logo_path = None
        if logo_file and logo_file.filename:
            filename = secure_filename(logo_file.filename)
            logo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            logo_file.save(logo_path)

        invoice = Invoice(sender, recipient, items, logo_path, note, address,
                          payment_method, paid_status, deposit, discount,
                          invoice_title, due_date)
        pdf_path = os.path.join(app.config['INVOICE_FOLDER'], f"{invoice.invoice_number}.pdf")
        invoice.generate_pdf(pdf_path)
        return send_file(pdf_path, as_attachment=True)

    return render_template('form.html')

if __name__ == '__main__':
    app.run(debug=True)
