from mongoengine.fields import DateTimeField, IntField, BooleanField, DictField, ListField, StringField
from mongoengine import QuerySet, Document, connect
from datetime import datetime
from utils.config import SriftConfig


class Mongo():
    def __init__(self, db, host, port):
        self.db = db
        self.host = host
        self.port = int(port)
        self.connection = None

    def connect(self):
        try:
            print('Connecting to database...')
            self.connection = connect(
                db=self.db,
                host=self.host,
                port=self.port
            )
        except Exception as connectionerr:
            print(str(connectionerr))
            raise SystemExit(0)

        return self.connection

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


class SriftUser(Document):
    date_created = DateTimeField(default=datetime.utcnow)
    discord_id = IntField()
    summoner_id = StringField()
    summoner_region = StringField()
    summoner_accountId = StringField()
    summoner_puuid = StringField()
    summoner_name = StringField()

    meta = {
        'indexes': ['discord_id'],
        'ordering': ['-date_created']
    }
