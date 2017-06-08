from rest_framework import serializers

from foodtaskerapp.models import Restaurant, Meal

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
