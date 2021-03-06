import os
import sys
import json
import dateutil.parser
import babel
from datetime import datetime
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, Blueprint
from flask_moment import Moment
from flask_wtf import Form, CsrfProtect
from .forms import ShowForm, VenueForm, ArtistForm
from .models import db, Venue, Artist, Show

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#
site = Blueprint('site', __name__)

# change genres string to list


def fix_genres(artist, form):
    genres = artist.genres
    genres = genres.replace('{', '')
    genres = genres.replace('}', '')
    genres_list = []

    for g in genres.split(','):
        genres_list.append(g)
    form.genres.data = genres_list


@site.route('/')
def index():
    return render_template('pages/home.html')

#  Venues
#  ----------------------------------------------------------------


@site.route('/venues')
def venues():
    venues = Venue.query.all()
    areas = set()
    data = []

    for v in venues:
        areas.add((v.city, v.state))

    for a in areas:
        data.append({
            'city': a[0],
            'state': a[1],
            'venues': Venue.query.filter_by(city=a[0], state=a[1]).all()
        })
    return render_template('pages/venues.html', areas=data)


@site.route('/venues/search', methods=['POST'])
def search_venues():
    # implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return 'The Musical Hop'.
    # search for 'Music' should return 'The Musical Hop' and 'Park Square Live Music & Coffee'
    data = Venue.query.filter(Venue.name.ilike(
        "%" + request.form.get('search_term') + "%")).all()
    response = {
        'count': len(data),
        'data': data
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@site.route('/venues/<int:venue_id>')
def show_venue(venue_id):

    upcoming_shows = []
    past_shows = []
    now = datetime.now()
    venue = Venue.query.get(venue_id)
    # query all the available shows using joins
    shows = db.session.query(Show.date_time, Show.artist_id, Artist.image_link, Artist.name).\
        join(Venue, Show.venue_id == Venue.id).\
        join(Artist, Show.artist_id == Artist.id).filter(
            Show.venue_id == venue_id)

    # checking if they are past or future
    for s in shows:
        if s.date_time < now:
            past_shows.append({
                'artist_id': s.artist_id,
                'artist_image_link': s.image_link,
                'artist_name': s.name,
                'start_time': s.date_time.isoformat()
            })
        else:
            upcoming_shows.append({
                'artist_id': s.artist_id,
                'artist_image_link': s.image_link,
                'artist_name': s.name,
                'start_time': s.date_time.isoformat()
            })

    venue.upcoming_shows = upcoming_shows
    venue.past_shows = past_shows
    venue.upcoming_shows_count = len(upcoming_shows)
    venue.past_shows_count = len(past_shows)

    return render_template('pages/show_venue.html', venue=venue)

#  Create Venue
#  ----------------------------------------------------------------


@site.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@site.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # insert form data as a new Venue record in the db, instead
    # modify data to be the data object returned from db insertion
    form = VenueForm()
    if form.validate_on_submit():
        try:
            new_venue = Venue(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                address=form.address.data,
                phone=form.phone.data,
                image_link=form.image_link.data,
                genres=form.genres.data,
                facebook_link=form.facebook_link.data,
                website_link=form.website_link.data,
                seeking_talent=form.seeking_talent.data,
                seeking_description=form.seeking_description.data)

            new_venue.create()

            # on successful db insert, flash success
            flash('Venue ' + form.name.data + ' was successfully listed!')
            return redirect(url_for('site.show_venue', venue_id=new_venue.id))

            # on unsuccessful db insert, flash an error instead.
            # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        except:
            db.session.rollback()
            print(sys.exc_info())
            flash('An error occurred. Venue ' +
                  form.name.data + ' could not be listed.')
        finally:
            db.session.close()
    else:
        flash('An error occurred. Venue ' +
              form.name.data + ' could not be listed.')
        print(form.errors)
    return render_template('forms/new_venue.html', form=form)


@site.route('/venues/<venue_id>/delete', methods=['GET'])
def delete_venue(venue_id):
    # Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    try:
        delete_venue = Venue.query.get(venue_id)
        # delete related shows
        shows = Show.query.filter_by(venue_id=venue_id).all()
        for show in shows:
            show.delete()
        delete_venue.delete()
        print("Venue deleted")
    except:
        db.session.rollback()
        print("Error")
    finally:
        db.session.close()
    return redirect(url_for('site.index'))

#  Artists
#  ----------------------------------------------------------------


@site.route('/artists')
def artists():
    artists = Artist.query.all()
    data = []
    for a in artists:
        data.append({
            'id': a.id,
            'name': a.name
        })
    return render_template('pages/artists.html', artists=data)


@site.route('/artists/search', methods=['POST'])
def search_artists():
    # implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for 'A' should return 'Guns N Petals', 'Matt Quevado', and 'The Wild Sax Band'.
    # search for 'band' should return 'The Wild Sax Band'.
    data = Artist.query.filter(Artist.name.ilike(
        "%" + request.form.get('search_term') + "%")).all()
    response = {
        'count': len(data),
        'data': data
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@site.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    upcoming_shows = []
    past_shows = []
    now = datetime.now()
    artist = Artist.query.get(artist_id)
    # query all the available shows using joins
    shows = db.session.query(Show.date_time, Show.venue_id, Venue.image_link, Venue.name).\
        join(Venue, Show.venue_id == Venue.id).\
        join(Artist, Show.artist_id == Artist.id).filter(
            Show.artist_id == artist_id)

    # checking if they are past or future
    for s in shows:
        if s.date_time < now:
            past_shows.append({
                'venue_id': s.venue_id,
                'venue_image_link': s.image_link,
                'venue_name': s.name,
                'start_time': s.date_time.isoformat()
            })
        else:
            upcoming_shows.append({
                'venue_id': s.venue_id,
                'venue_image_link': s.image_link,
                'venue_name': s.name,
                'start_time': s.date_time.isoformat()
            })

    artist.upcoming_shows = upcoming_shows
    artist.past_shows = past_shows
    artist.upcoming_shows_count = len(upcoming_shows)
    artist.past_shows_count = len(past_shows)

    return render_template('pages/show_artist.html', artist=artist)

#  Update
#  ----------------------------------------------------------------


@site.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    # populate form with fields from artist with ID <artist_id>
    artist = Artist.query.get(artist_id)
    form = ArtistForm(obj=artist)
    fix_genres(artist, form)

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@site.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    form = ArtistForm()
    artist = Artist.query.get(artist_id)

    if form.validate_on_submit():
        try:
            print(form.genres.data)
            form.populate_obj(artist)
            artist.create()

            flash('Artist ' + form.name.data + ' was successfully updated!')
            return redirect(url_for('site.show_artist', artist_id=artist.id))
        except:
            db.session.rollback()
            print(sys.exc_info())
            flash('An error occurred. Artist ' +
                  form.name.data + ' could not be updated.')
        finally:
            db.session.close()
    else:
        flash('An error occurred. Artist ' +
              form.name.data + ' could not be updated.')
        print(form.errors)

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@site.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    # populate form with values from venue with ID <venue_id>
    venue = Venue.query.get(venue_id)
    form = VenueForm(obj=venue)
    fix_genres(venue, form)
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@site.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    form = VenueForm()
    venue = Venue.query.get(venue_id)

    if form.validate_on_submit():
        try:
            print(form.genres.data)
            form.populate_obj(venue)
            venue.create()

            flash('Venue ' + form.name.data + ' was successfully updated!')
            return redirect(url_for('site.show_venue', venue_id=venue.id))
        except:
            db.session.rollback()
            print(sys.exc_info())
            flash('An error occurred. Venue ' +
                  form.name.data + ' could not be updated.')
        finally:
            db.session.close()
    else:
        flash('An error occurred. Venue ' +
              form.name.data + ' could not be updated.')
        print(form.errors)

    return render_template('forms/edit_venue.html', form=form, venue=venue)

#  Create Artist
#  ----------------------------------------------------------------


@site.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@site.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # insert form data as a new Venue record in the db, instead
    # modify data to be the data object returned from db insertion
    form = ArtistForm()
    if form.validate_on_submit():
        try:
            new_artist = Artist(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                phone=form.phone.data,
                image_link=form.image_link.data,
                genres=form.genres.data,
                facebook_link=form.facebook_link.data,
                website_link=form.website_link.data,
                seeking_venue=form.seeking_venue.data,
                seeking_description=form.seeking_description.data
            )

            new_artist.create()

            # on successful db insert, flash success
            flash('Artist ' + form.name.data + ' was successfully listed!')
            return redirect(url_for('site.show_artist', artist_id=new_artist.id))
            # on unsuccessful db insert, flash an error instead.
            # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
        except:
            db.session.rollback()
            print(sys.exc_info())
            flash('An error occurred. Artist ' +
                  form.name.data + ' could not be listed.')
        finally:
            db.session.close()
    else:
        flash('An error occurred. Artist ' +
              form.name.data + ' could not be listed.')
        print(form.errors)

    return render_template('forms/new_artist.html', form=form)

#  Shows
#  ----------------------------------------------------------------


@site.route('/shows')
def shows():
    shows = Show.query.all()
    data = []
    for s in shows:
        data.append({
            'venue_id': s.venue_id,
            'venue_name': s.venue.name,
            'artist_id': s.artist_id,
            'artist_name': s.artist.name,
            'artist_image_link': s.artist.image_link,
            'start_time': s.date_time.isoformat()
        })
    return render_template('pages/shows.html', shows=data)


@site.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@site.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # insert form data as a new Show record in the db, instead
    form = ShowForm()
    if form.validate_on_submit():
        try:
            new_show = Show(
                artist_id=form.artist_id.data,
                venue_id=form.venue_id.data,
                date_time=form.start_time.data)

            new_show.create()

            # on successful db insert, flash success
            flash('Show was successfully listed!')
            return redirect(url_for('site.shows'))

# on unsuccessful db insert, flash an error instead.
        except:
            db.session.rollback()
            print(sys.exc_info())
            flash('An error occurred. Show could not be listed.')
        finally:
            db.session.close()
    else:
        flash('An error occurred. Show could not be listed.')
        print(form.errors)
    return render_template('forms/new_show.html', form=form)


@site.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@site.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500
