import re
import requests 
from bs4 import BeautifulSoup

def parse_ip(a): 
    matches = re.findall(r"((\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(?=[^\d])\s*:?\s*(\d{2,5}))", a) 
    return [x[0] for x in matches] 

def parse_spysone(text):
    v1 = text.split("ago)")
    v2 = [x.strip().split('\t') for x in v1 if x]
    v3 = [x[0] for x in v2 if x[1]!='HTTPS']
    return v3

def eval_operation(base_js_content, js_op):

    js_vars = [x for x in base_js_content.split(";") if x]
    for math in js_vars:
        varname = math.split("=")[0]
        varval = math.split("=")[1]
        query2 = math
        exec("{}={}".format(varname, varval))
    
    # JS_OPERATION PROCESS
    js_op_cleaned = js_op.replace("document.write(\"<font class=spy2>:<\/font>\"", "")[:-1]
    current_port = ""
    op_split = [x for x in js_op_cleaned.split("+") if x]
    for char_math in op_split:
        (p1, p2) = char_math[1:-1].split("^")
        current_port += str(locals()[p1]^locals()[p2])
    # print("CURRENT PORT : ", current_port)
    return current_port

def get_spysone_proxies():
    default500recent = {"xpp":"5","xf1":"0","xf2":"2","xf4":"0","xf5":"1"} #DEFAULT 500 proxies
    kr_proxies = {"xx0": "9d7ef888c7aa805ecdbab71dffc5e5e6", "xpp": "5", "xf1": "0", "xf2": "0", "xf4": "0", "xf5": "1"}
    vn_proxies = {"xx0": "c051f8637a69c39fc66fe4fa76a4d5e7", "xpp": "5", "xf1": "0", "xf2": "0", "xf4": "0", "xf5": "1"}
    br_proxies = {"xx0": "a417a0a32e8b01002e279288992fa52f", "xpp": "5", "xf1": "0", "xf2": "0", "xf4": "0", "xf5": "1"}
    de_proxies = {"xx0": "bca1264b61d3e65d05cb62bee3a36188", "xpp": "5", "xf1": "0", "xf2": "0", "xf4": "0", "xf5": "1"}
    us_proxies = {"xx0": "191716f9d0386b439de97a93f16570e0", "xpp": "5", "xf1": "0", "xf2": "0", "xf4": "0", "xf5": "1"}
    indo = {"xx0": "094061f8cb02463e2a93945561104afd", "xpp": "5", "xf1": "0", "xf2": "0", "xf4": "0", "xf5": "1"}
    ru_proxies = {"xx0": "08c03d59771ef8dce9ffcf05b27c5026", "xpp": "5", "xf1": "0", "xf2": "0", "xf4": "0", "xf5": "1"}
    ukraine = {"xx0": "baacc1b703c9e8a40122a926648bfe40", "xpp": "5", "xf1": "0", "xf2": "0", "xf4": "0", "xf5": "1"}
    thailand = {"xx0": "50783c5d482ee3fdc2d0e88b5a1cdbd8", "xpp": "5", "xf1": "0", "xf2": "0", "xf4": "0", "xf5": "1"}
    proxies = []
    for post_data in [default500recent, kr_proxies, vn_proxies, br_proxies, de_proxies, us_proxies, indo, ru_proxies, ukraine, thailand]:
        proxies.extend(_get_spysone_proxies(post_data))
    return proxies


def _get_spysone_proxies(postdata):
    data = postdata

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:68.0) Gecko/20100101 Firefox/68.0', 'Referer': 'http://spys.one/en/free-proxy-list/', 'Origin': 'http://spys.one'}
    r = requests.post("http://spys.one/en/free-proxy-list/", data=data, headers=headers)
    soup = BeautifulSoup(r.text, 'lxml')
    base_script = soup.find(lambda tag: tag.name=='script' and 'google' not in str(tag).lower())

    results = []

    rows = soup.find_all(lambda tag: tag.name=='font' and '<font class=spy2>' in str(tag))
    for row in rows:
        row_ip = re.findall(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", str(row))[0]
        row_port = eval_operation(base_script.decode_contents(), row.script.decode_contents())
        results.append("{}:{}".format(row_ip, row_port))
    return results
    
    


if __name__ == "__main__":
    import json
    results = get_spysone_proxies()
    print (json.dumps(results, indent=2))
        

    # port_script = soup.find_all(lambda tag: tag.name=='script' and 'document.write("<font class=spy2>' in str(tag).lower())
    # port_operations = [x.decode_contents().replace("document.write(\"<font class=spy2>:<\/font>\"", "")[:-1] for x in port_script]
    # ports = []
    
    # for op in port_operations:
    #     current_port = ""
    #     op_split = [x for x in op.split("+") if x]
        # for char_math in op_split:
        #     exec("current_port+=str("+char_math+")")
        # ports.append(current_port)

    # ips = re.findall(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", str(soup.body))
    # for i in ips:
    #     print (i)
    # print (len(ports))
    # print (len(ips))



