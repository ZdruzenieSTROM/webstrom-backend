from django_typomatic import ts_interface
from rest_framework import serializers
from drf_writable_nested.serializers import WritableNestedModelSerializer

from cms import models


@ts_interface(context='cms')
class MenuItemShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MenuItem
        exclude = ['priority', 'sites']


@ts_interface(context='cms')
class PostLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PostLink
        exclude = ['post']


@ts_interface(context='cms')
class PostSerializer(WritableNestedModelSerializer):
    links = PostLinkSerializer(many=True)

    class Meta:
        model = models.Post
        fields = '__all__'


@ts_interface(context='cms')
class InfoBannerSerializer(serializers.ModelSerializer):
    rendered_message = serializers.CharField(source='render_message')

    class Meta:
        model = models.InfoBanner
        fields = ['rendered_message']


@ts_interface(context='cms')
class MessageTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MessageTemplate
        fields = ['message']
