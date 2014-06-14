#!/usr/bin/env python

from matplotlib import pyplot as plotting
import numpy as math
from xml.dom import minidom
import subprocess
import codecs
import time
import os


'''
items = ['Tritanium', 'Pyerite', 'Mexallon', 'Isogen', 'Nocxium', 'Zydrine', 'Megacyte', 'Heavy Water', 'Liquid Ozone', 'Helium Isotopes', 'Strontium Clathrates', 'Oxygen Isotopes', 'Nitrogen Isotopes', 'Hydrogen Isotopes']
'''
items = ['Tritanium' ]
systems = ['Jita', 'Amarr', 'Rens', 'Dodixie']


colors  = { 
            'Jita' : '#000000',
            'Amarr' : '#FFBF00', 
            'Rens' : '#FF6100', 
            'Dodixie' : '#37AEE5',
            'Oursulaert' : '#01DB55', 
           }


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
curve_priceMean = {}
curve_priceSell = {}
curve_priceBuy  = {}

curve_meanGain = {}
curve_sellGain = {}
curve_buyGain  = {}

curve_priceBuyMax   = {}
curve_priceBuyMin   = {}
curve_priceSellMax  = {}
curve_priceSellMin  = {}
curve_maxGainAllSystems  = {}
curve_minGainAllSystems  = {}
curve_meanGainAllSystems = {}

history = sorted(os.listdir("./history/"))
for item in items :
    for system in systems :
        timeAxis[item, system] = []
        curve_priceMean[item, system] = []
        curve_priceSell[item, system] = []
        curve_priceBuy [item, system] = []
        curve_meanGain[item, system] = []
        curve_sellGain[item, system] = []
        curve_buyGain [item, system] = []

        for (i, record) in enumerate(history):
            timeAxis[item, system].append(int(int(time.mktime(time.strptime(record,"%Y_%m_%d_%H:%M:%S")) - time.time()) / 864.0)/100.0)
            (p,g) = analyzeOrders(record,item,system)
            p = int(p * 100)/100.0
            g = int(g * 100)/100.0
            curve_priceMean[item, system].append(p)
            curve_priceSell[item, system].append(p+g)
            curve_priceBuy [item, system].append(p-g)
            
            curve_meanGain[item, system].append(curve_priceMean[item, system][i] / curve_priceMean[item, ref][i])
            curve_sellGain[item, system].append(curve_priceSell[item, system][i] / curve_priceMean[item, ref][i])
            curve_buyGain [item, system].append(curve_priceBuy [item, system][i] / curve_priceMean[item, ref][i])

            print item, "@", system, "on", record,  p, g

for item in items :
    curve_priceBuyMax[item]  = [] 
    curve_priceBuyMin[item]  = []
    curve_priceSellMax[item] = []
    curve_priceSellMin[item] = []
    curve_maxGainAllSystems[item]      = []
    curve_minGainAllSystems[item]      = []
    curve_meanGainAllSystems[item]     = []
        
    for (i, record) in enumerate(history):
        buyMax = -1
        buyMin = 999999999
        sellMax = -1
        sellMin = 999999999
        for system in systems :
            priceSell = curve_priceSell[item,system][i]
            priceBuy  = curve_priceBuy [item,system][i]
            if (priceSell < sellMin) :
                sellMin = priceSell
            if (priceSell > sellMax) :
                sellMax = priceSell
            if (priceBuy < buyMin) :
                buyMin = priceBuy
            if (priceBuy > buyMax) :
                buyMax = priceBuy

        ''' Apply taxes '''
        
        ''' direct sale, 1.5% fees => 1.5% less profit '''
        buyMax = buyMax * (1 - 0.015)  
        ''' buy order, 0.9% fees => 0.9% higher price '''
        buyMin = buyMin * (1 + 0.009)  
        ''' sell order, 1.5+0.5M fees => 2% less profit '''
        sellMax = sellMax * (1 - 0.020) 
        ''' direct buy, no tax '''
        sellMin = sellMin              
        curve_priceBuyMax[item].append(buyMax)
        curve_priceBuyMin[item].append(buyMin)
        curve_priceSellMax[item].append(sellMax)
        curve_priceSellMin[item].append(sellMin)
        curve_maxGainAllSystems[item].append(sellMax / buyMin - 1)
        curve_minGainAllSystems[item].append(buyMax / sellMin - 1)
        curve_meanGainAllSystems[item].append(((buyMax / sellMin - 1) + (sellMax / buyMin - 1)) / 2)

    



for item in items :
    fig = plotting.figure()
    fig.suptitle(item, fontsize = 20)
    
    refPrice = fig.add_subplot(3, 1, 1)
    refPrice.plot(timeAxis[item, ref], curve_priceMean[item, ref], 'yo-', color=colors[ref], linewidth=1.5)
    refPrice.fill_between(timeAxis[item, ref], curve_priceSell[item, ref], curve_priceBuy[item, ref], alpha=0.1, edgecolor=colors[ref], facecolor=colors[ref])
    refPrice.set_ylabel(ref+' price')
    refPrice.grid(True)

    relPrices = fig.add_subplot(3, 1, 2, sharex=refPrice)
    for system in systems :
        relPrices.set_ylabel('Relative prices')
        relPrices.plot(timeAxis[item, system], curve_meanGain[item, system], 'r-', color=colors[system], linewidth=1.5)
        relPrices.fill_between(timeAxis[item, system], curve_sellGain[item, system], curve_buyGain[item, system], alpha=0.2, edgecolor=colors[system], facecolor=colors[system])
        relPrices.grid(True)
    
    profit = fig.add_subplot(3, 1, 3, sharex=refPrice)
    profit.set_ylabel('Best profit margin')
    profit.plot(timeAxis[item, system], curve_meanGainAllSystems[item], 'yo-', color=colors[ref], linewidth=1.5)
    profit.fill_between(timeAxis[item, system], curve_maxGainAllSystems[item], curve_minGainAllSystems[item], alpha=0.1, edgecolor=colors[ref], facecolor=colors[ref])
    profit.grid(True)

    plotting.setp(refPrice.get_xticklabels(), visible=False)
    plotting.setp(relPrices.get_xticklabels(), visible=False)

    plotting.savefig(item+'.png', bbox_inches='tight', dpi = 200)
