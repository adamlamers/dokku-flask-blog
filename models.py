from peewee import PostgresqlDatabase, Model, TextField, DateTimeField, ForeignKeyField, BooleanField, IntegerField
from datetime import datetime
from config import Config
import os
import urllib.parse

db_parsed_url = urllib.parse.urlparse(Config.DATABASE_URL)
username = db_parsed_url.username
password = db_parsed_url.password
database = db_parsed_url.path[1:]
hostname = db_parsed_url.hostname

postgres_db = PostgresqlDatabase(
                database=database,
                user=username,
                password=password,
                host=hostname,
                autocommit=True,
                autorollback=True)

class User(Model):
    name = TextField(unique=True)
    admin = BooleanField(default=False)
    password = TextField()
    active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    def get_id(self):
        return str(self.id)

    @property
    def is_active(self):
        return self.active

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    class Meta:
        database = postgres_db

class Post(Model):
    title = TextField()
    description = TextField()
    content = TextField()
    tags = TextField()
    slug = TextField()
    posted_by = ForeignKeyField(User, related_name='posts')
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    class Meta:
        database = postgres_db

class Settings(Model):

    blog_title = TextField()
    initialized = BooleanField()

    icon_1_link = TextField()
    icon_1_icon_type = TextField()
    icon_2_link =  TextField()
    icon_2_icon_type = TextField()

    posts_per_page = IntegerField()
    number_of_recent_posts = IntegerField()
    max_synopsis_chars = IntegerField()

    class Meta:
        database = postgres_db
