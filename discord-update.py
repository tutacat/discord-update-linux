#!/bin/env python3
import json
import os
import requests
import signal
import subprocess
import sys
import tempfile
import urllib.request

def log(*args, **kwargs):
    kwargs["file"] = sys.stderr
    print(*args, **kwargs)

def ver_tuple(ver_string):
    return tuple(int(n) for n in ver_string.split("."))

# ----

def get_web_version():
    x = requests.head(download_url)
    # curl -h | grep -i '^location=' | cut -f = -d 2
    location = x.headers["location"]
    log(location)
    return location.split("=",1)[-1]


### Official postinst.sh
#def discord_postint():
#    return subprocess.run(("bash", os.path.join(discord_inst, "postinst.sh")))

### Built-in post-inst
def discord_postinst():
    ### this is the same method as "official" script but less buggy, doesn't try and remove all /home users caches
    import shutil
    ### remove local cache
    DIR = os.environ.get("HOME")
    for path in (f"{DIR}/.config/discord/Cache", f"{DIR}/.config/discord/GPUCache"):
        shutil.rmtree(path)
    ### check file owners
    settings_dat = f"{HOME}/.config/Crashpad/settings.dat"
    owner = os.stat(settings_dat).st_uid

    if os.getuid() != owner:
        import pwd
        print(f"discord-update.py: warning: file(s) not owned by you under: {os.path.realpath(os.path.join(settings_dat, '..'))}")
        print(f"It is owned by {owner} (username: `{pwd.getpwuid(owner).pw_name}`)")
        if 0 == owner:
            print("This is most likely due to an older bug in Discord.")
            print("You should remove that directory tree as root")
        else:
            print("This is unexpected.")
            print("You should either remove the directory tree (.config/discord/Crashpad), or take ownership")
        exit(1)


data_home = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share");
config_home = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config");

discord_inst = data_home


build_info=f"{discord_inst}/Discord/resources/build_info.json";
version = (0,0,0);
platform = "linux";
format = "tar.gz";
release_channel = "stable";

download_url = f"https://discord.com/api/download/{release_channel}?platform={platform}&format={format}"

if os.path.isfile("install.conf"):
    with open("install.conf") as file:
        conf = [v.split("=",1) for v in file.read().split("\n") if not v.lstrip()[0].startsWith("#")]
        conf = {v[0]:v[1] for v in conf}
    if "discord_install_parent" in conf:
        discord_inst = conf["discord_install_parent"]
    if "discord_tarball_url" in conf:
        download_url = conf["discord_tarball_url"]



if os.path.isfile(build_info):
    print("Discord info exists.")
    info = json.load(open(build_info))
    release_channel = info["releaseChannel"]
    log(f'Current version: "{info["version"]}"')
    current_version = ver_tuple(info["version"])
else:
    print("Discord info DOESN'T EXIST.")
    current_version = (0, 0, 0)

latest_verstring = get_web_version().rsplit("/",1)[1].rsplit(".",2)[0].split("-",1)[1]
log(f'Latest version: "{latest_verstring}"')
latest_version = ver_tuple(latest_verstring)

log(f"release_channel = {release_channel}, current_version = {current_version}")
sysname = os.uname().sysname
if not (platform == "linux" and sysname == "Linux"):
    print(f"Unexpected platform? Target is {platform} but host kernel is {sysname}?");

log(f"latest_version version: {latest_version}")

if latest_version > current_version:
    print("New Discord version is available.");
    if os.isatty(1):
        ans = input("Would you like to update? (Y/n)");
        if ans.strip().lower()[0] == "n":
            print("OK, quitting...")
            exit(0)
    do_restart = False;
    procs = subprocess.getoutput("pgrep -x Discord").split("\n")
    log("procs:",procs)
    if procs and procs[-1]:
        do_restart = True
        for proc in procs:
            os.kill(int(proc), signal.SIGTERM)
    update_file = tempfile.NamedTemporaryFile(delete=False, delete_on_close=False)
    update_path = update_file.path
    update_file.close()
    urllib.request.urlretrieve(download_url, update_path)
    quot = "'"
    escquot = "'\\''"
    stat = subprocess.run(
        ("tar",
         "-xzf", update_path, # extract, gzipped, file
         "-C", discord_inst, # Containing directory
         "Discord" # archive item
        ), capture_output=True)
    os.remove(update_path)
    if stat.returncode < 1:
        stat = discord_postinst()
    else:
        print("An error occured extracting Discord");
        print(stat.stdout.decode(), stat.stderr.decode(), sep="\n")
else:
    print("Available Discord version is not higher than current version.")
    exit(0)

if do_restart:
    os.system('gio launch "${data_home:-$HOME/.local/share}/applications/discord-stable.desktop" -- </dev/null 2>&1 >/dev/null & sleep 0.1; disown -a -h')

