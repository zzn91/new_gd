from app import app
from register_bp import register_bp

register_bp(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8009)