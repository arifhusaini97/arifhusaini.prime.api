# from django.urls import reverse
# from django.test import TestCase

# from rest_framework import status
# from rest_framework.test import APIClient

# from core.models import Country

# from app_vote.serializers import CountrySerializer

# CANDIDATES_URL = reverse('app_vote:country-list')


# def detail_url(id):
#     """Return country detail url"""
#     return reverse('app_vote:country-detail', args=[id])


# class PublicCountriesApiTests(TestCase):
#     """Test the publicly available"""

#     def setUp(self):
#         self.client = APIClient()

#     def test_login_not_required(self):
#         """Test that login is not required for retrieving country"""

#         res = self.client.get(CANDIDATES_URL)

#         self.assertEqual(res.status_code, status.HTTP_200_OK)

#     def test_retrieve_countries(self):
#         """Test retrieving countries"""

#         Country.objects.create(name='Country 1')

#         Country.objects.create(name='Country 2')

#         res = self.client.get(CANDIDATES_URL)

#         countries = Country.objects.all().order_by('-name')

#         serializer = CountrySerializer(countries, many=True)

#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#         self.assertEqual(res.data, serializer.data)

#     def test_retrieve_country(self):
#         """Test retrieving country"""

#         country = Country.objects.create(name='Country 1')

#         Country.objects.create(name='Country 2')

#         url = detail_url(country.id)
#         res = self.client.get(url)

#         serializer = CountrySerializer(country)

#         self.assertEqual(res.data, serializer.data)
