from django.db import models
from django.contrib.sites.models import Site

# Create your models here.

@with_author
@with_timestamp
class Post(models.Model):
    class Meta:
        verbose_name = 'príspevok'
        verbose_name_plural = 'príspevky'

    sites = models.ManyToManyField(Site)

    title = models.CharField(
        max_length = 64,
        verbose_name = 'nadpis'
    )
    text = models.TextField(
        verbose_name='text príspevku'
    )
    img_url = models.URLField(
        verbose_name='adresa obrázku'
    )

    published = models.BooleanField(
        default = False,
        verbose_name = 'viditeľný'
    )
    # Tu by som nejak možno zapracoval aby ich nebolo pinnutých veľa, prípadne môžeme to aj úplne vypustiť aale príde mi to useful
    pinned = models.BooleanField(
        default = False,
        verbose_name = 'pripnúť príspevok',
        help_text = 'Príspevok bude zobrazený vždy na vrchu feedu'
    )

    def __str__(self):
        return self.title
