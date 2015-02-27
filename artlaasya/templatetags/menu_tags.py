"""artlaasya menu_tags"""

from django import template

from artlaasya.models import Artist, Artwork, Genre


register = template.Library()


@register.assignment_tag
def get_genres_menu():
    '''
    Retrieves 'name', and 'slug' of Traditional genres.
    '''
    return Genre.genres.traditional(
                      ).values_list('name',
                                    'slug')
#end get_genres_menu


@register.assignment_tag(takes_context=True)
def get_sidebar_NEW_menu(context):
    ''' 
    Retrieves 'first_name', 'last_name', and 'slug' of Artists 
    categorized as NEW.
    '''
    return Artist.artists.recent(
                        ).active(
                        ).values('slug',
                                 'first_name',
                                 'last_name')
#end get_sidebar_NEW_menu


@register.assignment_tag
def get_sidebar_CONT_menu():
    ''' 
    Retrieves 'first_name', 'last_name', and 'slug' of Artists 
    categorized as CONTEMPORARY.
    '''
    return Artwork.artworks.contemporary(
                          ).orderly(
                          ).distinct(
                          ).active(
                          ).values('artist__slug',
                                   'artist__first_name',
                                   'artist__last_name')
#end get_sidebar_CONT_menu


@register.assignment_tag
def get_sidebar_TRAD_menu():
    '''
    Retrieves 'first_name', 'last_name', and 'slug' of Artists 
    categorized as TRADITIONAL.
    '''
    _genres_TRAD = Genre.genres.traditional(
                              ).values_list('name',
                                            'slug')
    _artists_TRAD = []
    for _genre_TRAD in _genres_TRAD:
        _artists_TRAD.append(Artwork.artworks.filter(genre__name=_genre_TRAD[0]
                                            ).orderly(
                                            ).distinctly(
                                            ).active(
                                            ).values('artist__slug',
                                                     'artist__first_name',
                                                     'artist__last_name'))
    return list(zip(_genres_TRAD, _artists_TRAD))
#end get_sidebar_TRAD_menu


@register.assignment_tag
def get_sidebar_ALL_menu():
    '''
    Retrieves 'first_name', 'last_name', and 'slug' of Artists categorized as ALL.
    '''
    return Artist.artists.active(
                        ).values('slug',
                                 'first_name',
                                 'last_name')
#end get_sidebar_ALL_menu


#EOF - menu_tags