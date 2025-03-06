# discord-update-linux

Helper script to install/update Discord in the user directory (or other) instead of just /opt (no root needed.)

##### Changing installation location
You can simple change the discord_install location, using `discord_install.conf`, if it is not to your liking. i.e.:

```conf
install_parent=/opt
```

##### Defaults settings
They are the same as:

```conf
# we automatically get config_home if not set
install_parent=$XDG_CONFIG_HOME
tarball_url=https://discord.com/api/download/{release_channel}?platform={platform}&format={format}
proc_name=Discord
# script is a bit weird deleting /home/*/.config/discord/{Cache,GPUCache}
official_postinst=n
```

##### *This script **will not be updated.** It is left here as a courtesy.*


