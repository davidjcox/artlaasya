"""artlaasya views"""

from django.shortcuts import get_object_or_404, get_list_or_404, render_to_response
from django.core.context_processors import csrf
from django.template import RequestContext
from django.views.generic import TemplateView
from django.contrib.sitemaps import Sitemap
from django.conf import settings
from django.db.models import Q

import re
import os.path
import operator
from random import shuffle

from artlaasya.models import Artist, Genre, Artwork, Event



class BaseSitemap(Sitemap):
    """
    Base class for other Sitemap classes.
    """
    changefreq = "weekly"
 
    def location(self, obj):
        return obj.get_absolute_url()
 
    def lastmod(self, obj):
        return obj.updated or obj.created
# /BaseSitemap


class StaticSitemap(Sitemap):
    """
    Sitemap class for static pages.
    """
    priority = 0.5
    changefreq = "never"
    lastmod = None
 

    def items(self):
        return ["/contact", 
                "/termsofuse", 
                "/privacy", 
                "/termsofsale", ]
 
    def location(self, obj):
        return obj
# /StaticSitemap


class ArtistSitemap(BaseSitemap):
    """
    Sitemap for Artists.
    """
    priority = 0.75
 
    def items(self):
        return Artist.artists.active()
# /ArtistSitemap


class ArtworkSitemap(BaseSitemap):
    """
    Sitemap for Artworks.
    """
    priority = 1.0
 
    def items(self):
        return Artwork.artworks.active()
# /ArtworkSitemap


class EventSitemap(BaseSitemap):
    """
    Sitemap for Events.
    """
    def items(self):
        return Event.events.active()
# /EventSitemap


def normalize_query(query_string,
                    findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)] 
# /normalize_query


def get_query(query_string, search_fields):
    """
    Compound query compiler.
    """
    query = None # Query to search for every search term        
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
    return query
# /get_query


def merge_lists(list1, list2):
    """
    Alternative list merge function to `zip_longest()`.  It does not extend 
    shorter list with values unlike `zip_longest()` which extends with `None`.
    """
    num = min(len(list1), len(list2))
    result = [None]*(num*2)
    result[::2] = list1[:num]
    result[1::2] = list2[:num]
    result.extend(list1[num:])
    result.extend(list2[num:])
    return result
# /merge_lists


#===============================================================================

def home(request):
    """
    Returns all artworks that are representative for each artist and that are 
    active.
    Only one artwork can be representative per artist.
    """
    _artworks = get_list_or_404(Artwork.artworks.representative().active())
    
    return render_to_response('t_home.html', 
                              {'artworks': _artworks}, 
                              context_instance=RequestContext(request))
# /home


def artist(request, artist_name=None):
    """
    Returns an artist and all active artworks for that artist.
    """
    _artist = get_object_or_404(Artist.artists.active(), slug=artist_name)
    _artworks = get_list_or_404(Artwork.artworks.active(), artist=_artist)
    
    return render_to_response('t_artist.html', 
                              {'artist': _artist, 
                               'artworks': _artworks}, 
                              context_instance=RequestContext(request))
# /artist


def artists(request, artist_genre=None):
    """
    Returns either only new, only contemporary, only traditional, or all 
    artworks that are representative for each artist and that are active.
    
    New artists are those added since the interval of time defined in the 
    `recent` queryset of the `ArtistManager` manager.
    """
    if (artist_genre == 'new'):
        _artworks = get_list_or_404(Artwork.artworks.recent(
                                                   ).representative(
                                                   ).active(
                                                   ).orderly(),
                                                   artist__is_active=True)
    elif (artist_genre == 'all'):
        _artworks = get_list_or_404(Artwork.artworks.representative(
                                                   ).active(
                                                   ).orderly(),
                                                   artist__is_active=True)
    elif (artist_genre == 'contemporary'):
        _artworks = get_list_or_404(Artwork.artworks.contemporary(
                                                   ).representative(
                                                   ).active(
                                                   ).orderly(),
                                                   artist__is_active=True)
    elif (artist_genre == 'traditional'):
        _artworks = get_list_or_404(Artwork.artworks.traditional(
                                                   ).representative(
                                                   ).active(
                                                   ).orderly(),
                                                   artist__is_active=True)
    
    return render_to_response('t_artists.html', 
                              {'artworks': _artworks}, 
                              context_instance=RequestContext(request))
# /artists


def artwork(request, artist_name=None, artwork_title=None):
    """
    Returns the specified artwork for the specified artist and all additional 
    artworks by that artist that are active.
    """
    _selected_artwork = get_object_or_404(Artwork.artworks.active(), 
                                          slug=artwork_title)
    
    _other_artworks = Artwork.artworks.filter(artist__slug=artist_name).exclude(
                                              slug=artwork_title).active()
    
    return render_to_response('t_artwork.html', 
                              {'other_artworks': _other_artworks,
                               'selected_artwork': _selected_artwork}, 
                              context_instance=RequestContext(request))
# /artwork


def artworks(request, artwork_genre=None):
    """
    Returns either only new, only contemporary, only traditional, or all 
    artworks for each artist that are active.
    
    New artists are those added since the interval of time defined in the 
    `recent` queryset of the `ArtworkManager` manager.
    
    Requirements dictated that artists within a genre must be ordered randomly 
    to ensure equal promotion placement for each artist over page views.
    
    Requirements dictated that when all artwork genres are listed, the genres 
    must be interleaved into a listing order that alternates between
    "contemporary" and "traditional" artworks.
    
    Since requirements dictated that art genre could only be linked to artwork, 
    and not artist, two queries are needed instead of one for artists with a 
    `select_related()`.  The first to locate all artists of a particular genre, 
    and the second to retrieve all artworks for each artist.
    
    Artists are retrieved per genre, then shuffled, then merged if all or new, 
    and finally artworks are retrieved for the artists.
    
    It is slower than the more straightforward solution of linking genre to 
    artist too, but is compliant with requirements...
    """
    if (artwork_genre == 'new'):
        #Find any NEW contemporary artists.
        _contemporary_new = list(Artwork.artworks.contemporary(
                                                ).recent(
                                                ).active(
                                                ).orderly(
                                                ).distinctly(
                                                ).values_list('artist__slug',
                                                              flat=True))
        #Find any NEW traditional artists.
        _traditional_new = list(Artwork.artworks.traditional(
                                               ).recent(
                                               ).active(
                                               ).orderly(
                                               ).distinctly(
                                               ).values_list('artist__slug',
                                                             flat=True))
        #Shuffle the lists.
        shuffle(_contemporary_new)
        shuffle(_traditional_new)
        
        #Merge the two lists together in alternating order.
        _alternating_new = merge_lists(_contemporary_new, _traditional_new)
        
        #Gather all artworks for each artist.
        _artworks = []
        for _artist in _alternating_new:
            _artworks.extend(Artwork.artworks.filter(artist__slug=_artist))
    else:
        #Find ALL contemporary artists.
        _contemporary_all = list(Artwork.artworks.contemporary(
                                                ).active(
                                                ).orderly(
                                                ).distinctly(
                                                ).values_list('artist__slug',
                                                              flat=True))
        #Find ALL traditional artists.
        _traditional_all = list(Artwork.artworks.traditional(
                                               ).active(
                                               ).orderly(
                                               ).distinctly(
                                               ).values_list('artist__slug',
                                                             flat=True))
        #Shuffle the lists.
        shuffle(_contemporary_all)
        shuffle(_traditional_all)
        
        if (artwork_genre == 'all'):
            #If ALL, merge the two shuffled lists together in alternating order.
            _alternating_all = merge_lists(_contemporary_all, _traditional_all)
            
            #Gather all artworks for each artist.
            _artworks = []
            for _artist in _alternating_all:
                _artworks.extend(Artwork.artworks.filter(artist__slug=_artist))
        elif (artwork_genre == 'contemporary'):
            #If ONLY contemporary, gather only the contemporary artworks.
            _artworks = []
            for _artist in _contemporary_all:
                _artworks.extend(Artwork.artworks.filter(artist__slug=_artist))
        elif (artwork_genre == 'traditional'):
            #If ONLY traditional, gather only the traditional artworks.
            _artworks = []
            for _artist in _traditional_all:
                _artworks.extend(Artwork.artworks.filter(artist__slug=_artist))
    
    return render_to_response('t_artworks.html', 
                              {'artworks': _artworks}, 
                              context_instance=RequestContext(request))
# /artworks


def learn(request, artwork_genre=None):
    """
    Returns an art genre.
    """
    _genre = get_object_or_404(Genre, slug=artwork_genre)
    
    return render_to_response('t_learn.html', 
                              {'genre': _genre}, 
                              context_instance=RequestContext(request))
# /learn


def event(request, event_title=None):
    """
    Returns an active event.
    """
    _event = get_object_or_404(Event.events.active(), slug=event_title)
    
    return render_to_response('t_event.html', 
                              {'event': _event}, 
                              context_instance=RequestContext(request))
#end event


def events(request):
    """
    Returns all active events.
    """
    _events = get_list_or_404(Event.events.active())
    
    return render_to_response('t_events.html', 
                              {'events': _events}, 
                              context_instance=RequestContext(request))
#end events


class search(TemplateView):
    """
    Returns a simple search template.
    """
    template_name = "search.html"
# /search


def searching(request):
    """
    Simple search function.
    """
    query_string = ''
    artworks_found = None
    artists_found = None
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']
        
        artwork_query = get_query(query_string, ['title',
                                                 'genre__name',
                                                 'medium_description',
                                                 'description',])
        
        artworks_found = Artwork.artworks.filter(artwork_query).active().orderly()
        
        artist_query = get_query(query_string, ['first_name', 
                                                'last_name',])
        
        artists_found = Artist.artists.filter(artist_query).active().orderly()
    
    return render_to_response('t_search_results.html', 
                              {'query_string': query_string, 
                               'artworks_found': artworks_found, 
                               'artists_found': artists_found}, 
                              context_instance=RequestContext(request))
# /searching


#EOF - artlaasya views

