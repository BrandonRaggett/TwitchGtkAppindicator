import os
import signal
import json
import webbrowser

from urllib2 import Request, urlopen, URLError

from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator
from gi.repository import GLib as glib

"""
TODO
Display a notification when a new streamer goes online
Find out why self.build_menu keeps getting called and spamming output
"""

APPINDICATOR_ID = 'indicator'

class TwitchIndicator:


    def __init__(self):

        self.timer = None #Used for glib timing
        self.indicator = appindicator.Indicator.new(APPINDICATOR_ID, gtk.STOCK_EDIT, appindicator.IndicatorCategory.SYSTEM_SERVICES)
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.get_online()

        gtk.main()


    def load_file(self, *data):
        try:
            if len(os.path.dirname(__file__))>2:
                path_to_open = os.path.dirname(__file__)+'/streamers.txt'
            else:
                path_to_open = 'streamers.txt'

            f = open(path_to_open, 'r')
            self.channels = f.readline()
            f.close()
        except Exception as e:
            print e


    def build_menu(self, online_channels):
        # print " -- BUILDING MENU -- "
        menu = gtk.Menu()

        if len(online_channels) > 0:
            for channel in range(len(online_channels)):
                name = str(online_channels[channel]['channel']['display_name']) + \
                    '  ' + str(online_channels[channel]['viewers'])
                c = gtk.MenuItem(name)
                c.connect('activate', self.open_browser, online_channels[channel]['channel']['url'])
                menu.append(c)

        item_sep = gtk.SeparatorMenuItem()
        menu.append(item_sep)

        item_reload = gtk.MenuItem('Reload Streamers')
        item_reload.connect('activate', self.get_online)
        menu.append(item_reload)

        item_quit = gtk.MenuItem('Quit')
        item_quit.connect('activate', self.quit)
        menu.append(item_quit)

        menu.show_all()
        return menu

    def open_browser(self, *data):
        # print '\nOpening in browser:\n', data[1], '\n'
        webbrowser.open(data[1])

    def get_online(self, *data):
        # print " -- REFRESHING CURRENTLY LIVE STREAMS -- "
        if self.timer is not None:
            glib.source_remove(self.timer)

        self.load_file()

        request = Request('https://api.twitch.tv/kraken/streams?channel='+self.channels)
        response = urlopen(request)

        online_channels = json.loads(response.read())['streams']

        self.indicator.set_menu(self.build_menu(online_channels))

        self.timer = glib.timeout_add_seconds(30, self.get_online)

    def quit(self):
        gtk.main_quit()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    a = TwitchIndicator()
