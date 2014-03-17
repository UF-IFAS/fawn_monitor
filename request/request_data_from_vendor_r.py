import urllib
import urllib2
import datetime
def main():

	date = [["05","31"],["06","30"],["07","31"],["08","31"],["09","30"],["10","31"],
            ["11","30"],["12","31"]]
	station_id = [1372273825011,1372273972292,1369420647569,1369420784490,1372273566294,
                  1371493004601,1371493821371,1371749589983,1371840250117,1371841699306,
                  1375364577377,1372185383365,1372185772594,1375364809900]

	for date_time in date:
		print "--------------------start--------------------------"
		for id in station_id:
			url = """http://localhost:8080/fdacs-data-collection/application/data_collection/scheduled_tasks/onDemand/data_quality_tool/manager.php?command=insert&date=2013%s01T2013%s%s&vendorinitial=r&stationid=%s""" % (date_time[0],date_time[0],date_time[1],str(id))
			print url
			req = urllib2.Request(url)
			res_data = urllib2.urlopen(req)
			res = res_data.read()
		print "----------------one month done---------------------"

def onetime():

    station_id = [1372273825011,1372273972292,1369420647569,1369420784490,1372273566294,
                  1371493004601,1371493821371,1371749589983,1371840250117,1371841699306,
                  1375364577377,1372185383365,1372185772594,1375364809900]
    ''''
    for id in station_id:
        print "start"
        url = """http://localhost:8080/fdacs-data-collection/application/data_collection/scheduled_tasks/onDemand/data_quality_tool/manager.php?command=insert&date=20140122T20140126&vendorinitial=r&stationid=%s""" %(str(id))
        print url
        req = urllib2.Request(url)
        res_data = urllib2.urlopen(req)
        res = res_data.read()
        print "----------------one month done---------------------"
    '''
    today = datetime.datetime.today() - datetime.timedelta(days = 1)
    date_string = today.strftime("%Y%m%d")
    for id in station_id:
        print "start @ " + date_string + " id: " + str(id)
        url = """http://localhost:8080/fdacs-data-collection/application/data_collection/scheduled_tasks/onDemand/data_quality_tool/manager.php?command=insert&date=%s&vendorinitial=r&stationid=%s""" % (date_string,str(id))
        req = urllib2.Request(url)
        res_data = urllib2.urlopen(req)
        res = res_data.read()
        print res
onetime()
