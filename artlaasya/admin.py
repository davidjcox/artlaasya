"""artlaasya admin"""

from django.contrib import admin

from .models import Artist, Genre, Artwork, Event



class ArtistAdmin(admin.ModelAdmin):
    ordering = ('last_name', 'first_name',)
    search_fields = ('last_name', 'first_name',)
    list_display = ('last_name', 'first_name', 'is_active',)
    list_filter = ('is_active',)
    fieldsets = (
        ('Personal', {
            'fields': (('is_active'), ('first_name', 'last_name'),)
        }),
        ('Biographical', 
            {'fields': ('biography', 'description',)
        }),
        (None, {
            'fields': (('slug', 'created', 'updated'),)
        }),
    )
    readonly_fields = ('slug', 'created', 'updated',)
# /ArtistAdmin

admin.site.register(Artist, ArtistAdmin)


class GenreAdmin(admin.ModelAdmin):
    ordering = ('name',)
    search_fields = ('name',)
    list_display = ('name', 'is_active',)
    list_filter = ('is_active',)
    fieldsets = (
        ('Identity', {
            'fields': (('is_active', 'name', 'location'), 'description',)
        }),
        (None, {
            'fields': ('slug',)
        }),
    )
    readonly_fields = ('slug',)
# /GenreAdmin

admin.site.register(Genre, GenreAdmin)


class ArtworkAdmin(admin.ModelAdmin):
    ordering = ('name',)
    search_fields = ('title', 'artist__last_name', 'artist__first_name', 
                     'inventory_name', 'internal_name',)
    list_display = ('title', 'artist', 'is_representative', 'is_active',)
    list_filter = ('artist', 'is_representative', 'is_active',)
    fieldsets = (
        ('Identity', {
            'fields': (('is_active'), ('title', 'name',), 
                       ('inventory_name', 'internal_name'), 
                       ('artist', 'year', 'is_representative'),)
        }),
        ('Physical Attributes', {
            'fields': (('image_height', 'image_width', 'measurement_units'), 
                       ('height_metric', 'width_metric', 'metric_units'), 
                       ('height_imperial', 'width_imperial', 'imperial_units'), 
                       ('genre', 'medium_description', 'style_class'), 
                       'description',)
        }),
        ('Acquisition', {
            'fields': (('price', 'status'), ('is_price_displayed'), 
                       'alternative_pricing_message',)
        }),
        ('Image Upload', {
            'fields': (('uploaded_image', 'create_deepzoom'),)
        }),
        (None, {
            'fields': (('slug', 'created', 'updated'),)
        }),
    )
    readonly_fields = ('name', 'height_metric', 'width_metric', 
                       'metric_units', 'height_imperial', 'width_imperial', 
                       'imperial_units', 'slug', 'created', 'updated',)
# /ArtworkAdmin

admin.site.register(Artwork, ArtworkAdmin)


class EventAdmin(admin.ModelAdmin):
    ordering = ('-created',)
    search_fields = ('title', 'start_date',)
    list_display = ('title', 'start_date', 'is_admission', 'is_active',)
    list_filter = ('is_admission', 'is_active',)
    fieldsets = (
        ('Identity', {
            'fields': (('is_active'), ('title', 'image'),)
        }),
        ('Admissions', {
            'fields': (('total_seats', 'is_admission', 'admission_price'),)
        }),
        ('Details', {
            'fields': ('type', ('start_date', 'end_date'), 'location', 
            'details',)
        }),
        (None, {
            'fields': (('slug', 'created', 'updated'),)
        }),
    )
    readonly_fields = ('slug', 'created', 'updated',)
# /EventAdmin

admin.site.register(Event, EventAdmin)


#EOF - artlaasya admin