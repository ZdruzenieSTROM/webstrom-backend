from django.contrib.flatpages.models import FlatPage
from django_typomatic import ts_interface
from rest_framework import serializers


@ts_interface(context='base')
class FlatPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlatPage
        fields = '__all__'
