# -*- coding: utf-8 -*-
__author__ = "Paul Schifferer <dm@sweetrpg.com>"
"""
"""

import logging
from sweetrpg_model_core.model.base import Model


class Store(Model):
    """A model object representing a key-value store."""

    def __init__(self, *args, **kwargs):
        """Creates a new Store object."""
        logging.debug("args: %s, kwargs: %s", args, kwargs)

        super().__init__(*args, **kwargs)

        self.name = kwargs.get("name")
        self.description = kwargs.get("description")
        self.tags = kwargs.get("tags")
