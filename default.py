'''
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.
'''

'''
    EDL Creator for Kodi
    by elParaguayo

    Create EDL files while watching a video.
'''

import simplejson as json
from os.path import splitext, basename

from resources.lib.notifications import notify
from resources.lib.edlwriter import EDLWriter

import xbmc
import xbmcaddon
import xbmcgui

class EDLPlayer(xbmc.Player):

    def __init__( self, *args, **kwargs ):
        self.writer = writer
        self.is_active = True
        self.is_marking = False

    def onPlayBackPaused(self):
        # We should only be trying to add a marker when pause is pressed by the
        # user, and not when the script adjusts the position of the video
        if not self.is_marking:
            # We've started marking, so disable future events until we've
            # finished
            self.is_marking = True
            self.addPoint(self.getTime())

    def onPlayBackResumed(self):
        pass

    def onPlayBackStarted(self):
        try:
            vname = splitext(basename(self.getPlayingFile()))[0]
            self.writer.SetVideoName(vname)
        except:
            self.writer.SetVideoName("CHANGE_ME")

    def onPlayBackEnded(self):
        self.is_active = False
        self.Finish()

    def onPlayBackStopped(self):
        self.is_active = False
        self.Finish()

    def Finish(self):
        self.writer.Finish()

    def sleep(self, s):
        xbmc.sleep(s)

    def addPoint(self, marktime):
        self.writer.AddPoint(marktime, self)
        # If we're here, we should have added a marker so we can re-enable
        # event handling
        self.is_marking = False

writer = EDLWriter()
player = EDLPlayer(xbmc.PLAYER_CORE_DVDPLAYER, writer=writer)

notify("Script started.")

while player.is_active:
    xbmc.sleep(1000)

notify("EDL script stopped.")
