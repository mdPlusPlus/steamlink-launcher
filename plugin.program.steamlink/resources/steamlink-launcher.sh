#!/bin/sh

NOTIFICATION="kodi-send --action=\"Notification(Installing Steam Link, Please wait while installing Steam Link and packages... This might take awhile,1500)\""

# Installation (LibreELEC)
install_on_libre () {

    # Send notification
    $(NOTIFICATION)

    
    # Create required directories
    mkdir -p \
        /storage/steamlink/lib \
        /storage/steamlink/overlay_work
    
    
    # Download and extract Steam SteamLink
    wget "$(wget -q -O - http://media.steampowered.com/steamlink/rpi/public_build.txt)" \
        -O /storage/steamlink.tar.gz
    tar -zxf steamlink.tar.gz
    cp /storage/steamlink/udev/rules.d/*-steamlink.rules /storage/.config/udev.rules.d/
    rm /storage/steamlink.tar.gz
    
    
    # Get required libraries
    LIB_SOURCE="https://github.com/mdPlusPlus/steamlink-launcher/raw/dev/libreelec_additonal/lib/"
    LIB_TARGET="/storage/steamlink/lib/"
    
    wget -O "${LIB_TARGET}libbsd.so.0.9.1"           "${LIB_SOURCE}libbsd.so.0.9.1"
    wget -O "${LIB_TARGET}libjpeg.so.62.2.0"         "${LIB_SOURCE}libjpeg.so.62.2.0"
    wget -O "${LIB_TARGET}libpng16.so.16.36.0"       "${LIB_SOURCE}libpng16.so.16.36.0"
    wget -O "${LIB_TARGET}libX11.so.6.3.0"           "${LIB_SOURCE}libX11.so.6.3.0"
    wget -O "${LIB_TARGET}libX11-xcb.so.1.0.0"       "${LIB_SOURCE}libX11-xcb.so.1.0.0"
    wget -O "${LIB_TARGET}libXau.so.6.0.0"           "${LIB_SOURCE}libXau.so.6.0.0"
    wget -O "${LIB_TARGET}libxcb.so.1.1.0"           "${LIB_SOURCE}libxcb.so.1.1.0"
    wget -O "${LIB_TARGET}libxcb-xkb.so.1.0.0"       "${LIB_SOURCE}libxcb-xkb.so.1.0.0"
    wget -O "${LIB_TARGET}libXdmcp.so.6.0.0"         "${LIB_SOURCE}libXdmcp.so.6.0.0"
    wget -O "${LIB_TARGET}libXext.so.6.4.0"          "${LIB_SOURCE}libXext.so.6.4.0"
    wget -O "${LIB_TARGET}libxkbcommon-x11.so.0.0.0" "${LIB_SOURCE}libxkbcommon-x11.so.0.0.0"

    ln -snf "${LIB_TARGET}libjpeg.so.62.2.0"   "${LIB_TARGET}libjpeg.so.62"
    ln -snf "${LIB_TARGET}libpng16.so.16.36.0" "${LIB_TARGET}libpng16.so.16"


    # TODO: Are the paths correct?
    # TODO: enable necessary?
    # Install Steam Link Systemd service
    SYSTEMD_TARGET="/storage/.config/system.d/"
    ln -snf /storage/.kodi/addons/plugin.program.steamlink/resources/steamlink.service "${SYSTEMD_TARGET}"
    systemctl enable "${SYSTEMD_TARGET}steamlink.service"


    # Actually start Steam Link
    start_steamlink
}

# Installation (OSMC)
install_on_osmc () {

    # Send notification
    $(NOTIFICATION)
    
    # Install dependencies
    sudo apt-get install curl gnupg libc6 xz-utils -y
    
    # Install Steam Link
    wget http://media.steampowered.com/steamlink/rpi/steamlink.deb -O /tmp/steamlink.deb
    sudo dpkg -i /tmp/steamlink.deb
    rm -f /tmp/steamlink.deb
    sudo mv /home/osmc/.local/share/SteamLink/udev/rules.d/*-steamlink.rules /lib/udev/rules.d/
    
    # TODO: Why this line?
    sudo -u osmc steamlink
    
    # Actually start Steam Link
    start_steamlink
}

# Start Steam Link
start_steamlink () {
    # TODO: Correct path for steamlink-watchdog.sh
    chmod 755 /tmp/steamlink-watchdog.sh
    case $(cat /etc/os-release | grep -oE "^NAME=\".*") in
     *LibreELEC*) systemctl start steamlink
          *OSMC*) sudo su -c "nohup sudo openvt -c 7 -s -f -l /tmp/steamlink-watchdog.sh >/dev/null 2>&1 &" ;;
    esac
}

# Detect existing installation
detect_steamlink () {
    case $(cat /etc/os-release | grep -oE "^NAME=\".*") in
     *LibreELEC*) if [ -f "/storage/steamlink/steamlink.sh" ]; then start_steamlink ; else install_on_libre; fi ;;
          *OSMC*) if [ "$(which steamlink)" -eq "1" ]; then start_steamlink ; else install_on_osmc; fi ;;
    esac
}

# Main
detect_steamlink
