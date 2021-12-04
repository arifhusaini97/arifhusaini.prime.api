from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
import json
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Vote, Candidate

from app_vote.serializers import VoteSerializer

VOTES_URL = reverse('app_vote:vote-list')


def detail_url(id):
    """Return vote detail url"""
    return reverse('app_vote:vote-detail', args=[id])


class PublicVotesApiTests(TestCase):
    """Test the publicly available"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving vote"""

        res = self.client.get(VOTES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateVotesApiTests(TestCase):
    """Test the authorized used tags API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'testprivate@example.com',
            'testprivate1234'
        )

        self.candidate_1 = Candidate.objects.create(name='Candidate 1')

        self.candidate_2 = Candidate.objects.create(name='Candidate 1')

        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_votes(self):
        """Test retrieving votes"""

        Vote.objects.create(
            user=self.user, name='Vote 1',
            candidate=self.candidate_1, is_vote=True)

        Vote.objects.create(
            user=self.user, name='Vote 2',
            candidate=self.candidate_2, is_vote=False)

        res = self.client.get(VOTES_URL)

        votes = Vote.objects.all().order_by('-name')

        serializer = VoteSerializer(votes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_vote(self):
        """Test retrieving vote"""

        vote = Vote.objects.create(
            user=self.user, name='Vote 1',
            candidate=self.candidate_1, is_vote=True)

        Vote.objects.create(
            user=self.user, name='Vote 2',
            candidate=self.candidate_2, is_vote=False)

        url = detail_url(vote.id)

        res = self.client.get(url)

        serializer = VoteSerializer(vote)

        self.assertEqual(res.data, serializer.data)

    def test_votes_limited_to_user(self):
        """Test that votes returned are for the authenticated user"""
        user2 = get_user_model().objects.create_user(
            'testprivate2@example.com',
            'testprivate1234'
        )

        Vote.objects.create(
            user=user2, name='Vote 1',
            candidate=self.candidate_1, is_vote=True)

        Vote.objects.create(
            user=user2, name='Vote 2',
            candidate=self.candidate_2, is_vote=False)

        vote = Vote.objects.create(
            user=self.user, name='Vote 1',
            candidate=self.candidate_2, is_vote=True)

        res = self.client.get(VOTES_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

        self.assertEqual(res.data[0]['name'], vote.name)

    def test_create_vote_successful(self):
        """Test creating a new vote"""
        payload = {'name': 'Vote_1_1',
                   'candidate': self.candidate_1.id, 'is_vote': True}
        self.client.post(VOTES_URL, data=json.dumps(payload),
                         content_type='application/json')

        exists = Vote.objects.filter(
            user=self.user,
            name=payload['name'],
            candidate=payload['candidate'],
            is_vote=True
        ).exists()

        self.assertTrue(exists)

    def test_create_vote_invalid(self):
        """Test creating a new vote with invalid payload"""
        payload = {'name': ''}
        res = self.client.post(VOTES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
