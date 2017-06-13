import json

from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from oauth2_provider.models import AccessToken

from foodtaskerapp.models import Restaurant, Meal, Order, OrderDetails
from foodtaskerapp.serializers import RestaurantSerializer, MealSerializer, OrderSerializer

################
# CUSTOMER APIS
################

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
    #get token
    access_token = AccessToken.objects.get(token = request.GET.get("access_token"), expires__gt = timezone.now())

    #get Customer
    customer = access_token.user.customer

    #get Order
    order = OrderSerializer(Order.objects.filter(customer = customer).last()).data

    return JsonResponse({"order": order})


################
# RESTAURANT APIS
################

def restaurant_order_notification(request, last_request_time):
    notification = Order.objects.filter(restaurant = request.user.restaurant, created_at__gt = last_request_time).count()

    return JsonResponse({"notification": notification})



################
# DRIVER APIS
################

#Gets all the orders that are ready for delivery
def driver_get_ready_orders(request):
    #get all the orders that are READY and no DRIVER assigned
    orders = OrderSerializer(
        Order.objects.filter(status = Order.READY, driver = None).order_by("-id"), many = True
    ).data
    return JsonResponse({"orders": orders})

@csrf_exempt #as this will be made from outside the system csrf_exempt needs to be used
#POST request that requires params: access_token, order_id
def driver_pick_order(request):

        if request.method == "POST":
            #Get tokena
            access_token = AccessToken.objects.get(token = request.POST.get("access_token"), expires__gt = timezone.now())

            #Get the driver based on the token ABOVE
            driver = access_token.user.driver

            #check if driver can only pick up one order at the same time
            #get all orders assigned to Driver and exclude the ones set to ON THE WAY, this checks to see if the Driver is delivering another order
            if Order.objects.filter(driver = driver).exclude(status = Order.ONTHEWAY):
                return JsonResponse ({"status": "failed", "error": "You can only pick one order at a time."})

            try: #search for the Order that is being attempted to be picked up
                order = Order.objects.get(
                id = request.POST["order_id"],
                driver = None,
                status = Order.READY
                )
                order.driver = driver #assign driver to order if it meets the conditions above
                order.status = Order.ONTHEWAY #update the order status to ONTHEWAY
                order.picked_at = timezone.now() #update time
                order.save() #save order

                return JsonResponse({"status": "success"})

            except Order.DoesNotExist:
                return JsonResponse({"status": "failed", "error": "This order has been picked up by another driver."})

        return JsonResponse({})

#GET params: 'access_token'
def driver_get_latest_order(request):
    #Get tokena
    access_token = AccessToken.objects.get(token = request.GET.get("access_token"), expires__gt = timezone.now())

    #Get the driver based on the token ABOVE
    driver = access_token.user.driver
    #Get the order
    order = OrderSerializer(
        Order.objects.filter(driver = driver).order_by("picked_at").last() #Get ALL Orders that are asigned to Driver get the last order.
    ).data

    return JsonResponse({"order": order})

#POST request params: access_token, order_id (note: params for POST requests are passed in the Body of the request)
@csrf_exempt
def driver_complete_order(request):
    #Get token
    access_token = AccessToken.objects.get(token = request.POST.get("access_token"), expires__gt = timezone.now())
    #Get the driver based on the token ABOVE
    driver = access_token.user.driver
    #Get the order
    order = Order.objects.get(id = request.POST["order_id"], driver = driver)
    #Update the order status
    order.status = Order.DELIVERED
    order.save()

    return JsonResponse({"status": "success"})

# GET params: access_token
def driver_get_revenue(request):
    #Get token
    access_token = AccessToken.objects.get(token = request.GET.get("access_token"), expires__gt = timezone.now())
    #Get the driver based on the token ABOVE
    driver = access_token.user.driver

    from datetime import timedelta #function returns the difference between 2 dates

    revenue = {} #creates an empty dictionary
    today = timezone.now()
    current_weekdays = [today + timedelta(days = i) for i in range (0 - today.weekday(), 7 - today.weekday())] #This will return the current weekdays and put into array

    for day in current_weekdays:
        orders = Order.objects.filter(
            driver = driver,
            status = Order.DELIVERED,
            created_at__year = day.year,
            created_at__month = day.month,
            created_at__day = day.day
        )

        revenue[day.strftime("%a")] = sum(order.total for order in orders) #for all ORDERS in the 'orders' collection, add-up the total, then assign to the day eg TUE, WED

    return JsonResponse({"revenue": revenue}) #return the 'revenue' dictionary
