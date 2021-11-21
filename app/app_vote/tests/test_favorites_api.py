from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Favorite, Candidate

from app_vote.serializers import FavoriteSerializer

FAVORITES_URL = reverse('app_vote:favorite-list')


def detail_url(id):
    """Return favorite detail url"""
    return reverse('app_vote:favorite-detail', args=[id])


class PublicFavoritesApiTests(TestCase):
    """Test the publicly available"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving favorite"""

        res = self.client.get(FAVORITES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateFavoritesApiTests(TestCase):
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

    def test_retrieve_favorites(self):
        """Test retrieving favorites"""

        Favorite.objects.create(
            user=self.user, name='Favorite 1', candidate=self.candidate_1)

        Favorite.objects.create(
            user=self.user, name='Favorite 2', candidate=self.candidate_2)

        res = self.client.get(FAVORITES_URL)

        favorites = Favorite.objects.all().order_by('-name')

        serializer = FavoriteSerializer(favorites, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_favorite(self):
        """Test retrieving favorite"""

        favorite = Favorite.objects.create(
            user=self.user, name='Favorite 1', candidate=self.candidate_1)

        Favorite.objects.create(
            user=self.user, name='Favorite 2', candidate=self.candidate_2)

        url = detail_url(favorite.id)
        res = self.client.get(url)

        serializer = FavoriteSerializer(favorite)

        self.assertEqual(res.data, serializer.data)

    def test_favorites_limited_to_user(self):
        """Test that favorites returned are for the authenticated user"""
        user2 = get_user_model().objects.create_user(
            'testprivate2@example.com',
            'testprivate1234'
        )

        Favorite.objects.create(
            user=user2, name='Favorite 1', candidate=self.candidate_1)
        Favorite.objects.create(
            user=user2, name='Favorite 2', candidate=self.candidate_2)

        favorite = Favorite.objects.create(
            user=self.user, name='Favorite 1', candidate=self.candidate_2)

        res = self.client.get(FAVORITES_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

        self.assertEqual(res.data[0]['name'], favorite.name)

    def test_create_favorite_successful(self):
        """Test creating a new favorite"""
        payload = {'name': 'Favorite_1_1',
                   'candidate': self.candidate_1.id}
        self.client.post(FAVORITES_URL, payload)

        exists = Favorite.objects.filter(
            user=self.user,
            name=payload['name'],
            candidate=payload['candidate']
        ).exists()

        self.assertTrue(exists)

    def test_create_favorite_invalid(self):
        """Test creating a new favorite with invalid payload"""
        payload = {'name': ''}
        res = self.client.post(FAVORITES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
