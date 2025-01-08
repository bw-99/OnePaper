from flask import Flask
from routes import home_route, paper_route, chat_bp
from socketio_instance import socketio  # Import socketio from the new module

# Flask 인스턴스 생성
app = Flask(__name__)
socketio.init_app(app)  # Initialize socketio with the Flask app

# Blueprint 등록
app.register_blueprint(home_route)
app.register_blueprint(paper_route)
app.register_blueprint(chat_bp)

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", debug=True)
