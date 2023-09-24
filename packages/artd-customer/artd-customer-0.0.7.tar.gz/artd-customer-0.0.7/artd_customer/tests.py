from django.test import TestCase
from artd_customer.utils.generators import generate_random_string, generate_random_email
from artd_location.models import Country, Region, City
from artd_partner.models import Partner
from artd_customer.models import (
    Customer,
    Tag,
    CustomerTag,
    CustomerAddress,
    CustomerAdditionalFields,
    FIELD_TYPES,
)
from datetime import datetime


class TestCustomer(TestCase):
    def setUp(self):
        self.country = Country.objects.create(
            spanish_name=generate_random_string(),
            english_name=generate_random_string(),
            nom=generate_random_string(),
            iso2=generate_random_string(),
            phone_code=generate_random_string(),
        )
        self.region = Region.objects.create(
            name=generate_random_string(),
            country=self.country,
        )
        self.city = City.objects.create(
            name=generate_random_string(),
            name_in_capital_letters=generate_random_string(),
            code=generate_random_string(),
            region=self.region,
        )
        self.customer = Customer.objects.create(
            name=generate_random_string(),
            last_name=generate_random_string(),
            birth_date=datetime.now(),
            document=generate_random_string(),
            email=generate_random_email(),
            phone=generate_random_string(),
            city=self.city,
        )
        self.partner = Partner.objects.create(
            name=generate_random_string(),
            dni=generate_random_string(),
            email=generate_random_email(),
            city=self.city,
            address=generate_random_string(),
        )
        self.tag = Tag.objects.create(
            partner=self.partner,
            description=generate_random_string(),
        )
        self.customer_tag = CustomerTag.objects.create(
            customer=self.customer,
            tag=self.tag,
        )
        self.customer_address = CustomerAddress.objects.create(
            customer=self.customer,
            city=self.city,
            phone=generate_random_string(),
            address=generate_random_string(),
            other_data={
                "other_data": generate_random_string(),
            },
        )
        self.customer_additional_fields = CustomerAdditionalFields.objects.create(
            partner=self.partner,
            name=generate_random_string(),
            field_type=FIELD_TYPES[0][0],
            label=generate_random_string(),
            required=True,
        )

    def test_customer(self):
        assert Customer.objects.count() == 1
        assert Customer.objects.first().name == self.customer.name

    def test_tag(self):
        assert Tag.objects.count() == 1
        assert Tag.objects.first().partner == self.partner

    def test_customer_tag(self):
        assert CustomerTag.objects.count() == 1
        assert CustomerTag.objects.first().customer == self.customer
        assert CustomerTag.objects.first().tag == self.tag

    def test_customer_address(self):
        assert CustomerAddress.objects.count() == 1
        assert CustomerAddress.objects.first().customer == self.customer

    def test_customer_additional_fields(self):
        assert CustomerAdditionalFields.objects.count() == 1
        assert CustomerAdditionalFields.objects.first().partner == self.partner
        assert CustomerAdditionalFields.objects.first().field_type == FIELD_TYPES[0][0]
