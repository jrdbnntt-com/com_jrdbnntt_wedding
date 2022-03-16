PROJECT_DIR_NAME='com_jrdbnntt_wedding'
SERVICE_USER='com_jrdbnntt_wedding'
FILE_OWNERSHIP_GROUP='www-data'
REQUIRED_REPO_INSTALL_DIR="/var/www/${PROJECT_DIR_NAME}"
DJANGO_SERVER_LOG_DIR="/var/www/${PROJECT_DIR_NAME}"
NGINX_CONFIG_DIR='/etc/nginx/conf.d'
SYSTEMD_INSTALL_DIR="/etc/systemd"
SYSTEMD_SERVICE_NAME="${PROJECT_DIR_NAME}.service"
PROJECT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )/.." &> /dev/null && pwd )
PROJECT_NGINX_CONFIG_PATH="${PROJECT_DIR}/hosting/nginx.conf"
PROJECT_NGINX_TEST_CONFIG_PATH="${PROJECT_DIR}/hosting/nginx_test.conf"
PROJECT_SYSTEMD_SERVICE_PATH="${PROJECT_DIR}/hosting/systemd.service"
FILENAME_DATETIME_NOW_SUFFIX=$(date --utc +"%Y-%m-%dT%H-%M-%SZ")
DAPHNE_SERVER_PORT=5000

function test_nginx_config {
  echo "Testing nginx config..."
  if nginx -t -c "${PROJECT_NGINX_TEST_CONFIG_PATH}"; then
    echo "nginx config error"
    exit 1
  fi
}

function test_systemd_config {
  echo "Testing systemd config..."
  if systemd-analyze verify "${PROJECT_SYSTEMD_SERVICE_PATH}" &> /dev/null; then
    echo "systemd config error"
    exit 1
  fi
}
