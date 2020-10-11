from django.contrib import admin
from cms.models import Post, PostLink


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'caption',
        'short_text',
        'details',
        'added_at',
        'show_after',
        'disable_after',
        'is_visible'
    )

    list_filter = (
        'caption',
    )


@admin.register(PostLink)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'caption',
        'url',
    )
