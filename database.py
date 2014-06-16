from google.appengine.ext import db


class Record(db.Model):

    record_time = db.DateTimeProperty()
    error_code = db.StringProperty(required=True)
    error_details = db.StringProperty(required=True)
    error_time = db.StringProperty()



class FdacsRecord(db.Model):
    record_time = db.DateTimeProperty()
    error_code = db.StringProperty(required=True)
    error_details = db.StringProperty(required=True)
    error_time = db.StringProperty()
    
    
class EmailRecord(db.Model):
    station_id = db.StringProperty(required = True)
    email_time = db.DateTimeProperty()
    
def main():
    print "new record!"
if __name__ == "__main__":
    main()