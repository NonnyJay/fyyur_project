#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import os
import sys
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from jinja2.utils import markupsafe 
markupsafe.Markup()
from markupsafe import escape
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_migrate import Migrate
from forms import *
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# DONE: connect to a local postgresql database
migrate = Migrate(app, db)
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
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

# Function to convert values to boolean
#new_tal = lambda x : True if x == "y" else False

#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # DONE: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  # Get distinct City and State combination
  dataCityStates = Venue.query.with_entities(db.distinct(Venue.city),Venue.state).order_by('state','city').all()
  
  # Extra distinct City and State combination into placeholder with a for loop
  for dataCity in dataCityStates:
    ind_city_state_data = {
      "city" : dataCity[0],
      "state" : dataCity[1]
    }
    #print(ind_city_state_data["city"])
    #print(ind_city_state_data["state"])
    # Get the venue details for the city and state combination
    dataVenues = Venue.query.filter(Venue.city == dataCity[0], Venue.state == dataCity[1]).all()
    ind_venue = []
    print(dataVenues)
    # Extra distinct Venue into placeholder with a for loop
    for dataVenue in dataVenues:
      dataGetUp = db.session.query(Show).filter(Show.venue_id == dataVenue.id,Show.start_time > datetime.now()).count()
      venue_data = {
        "id" : dataVenue.id,
        "name" : dataVenue.name,
        "num_upcoming_shows" : dataGetUp,
      }
      # Append venue details to list
      ind_venue.append(venue_data)

    #Include the venue data to the dictionary "ind_city_state_data"""sumary_line"""
    ind_city_state_data["venues"] = ind_venue

    # Append all details to the entire data list
    data.append(ind_city_state_data)

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # DONE: implement search on artists (venues) with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term=request.form.get('search_term', '')
  response = {}

  # Get Venues record
  dataGetVenues = Venue.query.filter(Venue.name.ilike(f"%{search_term}%") | Venue.city.ilike(f"%{search_term}%") |Venue.state.ilike(f"%{search_term}%")).all()
  #print(dataGetVenues)
  ind_srch_ven = []
  # Extra distinct Venue into placeholder with a for loop
  for dataGetVen in dataGetVenues:
    dataGetUp = db.session.query(Show).filter(Show.venue_id == dataGetVen.id,Show.start_time > datetime.now()).count()
    srch_ven = {
      "id" : dataGetVen.id,
      "name" : dataGetVen.name,
      "num_upcoming_shows": dataGetUp,
    }
    ind_srch_ven.append(srch_ven)
  response["count"] = len(dataGetVenues)
  response["data"] = ind_srch_ven
  #print(response)

  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # DONE: replace with real venue data from the venues table, using venue_id
  #data = {}
  # Query venue details with venue id
  print(venue_id)
  dataShowVenue = Venue.query.get(venue_id)
  #print(dataShowVenue)
  #print(dataShowVenue.id)
  #print(dataShowVenue.website_link)
  #print(dataShowVenue.phone)
  # Generate data file from query
  data = {
    "id": dataShowVenue.id,
    "name": dataShowVenue.name,
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk", "Electric"],
    "address": dataShowVenue.address,
    "city": dataShowVenue.city,
    "state": dataShowVenue.state,
    "phone": dataShowVenue.phone,
    "website": dataShowVenue.website_link,
    "facebook_link": dataShowVenue.facebook_link,
    "seeking_talent": dataShowVenue.look_talent,
    "seeking_description": dataShowVenue.seek_description,
    "image_link": dataShowVenue.image_link
  }
  dataPastVenObj = db.session.query(Artist,Show).with_entities(Artist.id,Artist.name,Artist.image_link,Show.start_time).filter(Artist.id == Show.artist_id,Show.venue_id == venue_id,Show.start_time < datetime.now()).order_by(Show.start_time)
  #print(dataPastVenObj.count())
  dataVenPastShows = []
  for dataPastVen in dataPastVenObj.all():
    ind_dataPastVen={
      "artist_id" : dataPastVen[0],
      "artist_name" : dataPastVen[1],
      "artist_image_link": dataPastVen[2],
      "start_time": dataPastVen[3].strftime('%Y-%m-%d %H:%S:%M')
    }
    dataVenPastShows.append(ind_dataPastVen)
  data["past_shows"] = dataVenPastShows


  dataUpcVenObj = db.session.query(Artist,Show).with_entities(Artist.id,Artist.name,Artist.image_link,Show.start_time).filter(Artist.id == Show.artist_id,Show.venue_id == venue_id,Show.start_time > datetime.now()).order_by(Show.start_time)
  #print(dataUpcVenObj.count())
  dataVenUpcShows = []
  for dataUpcVen in dataUpcVenObj.all():
    ind_dataUpcVen={
      "artist_id" : dataUpcVen[0],
      "artist_name" : dataUpcVen[1],
      "artist_image_link": dataUpcVen[2],
      "start_time": dataUpcVen[3].strftime('%Y-%m-%d %H:%S:%M')
    }
    dataVenUpcShows.append(ind_dataUpcVen)
  data["upcoming_shows"] = dataVenUpcShows
  data["past_shows_count"] = dataPastVenObj.count()
  data["upcoming_shows_count"] = dataUpcVenObj.count()

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # DONE: insert form data as a new Venue record in the db, instead
  curr_time = datetime.now().strftime('%Y-%m-%d %H:%S:%M')
  print(curr_time)
  #rf = request.form['seeking_talent']
  # Get values from the uses inputed fields
  try:
    add_venue = Venue(
    name = request.form['name'],
    city = request.form['city'],
    state = request.form['state'],
    address = request.form['address'],
    phone = request.form['phone'],
    image_link = request.form['image_link'],
    genres = ','.join([str(elem) for elem in request.form.getlist('genres')]),
    #genres = ','.join([str(elem) for elem in genresList])
    facebook_link = request.form['facebook_link'],
    website_link = request.form['website_link'],
    look_talent = request.form.get('seeking_talent', False),
    #look_talent = new_tal(rf),
    seek_description = request.form['seeking_description'],
    #date_created = curr_time
    )
    # DONE: modify data to be the data object returned from db insertion
    print(add_venue)
    db.session.add(add_venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    # DONE: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # DONE: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  print(venue_id)
  try:
      venueDel = Venue.query.get(venue_id)
      venueName = venueDel.name
      db.session.delete(venueDel)
      db.session.commit()
      # on successful db deletion, flash success
      flash('Venue ' + venueName + ' was successfully deleted!')
  except:
      db.session.rollback()
      print(sys.exc_info())
      flash('An error occurred. Venue ' + venueName + ' could not be deleted.')
  finally:
      db.session.close()
  return None
  #return render_template('pages/home.html')

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # DONE: replace with real data returned from querying the database
  data = []
  # Get Artist information from the database
  dataArtists = Artist.query.with_entities(Artist.id,Artist.name).order_by('id').all()
  
  # Extra Artist list into placeholder with a for loop
  for dataArtist in dataArtists:
    ind_artist_data = {
      "id" : dataArtist[0],
      "name" : dataArtist[1]
    }
    #print(ind_artist_data)
    # Append all details to the entire data list
    data.append(ind_artist_data)

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term=request.form.get('search_term', '')
  response = {}

  # Get Artist record
  dataGetArtists = Artist.query.filter(Artist.name.ilike(f"%{search_term}%")).all()
  ind_srch_art = []
  # Extra distinct artist into placeholder with a for loop
  for dataGetArt in dataGetArtists:
    dataGetUp = db.session.query(Show).filter(Show.artist_id == dataGetArt.id,Show.start_time > datetime.now()).count()
    print("Testing Result")
    print(dataGetUp)
    srch_art = {
      "id" : dataGetArt.id,
      "name" : dataGetArt.name,
      "num_upcoming_shows": dataGetUp,
    }
    ind_srch_art.append(srch_art)
  response["count"] = len(dataGetArtists)
  response["data"] = ind_srch_art
  #print(response)

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # DONE: replace with real artist data from the artist table, using artist_id
  print(artist_id)
  dataShowArtist = Artist.query.get(artist_id)
  print(dataShowArtist.genres)
  print(dataShowArtist)
  print(dataShowArtist.id)
  print(dataShowArtist.website_link)
  print(dataShowArtist.phone)
  # Generate data file from query
  data = {
    "id": dataShowArtist.id,
    "name": dataShowArtist.name,
    #"genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk", "Electric"],
    "genres": list(dataShowArtist.genres.split(",")),
    "city": dataShowArtist.city,
    "state": dataShowArtist.state,
    "phone": dataShowArtist.phone,
    "website": dataShowArtist.website_link,
    "facebook_link": dataShowArtist.facebook_link,
    "seeking_venue": dataShowArtist.look_venue,
    "seeking_description": dataShowArtist.seek_description,
    "image_link": dataShowArtist.image_link
  }
  dataPastObj = db.session.query(Venue,Show).with_entities(Venue.id,Venue.name,Venue.image_link,Show.start_time).filter(Venue.id == Show.venue_id,Show.artist_id == artist_id,Show.start_time < datetime.now()).order_by(Show.start_time)
  print(dataPastObj.count())
  dataArtPastShows = []
  for dataPast in dataPastObj.all():
    ind_dataPast={
      "venue_id" : dataPast[0],
      "venue_name" : dataPast[1],
      "venue_image_link": dataPast[2],
      "start_time": dataPast[3].strftime('%Y-%m-%d %H:%S:%M')
    }
    dataArtPastShows.append(ind_dataPast)
  data["past_shows"] = dataArtPastShows
    #print(dataPast[0])
    #print(dataPast[1])
    #print(dataPast[2])
    #print(dataPast[3])
    
  dataUpcObj = db.session.query(Venue,Show).with_entities(Venue.id,Venue.name,Venue.image_link,Show.start_time).filter(Venue.id == Show.venue_id,Show.artist_id == artist_id,Show.start_time > datetime.now()).order_by(Show.start_time)
  print(dataUpcObj.count())
  dataArtUpcShows = []
  for dataUpc in dataPastObj.all():
    ind_dataUpc={
      "venue_id" : dataUpc[0],
      "venue_name" : dataUpc[1],
      "venue_image_link": dataUpc[2],
      "start_time": dataUpc[3].strftime('%Y-%m-%d %H:%S:%M')
    }
    dataArtUpcShows.append(ind_dataUpc)
  data["upcoming_shows"] = dataArtUpcShows
  data["past_shows_count"] = dataPastObj.count()
  data["upcoming_shows_count"] = dataUpcObj.count()

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  print(artist_id)
  dataShowArtist = Artist.query.get(artist_id)
  
  form.genres.data = list(dataShowArtist.genres.split(",")) # Convert string to list value
  form.name.data = dataShowArtist.name
  form.city.data = dataShowArtist.city
  form.state.data = dataShowArtist.state
  form.phone.data = dataShowArtist.phone
  form.website_link.data = dataShowArtist.website_link
  form.facebook_link.data = dataShowArtist.facebook_link
  form.seeking_venue.data = dataShowArtist.look_venue
  form.seeking_description.data = dataShowArtist.seek_description
  form.image_link.data = dataShowArtist.image_link
  #print(dataShowArtist.genres)
  #print(dataShowArtist)
  #print(dataShowArtist.id)
  #print(dataShowArtist.website_link)
  #print(dataShowArtist.phone)
  # Generate data file from query

  # DONE: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=dataShowArtist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # DONE: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  # Get values from the uses inputed fields
  form = ArtistForm()
  curr_time = datetime.now().strftime('%Y-%m-%d %H:%S:%M')
  print(curr_time)
  #print(form.genres.data)
  #print(form.seeking_venue.data)
  #rv = request.form.get('seeking_venue', False)
  dataEditArtist = Artist.query.get(artist_id)
  if  dataEditArtist:
    try:
      print("Before getting artist")
      dataEditArtist.name = request.form['name']
      dataEditArtist.genres = ','.join([str(elem) for elem in form.genres.data])
      dataEditArtist.city = request.form['city']
      dataEditArtist.state = request.form['state']
      dataEditArtist.phone = request.form['phone']
      dataEditArtist.website_link = request.form['website_link']
      dataEditArtist.facebook_link = request.form['facebook_link']
      dataEditArtist.look_venue = form.seeking_venue.data
      dataEditArtist.seek_description = request.form['seeking_description']
      dataEditArtist.image_link = request.form['image_link']
      dataEditArtist.date_last_modified = datetime.now()
      print(dataEditArtist.genres)
      print(dataEditArtist.phone)
      print(dataEditArtist.look_venue)
      print(dataEditArtist.website_link)
      print(dataEditArtist.facebook_link)
      print(dataEditArtist.image_link)
      print(dataEditArtist.date_last_modified)

      # DONE: modify data to be the data object returned from db insertion
      db.session.commit()
      # on successful db update, flash success
      flash('Artist Details for ' + form.name.data + ' was successfully updated!')
    except:
      # DONE: on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
      db.session.rollback()
      print(sys.exc_info())
      flash('An error occurred. Artist Details for ' + request.form['name'] + ' could not be updated.')
    finally:
      return redirect(url_for('show_artist', artist_id=artist_id))
  return render_template('errors/404.html'), 404

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  print(venue_id)
  dataShowVenue = Venue.query.get(venue_id)
  form.genres.data = list(dataShowVenue.genres.split(",")) # Convert string to list value
  form.name.data = dataShowVenue.name
  form.city.data = dataShowVenue.city
  form.state.data = dataShowVenue.state
  form.phone.data = dataShowVenue.phone
  form.address.data = dataShowVenue.address
  form.website_link.data = dataShowVenue.website_link
  form.facebook_link.data = dataShowVenue.facebook_link
  form.seeking_talent.data = dataShowVenue.look_talent
  form.seeking_description.data = dataShowVenue.seek_description
  form.image_link.data = dataShowVenue.image_link

  # DONE: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=dataShowVenue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # DONE: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm()
  curr_time = datetime.now().strftime('%Y-%m-%d %H:%S:%M')
  print(curr_time)
  #print(form.genres.data)
  #print(form.seeking_venue.data)
  #rv = request.form.get('seeking_venue', False)
  dataEditVenue = Venue.query.get(venue_id)
  if  dataEditVenue:
    try:
      print("Before getting venue")
      dataEditVenue.name = request.form['name']
      dataEditVenue.genres = ','.join([str(elem) for elem in form.genres.data]) #convert list to strings
      dataEditVenue.city = request.form['city']
      dataEditVenue.address = request.form['address']
      dataEditVenue.state = request.form['state']
      dataEditVenue.phone = request.form['phone']
      dataEditVenue.website_link = request.form['website_link']
      dataEditVenue.facebook_link = request.form['facebook_link']
      dataEditVenue.look_talent = form.seeking_talent.data
      dataEditVenue.seek_description = request.form['seeking_description']
      dataEditVenue.image_link = request.form['image_link']
      dataEditVenue.date_last_modified = datetime.now()
      #print(dataEditVenue.genres)
      #print(dataEditVenue.phone)
      #print(dataEditVenue.look_talent)
      #print(dataEditVenue.website_link)
      #print(dataEditVenue.facebook_link)
      #print(dataEditVenue.image_link)
      #print(dataEditVenue.date_last_modified)

      # DONE: modify data to be the data object returned from db insertion
      #db.session.commit()
      # on successful db update, flash success
      flash('Venue  Details for ' + form.name.data + ' was successfully updated!')
    except:
      # DONE: on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
      db.session.rollback()
      print(sys.exc_info())
      flash('An error occurred. Venue Details for ' + request.form['name'] + ' could not be updated.')
    finally:
      return redirect(url_for('show_venue', venue_id=venue_id))
  return render_template('errors/404.html'), 404
  
  #return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # DONE: insert form data as a new Venue record in the db, instead
  # DONE: modify data to be the data object returned from db insertion
  try:
    add_artist = Artist(
    name = request.form['name'],
    city = request.form['city'],
    state = request.form['state'],
    #address = request.form['address'],
    phone = request.form['phone'],
    image_link = request.form['image_link'],
    genres = ','.join([str(elem) for elem in request.form.getlist('genres')]),
    facebook_link = request.form['facebook_link'],
    website_link = request.form['website_link'],
    look_venue = request.form.get('seeking_venue', False),
    seek_description = request.form['seeking_description'],
    )
    # DONE: modify data to be the data object returned from db insertion
    print(add_artist)
    db.session.add(add_artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    # DONE: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  finally:
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # DONE: replace with real venues data.
  data = []
  # Get Shows combination with venue and artist table
  dataShows = db.session.query(Show, Artist, Venue).with_entities(Show.venue_id,Venue.name,Show.artist_id,Artist.name,Artist.image_link,Show.start_time).filter(Artist.id == Show.artist_id,Venue.id == Show.venue_id).order_by(Show.start_time).all()

  # Extra distinct Show into placeholder with a for loop
  for dataShow in dataShows:
    ind_show_data = {
      "venue_id" : dataShow[0],
      "venue_name" : dataShow[1],
      "artist_id" : dataShow[2],
      "artist_name" : dataShow[3],
      "artist_image_link" : dataShow[4],
      "start_time" : dataShow[5].strftime('%Y-%m-%d %H:%S:%M')
    }
    #print(ind_show_data)
    # Append show details to list
    data.append(ind_show_data)
    #print(data)

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # DONE: insert form data as a new Show record in the db, instead
  try:
    add_show = Show(
    artist_id = request.form['artist_id'],
    venue_id = request.form['venue_id'],
    start_time = request.form['start_time'],
    )
    # DONE: modify data to be the data object returned from db insertion
    #print(add_show)
    #print(request.form['artist_id'])
    #print(request.form['venue_id'])
    #print(request.form['start_time'])
    db.session.add(add_show)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    # DONE: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Show could not be listed.')
  finally:
    return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:

""" if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port) """

