#-------------------------------------------------------------------------------
# Name:        monitor.py
# Purpose:     1. monitor helper
# Author:      Dawei Jia
#
# Created:     03/20/2014
# Copyright:   (c) DaweiJia 2014
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

class MonitorHelper():
    '''Monitor Helper'''

    @classmethod
    def emailInfo(self,email_list, resp, email_subject, email_html):
        '''send error or restored email'''
        for user_address in email_list:
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
        resp.response.out.write("End application !<br /><br />")
        return

    @classmethod
    def allGoodInfo(self,resp):
        '''Action for all good stations info'''
        logging.info("No alert for %s stns" % str(resp.__class__.__name__))
        logging.info("End application")
        resp.response.out.write("No alert for %s stns !<br />" % str(resp.__class__.__name__))
        resp.response.out.write("End application ! <br />")
        return


    @classmethod
    def checkStatusCode(self,resp):

        '''check status code'''
        logging.info("Start the %s monitor request" % resp.__class__.__name__)
        resp.response.out.write("Start %s monitor<br />" % resp.__class__.__name__)

        #fetch content from url
        result = urlfetch.fetch(resp.__class__.url)
        logging.info("Getting the response status code...")
        resp.response.out.write("<b>1. Check availbility</b><br />")

        #check response status code
        if result.status_code == 200:
            logging.info("Status code is ok, get fdacs station info")
            logging.info("Check timeliness")
            resp.response.out.write("<b>Success !</b><br /> Status code: "+ \
                                    str(result.status_code)+"<br />")
            resp.response.out.write("<b>2. Check timeliness</b><br />")
            resp.getInfo(result)
            return
        else:
            #retry request
            if retries > 0:
                logging.info("Fail ! Retry %d times", retries - 1)
                information = """
                <b>Fail !</b><br /> Retry %d times<br />
                """ % (retries - 1)
                resp.response.out.write(information)
                return resp.get(retries - 1)
            else:
                logging.info("After 3 times no response, return status code")
                errorInformation = """
                <b>After 3 times no response, Error %s </b><br />
                """ % (result.status_code)
                resp.response.out.write(errorInformation)
                resp.response.out.write("Building error email...<br />")
                logging.info("Build error email")
                subject = "FDACS ALERT NO RESPONSE"
                html = """<p>Error %s happens</p>""" % (result.status_code)
                record
                if resp.__class__.__name__ == 'FdacsMonitor':
                    record = database.FdacsRecord(error_code = str(result.status_code), error_details = str(result.status_code))
                else:
                    record = database.Record(error_code = str(result.status_code), error_details = str(result.status_code))
                record.record_time = datetime.datetime.now() - self.__class__.record_time_delta
                record.error_time = record.record_time
                record.put()
                MonitorHelper.emailErrorInfo(self.__class__.emailList,self,subject,html)
            return
    @classmethod
    def parseJson(self,resp,result):
        '''parse Json content helper'''
        logging.info("parsing json content")
        resp.response.out.write("Parsing json content...<br />")
        # parse json content
        decoded = json.loads(result.content)
        return decoded

    @classmethod
    def buildEmailContent(self,resp,no_update_list,addInfo = ""):
        '''bulid Email Content'''
        resp.response.out.write("<br/>Building email content!<br/>")
        if resp.__class__.__name__ == 'FdacsMonitor' or resp.__class__.__name__ == 'FdacsRoutineEmail':
            station = no_update_list[0]
            html ="""<p>FAWN has failed to receive data from the weather station listed below during the past 2 hours.</p>          
                     <table border="1" cellspacing="0" cellpadding="5">
                        <tr>
                            <th>Station_id</th>
                            <th>Vendor_id</th>
                            <th>Vendor_name</th>
                            <th>Grower_name</th>
                            <th>Station_name</th>
                        </tr>
                        <tr>
                                <td>%s</td>
                                <td>%s</td>
                                <td>%s</td>
                                <td>%s</td>
                                <td>%s</td>
                        </tr>
                    </table>
                    <p>We have contacted your weather station provider/vendor and will work with them 
                    jointly to resolve this issue.</p>
                    <p>We will send you an email message once the issue is resolved.</p>
                    <p>Thank you</p>
                    <p>If you have any questions please contact:</p>
                    <p>Rick Lusher, FAWN Director, University of Florida IFAS<br />
                    Phone: 352-846-3219<br />
                    E-mail: rlusher@ufl.edu</p> """ %(station[0],station[1],station[2],station[3],station[6])
        else:
            html = html + """<h3>Alert Info Table</h3>
                      <table border="1" cellspacing="0" cellpadding="5">
                        <tr>
                            <th>Station_id</th>
                            <th>No update since</th>lists
                        </tr>
                      """
            for data in no_update_list:
                station_id = """<a href='http://fawn.ifas.ufl.edu/station/station.php?id=%s'>%s<a/>""" % (data[0],data[0])
                html_text ="""
                            <tr>
                                <td>%s</td>
                                <td>%s</td>
                            </tr>
                """ % (station_id, str(data[1]) + "&nbsp;" + addInfo)
                html = html + html_text
            html = html + "</table>"
        return html

    @classmethod
    def updateRecord(self, resp, record, alert_time, message_time):
        '''check whether insert new record in the database'''
        resp.response.out.write("<br />Update record in the database<br/>")
        record.record_time = alert_time
        record.error_time = message_time
        record.put()
        return
    
    @classmethod
    def buildInfoList(self, org_list, vendor_dict):
        '''build email info list'''
        info_list = []
        for data in org_list:
            data_list = []
            data_list.append(data["station_id"])
            ##resp.response.out.write(vendor_dict[daliststa["station_id"]]['vendor_name'])
            data_list.append(vendor_dict[data["station_id"]]['vendor_station_id'])
            data_list.append(vendor_dict[data["station_id"]]['vendor_name'])
            data_list.append(vendor_dict[data["station_id"]]['grower_name'])
            data_list.append(vendor_dict[data["station_id"]]['vendor_email'])
            data_list.append(vendor_dict[data["station_id"]]['grower_email'])
            data_list.append(vendor_dict[data["station_id"]]['station_name'])
            logging.info(data_list)
            ##resp.response.out.write(str(data_list) + "<br />")
            info_list.append(data_list)
        return info_list
    
    @classmethod
    def buildRestoreEmailContent(self, resp, restore_station):
        '''build restored email content'''
        resp.response.out.write("<br/>Building email content!<br/>")
        html = """<p>The issue we reported to you on DATE  regarding the weather station listed below has been resolved</p>
                  <table border="1" cellspacing="0" cellpadding="5">
                        <tr>
                            <th>Station_id</th>
                            <th>Vendor_id</th>
                            <th>Vendor_name</th>
                            <th>Grower_name</th>
                            <th>Station_name</th>
                        </tr>
                        <tr>
                                <td>%s</td>
                                <td>%s</td>
                                <td>%s</td>
                                <td>%s</td>
                                <td>%s</td>
                        </tr>
                    </table>
                    <p>Your weather station is now reporting to FAWN all required data</p>
                    <p>If you have any questions please contact:</p>
                    <p>Rick Lusher, FAWN Director, University of Florida IFAS<br />
                    Phone: 352-846-3219<br />
                    E-mail: rlusher@ufl.edu</p> """ %(restore_station[0],restore_station[1],restore_station[2],
                                                      restore_station[3],restore_station[6])
        return html
        
        