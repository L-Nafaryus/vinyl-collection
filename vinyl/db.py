from peewee import *

db = SqliteDatabase("vinyl.db")

class BaseModel(Model):
    class Meta:
        db = db

class Release(BaseModel):
    release_id = TextField(unique = True)
    artist = TextField()
    country = TextField()
    title = TextField()
    year = IntegerField()
    master = ForeignKeyField(Master, backref = "releases")
    url = TextField()
    
class Master(BaseModel):
    master_id = TextField(unique = True)
    year = IntegerField()
    url = TextField()
