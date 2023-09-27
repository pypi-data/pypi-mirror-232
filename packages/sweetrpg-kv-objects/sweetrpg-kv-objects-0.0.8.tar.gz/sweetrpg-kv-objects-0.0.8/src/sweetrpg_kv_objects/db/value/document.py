# -*- coding: utf-8 -*-
__author__ = "Paul Schifferer <dm@sweetrpg.com>"
"""
Value document for MongoDB.
"""

from datetime import datetime
from mongoengine import Document, fields
from sweetrpg_kv_objects.db.embedded.property.document import PropertyDocument
from sweetrpg_kv_objects.db.embedded.tag.document import TagDocument


class ValueDocument(Document):
    """
    A mapping object to convert MongoDB data to a Value object.
    """

    meta = {
        "indexes": [
            {"name": "value_key_snapshot", "fields": ["key", "snapshot"]},
        ],
        "db_alias": "default",
        "collection": "values",
        "strict": False,
    }

    # basic properties
    key = fields.ReferenceField("KeyDocument")
    snapshot = fields.ReferenceField("SnapshotDocument")
    value = fields.StringField(required=True)
    tags = fields.ListField(fields.EmbeddedDocumentField(TagDocument))

    # audit properties
    created_at = fields.DateTimeField(default=datetime.utcnow, required=True)
    created_by = fields.StringField(default="system", required=True)
    updated_at = fields.DateTimeField(default=datetime.utcnow, required=True)
    updated_by = fields.StringField(default="system", required=True)
    deleted_at = fields.DateTimeField(null=True)
    deleted_by = fields.StringField(null=True)
