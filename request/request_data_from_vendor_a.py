import urllib
import urllib2
import datetime

def main():

    station_id = [1371134670088,1371232073915,1371564676246,1371564826652,1372082127762,
                    1372085089831,1372088050015,1372436592530,1372436695136,1376510192542,
                    1376511125659,1376511254565,1376511371266,1376511520161,1376511687661,
                    1377116716521,1378835808348,1378835967650,1378836081600,1383323874602,
                    1383849429285,1389794987344,1389798278419,1389798514339,1389798711083,
                    1389798885198,1389799063221]
    for data in station_id:
        print "start"
        url = """http://localhost:8080/fdacs-data-collection/application/data_collection/scheduled_tasks/onDemand/data_quality_tool/manager.php?command=insert&date=20140122T20140126&vendorinitial=a&stationid=%s""" % str(data)
        print url
        req = urllib2.Request(url)
        ##print req
        res_data = urllib2.urlopen(req)
        res = res_data.read()
        ##print res
        print "----------------one month done---------------------"

def onetime():
    station_id = [1371134670088,1371232073915,1371564676246,1371564826652,1372082127762,
                    1372085089831,1372088050015,1372436592530,1372436695136,1376510192542,
                    1376511125659,1376511254565,1376511371266,1376511520161,1376511687661,
                    1377116716521,1378835808348,1378835967650,1378836081600,1383323874602,
                    1383849429285,1389794987344,1389798278419,1389798514339,1389798711083,
                    1389798885198,1389799063221]
    today = datetime.datetime.today() - datetime.timedelta(days = 1)
    date_string = today.strftime("%Y%m%d")
    for id in station_id:
        print "start @ " + date_string + " id: " + str(id)
        url = """http://localhost:8080/fdacs-data-collection/application/data_collection/scheduled_tasks/onDemand/data_quality_tool/manager.php?command=insert&date=%s&vendorinitial=a&stationid=%s""" % (date_string,str(id))
        req = urllib2.Request(url)
        res_data = urllib2.urlopen(req)
        res = res_data.read()
        print res
onetime()

