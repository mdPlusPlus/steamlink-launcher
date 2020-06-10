#!/bin/bash

# Installation (OSMC)
install_on_osmc () {

    # Install dependencies
    sudo apt-get install curl gnupg libc6 xz-utils -y

    # Install Steam Link
    wget http://media.steampowered.com/steamlink/rpi/steamlink.deb -O /tmp/steamlink.deb
    sudo dpkg -i /tmp/steamlink.deb
    rm -f /tmp/steamlink.deb
    sudo mv /home/osmc/.local/share/SteamLink/udev/rules.d/*-steamlink.rules /lib/udev/rules.d/

}

