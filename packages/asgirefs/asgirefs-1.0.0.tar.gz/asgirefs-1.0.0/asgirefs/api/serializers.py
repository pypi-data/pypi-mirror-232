from rest_framework import serializers

from .models import User, Product, Order


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['fio', 'email', 'password']

    def create(self, validated_data):
        user = User(
            fio=validated_data['fio'],
            email=validated_data['email'],
        )

        user.set_password(validated_data['password'])
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(required=True, allow_blank=False, allow_null=False)
    password = serializers.CharField(required=True, allow_blank=False, allow_null=False)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
