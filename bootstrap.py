from app import db

print "Dropping database..."
db.drop_all()
print "Creating database..."
db.create_all()
print "Done"
