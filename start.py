

from app import app




from views.response import response_bp
app.register_blueprint(response_bp, url_prefix='')



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8009)