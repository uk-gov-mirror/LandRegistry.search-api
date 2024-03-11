from contextlib import contextmanager

import psycopg2
from flask import current_app
from geoalchemy2 import Geometry
from llc_schema_dto import llc_schema
from search_api import config
from search_api.exceptions import ApplicationError
from search_api.extensions import db
from search_api.utilities.organisation_name import get_latest_organisation_name
from sqlalchemy import desc
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.schema import FetchedValue


@contextmanager
def getcursor():  # pragma: no cover
    con = db.engine.raw_connection()
    try:
        yield con.cursor()
    finally:
        con.commit()
        con.close()


def get_charge_type(self):
    # Gets the charge type from the llc_item and search the charge categories table
    # for the display_name corresponding to that charge type. If there is an error, it is logged
    # and the original charge type is returned.
    charge_type = self.llc_item['charge-type']
    with getcursor() as cur:
        try:
            cur.execute("SELECT display_name FROM charge_categories WHERE (display_name_valid->'valid_display_names')\
                        ::jsonb ? '{}' AND parent_id is null;".format(charge_type))
            row = cur.fetchone()
            if row is not None:
                charge_type = row[0]

        except psycopg2.Error as e:
            current_app.logger.exception('Application Error: %s', repr(e))
            raise ApplicationError("Error Getting Charge Category", "400")

    return charge_type


def get_charge_sub_cat(self):
    # Gets the charge sub category from the llc_item and search the charge categories table
    # for the display_name corresponding to that charge sub cat. If there is an error, it is logged
    # and the original charge sub cat is returned.
    charge_sub_cat = self.llc_item['charge-sub-category']
    with getcursor() as cur:
        try:
            cur.execute("SELECT display_name FROM charge_categories WHERE (display_name_valid->'valid_display_names')\
                        ::jsonb ? '{}' AND parent_id is not null;".format(charge_sub_cat))
            row = cur.fetchone()
            if row is not None:
                charge_sub_cat = row[0]

        except psycopg2.Error as e:
            current_app.logger.exception('Application Error: %s', repr(e))
            raise ApplicationError("Error Getting Charge Sub Category", "400")

    return charge_sub_cat


def get_stat_prov(self):
    # Gets the stat Prov from the llc_item and search the statutory provisions table
    # for the display_title corresponding to that stat prov. If there is an error, it is logged
    # and the original stat prov is returned.
    stat_prov = self.llc_item['statutory-provision']
    with getcursor() as cur:
        try:
            cur.execute("SELECT display_title FROM statutory_provision WHERE title = %s", (stat_prov,))
            row = cur.fetchone()
            if row is not None:
                stat_prov = row[0]

        except psycopg2.Error as e:
            current_app.logger.exception('Application Error: %s', repr(e))
            raise ApplicationError("Error Getting Statutory Provision", "400")

    return stat_prov


class LocalLandCharge(db.Model):
    __tablename__ = 'local_land_charge'

    id = db.Column(db.BigInteger, primary_key=True)
    geometry = db.relationship('GeometryFeature', back_populates='local_land_charge', cascade="all, delete-orphan")
    type = db.Column(db.String, nullable=False)
    llc_item = db.Column(JSONB, nullable=False)
    cancelled = db.Column(db.Boolean, nullable=False)
    further_information_reference = db.Column(db.String, nullable=True)
    llc_id = db.Column(db.String, nullable=True)

    def __init__(self, id, geometry, type, llc_item, cancelled, further_information_reference, llc_id):
        self.id = id
        self.geometry = geometry
        self.type = type
        self.llc_item = llc_item
        self.cancelled = cancelled
        self.further_information_reference = further_information_reference
        self.llc_id = llc_id

    def to_dict(self):
        return {
            "id": self.id,
            "display-id": self.llc_id,
            "geometry": self.llc_item['geometry'],
            "type": self.type,
            "item": llc_schema.convert(self.llc_item, config.SCHEMA_VERSION),
            "cancelled": self.cancelled,
            "entry_number": self.entry_number
        }

    def to_display_dict(self):
        return {
            "id": self.id,
            "display-id": self.llc_id
        }

    def to_charge_display_dict(self):
        # Get the stat_prov from the JSON object and then replace with the display version
        if self.llc_item.get("statutory-provision"):
            self.llc_item['statutory-provision'] = get_stat_prov(self)

        # Get the chargetype  from the JSON object and then replace with the display version
        if self.llc_item.get("charge-type"):
            self.llc_item['charge-type'] = get_charge_type(self)

        # Get the charge-sub category from the JSON object and then replace with the display version
        if self.llc_item.get("charge-sub-category"):
            self.llc_item['charge-sub-category'] = get_charge_sub_cat(self)

        # Get the originating-authority from the JSON object and then replace with the display version
        if self.llc_item.get("originating-authority"):
            self.llc_item['originating-authority'] = \
                get_latest_organisation_name(self.llc_item['originating-authority'])

        # Get the migrating-authority from the JSON object and then replace with the display version
        if self.llc_item.get("migrating-authority"):
            self.llc_item['migrating-authority'] = get_latest_organisation_name(self.llc_item['migrating-authority'])

        return {
            "id": self.id,
            "display-id": self.llc_id,
            "geometry": self.llc_item['geometry'],
            "type": self.llc_item['charge-type'],
            "item": llc_schema.convert(self.llc_item, config.SCHEMA_VERSION),
            "cancelled": self.cancelled,
            "entry_number": self.entry_number
        }

    @hybrid_property
    def entry_number(self):
        latest = LocalLandChargeHistory.query.filter(LocalLandChargeHistory.id == self.id).order_by(
            desc(LocalLandChargeHistory.entry_number)).limit(1).first()
        return latest.entry_number


class LocalLandChargeHistory(db.Model):
    __tablename__ = 'local_land_charge_history'

    id = db.Column(db.BigInteger, primary_key=True)
    llc_item = db.Column(JSONB, nullable=False)
    cancelled = db.Column(db.Boolean, nullable=False)
    item_changes = db.Column(JSONB)
    entry_number = db.Column(db.BigInteger, primary_key=True, index=True)
    entry_timestamp = db.Column(db.DateTime, nullable=False)

    def __init__(self, id, llc_item, cancelled, item_changes, entry_number, entry_timestamp):
        self.id = id
        self.llc_item = llc_item
        self.cancelled = cancelled
        self.item_changes = item_changes
        self.entry_number = entry_number
        self.entry_timestamp = entry_timestamp

    def to_dict(self):
        history = {
            "entry-timestamp": self.entry_timestamp.isoformat(),
            "cancelled": self.cancelled,
            "entry-number": self.entry_number,
            "llc-item": self.llc_item
        }

        if self.item_changes is not None:
            history["item-changes"] = self.item_changes

        if "author" in self.llc_item:
            history["author"] = self.llc_item["author"]

        return history


class GeometryFeature(db.Model):
    __tablename__ = 'geometry_feature'

    id = db.Column(db.BigInteger, primary_key=True)
    local_land_charge_id = db.Column(db.BigInteger, db.ForeignKey('local_land_charge.id'), primary_key=True)
    local_land_charge = db.relationship('LocalLandCharge', back_populates='geometry', uselist=False)
    geometry = db.Column(Geometry(srid=27700), nullable=False)

    def __init__(self, local_land_charge, geometry):
        self.local_land_charge = local_land_charge
        self.geometry = geometry


class ChargeCategory(db.Model):
    __tablename__ = 'charge_categories'

    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String, nullable=False)
    display_name = db.Column(db.String, nullable=False)
    parent_id = db.Column(db.BigInteger, db.ForeignKey('charge_categories.id'), nullable=True)
    display_order = db.Column(db.Integer, nullable=False)
    add_permission = db.Column('add_permission', db.String(), nullable=False, server_default=FetchedValue())
    vary_permission = db.Column('vary_permission', db.String(), nullable=False, server_default=FetchedValue())
    cancel_permission = db.Column('cancel_permission', db.String(), nullable=False, server_default=FetchedValue())
    add_on_behalf_permission = db.Column('add_on_behalf_permission', db.String(), nullable=False,
                                         server_default=FetchedValue())
    display_name_valid = db.Column(JSONB)
    sensitive = db.Column(db.Boolean)
    selectable = db.Column(db.Boolean)
    charge_category = db.relationship('ChargeCategory', backref=db.backref('sub_categories'), remote_side=[id])
