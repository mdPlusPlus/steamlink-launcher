#!/bin/bash


install_on_osmc () {
	# Kodi notification
	kodi-send --action="Notification(Installing Steamlink, Please wait while installing Steamlink and packages,1500)"

	# Install dependencies
	sudo apt-get install curl gnupg libc6 xz-utils -y

	# Install Steam Link
	wget http://media.steampowered.com/steamlink/rpi/steamlink.deb -O /tmp/steamlink.deb
	sudo dpkg -i /tmp/steamlink.deb
	rm -f /tmp/steamlink.deb

	# udev rules
	sudo mv /home/osmc/.local/share/SteamLink/udev/rules.d/*-steamlink.rules /lib/udev/rules.d/
}

start_steamlink () {
	sudo su -c "nohup sudo openvt -c 7 -s -f -l /tmp/steamlink-watchdog.sh 2>&1 </dev/null &"
}

detect_steamlink () {
	if [ "$(which steamlink)" -eq "1" ]
		then start_steamlink
	else
		install_on_osmc
	fi
}

# Main
detect_steamlink

