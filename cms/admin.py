from django.contrib import admin

from cms.models import MenuItem, Post, PostLink


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = (
        'caption',
        'url',
        'priority'
    )

    list_filter = (
        'sites',
    )


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


@admin.register(PostLink)
class PostLinkAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'caption',
        'url',
    )
