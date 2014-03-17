import urllib
import urllib2
import datetime
def main():

	date = [["05","31"],["06","30"],["07","31"],["08","31"],["09","30"],["10","31"],["11","30"],["12","31"]]
	station_id = [1370037884721,1370903516170,1370904313766,1371069452397,1371069992583,1371070232061]

	for date_time in date:
		print "start"
		for id in station_id:
			url = """http://localhost:8080/fdacs-data-collection/application/data_collection/scheduled_tasks/onDemand/data_quality_tool/manager.php?command=insert&date=2013%s01T2013%s%s&vendorinitial=s&stationid=%s""" % (date_time[0],date_time[0],date_time[1],str(id))
			print url
			req = urllib2.Request(url)
			res_data = urllib2.urlopen(req)
			res = res_data.read()
		print "----------------one month done---------------------"

def onetime():
    station_id = [1370037884721,1370903516170,1370904313766,1371069452397,1371069992583,1371070232061]
    ''''
    for id in station_id:
        url = """http://localhost:8080/fdacs-data-collection/application/data_collection/scheduled_tasks/onDemand/data_quality_tool/manager.php?command=insert&date=20140122T20140126&vendorinitial=s&stationid=%s""" %(str(id))
        print url
        req = urllib2.Request(url)
        res_data = urllib2.urlopen(req)
        res = res_data.read()
    '''
    today = datetime.datetime.today() - datetime.timedelta(days = 1)
    date_string = today.strftime("%Y%m%d")
    for id in station_id:
        print "start @ " + date_string + " id: " + str(id)
        url = """http://localhost:8080/fdacs-data-collection/application/data_collection/scheduled_tasks/onDemand/data_quality_tool/manager.php?command=insert&date=%s&vendorinitial=s&stationid=%s""" % (date_string,str(id))
        req = urllib2.Request(url)
        res_data = urllib2.urlopen(req)
        res = res_data.read()
        print res
onetime()
