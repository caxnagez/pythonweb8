import unittest
import requests
import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import engine, Base, Session
from main import User, Jobs, Category, association_table

BASE_URL = 'http://127.0.0.1:5000'
class TestJobsAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def test_get_all_jobs(self):
        response = requests.get(f'{BASE_URL}/api/jobs')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('jobs', data)

    def test_get_single_job_valid(self):
        response = requests.get(f'{BASE_URL}/api/jobs/1')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('job', data)

    def test_get_single_job_invalid_id(self):
        response = requests.get(f'{BASE_URL}/api/jobs/999999')
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertEqual(data.get('error'), 'Job not found')

    def test_get_single_job_invalid_string(self):
        response = requests.get(f'{BASE_URL}/api/jobs/abc')
        self.assertIn(response.status_code, [400, 404])

    def test_add_job_valid(self):
        new_job_data = {
            "id": 999,
            "team_leader": 1,
            "job": "Test job via API",
            "work_size": 10,
            "collaborators": "2, 3",
            "is_finished": False,
            "categories": ["Research"]
        }
        response = requests.post(f'{BASE_URL}/api/jobs', json=new_job_data)
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data.get('success'), 'Job added successfully')

    def test_add_job_duplicate_id(self):
        job_data = {
            "id": 998,
            "team_leader": 1,
            "job": "Temp job",
            "work_size": 5,
            "collaborators": "2",
            "is_finished": False
        }
        requests.post(f'{BASE_URL}/api/jobs', json=job_data)

        duplicate_data = {
            "id": 998,
            "team_leader": 2,
            "job": "Duplicate job",
            "work_size": 7,
            "collaborators": "3",
            "is_finished": True
        }
        response = requests.post(f'{BASE_URL}/api/jobs', json=duplicate_data)
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data.get('error'), 'Id already exists')

    def test_add_job_missing_fields(self):
        incomplete_data = {
            "id": 997,
            "team_leader": 1
        }
        response = requests.post(f'{BASE_URL}/api/jobs', json=incomplete_data)
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)

    def test_add_job_invalid_json(self):
        response = requests.post(f'{BASE_URL}/api/jobs', data='not json')
        self.assertEqual(response.status_code, 415)

    def test_delete_job_valid(self):
        new_job_data = {
            "id": 996,
            "team_leader": 1,
            "job": "Job to delete via API",
            "work_size": 1,
            "collaborators": "1",
            "is_finished": True
        }
        requests.post(f'{BASE_URL}/api/jobs', json=new_job_data)

        response = requests.delete(f'{BASE_URL}/api/jobs/996')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('success'), 'Job deleted successfully')
        get_response = requests.get(f'{BASE_URL}/api/jobs/996')
        self.assertEqual(get_response.status_code, 404)

    def test_delete_job_invalid_id(self):
        response = requests.delete(f'{BASE_URL}/api/jobs/999999')
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertEqual(data.get('error'), 'Job not found')

    def test_edit_job_valid(self):
        new_job_data = {
            "id": 995,
            "team_leader": 1,
            "job": "Original job",
            "work_size": 2,
            "collaborators": "1",
            "is_finished": False
        }
        requests.post(f'{BASE_URL}/api/jobs', json=new_job_data)

        update_data = {
            "job": "Updated job via API",
            "work_size": 8,
            "is_finished": True,
            "categories": ["Maintenance"]
        }
        response = requests.put(f'{BASE_URL}/api/jobs/995', json=update_data)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('success'), 'Job updated successfully')
        get_response = requests.get(f'{BASE_URL}/api/jobs/995')
        self.assertEqual(get_response.status_code, 200)
        updated_job = get_response.json().get('job')
        self.assertEqual(updated_job['job'], 'Updated job via API')
        self.assertEqual(updated_job['work_size'], 8)
        self.assertEqual(updated_job['is_finished'], True)
        self.assertIn('Maintenance', updated_job['categories'])

    def test_edit_job_invalid_id(self):
        update_data = {"job": "Should not update"}
        response = requests.put(f'{BASE_URL}/api/jobs/999999', json=update_data)
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertEqual(data.get('error'), 'Job not found')

    def test_edit_job_invalid_json(self):
        response = requests.put(f'{BASE_URL}/api/jobs/1', data='not json')
        self.assertEqual(response.status_code, 415)


if __name__ == '__main__':
    unittest.main()
