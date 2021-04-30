#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import os
import logging
from logging import Formatter, FileHandler
from flask import Flask
from flask_moment import Moment
from flask_migrate import Migrate
import dateutil.parser
import babel
from datetime import datetime


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format="EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format="EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

from models import db
db.init_app(app)
migrate = Migrate(app,db)
app.jinja_env.filters['datetime'] = format_datetime

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
import routes
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

