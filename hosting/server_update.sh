#!/bin/bash

########################################################################################################################
# Run this script as sudo to update the project environment as the service user and restart the systemd service. This
# expects the system components to have been installed as defined in ./server_install_system_components.sh.
#
# Note: This does not update the local project files, so do that with git prior to running this script.
#
# Dependencies:
# - systemd
# - nginx
# - systemd-analyze
########################################################################################################################
set -e # Stop script if any command fails

SERVICE_USER='com_jrdbnntt_wedding'

ORIGINAL_WORKING_DIR="$(pwd)"
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
source "${SCRIPT_DIR}/server_config_vars.sh"
cd "${PROJECT_DIR}" || exit 1

# Verify config files are valid
test_nginx_config
test_systemd_config

# Ensure all project files are owned by service user
chown -R "${SERVICE_USER}:${FILE_OWNERSHIP_GROUP}" "${PROJECT_DIR}"
chown -R "${SERVICE_USER}:${FILE_OWNERSHIP_GROUP}" "${DJANGO_SERVER_LOG_DIR}"

# Stop service
systemctl stop "${SYSTEMD_SERVICE_NAME}"

# Archive logs
LOG_ARCHIVE_PATH="${DJANGO_SERVER_LOG_DIR}/logs_${FILENAME_DATETIME_NOW_SUFFIX}.tar.gz"
FILES_TO_LOG=$(runuser -l "${SERVICE_USER}" find -P /var/log -mindepth 1 -maxdepth 1 '(' -type d,f ! -name '*.gz' ')' | tr '\n' ' ')
echo "${FILES_TO_LOG}" | xargs -0 runuser -l "${SERVICE_USER}" tar -czvf "${LOG_ARCHIVE_PATH}"
echo "${FILES_TO_LOG}" | xargs -0 runuser -l "${SERVICE_USER}" rm -rf

# Restart service and reload nginx
systemctl start "${SYSTEMD_SERVICE_NAME}"
nginx -s HUP

echo "Server updated"
cd "${ORIGINAL_WORKING_DIR}" || exit 1