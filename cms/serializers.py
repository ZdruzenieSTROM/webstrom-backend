from rest_framework import serializers

from cms import models


class MenuItemShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MenuItem
        exclude = ['priority', 'sites']


class PostLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PostLink
        exclude = ['post']


class PostSerializer(serializers.ModelSerializer):
    links = PostLinkSerializer(many=True)

    class Meta:
        model = models.Post
        fields = '__all__'

    def create(self, validated_data):
        post_links_data = validated_data.pop('links')
        post = models.Post.objects.create(**validated_data)
        for post_link_data in post_links_data:
            models.PostLink.objects.create(post=post, **post_link_data)
        return post
