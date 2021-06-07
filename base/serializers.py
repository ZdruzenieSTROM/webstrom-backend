from django_typomatic import ts_interface
from rest_framework import serializers
from django.contrib.flatpages.models import FlatPage

@ts_interface()
class FlatPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlatPage
        fields = '__all__'
