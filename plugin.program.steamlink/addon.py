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
mkdir -p /storage/raspbian
mkdir -p /storage/raspbian/image

## NOTE: Some raspbian/raspios images can not get extracted on LibreELEC (>2GB, "need PK compat.", etc.)
##       We use 7za to circumvent this
## TODO: Using a non-busybox "unzip" is probably the better alternative
wget https://github.com/develar/7zip-bin/raw/master/linux/arm/7za -O /storage/7za
chmod +x /storage/7za


# Download and extract Raspberry Pi OS
# TODO: overkill for just the libs (you currently need at least a 16GB microSD card)
cd /storage/raspbian/
wget http://downloads.raspberrypi.org/raspios_full_armhf/images/raspios_full_armhf-2020-05-28/2020-05-27-raspios-buster-full-armhf.zip
/storage/7za x 2020-05-27-raspios-buster-full-armhf.zip

# Download and extract Steam SteamLink
cd /storage/
wget "$(wget -q -O - http://media.steampowered.com/steamlink/rpi/public_build.txt)" -O /storage/steamlink.tar.gz
tar -zxf steamlink.tar.gz
cp /storage/steamlink/udev/rules.d/55-steamlink.rules /storage/.config/udev.rules.d/55-steamlink.rules
rm /storage/steamlink.tar.gz

# Mount Raspberry Pi OS image and extract necessary libs for Steam Link
# TODO: overkill
cd /storage/
# FIXME: mount does not work under busybox -- mount: mounting /dev/loop1 on /storage/raspbian/image/ failed: Invalid argument
mount -o loop,ro,offset=272629760 -t ext4 /storage/raspbian/2020-05-27-raspios-buster-full-armhf.img /storage/raspbian/image/
cd /storage/raspbian/image/
for i in libpng*.so.* libicui18n.so.* libicuuc.so.* libicudata.so.* libX11-xcb.so.* libX11.so.* libXext.so.* libxcb.so.* libxkbcommon-x11.so.* libXau.so.* libXdmcp.so.* libxcb-xkb.so.* libbsd.so.*; do cp $(find ./usr/lib/arm-linux-gnueabihf/ -type f -name $i) /storage/steamlink/lib/ ; done
cd ../..
umount /storage/raspbian/image
rm -r /storage/rasbian/

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
case $(cat /etc/os-release | grep -oE "^NAME=\".*") in
 *LibreELEC*) watchdog_libre ;;
      *OSMC*) watchdog_osmc ;;
esac
}

os_detection
""")
        outfile.close()

main()
