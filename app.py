# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from main import Session, User, Jobs, Department, Category, association_table # Импортируем модели и сессию из main.py

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here' # Замените на реальный секретный ключ

# --- Настройка Flask-Login ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # URL для перенаправления при необходимости входа

@login_manager.user_loader
def load_user(user_id):
    session = Session()
    user = session.query(User).get(int(user_id))
    session.close()
    return user

# --- Главная страница (список работ) ---
@app.route('/')
def index():
    session = Session()
    jobs = session.query(Jobs).all()
    users = {u.id: u.full_name for u in session.query(User).all()} # Словарь для удобства
    categories = {c.id: c.name for c in session.query(Category).all()}
    session.close()
    return render_template('index.html', jobs=jobs, users=users, categories=categories)

# --- Страница авторизации ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        session = Session()
        user = session.query(User).filter(User.email == email).first()
        session.close()

        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Invalid email or password')
    return render_template('login.html')

# --- Страница регистрации ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        session = Session()
        # Получаем данные из формы
        surname = request.form['surname']
        name = request.form['name']
        age = int(request.form['age'])
        position = request.form['position']
        speciality = request.form['speciality']
        address = request.form['address']
        email = request.form['email']
        password = request.form['password']
        password_confirm = request.form['password_confirm']

        # Простая проверка подтверждения пароля
        if password != password_confirm:
            flash('Passwords do not match!')
            session.close()
            return redirect(url_for('register'))

        # Проверяем, существует ли уже пользователь с таким email
        existing_user = session.query(User).filter(User.email == email).first()
        if existing_user:
            flash('Email already registered.')
            session.close()
            return redirect(url_for('register'))

        # Создаем нового пользователя
        new_user = User(
            surname=surname,
            name=name,
            age=age,
            position=position,
            speciality=speciality,
            address=address,
            email=email,
        )
        new_user.set_password(password) # Хэшируем пароль перед сохранением
        session.add(new_user)
        session.commit()
        session.close()
        flash('Registration successful. Please log in.')
        return redirect(url_for('login')) # Перенаправляем на страницу входа после регистрации

    return render_template('register.html')

# --- Выход из системы ---
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# --- Форма добавления работы ---
@app.route('/add_job', methods=['GET', 'POST'])
@login_required
def add_job():
    if request.method == 'POST':
        session = Session()
        team_leader_id = int(request.form['team_leader_id'])
        job_description = request.form['job_description']
        work_size = int(request.form['work_size'])
        collaborators_str = request.form['collaborators'] # Ожидается строка вида "1, 2, 3"
        is_finished = request.form.get('is_finished') == 'on' # on если чекбокс отмечен
        category_ids = request.form.getlist('categories') # Получаем список ID категорий

        new_job = Jobs(
            team_leader=team_leader_id,
            job=job_description,
            work_size=work_size,
            collaborators=collaborators_str,
            is_finished=is_finished
        )

        # Привязываем выбранные категории
        for cat_id in category_ids:
            category = session.query(Category).get(int(cat_id))
            if category:
                new_job.categories.append(category)

        session.add(new_job)
        session.commit()
        session.close()
        return redirect(url_for('index'))

    session = Session()
    users = session.query(User).all()
    categories = session.query(Category).all()
    session.close()
    return render_template('add_job.html', users=users, categories=categories)

# --- Форма редактирования работы ---
@app.route('/edit_job/<int:job_id>', methods=['GET', 'POST'])
@login_required
def edit_job(job_id):
    session = Session()
    job = session.query(Jobs).get_or_404(job_id) # Flask-SQLAlchemy метод, но можно заменить на .filter().first_or_404()
    if job.team_leader_user != current_user and current_user.id != 1: # Проверка прав
        flash('You cannot edit this job.')
        session.close()
        return redirect(url_for('index'))

    if request.method == 'POST':
        job.job = request.form['job_description']
        job.work_size = int(request.form['work_size'])
        job.collaborators = request.form['collaborators']
        job.is_finished = request.form.get('is_finished') == 'on'
        # Обновляем категории
        job.categories.clear() # Удаляем старые связи
        category_ids = request.form.getlist('categories')
        for cat_id in category_ids:
            category = session.query(Category).get(int(cat_id))
            if category:
                job.categories.append(category)

        session.commit()
        session.close()
        return redirect(url_for('index'))

    users = session.query(User).all()
    categories = session.query(Category).all()
    session.close()
    return render_template('edit_job.html', job=job, users=users, categories=categories)

# --- Удаление работы ---
@app.route('/delete_job/<int:job_id>')
@login_required
def delete_job(job_id):
    session = Session()
    job = session.query(Jobs).get_or_404(job_id)
    if job.team_leader_user != current_user and current_user.id != 1: # Проверка прав
        flash('You cannot delete this job.')
        session.close()
        return redirect(url_for('index'))

    session.delete(job)
    session.commit()
    session.close()
    return redirect(url_for('index'))

# --- Страница просмотра департаментов ---
@app.route('/departments')
def departments():
    session = Session()
    depts = session.query(Department).all()
    users = {u.id: u.full_name for u in session.query(User).all()} # Словарь для удобства
    session.close()
    return render_template('departments.html', depts=depts, users=users)

# --- Форма добавления департамента ---
@app.route('/add_department', methods=['GET', 'POST'])
@login_required
def add_department():
    if request.method == 'POST':
        session = Session()
        title = request.form['title']
        chief_id = int(request.form['chief_id'])
        members_str = request.form['members'] # Ожидается строка вида "1, 2, 3"
        email = request.form['email']

        new_dept = Department(
            title=title,
            chief=chief_id,
            members=members_str,
            email=email
        )
        session.add(new_dept)
        session.commit()
        session.close()
        return redirect(url_for('departments'))

    session = Session()
    users = session.query(User).all()
    session.close()
    return render_template('add_department.html', users=users)

# --- Форма редактирования департамента ---
@app.route('/edit_department/<int:dept_id>', methods=['GET', 'POST'])
@login_required
def edit_department(dept_id):
    session = Session()
    dept = session.query(Department).get_or_404(dept_id)

    if request.method == 'POST':
        dept.title = request.form['title']
        dept.chief = int(request.form['chief_id'])
        dept.members = request.form['members']
        dept.email = request.form['email']

        session.commit()
        session.close()
        return redirect(url_for('departments'))

    users = session.query(User).all()
    session.close()
    return render_template('edit_department.html', dept=dept, users=users)

# --- Удаление департамента ---
@app.route('/delete_department/<int:dept_id>')
@login_required
def delete_department(dept_id):
    session = Session()
    dept = session.query(Department).get_or_404(dept_id)

    session.delete(dept)
    session.commit()
    session.close()
    return redirect(url_for('departments'))

if __name__ == '__main__':
    app.run(debug=True)
