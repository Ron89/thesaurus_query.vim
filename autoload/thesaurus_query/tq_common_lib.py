# Supportive Python library for thesaurus_query.vim. 
#
# Author:       HE Chong [[chong.he.1989@gmail.com][E-mail]]

import sys
import urllib
try:
    import vim
    independent_session = False
except ImportError:
    independent_session = True



if sys.version_info < (3,0):
    import urlparse
    urlpquote = urllib.quote
    urlpunquote = urllib.unquote
    urlpurlsplit = urlparse.urlsplit
    urlpurlunsplit = urlparse.urlunsplit
else:
    import urllib.parse as urlparse
    urlpquote = urlparse.quote
    urlpunquote = urlparse.unquote
    urlpurlsplit = urlparse.urlsplit
    urlpurlunsplit = urlparse.urlunsplit

def decode_utf_8(string_in):
    ''' safely decode string into unicode string '''
    if sys.version_info < (3,0):
        return string_in.decode('utf-8') if not isinstance(string_in, unicode) else string_in
    return string_in.decode('utf-8') if not isinstance(string_in, str) else string_in

def encode_utf_8(string_in):
    ''' safely encode unicode string to string '''
    if sys.version_info < (3,0):
        return string_in.encode('utf-8') if isinstance(string_in, unicode) else string_in
    return string_in.encode('utf-8') if isinstance(string_in, str) else string_in

def send_string_to_vim(string_in):
    ''' return properly coded result
    Vim in default mac OS with python 2.* only receive encoded utf-8 string
    properly. Vim with python 3.* only receive decoded utf-8 string properly.
    Vim with python 2.* on Linux seemed to handle both well. Hence the
    function.
    '''
    if sys.version_info > (3,0):
        return decode_utf_8(string_in)
    return encode_utf_8(string_in)

def fixurl(url):
    ''' translate string into url compatible ascii string
    return:
        url-compatible_ascii_string
    code by Markus Jarderot
    '''
    url = decode_utf_8(url)

    # parse it
    parsed = urlpurlsplit(url)

    # divide the netloc further
    userpass,at,hostport = parsed.netloc.rpartition('@')
    user,colon1,pass_ = userpass.partition(':')
    host,colon2,port = hostport.partition(':')

    # encode each component
    scheme = parsed.scheme.encode('utf8')
    user = encode_utf_8(urlpquote(user.encode('utf8')))
    colon1 = colon1.encode('utf8')
    pass_ = encode_utf_8(urlpquote(pass_.encode('utf8')))
    at = at.encode('utf8')
    host = host.encode('idna')
    colon2 = colon2.encode('utf8')
    port = port.encode('utf8')
    if sys.version_info < (3,0):
        path = '/'.join(  # could be encoded slashes!
            urlpquote(urlpunquote(pce).encode('utf8'),'')
            for pce in parsed.path.split('/')
        )
    else:
        path = b'/'.join(  # could be encoded slashes!
            encode_utf_8(urlpquote(urlpunquote(pce).encode('utf8'),b''))
            for pce in parsed.path.split('/')
        )
    query = encode_utf_8(urlpquote(urlpunquote(parsed.query).encode('utf8'),'=&?/'))
    fragment = encode_utf_8(urlpquote(urlpunquote(parsed.fragment).encode('utf8')))

    # put it back together
    if sys.version_info < (3,0):
        netloc = ''.join((user,colon1,pass_,at,host,colon2,port))
    else:
        netloc = b''.join((user,colon1,pass_,at,host,colon2,port))
    return urlparse.urlunsplit((scheme,netloc,path,query,fragment))

def get_variable(v_name, default=None):
    ''' get variable from Vim
    return:
        vim_variable  # buffer variable tried first, global variable second
        default       # if no variable exists, or module used independently
                      # from Vim session.
    '''
    if independent_session:
        return default
    if vim.eval("exists('b:'.'{0}')".format(v_name))=='0':
        if vim.eval("exists('g:'.'{0}')".format(v_name))=='0':
            if vim.eval("exists('{0}')".format(v_name))=='0':
                return default
            else:
                return vim.eval(v_name)
        else:
            return vim.eval('g:'+v_name)
    else:
        return vim.eval('b:'+v_name)

def vim_command(command):
    """ wrapper for Vim command, do nothing if session is Vim independent """
    if independent_session:
        return None
    vim.command(command)

def vim_eval(command):
    """ wrapper for Vim eval, return None if session is Vim independent """
    if independent_session:
        return None
    return vim.eval(command)
