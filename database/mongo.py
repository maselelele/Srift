from mongoengine.fields import DateTimeField, IntField, BooleanField, DictField, ListField
from mongoengine import QuerySet, Document, connect
from datetime import datetime


class Mongo():
    def __init__(self):
        self.db = 'srift'
        self.connection = None

    def connect(self):
        conn = connect(
            # Currently using a local database
            db=self.db
            # username='',
            # password='',
            # host=''
        )

        self.connection = conn

    def getDatabase(self):
        return self.db

    def getConnection(self):
        return self.connection


class SriftGuild(Document):
    date_created = DateTimeField(default=datetime.utcnow)
    guild_id = IntField(required=True)
    initialized = BooleanField(required=True, default=False)
    srift_ids = DictField()
    user_channels = DictField()

    meta = {
        'indexes': ['guild_id'],
        'ordering': ['-date_created']
    }
