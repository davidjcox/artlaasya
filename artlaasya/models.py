"""artlaasya models"""

from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse

import os
import string
from datetime import date

import deepzoom.models as deepzoom_models

import artlaasya.managers as artlaasya_managers
from artlaasya.mixins import ModelDiffMixin



class ArtistRatchet(models.Model):
    """
    Provides a numerical suffix for appendeding to an `Artist` slug so that 
    uniqueness is ensured in the event more than one artist shares the same 
    name.  The same could be accomplished using the primary key, but this is 
    more uniform and creates more aesthetically pleasing URLs.
    
    The suffix only ratchets, so CRUD operations are guaranteed to produce 
    slugs that cannot be mistakenly re-applied to different artists.
    """
    class Meta:
        app_label = settings.APP_LABEL
        ordering = ['name']
    
    ratchets = models.Manager()
    
    
    name = models.CharField(max_length=61,
                            unique=True,
                            default="artistratchet_name",
                            editable=False)
    
    suffix = models.PositiveIntegerField(default=0,
                                         editable=False)
# /ArtistRatchet


class Artist(ModelDiffMixin, models.Model):
    """
    Represents an artist.
    
    Composed with `ModelDiffMixin` mixin which tracks field changes.
    
    Uses `ArtistManager` manager class which provides friendlier manager name 
    and a set of common querysets for artists.
    
    Provides optional uploadable `biography` PDF file.
    """
    class Meta:
        app_label = settings.APP_LABEL
        get_latest_by = 'created'
        ordering = ['last_name', 'first_name']
    
    artists = artlaasya_managers.ArtistManager()
    
    
    def get_sluggified_filename(instance, filename):
        _extension = os.path.splitext(filename)[1]
        return instance.slug + _extension
    
    
    def get_biography_filepath(instance, filename):
        _filename = instance.get_sluggified_filename(filename)
        return os.path.join(settings.DEFAULT_ARTIST_BIOGRAPHY_ROOT, _filename)
    
    
    first_name = models.CharField(max_length=30,
                                  help_text="Max 30 characters.")
    
    last_name = models.CharField(max_length=30,
                                 help_text="Max 30 characters.")
    
    slug = models.SlugField(max_length=65,
                            unique=True,
                            editable=False,
                            help_text="(system-constructed)")
    
    is_active = models.BooleanField(default=True)
    
    description = models.TextField(blank=True,
                                   help_text="Unlimited characters.")
    
    biography = models.FileField(upload_to=get_biography_filepath,
                                 blank=True,
                                 help_text="PDF-formatted file.")
    
    created = models.DateTimeField(auto_now_add=True,
                                   editable=False)
    
    updated = models.DateTimeField(auto_now=True,
                                   editable=False)
    
    
    def get_absolute_url(self):
        return reverse('v_artist',
                       kwargs={'artist_name': self.slug})
    
    
    def __unicode__(self):
        return six.u('%s %s') % (self.first_name, self.last_name)
    
    
    def __str__(self):
        return '%s %s' % (self.first_name, self.last_name)
# /Artist


class Genre(ModelDiffMixin, models.Model):
    """
    Represents an artwork genre.
    
    Composed with `ModelDiffMixin` mixin which tracks field changes.
    """
    class Meta:
        app_label = settings.APP_LABEL
        get_latest_by = 'created'
        ordering = ['name']
    
    genres = artlaasya_managers.GenreManager()
    
    
    name = models.CharField(max_length=60,
                            unique=True,
                            help_text="Max 60 characters.")
    
    slug = models.SlugField(max_length=65,
                            editable=False)
    
    is_active = models.BooleanField(default=True)
    
    location = models.CharField(max_length=100,
                                blank=True,
                                help_text="Max 100 characters.")
    
    description = models.TextField(blank=True,
                                   help_text="Unlimited characters.")
    
    
    def __unicode__(self):
        return six.u('%s') % (self.name)
    
    
    def __str__(self):
        return '%s' % (self.name)
# /Genre


class ArtworkRatchet(models.Model):
    """
    Provides a numerical suffix for appendeding to an Artwork slug so that 
    uniqueness is ensured in the event more than one artwork shares the same 
    title.  The same could be accomplished using the primary key, but this is 
    more uniform and creates more aesthetically pleasing URLs.
    
    The suffix only ratchets, so CRUD operations are guaranteed to produce 
    slugs that cannot be mistakenly re-applied to different artworks.
    """
    class Meta:
        app_label = settings.APP_LABEL
        ordering = ['title']
    
    ratchets = models.Manager()
    
    
    title = models.CharField(max_length=100,
                            unique=True,
                            default="artworkratchet_title",
                            editable=False)
    
    suffix = models.PositiveIntegerField(default=0,
                                         editable=False)
# /ArtworkRatchet


class Artwork(deepzoom_models.UploadedImage):
    """
    Represents an artwork.
    
    Composed with `ModelDiffMixin` mixin which tracks field changes.
    
    Uses `ArtworkManager` manager class which provides friendlier manager name 
    and a set of common querysets for artworks.
    
    Links to an artist.
    
    Provides the means to designate an artwork representative for the artist.
    
    Provides the means to display a replacement pricing message in place of 
    a price, if needed.
    """
    class Meta:
        app_label = settings.APP_LABEL
        get_latest_by = 'created'
        ordering = ['artist__last_name', 'artist__first_name', 'name', 'title']
    
    artworks = artlaasya_managers.ArtworkManager()
    
    
    STYLE_CHOICES = (
        ('TRAD', 'Traditional'), 
        ('ABST', 'Abstract'), 
        ('FIGU', 'Figurative'), 
        ('SEMA', 'Semi-Abstract'), 
        ('SEMF', 'Semi-Figurative'), 
    )
    
    UNIT_CHOICES = (
        ('C', 'cm'),
        ('I', 'in'),
    )
    
    STATUS_CHOICES = (
        ('AVAL', 'Available'),
        ('SOLD', 'Sold'),
    )
    
    title = models.CharField(max_length=100,
                             help_text="Max 100 characters.")
    
    is_active = models.BooleanField(default=True)
    
    inventory_name = models.CharField(max_length=100,
                                      unique=True,
                                      help_text="Max 100 characters.")
    
    internal_name = models.CharField(max_length=100,
                                     unique=True,
                                     help_text="Max 100 characters.")
    
    artist = models.ForeignKey(Artist,
                               related_name='artwork_artist')
    
    year = models.CharField(max_length=4,
                            blank=True,
                            help_text="Max 4 characters.")
    
    is_representative = models.BooleanField(default=False)
    
    genre = models.ForeignKey(Genre,
                              related_name='artwork_genre')
    
    style_class = models.CharField(max_length=4,
                                   choices=STYLE_CHOICES,
                                   default='TRAD')
    
    medium_description = models.CharField(max_length=100,
                                          help_text="Max 100 characters.")
    
    description = models.TextField(blank=True,
                                   help_text="Unlimited characters.")
    
    image_height = models.DecimalField(max_digits=10,
                                       decimal_places=2,
                                       blank=True,
                                       null=True,
                                       help_text="Two digits after decimal \
                                       point.")
    
    image_width = models.DecimalField(max_digits=10,
                                      decimal_places=2,
                                      blank=True,
                                      null=True,
                                      help_text="Two digits after decimal \
                                      point.")
    
    measurement_units = models.CharField(max_length=2,
                                         choices=UNIT_CHOICES,
                                         default='I',
                                         blank=True)
    
    height_metric = models.DecimalField(max_digits=10,
                                        decimal_places=2,
                                        blank=True,
                                        null=True,
                                        editable=False,
                                        help_text="(system-calculated)")
    
    width_metric = models.DecimalField(max_digits=10,
                                       decimal_places=2,
                                       blank=True,
                                       null=True,
                                       editable=False,
                                       help_text="(system-calculated)")
    
    metric_units = models.CharField(max_length=2,
                                    choices=UNIT_CHOICES,
                                    default='C',
                                    blank=True,
                                    editable=False,
                                    help_text="(system-assigned)")
    
    height_imperial = models.DecimalField(max_digits=10,
                                          decimal_places=2,
                                          blank=True,
                                          null=True,
                                          editable=False,
                                          help_text="(system-calculated)")
    
    width_imperial = models.DecimalField(max_digits=10,
                                         decimal_places=2,
                                         blank=True,
                                         null=True,
                                         editable=False,
                                         help_text="(system-calculated)")
    
    imperial_units = models.CharField(max_length=2,
                                      choices=UNIT_CHOICES,
                                      default='I',
                                      blank=True,
                                      editable=False,
                                      help_text="(system-assigned)")
    
    price = models.PositiveIntegerField(help_text="Displayed only if price is \
                                        toggled to be displayed.")
    
    is_price_displayed = models.BooleanField(default=True)
    
    alternative_pricing_message = models.CharField(max_length=100,
                                                   default="Please inquire",
                                                   blank=True,
                                                   help_text="Max 100 characters.\
                                                   Displayed only if price \
                                                   is toggled NOT to be \
                                                   displayed.")
    
    status = models.CharField(max_length=4,
                              choices=STATUS_CHOICES,
                              default='AVAL')
    
    
    def get_absolute_url(self):
        return reverse('v_artwork',
                       kwargs={'artist_name': self.artist.slug,
                               'artwork_title': self.slug})
    
    
    def __unicode__(self):
        return six.u('%s') % (self.title)
    
    
    def __str__(self):
        return '%s' % (self.title)
# /Artwork


class EventRatchet(models.Model):
    """
    Provides a numerical suffix for appendeding to an Event slug so that 
    uniqueness is ensured in the event more than one event shares the same 
    title.  The same could be accomplished using the primary key, but this is 
    more uniform and creates more aesthetically pleasing URLs.
    
    The suffix only ratchets, so CRUD operations are guaranteed to produce 
    slugs that cannot be mistakenly re-applied to different events.
    """
    class Meta:
        app_label = settings.APP_LABEL
        ordering = ['title']
    
    ratchets = models.Manager()
    
    
    title = models.CharField(max_length=128,
                            unique=True,
                            default="eventratchet_title",
                            editable=False)
    
    suffix = models.PositiveIntegerField(default=0,
                                         editable=False)
# /EventRatchet


class Event(ModelDiffMixin, models.Model):
    """
    Represents a gallery event.
    
    Composed with `ModelDiffMixin` mixin which tracks field changes.
    
    Uses `EventManager` manager class which provides friendlier manager name 
    and a set of common querysets for events.
    
    Links to an artist.
    
    Provides an display image.
    
    Provides start/end dates and times.
    """
    class Meta:
        app_label = settings.APP_LABEL
        get_latest_by = 'created'
        ordering = ['-start_date']
    
    events = artlaasya_managers.EventManager()
    
    
    def get_sluggified_filename(instance, filename):
        _extension = os.path.splitext(filename)[1]
        return instance.slug + _extension
    
    
    def get_event_image_filepath(instance, filename):
        _filename = instance.get_sluggified_filename(filename)
        return os.path.join(settings.DEFAULT_EVENT_IMAGE_ROOT, _filename)
    
    
    title = models.CharField(max_length=128,
                             unique=True,
                             help_text="Max 128 characters.")
    
    is_active = models.BooleanField(verbose_name="is event still active",
                                    default=True)
    
    slug = models.SlugField(max_length=132,
                            editable=False,
                            help_text="(system-constructed)")
    
    type = models.CharField(max_length = 128,
                            help_text="Max 128 characters.")
    
    artist = models.ManyToManyField(Artist,
                                    related_name='events_presented',
                                    blank=True,
                                    null=True)
    
    image = models.ImageField(upload_to=get_event_image_filepath,
                              help_text="Image will be automatically resized.")
    
    total_seats = models.PositiveIntegerField(blank=True,
                                              null=True,
                                              help_text="Total seats allotted.")
    
    is_admission = models.BooleanField(default=False)
    
    admission_price = models.PositiveIntegerField(blank=True,
                                                  null=True,
                                                  help_text="Displayed only if \
                                                  admission is charged.")
    
    start_date = models.DateField(default=date.today(),
                                  help_text="Set to date of event.")
    
    end_date = models.DateField(default=date.today(),
                                help_text="Set to start date if one-day event.")
    
    time = models.CharField(max_length=20,
                            default='6:00 pm - 9:00 pm',
                            help_text="Max 20 characters.")
    
    location = models.CharField(max_length=128,
                                help_text="Max 128 characters.")
    
    details = models.TextField(max_length=1024,
                               help_text="Unlimited characters.")
    
    created = models.DateTimeField(auto_now_add=True,
                                   editable=False)
    
    updated = models.DateTimeField(auto_now=True,
                                   editable=False)
   
    
    def get_absolute_url(self):
        return reverse('v_events', kwargs={
                       'event_title': self.slug})

    
    def __unicode__(self):
        return six.u('%s') % (self.title)
    
    
    def __str__(self):
        return '%s' % (self.title)
# /Event


#EOF - artlaasya models
