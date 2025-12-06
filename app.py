from flask import Flask, render_template, request, redirect, url_for
from main import Session, User, Jobs, Department

app = Flask(__name__)

@app.route('/')
def index():
    session = Session()
    jobs = session.query(Jobs).all()
    users = {u.id: f"{u.surname} {u.name}" for u in session.query(User).all()}
    session.close()
    return render_template('index.html', jobs=jobs, users=users)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        session = Session()
        surname = request.form['surname']
        name = request.form['name']
        age = int(request.form['age'])
        position = request.form['position']
        speciality = request.form['speciality']
        address = request.form['address']
        email = request.form['email']
        password = request.form['password']
        password_confirm = request.form['password_confirm']

        if password != password_confirm:
            return "Passwords do not match!", 400

        new_user = User(
            surname=surname,
            name=name,
            age=age,
            position=position,
            speciality=speciality,
            address=address,
            email=email,
            hashed_password=password
        )
        session.add(new_user)
        session.commit()
        session.close()
        return redirect(url_for('index'))

    return render_template('register.html')

@app.route('/add_job', methods=['GET', 'POST'])
def add_job():
    if request.method == 'POST':
        session = Session()
        team_leader_id = int(request.form['team_leader_id'])
        job_description = request.form['job_description']
        work_size = int(request.form['work_size'])
        collaborators_str = request.form['collaborators']
        is_finished = request.form.get('is_finished') == 'on'
        new_job = Jobs(
            team_leader=team_leader_id,
            job=job_description,
            work_size=work_size,
            collaborators=collaborators_str,
            is_finished=is_finished
        )
        session.add(new_job)
        session.commit()
        session.close()
        return redirect(url_for('index'))

    session = Session()
    users = session.query(User).all()
    session.close()
    return render_template('add_job.html', users=users)

@app.route('/add_department', methods=['GET', 'POST'])
def add_department():
    if request.method == 'POST':
        session = Session()
        title = request.form['title']
        chief_id = int(request.form['chief_id'])
        members_str = request.form['members']
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
        return redirect(url_for('index'))

    session = Session()
    users = session.query(User).all()
    session.close()
    return render_template('add_department.html', users=users)

if __name__ == '__main__':
    app.run(debug=True)
