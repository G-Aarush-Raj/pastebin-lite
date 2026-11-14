
import os
import uuid
import html

from datetime import datetime, timezone, timedelta

from flask import (
    Flask,
    jsonify,
    request,
    Response,
    url_for
)

from flask_cors import CORS
from dotenv import load_dotenv

from sqlalchemy import text, update
from sqlalchemy.exc import SQLAlchemyError

from extensions import db


# Load environment variables from .env
load_dotenv()


def create_app():

    # -----------------------------------
    # 1. Create Flask application
    # -----------------------------------

    app = Flask(__name__)

    # -----------------------------------
    # 2. Database configuration
    # -----------------------------------

    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL is missing")

    # Use psycopg 3 driver
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace(
            "postgresql://",
            "postgresql+psycopg://",
            1
        )

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_recycle": 300
    }

    # -----------------------------------
    # 3. Initialize extensions
    # -----------------------------------

    db.init_app(app)

    frontend_origin = os.getenv(
        "FRONTEND_ORIGIN",
        "http://localhost:5173"
    )

    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": frontend_origin
            }
        }
    )

    # Import models after initializing extensions
    from models import Paste

    # -----------------------------------
    # Helper: Get current time
    # -----------------------------------

    def get_current_time():

        # Deterministic time for automated testing
        if os.getenv("TEST_MODE") == "1":

            test_now = request.headers.get("x-test-now-ms")

            if test_now is not None:

                try:
                    milliseconds = int(test_now)

                    return datetime.fromtimestamp(
                        milliseconds / 1000,
                        tz=timezone.utc
                    )

                except (ValueError, OverflowError, OSError):
                    raise ValueError(
                        "Invalid x-test-now-ms header"
                    )

        return datetime.now(timezone.utc)

    # -----------------------------------
    # Helper: Check paste availability
    # -----------------------------------

    def is_paste_available(paste, now):

        if paste is None:
            return False

        # Check time-based expiry
        if paste.expires_at is not None:

            expires_at = paste.expires_at

            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(
                    tzinfo=timezone.utc
                )

            if expires_at <= now:
                return False

        # Check view-count limit
        if paste.max_views is not None:

            if paste.view_count >= paste.max_views:
                return False

        return True

    # -----------------------------------
    # Helper: Format datetime
    # -----------------------------------

    def format_datetime(value):

        if value is None:
            return None

        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)

        return value.astimezone(timezone.utc).isoformat(
            timespec="milliseconds"
        ).replace("+00:00", "Z")

    # -----------------------------------
    # 1. Health Check API
    # GET /api/healthz
    # -----------------------------------

    @app.route("/api/healthz", methods=["GET"])
    def health_check():

        try:

            db.session.execute(text("SELECT 1"))

            return jsonify({
                "ok": True
            }), 200

        except SQLAlchemyError:

            app.logger.exception(
                "Database health check failed"
            )

            db.session.rollback()

            return jsonify({
                "ok": False
            }), 503

    # -----------------------------------
    # 2. Create Paste API
    # POST /api/pastes
    # -----------------------------------

    @app.route("/api/pastes", methods=["POST"])
    def create_paste():

        data = request.get_json(silent=True)

        # Validate JSON body
        if not isinstance(data, dict):

            return jsonify({
                "error": "Request body must be a JSON object"
            }), 400

        content = data.get("content")

        # Content must be a non-empty string
        if not isinstance(content, str) or len(content) == 0:

            return jsonify({
                "error": "Content is required and must be a non-empty string"
            }), 400

        ttl_seconds = data.get("ttl_seconds")

        max_views = data.get("max_views")

        # Validate TTL
        if ttl_seconds is not None:

            if (
                isinstance(ttl_seconds, bool)
                or not isinstance(ttl_seconds, int)
                or ttl_seconds < 1
            ):

                return jsonify({
                    "error": "ttl_seconds must be an integer >= 1"
                }), 400

        # Validate maximum views
        if max_views is not None:

            if (
                isinstance(max_views, bool)
                or not isinstance(max_views, int)
                or max_views < 1
            ):

                return jsonify({
                    "error": "max_views must be an integer >= 1"
                }), 400

        # Get current time
        try:

            now = get_current_time()

        except ValueError as error:

            return jsonify({
                "error": str(error)
            }), 400

        # Generate unique paste ID
        paste_id = str(uuid.uuid4())

        # Calculate expiration time
        expires_at = None

        if ttl_seconds is not None:

            expires_at = now + timedelta(
                seconds=ttl_seconds
            )

        # Create database object
        paste = Paste(
            id=paste_id,
            content=content,
            expires_at=expires_at,
            max_views=max_views,
            view_count=0
        )

        try:

            db.session.add(paste)

            db.session.commit()

        except SQLAlchemyError:

            db.session.rollback()

            app.logger.exception(
                "Paste creation failed"
            )

            return jsonify({
                "error": "Unable to create paste"
            }), 500

        # Generate shareable URL dynamically
        paste_url = (
            request.host_url.rstrip("/")
            + url_for(
                "view_paste",
                paste_id=paste_id
            )
        )

        return jsonify({
            "id": paste_id,
            "url": paste_url
        }), 201

    # -----------------------------------
    # 3. Fetch Paste API
    # GET /api/pastes/:id
    # -----------------------------------

    @app.route(
        "/api/pastes/<string:paste_id>",
        methods=["GET"]
    )
    def get_paste(paste_id):

        try:

            now = get_current_time()

        except ValueError as error:

            return jsonify({
                "error": str(error)
            }), 400

        try:

            # Atomic database update:
            # Check availability and increment views
            # in the same SQL statement.

            statement = (
                update(Paste)

                .where(
                    Paste.id == paste_id,

                    (
                        Paste.expires_at.is_(None)
                        | (Paste.expires_at > now)
                    ),

                    (
                        Paste.max_views.is_(None)
                        | (Paste.view_count < Paste.max_views)
                    )
                )

                .values(
                    view_count=Paste.view_count + 1
                )

                .returning(
                    Paste.content,
                    Paste.max_views,
                    Paste.view_count,
                    Paste.expires_at
                )
            )

            result = db.session.execute(
                statement
            ).first()

            db.session.commit()

            if result is None:

                return jsonify({
                    "error": "Paste not found or unavailable"
                }), 404

            content, max_views, view_count, expires_at = result

            # Calculate remaining views
            remaining_views = None

            if max_views is not None:

                remaining_views = max_views - view_count

            return jsonify({
                "content": content,
                "remaining_views": remaining_views,
                "expires_at": format_datetime(expires_at)
            }), 200

        except SQLAlchemyError:

            db.session.rollback()

            app.logger.exception(
                "Paste retrieval failed"
            )

            return jsonify({
                "error": "Unable to retrieve paste"
            }), 500

    # -----------------------------------
    # 4. View Paste HTML
    # GET /p/:id
    # -----------------------------------

    @app.route(
        "/p/<string:paste_id>",
        methods=["GET"]
    )
    def view_paste(paste_id):

        try:

            now = get_current_time()

        except ValueError:

            return Response(
                "Invalid test time",
                status=400,
                mimetype="text/plain"
            )

        try:

            paste = db.session.get(
                Paste,
                paste_id
            )

            # Check paste availability
            if not is_paste_available(paste, now):

                return Response(
                    "Paste not found or unavailable",
                    status=404,
                    mimetype="text/plain"
                )

            # Escape user content to prevent XSS
            safe_content = html.escape(
                paste.content
            )

            html_page = f"""
            <!DOCTYPE html>
            <html lang="en">

            <head>
                <meta charset="UTF-8">

                <meta name="viewport"
                      content="width=device-width, initial-scale=1.0">

                <title>Pastebin Lite</title>

                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        background: #f4f4f4;
                        padding: 40px;
                        margin: 0;
                    }}

                    h2 {{
                        color: #333;
                    }}

                    pre {{
                        background: white;
                        padding: 24px;
                        border-radius: 8px;
                        white-space: pre-wrap;
                        overflow-wrap: anywhere;
                        line-height: 1.6;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                    }}
                </style>

            </head>

            <body>

                <h2>Pastebin Lite</h2>

                <pre>{safe_content}</pre>

            </body>

            </html>
            """

            return Response(
                html_page,
                status=200,
                mimetype="text/html"
            )

        except SQLAlchemyError:

            db.session.rollback()

            app.logger.exception(
                "HTML paste retrieval failed"
            )

            return Response(
                "Internal server error",
                status=500,
                mimetype="text/plain"
            )

    # Return configured application
    return app


# -----------------------------------
# Create Flask application
# -----------------------------------

app = create_app()


# -----------------------------------
# Automatically create database tables
# -----------------------------------

with app.app_context():

    from models import Paste

    db.create_all()


# -----------------------------------
# Run development server
# -----------------------------------

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
