#!/bin/bash

# check inputs and print USAGE message
if [ $# -lt 1 ]; then
    echo "USAGE: " $0 "<tunnel-host> [URL]"
    echo "where <tunnel-host> can be of the form user@host."
    echo ""
    exit
fi

# read tunnel host and print info to screen
tunnel_host=$1
echo "will route traffic through ${tunnel_host}"

# read URL
URL=$2

# find free port
socks_5_port=$(python -c 'import socket; s=socket.socket(); s.bind(("localhost", 0)); print(s.getsockname()[1]); s.close()')
echo "will use using port $socks_5_port"

# Open socks5 proxy which will close after 60 Seconds if the tunnel is not
# used and stay open as long as it is used.
ssh -f -D localhost:${socks_5_port} ${tunnel_host} sleep 60

# temporary user dir
tmp_user_dir=/tmp/temp_chrome_user_dir_$(date +%s%N)

# cycle through possible browsers
browser=$(
    which chromium-browser &>/dev/null && { echo chromium-browser; exit; }
    which chromium &>/dev/null && { echo chromium; exit; }
    [ -e /Applications/Chromium.app/Contents/MacOS/Chromium ] && { echo "/Applications/Chromium.app/Contents/MacOS/Chromium"; exit; }
    [ -e /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome ] && { echo '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'; exit; }
)

# start browser with tunnel as socks5 proxy
"${browser}" \
    --proxy-bypass-list="<-loopback>" \
    --proxy-server="socks5://localhost:${socks_5_port}" \
    --new-window --user-data-dir=${tmp_user_dir} \
    ${URL}

# clean up temp temporary user dir
rm -rf ${tmp_user_dir}
