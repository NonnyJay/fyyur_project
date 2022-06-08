from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Instantiate db models

db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=False)
    
    # DONE: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.String(255), nullable=False)
    website_link =db.Column(db.String(120), nullable=False)
    look_talent = db.Column(db.Boolean, nullable=False, default=False)
    seek_description = db.Column(db.String(400), nullable=True)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.now)
    shows = db.relationship("Show", backref="venues", lazy=True)
    date_last_modified = db.Column(db.DateTime)
    
    def __repr__(self):
      return f'<Venue : {self.id}, {self.name}, {self.city}, {self.state}, {self.look_talent}>'
class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(255), nullable=False)
    image_link = db.Column(db.String(500),nullable=False)
    facebook_link = db.Column(db.String(120), nullable=False)

    # DONE: implement any missing fields, as a database migration using Flask-Migrate
    website_link = db.Column(db.String(120), nullable=False)
    look_venue = db.Column(db.Boolean, default=False, nullable=False)
    seek_description = db.Column(db.String(400), nullable=True)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.now)
    shows = db.relationship("Show", backref="artists", lazy=True)
    date_last_modified = db.Column(db.DateTime)
    
    
    def __repr__(self):
      return f'<Artist : {self.id}, {self.name}, {self.city}, {self.state}, {self.look_venue}>'

    # DONE Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
    __tablename__ = 'show'
    
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'),nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.now, nullable=False)
    
    
    def __repr__(self):
      return f'<Show {self.id}, {self.artist_id}, {self.venue_id}, {self.start_time}>'
    
""" show = db.Table('show',
    db.Column('artist_id', db.Integer, db.ForeignKey('artist.id'), primary_key=True),
    db.Column('venue_id', db.Integer, db.ForeignKey('venue.id'), primary_key=True),
    db.Column('start_time', db.DateTime, nullable=False, default=datetime.now)
) """