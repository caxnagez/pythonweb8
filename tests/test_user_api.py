# tests/test_user_api.py
import unittest
import requests
import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import engine, Base, Session
from main import User, Jobs, Category, association_table

BASE_URL = 'http://127.0.0.1:5000'

class TestUserAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def test_get_all_users(self):
        response = requests.get(f'{BASE_URL}/api/users')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('users', data)

    def test_get_single_user_valid(self):
        response = requests.get(f'{BASE_URL}/api/users/1')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('user', data)

    def test_get_single_user_invalid_id(self):
        response = requests.get(f'{BASE_URL}/api/users/999999')
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertEqual(data.get('error'), 'User not found')

    def test_get_single_user_invalid_string(self):
        response = requests.get(f'{BASE_URL}/api/users/abc')
        self.assertIn(response.status_code, [400, 404])

    def test_add_user_valid(self):
        new_user_data = {
            "surname": "Test",
            "name": "User",
            "age": 30,
            "position": "tester",
            "speciality": "testing",
            "address": "module_test",
            "email": "testuser999@example.com",
            "city_from": "Test City",
            "password": "testpassword123"
        }
        response = requests.post(f'{BASE_URL}/api/users', json=new_user_data)
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data.get('success'), 'User added successfully')

    def test_add_user_duplicate_id(self):
        get_response = requests.get(f'{BASE_URL}/api/users/1')
        if get_response.status_code == 200:
            existing_user_data = get_response.json().get('user')
            if existing_user_data:
                user_id_to_duplicate = existing_user_data['id']
                duplicate_data = {
                    "id": user_id_to_duplicate,
                    "surname": "Duplicate",
                    "name": "User",
                    "age": 26,
                    "position": "dup",
                    "speciality": "duping",
                    "address": "module_dup",
                    "email": f"dupuser{user_id_to_duplicate}@example.com",
                    "city_from": "Dup City",
                    "password": "duppassword123"
                }
                response = requests.post(f'{BASE_URL}/api/users', json=duplicate_data)
                self.assertEqual(response.status_code, 400)
                data = response.json()
                self.assertEqual(data.get('error'), 'Id already exists')
            else:
                user_data = {
                    "id": 998,
                    "surname": "Temp",
                    "name": "User",
                    "age": 25,
                    "position": "temp",
                    "speciality": "temping",
                    "address": "module_temp",
                    "email": "tempuser998@example.com",
                    "city_from": "Temp City",
                    "password": "temppassword123"
                }
                requests.post(f'{BASE_URL}/api/users', json=user_data)

                duplicate_data = {
                    "id": 998,
                    "surname": "Duplicate",
                    "name": "User",
                    "age": 26,
                    "position": "dup",
                    "speciality": "duping",
                    "address": "module_dup",
                    "email": "dupuser998_2@example.com",
                    "city_from": "Dup City",
                    "password": "duppassword123"
                }
                response = requests.post(f'{BASE_URL}/api/users', json=duplicate_data)
                self.assertEqual(response.status_code, 400)
                data = response.json()
                self.assertEqual(data.get('error'), 'Id already exists')
        else:
            user_data = {
                "id": 998,
                "surname": "Temp",
                "name": "User",
                "age": 25,
                "position": "temp",
                "speciality": "temping",
                "address": "module_temp",
                "email": "tempuser998@example.com",
                "city_from": "Temp City",
                "password": "temppassword123"
            }
            requests.post(f'{BASE_URL}/api/users', json=user_data)

            duplicate_data = {
                "id": 998,
                "surname": "Duplicate",
                "name": "User",
                "age": 26,
                "position": "dup",
                "speciality": "duping",
                "address": "module_dup",
                "email": "dupuser998_2@example.com",
                "city_from": "Dup City",
                "password": "duppassword123"
            }
            response = requests.post(f'{BASE_URL}/api/users', json=duplicate_data)
            self.assertEqual(response.status_code, 400)
            data = response.json()
            self.assertEqual(data.get('error'), 'Id already exists')

    def test_add_user_duplicate_email(self):
        user_data = {
            "surname": "Temp2",
            "name": "User2",
            "age": 25,
            "position": "temp2",
            "speciality": "temping2",
            "address": "module_temp2",
            "email": "tempuser997@example.com",
            "city_from": "Temp City2",
            "password": "temppassword123"
        }
        response = requests.post(f'{BASE_URL}/api/users', json=user_data)
        self.assertEqual(response.status_code, 201)

        duplicate_email_data = {
            "surname": "Another",
            "name": "User",
            "age": 26,
            "position": "another",
            "speciality": "anothering",
            "address": "module_another",
            "email": "tempuser997@example.com",
            "city_from": "Another City",
            "password": "anotherpassword123"
        }
        response = requests.post(f'{BASE_URL}/api/users', json=duplicate_email_data)
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)

    def test_add_user_missing_fields(self):
        incomplete_data = {
            "surname": "Incomplete",
        }
        response = requests.post(f'{BASE_URL}/api/users', json=incomplete_data)
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)

    def test_add_user_invalid_json(self):
        response = requests.post(f'{BASE_URL}/api/users', data='not json')
        self.assertEqual(response.status_code, 415)

    def test_delete_user_valid(self):
        new_user_data = {
            "surname": "ToBe",
            "name": "Deleted",
            "age": 1,
            "position": "tbd",
            "speciality": "tbding",
            "address": "module_tbd",
            "email": "tbduser@example.com",
            "city_from": "TBD City",
            "password": "tbdpassword123"
        }
        response = requests.post(f'{BASE_URL}/api/users', json=new_user_data)
        self.assertEqual(response.status_code, 201)
        created_user_id = response.json().get('id')
        if not created_user_id:
             get_all_response = requests.get(f'{BASE_URL}/api/users')
             all_users = get_all_response.json().get('users', [])
             created_user = next((u for u in all_users if u['email'] == new_user_data['email']), None)
             if created_user:
                 created_user_id = created_user['id']
             else:
                 self.fail("Could not find created user to delete")

        response = requests.delete(f'{BASE_URL}/api/users/{created_user_id}')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('success'), 'User deleted successfully')

        get_response = requests.get(f'{BASE_URL}/api/users/{created_user_id}')
        self.assertEqual(get_response.status_code, 404)

    def test_delete_user_invalid_id(self):
        response = requests.delete(f'{BASE_URL}/api/users/999999')
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertEqual(data.get('error'), 'User not found')

    def test_edit_user_valid(self):
        new_user_data = {
            "surname": "Original",
            "name": "User",
            "age": 20,
            "position": "orig",
            "speciality": "origing",
            "address": "module_orig",
            "email": "origuser@example.com",
            "city_from": "Orig City",
            "password": "origpassword123"
        }
        response = requests.post(f'{BASE_URL}/api/users', json=new_user_data)
        self.assertEqual(response.status_code, 201)
        created_user_id = response.json().get('id')
        if not created_user_id:
             get_all_response = requests.get(f'{BASE_URL}/api/users')
             all_users = get_all_response.json().get('users', [])
             created_user = next((u for u in all_users if u['email'] == new_user_data['email']), None)
             if created_user:
                 created_user_id = created_user['id']
             else:
                 self.fail("Could not find created user to edit")

        update_data = {
            "name": "Updated User via API",
            "age": 25,
            "city_from": "Updated City"
        }
        response = requests.put(f'{BASE_URL}/api/users/{created_user_id}', json=update_data)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('success'), 'User updated successfully')

        get_response = requests.get(f'{BASE_URL}/api/users/{created_user_id}')
        self.assertEqual(get_response.status_code, 200)
        updated_user = get_response.json().get('user')
        self.assertEqual(updated_user['name'], 'Updated User via API')
        self.assertEqual(updated_user['age'], 25)
        self.assertEqual(updated_user['city_from'], 'Updated City')

    def test_edit_user_invalid_id(self):
        update_data = {"name": "Should not update"}
        response = requests.put(f'{BASE_URL}/api/users/999999', json=update_data)
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertEqual(data.get('error'), 'User not found')

    def test_edit_user_invalid_json(self):
        response = requests.put(f'{BASE_URL}/api/users/1', data='not json')
        self.assertEqual(response.status_code, 415)

    def test_edit_user_duplicate_email(self):
        user1_data = {
            "surname": "User",
            "name": "One",
            "age": 30,
            "position": "pos1",
            "speciality": "spec1",
            "address": "module_1",
            "email": "userone@example.com",
            "city_from": "City One",
            "password": "password123"
        }
        user2_data = {
            "surname": "User",
            "name": "Two",
            "age": 31,
            "position": "pos2",
            "speciality": "spec2",
            "address": "module_2",
            "email": "usertwo@example.com", 
            "city_from": "City Two",
            "password": "password123"
        }
        response1 = requests.post(f'{BASE_URL}/api/users', json=user1_data)
        response2 = requests.post(f'{BASE_URL}/api/users', json=user2_data)
        self.assertEqual(response1.status_code, 201)
        self.assertEqual(response2.status_code, 201)
        user1_id = response1.json().get('id')
        user2_id = response2.json().get('id')
        if not user1_id or not user2_id:
             get_all_response = requests.get(f'{BASE_URL}/api/users')
             all_users = get_all_response.json().get('users', [])
             user1 = next((u for u in all_users if u['email'] == user1_data['email']), None)
             user2 = next((u for u in all_users if u['email'] == user2_data['email']), None)
             if user1 and user2:
                 user1_id = user1['id']
                 user2_id = user2['id']
             else:
                 self.fail("Could not find created users for duplicate email test")

        update_data = {
            "email": "userone@example.com" 
        }
        response = requests.put(f'{BASE_URL}/api/users/{user2_id}', json=update_data)
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)


if __name__ == '__main__':
    unittest.main()
