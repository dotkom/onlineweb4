from rest_framework import serializers

from apps.contribution.models import Repository, RepositoryLanguage


class RepositoryLanguagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryLanguage
        fields = ("type", "size")


class RepositorySerializer(serializers.ModelSerializer):
    languages = RepositoryLanguagesSerializer(many=True)

    class Meta:
        model = Repository
        fields = (
            "id",
            "name",
            "description",
            "url",
            "public_url",
            "issues",
            "updated_at",
            "languages",
        )
