from django.urls import path, include
from rest_framework.routers import DefaultRouter

from app_vote import views

router = DefaultRouter()

router.register('favorite', views.FavoriteViewSet)
router.register('vote', views.VoteViewSet)
router.register('candidate', views.CandidateViewSet)
router.register('candidates/deleted',
                views.CandidateDeletedAPIView, basename='candidates-deleted')

app_name = 'app_vote'

urlpatterns = [
    path('', include(router.urls)),
    path(
        "candidates/",
        views.CandidateAllAPIView.as_view(),
        name='candidates'
    ),
]
