"""artlaasya utils """

from django import get_version

import os



def is_django_version_greater_than(major=1, minor=4):
    """
    Returns whether Django version is greater than given major and minor numbers.
    Major and minor should be passed as ints.
    """
    _major, _minor = get_version().split('.')[:2]
    return (int(_major) >= major and int(_minor) > minor)


def delete_uploaded_file(path_of_file_to_delete=None):
    """
    Deletes uploaded file from storage.
    """
    try:
        os.remove(path_of_file_to_delete)
    except OSError:
        pass


#EOF - artlaasya utils