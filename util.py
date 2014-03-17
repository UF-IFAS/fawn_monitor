#-------------------------------------------------------------------------------
# Name:        util.py
# Purpose:     1. find last error record in the database  fawn-monitor.appspot.com/queryLastRecord
#              2. query record in specific date range fawn-monitor.appspot.com/queryRecord
# Author:      Dawei Jia
#
# Created:     12/19/2013
# Copyright:   (c) DaweiJia 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import logging
import datetime
import database
from monitor import FawnMonitor
from google.appengine.api import users
#from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
import webapp2
class QueryLastFawnRecord(webapp2.RequestHandler):

    def get(self):

        query = db.GqlQuery("SELECT * FROM Record \
                            ORDER BY record_time DESC")
        result = query.get()
        self.response.out.write("<b>----The last error message----<b><br />")
        if result.error_code != '200':
            self.response.out.write("NO RESPONSE FROM SERVER ! @ " + str(result.record_time))
        else:
            stnIdList = result.error_details.split(",")
            errorTimeList = result.error_time.split(",")
            for id in stnIdList:
                self.response.out.write("""NO UPDATE STATION %s @ %s<br />""" %(id, str(errorTimeList[stnIdList.index(id)])))

class QueryFawnRecord(webapp2.RequestHandler):

    def get(self):

        self.response.out.write("""
          <html>
          <head>
            <meta charset="utf-8">
            <link rel="stylesheet" href="http://code.jquery.com/ui/1.10.3/themes/smoothness/jquery-ui.css">
            <script src="http://code.jquery.com/jquery-1.9.1.js"></script>
            <script src="http://code.jquery.com/ui/1.10.3/jquery-ui.js"></script>
            <script src="/js/query.js"></script>
            <link rel="stylesheet" href="/resources/demos/style.css">
            </head>
            <body>
              <form action="/fawn/queryRecord" method="get">
                <label for="from">From</label>
                <input type="text" id="from" name="from">
                <label for="to">to</label>
                <input type="text" id="to" name="to">
                <div><input type="submit" value="Query"></div>
              </form>
           """)
        if self.request.get("from") != "":
            startTime = self.request.get("from").split('/')
            endTime = self.request.get("to").split('/')
            query = db.GqlQuery("""SELECT * FROM Record
                                WHERE record_time > DATE(%s,%s,%s) and record_time < DATE(%s,%s,%s)
                                """% (startTime[2],startTime[0],startTime[1],endTime[2],endTime[0],endTime[1]))
            results = query.fetch(100)
            self.response.out.write("----RESULT----<br />")
            self.response.out.write("""<table border="1" cellpadding="5"><tr>
                                        <th>error_code</th>
                                        <th>error_details</th>
                                        <th>error_time</th>
                                        <th>record_time</th>
                                    </tr>""")
            for result in results:
                self.response.out.write("""<tr>
                                            <td align='center'>%s</td>
                                            <td align='center'>%s</td>
                                            <td align='center'>%s</td>
                                            <td align='center'>%s</td>
                                        </tr>"""%(str(result.error_code),str(result.error_details),str(result.error_time),str(result.record_time)))
        self.response.out.write("""</table></body></html>""")

class QueryLastFdacsRecord(webapp2.RequestHandler):

    def get(self):
        pass


class QueryFdacsRecord(webapp2.RequestHandler):

    def get(self):
        pass

class Option(webapp2.RequestHandler):

    def get(self):
        path = self.request.path
        self.response.out.write("""
        <html>
            <head>
            </head>
            <body>
            <h2>Choose your action</h2>
            1.<a href="%s/monitor">check monitor</a>
            2.<a href="%s/queryRecord">query record</a>
            3.<a href="%s/queryLastRecord">query last record</a>
            </body>
            </html>



        """ % (path,path,path))



application = webapp2.WSGIApplication(
                                    [('/fawn/queryLastRecord',QueryLastFawnRecord),
                                     ('/fawn/queryRecord',QueryFawnRecord),
                                     ('/fdacs/queryLastRecord',QueryLastFdacsRecord),
                                     ('/fdacs/queryRecord',QueryFdacsRecord),
                                     ('/fawn', Option),
                                     ('/fdacs', Option)],
                                    debug = True)


