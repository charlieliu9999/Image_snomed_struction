from flask import Flask

def create_app():
    app = Flask(__name__)

    # Import and register blueprints
    from api.reports_api import reports_bp
    from api.terminology_api import terminology_bp

    app.register_blueprint(reports_bp, url_prefix='/api/v1/reports')
    app.register_blueprint(terminology_bp, url_prefix='/api/v1/terminology')

    @app.route('/')
    def hello():
        return "Imaging Report Backend is running!"

    return app

if __name__ == '__main__':
    app = create_app()
    # Note: For development, app.run() is fine.
    # For production, use a proper WSGI server like Gunicorn.
    # The sandbox might not support running a persistent server,
    # so this __main__ block is for conceptual structure.
    # For the purpose of this task, we'll assume the structure is set up
    # and individual endpoint handlers will be tested/verified conceptually.
    print("Flask app configured. To run (locally, outside sandbox): flask run")
