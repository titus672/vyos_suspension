#! /usr/bin/env python3
import requests
import traceback
import json


class Config:
    def __init__(self):
        with open("config.json", "r") as config:
            self.config = json.load(config)
        self.uisp_url = self.config.get("uisp_url", None)
        self.nms_key = self.config.get("nms_key", None)
        self.crm_key = self.config.get("crm_key", None)
        self.discord_url = self.config.get("discord_url", None)


CONFIG = Config()


def nms_connector(endpoint, action="get"):
    url = f"https://{CONFIG.uisp_url}/nms/api/v2.1/{endpoint}"
    headers = {"x-auth-token": CONFIG.nms_key, "accept": "application/json"}
    request = requests.request(action, url, headers=headers)
    request.raise_for_status()
    return request.json()


def crm_connector(endpoint, action="get"):
    url = f"https://{CONFIG.uisp_url}/crm/api/v1.0/{endpoint}"
    headers = {"x-auth-token": CONFIG.crm_key, "accept": "application/json"}
    request = requests.request(action, url, headers=headers)
    request.raise_for_status()
    return request.json()


def discord_post(url, message):
    if url is not None:
        contents = {
            "content": str(message),
            "username": "vyos_suspension",
        }
        requests.post(url, json=contents)
        print("Error:", message)
    else:
        print("Error:", message)


def get_suspended_ips():
    result = crm_connector("clients/services?statuses%5B%5D=2&statuses%5B%5D=3")
    suspended_sites = []
    suspended_devices = []
    for r in result:
        if r["unmsClientSiteId"]:
            suspended_sites.append(r["unmsClientSiteId"])

    for s in suspended_sites:
        suspended_devices.append(nms_connector(f"devices?siteId={s}"))
    suspended_ips = []
    for device in suspended_devices:
        for a in device:
            if a["ipAddress"]:
                suspended_ips.append(a["ipAddress"].split("/")[0])
    return suspended_ips


def main():
    f_ips = get_suspended_ips()
    if len(f_ips) != 0:
        commands = ""
        commands += "source /opt/vyatta/etc/functions/script-template\n"
        commands += "configure\n"
        commands += "delete firewall group address-group SUSPENDED_IPS\n"
        commands += "set firewall group address-group SUSPENDED_IPS\n"
        for ip in f_ips:
            commands += f"set firewall group address-group SUSPENDED_IPS address {ip}\n"
        commands += "commit\n"
        commands += "save\n"
        commands += "exit\n"
        print(commands)
    else:
        commands = ""
        commands += "source /opt/vyatta/etc/functions/script-template\n"
        commands += "configure\n"
        commands += "delete firewall group address-group SUSPENDED_IPS\n"
        commands += "set firewall group address-group SUSPENDED_IPS\n"
        commands += "set firewall group address-group SUSPENDED_IPS address 172.16.0.254\n"
        commands += "commit\n"
        commands += "save\n"
        commands += "exit\n"
        print(commands)


try:
    main()
except requests.exceptions.HTTPError as httperror:
    discord_post(CONFIG.discord_url, f"HTTPError:\n```{httperror}```")
    exit(1)
except requests.exceptions.ConnectionError as timeouterr:
    discord_post(CONFIG.discord_url, f"ConnErr:\n```{timeouterr}```")
    exit(1)
except Exception:
    tb = traceback.format_exc()
    discord_post(CONFIG.discord_url, f"Fatal:\n```{tb}```")
    exit(1)
