#  gLifestream Copyright (C) 2009, 2010 Wojciech Polak
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

from django.conf import settings
from django.shortcuts import render_to_response
from glifestream.stream.models import Service

def js (request, **args):
    page = {
        'base_url': settings.BASE_URL,
    }
    if request.is_secure ():
        page['base_url'] = page['base_url'].replace ('http://', 'https://')

    return render_to_response ('bookmarklet.js', { 'page': page },
                               mimetype='application/javascript')

def frame (request, **args):
    page = {
        'base_url': settings.BASE_URL,
    }
    if request.is_secure ():
        page['base_url'] = page['base_url'].replace ('http://', 'https://')

    authed = request.user.is_authenticated () and request.user.is_staff
    if authed:
        srvs = Service.objects.filter (api='selfposts').order_by ('cls')
        srvs.query.group_by = ['cls']
        srvs = srvs.values ('id', 'cls')
    else:
        srvs = None

    return render_to_response ('frame.html',
                               { 'authed': authed,
                                 'page': page,
                                 'is_secure': request.is_secure (),
                                 'srvs': srvs })
