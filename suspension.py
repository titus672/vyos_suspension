#! /usr/bin/env python3
import requests
base_url = "uisp.example.com"
uisp_key = ""

def nms_connector(endpoint, action="get"):
    url = f"https://{base_url}/nms/api/v2.1/{endpoint}"
    headers = {"x-auth-token": uisp_key, "accept": "application/json"}
    request = requests.request(action, url, headers=headers)
    return request.json()

def crm_connector(endpoint, action="get"):
    url = f"https://{base_url}/crm/api/v1.0/{endpoint}"
    headers = {"x-auth-token": uisp_key, "accept": "application/json"}
    request = requests.request(action, url, headers=headers)
    return request.json()

def get_suspended_ips():
    result = crm_connector("clients/services?statuses%5B%5D=3")
    suspended_sites = []
    suspended_devices = []
    for r in result:
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
        print(commands)
    else:
        commands = ""
        commands += "source /opt/vyatta/etc/functions/script-template\n"
        commands += "configure\n"
        commands += "delete firewall group address-group SUSPENDED_IPS\n"
        commands += "set firewall group address-group SUSPENDED_IPS\n"
        commands += f"set firewall group address-group SUSPENDED_IPS address 172.16.0.254\n"
        commands += "commit\n"
        commands += "save\n"
        print(commands)
main()
