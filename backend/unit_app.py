import unittest
from unittest.mock import patch, MagicMock
import json
import datetime

from app import app


class TestApp(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_register_user(self):
        with patch('app.db.users_collection.find_one') as mock_find_one:
            mock_find_one.return_value = None  # User does not exist
            new_user = {
                'username': 'test_user',
                'password': 'password123',
                'admin': 'False'
            }
            response = self.app.post('/api/v1/users', json=new_user)
            data = json.loads(response.get_data(as_text=True))
            self.assertEqual(response.status_code, 201)
            self.assertEqual(data['msg'], 'User created successfully')

    def test_login_user(self):
        with patch('app.db.users_collection.find_one') as mock_find_one:
            mock_find_one.return_value = {
                'username': 'test_user',
                'password': 'e08ac5db469405b278ecd1b50a68e7f41e1b70a06a1a82ec2bb437ffdf1949c5',  # Hashed 'password123'
                'admin': 'False'
            }
            login_details = {
                'username': 'test_user',
                'password': 'password123'
            }
            response = self.app.post('/api/v1/login', json=login_details)
            data = json.loads(response.get_data(as_text=True))
            self.assertEqual(response.status_code, 200)
            self.assertIn('access_token', data)

    def test_get_profile(self):
        with patch('app.get_jwt_identity') as mock_get_jwt_identity:
            mock_get_jwt_identity.return_value = 'test_user'
            with patch('app.db.users_collection.find_one') as mock_find_one:
                mock_find_one.return_value = {
                    'username': 'test_user',
                    'admin': 'True'
                }
                response = self.app.get('/api/v1/user')
                data = json.loads(response.get_data(as_text=True))
                self.assertEqual(response.status_code, 200)
                self.assertIn('profile', data)

    def test_send_feedback(self):
        with patch('app.get_jwt_identity') as mock_get_jwt_identity:
            mock_get_jwt_identity.return_value = 'test_user'
            with patch('app.db.users_collection.find_one') as mock_find_one:
                mock_find_one.return_value = {'username': 'test_user'}
                feedback = {'text': 'This is a test feedback'}
                response = self.app.post('/api/v1/sendFeedback', json=feedback)
                data = json.loads(response.get_data(as_text=True))
                self.assertEqual(response.status_code, 200)
                self.assertEqual(data['msg'], 'Inserted successfully')

    def test_get_all_feedback(self):
        with patch('app.get_jwt_identity') as mock_get_jwt_identity:
            mock_get_jwt_identity.return_value = 'admin_user'
            with patch('app.db.users_collection.find_one') as mock_find_one:
                mock_find_one.return_value = {'username': 'admin_user', 'admin': 'True'}
                with patch('app.db.feedback_collection.find') as mock_feedback_find:
                    mock_feedback_find.return_value = [
                        {'_id': '1', 'username': 'user1', 'timestamp': '2022-03-10', 'text': 'Feedback 1'},
                        {'_id': '2', 'username': 'user2', 'timestamp': '2022-03-11', 'text': 'Feedback 2'}
                    ]
                    response = self.app.get('/api/v1/getAllFeedback')
                    data = json.loads(response.get_data(as_text=True))
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(len(data), 2)

    def test_log_convo(self):
        with patch('app.get_jwt_identity') as mock_get_jwt_identity:
            mock_get_jwt_identity.return_value = 'test_user'
            with patch('app.db.users_collection.find_one') as mock_find_one:
                mock_find_one.return_value = {'username': 'test_user'}
                with patch('app.client.chat.completions.create') as mock_completion_create:
                    mock_completion_create.return_value = MagicMock(choices=[MagicMock(message=MagicMock(content='Response from GPT'))])
                    convo_details = {
                        'messages': [{'role': 'User', 'content': 'Hello'}, {'role': 'AI', 'content': 'Hi!'}]
                    }
                    response = self.app.post('/api/v1/logConvo', json=convo_details)
                    data = json.loads(response.get_data(as_text=True))
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(data['response'], 'Response from GPT')

    def test_get_all_convo(self):
        with patch('app.get_jwt_identity') as mock_get_jwt_identity:
            mock_get_jwt_identity.return_value = 'admin_user'
            with patch('app.db.users_collection.find_one') as mock_find_one:
                mock_find_one.return_value = {'username': 'admin_user', 'admin': 'True'}
                with patch('app.db.users_collection.find') as mock_users_find:
                    mock_users_find.return_value = [
                        {'_id': '1', 'username': 'user1'},
                        {'_id': '2', 'username': 'user2'}
                    ]
                    with patch('app.db.users_collection.find_one') as mock_find_one:
                        mock_find_one.return_value = {'username': 'user1'}
                        with patch('app.db.users_collection.find') as mock_convo_find:
                            mock_convo_find.return_value = [
                                {'_id': '1', 'username': 'user1', 'timestamp': '2022-03-10', 'query': 'Question 1', 'response': 'Response 1'},
                                {'_id': '2', 'username': 'user1', 'timestamp': '2022-03-11', 'query': 'Question 2', 'response': 'Response 2'}
                            ]
                            response = self.app.get('/api/v1/getAllConvo')
                            data = json.loads(response.get_data(as_text=True))
                            self.assertEqual(response.status_code, 200)
                            self.assertEqual(len(data), 2)

    def test_get_all_names(self):
        with patch('app.get_jwt_identity') as mock_get_jwt_identity:
            mock_get_jwt_identity.return_value = 'admin_user'
            with patch('app.db.users_collection.find_one') as mock_find_one:
                mock_find_one.return_value = {'username': 'admin_user', 'admin': 'True'}
                with patch('app.db.users_collection.find') as mock_users_find:
                    mock_users_find.return_value = [
                        {'_id': '1', 'username': 'user1', 'timestamp': '2022-03-10'},
                        {'_id': '2', 'username': 'user2', 'timestamp': '2022-03-11'}
                    ]
                    response = self.app.get('/api/v1/getAllNames')
                    data = json.loads(response.get_data(as_text=True))
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(len(data), 2)

    def test_send_to_jira(self):
        with patch('app.get_jwt_identity') as mock_get_jwt_identity:
            mock_get_jwt_identity.return_value = 'test_user'
            with patch('app.db.users_collection.find_one') as mock_find_one:
                mock_find_one.return_value = {'username': 'test_user'}
                with patch('app.db.users_collection.find') as mock_users_find:
                    mock_users_find.return_value = [
                        {'_id': '1', 'username': 'test_user'}
                    ]
                    with patch('app.app.run') as mock_run:
                        issue = {
                            'description': 'This is a test issue'
                        }
                        response = self.app.post('/api/v1/sendToJira', json=issue)
                        data = json.loads(response.get_data(as_text=True))
                        self.assertEqual(response.status_code, 200)
                        self.assertEqual(data['msg'], 'JIRA ticket created')

    # Add more test cases for other endpoints...

if __name__ == '__main__':
    unittest.main()