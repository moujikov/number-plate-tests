#!/bin/bash

set -eu -o pipefail

ftp_users=()

while IFS='=' read -r -d '' user_var login; do
  if [[ "$user_var" == FTP_USER_* ]]; then
    id="${user_var#FTP_USER_}"
    password_var="FTP_PASSWORD_${id}"
    password="${!password_var:-}"

    if [[ -z "$password" ]]; then
      echo "Error: No password found for user '$login' (expected in variable '$password_var')" >&2
      exit 1
    fi

    echo "Setting up FTP user: $login"

    adduser -u 100${id} -G ftp -s /sbin/nologin -h "/home/$login" -D "$login"
    echo "$login:$password" | chpasswd > /dev/null 2>&1

    mkdir -p "/home/$login/upload"
    chown "$login:ftp" "/home/$login/upload"

    ftp_users+=( "$login" )
  fi
done < <(env -0)

config='/etc/proftpd/conf.d/runtime.conf'

if [[ -n "${PORT:-}" ]]; then
  echo "Setting FTP server port: ${PORT}"
  echo "Port $PORT" >> $config
fi

if [[ -n "${PASSIVE_PORTS:-}" ]]; then
  echo "Setting FTP server passive ports: ${PASSIVE_PORTS}"
  echo "PassivePorts ${PASSIVE_PORTS/-/ }" >> $config
fi

echo "<Limit LOGIN>" >> $config
for user in "${ftp_users[@]}"; do
  echo "  AllowUser $user" >> $config
done
echo "  DenyAll" >> $config
echo "</Limit>" >> $config


### Start the FTP server
exec proftpd -n
