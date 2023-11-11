from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.timezone import now
from base.models import RestrictedFileField

from competition.models import Event, Series

from .querysets import VisibilityQuerySet


class ModelWithVisibility(models.Model):
    visible_after = models.DateTimeField(verbose_name='Zobrazuj od')
    visible_until = models.DateTimeField(verbose_name='Zobrazuj do')

    objects = VisibilityQuerySet.as_manager()

    def is_visible(self):
        return now() > self.visible_after and now() < self.visible_until
    is_visible.short_description = "Viditeľný"
    is_visible = property(is_visible)

    class Meta:
        abstract = True


class MessageTemplate(models.Model):
    class Meta:
        verbose_name = 'Generické správy pre banner a posty'
        verbose_name_plural = 'Generické správy pre banner a posty'

    name = models.CharField(
        verbose_name='Názov',
        help_text='Pomenovanie generickej správy. Slúži pre orientáciu',
        max_length=50)
    message = models.CharField(
        verbose_name='Generická správa',
        help_text='Generické správy pre banner a posty',
        max_length=200)
    is_active = models.BooleanField(verbose_name='Aktívna', default=True)

    def render_with(self, event):
        return self.message.format(**event.__dict__,)


class Post(ModelWithVisibility):
    class Meta:
        verbose_name = 'príspevok'
        verbose_name_plural = 'príspevky'
        ordering = ['-added_at', ]

    caption = models.CharField(verbose_name='nadpis', max_length=50)
    short_text = models.CharField(
        verbose_name='krátky text',
        help_text='Krátky 1-2 vetový popis.',
        max_length=200)
    details = models.TextField(
        verbose_name='podrobnosti k príspevku',
        help_text='Dlhší text, ktorý sa zobrazí po rozkliknutí.',
        blank=True)
    added_at = models.DateTimeField(verbose_name='pridané',
                                    auto_now_add=True,
                                    editable=False)

    sites = models.ManyToManyField(Site)

    def __str__(self):
        return f'{self.pk}-{self.caption}'


class PostLink(models.Model):
    class Meta:
        verbose_name = 'link k príspevku'
        verbose_name_plural = 'linky k príspevkom'

    post = models.ForeignKey(
        Post,
        verbose_name='Relevantný príspevok',
        related_name='links',
        on_delete=models.CASCADE)
    caption = models.CharField(
        verbose_name='názov',
        help_text='Nápis, ktorý po kliknutí presmeruje na link. Maximálne 2 slová.',
        max_length=25)
    url = models.CharField(verbose_name='URL', max_length=100,
                           help_text='URL stránky kam má preklik viesť')

    def __str__(self):
        return f'{self.post}-{self.caption}'


class MenuItem(models.Model):
    class Meta:
        verbose_name = 'položka v menu'
        verbose_name_plural = 'položky v menu'
        ordering = ['-priority', ]

    caption = models.CharField(
        verbose_name='názov',
        help_text='Nápis, ktorý sa zobrazí v menu. Maximálne 2 slová.',
        max_length=25)
    url = models.CharField(verbose_name='URL',
                           max_length=100,
                           help_text='URL stránky kam má preklik viesť')
    priority = models.SmallIntegerField(
        verbose_name='priorita',
        help_text='Priorita, čím väčšie, tým vyššie v menu.')
    sites = models.ManyToManyField(Site)

    # TODO: Pridať oprávnenia a umožniť tak vedúcovské položky v menu
    # zobrazované aj možno niekde inde


class Logo(models.Model):
    """
    Logo
    """
    class Meta:
        verbose_name = 'logo'
        verbose_name_plural = 'logá'

        ordering = ['name', ]

    name = models.CharField(verbose_name='názov loga', max_length=150)
    disabled = models.BooleanField()
    image = RestrictedFileField(
        content_types=['image/svg+xml', 'image/png'],
        upload_to='logo_images/',
        verbose_name='Logo', null=True, blank=True)

    def __str__(self):
        return f'{self.series.semester.competition.name}-{self.series.semester.year}' \
            f'-{self.series.semester.season[0]}S-S{self.series.order} - {self.order}. úloha'



class InfoBanner(ModelWithVisibility):
    class Meta:
        verbose_name = 'Informácia v pohyblivom baneri'
        verbose_name_plural = 'Informácie v pohyblivom baneri'

    message = models.CharField(
        verbose_name='správa',
        help_text='Správa sa zobrazí v baneri. Správa musí byť stručná - jedna krátka veta.',
        max_length=200)
    page = models.ForeignKey(FlatPage, on_delete=models.CASCADE, null=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True)
    series = models.ForeignKey(Series, on_delete=models.CASCADE, null=True)
    message_template = models.ForeignKey(
        MessageTemplate, on_delete=models.PROTECT, null=True)

    def clean(self):
        try:
            self.render_message()
        except KeyError as key_error:
            raise ValidationError(
                'Template správy nie je kompatibilný s priradenou akciou') from key_error

    def render_message(self):
        if self.message_template is None:
            return self.message
        if self.event is not None:
            return self.message_template.render_with(self.event)
        if self.series is not None:
            return self.message_template.render_with(self.series)
        return self.message_template.render_with({})
