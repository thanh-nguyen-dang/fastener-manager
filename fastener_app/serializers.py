from rest_framework import serializers
from .models import Seller, Fastener, SellerFastener, ThreadSize, Material, Finish, Category


class ThreadSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThreadSize
        fields = [
            'id',
            'name',
            'thread_type',
            'unit',
            'metric_size_str',
            'metric_size_num',
            'imperial_size_str',
            'imperial_size_num',
        ]

    def validate_metric_size_num(self, value):
        if value <= 0:
            raise serializers.ValidationError("Metric size must be a positive number.")
        return value

    def validate_imperial_size_num(self, value):
        if value <= 0:
            raise serializers.ValidationError("Imperial size must be a positive number.")
        return value


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ['id', 'name']


class FinishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Finish
        fields = ['id', 'name']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class SellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seller
        fields = ['id', 'name', 'contact_email', 'phone_number', 'address', 'csv_mapping']

    def get_required_fastener_fields(self):
        """
        Dynamically fetch required fields from the Fastener model.
        A field is considered required if it's not allowed to be blank and not nullable.
        """
        required_fields = []
        for field in Fastener._meta.get_fields():
            if hasattr(field, 'blank') and not field.blank and not field.null:
                required_fields.append(field.name)
        return required_fields

    def validate_csv_mapping(self, value):
        """
        Custom validator to ensure that the required Fastener fields
        are included in the csv_mapping field.
        """
        # Get dynamically required Fastener fields
        required_fields = self.get_required_fastener_fields()

        # Check if required Fastener fields are present in the csv_mapping
        missing_fields = [field for field in required_fields if field not in value.values()]

        if missing_fields:
            raise serializers.ValidationError(f"Missing required fields in csv_mapping: {', '.join(missing_fields)}")

        return value


class FastenerSerializer(serializers.ModelSerializer):
    thread_size = ThreadSizeSerializer(read_only=True)
    material = MaterialSerializer(read_only=True)
    finish = FinishSerializer(read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Fastener
        fields = ['id', 'product_id', 'description', 'thread_size', 'material', 'finish', 'category']


class SellerFastenerSerializer(serializers.ModelSerializer):
    seller = SellerSerializer(read_only=True)
    fastener = FastenerSerializer(read_only=True)
    seller_id = serializers.PrimaryKeyRelatedField(queryset=Seller.objects.all(), source='seller', write_only=True)
    fastener_id = serializers.PrimaryKeyRelatedField(queryset=Fastener.objects.all(), source='fastener', write_only=True)

    class Meta:
        model = SellerFastener
        fields = ['id', 'seller', 'fastener', 'seller_id', 'fastener_id', 'price', 'quantity', 'last_updated']
