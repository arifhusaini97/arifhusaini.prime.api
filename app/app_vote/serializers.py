from rest_framework import serializers

from core.models import Favorite, Candidate, Vote


class FavoriteSerializer(serializers.ModelSerializer):
    """Serializer for favorite objects"""

    class Meta:
        model = Favorite
        fields = '__all__'
        read_only_fields = ('id', 'created', 'modified',
                            'deleted', 'is_active', 'user')


class VoteSerializer(serializers.ModelSerializer):
    """Serializer for vote objects"""

    class Meta:
        model = Vote
        fields = '__all__'
        read_only_fields = ('id', 'created', 'modified',
                            'deleted', 'is_active', 'user')


class CandidateSerializer(serializers.ModelSerializer):
    """Serializer for candidate objects"""

    class Meta:
        model = Candidate
        fields = '__all__'
        read_only_fields = ('id', 'created', 'modified',
                            'deleted', 'is_active')
