# -*- coding: utf-8 -*-
# Copyright 2004-2006 Joe Wreschnig, Michael Urman, Iñigo Serna
#           2012 Christoph Reiter
#           2013 Nick Boultbee
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation

from quodlibet import app
from quodlibet.plugins.events import EventPlugin
from quodlibet.qltk import is_wayland
from quodlibet.qltk.window import Window
from quodlibet.util import is_unity, is_osx, is_kde, print_exc

from .prefs import Preferences
from .util import pconfig
from .systemtray import SystemTray


def get_indicator_impl():
    """Returns a BaseIndicator implementation depending on the environ"""

    use_app_indicator = (is_unity() or is_wayland() or is_kde())

    print_d("use app indicator: %s" % use_app_indicator)
    if not use_app_indicator:
        return SystemTray
    else:
        try:
            from .appindicator import AppIndicator
        except ImportError:
            print_w("importing app indicator failed")
            print_exc()
            # no indicator, fall back
            return SystemTray
        else:
            return AppIndicator


class TrayIconPlugin(EventPlugin):

    PLUGIN_ID = "Tray Icon"
    PLUGIN_NAME = _("Tray Icon")
    PLUGIN_DESC = _("Controls Quod Libet from the system tray.")

    def enabled(self):
        impl = get_indicator_impl()
        self._tray = impl()
        self._tray.set_song(app.player.song)
        self._tray.set_info_song(app.player.info)
        self._tray.set_paused(app.player.paused)

        if not is_osx() and not pconfig.getboolean("window_visible"):
            Window.prevent_inital_show(True)

    def disabled(self):
        self._tray.remove()
        del self._tray

    def PluginPreferences(self, parent):
        return Preferences()

    def plugin_on_song_started(self, song):
        self._tray.set_song(app.player.song)
        self._tray.set_info_song(app.player.info)

    def plugin_on_paused(self):
        self._tray.set_paused(True)

    def plugin_on_unpaused(self):
        self._tray.set_paused(False)
