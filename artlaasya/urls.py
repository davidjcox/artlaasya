"""artlaasya urls"""

from django.conf.urls import patterns, url, include
from django.contrib import admin
from django.conf import settings

from artlaasya import views



admin.autodiscover()

# Dynamic page URL patterns.
urlpatterns = patterns('', 
  url(r'^$', views.home, name="v_home"), 
  url(r'^artist/(?P<artist_name>\b[a-z0-9\-]+\b)',
      views.artist,
      name="v_artist"), 
  url(r'^artists/(?P<artist_genre>\b[a-z\-]+\b)',
      views.artists,
      name="v_artists-genre"), 
  url(r'^artwork/(?P<artist_name>\b[a-z0-9\-]+\b)/(?P<artwork_title>\b[a-z0-9\-\'\(\.\)\!\?]+\b)',
      views.artwork,
      name="v_artwork"), 
  url(r'^artworks/(?P<artwork_genre>\b[a-z\-]+\b)',
      views.artworks,
      name="v_artworks-genre"), 
  url(r'^event/(?P<event_title>\b[a-z0-9\-\'\(\)\!\?]+\b)',
      views.event,
      name="v_event"), 
  url(r'^events/$',
      views.events,
      name="v_events"), 
  url(r'^learn/(?P<artwork_genre>\b[a-z\-]+\b)',
      views.learn,
      name="v_learn"), 
  url(r'^search/',
      views.search.as_view(),
      name="search"), 
  url(r'^searching/$',
      views.searching,
      name="v_searching"), 
)

# Static page URL patterns. 
urlpatterns += patterns('django.contrib.flatpages.views',
  url(r'^contact/$',
      'flatpage',
      {'url': '/contact/'},
      name='contact'), 
  url(r'^termsofuse/$',
      'flatpage',
      {'url': '/termsofuse/'},
      name='termsofuse'), 
  url(r'^privacy/$',
      'flatpage',
      {'url': '/privacy/'},
      name='privacy'), 
  url(r'^termsofsale/$',
      'flatpage',
      {'url': '/termsofsale/'},
      name='termsofsale'), 
)

# Sitemap tuple compiler.
sitemaps = (
                {
                 '_static': views.StaticSitemap,
                 '_artists': views.ArtistSitemap,
                 '_artworks': views.ArtworkSitemap,
                 '_events': views.EventSitemap,
                }
)

# Sitemap and admin page URL patterns.
urlpatterns += patterns('', 
    url(r'^admin/',
        include(admin.site.urls)), 
    url(r'^sitemap\.xml$',
        'django.contrib.sitemaps.views.sitemap',
        {'sitemaps': sitemaps},
        name='sitemap'), 
)

# Debug toolbar URL patterns.
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )

    
#EOF - artlaasya urls