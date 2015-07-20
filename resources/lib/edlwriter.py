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

import xbmcgui, xbmc

from resources.lib.notifications import notify, yesno


# Set to True if you want to be able to adjust marker time
# Warning: this is experimental (i.e. not working well!)
ADVANCED_MODE = True

# Define types of marker
# This isn't implemented yet...
EDL_CUT = 0
EDL_MUTE = 1
EDL_SCENE_MARKER = 2
EDL_COMMERCIAL_BREAK = 3

# Define how big we want our steps to be if using Advanced Mode (in seconds)
SMALL_STEP = 100
BIG_STEP = 60000

# Constants for Advanced Mode menu
BIG_STEP_BACK = 0
SMALL_STEP_BACK = 1
SMALL_STEP_FORWARD = 2
BIG_STEP_FORWARD = 3
DONE = 4

Select = xbmcgui.Dialog().select

MENU_LIST = [(BIG_STEP_BACK, "Big step back"),
             (SMALL_STEP_BACK, "Small step back"),
             (SMALL_STEP_FORWARD, "Small step forward"),
             (BIG_STEP_FORWARD, "Big step forward"),
             (DONE, "Done")]

class EDLWriter(object):
    def __init__(self, default = EDL_COMMERCIAL_BREAK):
        self.videoname = None
        self.is_open = False
        self.edllist = []
        self.current = {}
        self.default = default

    def SetVideoName(self, vname):
        self.videoname = vname

    def AddPoint(self, marktime, player, marktype = None):
        edltype = marktype if marktype else self.default
        self.player = player
        update = True

        # Check if this the first marker
        if not self.is_open and not self.edllist:
            first = yesno("This is your first marker. "
                          "Do you want to create a marker from the beginning of"
                          " the video to here?")
            if first:
                self.current["start"] = 0
                self.is_open = True

        # If using advanced mode then we call the necessary function
        if ADVANCED_MODE:
            update, marktime = self.adjustTime(marktime)

        # If we want to add the marker...
        if update:

            if self.is_open:
                self.current["end"] = self.player.toMillis(marktime) / 1000.0
                self.current["type"] = edltype
                self.edllist.append(self.current)
                notify("New markers added.")
                self.current = {}
                self.is_open = False

            else:
                self.current["start"] = self.player.toMillis(marktime) / 1000.0
                notify("Starting marker added.")
                self.is_open = True

    def adjustTime(self, adjustTime):

        finished = False
        update = False
        seektime = adjustTime

        while not finished:
            seek = False

            action = Select("EDL Writer", [x[1] for x in MENU_LIST])

            selected = MENU_LIST[action][0]

            if selected == BIG_STEP_BACK:
                seektime = self.player.calcTime(seektime, BIG_STEP, True)
                seek = True

            elif selected == SMALL_STEP_BACK:
                seektime = self.player.calcTime(seektime, SMALL_STEP, True)
                seek = True

            elif selected == SMALL_STEP_FORWARD:
                seektime = self.player.calcTime(seektime, SMALL_STEP)
                seek = True

            elif selected == BIG_STEP_FORWARD:
                seektime = self.player.calcTime(seektime, BIG_STEP)
                seek = True

            elif selected == DONE:
                finished = True
                update = True

            else:
                finished = True

            # User wants to adjust time
            if seek:
                # THIS IS THE BIT THAT DOESN'T WORK
                # WE NEED TO MOVE TO THE NEW "SEEKTIME" BUT USER NEEDS TO SEE
                # THE SCREEN.
                # CURRENT ATTEMPT TRIES TO JUMP TO 1 SECOND BEFORE ADJUSTED TIME
                # AND THEN PAUSE...
                # ...DOESN'T WORK.
                self.player.seekVideoTime(seektime)

        return update, seektime

    def Finish(self):
        with open("{0}.edl".format(self.videoname), "w") as edl:
            for scene in self.edllist:
                edl.write("{start:.3f}\t{end:.3f}\t{type}\n".format(**scene))
            edl.write("# File generated by script.edl.creator addon for Kodi.")
        notify("EDL file written successfully!")
