from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email='test@example.com', password='test1234'):
    """Create a sample user"""
    return get_user_model().objects.create_user(email, password)


def sample_candidate(name='azzanamin97'):
    """Create a sample candidate"""
    return models.Candidate.objects.create(name=name)


class ModelTests(TestCase):
    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful"""
        email = 'testpublic@example.com'
        password = 'testpublic1234'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_create_user_with_email_normalized(self):
        """Test the email for a new user is normalized"""
        email = 'testpublic@EXAMPLE.com'
        user = get_user_model().objects.create_user(email, 'testpublic1234')
        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user with no email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'testpublic1234')

    def test_create_superuser(self):
        """Test creating a new superuser"""

        user = get_user_model().objects.create_superuser(
            'testsuperuser@example.com', 'testsuperuser1234')

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_candidate_str(self):
        """Test the candidate string representation"""
        candidate = models.Candidate.objects.create(
            name='Candidate 1',
        )

        self.assertEqual(str(candidate), 'Candidate: %s' % (candidate.name))

    def test_vote_str(self):
        """Test the vote string representation"""
        vote = models.Vote.objects.create(
            user=sample_user(),
            name='Vote 1',
            is_vote=True,
            candidate=sample_candidate()
        )

        self.assertEqual(str(vote), 'Vote: %s' % (vote.name))
