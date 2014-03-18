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
    record_time_delta = datetime.timedelta(hours = 5)
    fawnStn_time_delta = datetime.timedelta(hours = 1)
    no_update_time_delta = datetime.timedelta(hours = 2)
    def get(self,retries = 3):
        '''response request method=get'''
        logging.info("Start the fawn monitor request")
        self.response.out.write("Start fawn monitor<br />")

        #fetch content from url
        result = urlfetch.fetch(self.__class__.url)
        logging.info("Getting the response status code...")
        self.response.out.write("<b>1. Check availablity</b><br />")

        #check response status code
        if result.status_code == 200:
            logging.info("Status code is ok, get fawn station info")
            logging.info("Check timeliness")
            self.response.out.write("<b>Success !</b><br /> Status code: "+ \
                                    str(result.status_code)+"<br />")
            self.response.out.write("<b>2. Check timeliness</b><br />")
            self.getFawnInfo(self,result)

        else:
            #retry request
            if retries >0:
                logging.info("Fail! Retry %d times", retries-1)
                information = """
                <b>Fail !</b><br /> Retry %d times<br />
                """ % (retries-1)
                self.response.out.write(information)
                return self.get(retries-1)
            else:
                logging.info("After 3 times no response, return status code")
                errorInformation = """
                After 3 times no response, Error %s<br />
                """ % result.status_code
                self.response.out.write(errorInformation)
                self.response.out.write("Building error email...<br />")
                logging.info("Build error email")
                ##self.response.out.write(result.status_code)
                subject = "FAWN ALERT NO RESPONSE"
                html = """<p>Error %s happens</p>""" % result.status_code
                ##body = """Error %s for the fawn station monitor""" % result.status_code
                record = database.Record(error_code = str(result.status_code), error_details = str(result.status_code))
                record.record_time = datetime.datetime.now() - self.__class__.record_time_delta
                record.error_time = record.record_time
                record.put()
                self.emailErrorInfo(self,subject,html)

    def getFawnInfo(self,resp,result):

        '''parse fawn station information'''
        logging.info("parsing json content")
        resp.response.out.write("Parsing json content...<br />")
        #parse json content
        decoded = json.loads(result.content)
        logging.info("Getting fawn time...")
        resp.response.out.write("Getting fawn time...<br />")
        #fawn time
        fawnTime = datetime.datetime.strptime(decoded['fawnTime'][:-4],'%A %B %d, %Y %I:%M %p')
        season = str(decoded['fawnTime'][-3:])
        fawnData=[]
        resp.response.out.write("fawnTime: " + str(fawnTime) + "  " + season)
        for data in decoded['stnsWxData']:
            resp.response.out.write("<br />")
            fawnStn_time = datetime.datetime.strptime(data['dateTimes'][:-4],'%m/%d/%Y %I:%M %p')
            data_list = []
            data_list.append(data['stnID'])
            if data['dateTimes'][-3:] =='CST' or data['dateTimes'][-3:] =='CDT':
                data_list.append(fawnStn_time + self.__class__.fawnStn_time_delta)
                resp.response.out.write(str(data['stnID']) +": "+ \
                str(fawnStn_time + self.__class__.fawnStn_time_delta) + "  " + season)
            else:
                data_list.append(fawnStn_time)
                resp.response.out.write(str(data['stnID']) +": "+str(fawnStn_time) + "  " + season)
            fawnData.append(data_list)
        logging.info("Getting stnID...")
        resp.response.out.write("<br />Getting fawn stnID...<br />")
        no_update_list = [data for data in fawnData if fawnTime - data[1] > self.__class__.no_update_time_delta]
        logging.info("Getting no update stnID...")
        resp.response.out.write(len(no_update_list))
        resp.response.out.write("<br />Getting no update stnID...<br />")
        if len(no_update_list) != 0:
            #report data late station
            logging.info("number of no update stn ID is: %d", len(no_update_list))
            missingInformation ="""
            number of no update stn ID is %d<br />
            """ % len(no_update_list)
            resp.response.out.write(missingInformation)
            subject = "FAWN ALERT NO UPDATE @ " + str(fawnTime)
            message = ",".join([data[0] for data in no_update_list])
            message_time = ",".join(str(data[1]) for data in no_update_list)
            html = """<h3>Alert Info Table</h3>
                      <table border="1" cellspacing="0">
                        <tr>
                            <th>Station_id</th>
                            <th>No update since</th>
                        </tr>
                      """
            for data in no_update_list:
                station_id = """<a href='http://fawn.ifas.ufl.edu/station/station.php?id=%s'>""" % data[0]
                html_text ="""
                            <tr>
                                <td>%s</td>
                                <td>%s</td>
                            </tr>
                """ % (station_id, str(data[1]) + "&nbsp;" + season)
                html = html + html_text
            html = html + "</table>"
            resp.response.out.write("Building no update stn email...<br />")
            q = db.GqlQuery("SELECT * FROM Record \
                             WHERE error_code = '200'\
                             ORDER BY record_time DESC")
            queryResult = q.get()
            if queryResult is None or message_time not in queryResult.error_time or message not in queryResult.error_details :

                record = database.Record(error_code = str(result.status_code),error_details = message)
                record.record_time = fawnTime
                record.error_time = message_time
                record.put()
                self.emailErrorInfo(resp,subject,html)
        else:
            #all stations are good
            logging.info("No missing stnID")
            logging.info("End application")
            resp.response.out.write("No missing stnID<br />")
            resp.response.out.write("End application ! <br />")
    def emailErrorInfo(self,resp,email_subject,email_html):
        '''send error email'''
        for user_address in self.__class__.emailList:
            if mail.is_email_valid(user_address):
                resp.response.out.write("Sending email...<br />")
                logging.info(user_address)
                sender_address = "uffawn@gmail.com"
                message = mail.EmailMessage(sender = sender_address,subject = email_subject)
                message.to = user_address
                message.body = " "
                message.html = email_html
                message.send()
                resp.response.out.write("Sending out... <br />")

            else:
                pass
        resp.response.out.write("End application !<br />")

class FdacsMonitor(webapp2.RequestHandler):
    '''Fdacs Monitor'''
    default_emailList =["jiadw007@gmail.com", "uffawn@gmail.com","tiejiazhao@gmail.com"]
    fdacs_url = "http://fdacswx.fawn.ifas.ufl.edu/index.php/read/latestobz/format/json"
    vendor_url = "http://fdacswx.fawn.ifas.ufl.edu/index.php/read/station/format/json"
    record_time_delta = datetime.timedelta(hours = 5)
    emailList=[]
    def get(self,retries = 3):
        '''response request method = get'''
        logging.info("Start the fdacs monitor request")
        self.response.out.write("Start fawn monitor<br />")

        #fetch content from url
        result = urlfetch.fetch(self.__class__.fdacs_url)
        logging.info("Getting the response status code...")
        self.response.out.write("<b>1. Check availbility</b><br />")

        #check response status code
        if result.status_code == 200:
            logging.info("Status code is ok, get fdacs station info")
            logging.info("Check timeliness")
            self.response.out.write("<b>Success !</b><br /> Status code: "+ \
                                    str(result.status_code)+"<br />")
            self.response.out.write("<b>2. Check timeliness</b><br />")
            self.getFdacsInfo(self,result)
        else:
            #retry request
            if retries > 0:
                logging.info("Fail ! Retry %d times", retries - 1)
                information = """
                <b>Fail !</b><br /> Retry %d times<br />
                """ % (retries - 1)
                self.response.out.write(information)
                return self.get(retries - 1)
            else:
                loggin.info("After 3 times no response, return status code")
                errorInformation = """
                <b>After 3 times no response, Error %s </b><br />
                """ % (result.status_code)
                self.response.out.write(errorInformation)
                self.response.out.write("Building error email...<br />")
                logging.info("Build error email")
                subject = "FDACS ALERT NO RESPONSE"
                html = """<p>Error %s happens</p>""" % (result.status_code)
                record = database.FdacsRecord(error_code = str(result.status_code), error_details = str(result.status_code))
                record.record_time = datetime.datetime.now() - self.__class__.record_time_delta
                record.error_time = record.record_time
                record.put()
                self.emialErrorInfo(self, subject, html)

    def getFdacsInfo(self, resp, result):

        '''parse fawn station information'''
        logging.info("parsing json content")
        resp.response.out.write("Parsing json content...<br />")
        # parse json content
        decoded = json.loads(result.content)
        logging.info("Getting fresh status")
        resp.response.out.write("Getting fresh status...<br />")
        total_stns_num = len(decoded)
        resp.response.out.write("There are total %d stations.<br />" % total_stns_num)
        #fresh status
        fresh_false_list = [data for data in decoded if data['fresh'] == False]
        false_stns_num = len(fresh_false_list)
        resp.response.out.write("There are %d false fresh status stations.<br />" % false_stns_num)
        if false_stns_num != 0:

            alert_time = str(datetime.datetime.now()- datetime.timedelta(hours = 4))
            subject = "FDACS %d ALERT NO UPDATE @ %s" %(false_stns_num, alert_time[:-7])
            resp.response.out.write(subject + "<br />")
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
            no_update_list = []
            for data in fresh_false_list:
                data_list = []
                data_list.append(data["station_id"])
                ##resp.response.out.write(vendor_dict[data["station_id"]]['vendor_name'])
                data_list.append(vendor_dict[data["station_id"]]['vendor_station_id'])
                data_list.append(vendor_dict[data["station_id"]]['vendor_name'])
                data_list.append(data["standard_date_time"])
                logging.info(data_list)
                ##resp.response.out.write(str(data_list) + "<br />")
                no_update_list.append(data_list)

            html = """<h3>Alert Info Table</h3>
                      <table border="1" cellspacing="0">
                        <tr>
                            <th>Station_id</th>
                            <th>Vendor_id</th>
                            <th>Vendor_name</th>
                            <th>No update since</th>
                        </tr>
                      """
            for data in no_update_list:
                htmlText = """
                            <tr>
                                <td>%s</td>
                                <td>%s</td>
                                <td>%s</td>
                                <td>%s</td>
                            </tr>

                """ % (data[0],data[1],data[2],data[3])
                html = html + htmlText
            html = html + "</table>"
            resp.response.out.write(html)
            self.emailErrorInfo(resp,subject,html)

        else:
            #all stations are good
            logging.info("No alert for fdacs stns")
            logging.info("End application")
            resp.response.out.write("No alert for fdacs stns !<br />")
            resp.response.out.write("End application ! <br />")

    def emailErrorInfo(self,resp,email_subject,email_html):
        '''send error email'''
        for user_address in self.__class__.emailList:
            if mail.is_email_valid(user_address):
                resp.response.out.write("Sending email...<br />")
                logging.info(user_address)
                sender_address = "uffawn@gmail.com"
                message = mail.EmailMessage(sender = sender_address,subject = email_subject)
                message.to = user_address
                message.body = " "
                message.html = email_html
                message.send()
                resp.response.out.write("Sending out... <br />")

            else:
                pass
        resp.response.out.write("End application !<br />")


application = webapp2.WSGIApplication(
                                    [('/fawn/monitor',FawnMonitor),
                                     ('/fdacs/monitor',FdacsMonitor)],
                                    debug = True)
