"""Steamlink Launcher for OSMC"""
import os
import xbmc
import xbmcgui
import xbmcaddon

__plugin__ = "Steamlink"
__author__ = "Toast"
__url__ = "https://github.com/swetoast/steamlink-launcher/"
__git_url__ = "https://github.com/swetoast/steamlink-launcher/"
__credits__ = "Ludeeus, Slouken, sgroen88, ToiletSalad, mdPlusPlus"
__version__ = "0.0.7"

dialog = xbmcgui.Dialog()
ADDON_DIR = xbmcaddon.Addon().getAddonInfo("path") + "/"

def main():
    """Main operations of this plugin."""
    output = os.popen("sh " + ADDON_DIR + "resources/steamlink-launcher.sh").read()
    dialog.ok("Starting Steamlink...", output)


main()
