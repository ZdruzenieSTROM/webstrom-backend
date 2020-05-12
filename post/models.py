from django.db import models
from django.contrib.sites.models import Site


class Post(models.Model):
    class Meta:
        verbose_name = 'príspevok'
        verbose_name_plural = 'príspevky'

    sites = models.ManyToManyField(Site)

    title = models.CharField(
        max_length=64,
        verbose_name='nadpis'
    )
    text = models.TextField(
        verbose_name='text príspevku v markdowne'
    )

    published = models.BooleanField(
        default=False,
        verbose_name='viditeľný'
    )
    # TODO: Tu by som nejak možno zapracoval aby ich nebolo pinnutých veľa,
    # prípadne môžeme to aj úplne vypustiť aale príde mi to useful
    pinned = models.BooleanField(
        default=False,
        verbose_name='pripnúť príspevok',
        help_text='Príspevok bude zobrazený vždy na vrchu feedu'
    )

    created_at = models.DateTimeField(
        verbose_name='dátum a čas vytvorenia',
        auto_now_add=True
    )
    modified_at = models.DateTimeField(
        verbose_name='dátum a čas poslednej úpravy',
        auto_now=True
    )

    created_by = models.ForeignKey(
        'user.User',
        verbose_name='autor',
        null=True,
        editable=False,
        on_delete=models.SET_NULL
    )

    def __str__(self):
        return self.title

class ClickableImage(models.Model):
    img_url = models.URLField(
        verbose_name='adresa obrázku',
        null=True
    )
    hyperlink = models.URLField(
        verbose_name='Link kam ťa presmeruje po kliknutí na obrázok',
        null=True
    )
    post = models.ForeignKey(
        Post,
        verbose_name='Príspevok v ktorom sa obrázok zobrazí'
    )
