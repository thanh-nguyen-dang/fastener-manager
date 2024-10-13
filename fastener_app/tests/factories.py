import factory
import random
from faker import Faker
from fastener_app.models import (
    Seller,
    Fastener,
    SellerFastener,
    ThreadSize,
    Material,
    Finish,
    Category
)
from fastener_app.unit_converter import imperial_to_metric_name

fake = Faker()

class ThreadSizeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ThreadSize

    name = factory.Sequence(lambda n: f'M{n}-1.75')
    thread_type = 'METRIC'
    unit = 'MILLIMETER'
    metric_size_str = factory.LazyAttribute(lambda obj: obj.name.replace('/', '-'))
    imperial_size_str = factory.LazyAttribute(lambda obj: imperial_to_metric_name(obj.metric_size_str))
    metric_size_num = factory.Sequence(lambda n: abs(n) + 1)
    imperial_size_num = factory.Sequence(lambda n: abs(n) + 1)
    thread_per_unit = 1

class MaterialFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Material

    name = factory.Sequence(lambda n: f'Material {n}')

class FinishFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Finish

    name = factory.Sequence(lambda n: f'Finish {n}')

class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f'Category {n}')

class SellerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Seller

    name = factory.Sequence(lambda n: f'Seller {n}')
    contact_email = factory.Sequence(lambda n: f'seller{n}@example.com')
    phone_number = factory.LazyAttribute(
        lambda _: f"+{random.choice([1, 44, 91])}-{fake.numerify('###-###-####')}"
    )
    address = factory.Faker('address')
    csv_mapping = factory.Dict({
        'id': 'product_id',
        'name': 'description',
        'size_and_length': 'thread_size',
        'material': 'material',
        'surface_treatment': 'finish',
        'category': 'category',
        'price': 'price',
        'quantity': 'quantity'
    })

class FastenerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Fastener

    product_id = factory.Sequence(lambda n: f'F{n:03}')
    description = factory.Faker('sentence', nb_words=10)
    thread_size = factory.SubFactory(ThreadSizeFactory)
    material = factory.SubFactory(MaterialFactory)
    finish = factory.SubFactory(FinishFactory)
    category = factory.SubFactory(CategoryFactory)

class SellerFastenerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SellerFastener

    seller = factory.SubFactory(SellerFactory)
    fastener = factory.SubFactory(FastenerFactory)
    price = factory.Faker('pydecimal', left_digits=5, right_digits=2, positive=True)
    quantity = factory.Faker('random_int', min=0, max=1000)
