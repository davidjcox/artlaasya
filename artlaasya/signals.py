'''artlaasya signals'''

from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save, pre_delete

try:
    from django.utils.text import slugify
except ImportError:
    try:
        from django.template.defaultfilters import slugify
    except ImportError:
        print("Unable to import `slugify`.")
except:
    print("Unable to import `slugify`.")

from decimal import Decimal

from artlaasya.utils import is_django_version_greater_than, delete_uploaded_file

from artlaasya.models import (Artist,
                              ArtistRatchet,
                              Genre,
                              Artwork,
                              ArtworkRatchet,
                              Event,
                              EventRatchet)



DJANGO_SAVE_UPDATEABLE = is_django_version_greater_than(1, 4)


@receiver(pre_save, sender=Artist)
def slugify__artist(sender, instance, slugify=slugify, **kwargs):
    """
    Manages the uniquely numbered suffix for `name`.
    Artist [`first_name` + `last_name` + suffix] --> `slug`.
    """
    name_fields_changed = ('first_name' in instance.changed_fields  or
                           'last_name' in instance.changed_fields)
    
    if (name_fields_changed or not instance.slug):
        _name = instance.__str__().lower()
        _ratchet, _created = ArtistRatchet.ratchets.get_or_create(name=_name)
        _incremented_suffix = _ratchet.suffix + 1
        _ratchet.suffix = _incremented_suffix
        _ratchet.save()
        _suffix = str.zfill(str(_incremented_suffix), 3)
        instance.slug = slugify('-'.join([_name, _suffix]))


@receiver(post_save, sender=Artist)
def deactivate_artworks_of_inactive_artist(sender, instance, created, **kwargs):
    """
    Ensures that all artworks of an artist are deactivated when artist is
    deactivated.
    """
    is_active_field_changed = ('is_active' in instance.changed_fields)
    
    if (is_active_field_changed and not instance.is_active):
        for _artwork in instance.artworks_authored.all():
            if _artwork.is_active:
                _artwork.is_active = False
                if DJANGO_SAVE_UPDATEABLE:
                    _artwork.save(update_fields=['is_active'])
                else:
                    _artwork.save()


@receiver(pre_save, sender=Artist, dispatch_uid="d__a_b")
def delete__artist_biography(sender, instance, **kwargs):
    """
    If file already exists, but new file uploaded, delete existing file.
    """
    biography_field_changed = ('biography' in instance.changed_fields)
    
    if biography_field_changed:
        previous_file = instance.get_field_diff('biography')[0]
        if previous_file:
            delete_uploaded_file(previous_file.path)


@receiver(pre_delete, sender=Artist, dispatch_uid="d__a")
def delete__artist(sender, instance, **kwargs):
    """
    Deletes `biography` uploaded file when Artist is deleted.
    """
    if instance.biography:
        delete_uploaded_file(instance.biography.path)


@receiver(pre_save, sender=Genre)
def slugify__genre(sender, instance, slugify=slugify, **kwargs):
    """
    Manages the slugifying of `name`.
    Genre [`name`] --> `slug`.
    """
    name_fields_changed = ('name' in instance.changed_fields)
    
    if (name_fields_changed or not instance.slug):
        _name = instance.__str__().lower()
        instance.slug = slugify(_name)


@receiver(pre_save, sender=Artwork)
def name_slugify__artwork(sender, instance, slugify=slugify, **kwargs):
    """
    Manages the uniquely numbered suffix for `title`.
    Artwork [`title` + suffix] --> `name' --> `slug`.
    UploadedImage provides `name` and `slug`.
    """
    title_field_changed = ('title' in instance.changed_fields)
    if (title_field_changed or not instance.name):
        _title=instance.title.lower()
        _ratchet, _created = ArtworkRatchet.ratchets.get_or_create(title=_title)
        _incremented_suffix = _ratchet.suffix + 1
        _ratchet.suffix = _incremented_suffix
        _ratchet.save()
        _suffix = str.zfill(str(_incremented_suffix), 3)
        instance.name = '-'.join([instance.title, _suffix])
        instance.slug = slugify(instance.name)


@receiver(pre_save, sender=Artwork)
def calculate_artwork_dimensions(sender, instance, **kwargs):
    """
    Calculates artwork measurements in other measurement system.
    """
    dimension_fields_changed = ('image_height' in instance.changed_fields or 
                                'image_width' in instance.changed_fields or 
                                'measurement_units' in instance.changed_fields)
    
    if (dimension_fields_changed or 
        not instance.image_height and not instance.image_width):
        if instance.measurement_units == 'I':
            instance.height_imperial = instance.image_height
            instance.width_imperial = instance.image_width
            instance.imperial_units = 'I'
            instance.height_metric = round((Decimal(2.54) * instance.image_height), 2)
            instance.width_metric = round((Decimal(2.54) * instance.image_width), 2)
            instance.metric_units = 'C'
        elif instance.measurement_units == 'C':
            instance.height_metric = instance.image_height
            instance.width_metric = instance.image_width
            instance.metric_units = 'C'
            instance.height_imperial = round((Decimal(0.394) * instance.image_height), 2)
            instance.width_imperial = round((Decimal(0.394) * instance.image_width), 2)
            instance.imperial_units = 'I'


@receiver(post_save, sender=Artwork)
def ensure_artwork_uniquely_representative(sender, instance, created, **kwargs):
    """
    Ensures that only one artwork is representative for any one artist.
    """
    if instance.is_representative:
        _artworks = Artwork.artworks.filter(artist__slug=instance.artist.slug
                                   ).exclude(slug=instance.slug)
        for _artwork in _artworks:
            if _artwork.is_representative:
                _artwork.is_representative = False
                if DJANGO_SAVE_UPDATEABLE:
                    _artwork.save(update_fields=['is_representative'])
                else:
                    _artwork.save()


@receiver(pre_save, sender=Event)
def slugify__event(sender, instance, slugify=slugify, **kwargs):
    """
    Manages the uniquely numbered suffix for `title`.
    Event [`title` + suffix] --> `slug`.
    """
    title_field_changed = ('title' in instance.changed_fields)
    
    if (title_field_changed or not instance.title):
        _title=instance.title.lower()
        _ratchet, _created = EventRatchet.ratchets.get_or_create(title=_title)
        _incremented_suffix = _ratchet.suffix + 1
        _ratchet.suffix = _incremented_suffix
        _ratchet.save()
        _suffix = str.zfill(str(_incremented_suffix), 3)
        instance.slug = slugify('-'.join([_title, _suffix]))


@receiver(pre_save, sender=Event, dispatch_uid="d__e_i")
def delete__event_image(sender, instance, **kwargs):
    """
    If image already exists, but new image uploaded, deletes existing image file.
    """
    image_field_changed = ('image' in instance.changed_fields)
    
    if image_field_changed:
        previous_image = instance.get_field_diff('image')[0]
        if previous_image:
            delete_uploaded_file(previous_image.path)


@receiver(pre_delete, sender=Event, dispatch_uid="d__e")
def delete__event(sender, instance, **kwargs):
    """
    Deletes `image` uploaded file when Event is deleted.
    """
    delete_uploaded_file(instance.image.path)


#EOF - artlaasya signals
