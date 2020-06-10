#!/bin/bash

# ?
hyperion_fix_osmc () {
    if [ "$HYPERIONFIX" = 1 ]; then
        if [ "$(pgrep hyperion)" ]; then sudo systemctl stop hyperion; fi
        if [ ! "$(pgrep hyperion)" ]; then sudo systemctl start hyperion; fi
    fi
}
hyperion_fix_libre () {
    if [ "$HYPERIONFIX" = 1 ]; then
        if [ "$(pgrep hyperion)" ]; then systemctl stop hyperion; fi
        if [ ! "$(pgrep hyperion)" ]; then systemctl start hyperion; fi
    fi
}


# Watchdog on OSMC
watchdog_osmc () {
    sudo systemctl stop mediacenter
    hyperion_fix_osmc
    sudo -u osmc steamlink
    sudo openvt -c 7 -s -f clear
    sudo systemctl start mediacenter
}

# Enable udev rules
mount_overlay () {
    mount -t overlay overlay \
        -o lowerdir=/lib/udev/rules.d,upperdir=/storage/steamlink/udev/rules.d/,workdir=/storage/steamlink/overlay_work
    udevadm trigger
}

# Disable udev rules
unmount_overlay () {
    umount /lib/udev/rules.d/
    udevadm trigger
}


# FIXME (RPi4): # /storage/steamlink/steamlink.sh
#                 * failed to add service - already in use?
#
# Official response to that: https://steamcommunity.com/app/353380/discussions/6/1642041886371250832/?ctp=4#c3428846977637944531
# This is because on Buster the graphics hardware is in use for system display
# and Qt can't create an EGL context on the console. You'll need to run a
# minimal X11 setup in order to use Steam Link on the Raspberry Pi 4.
#
# FIXME: "systemctl kodi stop" kills everything run from kodi
#        steamlink.sh does not get started
#        How to circumvent this?
#        Write systemd service that stops kodi and starts steamlink.sh?
#
# Watchdog on LibreELEC
watchdog_libre () {
    systemctl stop kodi
    #systemctl stop pluseaudio
    hyperion_fix_libre
    mount_overlay
    #/storage/steamlink/steamlink.sh &> /storage/steamlink/steamlink.log >/dev/null 2>&1 &
    /storage/steamlink/steamlink.sh >/storage/steamlink/steamlink.log >/dev/null 2>&1
    unmount_overlay
    #systemctl start pulseaudio
    systemctl start kodi
}

os_detection () {
    case $(grep -oE "^NAME=\".*" /etc/os-release) in
     *LibreELEC*) watchdog_libre ;;
          *OSMC*) watchdog_osmc ;;
    esac
}

os_detection
