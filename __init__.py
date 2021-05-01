#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#
import os
from fyyur.app import create_app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app = create_app()
    app.run(host='0.0.0.0', port=port)

