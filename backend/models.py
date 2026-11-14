
from datetime import datetime, timezone

from extensions import db


class Paste(db.Model):
    __tablename__ = "pastes"

    id = db.Column(
        db.String(36),
        primary_key=True
    )

    content = db.Column(
        db.Text,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    expires_at = db.Column(
        db.DateTime(timezone=True),
        nullable=True
    )

    max_views = db.Column(
        db.Integer,
        nullable=True
    )

    view_count = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )
