#-------------------------------------------------------------------------------
# Name:        monitor.py
# Purpose:     1. check availbility http://fawn.ifas.ufl.edu/controller.php/latestmapjson/
#              2. check data timeliness for 42 fawn stations fawn-monitor.appspot.com/
#                   fawn-monitor.appspot.com/monitor
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
from google.appengine.ext import webapp
from google.appengine.api import urlfetch
from google.appengine.api import mail
from google.appengine.ext import db
import webapp2
class Monitor(webapp2.RequestHandler):
    '''monitor data availability and timeliness '''
    url = "http://fawn.ifas.ufl.edu/controller.php/latestmapjson/"
    stnIDList = ['260','240','241','110','280','330','450','380','311','360',
               '435','170','150','455','480','410','130','250','390','302',
               '121','304','303','230','371','270','290','320','350','460',
               '275','180','405','440','470','340','160','490','120','420',
               '140','425']
    emailList = ["jiadw007@gmail.com","rlusher@ufl.edu","tiejiazhao@gmail.com","ohyeahfanfan@gmail.com"]
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

        '''pasre fawn station information'''
        logging.info("parsing json content")
        resp.response.out.write("Parsing json content...<br />")
        #parse json content
        decoded = json.loads(result.content)
        logging.info("Getting fawn time...")
        resp.response.out.write("Getting fawn time...<br />")
        #fawn time
        fawnTime = datetime.datetime.strptime(decoded['fawnTime'][:-4],'%A %B %d, %Y %I:%M %p')
        fawnData=[]
        resp.response.out.write("fawnTime: " + str(fawnTime) + "   EST")
        for data in decoded['stnsWxData']:
            resp.response.out.write("<br />")
            fawnStn_time = datetime.datetime.strptime(data['dateTimes'][:-4],'%m/%d/%Y %I:%M %p')
            data_list = []
            data_list.append(data['stnID'])
            if data['dateTimes'][-3:] =='CST' or data['dateTimes'][-3:] =='CDT':
                data_list.append(fawnStn_time + self.__class__.fawnStn_time_delta)
                resp.response.out.write(str(data['stnID']) +": "+ \
                str(fawnStn_time + self.__class__.fawnStn_time_delta) + "  EST")
            else:
                data_list.append(fawnStn_time)
                resp.response.out.write(str(data['stnID']) +": "+str(fawnStn_time) + "  EST")
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
            html = ""
            ##body = ""
            count = 1;
            for data in no_update_list:
                html_text = """
                . Station ID: <a href='http://fawn.ifas.ufl.edu/station/station.php?id=%s'>
                """% data[0]
                html = "<p>"+ html + str(count) + html_text + data[0] + \
                "</a></p><p>No update since: " + str(data[1]) + "&nbsp;EST</p>"
                ##body = body + str(count) + ". Station ID: " + data[0] +"\n    No update since:" + str(data[1]) + "\n"
                count = count + 1
            resp.response.out.write("Building no update stn email...<br />")
            q = db.GqlQuery("SELECT * FROM Record \
                             WHERE error_code = '200'\
                             ORDER BY record_time DESC")
            queryResult = q.get()
            if queryResult is None or queryResult.error_time != message_time or queryResult.error_details != message:

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
                sender_address = "jiadw007@gmail.com"
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
                                    [('/monitor',Monitor),
                                     ('/',Monitor)],
                                    debug = True)
