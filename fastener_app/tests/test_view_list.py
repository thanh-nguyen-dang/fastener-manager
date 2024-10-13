# fastener_app/tests/test_views.py

import pytest
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from fastener_app.models import Fastener, SellerFastener
from fastener_app.tests.factories import ThreadSizeFactory, FastenerFactory

@pytest.mark.django_db
def test_ingest_fasteners(api_client, seller):
    url = reverse('fastener-ingest', args=[seller.id])
    csv_content = (
        "id,name,size_and_length,material,surface_treatment,category,price,quantity\n"
        "F001,M12/1.75 X 220 HCS DIN 931 10.9 PLN,M12/1.75,Steel,Plain,Hex Cap Screw,15.99,200\n"
    ).encode('utf-8')
    csv_file = SimpleUploadedFile('fasteners.csv', csv_content, content_type='text/csv')
    response = api_client.post(url, {'file': csv_file}, format='multipart')
    assert response.status_code == status.HTTP_201_CREATED
    assert Fastener.objects.filter(product_id='F001').exists()
    seller_fastener = SellerFastener.objects.get(seller=seller, fastener__product_id='F001')
    assert str(seller_fastener.price) == str(15.99)
    assert seller_fastener.quantity == 200

@pytest.mark.django_db
def test_get_fasteners_no_sort(api_client, fastener):
    url = reverse('fastener-list')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['product_id'] == fastener.product_id

@pytest.mark.django_db
def test_list_fasteners_sort_by_invalid_field(api_client, fastener):
    url = reverse('fastener-list') + '?sort=invalid_field:asc'
    response = api_client.get(url)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Cannot sort by field 'invalid_field'." in response.data['error']

@pytest.mark.django_db
def test_get_fasteners_includes_metric_and_imperial_size(api_client):
    """
    Ensure that the GET /fasteners/ endpoint includes metric_size_num and imperial_size_num in the response.
    """
    # Create a thread size with specific metric and imperial sizes
    thread_size = ThreadSizeFactory(
        metric_size_str='M12-1.75',
        metric_size_num=12.0,
        imperial_size_str='1/2-13',
        imperial_size_num=0.5
    )

    # Create a fastener associated with this thread size
    fastener = FastenerFactory(thread_size=thread_size)

    url = reverse('fastener-list')
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response['Content-Type'] == 'application/json'

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

    first_fastener = data[0]
    assert 'thread_size' in first_fastener
    thread_size_data = first_fastener['thread_size']

    # Check for both string and numeric fields
    assert 'metric_size_str' in thread_size_data
    assert 'metric_size_num' in thread_size_data
    assert 'imperial_size_str' in thread_size_data
    assert 'imperial_size_num' in thread_size_data

    # Validate the values
    assert thread_size_data['metric_size_str'] == 'M12-1.75'
    assert thread_size_data['metric_size_num'] == 12.0
    assert thread_size_data['imperial_size_str'] == '1/2-13'
    assert thread_size_data['imperial_size_num'] == 0.5

@pytest.mark.django_db
def test_get_fasteners_sorted_by_metric_size_ascending(api_client):
    """
    Ensure that fasteners are sorted by thread_size.metric_size_num in ascending order.
    """
    # Create thread sizes with varying metric_size_num
    thread_size1 = ThreadSizeFactory(metric_size_num=10.0, metric_size_str='M10-1.5', imperial_size_str='1/4-20', imperial_size_num=0.25)
    thread_size2 = ThreadSizeFactory(metric_size_num=12.0, metric_size_str='M12-1.75', imperial_size_str='1/2-13', imperial_size_num=0.5)
    thread_size3 = ThreadSizeFactory(metric_size_num=8.0, metric_size_str='M8-1.25', imperial_size_str='5/16-18', imperial_size_num=0.3125)

    # Create fasteners associated with these thread sizes
    FastenerFactory(thread_size=thread_size1)
    FastenerFactory(thread_size=thread_size2)
    FastenerFactory(thread_size=thread_size3)

    url = reverse('fastener-list') + '?sort=thread_size:asc'
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    # Extract metric_size_num for all fasteners in the response
    metric_sizes = [item['thread_size']['metric_size_num'] for item in data]
    expected_order = sorted(metric_sizes)
    assert metric_sizes == expected_order, "Fasteners are not sorted by metric_size_num in ascending order."

import pytest
from django.urls import reverse
from rest_framework import status
from fastener_app.models import Fastener, Material, Finish, Category, ThreadSize

@pytest.fixture
def setup_fasteners(db):
    """Fixture to create some fasteners and related data."""
    material_1 = Material.objects.create(name="Steel")
    finish_1 = Finish.objects.create(name="Plain")
    category_1 = Category.objects.create(name="Hex Cap Screw")
    thread_size_1 = ThreadSize.objects.create(metric_size_num=12.0, metric_size_str="M12-1.75", thread_per_unit=1)
    thread_size_2 = ThreadSize.objects.create(metric_size_num=10.0, metric_size_str="M10-1.75", thread_per_unit=1.1)

    Fastener.objects.create(
        product_id="F001", description="M12-1.75", thread_size=thread_size_1,
        material=material_1, finish=finish_1, category=category_1
    )
    Fastener.objects.create(
        product_id="F002", description="M10-1.75", thread_size=thread_size_2,
        material=material_1, finish=finish_1, category=category_1
    )


@pytest.mark.django_db
def test_list_fasteners_sort_by_thread_size_asc(api_client, setup_fasteners):
    """Test sorting by thread size in ascending order."""
    url = reverse('fastener-list') + '?sort=thread_size:asc'
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2
    assert response.data[0]['product_id'] == 'F002'  # M10 is smaller than M12
    assert response.data[1]['product_id'] == 'F001'


@pytest.mark.django_db
def test_list_fasteners_sort_by_thread_size_desc(api_client, setup_fasteners):
    """Test sorting by thread size in descending order."""
    url = reverse('fastener-list') + '?sort=thread_size:desc'
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2
    assert response.data[0]['product_id'] == 'F001'  # M12 is larger than M10
    assert response.data[1]['product_id'] == 'F002'


@pytest.mark.django_db
def test_list_fasteners_invalid_sort_parameter_format(api_client, setup_fasteners):
    """Test invalid sorting parameter format."""
    sort_param = "thread_size"
    url = reverse('fastener-list') + f'?sort={sort_param}'
    response = api_client.get(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['error'] == f"Invalid sort parameter format: '{sort_param}'. Expected format: 'field:direction'."


@pytest.mark.django_db
def test_list_fasteners_invalid_sort_direction(api_client, setup_fasteners):
    """Test invalid sorting direction."""
    url = reverse('fastener-list') + '?sort=thread_size:invalid'
    response = api_client.get(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['error'] == "Invalid sort direction. Use 'asc' or 'desc'."

@pytest.mark.django_db
def test_valid_filtering(api_client, setup_fasteners):
    """
    Test filtering fasteners by valid filter params.
    """
    url = reverse('fastener-list') + '?sort=thread_size:asc'
    response = api_client.get(url, {'filter': ['material:Steel', 'finish:plain']})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2  # Both fasteners have 'Steel' material and 'Plain' finish

@pytest.mark.django_db
def test_invalid_filter_key(api_client, setup_fasteners):
    """
    Test filtering with an invalid filter key.
    """
    url = reverse('fastener-list') + '?sort=thread_size:asc'
    response = api_client.get(url, {'filter': ['invalid_key:Steel']})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "error" in response.data
    assert response.data['error'] == "Invalid filter key 'invalid_key'."

@pytest.mark.django_db
def test_invalid_filter_format(api_client, setup_fasteners):
    """
    Test filtering with an invalid filter format.
    """
    url = reverse('fastener-list') + '?sort=thread_size:asc'
    response = api_client.get(url, {'filter': ['materialSteel']})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "error" in response.data
    assert response.data['error'] == "Invalid filter format: 'materialSteel'. Expected format: 'key:value'."
