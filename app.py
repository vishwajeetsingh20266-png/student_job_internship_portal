from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)
app.config['SECRET_KEY'] = 'student-portal-secret-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_RESUME = {'pdf', 'doc', 'docx'}
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(160), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(30), default='student')
    phone = db.Column(db.String(30), default='')
    location = db.Column(db.String(160), default='')
    education = db.Column(db.String(250), default='')
    skills = db.Column(db.String(1000), default='')
    bio = db.Column(db.Text, default='')
    linkedin = db.Column(db.String(300), default='')
    github = db.Column(db.String(300), default='')
    resume = db.Column(db.String(300), default='')
    company_name = db.Column(db.String(180), default='')
    company_description = db.Column(db.Text, default='')
    website = db.Column(db.String(300), default='')
    company_location = db.Column(db.String(160), default='')
    recruiter_name = db.Column(db.String(120), default='')

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), nullable=False)
    company = db.Column(db.String(160), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    location = db.Column(db.String(120), default='Pune')
    job_type = db.Column(db.String(80), default='Full Time')
    mode = db.Column(db.String(50), default='Hybrid')
    salary = db.Column(db.String(100), default='')
    skills = db.Column(db.String(500), default='')
    description = db.Column(db.Text, default='')
    deadline = db.Column(db.String(30), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    owner = db.relationship('User', foreign_keys=[company_id])

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    status = db.Column(db.String(50), default='Applied')
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    interview_date = db.Column(db.String(30), default='')
    interview_time = db.Column(db.String(20), default='')
    interview_type = db.Column(db.String(30), default='')
    meeting_link = db.Column(db.String(500), default='')
    interview_message = db.Column(db.Text, default='')
    student = db.relationship('User', foreign_keys=[student_id], backref='applications')
    job = db.relationship('Job', backref='applications')


def seed():
    if User.query.count() == 0:
        db.session.add(User(name='Vishwajeet', email='student@example.com', password=generate_password_hash('student123'), role='student', skills='Python, Flask, HTML, CSS, SQL', education='BCS', phone='+91 90000 00000', location='Pune, Maharashtra'))
        db.session.add(User(name='Admin', email='admin@example.com', password=generate_password_hash('admin123'), role='admin'))
        db.session.add(User(name='Nexora HR', email='company@example.com', password=generate_password_hash('company123'), role='company', company_name='Nexora Technologies', company_description='Technology company building modern software, cloud and digital solutions.', website='https://example.com', company_location='Pune, Maharashtra', recruiter_name='Nexora HR', phone='+91 98765 43210'))
        db.session.commit()
    if Job.query.count() == 0:
        company = User.query.filter_by(role='company').first()
        jobs = [
            Job(title='Python Developer Intern', company='Nexora Technologies', company_id=company.id if company else None, location='Pune', job_type='Internship', mode='Hybrid', salary='₹10,000 / month', skills='Python, Flask, SQL', description='Work on Python web applications, APIs and database features.', deadline='30 Oct 2026'),
            Job(title='Frontend Developer', company='TechNova Solutions', location='Mumbai', job_type='Full Time', mode='On-site', salary='₹4 - ₹7 LPA', skills='HTML, CSS, JavaScript, Bootstrap', description='Build responsive interfaces and reusable frontend components.', deadline='05 Nov 2026'),
            Job(title='Cloud / DevOps Intern', company='CloudBridge', location='Remote', job_type='Internship', mode='Remote', salary='₹12,000 / month', skills='Linux, AWS, Docker, Git', description='Assist with cloud infrastructure, CI/CD and deployment automation.', deadline='12 Nov 2026'),
            Job(title='Cyber Security Intern', company='SecureStack', location='Pune', job_type='Internship', mode='Hybrid', salary='₹8,000 / month', skills='Networking, Linux, Security', description='Learn security monitoring, vulnerability assessment and incident response.', deadline='20 Nov 2026')]
        db.session.add_all(jobs)
        db.session.commit()


def current_user():
    return db.session.get(User, session['user_id']) if session.get('user_id') else None

def login_required(role=None):
    if not session.get('user_id'):
        return False
    return role is None or session.get('role') == role

def ext_ok(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_RESUME

@app.context_processor
def inject():
    u = current_user()
    data = {'current_user': u, 'application_count': 0, 'job_count': Job.query.count()}
    if u and u.role == 'student':
        data['application_count'] = Application.query.filter_by(student_id=u.id).count()
    return data

@app.route('/')
def index():
    if not session.get('user_id'): return redirect(url_for('login'))
    if session.get('role') == 'company': return redirect(url_for('company_dashboard'))
    if session.get('role') == 'admin': return redirect(url_for('admin'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email'].strip().lower()).first()
        if user and check_password_hash(user.password, request.form['password']):
            session.update(user_id=user.id, name=user.name, role=user.role)
            return redirect(url_for('index'))
        flash('Invalid email or password.', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        role = request.form.get('role','student')
        email = request.form['email'].strip().lower()
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error'); return render_template('register.html')
        user = User(name=request.form['name'].strip(), email=email, password=generate_password_hash(request.form['password']), role=role)
        if role == 'company':
            user.company_name = request.form.get('company_name','').strip()
            user.company_description = request.form.get('company_description','').strip()
            user.website = request.form.get('website','').strip()
            user.company_location = request.form.get('company_location','').strip()
            user.recruiter_name = request.form.get('recruiter_name','').strip()
            user.phone = request.form.get('phone','').strip()
        else:
            user.education = request.form.get('education','').strip(); user.skills = request.form.get('skills','').strip()
        db.session.add(user); db.session.commit()
        flash('Registration successful. Please login.', 'success'); return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if not login_required('student'): return redirect(url_for('index'))
    u=current_user(); apps=Application.query.filter_by(student_id=u.id).order_by(Application.applied_at.desc()).limit(5).all(); jobs=Job.query.order_by(Job.created_at.desc()).limit(4).all()
    counts={'applications':Application.query.filter_by(student_id=u.id).count(),'shortlisted':Application.query.filter_by(student_id=u.id,status='Shortlisted').count(),'interviews':Application.query.filter_by(student_id=u.id,status='Interview').count(),'selected':Application.query.filter_by(student_id=u.id,status='Selected').count()}
    return render_template('dashboard.html', user=u, applications=apps, jobs=jobs, counts=counts)

@app.route('/jobs')
def jobs():
    if not session.get('user_id'): return redirect(url_for('login'))
    q=request.args.get('q','').strip(); mode=request.args.get('mode',''); query=Job.query
    if q:
        like=f'%{q}%'; query=query.filter(db.or_(Job.title.ilike(like),Job.company.ilike(like),Job.skills.ilike(like)))
    if mode: query=query.filter_by(mode=mode)
    return render_template('jobs.html', jobs=query.order_by(Job.created_at.desc()).all(), q=q, mode=mode)

@app.route('/job/<int:job_id>')
def job_detail(job_id):
    if not session.get('user_id'): return redirect(url_for('login'))
    job=db.get_or_404(Job,job_id); applied=Application.query.filter_by(student_id=session['user_id'],job_id=job_id).first() if session.get('role')=='student' else None
    return render_template('job_detail.html',job=job,applied=applied)

@app.route('/apply/<int:job_id>', methods=['POST'])
def apply(job_id):
    if not login_required('student'): return redirect(url_for('index'))
    u=current_user()
    if not u.resume: flash('Please complete your profile and upload your resume before applying.','error'); return redirect(url_for('profile'))
    if not Application.query.filter_by(student_id=u.id,job_id=job_id).first():
        db.session.add(Application(student_id=u.id,job_id=job_id)); db.session.commit(); flash('Application submitted successfully.','success')
    else: flash('You already applied for this opportunity.','error')
    return redirect(url_for('job_detail',job_id=job_id))

@app.route('/applications')
def applications():
    if not login_required('student'): return redirect(url_for('index'))
    return render_template('applications.html',applications=Application.query.filter_by(student_id=session['user_id']).order_by(Application.applied_at.desc()).all())

@app.route('/profile', methods=['GET','POST'])
def profile():
    if not login_required('student'): return redirect(url_for('index'))
    u=current_user()
    if request.method=='POST':
        for field in ['name','phone','location','education','skills','bio','linkedin','github']: setattr(u,field,request.form.get(field,'').strip())
        file=request.files.get('resume')
        if file and file.filename:
            if not ext_ok(file.filename): flash('Only PDF, DOC or DOCX resumes are allowed.','error'); return redirect(url_for('profile'))
            old=u.resume
            filename=f'{u.id}_{secure_filename(file.filename)}'; file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename)); u.resume=filename
            if old and old != filename:
                try: os.remove(os.path.join(app.config['UPLOAD_FOLDER'],old))
                except OSError: pass
        db.session.commit(); session['name']=u.name; flash('Profile and resume updated.','success'); return redirect(url_for('profile'))
    return render_template('profile.html',user=u)

@app.route('/resume/<int:user_id>')
def resume(user_id):
    if not session.get('user_id'): return redirect(url_for('login'))
    u=db.get_or_404(User,user_id)
    if not u.resume: flash('Resume not uploaded.','error'); return redirect(request.referrer or url_for('index'))
    if session.get('role') == 'student' and u.id != session['user_id']:
        flash('Access denied.','error'); return redirect(url_for('dashboard'))
    return send_from_directory(app.config['UPLOAD_FOLDER'],u.resume,as_attachment=False)

@app.route('/company')
def company_dashboard():
    if not login_required('company'): return redirect(url_for('index'))
    u=current_user(); jobs=Job.query.filter_by(company_id=u.id).order_by(Job.created_at.desc()).all(); job_ids=[j.id for j in jobs]
    apps=Application.query.filter(Application.job_id.in_(job_ids)).order_by(Application.applied_at.desc()).all() if job_ids else []
    counts={'jobs':len(jobs),'applications':len(apps),'shortlisted':sum(a.status=='Shortlisted' for a in apps),'interviews':sum(a.status=='Interview' for a in apps),'selected':sum(a.status=='Selected' for a in apps)}
    return render_template('company_dashboard.html',company=u,jobs=jobs,applications=apps,counts=counts)

@app.route('/company/profile', methods=['GET','POST'])
def company_profile():
    if not login_required('company'): return redirect(url_for('index'))
    u=current_user()
    if request.method=='POST':
        u.name=request.form.get('name','').strip(); u.company_name=request.form.get('company_name','').strip(); u.recruiter_name=request.form.get('recruiter_name','').strip(); u.phone=request.form.get('phone','').strip(); u.company_location=request.form.get('company_location','').strip(); u.website=request.form.get('website','').strip(); u.company_description=request.form.get('company_description','').strip(); db.session.commit(); session['name']=u.name; flash('Company profile updated.','success'); return redirect(url_for('company_profile'))
    return render_template('company_profile.html',company=u)

@app.route('/company/job/add', methods=['GET','POST'])
def company_add_job():
    if not login_required('company'): return redirect(url_for('index'))
    u=current_user()
    if request.method=='POST':
        job=Job(title=request.form['title'],company=u.company_name or u.name,company_id=u.id,location=request.form['location'],job_type=request.form['job_type'],mode=request.form['mode'],salary=request.form['salary'],skills=request.form['skills'],description=request.form['description'],deadline=request.form['deadline'])
        db.session.add(job); db.session.commit(); flash('Job / internship posted successfully.','success'); return redirect(url_for('company_dashboard'))
    return render_template('job_form.html',company=u)

@app.route('/company/application/<int:app_id>/status', methods=['POST'])
def company_status(app_id):
    if not login_required('company'): return redirect(url_for('index'))
    a=db.get_or_404(Application,app_id); u=current_user()
    if a.job.company_id != u.id: flash('Access denied.','error'); return redirect(url_for('company_dashboard'))
    status=request.form.get('status');
    if status in {'Under Review','Shortlisted','Rejected','Selected'}: a.status=status; db.session.commit(); flash(f'Application marked {status}.','success')
    return redirect(request.referrer or url_for('company_dashboard'))

@app.route('/company/application/<int:app_id>/interview', methods=['POST'])
def company_interview(app_id):
    if not login_required('company'): return redirect(url_for('index'))
    a=db.get_or_404(Application,app_id); u=current_user()
    if a.job.company_id != u.id: flash('Access denied.','error'); return redirect(url_for('company_dashboard'))
    a.interview_date=request.form.get('interview_date',''); a.interview_time=request.form.get('interview_time',''); a.interview_type=request.form.get('interview_type','Online'); a.meeting_link=request.form.get('meeting_link',''); a.interview_message=request.form.get('interview_message',''); a.status='Interview'; db.session.commit(); flash('Interview scheduled and student status updated.','success'); return redirect(url_for('company_dashboard'))

@app.route('/admin/settings', methods=['GET','POST'])
def admin_settings():
    if not login_required('admin'):
        return redirect(url_for('index'))
    u = current_user()
    if request.method == 'POST':
        current_password = request.form.get('current_password','')
        new_email = request.form.get('email','').strip().lower()
        new_password = request.form.get('new_password','')
        confirm_password = request.form.get('confirm_password','')

        if not check_password_hash(u.password, current_password):
            flash('Current password is incorrect.', 'error')
            return render_template('admin_settings.html', user=u)
        if not new_email:
            flash('Admin email/username is required.', 'error')
            return render_template('admin_settings.html', user=u)
        existing = User.query.filter(User.email == new_email, User.id != u.id).first()
        if existing:
            flash('This email/username is already in use.', 'error')
            return render_template('admin_settings.html', user=u)
        if new_password and len(new_password) < 6:
            flash('New password must be at least 6 characters.', 'error')
            return render_template('admin_settings.html', user=u)
        if new_password != confirm_password:
            flash('New password and confirmation do not match.', 'error')
            return render_template('admin_settings.html', user=u)

        u.email = new_email
        if new_password:
            u.password = generate_password_hash(new_password)
        db.session.commit()
        session['name'] = u.name
        flash('Admin credentials updated successfully.', 'success')
        return redirect(url_for('admin_settings'))
    return render_template('admin_settings.html', user=u)

@app.route('/admin')
def admin():
    if not login_required('admin'): return redirect(url_for('index'))
    users = User.query.order_by(User.id.desc()).all()
    students = User.query.filter_by(role='student').order_by(User.id.desc()).all()
    companies = User.query.filter_by(role='company').order_by(User.id.desc()).all()
    jobs = Job.query.order_by(Job.id.desc()).all()
    applications = Application.query.order_by(Application.id.desc()).all()
    counts = {
        'users': len(users),
        'students': len(students),
        'companies': len(companies),
        'jobs': len(jobs),
        'applications': len(applications),
    }
    return render_template('admin.html', users=users, students=students, companies=companies, jobs=jobs, applications=applications, counts=counts)

@app.route('/admin/user/<int:user_id>/delete', methods=['POST'])
def admin_delete_user(user_id):
    if not login_required('admin'): return redirect(url_for('index'))
    user = db.get_or_404(User, user_id)
    if user.role == 'admin':
        flash('Admin accounts cannot be removed from this screen.', 'error')
        return redirect(url_for('admin'))

    # Remove uploaded resume if present.
    if user.resume:
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], user.resume))
        except OSError:
            pass

    if user.role == 'company':
        owned_jobs = Job.query.filter_by(company_id=user.id).all()
        for job in owned_jobs:
            Application.query.filter_by(job_id=job.id).delete(synchronize_session=False)
            db.session.delete(job)
    elif user.role == 'student':
        Application.query.filter_by(student_id=user.id).delete(synchronize_session=False)

    db.session.delete(user)
    db.session.commit()
    flash(f'{user.role.title()} account removed successfully.', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/job/<int:job_id>/delete', methods=['POST'])
def admin_delete_job(job_id):
    if not login_required('admin'): return redirect(url_for('index'))
    job = db.get_or_404(Job, job_id)
    Application.query.filter_by(job_id=job.id).delete(synchronize_session=False)
    db.session.delete(job)
    db.session.commit()
    flash('Job / internship removed successfully.', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/application/<int:app_id>/delete', methods=['POST'])
def admin_delete_application(app_id):
    if not login_required('admin'): return redirect(url_for('index'))
    application = db.get_or_404(Application, app_id)
    db.session.delete(application)
    db.session.commit()
    flash('Application removed successfully.', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/job/add', methods=['POST'])
def admin_add_job():
    if not login_required('admin'): return redirect(url_for('index'))
    job=Job(title=request.form['title'],company=request.form['company'],location=request.form['location'],job_type=request.form['job_type'],mode=request.form['mode'],salary=request.form['salary'],skills=request.form['skills'],description=request.form['description'],deadline=request.form['deadline'])
    db.session.add(job); db.session.commit(); flash('Job added successfully.','success'); return redirect(url_for('admin'))

@app.route('/admin/application/<int:app_id>/<status>', methods=['POST'])
def admin_status(app_id,status):
    if not login_required('admin'): return redirect(url_for('index'))
    if status in {'Applied','Under Review','Shortlisted','Interview','Selected','Rejected'}:
        a=db.get_or_404(Application,app_id); a.status=status; db.session.commit()
    return redirect(url_for('admin'))

@app.route('/logout')
def logout(): session.clear(); return redirect(url_for('login'))

@app.errorhandler(413)
def too_large(e): flash('Resume file is too large. Maximum size is 5 MB.','error'); return redirect(request.referrer or url_for('profile'))

with app.app_context():
    db.create_all(); seed()

if __name__=='__main__': app.run(debug=True)
