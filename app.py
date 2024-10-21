from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, RadioField
from wtforms.validators import DataRequired, Email

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, Render!"
app.config['SECRET_KEY'] = 'FIREINPANTS'  
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///small_arms.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database model for complaints
class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(10), nullable=False)  # Column for priority
    status = db.Column(db.String(20), default='Open')  # Column for status

# WTForm for complaint submission
class ComplaintForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(message="Please enter your name.")])
    email = StringField('Email', validators=[DataRequired(message="Please enter your email."), Email(message="Invalid email address.")])
    subject = StringField('Subject', validators=[DataRequired(message="Please enter a subject.")])
    description = TextAreaField('Description', validators=[DataRequired(message="Please enter the description of your complaint.")])
    priority = RadioField('Priority', choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], default='medium')
    submit = SubmitField('Submit Complaint')

class UpdateForm(FlaskForm):
    status =  RadioField('Status', choices=[('open', 'Open'), ('in_progress', 'In_Progress'), ('close', 'Close')], default='Open')
    submit = SubmitField('Update') 
@app.route('/', methods=['GET', 'POST'])
def index():
    form = ComplaintForm()
    if form.validate_on_submit():
        complaint = Complaint(
            name=form.name.data,
            email=form.email.data,
            subject=form.subject.data,
            description=form.description.data,
            priority=form.priority.data
        )
        db.session.add(complaint)
        db.session.commit()
        flash('Your complaint has been submitted successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('index.html', form=form)

@app.route('/complaints')
def complaints():
    try:
        all_complaints = Complaint.query.order_by(Complaint.priority.desc()).all()
        return render_template('complaints.html', complaints=all_complaints)
    except Exception as e:
        app.logger.error(f"Error fetching complaints: {e}")
        flash('An error occurred while fetching complaints. Please try again later.', 'danger')
        return redirect(url_for('index'))

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Dummy check for admin credentials; replace with your own logic
        if username == 'admin' and password == '123':
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')
    return render_template('admin_login.html')

@app.route('/admin_dashboard', methods=['GET','POST'])
def admin_dashboard():
    # Fetch all complaints to display on the dashboard
    complaints = Complaint.query.all()
    return render_template('admin_dashboard.html',complaints=complaints)
@app.route('/update/<int:complaint_id>', methods=['GET','POST'])
def update_complaint(complaint_id,new_status="Open"):
    form=UpdateForm()
    complaint = Complaint.query.get_or_404(complaint_id)
    new_status = request.form.get('status')
    print(new_status)
    complaint.status = new_status
    db.session.commit()
    flash('Complaint status has been updated.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/delete/<int:complaint_id>', methods=['POST'])
def delete_complaint(complaint_id):
    complaint = Complaint.query.get_or_404(complaint_id)
    db.session.delete(complaint)
    db.session.commit()
    flash('Complaint has been deleted.', 'success')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    # Create the database tables if they don't exist
    with app.app_context():
        db.create_all()

    app.run(debug=True)
