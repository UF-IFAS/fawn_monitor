#-------------------------------------------------------------------------------
# Name:        monitor.py
# Purpose:     1. check availbility http://fawn.ifas.ufl.edu/controller.php/latestmapjson/
#              2. check data timeliness for 42 fawn stations fawn-monitor.appspot.com
#              3. check availbility  http://fdacswx.fawn.ifas.ufl.edu/index.php/read/latestobz/format/json
# Author:      Dawei Jia
#
# Created:     12/09/2013
# Copyright:   (c) DaweiJia 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import logging
import json
import datetime
import database

from monitor_helper import MonitorHelper
from google.appengine.api import users
#from google.appengine.ext import webapp
from google.appengine.api import urlfetch
from google.appengine.api import mail
from google.appengine.ext import db
import webapp2

class FawnMonitor(webapp2.RequestHandler):
    '''monitor data availability and timeliness '''
    url = "http://fawn.ifas.ufl.edu/controller.php/latestmapjson/"
    stnIDList = ['260','240','241','110','280','330','450','380','311','360',
               '435','170','150','455','480','410','130','250','390','302',
               '121','304','303','230','371','270','290','320','350','460',
               '275','180','405','440','470','340','160','490','120','420',
               '140','425']
    emailList = ["jiadw007@gmail.com","lstaudt@ufl.edu","rlusher@ufl.edu","gbraun@ufl.edu","tiejiazhao@gmail.com","ohyeahfanfan@gmail.com"]
    record_time_delta = datetime.timedelta(hours = 4)
    fawnStn_time_delta = datetime.timedelta(hours = 1)
    no_update_time_delta = datetime.timedelta(hours = 2)
    def get(self,retries = 3):

        '''response request method = get'''
        MonitorHelper.checkStatusCode(self)

    def getInfo(self,result):
        '''get fawn station information'''
        decoded = MonitorHelper.parseJson(self,result)
        logging.info("Getting fawn time...")
        self.response.out.write("Getting fawn time...<br />")
        #fawn time
        alert_time = datetime.datetime.strptime(decoded['fawnTime'][:-4],'%A %B %d, %Y %I:%M %p')
        season = str(decoded['fawnTime'][-3:])
        fawnData=[]
        self.response.out.write("fawnTime: " + str(alert_time) + "  " + season)
        #build fawn station time list
        for data in decoded['stnsWxData']:
            self.response.out.write("<br />")
            fawnStn_time = datetime.datetime.strptime(data['dateTimes'][:-4],'%m/%d/%Y %I:%M %p')
            data_list = []
            data_list.append(data['stnID'])
            if data['dateTimes'][-3:] =='CST' or data['dateTimes'][-3:] =='CDT':
                data_list.append(fawnStn_time + self.__class__.fawnStn_time_delta)
                self.response.out.write(str(data['stnID']) +": "+ \
                str(fawnStn_time + self.__class__.fawnStn_time_delta) + "  " + season)
            else:
                data_list.append(fawnStn_time)
                self.response.out.write(str(data['stnID']) +": "+str(fawnStn_time) + "  " + season)
            fawnData.append(data_list)
        logging.info("Getting stnID...")
        self.response.out.write("<br />Getting fawn stnID...<br />")
        #build no update list
        no_update_list = [data for data in fawnData if alert_time - data[1] > self.__class__.no_update_time_delta]
        logging.info("Getting no update stnID...")
        self.response.out.write(len(no_update_list))
        self.response.out.write("<br />Getting no update stnID...<br />")
        #report no update stations
        if len(no_update_list) != 0:

            logging.info("number of no update stn ID is: %d", len(no_update_list))
            missingInformation ="""
            number of no update stn ID is %d<br />
            """ % len(no_update_list)
            self.response.out.write(missingInformation)
            subject = "FAWN ALERT NO UPDATE @ " + str(alert_time)
            #build email content
            html = MonitorHelper.buildEmailContent(self,no_update_list,season)
            self.response.out.write(html)
            #query last record in the database
            q = db.GqlQuery("SELECT * FROM Record \
                             WHERE error_code = '200'\
                             ORDER BY record_time DESC")
            queryResult = q.get()
            message = ",".join([data[0] for data in no_update_list])
            message_time = ",".join([str(data[1]) for data in no_update_list])
            self.response.out.write("Check last record in the database<br/>")
            if queryResult is None or message_time not in queryResult.error_time or message not in queryResult.error_details :

                record = database.Record(error_code = str(result.status_code),error_details = message)
                MonitorHelper.updateRecord(self, record, alert_time,message_time)
                MonitorHelper.emailInfo(self.__class__.emailList,self,subject,html)
        else:
            MonitorHelper.allGoodInfo(self)


class FdacsMonitor(webapp2.RequestHandler):
    '''Fdacs Monitor'''
    default_emailList =["uffawn@gmail.com"]
    url = "http://fdacswx.fawn.ifas.ufl.edu/index.php/read/latestobz/format/json"
    vendor_url = "http://fdacswx.fawn.ifas.ufl.edu/index.php/read/station/format/json"
    record_time_delta = datetime.timedelta(hours = 4)
    emailList=[]
    def get(self,retries = 3):

        '''response request method = get'''
        MonitorHelper.checkStatusCode(self)

    def getInfo(self,result):

        '''get Fdacs station infomation'''
        #parse json
        decoded = MonitorHelper.parseJson(self,result)
        logging.info("Getting fresh status")
        self.response.out.write("Getting fresh status...<br />")
        total_stns_num = len(decoded)
        self.response.out.write("There are total %d stations.<br />" % total_stns_num)
        #fresh status
        fresh_false_list = [data for data in decoded if data['fresh'] == False]
        false_stns_num = len(fresh_false_list)
        self.response.out.write("There are %d false fresh status stations.<br />" % false_stns_num)
        #report no update stations
        if false_stns_num != 0:
            alert_time = datetime.datetime.now() - self.__class__.record_time_delta
            subject = "FDACS %d ALERT NO UPDATE @ %s" %(false_stns_num, str(alert_time)[:-7])
            self.response.out.write(subject + "<br />")
            #set email list
            if false_stns_num >= total_stns_num / 2:
                self.__class__.emailList = self.__class__.default_emailList[:]
                self.__class__.emailList.append("tiejiazhao@gmail.com")
            else:
                self.__class__.emailList = self.__class__.default_emailList[:]

            vendor_lists= json.loads(urlfetch.fetch(self.__class__.vendor_url).content)
            vendor_dict = {}
            for vendor in vendor_lists:
                vendor_dict[vendor['id']] = vendor
                ##resp.response.out.write(vendor_dict[vendor['id']])
            #build no update list
            no_update_list = []
            for data in fresh_false_list:
                data_list = []
                data_list.append(data["station_id"])
                ##resp.response.out.write(vendor_dict[data["station_id"]]['vendor_name'])
                data_list.append(data["standard_date_time"])
                data_list.append(vendor_dict[data["station_id"]]['vendor_station_id'])
                data_list.append(vendor_dict[data["station_id"]]['vendor_name'])
                data_list.append(vendor_dict[data["station_id"]]['grower_name'])
                data_list.append(vendor_dict[data["station_id"]]['vendor_email'])
                data_list.append(vendor_dict[data["station_id"]]['grower_email'])
                data_list.append(vendor_dict[data["station_id"]]['station_name'])
                logging.info(data_list)
                ##resp.response.out.write(str(data_list) + "<br />")
                no_update_list.append(data_list)
                           
            record_sql = "SELECT * FROM FdacsRecord \
                             WHERE error_code = '200'\
                             ORDER BY record_time DESC"
            logging.info(record_sql)
            record_q = db.GqlQuery(record_sql)
            #build email content
            html = MonitorHelper.buildEmailContent(self,no_update_list)
            self.response.out.write("<b>Email to: %s</b>" % ",".join(self.__class__.emailList))
            self.response.out.write(html)
            #query last record in the database
            queryResult = record_q.get()
            message = ",".join([data[0] for data in no_update_list])
            message_time = ",".join([data[1] for data in no_update_list])
            self.response.out.write("Check last record in the database<br/>")
            if queryResult is None or message_time not in queryResult.error_time or message not in queryResult.error_details :

                record = database.FdacsRecord(error_code = str(result.status_code),error_details = message)
                MonitorHelper.updateRecord(self, record, alert_time,message_time)
                #MonitorHelper.emailErrorInfo(self.__class__.emailList,self,subject,html)

        else:
            #all stations are good
            MonitorHelper.allGoodInfo(self)


class FdacsRoutineEmail(webapp2.RequestHandler):
    
    default_email_list = ["conserv@ufl.edu","Camilo.Gaitan@freshfromflorida.com","sbishop@highlandsswcd.org","rlusher@ufl.edu"]
    url = "http://fdacswx.fawn.ifas.ufl.edu/index.php/read/latestobz/format/json"
    vendor_url = "http://fdacswx.fawn.ifas.ufl.edu/index.php/read/station/format/json"
    record_time_delta = datetime.timedelta(hours = 4)
    #email_time_delta = datetime.timedelta(hours = 1)
    
    """Fdacs routine email handler"""
    def get(self,retries = 3):

        '''response request method = get'''
        MonitorHelper.checkStatusCode(self)

    def getInfo(self,result):

        '''get Fdacs station information'''
        #parse json
        decoded = MonitorHelper.parseJson(self,result)
        logging.info("Getting fresh status")
        total_stns_num = len(decoded)
        logging.info("There are total %d stations.<br />" % total_stns_num)
        #fresh status
        fresh_false_list = [data for data in decoded if data['fresh'] == False]
        fresh_true_list = [data for data in decoded if data['fresh'] == True]
        false_stns_num = len(fresh_false_list)
        logging.info("There are %d false fresh status stations.<br />" % false_stns_num)
        #report no update stations
        if false_stns_num != 0:
            alert_time = datetime.datetime.now() - self.__class__.record_time_delta
            #subject = "Weather Station Notification @ %s" %(str(alert_time)[:-7])
            #logging.info(subject + "<br />")
            #set email list
            ##if false_stns_num >= total_stns_num / 2:
               ## self.__class__.email_liconserv@ufl.edust.apeend("tiejiazhao@gmail.com")
            vendor_lists= json.loads(urlfetch.fetch(self.__class__.vendor_url).content)
            vendor_dict = {}
            for vendor in vendor_lists:
                vendor_dict[vendor['id']] = vendor
                ##resp.response.out.write(vendor_dict[vendor['id']])
            #build no update list
            no_update_list = MonitorHelper.buildInfoList(fresh_false_list, vendor_dict)
            #build fawn email content and insert record into fdacs record database
            record_sql = "SELECT * FROM FdacsRecord \
                          WHERE error_code = '200'\
                          ORDER BY record_time DESC"
            logging.info(record_sql)
            record_q = db.GqlQuery(record_sql)
                            
            #query last 4 recordsin the database
            records_lists=[]
            for q_result in record_q.run(limit = 4):
                if q_result is not None :
                    records_lists.append(q_result.error_details)
            message = ",".join([data[0] for data in no_update_list])
            message_time = ",".join([data[7] for data in no_update_list])
            self.response.out.write("Check last record in the database<br/>")
            
            #find four consecutive observations for stations
            no_update_filter_list = []
            if len(records_lists) == 4:
                for data in no_update_list:
                    put_in = True
                    for record in records_lists:
                        if data[0] not in record:
                            put_in = False
                            break
                    if put_in :
                        no_update_filter_list.append(data)
            self.response.out.write("<h4>Four Consecutive Alert Obeservations List</h4>")
            self.response.out.write([data[0] for data in no_update_filter_list])
            no_update_email_list=[]
            #filter no update list
            email_record_id_list = [obj.station_id for obj in database.EmailRecord.all()]
            for data in no_update_filter_list:
                if data[0] in email_record_id_list:
                    record = database.EmailRecord.all().filter("station_id", data[0]).get()
                    if record.latest_email is not True:
                        no_update_email_list.append(data)
                        record.email_time = alert_time
                        record.latest_email = True
                        record.put()
                else:
                    no_update_email_list.append(data)
                    record = database.EmailRecord(station_id = data[0],email_time = alert_time, latest_email = True)
                    record.put()
                        
            
            '''
            for data in no_update_filter_list: 
                #self.response.out.write("%s <br/>" % data[0])
                if data[0] in email_record_id_list:
                    record = database.EmailRecord.all().filter("station_id",data[0]).get()
                    #self.response.out.write(record.email_time)
                    ## time_delta = alert_time - record.email_time
                    #self.response.out.write("%s,  %s<br />" % (record.station_id, time_delta))
                    if alert_time -  record.email_time < self.__class__.email_time_delta:
                        pass
                    else:
                        no_update_email_list.append(data)
                        record.email_time= alert_time
                        record.latest_email = True
                        record.put()
                else:
                    no_update_email_list.append(data)
                    record = database.EmailRecord(station_id = data[0], email_time = alert_time, latest_email=True)
                    record.put()
            '''        
            self.response.out.write("<h4>Final Email Station List</h4>")
            self.response.out.write([data[0] for data in no_update_email_list])
            ##self.response.out.write(no_update_email_list)
            #update record in the database
            record = database.FdacsRecord(error_code = str(result.status_code),error_details = message)
            MonitorHelper.updateRecord(self, record, alert_time,message_time)
            #build email content and send out email 
            self.response.out.write('------------------------<h3>DATA OUTAGE EMAIL PART</h3>-------------------------')
            if len(no_update_email_list) != 0:
                for info in no_update_email_list:
                    html = MonitorHelper.buildEmailContent(self,[info])
                    self.response.out.write(html)
                    self.response.out.write("<br />")
                    #logging.info(html)
                    recipient=self.__class__.default_email_list[:]
                    
                    if info[2] == "Ag-tronix":
                        recipient.append("sonya@ag-tronix.com")
                        recipient.append("scottf@ag-tronix.com")
                    else:
                        recipient.append(info[4])
                    recipient.append(info[5])
                    logging.info("<b>Email to: %s</b>" % ",".join(recipient))
                    self.response.write("<b>Email to: %s</b><br />" % ",".join(recipient))                    
                    subject = "%s weather station data issue" % info[6]
                    MonitorHelper.emailFdacsInfo(recipient,self,subject,html)
            
            '''
            #build email content
            if len(no_update_email_list) != 0:
                
                html = MonitorHelper.buildEmailContent(self,no_update_email_list)
                self.response.out.write("<b>Email to: %s</b>" % ",".join(self.__class__.email_list))
                self.response.out.write(html)
                MonitorHelper.emailInfo(self.__class__.email_list,self,subject,html) 
            
            #build vendor_email_list and grow_email_list dict for no_update_options
            vendor_email_dict = {}
            grower_email_dict = {}
            
            for data in no_update_email_list:
                #build vendor_email_list dict
                if data[5] in vendor_email_dict.keys():
                    vendor_email_dict[data[5]].append(data)
                else:
                    vendor_email_dict[data[5]] = [data]

                #build grower_email_list dict
                if data[6] in grower_email_dict.keys():
                    grower_email_dict[data[6]].append(data)
                else:
                    grower_email_dict[data[6]] = [data]
            logging.info(vendor_email_dict.items())
            logging.info(grower_email_dict.items())
            logging.info("<h3>Email to Grower </h3>")7
            self.response.out.write("<h3>Email to Grower </h3>")
            #email grower
            for k,v in grower_email_dict.items():
                html = MonitorHelper.buildEmailContent(self,v)
                logging.info("<b>Email to: %s</b>" % k)
                self.response.write("<b>Email to: %s</b>" % k)
                self.response.out.wzhu shirite(html)
                logging.info(html)
                MonitorHelper.emailInfo([k],self,subject,html)
            logging.info("<h3>Email to Vendor </h3>")
            self.response.out.write("<h3>Email to Vendor </h3>")
            #email vendor
            for k,v in vendor_email_dict.items():
                html = MonitorHelper.buildEmailContent(self,v)
                self.response.write("<b>Email to: %s</b>" % k)
                self.response.out.write(html)
                logging.info("<b>Email to: %s</b>" % k)
                logging.info(html)
                MonitorHelper.emailInfo([k],self,subject,html)
                
            '''    
            #restored email options
            self.restore_email(self, fresh_true_list,vendor_dict)            
            #latest_email_id_list = database.EmailRecord.all().filter("latest_email", True).run()
            #logging.info(latest_email_id_list)
            #self.response.out.write(latest_email_id_list)
            #q_result = database.EmailRecord.all().run()
            #for result in q_result:
                #self.response.out.write(result.email_time.strftime("%Y-%m-%d %H:%M:%S"))
                #self.response.out.write("<br />")
        else:
            #all stations are good
            MonitorHelper.allGoodInfo(self)
    
    def restore_email(self, resp, fresh_true_list,vendor_dict):
        '''send out the restored email'''
        subject=""
        resp.response.out.write("-------------------------<h3>Restored Email Part</h3>---------------------------")
        latest_email_id_list = [data.station_id for data in database.EmailRecord.all().filter("latest_email", True).run()]
        resp.response.out.write("<h4>Latest Email Station List</h4>")
        resp.response.out.write(latest_email_id_list)
        logging.info(latest_email_id_list)
        #build restore station list
        restore_station_list = [data for data in fresh_true_list if data['station_id'] in latest_email_id_list]
        #build restore email list
        restore_email_list = MonitorHelper.buildInfoList(restore_station_list,vendor_dict)
        resp.response.out.write("<h4>Restored Station List</h4>")
        resp.response.out.write(restore_email_list)
        
        #build restore email content and send out email
        if len(restore_email_list) !=0:
            for info in restore_email_list:
                q_result = database.EmailRecord.all().filter("station_id",info[0]).get()
                time = q_result.email_time.strftime("%Y-%m-%d %H:%M:%S")
                html = MonitorHelper.buildRestoreEmailContent(self,info,time)
                self.response.out.write(html)
                self.response.out.write("<br />")
                #logging.info(html)
                recipient=self.__class__.default_email_list[:]
                if info[2] == "Ag-tronix":
                    recipient.append("sonya@ag-tronix.com")
                    recipient.append("scottf@ag-tronix.com")
                else:
                    recipient.append(info[4])
                recipient.append(info[5])
                logging.info("<b>Email to: %s</b>" % ",".join(recipient))
                self.response.write("<b>Email to: %s</b><br />" % ",".join(recipient))                    
                subject = "%s weather station data issue resolved" % info[6]
                MonitorHelper.emailFdacsInfo(recipient,self,subject,html)                
            
        #update email record in the database
        for data in restore_station_list:
            station_id = data["station_id"]
            record = database.EmailRecord.all().filter("station_id",station_id).get()
            record.latest_email = False
            record.put()
        
        
            
class FdacsUnfixedEmail(webapp2.RequestHandler):
    '''Fdacs Unfixed Email'''
    url = "http://fdacswx.fawn.ifas.ufl.edu/index.php/read/latestobz/format/json"
    email_address = "rlusher@ufl.edu"
    def get(self):
        unfixed_station_id_list = [data.station_id for data in database.EmailRecord.all().filter("latest_email", True).run()]
        self.response.out.write("<h4>There are %d unfixed stations.</h4>" % len(unfixed_station_id_list))
        result = urlfetch.fetch(self.__class__.url)
        decoded = json.loads(result.content)
        info_list = []
        for station in unfixed_station_id_list:
            station_info = [data for data in decoded if data['station_id'] == station]
            data_list=[]
            data_list.append(station)
            data_list.append(station_info[0]["station_name"])
            data_list.append(station_info[0]["vendor_name"])
            data_list.append(station_info[0]["standard_date_time"])
            info_list.append(data_list)
        html = MonitorHelper.buildUnfixedEmailContent(self,info_list)
        subject = "Unfixed Station Weekly Report"
        MonitorHelper.emailInfo([self.__class__.email_address], self, subject, html)
        
    
         
        

application = webapp2.WSGIApplication(
                                    [('/fawn/monitor',FawnMonitor),
                                     ('/fdacs/monitor',FdacsRoutineEmail),
                                     ('/fdacs/routine_vendor_email',FdacsRoutineEmail),
                                     ('/fdacs/unfixed_email', FdacsUnfixedEmail)],
                                    debug = True)
