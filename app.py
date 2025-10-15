from flask import Flask
from flask_socketio import SocketIO
from api.routes import api_bp
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__, static_folder='dashboard', static_url_path='/dashboard')
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET', 'secret!')

socketio = SocketIO(app, async_mode='threading', cors_allowed_origins="*")

app.register_blueprint(api_bp, url_prefix='/api')

@app.route('/')
def index():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    socketio.run(app, host=os.getenv('HOST', '127.0.0.1'), port=int(os.getenv('PORT', 5000)))
