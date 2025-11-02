import qrcode
import io
from flask import send_file

from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Movies and images (filenames should match files in static/images/)
MOVIES = [
    {"name": "Leo", "image": "leo.jpg"},
    {"name": "Vaaranam Aayiram", "image": "V1000.jpg"},
    {"name": "Dude", "image": "dude.jpg"},
    {"name": "Diesel", "image": "diesel.jpg"},
    {"name": "Bison", "image": "bison.jpg"},
    {"name": "96", "image": "96.jpg"},
    {"name": "Jailer", "image": "jailer.jpg"},
    {"name": "Kantara", "image": "kantara.avif"},
    {"name": "Kalki", "image": "kalki.jpg"}
]

# Theatres and availability per movie (subset mapping)
THEATRES = {
    "Leo": ["PVR Cinemas (VR Chennai)", "Luxe Cinemas", "Palazzo (Forum)"],
    "V1000": ["Escape Cinemas (Express Avenue)", "PVR Cinemas (VR Chennai)", "INOX (Arcot Road)"],
    "Dude": ["Abirami Multiplex", "Udhayam Theatre"],
    "Diesel": ["PVR Cinemas (VR Chennai)", "Luxe Cinemas"],
    "Bison": ["Devi Cineplex", "Kamala Cinemas"],
    "96": ["Sathyam Cinemas", "INOX (Arcot Road)", "Palazzo (Forum)"],
    "Jailer": ["PVR Cinemas (VR Chennai)", "Abirami Multiplex", "Udhayam Theatre"],
    "Kantara": ["Palazzo (Forum)", "Escape Cinemas (Express Avenue)", "Kamala Cinemas"],
    "Kalki": ["Luxe Cinemas", "PVR Cinemas (VR Chennai)", "Sathyam Cinemas"]
}

SHOW_TIMES = ["10:00 AM", "1:30 PM", "5:00 PM", "8:30 PM"]

TICKET_PRICE = 150  # per seat (for demo)

@app.route('/')
def home():
    return render_template('index.html', movies=MOVIES)

@app.route('/theatre/<movie_name>')
def theatre(movie_name):
    theatres = THEATRES.get(movie_name, [])
    return render_template('theatre.html', movie_name=movie_name, theatres=theatres, show_times=SHOW_TIMES)

# seats page - receives movie + theatre + time by POST (from theatre.html form)
@app.route('/seats', methods=['POST'])
def seats():
    movie_name = request.form.get('movie_name')
    theatre = request.form.get('theatre')
    showtime = request.form.get('showtime')
    # create seat labels A1..E10
    rows = ["A", "B", "C", "D", "E"]
    cols = list(range(1, 11))
    seat_grid = [f"{r}{c}" for r in rows for c in cols]
    return render_template('seats.html',
                           movie_name=movie_name,
                           theatre=theatre,
                           showtime=showtime,
                           seat_grid=seat_grid)

# payment page - receives selected seats plus booking details via POST from seats.html
@app.route('/payment', methods=['POST'])
def payment():
    movie_name = request.form.get('movie_name')
    theatre = request.form.get('theatre')
    showtime = request.form.get('showtime')
    # seats may be multiple values
    seats = request.form.getlist('seats')
    if not seats:
        # no seats selected -> redirect back to seats page (could show message)
        return redirect(url_for('theatre', movie_name=movie_name))
    total = len(seats) * TICKET_PRICE
    return render_template('payment.html',
                           movie_name=movie_name,
                           theatre=theatre,
                           showtime=showtime,
                           seats=seats,
                           total=total)
from flask import send_file
from io import BytesIO
from reportlab.lib.pagesizes import A6
from reportlab.pdfgen import canvas

@app.route('/download_ticket')
def download_ticket():
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
    import qrcode
    import io
    import os

    movie_name = request.args.get('movie_name')
    theatre_name = request.args.get('theatre_name')
    show_time = request.args.get('show_time')
    seats = request.args.get('seats')
    name = request.args.get('name')

    # 🎟️ Ticket Data
    qr_data = f"Movie: {movie_name}\nTheatre: {theatre_name}\nShowtime: {show_time}\nSeats: {seats}\nName: {name}"
    qr_img = qrcode.make(qr_data)

    # Save temporary QR image
    qr_path = "temp_qr.png"
    qr_img.save(qr_path)

    # Create PDF
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=A4)

    # 🖤 Background
    c.setFillColorRGB(0.08, 0.08, 0.1)  # Dark grey/black
    c.rect(0, 0, A4[0], A4[1], fill=1)

    # 🎬 Header
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(A4[0] / 2, 800, "🎬 DIGITAL MOVIE TICKET 🎟️")

    # 🧾 Ticket Info Box
    c.setFillColorRGB(0.15, 0.15, 0.2)
    c.roundRect(60, 520, 480, 220, 20, fill=1)

    c.setFillColor(colors.whitesmoke)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(80, 700, f"Name: {name}")
    c.drawString(80, 670, f"Movie: {movie_name}")
    c.drawString(80, 640, f"Theatre: {theatre_name}")
    c.drawString(80, 610, f"Show Time: {show_time}")
    c.drawString(80, 580, f"Seats: {seats}")

    # 🧠 QR Code
    c.drawImage(qr_path, 420, 550, width=100, height=100)

    # 🖋️ Footer
    c.setFont("Helvetica-Oblique", 12)
    c.setFillColorRGB(0.7, 0.7, 0.7)
    c.drawCentredString(A4[0] / 2, 100, "Enjoy your movie experience 🍿 | TicketBookingSystem")

    # Save & clean
    c.save()
    pdf_buffer.seek(0)

    try:
        os.remove(qr_path)
    except:
        pass

    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"{movie_name}_ticket.pdf",
        mimetype='application/pdf'
    )





# success page - receives payment form POST
@app.route('/success', methods=['POST'])
def success():
    name = request.form.get('name')
    email = request.form.get('email')
    movie_name = request.form.get('movie_name')
    theatre = request.form.get('theatre')
    showtime = request.form.get('showtime')
    seats = request.form.get('seats')
    total = request.form.get('total')
    # seats arrives as comma-joined string in hidden field; keep as string for display
    return render_template('success.html',
                           name=name,
                           email=email,
                           movie_name=movie_name,
                           theatre=theatre,
                           showtime=showtime,
                           seats=seats,
                           total=total)

if __name__ == '__main__':
    app.run(debug=True)
