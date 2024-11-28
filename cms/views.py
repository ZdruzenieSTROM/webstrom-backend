

from datetime import datetime

from django.utils.timezone import now
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from cms.models import InfoBanner, Logo, MenuItem, MessageTemplate, Post
from cms.permissions import PostPermission
from cms.serializers import (InfoBannerSerializer, LogoSerializer,
                             MenuItemShortSerializer,
                             MessageTemplateSerializer, PostSerializer)
from competition.models import Competition, Event, Series


class MenuItemViewSet(viewsets.ReadOnlyModelViewSet):
    """Položky menu"""
    queryset = MenuItem.objects.order_by('-priority')
    serializer_class = MenuItemShortSerializer

    def filter_(self, queryset, filter_by: str | None):
        if filter_by == 'menu':
            queryset = queryset.filter(in_menu=True)
        if filter_by == 'footer':
            queryset = queryset.filter(in_footer=True)
        return queryset

    @action(methods=['get'], detail=False, url_path=r'on-site/(?P<site_id>\d+)')
    def on_site(self, request: Request, site_id):
        """Položky menu na stránke(na stránke Matik, Malynár ...)"""
        filter_by = request.query_params.get('type')
        queryset = self.get_queryset().filter(
            sites=site_id)
        items = self.filter_(queryset, filter_by)
        serializer = MenuItemShortSerializer(items, many=True)
        return Response(serializer.data)


class PostViewSet(viewsets.ModelViewSet):
    """Príspevky"""
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (PostPermission,)
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['sites']
    search_fields = ['caption', 'short_text', 'details']
    ordering_fields = ['added_at', 'visible_until', 'visible_after']
    ordering = ['added_at']

    @action(detail=False)
    def visible(self, request):
        """Iba príspevky viditeľné pre užívateľov"""
        posts = self.filter_queryset(self.get_queryset()).visible()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)


class LogoViewSet(viewsets.ReadOnlyModelViewSet):
    """Logá"""
    queryset = Logo.objects.all()
    serializer_class = LogoSerializer


class InfoBannerViewSet(viewsets.ModelViewSet):
    """Správy v čiernom info banneri"""
    serializer_class = InfoBannerSerializer
    queryset = InfoBanner.objects.visible()
    filterset_fields = ['event', 'page', 'series']

    def format_date(self, datetime_: datetime):
        return datetime_.strftime("%d.%m.%Y %H:%M")

    @action(methods=['get'], detail=False, url_path=r'series-problems/(?P<series_id>\d+)')
    def series_problems(self, request, series_id: int) -> list[str]:
        series_messages = InfoBanner.objects.filter(series=series_id).all()
        messages = [message.render_message() for message in series_messages]
        series = Series.objects.get(pk=series_id)
        if series.complete:
            messages.append('Séria je uzavretá')
        elif series.can_submit:
            messages.append(
                f'Termín série: {self.format_date(series.deadline)}'
            )
        else:
            messages.append('Prebieha opravovanie')
        return Response(messages)

    @action(methods=['get'], detail=False, url_path=r'series-results/(?P<series_id>\d+)')
    def series_results(self, request, series_id):
        series = Series.objects.get(pk=series_id)
        if not series.complete:
            return Response(['Poradie nie je uzavreté'])
        return Response([])

    @action(methods=['get'], detail=False, url_path=r'competition/(?P<competition_id>\d+)')
    def event(self, request, competition_id: int) -> list[str]:
        competition = Competition.objects.get(pk=competition_id)
        try:
            event = Event.objects.filter(
                competition=competition_id, end__gte=now()).earliest('start')
        except Event.DoesNotExist:
            return Response([])
        event_messages = InfoBanner.objects.filter(event=event).all()
        messages = [message.render_message() for message in event_messages]

        if event.registration_link is not None:
            if competition.competition_type.name == 'Seminár':
                if event.registration_link.start > now():
                    messages.append(
                        'Prihlasovanie na sústredenie bude spustené '
                        f'{self.format_date(event.registration_link.start)}')
                elif event.registration_link.end > now():
                    messages.append(
                        'Prihlasovanie na sústredenie končí '
                        f'{self.format_date(event.registration_link.end)}')
            else:
                if event.registration_link.start > now():
                    messages.append(
                        'Registrácia bude spustená '
                        f'{self.format_date(event.registration_link.start)}')
                elif event.registration_link.end > now():
                    messages.append(
                        'Registrácia bude uzavretá '
                        f'{self.format_date(event.registration_link.end)}')

                else:
                    messages.append('Registrácia ukončená')
        return Response(messages)


class MessageTemplateViewSet(viewsets.ModelViewSet):
    """Templaty správ pre info banner/posty"""
    serializer_class = MessageTemplateSerializer
    queryset = MessageTemplate.objects.all()
