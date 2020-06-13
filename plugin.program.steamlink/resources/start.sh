#!bin/bash

. /etc/profile
oe_setup_addon plugin.program.steamlink

# Mount an overlay for udev rules and reload udev rules
if [ $(grep -c "/lib/udev/rules.d" /proc/mounts) -eq 0 ]; then
	if [ ! -d ${ADDON_DIR}/steamlink/.overlay ]; then
		mkdir -p ${ADDON_DIR}/steamlink/.overlay
	fi
	mount -t overlay overlay -o lowerdir=/lib/udev/rules.d,upperdir=${ADDON_DIR}/steamlink/udev/rules.d/,workdir=${ADDON_DIR}/steamlink/.overlay /lib/udev/rules.d/
	udevadm trigger
fi

# Launch Steam Link
systemctl stop kodi # Shutdown kodi or controller input goes to kodi too
systemctl stop pulseaudio # Shutdown pulseaudio or no sound
${ADDON_DIR}/steamlink/steamlink.sh
sleep 3

# Cleanup
umount /lib/udev/rules.d/
#rm /tmp/steamlink.watchdog
systemctl start pulseaudio
systemctl start kodi
