# SPDX-License-Identifier: GPL-2.0
# Copyright (C) 2019-present Team LibreELEC (https://libreelec.tv)

import os
import tarfile
import subprocess
import xbmcaddon
import xbmcgui
from pathlib import Path
from tempfile import TemporaryDirectory
from sys import exit
from urllib.request import urlretrieve


ADDON_DIR = xbmcaddon.Addon().getAddonInfo("path") + "/"


def GetRPiProcessor():
  """ Use vcgencmd to obtain cpu identifier as int """
  VC_CMD_OUTPUT=subprocess.check_output(["vcgencmd", "otp_dump"], encoding="utf-8")

  for line in VC_CMD_OUTPUT.splitlines():
    if line[0:3] == "30:":
      PROCESSOR=line.split(":")[1] # entire processor id
      return int(PROCESSOR[4:5])   # only cpu id

  return 0

def DownloadSteamlinkLibre(temp_dir):
  """ Download Steam Link for RPi (LibreELEC) """
  STEAMLINK_URL = os.popen("wget -q -O - http://media.steampowered.com/steamlink/rpi/public_build.txt").read().split("\n",1)[0]
  STEAMLINK_VERSION = STEAMLINK_URL.split("http://media.steampowered.com/steamlink/rpi/steamlink-",1)[1].split(".tar.gz",1)[0]
  STEAMLINK_TARBALL_NAME = f"steamlink-rpi3-{STEAMLINK_VERSION}.tar.gz"

  STEAMLINK_TEMP_PATH = os.path.join(temp_dir, STEAMLINK_TARBALL_NAME)

  xbmcgui.Dialog().notification("Steam Link", "Downloading Steam Link (about 30MiB)", xbmcgui.NOTIFICATION_INFO, 5000)
  urlretrieve(STEAMLINK_URL, STEAMLINK_TEMP_PATH)
  if tarfile.is_tarfile(STEAMLINK_TEMP_PATH):
    xbmcgui.Dialog().notification("Steam Link", "Download complete, extracting...", xbmcgui.NOTIFICATION_INFO, 5000)
    STEAMLINK_TARBALL = tarfile.open(STEAMLINK_TEMP_PATH)
    STEAMLINK_TARBALL.extractall(path=ADDON_DIR)
  else:
    xbmcgui.Dialog().notification("Steam Link", "Download error: bad download or missing file", xbmcgui.NOTIFICATION_INFO, 5000)
    exit(1)

def InstallLibreELEC():
  # Check if running on RPi3 or higher
  if not os.path.isfile(ADDON_DIR + "steamlink/.ignore_cpuinfo") and GetRPiProcessor() < 2:
    xbmcgui.Dialog.notification("Steam Link", "Steam Link will not run on this hardware. Aborting...", xbmcgui.NOTIFICATION_INFO, 5000)
    exit(1)

  # Download Steam Link if not present
  if not os.path.isfile(ADDON_DIR + 'prep.ok'):
    with TemporaryDirectory() as Temp_Dir:
      DownloadSteamlinkLibre(Temp_Dir)
    subprocess.run(ADDON_DIR + "bin/steamlink-prep.sh")
  # Disable Steam Link's cpu check
  if not os.path.isfile(ADDON_DIR + "steamlink/.ignore_cpuinfo"):
    Path(ADDON_DIR + "steamlink/.ignore_cpuinfo").touch()

  # Start Steamlink
  xbmcgui.Dialog().notification("Steam Link", "Starting Steam Link", xbmcgui.NOTIFICATION_INFO, 3000)
  Path("/tmp/steamlink.watchdog").touch()
  subprocess.run(["systemctl", "start", "steamlink-rpi.watchdog.service"])

def InstallOSMC():
  OSMC_INSTALL_SCRIPT = ADDON_DIR + 'bin/osmc_install.sh'
  os.system("sh " + OSMC_INSTALL_SCRIPT)

def StartSteamlink():
  OS_STRING = os.popen('grep -oE "^NAME=\\".*" /etc/os-release').read() # 'NAME="LibreELEC"\n'
  OS_STRING = OS_STRING.split("\"\n",1)[0] # -> 'NAME="LibreELEC'
  OS_STRING = OS_STRING.split("NAME=\"",1)[1] # -> 'LibreELEC'

  """ Check OS and check installation accordingly """
  if OS_STRING == "LibreELEC":
    InstallLibreELEC()
  elif OS_STRING == "OSMC":
    InstallOSMC()
  else:
    xbmcg.Dialog.notification("Steam Link", "Unssupported operaiong system. Aborting...",
    xbmcgui.NOTIFICATION_INFO, 5000)
    exit(1)


# Main
StartSteamlink()
