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

try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    BeautifulSoup = None

def strip_script (s):
    try:
        if BeautifulSoup:
            soup = BeautifulSoup (s)
            to_extract = soup.findAll ('script')
            for item in to_extract:
                item.extract ()
            s = str (soup)
    except:
        pass
    return s
