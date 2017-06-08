import json

from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from oauth2_provider.models import AccessToken

from foodtaskerapp.models import Restaurant, Meal, Order, OrderDetails
from foodtaskerapp.serializers import RestaurantSerializer, MealSerializer

#This is for a Customer to get all the Restaurants from the DB returned as a JSON objects
def customer_get_restaurants(request):
    restaurants = RestaurantSerializer(
        Restaurant.objects.all().order_by("-id"),
        many = True,
        context = {"request": request}
    ).data

    return JsonResponse({"restaurants": restaurants}) #response in JSON format

#Function for getting all the meals
def customer_get_meals(request, restaurant_id):
    meals = MealSerializer(
        Meal.objects.filter(restaurant_id = restaurant_id).order_by("-id"),
        many = True,
        context = {"request": request}
    ).data

    return JsonResponse({"meals": meals})

#To create a new Order.
#Params required: access_token, restaurant_id, customer_address, order_details (JSON format)
# order_details: [{"meal_id": 1, "quantity": 2}{{"meal_id": 2, "quantity": 2}]
# return: {"status": "success"}
@csrf_exempt
def customer_add_order(request):

    if request.method == "POST":
        #Get token
        access_token = AccessToken.objects.get(token = request.POST.get("access_token"),
            expires__gt = timezone.now()
        )

        #Geting the user via the access_token param provided, checking AccessToken table in the DB
        customer = access_token.user.customer

        #Check UNDELIVERED ORDERS if customer has any undelivered orders
        if Order.objects.filter(customer =  customer).exclude(status = Order.DELIVERED):
            return JsonResponse({"response": "failed", "error": "Your last order must be completed."})

        #Check ADDRESS to ensure address has been provided
        if not request.POST["address"]:
            return JsonResponse({"status": "failed", "error": "Address is required."})

        #Get ORDER DETAILS details from the Params passed
        order_details = json.loads(request.POST["order_details"])

        #calculate SUBTOTAL by traversing though the order_details array
        order_total = 0
        for meal in order_details:
            order_total += Meal.objects.get(id = meal["meal_id"]).price * meal["quantity"] # using params 'meal_id' and 'quantity' to calculate total

        #check that there are items being orders by checking the 'order_details' params array length
        if len(order_details) > 0:
            #step 1. Create Order
            order = Order.objects.create(
                customer = customer,
                restaurant_id = request.POST["restaurant_id"],
                total = order_total,
                status = Order.COOKING,
                address = request.POST["address"]
            )

            #step 2. Create Order Details
            for meal in order_details:
                OrderDetails.objects.create(
                    order = order,
                    meal_id = meal["meal_id"],
                    quantity = meal["quantity"],
                    sub_total = Meal.objects.get(id = meal["meal_id"]).price * meal["quantity"]
            )

            return JsonResponse({"status": "success"})


#Get the latest order
def customer_get_latest_order(request):

    return JsonResponse({})

def restaurant_order_notification(request, last_request_time):
    notification = Order.objects.filter(restaurant = request.user.restaurant, created_at__gt = last_request_time).count()

    return JsonResponse({"notification": notification})
