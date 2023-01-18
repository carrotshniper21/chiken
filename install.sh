sudo curl -sL github.com/carrotshniper21/chiken/raw/main/chiken.py -o /usr/local/bin/chiken &&
sudo chmod +x /usr/local/bin/chiken
config_home="${config_home:-$HOME/.config}"
config="$config_home/chiken/config.txt"
[ ! -d "$config_home/chiken" ] && mkdir -p "$config_home/chiken"
[ ! -f "$config" ] && printf "player=mpv\nsubs_language=English\nvideo_quality=1080\npreferred_server=vidcloud\n" > "$config"
