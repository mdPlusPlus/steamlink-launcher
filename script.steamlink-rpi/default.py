# SPDX-License-Identifier: GPL-2.0
# Copyright (C) 2019-present Team LibreELEC (https://libreelec.tv)

import os
import tarfile
import subprocess
import xbmcaddon
import xbmcgui
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from sys import exit
from urllib.request import urlretrieve


# STEAMLINK_VERSION = "@STEAMLINK_VERSION@"
STEAMLINK_VERSION = "1.1.64.162"
# STEAMLINK_HASH = "@STEAMLINK_HASH@"
STEAMLINK_HASH = "1ea1c41802bd6cc3efdba7ba258b9d25d5c07cdd1d0ffe9f2d47597588a09155"
STEAMLINK_TARBALL_NAME = f"steamlink-rpi3-{STEAMLINK_VERSION}.tar.gz"
STEAMLINK_URL = f"http://media.steampowered.com/steamlink/rpi/{STEAMLINK_TARBALL_NAME}"
ADDON_DIR = xbmcaddon.Addon().getAddonInfo("path") + "/"


def GetSHA256Hash(file_name):
  """ Get sha256sum of file_name in 8kb chunks """
  with open(file_name,"rb") as file:
    SHA256HASH = sha256()
    while True:
      data_block = file.read(8192)
      if not data_block:
        break
      SHA256HASH.update(data_block)
  return SHA256HASH.hexdigest()

def GetRPiProcessor():
  """ Use vcgencmd to obtain cpu identifier as int """
  VC_CMD_OUTPUT=subprocess.check_output(["vcgencmd", "otp_dump"], encoding="utf-8")

  for line in VC_CMD_OUTPUT.splitlines():
    if line[0:3] == "30:":
      PROCESSOR=line.split(":")[1] # entire processor id
      return int(PROCESSOR[4:5])   # only cpu id

  return 0

def DownloadSteamlink(temp_dir):
  """ Download Steam Link for RPi """
  STEAMLINK_TEMP_PATH = os.path.join(temp_dir, STEAMLINK_TARBALL_NAME)

  xbmcgui.Dialog().notification("Steam Link", "Downloading Steam Link (about 30MiB)", xbmcgui.NOTIFICATION_INFO, 5000)
  urlretrieve(STEAMLINK_URL, STEAMLINK_TEMP_PATH)
  if tarfile.is_tarfile(STEAMLINK_TEMP_PATH):
    DOWNLOAD_HASH = GetSHA256Hash(STEAMLINK_TEMP_PATH)
    if STEAMLINK_HASH == DOWNLOAD_HASH:
      xbmcgui.Dialog().notification("Steam Link", "Download complete, extracting...", xbmcgui.NOTIFICATION_INFO, 5000)
      STEAMLINK_TARBALL = tarfile.open(STEAMLINK_TEMP_PATH)
      STEAMLINK_TARBALL.extractall(path=ADDON_DIR)
    else:
      xbmcgui.Dialog().notification("Steam Link", "Download error: bad file hash, try again later", xbmcgui.NOTIFICATION_INFO, 5000)
      exit(1)
  else:
    xbmcgui.Dialog().notification("Steam Link", "Download error: bad download or missing file", xbmcgui.NOTIFICATION_INFO, 5000)
    exit(1)

def StartSteamlink():
  # Check if running on RPi3 or higher
  if not os.path.isfile(ADDON_DIR + "steamlink/.ignore_cpuinfo") and GetRPiProcessor() < 2:
    xbmcgui.Dialog.notification("Steam Link", "Steam Link will not run on this hardware. Aborting...", xbmcgui.NOTIFICATION_INFO, 5000)
    exit(1)

  # Download Steam Link if not present
  if not os.path.isfile(ADDON_DIR + 'prep.ok'):
    with TemporaryDirectory() as Temp_Dir:
      DownloadSteamlink(Temp_Dir)
    subprocess.run(ADDON_DIR + "bin/steamlink-prep.sh")
  # Disable Steam Link's cpu check
  if not os.path.isfile(ADDON_DIR + "steamlink/.ignore_cpuinfo"):
    Path(ADDON_DIR + "steamlink/.ignore_cpuinfo").touch()

  # Start Steamlink
  xbmcgui.Dialog().notification("Steam Link", "Starting Steam Link", xbmcgui.NOTIFICATION_INFO, 3000)
  Path("/tmp/steamlink.watchdog").touch()
  subprocess.run(["systemctl", "start", "steamlink-rpi.watchdog.service"])


StartSteamlink()
