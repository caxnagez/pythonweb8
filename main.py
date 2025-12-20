import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

engine = create_engine('sqlite:///mars_explorer.db', echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)

association_table = Table('job_categories', Base.metadata,
    Column('job_id', Integer, ForeignKey('jobs.id'), primary_key=True),
    Column('category_id', Integer, ForeignKey('categories.id'), primary_key=True)
)

class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)

    def __repr__(self):
        return f'<Category> {self.name}'

class User(Base, UserMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=False)
    surname = Column(String, nullable=False)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    position = Column(String, nullable=False)
    speciality = Column(String, nullable=False)
    address = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    city_from = Column(String, nullable=True)
    _hashed_password = Column('hashed_password', String, nullable=False)
    modified_date = Column(DateTime, default=datetime.datetime.now)
    jobs_as_leader = relationship("Jobs", back_populates="team_leader_user")
    departments_led = relationship("Department", back_populates="chief_user")

    def set_password(self, password):
        self._hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self._hashed_password, password)

    @property
    def full_name(self):
        return f"{self.surname} {self.name}"

    def __repr__(self):
        return f'<Colonist>{self.id} {self.surname} {self.name}'

class Jobs(Base):
    __tablename__ = 'jobs'
    id = Column(Integer, primary_key=True, autoincrement=False)
    team_leader = Column(Integer, ForeignKey('users.id'), nullable=False)
    job = Column(String, nullable=False)
    work_size = Column(Integer, nullable=False)
    collaborators = Column(Text, nullable=False)
    start_date = Column(DateTime, default=datetime.datetime.now)
    end_date = Column(DateTime)
    is_finished = Column(Boolean, default=False)
    team_leader_user = relationship("User", back_populates="jobs_as_leader")
    categories = relationship("Category", secondary=association_table, lazy='subquery', backref="jobs")

    def __repr__(self):
        return f'<Job> {self.job}'


class Department(Base):
    __tablename__ = 'departments'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    chief = Column(Integer, ForeignKey('users.id'), nullable=False)
    members = Column(Text, nullable=False) 
    email = Column(String, unique=True, nullable=False)
    chief_user = relationship("User", back_populates="departments_led")

Base.metadata.create_all(engine)
session = Session()

if session.query(User).count() == 0:
    captain = User(
        id=1, 
        surname='Scott',
        name='Ridley',
        age=21,
        position='captain',
        speciality='research engineer',
        address='module_1',
        email='scott_chief@mars.org',
        city_from='London'
    )
    captain.set_password('hash123') 
    session.add(captain)

    colonist1 = User(
        id=2,
        surname='Theslave',
        name='Gael',
        age=25,
        position='middle engineer',
        speciality='biotech engineer',
        address='module_2',
        email='111@mars.com',
        city_from='New York'
    )
    colonist1.set_password('hash123')

    colonist2 = User(
        id=3, 
        surname='Eater',
        name='Oldrik',
        age=30,
        position='geologist',
        speciality='geologist',
        address='module_1',
        email='222@mars.com',
        city_from='Moscow'
    )
    colonist2.set_password('hash123')

    colonist3 = User(
        id=4, 
        surname='Gigant',
        name='Yourm',
        age=17,
        position='assistant',
        speciality='technician',
        address='module_1',
        email='333@mars.com',
        city_from='Paris'
    )
    colonist3.set_password('hash123')

    colonist4 = User(
        id=5, 
        surname='Fireceper',
        name='Cute',
        age=35,
        position='chief scientist',
        speciality='astrobiologist',
        address='module_3',
        email='444@mars.com',
        city_from='Tokyo'
    )
    colonist4.set_password('hash123')

    colonist5 = User(
        id=6, 
        surname='Blackfire',
        name='Fride',
        age=28,
        position='pilot',
        speciality='aviation engineer',
        address='module_1',
        email='555@mars.com',
        city_from='Sydney'
    )
    colonist5.set_password('hash123')

    session.add_all([colonist1, colonist2, colonist3, colonist4, colonist5])
    session.commit()

    if session.query(Jobs).count() == 0:
        first_job = Jobs(
            id=1, 
            team_leader=captain.id, 
            job='deployment of residential modules 1 and 2',
            work_size=15,
            collaborators='2, 3',
            start_date=datetime.datetime.now(),
            is_finished=False
        )
        session.add(first_job)
        session.commit()

    if session.query(Department).count() == 0:
        geology_dept = Department(
            title='Geological Survey',
            chief=colonist2.id,
            members='2, 3, 5',
            email='geology@mars.org'
        )
        session.add(geology_dept)
        session.commit()

    if session.query(Category).count() == 0:
        category_construction = Category(name='Construction')
        category_research = Category(name='Research')
        category_maintenance = Category(name='Maintenance')
        session.add_all([category_construction, category_research, category_maintenance])
        session.commit()

    construction_category = session.query(Category).filter(Category.name == 'Construction').first()
    if construction_category:
        first_job.categories.append(construction_category)
        session.commit()
session.close()


def task_4(db_name):
    session = Session()
    colonists = session.query(User).filter(User.address.like('module_1')).all()
    for c in colonists:
        print(c)
    session.close()

def task_5(db_name):
    session = Session()
    colonists = session.query(User.id).filter(
        User.address.like('module_1'),
        ~User.speciality.contains('engineer'),
        ~User.position.contains('engineer')
    ).all()
    for c_id, in colonists:
        print(c_id)
    session.close()

def task_6(db_name):
    session = Session()
    minors = session.query(User).filter(User.age < 18).all()
    for m in minors:
        print(f"{m} {m.age}")
    session.close()

def task_7(db_name):
    session = Session()
    leaders = session.query(User).filter(
        User.position.contains('chief') | User.position.contains('middle')
    ).all()
    for l in leaders:
        print(l)
    session.close()

def task_8(db_name):
    session = Session()
    jobs = session.query(Jobs).filter(
        Jobs.work_size < 20,
        Jobs.is_finished == False
    ).all()
    for j in jobs:
        print(j)
    session.close()

def task_9(db_name):
    session = Session()
    all_jobs = session.query(Jobs).all()
    max_team_size = 0
    team_leaders = []

    for job in all_jobs:
        try:
            collaborators_list = [int(x.strip()) for x in job.collaborators.split(',') if x.strip()]
            team_size = len(collaborators_list)
        except ValueError:
            team_size = 0

        if team_size > max_team_size:
            max_team_size = team_size
            leader = session.query(User).filter(User.id == job.team_leader).first()
            if leader:
                team_leaders = [(leader.surname, leader.name)]
        elif team_size == max_team_size and max_team_size > 0:
            leader = session.query(User).filter(User.id == job.team_leader).first()
            if leader:
                team_leaders.append((leader.surname, leader.name))

    for surname, name in team_leaders:
        print(f"{surname} {name}")
    session.close()

def task_10(db_name):
    session = Session()
    session.query(User).filter(
        User.address.like('module_1'),
        User.age < 21
    ).update({User.address: 'module_3'}, synchronize_session=False)
    session.commit()
    session.close()

def task_12(db_name):
    session = Session()
    dept = session.query(Department).filter(Department.id == 1).first()
    if not dept:
        print("Department with id=1 not found.")
        session.close()
        return

    try:
        dept_members_ids = {int(x.strip()) for x in dept.members.split(',') if x.strip()}
    except ValueError:
        print("Error parsing department members list.")
        session.close()
        return
    for member_id in dept_members_ids:
        user = session.query(User).filter(User.id == member_id).first()
        if not user:
            continue

        total_hours = 0
        all_jobs = session.query(Jobs).all()
        for job in all_jobs:
            try:
                job_collaborators = {int(x.strip()) for x in job.collaborators.split(',') if x.strip()}
                if member_id in job_collaborators:
                    total_hours += job.work_size
            except ValueError:
                continue

        if total_hours > 25:
            print(f"{user.surname} {user.name}")

    session.close()

if __name__ == "__main__":
    db_name = "mars_explorer.db"
    print("\n----------------------")
    task_4(db_name)
    print("\n----------------------")
    task_5(db_name)
    print("\n----------------------")
    task_6(db_name)
    print("\n----------------------")
    task_7(db_name)
    print("\n----------------------")
    task_8(db_name)
    print("\n----------------------")
    task_9(db_name)
    print("\n----------------------")
    session = Session()
    pre_update_users = session.query(User).filter(User.address.like('module_1')).all()
    for u in pre_update_users:
        print(f"ID: {u.id}, Name: {u.name}, Surname: {u.surname}, Age: {u.age}, Address: {u.address}")
    session.close()
    task_10(db_name)
    print("\n----------------------")
    session = Session()
    post_update_users = session.query(User).filter(User.address.like('module_3')).all()
    for u in post_update_users:
        print(f"ID: {u.id}, Name: {u.name}, Surname: {u.surname}, Age: {u.age}, Address: {u.address}")
    session.close()
    print("\n----------------------")
    task_12(db_name)
