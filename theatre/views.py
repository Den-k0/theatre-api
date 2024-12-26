from django.db.models import F, Count
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.utils.dateparse import parse_date
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from theatre.models import (
    Actor,
    Genre,
    Play,
    TheatreHall,
    Performance,
    Reservation,
)
from theatre.permissions import IsAdminOrIfAuthenticatedReadOnly
from theatre.serializers import (
    ActorSerializer,
    GenreSerializer,
    PlaySerializer,
    TheatreHallSerializer,
    PerformanceSerializer,
    ReservationSerializer,
    PlayListSerializer,
    PlayRetrieveSerializer,
    PerformanceListSerializer,
    PerformanceRetrieveSerializer,
    ReservationListSerializer,
    PlayImageSerializer,
)


class ActorViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly, )


class GenreViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly, )


class PlayViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = Play.objects.all()
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly, )

    @staticmethod
    def _params_to_ints(query_string):
        return [int(str_id) for str_id in query_string.split(",")]

    def get_serializer_class(self):
        if self.action == "list":
            return PlayListSerializer
        if self.action == "retrieve":
            return PlayRetrieveSerializer
        if self.action == "upload_image":
            return PlayImageSerializer
        return PlaySerializer

    def get_queryset(self):
        queryset = self.queryset

        actors = self.request.query_params.get("actors")
        if actors:
            actors = self._params_to_ints(actors)
            queryset = queryset.filter(actors__id__in=actors)

        genres = self.request.query_params.get("genres")
        if genres:
            genres = self._params_to_ints(genres)
            queryset = queryset.filter(genres__id__in=genres)

        title = self.request.query_params.get("title")
        if title:
            queryset = queryset.filter(title__icontains=title)

        queryset = queryset.distinct()

        if self.action in ("list", "retrieve"):
            return queryset.prefetch_related("actors", "genres")

        return queryset

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image"
    )
    def upload_image(self, request, pk=None):
        """http://127.0.0.1:8000/api/theatre/play/5/upload-image/"""
        play = self.get_object()
        serializer = self.get_serializer(play, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "title",
                type=str,
                description="Filter by title name",
                required=False,
            ),
            OpenApiParameter(
                "genres",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by genres ID"
            ),
            OpenApiParameter(
                "actors",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by actors ID"
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get list of plays"""
        return super().list(request, *args, **kwargs)


class TheatreHallViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    queryset = TheatreHall.objects.all()
    serializer_class = TheatreHallSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly, )


class PerformanceViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = Performance.objects.all()
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly, )

    def get_serializer_class(self):
        if self.action == "list":
            return PerformanceListSerializer
        elif self.action == "retrieve":
            return PerformanceRetrieveSerializer
        return PerformanceSerializer

    def get_queryset(self):
        queryset = self.queryset
        date = self.request.query_params.get("date")
        play = self.request.query_params.get("play")

        if date:
            date = parse_date(date)
            queryset = queryset.filter(show_time__date=date)

        if play:
            queryset = queryset.filter(play_id=play)

        if self.action == "list":
            return (
                queryset
                .select_related("play", "theatre_hall")
                .annotate(
                    tickets_available=(
                        F("theatre_hall__rows")
                        * F("theatre_hall__seats_in_row")
                        - Count("tickets")
                    )
                )
            )

        if self.action == "retrieve":
            return queryset.select_related()

        return queryset.distinct()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="date",
                type={"type": "string", "format": "date"},
                description="Filter by date (format YYYY-DD-MM)"
            ),
            OpenApiParameter(
                "play",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by play ID"
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get list of play performances"""
        return super().list(request, *args, **kwargs)


class ReservationSetPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 10


class ReservationViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    pagination_class = ReservationSetPagination
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)

        if self.action == "list":
            queryset = queryset.prefetch_related(
                "tickets__performance__play",
                "tickets__performance__theatre_hall"
            )

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        serializer = self.serializer_class

        if self.action == "list":
            serializer = ReservationListSerializer

        return serializer
