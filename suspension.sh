#!/bin/vbash
cd /config/scripts
commands=$(python3 suspension.py)
eval "$commands"
