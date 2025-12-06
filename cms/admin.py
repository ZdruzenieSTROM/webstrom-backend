from django.contrib import admin

from cms.models import (FileUpload, Gallery, InfoBanner, Logo, MenuItem,
                        MessageTemplate, Post, PostLink)


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


@admin.register(Logo)
class LogoAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'disabled'
    )


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'caption',
        'short_text',
        'details',
        'added_at',
        'visible_after',
        'visible_until',
        'is_visible'
    )
    search_fields = (
        'caption',
        'short_text'
    )


@admin.register(PostLink)
class PostLinkAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'caption',
        'url',
    )

    search_fields = (
        'caption',
        'url'
    )


@admin.register(MessageTemplate)
class MessageTemplateAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'message',
        'is_active'
    )


@admin.register(InfoBanner)
class InfoBannerAdmin(admin.ModelAdmin):
    list_display = (
        'message',
        'visible_after',
        'visible_until',
        'message_template'
    )

    search_fields = (
        'message',
    )


admin.site.register(FileUpload)

admin.site.register(Gallery)
