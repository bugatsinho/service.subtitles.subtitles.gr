# -*- coding: utf-8 -*-

'''
    Subtitles.gr
    Author Twilight0

        License summary below, for more details please read license.txt file

        This program is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 2 of the License, or
        (at your option) any later version.
        This program is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.
        You should have received a copy of the GNU General Public License
        along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

from xbmc import getCleanMovieTitle

import urllib, re, os

import subtitlesgr
import xsubstv
import subzxyz

from resources.lib import syshandle, sysaddon,langs

from tulip import control, workers


class Search:

    def __init__(self):

        self.list = []

    def run(self, query=None):

        if not 'Greek' in str(langs).split(','):
            control.directory(syshandle)
            control.infoDialog(control.lang(32002).encode('utf-8'))
            return

        if query is None:

            title = control.infoLabel('VideoPlayer.Title')

            if re.search(r'[^\x00-\x7F]+', title) is not None:
                title = control.infoLabel('VideoPlayer.OriginalTitle')

            year = control.infoLabel('VideoPlayer.Year')

            tvshowtitle = control.infoLabel('VideoPlayer.TVshowtitle')

            season = control.infoLabel('VideoPlayer.Season')

            episode = control.infoLabel('VideoPlayer.Episode')

            if 's' in episode.lower():
                season, episode = '0', episode[-1:]

            if not tvshowtitle == '':  # episode
                query = '%s S%02dE%02d' % (tvshowtitle, int(season), int(episode))
            elif not year == '':  # movie
                query = '%s (%s)' % (title, year)
            else:  # file
                query, year = getCleanMovieTitle(title)
                if not year == '': query = '%s (%s)' % (query, year)

        self.query = query

        threads = []

        threads.append(workers.Thread(self.xsubstv))
        threads.append(workers.Thread(self.subzxyz))
        threads.append(workers.Thread(self.subtitlesgr))

        [i.start() for i in threads]

        for i in range(0, 10 * 2):
            try:
                is_alive = [x.is_alive() for x in threads]
                if all(x == False for x in is_alive):
                    break
                if control.aborted is True:
                    break
                control.sleep(500)
            except:
                pass

        if len(self.list) == 0:
            control.directory(syshandle)
            return

        f = []

        f += [i for i in self.list if i['source'] == 'xsubstv']
        f += [i for i in self.list if i['source'] == 'subzxyz']
        f += [i for i in self.list if i['source'] == 'subtitlesgr']

        self.list = f

        for i in self.list:

            try:
                if i['source'] == 'subzxyz':
                    i['name'] = '[subzxyz] %s' % i['name']
                elif i['source'] == 'xsubstv':
                    i['name'] = '[xsubstv] %s' % i['name']
            except:
                pass

        for i in self.list:

            try:
                name, url, source, rating = i['name'], i['url'], i['source'], i['rating']

                u = {'action': 'download', 'url': url, 'source': source}
                u = '%s?%s' % (sysaddon, urllib.urlencode(u))

                item = control.item(label='Greek', label2=name, iconImage=str(rating), thumbnailImage='el')
                item.setProperty('sync', 'false')
                item.setProperty('hearing_imp', 'false')

                control.addItem(handle=syshandle, url=u, listitem=item, isFolder=False)
            except:
                pass

        control.directory(syshandle)

    def subtitlesgr(self):
        self.list.extend(subtitlesgr.subtitlesgr().get(self.query))

    def xsubstv(self):
        self.list.extend(xsubstv.xsubstv().get(self.query))

    def subzxyz(self):
        self.list.extend(subzxyz.subzxyz().get(self.query))


class Download:

    def __init__(self):

        pass

    def run(self, url, source):

        path = os.path.join(control.dataPath, 'temp')
        path = path.decode('utf-8')

        control.deleteDir(os.path.join(path, ''), force=True)

        control.makeFile(control.dataPath)

        control.makeFile(path)

        if source == 'subtitlesgr':

            subtitle = subtitlesgr.subtitlesgr().download(path, url)

        elif source == 'xsubstv':

            subtitle = xsubstv.xsubstv().download(path, url)

        elif source == 'subzxyz':

            subtitle = subzxyz.subzxyz().download(path, url)

        elif source == 'tvsubtitlesgr':

            subtitle = None

        else:

            subtitle = None

        if subtitle is not None:
            item = control.item(label=subtitle)
            control.addItem(handle=syshandle, url=subtitle, listitem=item, isFolder=False)

        control.directory(syshandle)
