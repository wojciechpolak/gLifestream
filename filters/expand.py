#  gLifestream Copyright (C) 2009 Wojciech Polak
#
#  This program is free software; you can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published by the
#  Free Software Foundation; either version 3 of the License, or (at your
#  option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along
#  with this program.  If not, see <http://www.gnu.org/licenses/>.

import os.path
import re
import httplib
import urllib
import hashlib
import tempfile
import shutil
from django.conf import settings
from django.utils.html import strip_tags

try:
    import Image
except ImportError:
    Image = None

#
# Short link services
#

def __su_subs (m):
    conn = httplib.HTTPConnection (m.group (1))
    try:
        conn.request ('HEAD', m.group (2))
        response = conn.getresponse ()
        url = response.getheader ('location')
        if url:
            return '%s' % response.getheader ('location')
        else:
            return m.group (0)
    except:
        return m.group (0)

def shorturls (text):
    """Expand short URLs."""
    return re.sub (r'http://(tinyurl.com|bit.ly|url4.eu|is.gd|ur1.ca|2tu.us|ff.im|post.ly|awe.sm|lnk.ms|pic.gd|tl.gd|vid.ly)(/\w+)',
                   __su_subs, text)

#
# Short image services
#

def save_image (url, force=False):
    if settings.BASE_URL in url:
        return url
    newfile = 'thumbs/%s' % hashlib.sha1 (url).hexdigest ()
    newpath = '%s/%s' % (settings.MEDIA_ROOT, newfile)
    if not os.path.isfile (newpath):
        tmp = tempfile.mktemp ('_ls')
        try:
            image = urllib.FancyURLopener ()
            resp = image.retrieve (url, tmp)[1]
            if not force and not 'image/' in resp.getheader ('Content-Type', ''):
                return url
            shutil.move (tmp, newpath)
        except:
            return url
    return newfile

def downscale_image (filename):
    if not Image:
        return
    filename = '%s/%s' % (settings.MEDIA_ROOT, filename)
    size = 400, 175
    try:
        im = Image.open (filename)
        w, h = im.size
        if w > size[0] or h > size[1]:
            im.thumbnail (size, Image.ANTIALIAS)
            im.save (filename, 'JPEG', quality=95)
    except:
        pass

def __sp_twitpic (m):
    url = 'http://%s/show/thumb/%s' % (m.group (2), m.group (3))
    newurl = save_image (url)
    return '<div class="thumbnails"><a href="%s" rel="nofollow"><img src="%s" alt="thumbnail" /></a></div>' % (m.group (0), newurl)

def __sp_yfrog (m):
    url = 'http://%s/%s.th.jpg' % (m.group (1), m.group (2))
    newurl = save_image (url)
    return '<div class="thumbnails"><a href="%s" rel="nofollow"><img src="%s" alt="thumbnail" /></a></div>' % (m.group (0), newurl)

def __sp_imglog (m):
    url = m.group (0)
    newurl = save_image (url)
    return '<div class="thumbnails"><img src="%s" alt="thumbnail" /></div>' % newurl

def shortpics (text):
    """Expand short picture-URLs."""
    text = re.sub (r'http://(www\.)?(twitpic.com)/(\w+)',
                   __sp_twitpic, text)
    return re.sub (r'http://(yfrog.com)/(\w+)',
                   __sp_yfrog, text)

def imgloc (text):
    """Convert image location to html img."""
    text = re.sub (r'https?://[\w\.\-\+/=%~]+\.(jpg|jpeg|png|gif)', __sp_imglog, text)
    return text

#
# Video services
#

def __sv_youtube (m):
    id     = m.group (1)
    rest   = m.group (2)
    ltag   = rest.find ('<') if rest else -1
    rest   = rest[ltag:] if ltag != -1 else ''
    link   = 'http://www.youtube.com/watch?v=%s' % id
    imgurl = 'http://i.ytimg.com/vi/%s/default.jpg' % id
    imgurl = save_image (imgurl)
    return '<table class="vc"><tr><td><div id="youtube-%s" class="play-video"><a href="%s" rel="nofollow"><img src="%s" width="120" height="90" alt="YouTube Video" /></a><div class="playbutton"></div></div></td></tr></table>%s' % (id, link, imgurl, rest)

def __sv_vimeo (m):
    from glifestream.apis import vimeo
    id = m.group (2)
    link = m.group (0)
    imgurl = vimeo.get_thumbnail_url (id)
    if imgurl:
        imgurl = save_image (imgurl)
        return '<table class="vc"><tr><td><div id="vimeo-%s" class="play-video"><a href="%s" rel="nofollow"><img src="%s" width="200" height="150" alt="Vimeo Video" /></a><div class="playbutton"></div></div></td></tr></table>' % (id, link, imgurl)
    else:
        return link

def __sv_ustream (m):
    id = m.group (1)
    link = m.group (0)
    return '<span id="ustream-%s" class="play-video video-inline"><a href="%s" rel="nofollow">%s</a></span>' % (id, link, link)

def __sv_twitvid (m):
    id = m.group (2)
    link = m.group (0)
    return '<span id="twitvid-%s" class="play-video video-inline"><a href="%s" rel="nofollow">%s</a></span>' % (id, link, link)

def __sv_vidly (m):
    id   = m.group (1)
    rest = m.group (2)
    ltag = rest.find ('<') if rest else -1
    rest = rest[ltag:] if ltag != -1 else ''
    link = 'http://vidly.com/%s' % id
    return '<span id="vidly-%s" class="play-video video-inline"><a href="%s" rel="nofollow">%s</a></span>%s' % (id, link, link, rest)

def __sv_dailymotion (m):
    link = strip_tags (m.group (0))
    id   = m.group (1)
    rest = m.group (2)
    ltag = rest.find ('<') if rest else -1
    rest = rest[ltag:] if ltag != -1 else ''
    imgurl = 'http://www.dailymotion.com/thumbnail/160x120/video/%s' % id
    imgurl = save_image (imgurl)
    return '<table class="vc"><tr><td><div id="dailymotion-%s" class="play-video"><a href="%s" rel="nofollow"><img src="%s" width="160" height="120" alt="Dailymotion Video" /></a><div class="playbutton"></div></div></td></tr></table>%s' % (id, link, imgurl, rest)

def __sv_metacafe (m):
    link = strip_tags (m.group (0))
    id   = m.group (2)
    rest = m.group (3)
    ltag = rest.find ('<') if rest else -1
    rest = rest[ltag:] if ltag != -1 else ''
    imgurl = 'http://www.metacafe.com/thumb/%s.jpg' % id
    imgurl = save_image (imgurl)
    return '<table class="vc"><tr><td><div id="metacafe-%s" class="play-video"><a href="%s" rel="nofollow"><img src="%s" width="136" height="81" alt="Metacafe Video" /></a><div class="playbutton"></div></div></td></tr></table>%s' % (id, link, imgurl, rest)

def __sv_googlevideo (m):
    link = strip_tags (m.group (0))
    id   = m.group (1)
    rest = m.group (2)
    ltag = rest.find ('<') if rest else -1
    rest = rest[ltag:] if ltag != -1 else ''
    return '<div id="googlevideo-%s" class="play-video video-inline"><a href="%s" rel="nofollow">Google Video %s</a></div>%s' % (id, link, id, rest)

def videolinks (s):
    """Expand video links."""
    if 'http://www.youtube.com/' in s:
        s = re.sub (r'http://www.youtube.com/watch\?v=([\-\w]+)(\S*)',
                    __sv_youtube, s)
    if 'vimeo.com/' in s:
        s = re.sub (r'http://(www\.)?vimeo.com/(\d+)', __sv_vimeo, s)
    if 'http://www.ustream.tv/recorded/' in s:
        s = re.sub (r'http://www.ustream.tv/recorded/(\d+)', __sv_ustream, s)
    if 'http://www.dailymotion.' in s:
        s = re.sub (r'http://www.dailymotion.[a-z]{2,3}/video/([\-\w]+)_(\S*)',
                    __sv_dailymotion, s)
    if 'http://www.metacafe.com/' in s:
        s = re.sub (r'http://www.metacafe.com/(w|watch)/(\d+)/(\S*)',
                    __sv_metacafe, s)
    if 'twitvid.com/' in s:
        s = re.sub (r'http://(www\.)?twitvid.com/(\w+)', __sv_twitvid, s)
    if 'vidly.com/' in s:
        s = re.sub (r'http://vidly.com/(\w+)(\S*)', __sv_vidly, s)
    if 'http://video.google.com/videoplay?docid=' in s:
        s = re.sub (r'http://video.google.com/videoplay\?docid=(\d+)(\S*)',
                    __sv_googlevideo, s)
    return s

#
# Audio services
#

def __sa_ogg (m):
    link = m.group (1)
    name = m.group (2)
    id = hashlib.md5 (link).hexdigest ()
    return '<span id="audio-%s" class="play-audio"><a href="%s">%s</a></span>' % (id, link, name)

def __sa_thesixtyone (m):
    link     = m.group (0)
    artist   = m.group (1)
    songname = urllib.unquote_plus (m.group (2))
    songid   = m.group (3)
    return '<span id="thesixtyone-%s-%s" class="play-audio"><a href="%s" rel="nofollow">%s</a></span>' % (artist, songid, link, songname)

def __sa_saynow (m):
    link = m.group (0)
    id   = m.group (1)
    return '<span id="saynow-%s" class="play-audio"><a href="%s" rel="nofollow">Say Now</a></span>' % (id, link)

def audiolinks (s):
    """Expand audio links."""
    if '.ogg' in s:
        s = re.sub (r'<a href="(https?://[\w\.\-\+/=%~]+\.ogg)">(.*?)</a>', __sa_ogg, s)
    if 'http://www.thesixtyone.com/' in s:
        # Scheme: http://www.thesixtyone.com/ARTIST/song/SONGNAME/SONGID/
        s = re.sub (r'http://www.thesixtyone.com/(.+)/song/(.+)/(\w+)/', __sa_thesixtyone, s)
    if 'http://www.saynow.com/playMsg.html?ak=' in s:
        s = re.sub (r'http://www.saynow.com/playMsg.html\?ak=(\w+)', __sa_saynow, s)
    return s

#
# Map services
#

from urlparse import urlparse
from cgi import parse_qsl

def __parse_qs (qs, keep_blank_values = 0, strict_parsing = 0):
    dict = {}
    for name, value in parse_qsl (qs, keep_blank_values, strict_parsing):
        dict[name] = value
    return dict

def __sm_googlemaps (m):
    link = strip_tags (m.group (0))
    rest = m.group (2)
    ltag = rest.find ('<') if rest else -1
    rest = rest[ltag:] if ltag != -1 else ''
    params = __parse_qs (urlparse (link).query)
    ll = params.get ('ll', None)
    if ll:
        ll = ll.split (',')
        geolat = float (ll[0])
        geolng = float (ll[1])
        return '<div class="geo"><a href="%s" class="map"><span class="latitude">%.10f</span> <span class="longitude">%.10f</span></a></div>%s' % (link, geolat, geolng, rest)
    else:
        return link

def maplinks (s):
    """Expand map links."""
    if 'http://maps.google.' in s:
        s = re.sub (r'http://maps.google.[a-z]{2,3}/(maps)?(\S*)',
                    __sm_googlemaps, s)
    return s

#
# Summary
#

def shorts (s):
    s = shortpics (s)
    return shorturls (s)

def all (s):
    s = shortpics (s)
    s = shorturls (s)
    s = audiolinks (s)
    s = videolinks (s)
    s = maplinks (s)
    return s
