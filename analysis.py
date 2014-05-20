#!/usr/bin/env python

from xml.dom import minidom

items = ['Tritanium', 'Pyerite', 'Mexallon', 'Isogen']
systems = ['Jita', 'Rens', 'Amarr']



for item in items :

    print "+-----------------------------------------------------------------------------------------------------------------------+"
    print "|\tSystem\t|\tBuy mean\t|\tBuy 5% mean\t|\t  Mean  \t|\tSell 5% mean\t|\tSell mean\t|"
    for system in systems :

        ''' Read input '''

        xmldoc = minidom.parse('data/'+item+'/'+system+'.xml')

        ''' Parse buy and sell orders '''

        buy_orders = xmldoc.getElementsByTagName('buy_orders')[0].getElementsByTagName('order')
        sell_orders = xmldoc.getElementsByTagName('sell_orders')[0].getElementsByTagName('order')

        buy_orders_list = []
        sell_orders_list = []

        print len(sell_orders)
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
        sell_priceMean /= sell_volumeTotal

        buy_volumeTotal = 0;
        buy_priceMean  = 0;

        for order in buy_orders_list :
            ''' Filter orders that don't look serious (ie buy price way too low) '''
            if (buy_volumeTotal > 0) and (order[0] < 0.7 * buy_priceMean / buy_volumeTotal) :
                break
            buy_priceMean += order[0] * order[1]
            buy_volumeTotal += order[1]
        buy_priceMean /= buy_volumeTotal

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
        sell_priceMeanBegin /= sell_volumeBegin

        buy_ordersBegin = []
        buy_volumeBegin = 0;
        buy_priceMeanBegin = 0;

        for order in buy_orders_list :
            if (buy_volumeBegin > buy_volumeTotal * 0.05) :
                break
            buy_ordersBegin.append(order)
            buy_priceMeanBegin += order[0] * order[1]
            buy_volumeBegin += order[1]
        buy_priceMeanBegin /= buy_volumeBegin
        '''
        print "-------------"
        print " Sell orders "
        print "-------------"
        print sell_ordersBegin
        print "------------"
        print " Buy orders "
        print "------------"
        print buy_ordersBegin
        '''
        sellAndBuy_priceMean = (buy_priceMeanBegin + sell_priceMeanBegin) / 2;

        ''' Keep only 3 digits after coma '''

        buy_priceMean        = int(buy_priceMean        * 1000) / 1000.0
        buy_priceMeanBegin   = int(buy_priceMeanBegin   * 1000) / 1000.0
        sell_priceMean       = int(sell_priceMean       * 1000) / 1000.0
        sell_priceMeanBegin  = int(sell_priceMeanBegin  * 1000) / 1000.0
        sellAndBuy_priceMean = int(sellAndBuy_priceMean * 1000) / 1000.0

        relbuy_priceMean        = int((buy_priceMean        - sellAndBuy_priceMean)/sellAndBuy_priceMean * 100) / 100.0
        relbuy_priceMeanBegin   = int((buy_priceMeanBegin   - sellAndBuy_priceMean)/sellAndBuy_priceMean * 100) / 100.0
        relsell_priceMean       = int((sell_priceMean       - sellAndBuy_priceMean)/sellAndBuy_priceMean * 100) / 100.0
        relsell_priceMeanBegin  = int((sell_priceMeanBegin  - sellAndBuy_priceMean)/sellAndBuy_priceMean * 100) / 100.0
        relsellAndBuy_priceMean = int((sellAndBuy_priceMean - sellAndBuy_priceMean)/sellAndBuy_priceMean * 100) / 100.0

        print "|\t", system, "\t|\t", buy_priceMean, "\t\t|\t", buy_priceMeanBegin, "\t\t|\t", sellAndBuy_priceMean, "\t\t|\t", sell_priceMeanBegin, "\t\t|\t", sell_priceMean, "\t\t|"
    
    print "+-----------------------------------------------------------------------------------------------------------------------+"


