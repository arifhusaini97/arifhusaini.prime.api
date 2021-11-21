from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

import json

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('app_user:create')
TOKEN_URL = reverse('app_user:token')
ME_URL = reverse('app_user:me')
ME_LOGOUT_URL = reverse('app_user:me-logout')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTest(TestCase):
    """Test the users API (public)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating user with valid payload is successful"""
        payload = {
            "password_confirmation": "test123",
            "password": "test123",
            "is_superuser": False,
            "email": "test@example.com",
            "name": "Test Name",
            "is_staff": False,
            # not json serializable
            # "birthday": datetime.date(1997, 6, 23),
            "birthday": "1997-06-23",
            "is_male": True,
            "working_id": None,
            "city": None
        }

        res = self.client.post(CREATE_USER_URL, data=json.dumps(payload),
                               content_type='application/json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)

        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """Test creating user that already exists"""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass',
            'name': 'Test name'
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that the password must be more than 5 characters"""

        payload = {
            'email': 'test@example.com',
            'password': 'pw',
            'name': 'Test name'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test that a token is created for the user"""
        payload = {'email': 'test@example.com', 'password': 'testpass'}
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test that token is not created if invalid credentials are given"""
        create_user(email='test@example.com', password='testpass')
        payload = {'email': 'test@example.com', 'password': 'wrong'}
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test that token is not created if user does not exist"""
        payload = {'email': 'test@example.com', 'password': 'testpass'}
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Test that email and password are required"""
        res = self.client.post(TOKEN_URL, {'email': 'one', 'password': '', })
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test that authentication is required for users"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication"""

    def setUp(self):
        self.user = create_user(
            is_superuser=False,
            email='test@example.com',
            name="Test Name",
            is_staff=False,
            password='test123',
            birthday="1997-06-23",
            is_male=True,
            working_id=None,
            city=None,
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in used"""

        res = self.client.get(ME_URL)

        del res.data['created']
        del res.data['modified']

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            res.data, {
                'id': res.data['id'],
                'is_superuser': False,
                'email': 'test@example.com',
                'name': "Test Name",
                'is_staff': False,
                'birthday': "1997-06-23",
                'is_male': True,
                'working_id': None,
                'city': None, })

    def test_post_me_not_allowed(self):
        """Test that POST is not allowed in me url"""

        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile for authenticated user"""
        payload = {'name': 'New Name', 'password': 'newpassword123',
                   'password_confirmation': 'newpassword123', }

        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()

        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_logout_user(self):
        """Test logout user by token"""
        payload = {'email': 'test@example.com', 'password': 'test123'}
        self.client.auth_token = self.client.post(
            TOKEN_URL, payload).data.get('token')
        res = self.client.post(ME_LOGOUT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
