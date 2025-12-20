from flask import Blueprint, jsonify, request
from main import Session, Jobs, Category, association_table
from sqlalchemy import and_

jobs_api = Blueprint('jobs_api', __name__)

def get_jobs_with_details(jobs_list):
    result = []
    for job in jobs_list:
        job_dict = {
            'id': job.id,
            'team_leader': job.team_leader,
            'job': job.job,
            'work_size': job.work_size,
            'collaborators': job.collaborators,
            'start_date': job.start_date.isoformat() if job.start_date else None,
            'end_date': job.end_date.isoformat() if job.end_date else None,
            'is_finished': job.is_finished,
            'categories': [cat.name for cat in job.categories]
        }
        result.append(job_dict)
    return result

@jobs_api.route('/api/jobs', methods=['GET'])
def get_jobs():
    session = Session()
    jobs = session.query(Jobs).all()
    session.close()
    return jsonify({'jobs': get_jobs_with_details(jobs)})

@jobs_api.route('/api/jobs/<int:job_id>', methods=['GET'])
def get_job(job_id):
    session = Session()
    job = session.query(Jobs).filter(Jobs.id == job_id).first()
    session.close()
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    return jsonify({'job': get_jobs_with_details([job])[0]})
@jobs_api.route('/api/jobs', methods=['POST'])
def add_job():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    job_id = data.get('id')
    if job_id is None:
        session.close()
        return jsonify({'error': 'Id is required'}), 400

    session = Session()
    existing_job = session.query(Jobs).filter(Jobs.id == job_id).first()
    if existing_job:
        session.close()
        return jsonify({'error': 'Id already exists'}), 400

    team_leader_id = data.get('team_leader')
    job_description = data.get('job')
    work_size = data.get('work_size')
    collaborators_str = data.get('collaborators')
    is_finished = data.get('is_finished', False)
    start_date_str = data.get('start_date')
    end_date_str = data.get('end_date')
    category_names = data.get('categories', [])

    if not all([team_leader_id, job_description, work_size, collaborators_str]):
        session.close()
        return jsonify({'error': 'Missing required fields'}), 400

    import datetime
    start_date = datetime.datetime.fromisoformat(start_date_str) if start_date_str else datetime.datetime.now()
    end_date = datetime.datetime.fromisoformat(end_date_str) if end_date_str else None

    new_job = Jobs(
        id=job_id,
        team_leader=team_leader_id,
        job=job_description,
        work_size=work_size,
        collaborators=collaborators_str,
        start_date=start_date,
        end_date=end_date,
        is_finished=is_finished
    )

    for name in category_names:
        category = session.query(Category).filter(Category.name == name).first()
        if not category:
            category = Category(name=name)
            session.add(category)
        new_job.categories.append(category)

    session.add(new_job)
    session.commit()
    session.close()
    return jsonify({'success': 'Job added successfully'}), 201

@jobs_api.route('/api/jobs/<int:job_id>', methods=['DELETE'])
def delete_job_api(job_id):
    session = Session()
    job = session.query(Jobs).filter(Jobs.id == job_id).first()
    if not job:
        session.close()
        return jsonify({'error': 'Job not found'}), 404

    session.delete(job)
    session.commit()
    session.close()
    return jsonify({'success': 'Job deleted successfully'})

@jobs_api.route('/api/jobs/<int:job_id>', methods=['PUT'])
def edit_job_api(job_id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    session = Session()
    job = session.query(Jobs).filter(Jobs.id == job_id).first()
    if not job:
        session.close()
        return jsonify({'error': 'Job not found'}), 404

    if 'team_leader' in data:
        job.team_leader = data['team_leader']
    if 'job' in data:
        job.job = data['job']
    if 'work_size' in data:
        job.work_size = data['work_size']
    if 'collaborators' in data:
        job.collaborators = data['collaborators']
    if 'start_date' in data:
        job.start_date = datetime.datetime.fromisoformat(data['start_date'])
    if 'end_date' in data:
        job.end_date = datetime.datetime.fromisoformat(data['end_date']) if data['end_date'] else None
    if 'is_finished' in data:
        job.is_finished = data['is_finished']

    if 'categories' in data:
        job.categories.clear()
        for name in data['categories']:
            category = session.query(Category).filter(Category.name == name).first()
            if not category:
                category = Category(name=name)
                session.add(category)
            job.categories.append(category)

    session.commit()
    session.close()
    return jsonify({'success': 'Job updated successfully'})
