#!/bin/bash
#~/.local/bin/discord-update
RESTART="${RESTART:-}";

XDG_DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}";
discord_dir="$XDG_DATA_HOME/Discord";
buildinfo="$discord_dir/resources/build_info.json";
releaseChannel="stable";
version="0.0.0";
platform="linux";
format="tar.gz";

download_url="https://discord.com/api/download/${channel}?platform=${platform}&format=${format}"

if [ -e "$buildinfo" ]; then
    info=($(jq '"releaseChannel="+.releaseChannel+" version="+.version' "$buildinfo" | grep -o '[^"]*'));
    echo ${info[@]};
    export ${info[@]};
fi

#echo channel: $releaseChannel, current_version: $version
Uname="$(uname -s)";
[ "$platform" = "linux" -a "$Uname" != "Linux" ] && echo "Unexpected platform? Target is ${platform} but host is ${Uname}?";

get_version() {
    curl --head "${download_url}" \
     | grep -i '^location' \
     | cut -f 2;
}
export latest="$(get_version)";

if python -c 'import os; e=os.environ; exit(not tuple(e["latest"].split(".")) > tuple(e["version"].split(".")));'; then
    echo "Version is higher.";
    if [ -t 1 ]; then
    echo "Would you like to update? (Y/n)";
    if [ "${a[0]}" = "" ] || [ "${a[0]}" != "n" -a "${a[0]}" != "N" ]; then
        RESTART="$(pgrep Discord && echo y)";
        [ ! -z "$RESTART" ] && pkill Discord;
        if ! ( curl -L "https://discord.com/api/download/${releaseChannel}?platform=${platform}&format=${format}" \
         | tar cxz "$XDG_DATA_HOME" ) \
         && ! . ~/.local/share/Discord/postinst.sh; then
            echo "An error occured.";
        fi
    else
        echo "OK, quitting..."
        exit 0
    fi
fi

if [ ! -z "$RESTART" ]; then
    nohup gio launch "${XDG_DATA_HOME:-$HOME/.local/share}/applications/discord-stable.desktop" -- < /dev/null > /dev/null 2>&1
fi
