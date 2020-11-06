#!/bin/python3
'''
FIAP 1TDCA - Optimization for Security
30 de Outubro de 2020

Eduardo Marchini Haddad 85884
Rodrigo Munhoz Ramos 84680
Giovanna Sayuri Costa Antunes 86036
Mateus Farias Ferreira 84559
Vitor Miguel Lasse Silva 84889

Validado em Ubuntu Server 20.04 LTS e Windows 10
Versão 2
'''

import requests
import json
from pymongo import MongoClient

try:
    input_func = raw_input
except:
    input_func = input

def menu():
    print('''
-------------------------------------
              Main Menu
-------------------------------------
(1)  List Containers
(2)  Show Container Stats
(3)  Stream Container Stats
(4)  Start Container
(5)  Stop Container
(6)  Create Container
(7)  Delete Container
(8)  Delete ALL Containers
(9)  List Images    
(10) Pull Image
(11) Delete Image
(12) Delete ALL Images
(13) Quit
-------------------------------------
''')

def paramenu():
    print('''
-------------------------------------
           Parameters Menu
-------------------------------------
(1) read
(2) cpu_stats
(3) memory_stats   
(4) id
(5) name
(6) networks
(7) pids_stats    
(8) Raw json
(9) Back to main menu
-------------------------------------
''')

def verify_error(response, code, show_error=True):
    if response.status_code == code:
        if show_error:
            print('Command OK')
            return True
        if show_error:
            print('ERROR: %d' % response.status_code)
            return False

def mongo_insert(cont, rjson):
    uri = "mongodb+srv://DRA:potato@cluster0.yx7hj.mongodb.net/test"
    client = MongoClient(uri)
    db = client.stats_db
    db[cont].insert_one(rjson)

def get_containers_stats(ipaddr, show=True):
    cont = input_func('Insert the Container UID: ')
    ret = requests.get('%s/containers/%s/stats?stream=0' % (ipaddr, cont))
    if verify_error(ret, 200):
        if show:
            rjson = json.loads(ret.text.encode("utf8"))
            try:
                mongo_insert(cont, rjson)
            except:
                print('Error connecting to MongoDB.')
            while True:
                try:
                    try:
                        a = "read: "+str(rjson["read"])
                        b = "total_usage: "+str(rjson["cpu_stats"]["cpu_usage"]["total_usage"])
                        c = "online_cpus: "+str(rjson["cpu_stats"]["online_cpus"])
                        d = "usage: "+str(rjson["memory_stats"]["usage"])
                        e = "max_usage: "+str(rjson["memory_stats"]["max_usage"])
                        f = "id: "+str(rjson["id"])
                        g = "name: "+str(rjson["name"])
                        h = "tx_bytes: "+str(rjson["networks"]["eth0"]["tx_bytes"])
                        j = "tx_packets: "+str(rjson["networks"]["eth0"]["tx_packets"])
                        k = "tx_errors: "+str(rjson["networks"]["eth0"]["tx_errors"])
                        m = "tx_dropped: "+str(rjson["networks"]["eth0"]["tx_dropped"])
                        n = "rx_bytes: "+str(rjson["networks"]["eth0"]["rx_bytes"])
                        o = "rx_packets: "+str(rjson["networks"]["eth0"]["rx_packets"])
                        p = "rx_errors: "+str(rjson["networks"]["eth0"]["rx_errors"])
                        q = "rx_dropped: "+str(rjson["networks"]["eth0"]["rx_dropped"])
                        r = "pids_stats: "+str(rjson["pids_stats"]["current"])
                    except:
                        print("Error generating parameters")
                        break
                    paramenu()
                    opt = input_func('Choice: ')
                    if opt == '1':
                        print(a)
                    elif opt == '2':
                        print('cpu_stats')
                        print(b)                        
                        print(c)           
                    elif opt == '3':
                        print('memory_stats')
                        print(d)
                        print(e)
                    elif opt == '4':
                        print(f)  
                    elif opt == '5':
                        print(g)
                    elif opt == '6':
                        print('networks')
                        print(h)
                        print(j)
                        print(k)
                        print(m)
                        print(n)
                        print(o)
                        print(p)
                        print(q)  
                    elif opt == '7':
                        print(r)
                    elif opt == '8':
                        print(rjson)
                    elif opt == '9':
                        break 
                    else:
                        print("Error! Number out of range.")
                except KeyboardInterrupt:
                    break
        else:
            return ret.json()

def stream_container_stats(ipaddr, show=True):
    cont = input_func('Insert the Container UID: ')
    ret = requests.get('%s/containers/%s/stats?stream=1' % (ipaddr, cont), stream=True)
    if verify_error(ret, 200):
        while True:
            try:
                if show:
                    for line in ret.iter_lines():
                        rjson = json.loads(line)
                        print(rjson)
                        try:
                            mongo_insert(cont, rjson)
                            print('\nData is being streamed and uploaded to MongoDB. Press Ctrl-C to return to Main Menu.\n')
                        except KeyboardInterrupt:
                            break
                        except:
                            print('\nError connecting to MongoDB. Press Ctrl-C to return to Main Menu.\n')
            except:
                break
    else:
        return ret.json()

def get_containers(ipaddr, show=True):
    ret = requests.get('%s/containers/json?all=1' % ipaddr)
    if verify_error(ret, 200):
        if show:
            for i in ret.json():
                print("\nContainer: "+str(i["Names"]).strip("['/").strip("']")+"\nState: "+str(i["State"]).strip("['/").strip("']"))
                print(i)
        else:
            return ret.json()

def delete_container(ipaddr, uid=None):
    if uid:
        cont = uid
    else:
        cont = input_func('Insert the Container UID: ')
        ret = requests.delete('%s/containers/%s' % (ipaddr, cont))
        return verify_error(ret, 204)

def start_container(ipaddr, uid=None):
    cont = input_func('Insert the Container UID: ')
    ret = requests.post('%s/containers/%s/start' % (ipaddr, cont))
    return verify_error(ret, 204)

def stop_container(ipaddr, uid=None):
    cont = input_func('Insert the Container UID: ')
    ret = requests.post('%s/containers/%s/stop?t=1' % (ipaddr, cont))
    return verify_error(ret, 204)

def create_container(ipaddr):
    cont_name = input_func('Insert Container name: ')
    image = input_func('Insert Image:Tag name: ')
    entry = input_func('Insert Entrypoint: ')
    payload = {'Image': image, 'Entrypoint': entry}
    ret = requests.post('%s/containers/create?name=%s' % (ipaddr, cont_name), json=payload)
    verify_error(ret, 201)

def delete_all_containers(ipaddr):
    lst = get_containers(ipaddr, False)
    for i in lst:
        delete_container(ipaddr, i['Id'])

def get_images(ipaddr, show=True):
    ret = requests.get('%s/images/json?all=0' % ipaddr)
    if verify_error(ret, 200):
        if show:
            for i in ret.json():
                print(i)
                print('')
        else:
            return ret.json()

def create_image(ipaddr):
    name = input_func('Insert the Image name: ')
    tag = input_func('Insert Tag name: ')
    if not name.strip() or not tag.strip():
        print('A name and a tag needs to be informed.')
        return
    print('Pulling image...')
    ret = requests.post('%s/images/create?fromImage=%s&tag=%s' % (ipaddr, name, tag))
    verify_error(ret, 200)

def delete_image(ipaddr, iname=None):
    if iname:
        name = iname
    else:
        name = input_func('Insert the Image:Tag name to be removed: ')
    ret = requests.delete('%s/images/%s' % (ipaddr, name))
    verify_error(ret, 200)

def delete_all_images(ipaddr):
    lst = get_images(ipaddr, False)
    for i in lst:
        delete_image(ipaddr, i['RepoTags'][0])

print('''
-------------------------------------
            Docker Manager
-------------------------------------
''')
ip = input_func('Insert target IP address: ')
port = input_func('Insert target port: ')
ipaddr = 'http://%s:%s' % (ip, port)
while True:
    try:
        menu()
        opt = input_func('Choice: ')
        if opt == '1':
            get_containers(ipaddr)
        elif opt == '2':
            get_containers_stats(ipaddr)
        elif opt == '3':
            stream_container_stats(ipaddr)
        elif opt == '4':
            start_container(ipaddr)
        elif opt == '5':
            stop_container(ipaddr)
        elif opt == '6':
            create_container(ipaddr)
        elif opt == '7':
            delete_container(ipaddr)
        elif opt == '8':
            delete_all_containers(ipaddr)
        elif opt == '9':
            get_images(ipaddr)
        elif opt == '10':
            create_image(ipaddr)
        elif opt == '11':
            delete_image(ipaddr)
        elif opt == '12':
            delete_all_images(ipaddr)
        elif opt == '13':
            break
        else:
            print("Error! Number out of range.")
    except KeyboardInterrupt:
        break
print('\nBye!\n')