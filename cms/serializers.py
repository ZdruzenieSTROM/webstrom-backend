from django_typomatic import ts_interface
from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework import serializers

from cms import models

from .models import FileUpload


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
class LogoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Logo
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


class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileUpload
        fields = ('id', 'file')
