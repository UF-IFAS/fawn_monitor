import urllib
import urllib2
import datetime

def main():
    date = [["07",31],["08",31],["09",30],["10",31],["11",30],["12",31]]
    station_id = [1372338552887,1372420047622,1372421223108,1372423160665,1372424134839,1372337178194,
1372337438126,1372337775808,1372338216652,1371202552366,1371206268000,1371209381707,
1371210336426,1371212307167,1372018181998,1372019019889,1372019765172,1372020950229,
1372022219640,1372022572473,1372023141695,1372023496375,1372023852704,1372027804042,
1372029613044,1372030897754,1372068297257,1372068598427,1372247203006,1372247484014,
1372247774219,1372248227202,1372248723090,1372249047973,1372249368331,1372249709837,
1372334729510,1372335072345,1372335458906,1372335765423,1372336007966,1372336223477,1372336547238,1372336894807,1372338874288
]
    for id in station_id:
        print "start"
        for date_time in date:
            day = 7
            while day <= date_time[1]:
                if day < 10:
                    dayString = "0" + str(day)
                else:
                    dayString = str(day)
                url = """http://localhost:8080/fdacs-data-collection/application/data_collection/scheduled_tasks/onDemand/data_quality_tool/manager.php?command=insert&date=2013%s%s&vendorinitial=l&stationid=%s""" % (date_time[0],dayString,str(id))
                print url
                req = urllib2.Request(url)
                res_data = urllib2.urlopen(req)
                res = res_data.read()
                day = day + 1
            print "----------------one month done---------------------"


def onetime():
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

    ''''
    date = [["01",26]]
    for id in station_id:
        print "start"
        for date_time in date:
            day = 22
            print date_time[0]
            while day <= date_time[1]:
                if day < 10:
                    dayString = "0" + str(day)
                else:
                    dayString = str(day)
                url = """http://localhost:8080/fdacs-data-collection/application/data_collection/scheduled_tasks/onDemand/data_quality_tool/manager.php?command=insert&date=2014%s%s&vendorinitial=l&stationid=%s""" % (date_time[0],dayString,str(id))
                print url
                req = urllib2.Request(url)
                res_data = urllib2.urlopen(req)
                res = res_data.read()
                day = day + 1
            print "----------------one month done---------------------"
    '''
    day_delta = 31
    while day_delta < 36:
        today = datetime.datetime.today() - datetime.timedelta(days = day_delta)
        date_string = today.strftime("%Y%m%d")
        for id in station_id:
            print "start @ " + date_string + " id: " + str(id)
            ##print today
            url = """http://localhost:8080/fdacs-data-collection/application/data_collection/scheduled_tasks/onDemand/data_quality_tool/manager.php?command=overwrite&date=%s&vendorinitial=l&stationid=%s&params=all""" % (date_string,str(id))

            req = urllib2.Request(url)
            res_data = urllib2.urlopen(req)
            res = res_data.read()
            print res
        day_delta = day_delta + 1

onetime()