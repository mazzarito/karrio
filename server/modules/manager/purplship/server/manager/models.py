from functools import partial
from typing import List, cast, Optional
from django.db import models

from purplship.server.core.utils import identity
from purplship.server.providers.models import Carrier
from purplship.server.core.models import OwnedEntity, uuid
from purplship.server.core.serializers import (
    WEIGHT_UNIT,
    DIMENSION_UNIT,
    CURRENCIES,
    SHIPMENT_STATUS,
    TRACKER_STATUS,
    COUNTRIES,
    INCOTERMS,
)


class Address(OwnedEntity):
    class Meta:
        db_table = "address"
        verbose_name = "Address"
        verbose_name_plural = "Addresses"
        ordering = ["-created_at"]

    id = models.CharField(
        max_length=50,
        primary_key=True,
        default=partial(uuid, prefix="adr_"),
        editable=False,
    )

    postal_code = models.CharField(max_length=10, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    federal_tax_id = models.CharField(max_length=50, null=True, blank=True)
    state_tax_id = models.CharField(max_length=50, null=True, blank=True)
    person_name = models.CharField(max_length=50, null=True, blank=True)
    company_name = models.CharField(max_length=50, null=True, blank=True)
    country_code = models.CharField(max_length=20, choices=COUNTRIES)
    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=50, null=True, blank=True)

    state_code = models.CharField(max_length=20, null=True, blank=True)
    suburb = models.CharField(max_length=20, null=True, blank=True)
    residential = models.BooleanField(null=True)

    address_line1 = models.CharField(max_length=100, null=True, blank=True)
    address_line2 = models.CharField(max_length=100, null=True, blank=True)

    validate_location = models.BooleanField(null=True)
    validation = models.JSONField(blank=True, null=True)


class Parcel(OwnedEntity):
    class Meta:
        db_table = "parcel"
        verbose_name = "Parcel"
        verbose_name_plural = "Parcels"
        ordering = ["-created_at"]

    id = models.CharField(
        max_length=50,
        primary_key=True,
        default=partial(uuid, prefix="pcl_"),
        editable=False,
    )

    weight = models.FloatField(blank=True, null=True)
    width = models.FloatField(blank=True, null=True)
    height = models.FloatField(blank=True, null=True)
    length = models.FloatField(blank=True, null=True)
    packaging_type = models.CharField(max_length=50, null=True, blank=True)
    package_preset = models.CharField(max_length=50, null=True, blank=True)
    description = models.CharField(max_length=250, null=True, blank=True)
    content = models.CharField(max_length=100, null=True, blank=True)
    is_document = models.BooleanField(default=False, blank=True, null=True)
    weight_unit = models.CharField(
        max_length=2, choices=WEIGHT_UNIT, null=True, blank=True
    )
    dimension_unit = models.CharField(
        max_length=2, choices=DIMENSION_UNIT, null=True, blank=True
    )


class Commodity(OwnedEntity):
    class Meta:
        db_table = "commodity"
        verbose_name = "Commodity"
        verbose_name_plural = "Commodities"
        ordering = ["-created_at"]

    id = models.CharField(
        max_length=50,
        primary_key=True,
        default=partial(uuid, prefix="cdt_"),
        editable=False,
    )

    weight = models.FloatField(blank=True, null=True)
    description = models.CharField(max_length=250, null=True, blank=True)
    quantity = models.IntegerField(blank=True, null=True)
    sku = models.CharField(max_length=100, null=True, blank=True)
    value_amount = models.FloatField(blank=True, null=True)
    weight_unit = models.CharField(
        max_length=2, choices=WEIGHT_UNIT, null=True, blank=True
    )
    value_currency = models.CharField(
        max_length=3, choices=CURRENCIES, null=True, blank=True
    )
    origin_country = models.CharField(
        max_length=3, choices=COUNTRIES, null=True, blank=True
    )


class CustomsManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related(
                "commodities",
                "created_by",
            )
        )


class Customs(OwnedEntity):
    DIRECT_PROPS = [
        "content_description",
        "content_type",
        "incoterm",
        "commercial_invoice",
        "certify",
        "duty",
        "created_by",
        "signer",
        "invoice",
        "invoice_date",
        "options",
    ]
    RELATIONAL_PROPS = ["commodities"]
    objects = CustomsManager()

    class Meta:
        db_table = "customs"
        verbose_name = "Customs Info"
        verbose_name_plural = "Customs Info"
        ordering = ["-created_at"]

    id = models.CharField(
        max_length=50,
        primary_key=True,
        default=partial(uuid, prefix="cst_"),
        editable=False,
    )

    certify = models.BooleanField(null=True)
    commercial_invoice = models.BooleanField(null=True)
    content_type = models.CharField(max_length=50, null=True, blank=True)
    content_description = models.CharField(max_length=250, null=True, blank=True)
    incoterm = models.CharField(max_length=20, choices=INCOTERMS)
    invoice = models.CharField(max_length=50, null=True, blank=True)
    invoice_date = models.DateField(null=True, blank=True)
    signer = models.CharField(max_length=50, null=True, blank=True)

    duty = models.JSONField(
        blank=True, null=True, default=partial(identity, value=None)
    )
    options = models.JSONField(
        blank=True, null=True, default=partial(identity, value={})
    )

    # System Reference fields

    commodities = models.ManyToManyField("Commodity", blank=True)

    def delete(self, *args, **kwargs):
        self.commodities.all().delete()
        return super().delete(*args, **kwargs)


class PickupManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related(
                "pickup_carrier",
                "shipments",
                "created_by",
            )
        )


class Pickup(OwnedEntity):
    DIRECT_PROPS = [
        "confirmation_number",
        "pickup_date",
        "instruction",
        "package_location",
        "ready_time",
        "closing_time",
        "test_mode",
        "pickup_charge",
        "created_by",
    ]
    objects = PickupManager()

    class Meta:
        db_table = "pickup"
        verbose_name = "Pickup"
        verbose_name_plural = "Pickups"
        ordering = ["-created_at"]

    id = models.CharField(
        max_length=50,
        primary_key=True,
        default=partial(uuid, prefix="pck_"),
        editable=False,
    )
    confirmation_number = models.CharField(max_length=50, unique=True, blank=False)
    test_mode = models.BooleanField(null=False)
    pickup_date = models.DateField(blank=False)
    ready_time = models.CharField(max_length=5, blank=False)
    closing_time = models.CharField(max_length=5, blank=False)
    instruction = models.CharField(max_length=200, null=True, blank=True)
    package_location = models.CharField(max_length=200, null=True, blank=True)

    options = models.JSONField(
        blank=True, null=True, default=partial(identity, value={})
    )
    pickup_charge = models.JSONField(blank=True, null=True)
    address = models.ForeignKey(
        "Address", on_delete=models.CASCADE, blank=True, null=True
    )

    # System Reference fields

    pickup_carrier = models.ForeignKey(Carrier, on_delete=models.CASCADE)
    shipments = models.ManyToManyField("Shipment", related_name="pickup_shipments")

    def delete(self, *args, **kwargs):
        handle = self.address or super()
        return handle.delete(*args, **kwargs)

    # Computed properties

    @property
    def carrier_id(self) -> str:
        return cast(Carrier, self.pickup_carrier).carrier_id

    @property
    def carrier_name(self) -> str:
        return cast(Carrier, self.pickup_carrier).data.carrier_name

    @property
    def parcels(self) -> List[Parcel]:
        return sum(
            [list(shipment.parcels.all()) for shipment in self.shipments.all()], []
        )

    @property
    def tracking_numbers(self) -> List[str]:
        return [shipment.tracking_number for shipment in self.shipments.all()]


class TrackingManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related("tracking_carrier", "created_by", "shipment")
        )


class Tracking(OwnedEntity):
    objects = TrackingManager()

    class Meta:
        db_table = "tracking-status"
        verbose_name = "Tracking Status"
        verbose_name_plural = "Tracking Statuses"
        ordering = ["-created_at"]

    id = models.CharField(
        max_length=50,
        primary_key=True,
        default=partial(uuid, prefix="trk_"),
        editable=False,
    )

    status = models.CharField(
        max_length=25, choices=TRACKER_STATUS, default=TRACKER_STATUS[0][0]
    )
    tracking_number = models.CharField(max_length=50)
    events = models.JSONField(
        blank=True, null=True, default=partial(identity, value=[])
    )
    delivered = models.BooleanField(blank=True, null=True, default=False)
    estimated_delivery = models.DateField(null=True, blank=True)
    test_mode = models.BooleanField(null=False)
    messages = models.JSONField(
        blank=True, null=True, default=partial(identity, value=[])
    )

    # System Reference fields

    tracking_carrier = models.ForeignKey(Carrier, on_delete=models.CASCADE)
    shipment = models.ForeignKey(
        "Shipment", on_delete=models.CASCADE, related_name="tracker", null=True
    )

    # Computed properties

    @property
    def carrier_id(self) -> str:
        return cast(Carrier, self.tracking_carrier).carrier_id

    @property
    def carrier_name(self) -> str:
        return cast(Carrier, self.tracking_carrier).data.carrier_name

    @property
    def pending(self) -> bool:
        return len(self.events) == 0 or (
            len(self.events) == 1 and self.events[0].get("code") == "CREATED"
        )


class ShipmentManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related(
                "shipper",
                "recipient",
                "parcels",
                "carriers",
                "selected_rate_carrier",
                "created_by",
                "tracker",
            )
        )


class Shipment(OwnedEntity):
    DIRECT_PROPS = [
        "label",
        "options",
        "services",
        "status",
        "meta",
        "label_type",
        "tracking_number",
        "tracking_url",
        "shipment_identifier",
        "test_mode",
        "messages",
        "rates",
        "payment",
        "created_by",
        "reference",
    ]
    RELATIONAL_PROPS = ["shipper", "recipient", "parcels", "customs", "selected_rate"]
    objects = ShipmentManager()

    class Meta:
        db_table = "shipment"
        verbose_name = "Shipment"
        verbose_name_plural = "Shipments"
        ordering = ["-created_at"]

    id = models.CharField(
        max_length=50,
        primary_key=True,
        default=partial(uuid, prefix="shp_"),
        editable=False,
    )
    status = models.CharField(
        max_length=50, choices=SHIPMENT_STATUS, default=SHIPMENT_STATUS[0][0]
    )

    recipient = models.ForeignKey(
        "Address", on_delete=models.CASCADE, related_name="recipient"
    )
    shipper = models.ForeignKey(
        "Address", on_delete=models.CASCADE, related_name="shipper"
    )
    label_type = models.CharField(max_length=25, null=True, blank=True)

    tracking_number = models.CharField(max_length=50, null=True, blank=True)
    shipment_identifier = models.CharField(max_length=50, null=True, blank=True)
    label = models.TextField(max_length=None, null=True, blank=True)
    tracking_url = models.TextField(max_length=None, null=True, blank=True)
    test_mode = models.BooleanField(null=False)
    reference = models.CharField(max_length=100, null=True, blank=True)

    customs = models.ForeignKey(
        "Customs", on_delete=models.SET_NULL, blank=True, null=True
    )

    selected_rate = models.JSONField(blank=True, null=True)
    payment = models.JSONField(
        blank=True, null=True, default=partial(identity, value=None)
    )
    options = models.JSONField(
        blank=True, null=True, default=partial(identity, value={})
    )
    services = models.JSONField(
        blank=True, null=True, default=partial(identity, value=[])
    )
    messages = models.JSONField(
        blank=True, null=True, default=partial(identity, value=[])
    )
    meta = models.JSONField(blank=True, null=True, default=partial(identity, value={}))

    # System Reference fields

    rates = models.JSONField(blank=True, null=True, default=partial(identity, value=[]))
    parcels = models.ManyToManyField("Parcel", related_name="shipment_parcels")
    carriers = models.ManyToManyField(
        Carrier, blank=True, related_name="rating_carriers"
    )
    selected_rate_carrier = models.ForeignKey(
        Carrier,
        on_delete=models.CASCADE,
        related_name="selected_rate_carrier",
        blank=True,
        null=True,
    )

    def delete(self, *args, **kwargs):
        self.parcels.all().delete()
        self.customs and self.customs.delete()
        return super().delete(*args, **kwargs)

    # Computed properties

    @property
    def carrier_id(self) -> str:
        return cast(Carrier, self.selected_rate_carrier).carrier_id

    @property
    def carrier_name(self) -> str:
        return cast(Carrier, self.selected_rate_carrier).carrier_name

    @property
    def tracker_id(self) -> Optional[str]:
        return getattr(self.tracker.first(), "id", None)

    @property
    def carrier_ids(self) -> List[str]:
        return [carrier.carrier_id for carrier in self.carriers.all()]

    @property
    def selected_rate_id(self) -> str:
        return (
            cast(dict, self.selected_rate).get("id")
            if self.selected_rate is not None
            else None
        )

    @property
    def service(self) -> str:
        return (
            cast(dict, self.selected_rate).get("service")
            if self.selected_rate is not None
            else None
        )