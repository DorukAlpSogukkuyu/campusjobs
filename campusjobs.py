# Gerekli kütüphaneleri import edelim
from flask import Flask, render_template_string, request, redirect, url_for, flash, session, get_flashed_messages
import psycopg2 # PostgreSQL ile bağlantı için
import psycopg2.extras # Dictionary cursor için
import os # Dosya yolu işlemleri için
import re # Regex işlemleri için (şifre ve e-posta doğrulama)
from werkzeug.security import generate_password_hash, check_password_hash # Şifre hashleme
import urllib.parse
import datetime # Yıl bilgisi için

# Flask uygulamasını başlatalım
app = Flask(__name__)
app.secret_key = 'campusjobs_another_super_secret_key' # flash() ve session için

DB_HOST = "localhost"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASS = "1234"

def get_db_connection():
    """PostgreSQL veritabanına bağlantı oluşturur."""
    try:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS, client_encoding='utf8')
        return conn
    except Exception as e:
        print(f"Veritabanı bağlantı hatası: {e}")
        return None

#sifre en az 8 karakter Buyuk kucuk harf ve sayi
def is_strong_password(password):
    if len(password) < 8: return False
    if not re.search(r"[a-z]", password): return False
    if not re.search(r"[A-Z]", password): return False
    if not re.search(r"[0-9]", password): return False
    return True

#ogrenci okul maili check
def is_student_email(email):
    return email.endswith(".edu.tr") 

#giris ve kayit
@app.route('/register', methods=['GET'])
def register_choice():
    if 'user_id' in session:
        return redirect(url_for('index'))
    return render_template_string(REGISTER_CHOICE_TEMPLATE)

@app.route('/register/student', methods=['GET', 'POST'])
def register_student():
    if 'user_id' in session: return redirect(url_for('index'))
    
#ogrenci kayit formu    
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        school_email = request.form.get('school_email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not all([first_name, last_name, school_email, password, confirm_password]):
            flash("Lütfen tüm alanları doldurun.", "danger")
        elif password != confirm_password:
            flash("Şifreler eşleşmiyor.", "danger")
        elif not is_strong_password(password):
            flash("Şifre yeterince güçlü değil. En az 8 karakter olmalı, büyük harf, küçük harf ve sayı içermelidir.", "danger")
        elif not is_student_email(school_email):
            flash("Öğrenciler sadece okul e-posta adresleri (.edu.tr uzantılı) ile kayıt olabilirler.", "danger")
        else:
            password_hash_val = generate_password_hash(password)
            conn, cur = None, None
            try:
                conn = get_db_connection()
                if not conn: raise Exception("Veritabanı bağlantı hatası.")
                cur = conn.cursor()
                cur.execute("SELECT id FROM students WHERE school_email = %s", (school_email,))
                if cur.fetchone():
                    flash("Bu okul e-posta adresi zaten kayıtlı.", "danger")
                else:
                    cur.execute("""
                        INSERT INTO students (first_name, last_name, school_email, password_hash)
                        VALUES (%s, %s, %s, %s) RETURNING id;
                    """, (first_name, last_name, school_email, password_hash_val))
                    new_user_id = cur.fetchone()[0]
                    conn.commit()
                    
                    session['user_id'] = new_user_id
                    session['account_type'] = 'student' 
                    session['user_email'] = school_email
                    session['user_name'] = f"{first_name} {last_name}"
                    flash("Öğrenci olarak başarıyla kayıt oldunuz ve giriş yaptınız!", "success")
                    return redirect(url_for('index'))
            except Exception as e:
                if conn: conn.rollback()
                print(f"Öğrenci kayıt hatası: {e}")
                flash(f"Kayıt sırasında bir hata oluştu: {e}", "danger")
            finally:
                if cur: cur.close()
                if conn: conn.close()
        return render_template_string(REGISTER_STUDENT_FORM_TEMPLATE, form_data=request.form)
    return render_template_string(REGISTER_STUDENT_FORM_TEMPLATE, form_data={})

#employer giris ve kayit formu
@app.route('/register/employer', methods=['GET', 'POST'])
def register_employer():
    if 'user_id' in session: return redirect(url_for('index'))

    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        company_name = request.form.get('company_name', '') 

        if not all([first_name, last_name, email, password, confirm_password]):
            flash("Lütfen tüm alanları doldurun.", "danger")
        elif password != confirm_password:
            flash("Şifreler eşleşmiyor.", "danger")
        elif not is_strong_password(password):
            flash("Şifre yeterince güçlü değil. En az 8 karakter olmalı, büyük harf, küçük harf ve sayı içermelidir.", "danger")
        else:
            password_hash_val = generate_password_hash(password)
            conn, cur = None, None
            try:
                conn = get_db_connection()
                if not conn: raise Exception("Veritabanı bağlantı hatası.")
                cur = conn.cursor()
                cur.execute("SELECT id FROM employers WHERE email = %s", (email,))
                if cur.fetchone():
                    flash("Bu e-posta adresi zaten kayıtlı.", "danger")
                else:
                    cur.execute("""
                        INSERT INTO employers (first_name, last_name, email, password_hash, company_name)
                        VALUES (%s, %s, %s, %s, %s) RETURNING id;
                    """, (first_name, last_name, email, password_hash_val, company_name))
                    new_user_id = cur.fetchone()[0]
                    conn.commit()

                    session['user_id'] = new_user_id
                    session['account_type'] = 'employer'
                    session['user_email'] = email
                    session['user_name'] = f"{first_name} {last_name}"
                    if company_name: session['user_name'] += f" ({company_name})"
                    flash("İşveren olarak başarıyla kayıt oldunuz ve giriş yaptınız!", "success")
                    return redirect(url_for('index'))
            except Exception as e:
                if conn: conn.rollback()
                print(f"İşveren kayıt hatası: {e}")
                flash(f"Kayıt sırasında bir hata oluştu: {e}", "danger")
            finally:
                if cur: cur.close()
                if conn: conn.close()
        return render_template_string(REGISTER_EMPLOYER_FORM_TEMPLATE, form_data=request.form)
    return render_template_string(REGISTER_EMPLOYER_FORM_TEMPLATE, form_data={})

#giris yapma
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session: return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash("Lütfen e-posta ve şifrenizi girin.", "danger")
        else:
            conn, cur = None, None
            try:
                conn = get_db_connection()
                if not conn: raise Exception("Veritabanı bağlantı hatası.")
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                
                user_data, account_type_found = None, None

                cur.execute("SELECT id, first_name, last_name, school_email AS email, password_hash FROM students WHERE school_email = %s", (email,))
                user_candidate = cur.fetchone()
                if user_candidate:
                    user_data = user_candidate
                    account_type_found = 'student'
                else:
                    cur.execute("SELECT id, first_name, last_name, email, password_hash, company_name FROM employers WHERE email = %s", (email,))
                    user_candidate = cur.fetchone()
                    if user_candidate:
                        user_data = user_candidate
                        account_type_found = 'employer'

                if user_data and check_password_hash(user_data['password_hash'], password):
                    session['user_id'] = user_data['id']
                    session['account_type'] = account_type_found
                    session['user_email'] = user_data['email']
                    session['user_name'] = f"{user_data['first_name']} {user_data['last_name']}"
                    if account_type_found == 'employer' and user_data.get('company_name'):
                         session['user_name'] += f" ({user_data['company_name']})"
                    flash("Başarıyla giriş yaptınız!", "success")
                    return redirect(url_for('index'))
                else:
                    flash("Geçersiz e-posta veya şifre.", "danger")
            except Exception as e:
                print(f"Giriş sırasında hata: {e}")
                flash(f"Giriş sırasında bir hata oluştu: {e}", "danger")
            finally:
                if cur: cur.close()
                if conn: conn.close()
        return render_template_string(LOGIN_TEMPLATE, form_data=request.form)
    return render_template_string(LOGIN_TEMPLATE, form_data={})

#cikis yapma
@app.route('/logout')
def logout():
    session.clear()
    flash("Başarıyla çıkış yaptınız.", "success")
    return redirect(url_for('index'))

#giris yapmadan gormeyi engelleme
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Bu sayfayı görüntülemek için giriş yapmalısınız.", "warning")
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

#sadece student gorsun
def student_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if session.get('account_type') != 'student':
            flash("Bu sayfaya sadece öğrenciler erişebilir.", "danger")
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

#sadece employer gorsun
def employer_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if session.get('account_type') != 'employer':
            flash("Bu sayfaya sadece işverenler erişebilir.", "danger")
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

#sayfalarin baslangici ilan ekleme ve eksik alan kalirsa uyari mesajlari
@app.route('/')
def index():
    return render_template_string(INDEX_TEMPLATE)

@app.route('/add_job', methods=['GET', 'POST'])
@employer_required
def add_job():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        working_days = request.form.get('working_days')
        working_hours = request.form.get('working_hours')
        total_hours_str = request.form.get('total_hours')
        daily_salary_str = request.form.get('daily_salary')
        job_duration = request.form.get('job_duration')
        job_type = request.form.get('job_type')
        location = request.form.get('location')
        contact_email = request.form.get('contact_email') 
        employer_id = session['user_id']

        if not all([title, description, working_days, working_hours, total_hours_str, daily_salary_str, job_duration, job_type, location]):
            flash("Lütfen tüm zorunlu alanları doldurun.", "danger")
        else:
            try:
                total_hours = float(total_hours_str)
                daily_salary = int(daily_salary_str)
                hourly_salary = (daily_salary / total_hours) if total_hours > 0 else 0.0
                
                conn, cur = None, None
                try:
                    conn = get_db_connection()
                    if not conn: raise Exception("DB connection failed")
                    cur = conn.cursor()
                    cur.execute("""
                        INSERT INTO jobs (title, description, working_days, working_hours, total_hours, daily_salary, hourly_salary, job_duration, job_type, location, contact_email, employer_id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (title, description, working_days, working_hours, total_hours, daily_salary, hourly_salary, job_duration, job_type, location, contact_email or None, employer_id)) 
                    conn.commit()
                    flash("İş ilanı başarıyla eklendi!", "success")
                    return redirect(url_for('my_jobs'))
                except Exception as e:
                    if conn: conn.rollback()
                    print(f"İlan ekleme hatası: {e}")
                    flash(f"İlan eklenirken bir hata oluştu: {e}", "danger")
                finally:
                    if cur: cur.close()
                    if conn: conn.close()
            except ValueError:
                flash("Toplam saat ve günlük maaş sayısal değer olmalıdır.", "danger")
        return render_template_string(JOB_FORM_TEMPLATE, page_title="Yeni İş İlanı Ekle", job=request.form)
    return render_template_string(JOB_FORM_TEMPLATE, page_title="Yeni İş İlanı Ekle", job={})

@app.route('/edit_job/<int:job_id>', methods=['GET', 'POST'])
@employer_required
def edit_job(job_id):
    conn, cur = None, None
    try:
        conn = get_db_connection()
        if not conn:
            flash("Veritabanı bağlantı hatası.", "danger")
            return redirect(url_for('my_jobs'))
        
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        # İlanın bu işverene ait olup olmadığını kontrol et
        cur.execute("SELECT * FROM jobs WHERE id = %s AND employer_id = %s", (job_id, session['user_id']))
        job = cur.fetchone()

        if not job:
            flash("İlan bulunamadı veya bu ilanı düzenleme yetkiniz yok.", "danger")
            return redirect(url_for('my_jobs'))

        if request.method == 'POST':
            title = request.form.get('title')
            description = request.form.get('description')
            working_days = request.form.get('working_days')
            working_hours = request.form.get('working_hours')
            total_hours_str = request.form.get('total_hours')
            daily_salary_str = request.form.get('daily_salary')
            job_duration = request.form.get('job_duration')
            job_type = request.form.get('job_type')
            location = request.form.get('location')
            contact_email = request.form.get('contact_email')

            if not all([title, description, working_days, working_hours, total_hours_str, daily_salary_str, job_duration, job_type, location]):
                flash("Lütfen tüm zorunlu alanları doldurun.", "danger")
                # Formu güncel verilerle tekrar render etmek için job sözlüğünü request.form ile güncelleyelim
                current_form_data = dict(job) # Mevcut job verilerini al
                current_form_data.update(request.form) # Üzerine formdan gelenleri yaz
                return render_template_string(JOB_FORM_TEMPLATE, page_title="İlanı Güncelle", job=current_form_data)


            try:
                total_hours = float(total_hours_str)
                daily_salary = int(daily_salary_str)
                hourly_salary = (daily_salary / total_hours) if total_hours > 0 else 0.0

                cur.execute("""
                    UPDATE jobs SET 
                    title = %s, description = %s, working_days = %s, working_hours = %s, 
                    total_hours = %s, daily_salary = %s, hourly_salary = %s, 
                    job_duration = %s, job_type = %s, location = %s, contact_email = %s
                    WHERE id = %s AND employer_id = %s
                """, (title, description, working_days, working_hours, 
                      total_hours, daily_salary, hourly_salary, 
                      job_duration, job_type, location, contact_email or None, 
                      job_id, session['user_id']))
                conn.commit()
                flash("İş ilanı başarıyla güncellendi!", "success")
                return redirect(url_for('my_jobs'))
            except ValueError:
                flash("Toplam saat ve günlük maaş sayısal değer olmalıdır.", "danger")
                current_form_data = dict(job) 
                current_form_data.update(request.form)
                return render_template_string(JOB_FORM_TEMPLATE, page_title="İlanı Güncelle", job=current_form_data)
            except Exception as e:
                if conn: conn.rollback()
                print(f"İlan güncelleme hatası: {e}")
                flash(f"İlan güncellenirken bir hata oluştu: {e}", "danger")
        
        # GET isteği için veya POST'ta hata olursa formu dolu göster
        return render_template_string(JOB_FORM_TEMPLATE, page_title="İlanı Güncelle", job=job)

    except Exception as e:
        print(f"Edit job genel hata: {e}")
        flash("Bir hata oluştu.", "danger")
        return redirect(url_for('my_jobs'))
    finally:
        if cur: cur.close()
        if conn: conn.close()


@app.route('/apply_no_email_message')
@login_required
def apply_no_email_message():
    flash("İşveren iletişim e-postası belirtmemiştir. Bu nedenle e-posta ile başvuru yapılamamaktadır.", "warning")
    return redirect(request.referrer or url_for('get_jobs'))

#ilan listeleme filtreleme siralama ve db baglantilari
@app.route('/jobs')
@student_required
def get_jobs():
    conn, cur = None, None
    favorite_job_ids = []
    jobs_data = []
    job_types = []
    try:
        conn = get_db_connection()
        if not conn: raise Exception("DB connection failed")
        
        student_id = session['user_id']
        cur_fav = conn.cursor()
        cur_fav.execute("SELECT job_id FROM favorites WHERE student_id = %s", (student_id,))
        favorite_job_ids = [row[0] for row in cur_fav.fetchall()]
        cur_fav.close()

        search_term = request.args.get('search_term', '').strip()
        job_type_filter = request.args.get('job_type_filter', '')
        min_daily_salary = request.args.get('min_daily_salary', type=int)
        max_daily_salary = request.args.get('max_daily_salary', type=int)
        sort_by = request.args.get('sort_by', 'j.created_at') 
        sort_order = request.args.get('sort_order', 'DESC')

        query = """
            SELECT j.id, j.title, j.description, j.working_days, j.working_hours, j.total_hours, 
                   j.daily_salary, j.hourly_salary, j.job_duration, j.job_type, j.location, 
                   j.contact_email, e.first_name AS employer_first_name, e.last_name AS employer_last_name, e.email AS employer_main_email, e.company_name
            FROM jobs j
            JOIN employers e ON j.employer_id = e.id
        """
        filters = []
        params = []
        if search_term:
            filters.append("(LOWER(j.title) LIKE LOWER(%s) OR LOWER(j.description) LIKE LOWER(%s))")
            params.extend([f"%{search_term}%", f"%{search_term}%"])
        if job_type_filter: filters.append("LOWER(j.job_type) = LOWER(%s)"); params.append(job_type_filter)
        if min_daily_salary is not None: filters.append("j.daily_salary >= %s"); params.append(min_daily_salary)
        if max_daily_salary is not None: filters.append("j.daily_salary <= %s"); params.append(max_daily_salary)
        if filters: query += " WHERE " + " AND ".join(filters)
        
        allowed_sort_columns = {'created_at': 'j.created_at', 'id': 'j.id', 'title': 'j.title', 'daily_salary': 'j.daily_salary', 'hourly_salary': 'j.hourly_salary', 'total_hours': 'j.total_hours'}
        db_sort_column = allowed_sort_columns.get(sort_by, 'j.created_at')
        if sort_order.upper() not in ['ASC', 'DESC']: sort_order = 'DESC'
        query += f" ORDER BY {db_sort_column} {sort_order};"
        
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(query, tuple(params))
        jobs_data = cur.fetchall()

        cur.execute("SELECT DISTINCT job_type FROM jobs ORDER BY job_type;")
        job_types = [row['job_type'] for row in cur.fetchall() if row['job_type']]
    except Exception as e:
        print(f"İş ilanları çekilirken hata: {e}")
        flash(f"İş ilanları yüklenirken bir sorun oluştu: {e}", "danger")
    finally:
        if cur: cur.close()
        if conn: conn.close()
    return render_template_string(JOBS_LISTING_TEMPLATE, jobs_data=jobs_data, job_types=job_types, request=request, url_for=url_for, favorite_job_ids=favorite_job_ids, urllib=urllib, session=session)

#isveren ilanlarim sayfasi
@app.route('/my_jobs')
@employer_required
def my_jobs():
    conn, cur = None, None
    jobs_data = []
    employer_id = session['user_id']
    try:
        conn = get_db_connection()
        if not conn: raise Exception("DB connection failed")
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""
            SELECT id, title, description, working_days, working_hours, total_hours, 
                   daily_salary, hourly_salary, job_duration, job_type, location, contact_email, created_at
            FROM jobs WHERE employer_id = %s ORDER BY created_at DESC;
        """, (employer_id,))
        jobs_data = cur.fetchall()
    except Exception as e:
        print(f"İşveren ilanları çekilirken hata: {e}")
        flash(f"İlanlarınız yüklenirken bir sorun oluştu: {e}", "danger")
    finally:
        if cur: cur.close()
        if conn: conn.close()
    return render_template_string(MY_JOBS_TEMPLATE, jobs_data=jobs_data, url_for=url_for, session=session)

#is ilani silme
@app.route('/delete_job/<int:job_id>', methods=['POST'])
@employer_required
def delete_job(job_id):
    """Bir iş ilanını siler."""
    employer_id = session['user_id']
    conn, cur = None, None
    try:
        conn = get_db_connection()
        if not conn: 
            flash("Veritabanı bağlantı hatası.", "danger")
            return redirect(url_for('my_jobs'))
        
        cur = conn.cursor()
        # İlanın bu işverene ait olup olmadığını kontrol et
        cur.execute("SELECT id FROM jobs WHERE id = %s AND employer_id = %s", (job_id, employer_id))
        job_to_delete = cur.fetchone()

        if job_to_delete:
            # Favoriler tablosundaki ilgili kayıtlar ON DELETE CASCADE ile otomatik silinecek.
            cur.execute("DELETE FROM jobs WHERE id = %s", (job_id,))
            conn.commit()
            flash("İş ilanı başarıyla kaldırıldı.", "success")
        else:
            flash("İlan bulunamadı veya bu ilanı silme yetkiniz yok.", "danger")
            
    except Exception as e:
        if conn: conn.rollback()
        print(f"İlan silinirken hata: {e}")
        flash(f"İlan silinirken bir hata oluştu: {e}", "danger")
    finally:
        if cur: cur.close()
        if conn: conn.close()
    return redirect(url_for('my_jobs'))

#favorileme
@app.route('/toggle_favorite/<int:job_id>', methods=['POST'])
@student_required
def toggle_favorite(job_id):
    student_id = session['user_id']
    conn, cur = None, None
    try:
        conn = get_db_connection()
        if not conn: raise Exception("DB connection failed")
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM favorites WHERE student_id = %s AND job_id = %s", (student_id, job_id))
        is_favorited = cur.fetchone()
        if is_favorited:
            cur.execute("DELETE FROM favorites WHERE student_id = %s AND job_id = %s", (student_id, job_id))
            flash("İlan favorilerden çıkarıldı.", "success")
        else:
            cur.execute("INSERT INTO favorites (student_id, job_id) VALUES (%s, %s)", (student_id, job_id))
            flash("İlan favorilere eklendi.", "success")
        conn.commit()
    except Exception as e:
        if conn: conn.rollback()
        print(f"Favori işlemi hatası: {e}")
        flash(f"Favori işlemi sırasında bir hata oluştu: {e}", "danger")
    finally:
        if cur: cur.close()
        if conn: conn.close()
    
    redirect_url = request.referrer
    if 'redirect_to_favorites' in request.form:
        redirect_url = url_for('show_favorites')
    return redirect(redirect_url or url_for('get_jobs'))

#favori sayfasi
@app.route('/favorites')
@student_required
def show_favorites():
    conn, cur = None, None
    jobs_data = []
    student_id = session['user_id']
    favorite_job_ids = [] 
    try:
        conn = get_db_connection()
        if not conn: raise Exception("DB connection failed")
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""
            SELECT j.id, j.title, j.description, j.working_days, j.working_hours, j.total_hours, 
                   j.daily_salary, j.hourly_salary, j.job_duration, j.job_type, j.location, 
                   j.contact_email, e.first_name AS employer_first_name, e.last_name AS employer_last_name, e.email AS employer_main_email, e.company_name
            FROM jobs j
            JOIN favorites f ON j.id = f.job_id
            JOIN employers e ON j.employer_id = e.id
            WHERE f.student_id = %s ORDER BY f.created_at DESC;
        """, (student_id,))
        jobs_data = cur.fetchall()
        favorite_job_ids = [job['id'] for job in jobs_data] 
    except Exception as e:
        print(f"Favori ilanları çekme hatası: {e}")
        flash(f"Favori ilanlarınız yüklenirken bir sorun oluştu: {e}", "danger")
    finally:
        if cur: cur.close()
        if conn: conn.close()
    return render_template_string(FAVORITES_PAGE_TEMPLATE, jobs_data=jobs_data, url_for=url_for, favorite_job_ids=favorite_job_ids, urllib=urllib, session=session)

# HTML kismi

COMMON_STYLES = """
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
    body { font-family: 'Montserrat', sans-serif; margin: 0; padding: 0; background-color: #f4f7f6; color: #333a45; display: flex; flex-direction: column; min-height: 100vh; }
    .navbar { background-color: #004080; padding: 12px 25px; color: white; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 5px rgba(0,0,0,0.15); }
    .navbar a { color: white; text-decoration: none; margin: 0 12px; padding: 8px 15px; border-radius: 5px; transition: background-color 0.3s ease; font-weight: 500; }
    .navbar a:hover, .navbar a.active { background-color: #0056b3; }
    .navbar .logo { font-size: 1.6em; font-weight: 700; }
    .navbar .user-info { font-size: 0.95em; margin-right: 15px; }
    .container { max-width: 950px; margin: 30px auto; background-color: #fff; padding: 30px 35px; border-radius: 10px; box-shadow: 0 5px 20px rgba(0,0,0,0.1); flex-grow: 1; }
    h1, h2 { color: #004080; text-align: center; margin-bottom: 30px; font-weight: 600;}
    h1 { font-size: 2.2em; } h2 { font-size: 1.8em; }
    label { display: block; margin-bottom: 9px; font-weight: 500; color: #34495e; font-size: 1em; }
    input[type="text"], input[type="email"], input[type="tel"], input[type="number"], input[type="password"], textarea, select { width: 100%; padding: 14px; margin-bottom: 22px; border: 1px solid #ced4da; border-radius: 7px; box-sizing: border-box; font-family: 'Montserrat', sans-serif; font-size: 1em; color: #333; transition: border-color 0.2s ease, box-shadow 0.2s ease; }
    input:focus, textarea:focus, select:focus { border-color: #007bff; box-shadow: 0 0 0 0.2rem rgba(0,123,255,.25); outline: none; }
    textarea { min-height: 120px; resize: vertical; }
    .button, button[type="submit"], .button-link { background-color: #007bff; color: white !important; padding: 14px 28px; border: none; border-radius: 28px; cursor: pointer; font-size: 1.1em; font-weight: 600; text-decoration: none; display: inline-block; text-align: center; transition: background-color 0.3s ease, transform 0.2s ease; margin-top: 12px; }
    .button:hover, button[type="submit"]:hover, .button-link:hover { background-color: #0056b3; transform: translateY(-2px); }
    .button-danger { background-color: #dc3545; } /* Kırmızı buton stili */
    .button-danger:hover { background-color: #c82333; } /* Kırmızı buton hover stili */
    .button-edit { background-color: #ffc107; color: #212529 !important; } /* Sarı/turuncu güncelleme butonu */
    .button-edit:hover { background-color: #e0a800; }
    .form-group { margin-bottom: 22px; }
    .flash-messages { list-style-type: none; padding: 0; margin: 0 0 22px 0; }
    .flash-messages li { padding: 14px 20px; margin-bottom: 12px; border-radius: 7px; font-size: 1em; border: 1px solid transparent; }
    .flash-messages .success { background-color: #d1e7dd; color: #0f5132; border-color: #badbcc; }
    .flash-messages .danger { background-color: #f8d7da; color: #842029; border-color: #f5c2c7; }
    .flash-messages .warning { background-color: #fff3cd; color: #664d03; border-color: #ffecb5; }
    .footer { text-align: center; padding: 25px; background-color: #333a45; color: #f4f7f6; font-size: 0.95em; margin-top: auto; }
    .footer a { color: #00aaff; text-decoration: none; } .footer a:hover { text-decoration: underline; }
    .job-listing { border: 1px solid #e0e0e0; padding: 22px; margin-bottom: 22px; border-radius: 10px; background-color: #fff; position: relative; transition: box-shadow 0.3s ease; }
    .job-listing:hover { box-shadow: 0 7px 25px rgba(0,0,0,0.1); }
    .job-summary { display: flex; justify-content: space-between; align-items: center; cursor: pointer; }
    .job-summary-info h3 { margin-top: 0; margin-bottom: 10px; color: #007bff; font-size: 1.45em; font-weight: 600;}
    .job-summary-info .salary-info { font-size: 1.05em; font-weight: 500; color: #28a745; margin-bottom: 6px; }
    .job-summary-info .employer-info { font-size: 0.95em; color: #5a6268; }
    .job-actions { display:flex; align-items:center; gap: 12px; }
    .job-details-toggle { font-size: 0.95em; color: #007bff; text-decoration: none; font-weight: 500; padding: 7px 14px; border: 1px solid #007bff; border-radius: 22px; transition: background-color 0.2s, color 0.2s; }
    .job-details-toggle:hover { background-color: #007bff; color: #fff; }
    .job-details { display: none; margin-top: 22px; padding-top: 22px; border-top: 1px dashed #ccc; font-size: 0.95em; line-height: 1.7; }
    .job-details p { margin: 9px 0; color: #454f5b; } .job-details strong { color: #2c3e50; font-weight: 600;}
    .job-details .actions-footer { margin-top: 20px; text-align: right; display: flex; justify-content: flex-end; gap: 10px; } /* Silme ve Güncelleme butonu için */
    .apply-button { margin-top: 18px; padding: 12px 25px; background-color: #28a745; font-size: 1.05em; }
    .apply-button:hover { background-color: #218838; }
    .favorite-btn { background: none; border: none; font-size: 2em; cursor: pointer; color: #ced4da; transition: color 0.2s ease; padding: 0 6px; }
    .favorite-btn.favorited { color: #ffc107; }
    .no-jobs { text-align: center; color: #6c757d; font-size: 1.15em; margin-top: 35px; padding: 30px; background-color: #f8f9fa; border-radius: 8px;}
    .filters-form { background-color: #f8f9fa; padding: 22px; border-radius: 10px; margin-bottom: 35px; display: flex; flex-wrap: wrap; gap: 20px; align-items: flex-end; border: 1px solid #e0e0e0;}
    .filters-form label { font-weight: 500; margin-bottom: 7px; display: block; font-size: 0.95em; color: #495057;}
    .filters-form input[type="text"], .filters-form input[type="number"], .filters-form select { padding: 12px; border: 1px solid #ced4da; border-radius: 6px; box-sizing: border-box; width: 100%; font-family: 'Montserrat', sans-serif; font-size: 1em; margin-bottom:0; }
    .filters-form .form-group { flex: 1; min-width: 160px; }
    .filters-form button[type="submit"] { padding: 12px 22px; background-color: #007bff; color: white; border: none; border-radius: 22px; cursor: pointer; height: auto; font-weight: 500; font-size: 1em; transition: background-color 0.2s ease; margin-top:0; align-self: flex-end; }
    .filters-form button[type="submit"]:hover { background-color: #0056b3; }
    small { display: block; color: #7f8c8d; margin-top: -15px; margin-bottom:15px; font-size: 0.9em; }
</style>
"""

NAVBAR_TEMPLATE = f"""
<nav class="navbar">
    <a href="{{{{ url_for('index') }}}}" class="logo">CampusJobs</a>
    <div>
        {{% if session.user_id %}}
            <span class="user-info">Hoşgeldin, {{{{ session.user_name }}}}!</span>
            {{% if session.account_type == 'student' %}}
                <a href="{{{{ url_for('get_jobs') }}}}" class="{{{{ 'active' if request.endpoint == 'get_jobs' else '' }}}}">İlanları Listele</a>
                <a href="{{{{ url_for('show_favorites') }}}}" class="{{{{ 'active' if request.endpoint == 'show_favorites' else '' }}}}">Favorilerim</a>
            {{% elif session.account_type == 'employer' %}}
                <a href="{{{{ url_for('my_jobs') }}}}" class="{{{{ 'active' if request.endpoint == 'my_jobs' else '' }}}}">İlanlarım</a>
                <a href="{{{{ url_for('add_job') }}}}" class="{{{{ 'active' if request.endpoint == 'add_job' else '' }}}}">Yeni İlan Ekle</a>
            {{% endif %}}
            <a href="{{{{ url_for('logout') }}}}">Çıkış Yap</a>
        {{% else %}}
            <a href="{{{{ url_for('login') }}}}" class="{{{{ 'active' if request.endpoint == 'login' else '' }}}}">Giriş Yap</a>
            <a href="{{{{ url_for('register_choice') }}}}" class="{{{{ 'active' if request.endpoint in ['register_choice', 'register_student', 'register_employer'] else '' }}}}">Hesap Oluştur</a>
        {{% endif %}}
    </div>
</nav>
"""

FOOTER_TEMPLATE = f"""
<footer class="footer">
    <p>&copy; {{{{ current_year }}}} CampusJobs. Tüm hakları saklıdır.</p>
</footer>
"""

INDEX_TEMPLATE = f"""
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8"> <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CampusJobs - Kampüste Fırsatları Yakala!</title> {COMMON_STYLES}
    <style>
        .hero-section {{ background-color: #ffffff; color: #0056b3; padding: 70px 25px; text-align: center; border-bottom: 1px solid #e0e0e0; }}
        .hero-section h1 {{ margin: 0 0 18px 0; font-size: 3.5em; font-weight: 700; color: #004080; }}
        .hero-section p.subtitle {{ font-size: 1.3em; margin-bottom: 35px; max-width: 800px; margin-left: auto; margin-right: auto; color: #0056b3; font-weight: 500; line-height: 1.85; }}
        .cta-buttons .button {{ font-size: 1.15em; padding: 15px 38px; margin: 0 12px; }}
        .features-section {{ padding: 60px 25px; background-color: #f9fafb; text-align: center; }}
        .features-section h2 {{ color: #004080; margin-bottom: 45px; font-size: 2.4em;}}
        .features-grid {{ display: flex; justify-content: center; gap: 35px; flex-wrap: wrap; max-width: 1100px; margin: 0 auto; }}
        .feature-item {{ background-color: #fff; padding: 30px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.08); flex: 1; min-width: 300px; max-width: 340px; }}
        .feature-item h3 {{ color: #007bff; margin-top: 0; margin-bottom: 12px; font-size: 1.4em; }}
        .feature-item p {{ font-size: 1em; line-height: 1.65; color: #333a45; }}
    </style>
</head>
<body> {NAVBAR_TEMPLATE}
    <header class="hero-section">
        <h1>CampusJobs'a Hoş Geldiniz!</h1>
        <p class="subtitle">Kampüs hayatınızı kolaylaştıracak, öğrencilere özel part-time ve full-time iş fırsatlarını keşfedin. İşverenler için ise ODTÜ'nün dinamik ve yetenekli öğrencilerine ulaşmanın en kolay yolu! Amacımız, öğrencilerle kampüs içi ve çevresindeki işverenleri buluşturarak karşılıklı fayda sağlamaktır.</p>
        {{% if not session.user_id %}}
        <div class="cta-buttons"> <a href="{{{{ url_for('login') }}}}" class="button">Giriş Yap</a> <a href="{{{{ url_for('register_choice') }}}}" class="button button-success">Hesap Oluştur</a> </div>
        {{% else %}}
            {{% if session.account_type == 'student' %}} <div class="cta-buttons"> <a href="{{{{ url_for('get_jobs') }}}}" class="button">İlanları Keşfet</a> </div>
            {{% elif session.account_type == 'employer' %}} <div class="cta-buttons"> <a href="{{{{ url_for('add_job') }}}}" class="button">Yeni İlan Ekle</a> </div>
            {{% endif %}}
        {{% endif %}}
    </header>
    <section class="features-section">
        <h2>Neden CampusJobs?</h2>
        <div class="features-grid">
            <div class="feature-item"><h3>Öğrenciler İçin</h3><p>Ders programına uygun esnek işler bul, deneyim kazan, harçlığını çıkar. Kariyerine ilk adımı kampüsünde at!</p></div>
            <div class="feature-item"><h3>İşverenler İçin</h3><p>ODTÜ'nün parlak ve motive öğrencilerine kolayca ulaş. İhtiyaç duyduğun pozisyonlar için genç yetenekleri keşfet.</p></div>
            <div class="feature-item"><h3>Kolay Kullanım</h3><p>Basit ve kullanıcı dostu arayüzümüzle aradığın işi veya çalışanı hızla bul. Karmaşık süreçlere son!</p></div>
        </div>
    </section>
    {{% set current_year = datetime.datetime.now().year %}}
    {FOOTER_TEMPLATE}
</body></html>"""

REGISTER_CHOICE_TEMPLATE = f"""
<!DOCTYPE html><html lang="tr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hesap Türü Seçin - CampusJobs</title>{COMMON_STYLES}
    <style>
        body {{ background-color: #ffffff; }}
        .choice-container {{ display: flex; flex-grow: 1; width: 100%; margin-top: 0; }}
        .choice-section {{ flex: 1; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 60px 35px; text-align: center; background-size: cover; background-position: center; position: relative; color: #fff; min-height: calc(100vh - 70px - 80px); }}
        .choice-section::before {{ content: ""; position: absolute; top: 0; left: 0; right: 0; bottom: 0; background-color: rgba(0, 25, 70, 0.7); z-index: 1; }}
        .choice-section .content {{ position: relative; z-index: 2; }}
        .choice-section h2 {{ font-size: 2.8em; margin-bottom: 22px; font-weight: 600; color: #fff; }}
        .choice-section p {{ font-size: 1.15em; margin-bottom: 35px; max-width: 480px; font-weight: 500; opacity: 0.95; line-height: 1.75; color: #e0e0e0; }}
        .choice-section .button {{ font-size: 1.15em; padding: 15px 40px; background-color: #007bff; border: 2px solid #007bff; }}
        .choice-section .button:hover {{ background-color: #0056b3; border-color: #0056b3; }}
        #student-choice-section {{ background-image: url('https://i.postimg.cc/CLHkNPWM/czech-University-Students.jpg'); }}
        #employer-choice-section {{ background-image: url('https://i.postimg.cc/0N3wQLJn/isci-isveren-uyusmazliklari-iscilik-alacaklari-ve-tazminatlar.jpg'); }}
        @media (max-width: 768px) {{ .choice-container {{ flex-direction: column; }} .choice-section {{ min-height: 400px; }} .choice-section h2 {{ font-size: 2.2em; }} }}
    </style></head><body> {NAVBAR_TEMPLATE}
    <main class="choice-container">
        <section id="student-choice-section" class="choice-section"><div class="content"><h2>Öğrenci Hesabı Oluştur</h2><p>Kampüsteki en iyi iş fırsatlarını yakala, deneyim kazan ve bütçene katkıda bulun!</p><a href="{{{{ url_for('register_student') }}}}" class="button">Öğrenci Olarak Kaydol</a></div></section>
        <section id="employer-choice-section" class="choice-section"><div class="content"><h2>İşveren Hesabı Oluştur</h2><p>ODTÜ'nün dinamik ve yetenekli öğrencilerine ulaşarak ekibinizi güçlendirin.</p><a href="{{{{ url_for('register_employer') }}}}" class="button">İşveren Olarak Kaydol</a></div></section>
    </main>
    {{% set current_year = datetime.datetime.now().year %}}
    {FOOTER_TEMPLATE} </body></html>"""

REGISTER_STUDENT_FORM_TEMPLATE = f"""
<!DOCTYPE html><html lang="tr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Öğrenci Hesabı Oluştur - CampusJobs</title>{COMMON_STYLES}</head><body> {NAVBAR_TEMPLATE}
    <div class="container"> {{% with messages = get_flashed_messages(with_categories=true) %}} {{% if messages %}} <ul class="flash-messages"> {{% for category, message in messages %}} <li class="{{{{ category }}}}">{{{{ message }}}}</li> {{% endfor %}} </ul> {{% endif %}} {{% endwith %}}
        <a href="{{{{ url_for('register_choice') }}}}" class="back-link" style="display:inline-block; margin-bottom:25px;">&larr; Hesap Türü Seçimine Dön</a>
        <h1>Öğrenci Hesabı Oluştur</h1>
        <form method="POST">
            <div class="form-group"><label for="first_name">Ad (*):</label><input type="text" id="first_name" name="first_name" value="{{{{ form_data.first_name or '' }}}}" required></div>
            <div class="form-group"><label for="last_name">Soyad (*):</label><input type="text" id="last_name" name="last_name" value="{{{{ form_data.last_name or '' }}}}" required></div>
            <div class="form-group"><label for="school_email">Okul E-posta Adresi (*):</label><input type="email" id="school_email" name="school_email" value="{{{{ form_data.school_email or '' }}}}" placeholder="ornek@okul.edu.tr" required><small>Lütfen .edu.tr uzantılı okul e-posta adresinizi kullanın.</small></div>
            <div class="form-group"><label for="password">Şifre (*):</label><input type="password" id="password" name="password" required><small>En az 8 karakter, büyük/küçük harf ve sayı içermelidir.</small></div>
            <div class="form-group"><label for="confirm_password">Şifre Tekrar (*):</label><input type="password" id="confirm_password" name="confirm_password" required></div>
            <button type="submit" class="button">Hesap Oluştur</button>
        </form></div> 
    {{% set current_year = datetime.datetime.now().year %}}
    {FOOTER_TEMPLATE} </body></html>"""

REGISTER_EMPLOYER_FORM_TEMPLATE = f"""
<!DOCTYPE html><html lang="tr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>İşveren Hesabı Oluştur - CampusJobs</title>{COMMON_STYLES}</head><body> {NAVBAR_TEMPLATE}
    <div class="container"> {{% with messages = get_flashed_messages(with_categories=true) %}} {{% if messages %}} <ul class="flash-messages"> {{% for category, message in messages %}} <li class="{{{{ category }}}}">{{{{ message }}}}</li> {{% endfor %}} </ul> {{% endif %}} {{% endwith %}}
        <a href="{{{{ url_for('register_choice') }}}}" class="back-link" style="display:inline-block; margin-bottom:25px;">&larr; Hesap Türü Seçimine Dön</a>
        <h1>İşveren Hesabı Oluştur</h1>
        <form method="POST">
            <div class="form-group"><label for="first_name">Ad (*):</label><input type="text" id="first_name" name="first_name" value="{{{{ form_data.first_name or '' }}}}" required></div>
            <div class="form-group"><label for="last_name">Soyad (*):</label><input type="text" id="last_name" name="last_name" value="{{{{ form_data.last_name or '' }}}}" required></div>
            <div class="form-group"><label for="email">E-posta Adresi (*):</label><input type="email" id="email" name="email" value="{{{{ form_data.email or '' }}}}" placeholder="ornek@sirket.com" required></div>
            <div class="form-group"><label for="company_name">Şirket Adı (Opsiyonel):</label><input type="text" id="company_name" name="company_name" value="{{{{ form_data.company_name or '' }}}}"></div>
            <div class="form-group"><label for="password">Şifre (*):</label><input type="password" id="password" name="password" required><small>En az 8 karakter, büyük/küçük harf ve sayı içermelidir.</small></div>
            <div class="form-group"><label for="confirm_password">Şifre Tekrar (*):</label><input type="password" id="confirm_password" name="confirm_password" required></div>
            <button type="submit" class="button">Hesap Oluştur</button>
        </form></div> 
    {{% set current_year = datetime.datetime.now().year %}}
    {FOOTER_TEMPLATE} </body></html>"""

LOGIN_TEMPLATE = f"""
<!DOCTYPE html><html lang="tr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Giriş Yap - CampusJobs</title>{COMMON_STYLES}</head><body> {NAVBAR_TEMPLATE}
    <div class="container"> {{% with messages = get_flashed_messages(with_categories=true) %}} {{% if messages %}} <ul class="flash-messages"> {{% for category, message in messages %}} <li class="{{{{ category }}}}">{{{{ message }}}}</li> {{% endfor %}} </ul> {{% endif %}} {{% endwith %}}
        <h1>Giriş Yap</h1>
        <form method="POST">
            <div class="form-group"><label for="email">E-posta Adresi:</label><input type="email" id="email" name="email" value="{{{{ form_data.email or '' }}}}" required></div>
            <div class="form-group"><label for="password">Şifre:</label><input type="password" id="password" name="password" required></div>
            <button type="submit" class="button">Giriş Yap</button>
        </form>
        <p style="text-align: center; margin-top: 25px; font-size: 1em;">Hesabın yok mu? <a href="{{{{ url_for('register_choice') }}}}">Hemen Hesap Oluştur</a></p>
    </div> 
    {{% set current_year = datetime.datetime.now().year %}}
    {FOOTER_TEMPLATE} </body></html>"""

JOB_FORM_TEMPLATE = f"""
<!DOCTYPE html><html lang="tr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{{{ page_title }}}} - CampusJobs</title>{COMMON_STYLES}</head><body> {NAVBAR_TEMPLATE}
    <div class="container"> {{% with messages = get_flashed_messages(with_categories=true) %}} {{% if messages %}} <ul class="flash-messages"> {{% for category, message in messages %}} <li class="{{{{ category }}}}">{{{{ message }}}}</li> {{% endfor %}} </ul> {{% endif %}} {{% endwith %}}
        <a href="{{{{ url_for('my_jobs') }}}}" class="back-link" style="display:inline-block; margin-bottom:25px;">&larr; İlanlarıma Dön</a>
        <h1>{{{{ page_title }}}}</h1>
        <form method="POST">
            <div class="form-group"><label for="title">İş Başlığı (*):</label><input type="text" id="title" name="title" value="{{{{ job.title or '' }}}}" required></div>
            <div class="form-group"><label for="description">Açıklama (*):</label><textarea id="description" name="description" required>{{{{ job.description or '' }}}}</textarea></div>
            <div class="form-group"><label for="working_days">Çalışma Günleri (*):</label><input type="text" id="working_days" name="working_days" value="{{{{ job.working_days or 'Pazartesi-Cuma' }}}}" placeholder="Örn: Pazartesi-Cuma" required></div>
            <div class="form-group"><label for="working_hours">Çalışma Saatleri (*):</label><input type="text" id="working_hours" name="working_hours" value="{{{{ job.working_hours or '09:00-17:00' }}}}" placeholder="Örn: 09:00-17:00" required></div>
            <div class="form-group"><label for="total_hours">Günlük Toplam Çalışma Saati (*):</label><input type="number" step="0.1" id="total_hours" name="total_hours" value="{{{{ job.total_hours or '' }}}}" placeholder="Örn: 8" required><small>Saatlik ücret bunun üzerinden hesaplanacaktır.</small></div>
            <div class="form-group"><label for="daily_salary">Günlük Maaş (TL) (*):</label><input type="number" id="daily_salary" name="daily_salary" value="{{{{ job.daily_salary or '' }}}}" placeholder="Örn: 800" required></div>
            <div class="form-group"><label for="job_duration">İş Süresi (*):</label><input type="text" id="job_duration" name="job_duration" value="{{{{ job.job_duration or 'Sürekli' }}}}" placeholder="Örn: Sürekli, 3 Ay, Proje Bazlı" required></div>
            <div class="form-group"><label for="job_type">İş Tipi (*):</label><input type="text" id="job_type" name="job_type" value="{{{{ job.job_type or '' }}}}" placeholder="Örn: Kafe, Restoran, Ofis" required></div>
            <div class="form-group"><label for="location">Konum (*):</label><input type="text" id="location" name="location" value="{{{{ job.location or '' }}}}" placeholder="Örn: ODTÜ Kampüsü, Çankaya/Ankara" required></div>
            <div class="form-group"><label for="contact_email">İlan İletişim E-postası (Opsiyonel):</label><input type="email" id="contact_email" name="contact_email" value="{{{{ job.contact_email or '' }}}}" placeholder="profilinizdeki_mail@adresiniz.com"><small>Boş bırakırsanız profilinizdeki e-posta adresi ({{{{ session.user_email }}}}) kullanılır.</small></div>
            <button type="submit" class="button">İlanı Kaydet</button>
        </form></div> 
    {{% set current_year = datetime.datetime.now().year %}}
    {FOOTER_TEMPLATE} </body></html>"""

JOBS_LISTING_TEMPLATE = f"""
<!DOCTYPE html><html lang="tr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>İş İlanları - CampusJobs</title>{COMMON_STYLES}</head><body> {NAVBAR_TEMPLATE}
    <div class="container"> {{% with messages = get_flashed_messages(with_categories=true) %}} {{% if messages %}} <ul class="flash-messages"> {{% for category, message in messages %}} <li class="{{{{ category }}}}">{{{{ message }}}}</li> {{% endfor %}} </ul> {{% endif %}} {{% endwith %}}
        <h1>Mevcut İş İlanları</h1>
        <form method="GET" action="{{{{ url_for('get_jobs') }}}}" class="filters-form">
            <div class="form-group"><label for="search_term">Ara (Başlık/Açıklama):</label><input type="text" name="search_term" id="search_term" value="{{{{ request.args.get('search_term', '') }}}}"></div>
            <div class="form-group"><label for="job_type_filter">İş Tipi:</label><select name="job_type_filter" id="job_type_filter"><option value="">Tümü</option>{{% for jt in job_types %}}<option value="{{{{ jt }}}}" {{{{ 'selected' if jt == request.args.get('job_type_filter') else '' }}}}>{{{{ jt }}}}</option>{{% endfor %}}</select></div>
            <div class="form-group"><label for="min_daily_salary">Min Günlük Maaş (TL):</label><input type="number" name="min_daily_salary" id="min_daily_salary" value="{{{{ request.args.get('min_daily_salary', '') }}}}" placeholder="Örn: 500"></div>
            <div class="form-group"><label for="max_daily_salary">Max Günlük Maaş (TL):</label><input type="number" name="max_daily_salary" id="max_daily_salary" value="{{{{ request.args.get('max_daily_salary', '') }}}}" placeholder="Örn: 1000"></div>
            <div class="form-group"><label for="sort_by">Sırala:</label><select name="sort_by" id="sort_by">
                <option value="created_at" {{{{ 'selected' if request.args.get('sort_by', 'created_at') == 'created_at' else '' }}}}>Eklenme Tarihi</option>
                <option value="title" {{{{ 'selected' if request.args.get('sort_by') == 'title' else '' }}}}>Başlık</option>
                <option value="daily_salary" {{{{ 'selected' if request.args.get('sort_by') == 'daily_salary' else '' }}}}>Günlük Maaş</option>
                <option value="hourly_salary" {{{{ 'selected' if request.args.get('sort_by') == 'hourly_salary' else '' }}}}>Saatlik Maaş</option>
            </select></div>
            <div class="form-group"><label for="sort_order">Sıralama Yönü:</label><select name="sort_order" id="sort_order"><option value="DESC" {{{{ 'selected' if request.args.get('sort_order', 'DESC') == 'DESC' else '' }}}}>Azalan</option><option value="ASC" {{{{ 'selected' if request.args.get('sort_order') == 'ASC' else '' }}}}>Artan</option></select></div>
            <button type="submit">Filtrele / Sırala</button></form>
        {{% if not jobs_data %}}<p class='no-jobs'>Bu kriterlere uygun iş ilanı bulunmamaktadır.</p>{{% else %}}
            {{% for job in jobs_data %}}
            <div class='job-listing'> <div class="job-summary" onclick="toggleDetails('details-{{{{ loop.index }}}}')"> <div class="job-summary-info"><h3>{{{{ job.title }}}}</h3><p class="salary-info">Günlük: {{{{ job.daily_salary }}}} TL / Saatlik: {{{{ "%.2f"|format(job.hourly_salary) }}}} TL</p><p class="employer-info">İşveren: {{{{ job.employer_first_name }}}} {{{{ job.employer_last_name }}}} {{{{ '('+job.company_name+')' if job.company_name else '' }}}}</p></div> <div class="job-actions"> <form method="POST" action="{{{{ url_for('toggle_favorite', job_id=job.id) }}}}" style="display: inline;"><button type="submit" class="favorite-btn {{{{ 'favorited' if job.id in favorite_job_ids else '' }}}}" title="Favorilere Ekle/Çıkar">{{{{ '★' if job.id in favorite_job_ids else '☆' }}}}</button></form> <a href="javascript:void(0);" class="job-details-toggle" id="toggle-btn-{{{{ loop.index }}}}">Detayları Gör</a></div></div>
                <div class="job-details" id="details-{{{{ loop.index }}}}">
                    <p><strong>Açıklama:</strong> {{{{ job.description }}}}</p><p><strong>Çalışma Günleri:</strong> {{{{ job.working_days }}}}</p><p><strong>Çalışma Saatleri:</strong> {{{{ job.working_hours }}}}</p><p><strong>Günlük Toplam Saat:</strong> {{{{ job.total_hours }}}}</p><p><strong>İş Süresi:</strong> {{{{ job.job_duration }}}}</p><p><strong>İş Tipi:</strong> {{{{ job.job_type }}}}</p><p><strong>Konum:</strong> {{{{ job.location }}}}</p>
                    {{% set display_email = job.contact_email or job.employer_main_email %}}
                    {{% if display_email %}}<p><strong>İletişim E-posta:</strong> <a href='mailto:{{{{ display_email }}}}'>{{{{ display_email }}}}</a></p>{{% endif %}}
                    {{% if display_email %}}
                        {{% set email_subject = "İş Başvurusu: " + job.title + " (CampusJobs)" %}}
                        {{% set email_body = "Merhaba " + (job.employer_first_name or 'Yetkili') + ",\\n\\nCampusJobs üzerinden yayınlanan '" + job.title + "' başlıklı iş ilanınıza başvurmak istiyorum.\\n\\nSaygılarımla," %}}
                        <a href="mailto:{{{{ display_email }}}}?subject={{{{ urllib.parse.quote_plus(email_subject) }}}}&body={{{{ urllib.parse.quote_plus(email_body) }}}}" class="button apply-button">E-posta ile Başvur</a>
                    {{% else %}}<a href="{{{{ url_for('apply_no_email_message') }}}}" class="button apply-button">Başvur</a>{{% endif %}}
                </div></div> {{% endfor %}} {{% endif %}}</div> 
    {{% set current_year = datetime.datetime.now().year %}}
    {FOOTER_TEMPLATE} <script>function toggleDetails(id){{var el=document.getElementById(id); var btn=document.getElementById(id.replace('details-','toggle-btn-')); if(el.style.display==="none"||el.style.display===""){{el.style.display="block";if(btn)btn.textContent="Detayları Gizle";}}else{{el.style.display="none";if(btn)btn.textContent="Detayları Gör";}}}}</script></body></html>"""

MY_JOBS_TEMPLATE = f"""
<!DOCTYPE html><html lang="tr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>İlanlarım - CampusJobs</title>{COMMON_STYLES}</head><body> {NAVBAR_TEMPLATE}
    <div class="container"> {{% with messages = get_flashed_messages(with_categories=true) %}} {{% if messages %}} <ul class="flash-messages"> {{% for category, message in messages %}} <li class="{{{{ category }}}}">{{{{ message }}}}</li> {{% endfor %}} </ul> {{% endif %}} {{% endwith %}}
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px;"><h1>Yayınladığım İlanlar</h1><a href="{{{{ url_for('add_job') }}}}" class="button button-success">Yeni İlan Ekle</a></div>
        {{% if not jobs_data %}}<p class='no-jobs'>Henüz yayınladığınız bir iş ilanı bulunmamaktadır.</p>{{% else %}}
            {{% for job in jobs_data %}}
            <div class='job-listing'><div class="job-summary" onclick="toggleDetails('details-{{{{ loop.index }}}}')"><div class="job-summary-info"><h3>{{{{ job.title }}}}</h3><p class="salary-info">Günlük: {{{{ job.daily_salary }}}} TL / Saatlik: {{{{ "%.2f"|format(job.hourly_salary) }}}} TL</p><p class="employer-info">Yayın Tarihi: {{{{ job.created_at.strftime('%d-%m-%Y %H:%M') }}}}</p></div><div class="job-actions"><a href="javascript:void(0);" class="job-details-toggle" id="toggle-btn-{{{{ loop.index }}}}">Detayları Gör</a></div></div>
                <div class="job-details" id="details-{{{{ loop.index }}}}">
                    <p><strong>Açıklama:</strong> {{{{ job.description }}}}</p><p><strong>Çalışma Günleri:</strong> {{{{ job.working_days }}}}</p><p><strong>Çalışma Saatleri:</strong> {{{{ job.working_hours }}}}</p><p><strong>Günlük Toplam Saat:</strong> {{{{ job.total_hours }}}}</p><p><strong>İş Süresi:</strong> {{{{ job.job_duration }}}}</p><p><strong>İş Tipi:</strong> {{{{ job.job_type }}}}</p><p><strong>Konum:</strong> {{{{ job.location }}}}</p>
                    {{% if job.contact_email %}}<p><strong>İlan İletişim E-posta:</strong> {{{{ job.contact_email }}}}</p>{{% else %}}<p><strong>İlan İletişim E-posta:</strong> Profil e-postanız ({{{{ session.user_email }}}}) kullanılacaktır.</p>{{% endif %}}
                    <div class="actions-footer">
                        <a href="{{{{ url_for('edit_job', job_id=job.id) }}}}" class="button button-edit" style="margin-right: 10px;">İlanı Güncelle</a>
                        <form method="POST" action="{{{{ url_for('delete_job', job_id=job.id) }}}}" style="display: inline;" onsubmit="return confirm('Bu ilanı kaldırmak istediğinizden emin misiniz?');">
                            <button type="submit" class="button button-danger">İlanı Kaldır</button>
                        </form>
                    </div>
                </div></div> {{% endfor %}} {{% endif %}}</div>
    {{% set current_year = datetime.datetime.now().year %}}
    {FOOTER_TEMPLATE} <script>function toggleDetails(id){{var el=document.getElementById(id); var btn=document.getElementById(id.replace('details-','toggle-btn-')); if(el.style.display==="none"||el.style.display===""){{el.style.display="block";if(btn)btn.textContent="Detayları Gizle";}}else{{el.style.display="none";if(btn)btn.textContent="Detayları Gör";}}}}</script></body></html>"""

FAVORITES_PAGE_TEMPLATE = f"""
<!DOCTYPE html><html lang="tr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Favori İlanlarım - CampusJobs</title>{COMMON_STYLES}</head><body> {NAVBAR_TEMPLATE}
    <div class="container"> {{% with messages = get_flashed_messages(with_categories=true) %}} {{% if messages %}} <ul class="flash-messages"> {{% for category, message in messages %}} <li class="{{{{ category }}}}">{{{{ message }}}}</li> {{% endfor %}} </ul> {{% endif %}} {{% endwith %}}
        <h1>Favori İlanlarım</h1>
        {{% if not jobs_data %}}<p class='no-jobs'>Henüz favorilere eklenmiş ilan bulunmamaktadır. <a href="{{{{ url_for('get_jobs') }}}}">Hemen ilanlara göz atın!</a></p>{{% else %}}
            {{% for job in jobs_data %}}
            <div class='job-listing'><div class="job-summary" onclick="toggleDetails('fav-details-{{{{ loop.index }}}}')"><div class="job-summary-info"><h3>{{{{ job.title }}}}</h3><p class="salary-info">Günlük: {{{{ job.daily_salary }}}} TL / Saatlik: {{{{ "%.2f"|format(job.hourly_salary) }}}} TL</p><p class="employer-info">İşveren: {{{{ job.employer_first_name }}}} {{{{ job.employer_last_name }}}} {{{{ '('+job.company_name+')' if job.company_name else '' }}}}</p></div><div class="job-actions"><form method="POST" action="{{{{ url_for('toggle_favorite', job_id=job.id) }}}}" style="display: inline;"><input type="hidden" name="redirect_to_favorites" value="true"><button type="submit" class="favorite-btn favorited" title="Favorilerden Çıkar">★</button></form><a href="javascript:void(0);" class="job-details-toggle" id="fav-toggle-btn-{{{{ loop.index }}}}">Detayları Gör</a></div></div>
                <div class="job-details" id="fav-details-{{{{ loop.index }}}}">
                    <p><strong>Açıklama:</strong> {{{{ job.description }}}}</p><p><strong>Çalışma Günleri:</strong> {{{{ job.working_days }}}}</p><p><strong>Çalışma Saatleri:</strong> {{{{ job.working_hours }}}}</p><p><strong>Günlük Toplam Saat:</strong> {{{{ job.total_hours }}}}</p><p><strong>İş Süresi:</strong> {{{{ job.job_duration }}}}</p><p><strong>İş Tipi:</strong> {{{{ job.job_type }}}}</p><p><strong>Konum:</strong> {{{{ job.location }}}}</p>
                    {{% set display_email = job.contact_email or job.employer_main_email %}}
                    {{% if display_email %}}<p><strong>İletişim E-posta:</strong> <a href='mailto:{{{{ display_email }}}}'>{{{{ display_email }}}}</a></p>{{% endif %}}
                    {{% if display_email %}}
                        {{% set email_subject = "İş Başvurusu: " + job.title + " (CampusJobs)" %}}
                        {{% set email_body = "Merhaba " + (job.employer_first_name or 'Yetkili') + ",\\n\\nCampusJobs üzerinden yayınlanan '" + job.title + "' başlıklı iş ilanınıza başvurmak istiyorum.\\n\\nSaygılarımla," %}}
                        <a href="mailto:{{{{ display_email }}}}?subject={{{{ urllib.parse.quote_plus(email_subject) }}}}&body={{{{ urllib.parse.quote_plus(email_body) }}}}" class="button apply-button">E-posta ile Başvur</a>
                    {{% else %}}<a href="{{{{ url_for('apply_no_email_message') }}}}" class="button apply-button">Başvur</a>{{% endif %}}
                </div></div> {{% endfor %}} {{% endif %}}</div>
    {{% set current_year = datetime.datetime.now().year %}}
    {FOOTER_TEMPLATE} <script>function toggleDetails(id){{var el=document.getElementById(id); var btnId=id.startsWith('fav-')?'fav-toggle-btn-'+id.split('-')[2]:'toggle-btn-'+id.split('-')[1]; var btn=document.getElementById(btnId); if(el.style.display==="none"||el.style.display===""){{el.style.display="block";if(btn)btn.textContent="Detayları Gizle";}}else{{el.style.display="none";if(btn)btn.textContent="Detayları Gör";}}}}</script></body></html>"""


@app.context_processor
def inject_global_vars():
    """Şablonlara genel değişkenleri enjekte eder."""
    return {
        'request': request, 
        'session': session, 
        'url_for': url_for, 
        'datetime': datetime, 
        'urllib': urllib,     
        'get_flashed_messages': get_flashed_messages 
    }

if __name__ == '__main__':
    app.run(debug=True)
