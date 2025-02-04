from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from extensions import db
from models import User, Outpass
import qrcode
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.getenv('EMAIL_PASSWORD')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable caching during development

# Initialize extensions
db.init_app(app)
login_manager = LoginManager(app)
mail = Mail(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
    
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:
            login_user(user)
            if user.role == 'student':
                return redirect(url_for('student_dashboard'))
            elif user.role == 'warden':
                return redirect(url_for('warden_dashboard'))
            elif user.role == 'guard':
                return redirect(url_for('guard_dashboard'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/student/dashboard')
@login_required
def student_dashboard():
    if current_user.role != 'student':
        return redirect(url_for('login'))
    outpasses = Outpass.query.filter_by(student_id=current_user.id).all()
    return render_template('student.html', outpasses=outpasses)

@app.route('/request-outpass', methods=['POST'])
@login_required
def request_outpass():
    if current_user.role != 'student':
        return redirect(url_for('login'))
    
    reason = request.form['reason']
    from_date = datetime.strptime(request.form['from_date'], '%Y-%m-%dT%H:%M')
    to_date = datetime.strptime(request.form['to_date'], '%Y-%m-%dT%H:%M')
    
    new_outpass = Outpass(
        student_id=current_user.id,
        reason=reason,
        from_date=from_date,
        to_date=to_date
    )
    db.session.add(new_outpass)
    db.session.commit()
    flash('Outpass requested successfully', 'success')
    return redirect(url_for('student_dashboard'))

@app.route('/warden/dashboard')
@login_required
def warden_dashboard():
    if current_user.role != 'warden':
        return redirect(url_for('login'))
    pending = Outpass.query.filter_by(status='pending').all()
    return render_template('warden.html', requests=pending)

@app.route('/approve-outpass/<int:op_id>')
@login_required
def approve_outpass(op_id):
    if current_user.role != 'warden':
        return redirect(url_for('login'))
    
    outpass = Outpass.query.get(op_id)
    outpass.status = 'approved'
    
    # Generate QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(f'OPID:{op_id}')
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Ensure qrcodes directory exists
    qr_dir = os.path.join(app.static_folder, 'qrcodes')
    if not os.path.exists(qr_dir):
        os.makedirs(qr_dir)
    
    img_name = f'op-{op_id}.png'
    img_path = os.path.join(qr_dir, img_name)
    img.save(img_path ,'PNG')
    
    outpass.qr_code = f'qrcodes/{img_name}'
    db.session.commit()
    
    # Send email
    student = User.query.get(outpass.student_id)
    msg = Message('Outpass Approved', 
                  sender=os.getenv('EMAIL_USER'), 
                  recipients=[student.email])
    msg.body = f'Your outpass (ID: {op_id}) has been approved. Access QR code at: {url_for("static", filename=img_path, _external=True)}'
    mail.send(msg)
    
    flash('Outpass approved successfully', 'success')
    return redirect(url_for('warden_dashboard'))

@app.route('/guard/dashboard', methods=['GET', 'POST'])
@login_required
def guard_dashboard():
    if current_user.role != 'guard':
        return redirect(url_for('login'))
    
    valid = None
    outpass = None
    
    if request.method == 'POST':
        qr_data = request.form['qr_data']
        try:
            op_id = int(qr_data.split(':')[-1].strip())
            outpass = Outpass.query.get(op_id)
            valid = outpass is not None and outpass.status == 'approved'
        except (ValueError, IndexError):
            valid = False
    
    return render_template('guard.html', valid=valid, outpass=outpass if valid else None)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)