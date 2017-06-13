from rest_framework import serializers

from foodtaskerapp.models import Restaurant, Meal, Customer, Driver, Order, OrderDetails

#Class executed when an API call for getting all restaurants is called
class RestaurantSerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField()

    #function created to return the absolute url for the logo
    def get_logo(self, restaurant):
        request = self.context.get('request')
        logo_url = restaurant.logo.url
        return request.build_absolute_uri(logo_url)

    class Meta:
        model = Restaurant
        fields = ("id", "name", "phone", "address", "logo")

#Executed when 'customer_get_meals' is called - all meals is requested for a particular Restaurant
class MealSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    #function created to return the absolute url for the image
    def get_image(self, meal):
        request = self.context.get('request')
        image_url = meal.image.url
        return request.build_absolute_uri(image_url)


    class Meta:
        model = Meal
        fields = ("id", "name", "short_description", "image", "price")

#USED IN ORDER SERIALIZER
class OrderCustomerSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source="user.get_full_name")

    class Meta:
        model = Customer
        fields = ("id", "name", "avatar", "phone", "address")

#USED IN ORDER SERIALIZER
class OrderDriverSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source="user.get_full_name")

    class Meta:
        model = Customer
        fields = ("id", "name", "avatar", "phone", "address")

#USED IN ORDER SERIALIZER
class OrderRestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ("id", "name", "phone", "address")

#USED IN ORDER SERIALIZER
class OrderMealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = ("id", "name", "price")

#USED IN ORDER SERIALIZER
class OrderDetailsSerializer(serializers.ModelSerializer):
    meal = OrderMealSerializer

    class Meta:
        model = OrderDetails
        fields = ("id", "meal", "quantity", "sub_total")

#USES SERIALIZERS ABOVE
class OrderSerializer(serializers.ModelSerializer):
    customer = OrderCustomerSerializer()
    driver = OrderDriverSerializer()
    restaurant = OrderRestaurantSerializer()
    order_details = OrderDetailsSerializer(many = True)
    status = serializers.ReadOnlyField(source="get_status_display")

    class Meta:
        model = Order
        fields = ("id", "customer", "restaurant", "driver", "order_details", "total", "status", "address")
