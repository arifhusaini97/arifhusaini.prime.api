from app_vote import serializers
from core.models import Favorite, Candidate, Vote
from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, \
    IsAuthenticatedOrReadOnly


class BaseVoteAttrViewSet(viewsets.GenericViewSet,
                          mixins.ListModelMixin,
                          mixins.CreateModelMixin,
                          mixins.RetrieveModelMixin):
    """Base viewset for user vote attributes"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        assigned_only = bool(
            # Because params will always be string
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(app_vote__isnull=False)

        return queryset.filter(
            user=self.request.user
        ).order_by('-name').distinct()

    def perform_create(self, serializer):
        """Create a new object"""
        serializer.save(user=self.request.user)


class FavoriteViewSet(BaseVoteAttrViewSet):
    """Manage favorites in the database"""

    queryset = Favorite.objects.all()
    serializer_class = serializers.FavoriteSerializer


class VoteViewSet(BaseVoteAttrViewSet):
    """Manage favorites in the database"""

    queryset = Vote.objects.all()
    serializer_class = serializers.VoteSerializer


class CandidateViewSet(viewsets.ModelViewSet):
    """Manage candidates in the database"""

    queryset = Candidate.objects.all()
    serializer_class = serializers.CandidateSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        """Return objects for all users"""
        assigned_only = bool(
            # Because params will always be string
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(app_vote__isnull=False)

        return queryset.order_by('-name').distinct()


class CandidateAllAPIView(viewsets.ModelViewSet):
    """Manage deleted candidates"""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = serializers.CandidateSerializer
    http_method_names = ['get']

    def get_queryset(self):
        return Candidate.objects.all_with_deleted()


class CandidateDeletedAPIView(viewsets.ModelViewSet):
    """Manage deleted candidates"""

    queryset = Candidate.objects.deleted_only()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = serializers.CandidateSerializer
    http_method_names = ['get', 'delete', 'put', 'patch']
