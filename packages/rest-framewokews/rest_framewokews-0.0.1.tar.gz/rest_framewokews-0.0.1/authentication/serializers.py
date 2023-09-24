from rest_framework import serializers
from .models import *
class ProductSer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"

class CartSer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = "__all__"


class OrderSer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["id","products","order_price"]

class UserSer(serializers.ModelSerializer):
    class Meta:
        model = AbstractUser
        fields = ["id","fio","email","password"]

    def save(self, **kwargs):
        user = AbstractUser(
            fio = self.validated_data["fio"],
            email=self.validated_data["email"],
        )
        password = self.validated_data["password"]
        user.set_password(password)
        user.save()
        return user

class LodinSer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()