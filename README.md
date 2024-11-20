# Vyos suspension scripts
the purpose of these scripts is to collect
the suspended clients from UISP and turn
off their service in an automated fashion

## Docs
# vyos suspension docs

### prerequisites
1. vyos > 1.4.x
2. put `suspension.sh` and `suspension.py` in the /config/scripts/ directory

### Create dnat and firewall rules
These rules are only created once. To suspend or unsuspend devices, add or remove them from the
"SUSPENDED_IPS" firewall address group

## be sure to replace the translation
## and destination addresses before
## running these commands
```
set firewall group address-group SUSPENDED_IPS address 172.16.0.1
set firewall group domain-group WHITELIST_DOMAINS add uisp.example.com

set nat destination rule 10 destination port 80
set nat destination rule 10 protocol tcp
set nat destination rule 10 source group address-group SUSPENDED_IPS
set nat destination rule 10 translation address "your uisp ip address"
set nat destination rule 10 translation port 81

set firewall ipv4 forward filter rule 20 action accept
set firewall ipv4 forward filter rule 20 destination group domain-group WHITELIST_DOMAINS

set firewall ipv4 forward filter rule 30 action accept
set firewall ipv4 forward filter rule 30 destination port 53
set firewall ipv4 forward filter rule 30 protocol udp
set firewall ipv4 forward filter rule 30 source group address-group SUSPENDED_IPS

set firewall ipv4 forward filter rule 40 action drop
set firewall ipv4 forward filter rule 40 protocol tcp_udp
set firewall ipv4 forward filter rule 40 source group address-group SUSPENDED_IPS

set system task-scheduler task suspension executable path /config/scripts/suspension.sh
set system task-scheduler task suspension interval 30m
```

According to the [Docs](https://docs.vyos.io/en/latest/automation/command-scripting.html#other-script-languages)
it needs to be in two files, `suspension.sh` and `suspension.py`. `suspension.py`
has the integration to uisp to gather the suspended ips and also formats the commands
to add them to the appropriate firewall group. `suspension.sh` has the job of calling
the python script.
