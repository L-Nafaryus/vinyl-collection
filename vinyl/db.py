from peewee import *
import vinyl

db = SqliteDatabase(vinyl.ENV["VINYL_DB"])

class BaseModel(Model):
    class Meta:
        database = db

class Master(BaseModel):
    master_id = TextField(unique = True)
    year = IntegerField()
    url = TextField()

class Release(BaseModel):
    release_id = TextField(unique = True)
    artist = TextField()
    country = TextField()
    title = TextField()
    year = IntegerField()
    master = IntegerField(null = True) 
    url = TextField()
    

