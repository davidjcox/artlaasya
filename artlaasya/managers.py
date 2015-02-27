"""artlaasya managers"""

from django.db import models
from django.utils import timezone

from datetime import timedelta



class ArtistQuerySet(models.QuerySet):
    
    DAYS = 30
    DATE = timezone.now() - timedelta(days=DAYS)
    
    def related_artwork(self):
        return self.select_related('artwork_artist')
    
    def active(self):
        return self.filter(is_active=True)
    
    def recent(self):
        return self.filter(created__gte=self.DATE)
    
    def orderly(self):
        return self.order_by('last_name', 'first_name')
    
    def distinctly(self):
        return self.distinct('last_name', 'first_name')
# /ArtistQuerySet


class ArtistManager(models.Manager):
    
    def get_queryset(self):
        return ArtistQuerySet(self.model, using=self._db)
    
    def related_artwork(self):
        return self.get_query_set().related_artwork()
    
    def active(self):
        return self.get_queryset().active()
    
    def recent(self):
        return self.get_queryset().recent()
    
    def orderly(self):
        return self.get_queryset().orderly()
    
    def distinctly(self):
        return self.get_queryset().distinctly()
# /ArtistManager


class GenreQuerySet(models.QuerySet):
    
    def contemporary(self):
        return self.filter(name="Contemporary")
    
    def traditional(self):
        return self.exclude(name="Contemporary")
# /GenreQuerySet


class GenreManager(models.Manager):
    
    def get_queryset(self):
        return GenreQuerySet(self.model, using=self._db)
    
    def contemporary(self):
        return self.get_queryset().contemporary()
    
    def traditional(self):
        return self.get_queryset().traditional()
# /GenreManager

    
class ArtworkQuerySet(models.QuerySet):
    
    DAYS = 30
    DATE = timezone.now() - timedelta(days=DAYS)
    
    def active(self):
        return self.filter(is_active=True)
    
    def recent(self):
        return self.filter(created__gte=self.DATE)
    
    def representative(self):
        return self.filter(is_representative=True)
    
    def orderly(self):
        return self.order_by('artist__last_name', 'artist__first_name')
    
    def distinctly(self):
        return self.distinct('artist__last_name', 'artist__first_name')
    
    def contemporary(self):
        return self.filter(genre__name="Contemporary")
    
    def traditional(self):
        return self.exclude(genre__name="Contemporary")
# /ArtworkQuerySet


class ArtworkManager(models.Manager):
    
    def get_queryset(self):
        return ArtworkQuerySet(self.model, using=self._db)
    
    def active(self):
        return self.get_queryset().active()
    
    def recent(self):
        return self.get_queryset().recent()
    
    def representative(self):
        return self.get_queryset().representative()
    
    def orderly(self):
        return self.get_queryset().orderly()
    
    def distinctly(self):
        return self.get_queryset().distinctly()
    
    def contemporary(self):
        return self.get_queryset().contemporary()
    
    def traditional(self):
        return self.get_queryset().traditional()
# /ArtworkManager


class EventQuerySet(models.QuerySet):
    
    def active(self):
        return self.filter(is_active=True)
# /EventQuerySet


class EventManager(models.Manager):
    
    def get_queryset(self):
        return EventQuerySet(self.model, using=self._db)
    
    def active(self):
        return self.get_queryset().active()
# /EventManager


#EOF - artlaasya managers