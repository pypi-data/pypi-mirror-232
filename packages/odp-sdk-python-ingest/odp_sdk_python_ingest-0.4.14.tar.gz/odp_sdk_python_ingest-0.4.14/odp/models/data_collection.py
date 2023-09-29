"""Data collection model."""
from datetime import datetime

from pydantic import AnyUrl, BaseModel

from odp.models.common.common_subtypes import License, Metadata, Spec
from odp.models.common.contact_info import Contact


class DataCollectionSpecDistribution(BaseModel):
    """Data collection spec distribution class."""

    published_by: Contact
    published_date: datetime
    website: AnyUrl
    license: License


class DataCollectionSpec(Spec):
    """Data collection spec."""

    distribution: DataCollectionSpecDistribution


class DataCollection(BaseModel):
    """Data collection class."""

    metadata: Metadata
    spec: DataCollectionSpec
