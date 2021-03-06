#-------------------------------------------------------------------------------
# Name:        request.py
# Purpose:     1. Double check the data request for locher, rainwise, spectrum and agtronix
# Author:      Dawei Jia
#
# Created:     12/09/2013
# Copyright:   (c) DaweiJia 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import logging
import datetime
import webapp2
import urllib2
from google.appengine.api import urlfetch


urlfetch.set_default_fetch_deadline(120)

class RequestAgtronix(webapp2.RequestHandler):
    
    station_id = [1371134670088,1371232073915,1371564676246,1371564826652,1372082127762,
                        1372085089831,1372088050015,1372436592530,1372436695136,1376510192542,
                        1376511125659,1376511254565,1376511371266,1376511520161,1376511687661,
                        1377116716521,1378835808348,1378835967650,1378836081600,1383323874602,
                        1383849429285,1389794987344,1389798278419,1389798514339,1389798711083,
                        1389798885198,1389799063221]    
    vendor_name = "Agtronix"
    def get(self):
        
        '''request data for all Ag-tronix stations'''
        
        today = datetime.datetime.today() - datetime.timedelta(days = 1)
        date_string = today.strftime("%Y%m%d")
        for id in self.__class__.station_id:
            self.response.out.write("start @ " + date_string + " id: " + str(id) + "<br />")
            url = """http://fdacswx.fawn.ifas.ufl.edu/application/data_collection/scheduled_tasks/onDemand/data_quality_tool/manager.php?command=overwrite&date=%s&vendorinitial=a&stationid=%s""" % (date_string,str(id))
            #req = urllib2.Request(url)
            #res_data = urllib2.urlopen(req)
            try:
                result = urlfetch.fetch(url)
                if result.status_code == 200:
                    logging.info("%s: update station %s succeed @ %s" % (self.__class__.vendor_name,str(id),date_string))
                else:
                    logging.error("%s: update station %s failed, error:%d @ %s" % (self.__class__.vendor_name,str(id),
                                                                                   result.status_code, date_string))                
            except Exception,exception:
                logging.error("%s: update station %s failed, error:%s @ %s" % (self.__class__.vendor_name,str(id),
                                                                              exception.message, date_string))

class RequestSpectrum(webapp2.RequestHandler):
    
    station_id = [1370037884721,1370903516170,1370904313766,1371069452397,1371069992583,1371070232061]
    vendor_name = "Spectrum"
    def get(self):
        '''request data from all Spectrum stations'''
        
        today = datetime.datetime.today() - datetime.timedelta(days = 1)
        date_string = today.strftime("%Y%m%d")
        for id in self.__class__.station_id:
            self.response.out.write("start @ " + date_string + " id: " + str(id) + "<br />")
            url = """http://fdacswx.fawn.ifas.ufl.edu/application/data_collection/scheduled_tasks/onDemand/data_quality_tool/manager.php?command=overwrite&date=%s&vendorinitial=s&stationid=%s""" % (date_string,str(id))
            #req = urllib2.Request(url)
            #res_data = urllib2.urlopen(req)
            try:
                result = urlfetch.fetch(url)
                if result.status_code == 200:
                    logging.info("%s: update station %s succeed @ %s" % (self.__class__.vendor_name,str(id),date_string))
                else:
                    logging.error("%s: update station %s failed, error:%d @ %s" % (str(self.__class__.vendor_name),
                                                                                   str(id),result.status_code),date_string)                
            except Exception,exception:
                logging.error("%s: update passstation %s failed, error:%s @ %s" % (str(self.__class__.vendor_name),
                                                                                  str(id),exception.message,date_string))   

class RequestRainwise(webapp2.RequestHandler):
    
    station_id = [1372273825011,1372273972292,1369420647569,1369420784490,1372273566294,
                      1371493004601,1371493821371,1371749589983,1371840250117,1371841699306,
                      1375364577377,1372185383365,1372185772594,1375364809900]
    vendor_name = "Rainwise"
    def get(self):
        '''request data from all Rainwise stations'''
        today = datetime.datetime.today() - datetime.timedelta(days = 1)
        date_string = today.strftime("%Y%m%d")
        for id in self.__class__.station_id:
            self.response.out.write("start @ " + date_string + " id: " + str(id) + "<br />")
            url = """http://fdacswx.fawn.ifas.ufl.edu/application/data_collection/scheduled_tasks/onDemand/data_quality_tool/manager.php?command=overwrite&date=%s&vendorinitial=r&stationid=%s""" % (date_string,str(id))
            #req = urllib2.Request(url)
            #res_data = urllib2.urlopen(req)
            try:
                result = urlfetch.fetch(url)
                if result.status_code == 200:
                    logging.info("%s: update station %s succeed @ %s" % (self.__class__.vendor_name,str(id), date_string))
                else:
                    logging.error("%s: update station %s failed, error:%s @ %s" % (self.__class__.vendor_name,str(id),
                                                                                   result.status_code, date_string))                
            except Exception,exception:
                logging.error("%s: update station %s failed, error:%s @ %s" % (self.__class__.vendor_name,str(id),
                                                                              exception.message,date_string)) 

class RequestLocher(webapp2.RequestHandler):
    
    station_id = [1372335072345,1371202552366,1371210336426,1372022219640,1372022572473,
                  1372023141695,1372023496375,1372023852704,1372027804042,1372248723090,
                  1372337438126,1372337775808,1372421223108,1372423160665,1372423662094,
                  1372423894859,1372424134839,1372019019889,
                  ##correct stations
                1372029613044,1372030897754,1372068598427,1372247203006,1372247484014,
                1372248227202,1372249047973,1372249709837,1372334729510,1372335458906,
                1372335765423,1372336007966,1372336223477,1372336547238,1372336894807,
                1371209381707,1372338552887,1372420047622,1372337178194,1372338216652,
                1371206268000,1371212307167,1372018181998,1372019765172]
    no_response_station_id = [1372249368331,1372247774219,1372338874288,1372068297257,1372020950229]
    vendor_name = "Locher"
    
    def get(self):
        '''request data from all Locher stations'''
        today = datetime.datetime.today() - datetime.timedelta(days = 1)
        date_string = today.strftime("%Y%m%d")
        for id in self.__class__.station_id:
            self.response.out.write("start @ " + date_string + " id: " + str(id) + "<br />")
            url = """http://fdacswx.fawn.ifas.ufl.edu/application/data_collection/scheduled_tasks/onDemand/data_quality_tool/manager.php?command=overwrite&date=%s&vendorinitial=l&stationid=%s""" % (date_string,str(id))
            req = urllib2.Request(url)
            try:
                response = urllib2.urlopen(req)
                data = response.read()
                logging.info(data)
                logging.info("%s: update station %s succeed @ %s" % (self.__class__.vendor_name,str(id), date_string))
                
            except Exception,e:
                logging.error("%s: update station %s failed, error:%s @ %s" % (self.__class__.vendor_name,str(id),
                                                                                              e.message,date_string))                 
           
application = webapp2.WSGIApplication(
				     [('/request/agtronix', RequestAgtronix),
				      ('/request/spectrum', RequestSpectrum),
				      ('/request/rainwise', RequestRainwise),
				      ('/request/locher', RequestLocher)
				     ], debug = True)
