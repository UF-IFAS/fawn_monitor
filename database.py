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

def main():
    print "new record!"
if __name__ == "main":
    main()