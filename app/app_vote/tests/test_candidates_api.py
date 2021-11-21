from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Candidate

import json

from app_vote.serializers import CandidateSerializer

CANDIDATE_URL = reverse('app_vote:candidate-list')
CANDIDATES_URL = reverse('app_vote:candidates-deleted-list')


def sample_candidate(**params):
    """Create and return a simple candidate"""
    defaults = {
        'name': 'Sample Candidate',
    }

    defaults.update(params)
    return Candidate.objects.create(**defaults)


def detail_url_candidate(id):
    """Return candidate detail url"""
    return reverse('app_vote:candidate-detail', args=[id])


def detail_url_candidates_deleted(id):
    """Return candidate deleted detail url"""
    return reverse('app_vote:candidates-deleted-detail', args=[id])


class PublicCandidatesApiTests(TestCase):
    """Test the publicly available"""

    def setUp(self):
        self.client = APIClient()

    def test_login_not_required(self):
        """Test that login is not required for retrieving candidate"""

        res = self.client.get(CANDIDATE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_retrieve_candidates(self):
        """Test retrieving candidates"""

        Candidate.objects.create(name='Candidate 1')

        Candidate.objects.create(name='Candidate 2')

        res = self.client.get(CANDIDATE_URL)

        candidates = Candidate.objects.all().order_by('-name')

        serializer = CandidateSerializer(candidates, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_candidate(self):
        """Test retrieving candidate"""

        candidate = Candidate.objects.create(name='Candidate 1')

        Candidate.objects.create(name='Candidate 2')

        url = detail_url_candidate(candidate.id)
        res = self.client.get(url)

        serializer = CandidateSerializer(candidate)

        self.assertEqual(res.data, serializer.data)

    def test_partial_update_candidate_need_auth(self):
        """Test updating a candidate with patch needs authentication"""
        candidate_name = 'Primary Name'
        candidate = sample_candidate(name=candidate_name)

        payload = {'name': 'Jamal'}
        url = detail_url_candidate(candidate.id)
        res = self.client.patch(url, payload)
        candidate.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(candidate.name, candidate_name)

    def test_full_update_candidate_need_auth(self):
        """Test updating a candidate with put needs authentication"""
        candidate_name = 'Primary Name'
        candidate_description = 'Primary Description'
        candidate = sample_candidate(
            name=candidate_name, description=candidate_description)
        payload = {'name': 'Jamal', 'description': 'Jamal Description'}
        url = detail_url_candidate(candidate.id)
        res = self.client.put(url, payload)
        candidate.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(candidate.name, candidate_name)
        self.assertEqual(candidate.description, candidate_description)


class PrivateCandidatesApiTests(TestCase):
    """Test the authorized used tags API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'testprivate@example.com',
            'testprivate1234'
        )

        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_partial_update_candidate(self):
        """Test updating a candidate with patch"""
        candidate = sample_candidate()

        payload = {'name': 'Jamal'}
        url = detail_url_candidate(candidate.id)
        self.client.patch(url, payload)
        candidate.refresh_from_db()

        self.assertEqual(candidate.name, payload['name'])

    def test_full_update_candidate(self):
        """Test updating a candidate with put"""
        candidate = sample_candidate()
        payload = {'name': 'Jamal', 'description': 'Jamal Description'}
        url = detail_url_candidate(candidate.id)
        self.client.put(url, payload)
        candidate.refresh_from_db()
        self.assertEqual(candidate.name, payload['name'])
        self.assertEqual(candidate.description, payload['description'])

    def test_soft_delete_candidate(self):
        """Test soft delete a candidate"""
        candidate = sample_candidate()
        url = detail_url_candidate(candidate.id)
        res = self.client.delete(url)

        candidates = Candidate.objects.all().order_by('-name')

        serializer = CandidateSerializer(candidates, many=True)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertNotIn(candidate, serializer.data)

        url = detail_url_candidates_deleted(candidate.id)
        res = self.client.get(url)

        serializer = CandidateSerializer(candidate)

        self.assertEqual(serializer.data['id'], res.data['id'])
        self.assertIsNotNone(res.data['deleted'])

        res = self.client.patch(url, data=json.dumps({'deleted': None}),
                                content_type='application/json')

        candidates = Candidate.objects.all().order_by('-name')

        serializer = CandidateSerializer(candidates, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(res.data, serializer.data)

    def test_hard_delete_candidate(self):
        """Test hard delete a candidate"""
        candidate = sample_candidate()
        url = detail_url_candidate(candidate.id)
        self.client.delete(url)

        url = detail_url_candidates_deleted(candidate.id)
        res = self.client.delete(url)

        candidates = Candidate.objects.all().order_by('-name')

        serializer = CandidateSerializer(candidates, many=True)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertNotIn(candidate, serializer.data)
