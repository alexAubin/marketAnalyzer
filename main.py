#!/usr/bin/env python

from matplotlib import pyplot as plotting
import numpy as math
from xml.dom import minidom
import subprocess
import codecs
import time
import os


items = ['Tritanium', 'Pyerite', 'Mexallon', 'Isogen', 'Nocxium', 'Zydrine', 'Megacyte', 'Heavy Water', 'Liquid Ozone', 'Helium Isotopes', 'Strontium Clathrates', 'Oxygen Isotopes', 'Nitrogen Isotopes', 'Hydrogen Isotopes']
systems = ['Jita', 'Amarr', 'Rens', 'Dodixie']
colors  = { 'Jita' : '#000000',
            'Amarr' : '#FFBF00', 
            'Rens' : '#FF6100', 
            'Dodixie' : '#37AEE5',
           }
'''            
            'Oursulaert' : '#01DB55', 
'''

'''
items = ['Tritanium', 'Pyerite', 'Mexallon', 'Isogen', 'Nocxium', 'Zydrine', 'Megacyte', 'Heavy Water', 'Liquid Ozone', 'Helium Isotopes', 'Strontium Clathrates', 'Oxygen Isotopes', 'Nitrogen Isotopes', 'Hydrogen Isotopes']
systems = ['Jita', 'Amarr', 'Rens', 'Oursulaert', 'Dodixie']
'''
def analyzeOrders(date, item, system) :

    ''' Read input '''

    xmldoc = minidom.parse('history/'+date+'/'+item+'/'+system+'.xml')

    ''' Parse buy and sell orders '''

    buy_orders = xmldoc.getElementsByTagName('buy_orders')[0].getElementsByTagName('order')
    sell_orders = xmldoc.getElementsByTagName('sell_orders')[0].getElementsByTagName('order')

    buy_orders_list = []
    sell_orders_list = []

    for order in sell_orders :
        ''' Filter low-sec systems '''
        if (float(order.getElementsByTagName("security")[0].childNodes[0].nodeValue) < 0.5) :
            continue
        sell_orders_list.append((float(order.getElementsByTagName("price")[0].childNodes[0].nodeValue), int(order.getElementsByTagName("vol_remain")[0].childNodes[0].nodeValue)))

    for order in buy_orders :
        ''' Filter low-sec systems '''
        if (float(order.getElementsByTagName("security")[0].childNodes[0].nodeValue) < 0.5) :
            continue
        buy_orders_list.append((float(order.getElementsByTagName("price")[0].childNodes[0].nodeValue), int(order.getElementsByTagName("vol_remain")[0].childNodes[0].nodeValue)))

    ''' Sort the orders according to prices '''
    
    sell_orders_list = sorted(sell_orders_list, key=lambda order: order[0])
    buy_orders_list = sorted(buy_orders_list, key=lambda order: order[0], reverse=True)
    
    ''' Compute mean price and total volume '''

    sell_volumeTotal = 0;
    sell_priceMean = 0;

    for order in sell_orders_list :
        ''' Filter orders that don't look serious (ie sell price way too high) '''
        if (sell_volumeTotal > 0) and (order[0] > 3 * sell_priceMean / sell_volumeTotal) :
            break
        sell_priceMean += order[0] * order[1]
        sell_volumeTotal += order[1]
    
    if (sell_volumeTotal != 0) :
        sell_priceMean /= sell_volumeTotal
    else :
        sell_priceMean = 0;

    buy_volumeTotal = 0;
    buy_priceMean  = 0;

    for order in buy_orders_list :
        ''' Filter orders that don't look serious (ie buy price way too low) '''
        if (buy_volumeTotal > 0) and (order[0] < 0.7 * buy_priceMean / buy_volumeTotal) :
            break
        buy_priceMean += order[0] * order[1]
        buy_volumeTotal += order[1]
    buy_priceMean /= buy_volumeTotal

    if (buy_volumeTotal != 0) :
        buy_priceMean /= buy_volumeTotal
    else :
        buy_priceMean = 0;

    ''' Compute mean for the first 5% of the distribution '''

    sell_ordersBegin = []
    sell_volumeBegin = 0;
    sell_priceMeanBegin = 0;

    for order in sell_orders_list :
        if (sell_volumeBegin > sell_volumeTotal * 0.05) :
            break
        sell_ordersBegin.append(order)
        sell_priceMeanBegin += order[0] * order[1]
        sell_volumeBegin += order[1]
    
    if (sell_volumeBegin != 0) :
        sell_priceMeanBegin /= sell_volumeBegin
    else :
        sell_priceMeanBegin = 0
    
    buy_ordersBegin = []
    buy_volumeBegin = 0;
    buy_priceMeanBegin = 0;

    for order in buy_orders_list :
        if (buy_volumeBegin > buy_volumeTotal * 0.05) :
            break
        buy_ordersBegin.append(order)
        buy_priceMeanBegin += order[0] * order[1]
        buy_volumeBegin += order[1]

    if (buy_volumeBegin != 0) :
        buy_priceMeanBegin /= buy_volumeBegin
    else :
        buy_priceMeanBegin = 0
    
    ''' Compute mean '''

    if (buy_priceMeanBegin == 0) :
        buy_priceMeanBegin = sell_priceMeanBegin;
    if (sell_priceMeanBegin == 0) :
        sell_priceMeanBegin = buy_priceMeanBegin;

    priceMean = (buy_priceMeanBegin + sell_priceMeanBegin) / 2;
    priceGap  = abs((buy_priceMeanBegin - sell_priceMeanBegin)) / 2;

    return (priceMean, priceGap)


def fetchNewData(itemsList, systemsList) :
    p = subprocess.Popen(["mkdir", "-p", "history/"])
    p.wait()

    ''' Read items ID '''
    itemsID = {}
    with codecs.open("info/items.list", 'r', "utf-8-sig") as f:
        for line in f:
           (val, key) = line.split(':')
           itemsID[key.split('\n')[0]] = val

    ''' Read systems ID '''
    systemsID = {}
    with codecs.open("info/systems.list", 'r', "utf-8-sig") as f:
        for line in f:
           (val, key) = line.split(':')
           systemsID[key.split('\n')[0]] = val

    ''' Fetch data '''
    for item in itemsList :
        for system in systemsList :

            url="http://api.eve-central.com/api/quicklook?typeid="+itemsID[item]+"&usesystem="+systemsID[system]+"&setminQ=10000"

            p = subprocess.Popen(["mkdir", "-p", "data/"+item+"/"])
            p.wait()
            p = subprocess.Popen(["wget", "--no-verbose", "-O", "data/"+item+"/"+system+".xml", url])
            p.wait()

    date = time.strftime("%Y_%m_%d_%H:%M:%S")
    p = subprocess.Popen(["mv", "data", "history/"+date])
    p.wait()


'''
fetchNewData(items, systems)
'''

plotting.clf()
plotting.hold(1)

ref = systems[0]
timeAxis = {}
priceCurve_mean = {}
priceCurve_sell = {}
priceCurve_buy  = {}

priceCurve_meanGain = {}
priceCurve_sellGain = {}
priceCurve_buyGain  = {}

history = sorted(os.listdir("./history/"))
for item in items :
    for system in systems :
        timeAxis[item, system] = []
        priceCurve_mean[item, system] = []
        priceCurve_sell[item, system] = []
        priceCurve_buy [item, system] = []
        priceCurve_meanGain[item, system] = []
        priceCurve_sellGain[item, system] = []
        priceCurve_buyGain [item, system] = []

        for (i, record) in enumerate(history):
            timeAxis[item, system].append(int(int(time.mktime(time.strptime(record,"%Y_%m_%d_%H:%M:%S")) - time.time()) / 864.0)/100.0)
            (p,g) = analyzeOrders(record,item,system)
            p = int(p * 100)/100.0
            g = int(g * 100)/100.0
            priceCurve_mean[item, system].append(p)
            priceCurve_sell[item, system].append(p+g)
            priceCurve_buy [item, system].append(p-g)
            
            priceCurve_meanGain[item, system].append(priceCurve_mean[item, system][i] / priceCurve_mean[item, ref][i])
            priceCurve_sellGain[item, system].append(priceCurve_sell[item, system][i] / priceCurve_mean[item, ref][i])
            priceCurve_buyGain [item, system].append(priceCurve_buy [item, system][i] / priceCurve_mean[item, ref][i])

            print item, "@", system, "on", record,  p, g
        '''
        plotting.plot(timeAxis[item, system], priceCurve_mean[item, system], 'k', color=colors[system], linewidth=2.5)
        plotting.fill_between(timeAxis[item, system], priceCurve_sell[item, system], priceCurve_buy[item, system], alpha=0.2, edgecolor=colors[system], facecolor=colors[system])
        print timeAxis
        print priceMean
        '''

for item in items :
    plotting.figure()
    plotting.subplot(2, 1, 1)
    plotting.plot(timeAxis[item, ref], priceCurve_mean[item, ref], 'yo-', color=colors[ref], linewidth=1.5)
    plotting.fill_between(timeAxis[item, ref], priceCurve_sell[item, ref], priceCurve_buy[item, ref], alpha=0.1, edgecolor=colors[ref], facecolor=colors[ref])
    plotting.ylabel(ref+' price')
    axes = plotting.gca()
    axes.grid(True)

    plotting.subplot(2, 1, 2)
    for system in systems :
        plotting.ylabel('Profit margin')
        plotting.plot(timeAxis[item, system], priceCurve_meanGain[item, system], 'r-', color=colors[system], linewidth=1.5)
        plotting.fill_between(timeAxis[item, system], priceCurve_sellGain[item, system], priceCurve_buyGain[item, system], alpha=0.2, edgecolor=colors[system], facecolor=colors[system])
        axes = plotting.gca()
        axes.grid(True)
    
    plotting.savefig(item+'.png', bbox_inches='tight')
