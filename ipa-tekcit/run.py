""" This is the main module to run Flask """
# System imports

# Third-party imports
from flask import Flask

# Local source tree imports
from api import ticket

app = Flask(__name__)

# Expose application endpoints
app.register_blueprint(ticket.api)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9090, threaded=True)
