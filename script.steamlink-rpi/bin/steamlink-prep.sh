#!/bin/sh

# SPDX-License-Identifier: GPL-2.0
# Copyright (C) 2019-present Team LibreELEC (https://libreelec.tv)

. /etc/profile
oe_setup_addon script.steamlink-rpi

# Merge addon libs with those bundled from download
cp -a ${ADDON_DIR}/system-libs/* ${ADDON_DIR}/steamlink/lib

# Systemd setup
ln -snf ${ADDON_DIR}/system.d/steamlink-rpi.watchdog.service ${HOME}/.config/system.d/
systemctl enable ${HOME}/.config/system.d/steamlink-rpi.watchdog.service

# Finalize
touch ${ADDON_DIR}/prep.ok
