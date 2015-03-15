#  gLifestream Copyright (C) 2009, 2010, 2012, 2015 Wojciech Polak
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

import re
import os
import requests
from django.conf import settings
from django.utils.six.moves import urllib

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (compatible; gLifestream; +%s/)' %
    settings.BASE_URL
}


class HTTPError(requests.exceptions.RequestException):
    pass


def head(url, timeout=15):
    if not url.startswith('http'):
        url = 'http://' + url
    try:
        return requests.head(url, headers=HEADERS, timeout=timeout)
    except requests.exceptions.RequestException as e:
        raise HTTPError(*e.args)


def get(url, data=None, auth=None, timeout=45):
    if not url.startswith('http'):
        url = 'http://' + url
    try:
        return requests.get(url, params=data, headers=HEADERS, auth=auth,
                            timeout=timeout)
    except requests.exceptions.RequestException as e:
        raise HTTPError(*e.args)


def retrieve(url, filename, timeout=15):
    r = requests.get(url, headers=HEADERS, stream=True, timeout=timeout)
    with open(filename, 'wb') as fp:
        for chunk in r.iter_content(4096):
            fp.write(chunk)
            fp.flush()
            os.fsync(fp.fileno())
    return r


def get_alturl_if_html(r):
    """Return alternate URL (using feed autodiscovery mechanism)
    if urlopen's Content-Type response is HTML."""

    ct = r.headers.get('content-type', '')
    if ';' in ct:
        ct = ct.split(';', 1)[0]
    if ct in ('text/html', 'application/xhtml+xml'):
        shortdata = r.text[:2048]
        for link in re.findall(r'<link(.*?)>', shortdata):
            if 'alternate' in link:
                rx = re.search('type=[\'"](.*?)[\'"]', link)
                if not rx:
                    continue
                alt_type = rx.groups()[0]
                if alt_type in ('application/rss+xml',
                                'application/atom+xml',
                                'application/rdf+xml',
                                'application/xml'):
                    rx = re.search('href=[\'"](.*?)[\'"]', link)
                    if rx:
                        alt_href = rx.groups()[0]
                        return urllib.parse.urljoin(r.url, alt_href)
    return None


def gen_auth(service, url):
    """Generate web authentication."""
    if service.creds and len(service.creds) and service.creds != 'oauth':
        return service.creds.split(':')
    return None
