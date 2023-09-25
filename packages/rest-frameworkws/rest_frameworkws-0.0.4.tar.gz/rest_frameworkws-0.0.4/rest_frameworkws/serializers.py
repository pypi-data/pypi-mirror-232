from rest_framework import serializers
from .models import *
class ProductsSer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = "__all__"

class CartSer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = "__all__"

class OrderSer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"

class UserSer(serializers.ModelSerializer):
    class Meta:
        model = AbstractUser
        fields = "__all__"

    def save(self, **kwargs):
        user = AbstractUser(
            email = self.validated_data["email"],
            fio =self.validated_data["fio"]
        )
        password = self.validated_data["password"]
        user.set_password(password)
        user.save()
        return user

class LoginSer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()