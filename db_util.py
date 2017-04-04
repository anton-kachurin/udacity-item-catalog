class NotAuthenticated(Exception):
    """ Raised in case of 401 error:
        user needs to authenticate themself before performing the operation
    """
    pass

class NotAuthorized(Exception):
    """ Raised in case of 403 error:
        the operation is forbidden for currently authenticated user
    """
    pass

class NotFound(Exception):
    """ Raised in case of 404 error:
        an item couldn't be found
    """
    pass

def latin_lower(s):
    """ Convert string to lower case,
    replace all non-latin or non-digit symbols with dashes,
    deduplicate and trim dashes
    """
    import re

    result = s.lower()
    result = re.sub("[^a-z0-9]", '-', result)
    result = re.sub("-+", '-', result)
    result = re.sub("^-", '', result)
    result = re.sub("-$", '', result)

    return result;
