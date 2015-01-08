from google.appengine.ext import db


class Record(db.Model):

    record_time = db.DateTimeProperty()
    error_code = db.StringProperty(required=True)
    error_details = db.TextProperty(required=True)
    error_time = db.TextProperty()



class FdacsRecord(db.Model):
    record_time = db.DateTimeProperty()
    error_code = db.StringProperty(required=True)
    error_details = db.TextProperty(required=True)
    error_time = db.TextProperty()
    
    
class EmailRecord(db.Model):
    station_id = db.StringProperty(required = True)
    email_time = db.DateTimeProperty()
    latest_email = db.BooleanProperty(default = False)
    
def main():
    print "new record!"
if __name__ == "__main__":
    main()