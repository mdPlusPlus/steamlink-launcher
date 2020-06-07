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
addon = xbmcaddon.Addon(id='plugin.program.steamlink')

def main():
    """Main operations of this plugin."""
    create_files()
    output = os.popen("sh /tmp/steamlink-launcher.sh").read()
    dialog.ok("Starting Steamlink...", output)

def create_files():
    """Creates bash files to be used for this plugin."""
    with open('/tmp/steamlink-launcher.sh', 'w') as outfile:
        outfile.write("""#!/bin/sh
# installation part
install_on_libre () {
kodi-send --action="Notification(Installing Steamlink, Please wait while installing Steamlink and packages.. this might take awhile,1500)"

mkdir -p /storage/steamlink
mkdir -p /storage/steamlink/overlay_work
mkdir -p /storage/steamlink/lib

# Download and extract Steam SteamLink
cd /storage/
wget "$(wget -q -O - http://media.steampowered.com/steamlink/rpi/public_build.txt)" -O /storage/steamlink.tar.gz
tar -zxf steamlink.tar.gz
cp /storage/steamlink/udev/rules.d/55-steamlink.rules /storage/.config/udev.rules.d/55-steamlink.rules
rm /storage/steamlink.tar.gz

# Get required libraries
wget -O /storage/steamlink/lib/libbsd.so.0.9.1           https://github.com/mdPlusPlus/steamlink-launcher/raw/dev/libreelec_additonal/lib/libbsd.so.0.9.1
wget -O /storage/steamlink/lib/libicudata.so.63.1        https://github.com/mdPlusPlus/steamlink-launcher/raw/dev/libreelec_additonal/lib/libicudata.so.63.1
wget -O /storage/steamlink/lib/libicui18n.so.63.1        https://github.com/mdPlusPlus/steamlink-launcher/raw/dev/libreelec_additonal/lib/libicui18n.so.63.1
wget -O /storage/steamlink/lib/libicuuc.so.63.1          https://github.com/mdPlusPlus/steamlink-launcher/raw/dev/libreelec_additonal/lib/libicuuc.so.63.1
wget -O /storage/steamlink/lib/libjpeg.so.62.2.0         https://github.com/mdPlusPlus/steamlink-launcher/raw/dev/libreelec_additonal/lib/libjpeg.so.62.2.0
wget -O /storage/steamlink/lib/libpng16.so.16.36.0       https://github.com/mdPlusPlus/steamlink-launcher/raw/dev/libreelec_additonal/lib/libpng16.so.16.36.0
wget -O /storage/steamlink/lib/libX11.so.6.3.0           https://github.com/mdPlusPlus/steamlink-launcher/raw/dev/libreelec_additonal/lib/libX11.so.6.3.0
wget -O /storage/steamlink/lib/libX11-xcb.so.1.0.0       https://github.com/mdPlusPlus/steamlink-launcher/raw/dev/libreelec_additonal/lib/libX11-xcb.so.1.0.0
wget -O /storage/steamlink/lib/libXau.so.6.0.0           https://github.com/mdPlusPlus/steamlink-launcher/raw/dev/libreelec_additonal/lib/libXau.so.6.0.0
wget -O /storage/steamlink/lib/libxcb.so.1.1.0           https://github.com/mdPlusPlus/steamlink-launcher/raw/dev/libreelec_additonal/lib/libxcb.so.1.1.0
wget -O /storage/steamlink/lib/libxcb-xkb.so.1.0.0       https://github.com/mdPlusPlus/steamlink-launcher/raw/dev/libreelec_additonal/lib/libxcb-xkb.so.1.0.0
wget -O /storage/steamlink/lib/libXdmcp.so.6.0.0         https://github.com/mdPlusPlus/steamlink-launcher/raw/dev/libreelec_additonal/lib/libXdmcp.so.6.0.0
wget -O /storage/steamlink/lib/libXext.so.6.4.0          https://github.com/mdPlusPlus/steamlink-launcher/raw/dev/libreelec_additonal/lib/libXext.so.6.4.0
wget -O /storage/steamlink/lib/libxkbcommon-x11.so.0.0.0 https://github.com/mdPlusPlus/steamlink-launcher/raw/dev/libreelec_additonal/lib/libxkbcommon-x11.so.0.0.0

cd /storage/steamlink/lib
ln -s libjpeg.so.62.2.0   libjpeg.so.62
ln -s libpng16.so.16.36.0 libpng16.so.16

# Download and enable swetoast's udev rules
cd /storage/
wget https://raw.githubusercontent.com/swetoast/steamlink-launcher/dev/libreelec_additonal/60-steam-input.rules -O /storage/.config/system.d/storage-steamlink-udev-rules.d.mount
systemctl enable storage-steamlink-udev-rules.d.mount
udevadm trigger

# Actually start Steam Link
start_steamlink
}

install_on_osmc () {
kodi-send --action="Notification(Installing Steamlink, Please wait while installing Steamlink and packages,1500)"
sudo mv /home/osmc/.local/share/SteamLink/udev/rules.d/55-steamlink.rules /lib/udev/rules.d/55-steamlink.rules
sudo apt-get install curl gnupg libc6 xz-utils -y
wget http://media.steampowered.com/steamlink/rpi/steamlink.deb -O /tmp/steamlink.deb
sudo dpkg -i /tmp/steamlink.deb
rm -f /tmp/steamlink.deb
sudo -u osmc steamlink
start_steamlink
}

install_on_os () {
case $(cat /etc/os-release | grep -oE "^NAME=\\".*") in
 *LibreELEC*) install_on_libre ;;
      *OSMC*) install_on_osmc ;;
esac
}

# TODO: Why "su -c" for LibreELEC? User is already root
start_steamlink () {
chmod 755 /tmp/steamlink-watchdog.sh
case $(cat /etc/os-release | grep -oE "^NAME=\\".*") in
 *LibreELEC*) su -c "nohup /tmp/steamlink-watchdog.sh >/dev/null 2>&1 &" ;;
      *OSMC*) sudo su -c "nohup sudo openvt -c 7 -s -f -l /tmp/steamlink-watchdog.sh >/dev/null 2>&1 &" ;;
esac
}

detect_steamlink () {
case $(cat /etc/os-release | grep -oE "^NAME=\\".*") in
 *LibreELEC*) if [ -f "/storage/steamlink/steamlink" ]; then start_steamlink ; else install_on_os; fi ;;
      *OSMC*) if [ "$(which steamlink)" -eq "1" ]; then start_steamlink ; else install_on_os; fi ;;
esac

}

detect_steamlink
""")
        outfile.close()

    with open('/tmp/steamlink-watchdog.sh', 'w') as outfile:
        outfile.write("""#!/bin/bash
# watchdog part
watchdog_osmc () {
sudo systemctl stop mediacenter
if [ "$HYPERIONFIX" = 1 ]; then
   if [ "$(pgrep hyperion)" ]; then sudo systemctl stop hyperion; fi
   if [ ! "$(pgrep hyperion)" ]; then sudo systemctl start hyperion; fi
fi
sudo -u osmc steamlink
sudo openvt -c 7 -s -f clear
sudo systemctl start mediacenter
}

watchdog_libre () {
systemctl stop kodi
if [ "$HYPERIONFIX" = 1 ]; then
   if [ "$(pgrep hyperion)" ]; then systemctl stop hyperion; fi
   if [ ! "$(pgrep hyperion)" ]; then systemctl start hyperion; fi
fi
systemctl stop kodi
/storage/steamlink/steamlink.sh &> /storage/steamlink/steamlink.log >/dev/null 2>&1 &
systemctl start kodi
}

os_detection () {
case $(cat /etc/os-release | grep -oE "^NAME=\\".*") in
 *LibreELEC*) watchdog_libre ;;
      *OSMC*) watchdog_osmc ;;
esac
}

os_detection
""")
        outfile.close()

main()
