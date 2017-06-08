from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from foodtaskerapp.forms import UserForm, RestaurantForm, UserFormForEdit, MealForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from foodtaskerapp.models import Meal, Order

# Create your views here. A place to handle and getting all the data.

def home(request):
    return redirect(restaurant_home) #specifies a new redirect for 'home'

@login_required(login_url='/restaurant/sign-in/') #ensures that authentication happens before proceeding to next page
def restaurant_home(request):
    return redirect(restaurant_order) #Order page will be the home page for our Restaurants

@login_required(login_url='/restaurant/sign-in/') #ensures that authentication happens before proceeding to next page
def restaurant_account(request):
    user_form = UserFormForEdit(instance = request.user)
    restaurant_form = RestaurantForm(instance = request.user.restaurant)

    if request.method == "POST":  #This executes when the Save button is pressed to update Account details
        user_form = UserFormForEdit(request.POST, instance = request.user)
        restaurant_form = RestaurantForm(request.POST, request.FILES, instance = request.user.restaurant)

        if user_form.is_valid() and restaurant_form.is_valid(): #check forms validity
            user_form.save() #save form
            restaurant_form.save() #save form

    return render(request, 'restaurant/account.html', {
        "user_form": user_form,
        "restaurant_form": restaurant_form
    }) #after successful login it renders the account.html

@login_required(login_url='/restaurant/sign-in/') #ensures that authentication happens before proceeding to next page
def restaurant_meal(request):
    meals = Meal.objects.filter(restaurant = request.user.restaurant).order_by("-id") #searching all Meals with contraints
    return render(request, 'restaurant/meal.html', {"meals": meals}) #after successful login it renders the meal.html and passes the list of Meals searched

@login_required(login_url='/restaurant/sign-in/') #ensures that authentication happens before proceeding to next page
def restaurant_add_meal(request):
    form = MealForm()

    if request.method == "POST": #execute this block when user submits data
        form = MealForm(request.POST, request.FILES)

        if form.is_valid():
            meal = form.save(commit=False) #dont save yet
            meal.restaurant = request.user.restaurant #setting restaurant first before commit
            meal.save()
            return redirect(restaurant_meal)

    return render(request, 'restaurant/add_meal.html', {
            "form": form
    }) #after successful login it renders the add_meal.html


@login_required(login_url='/restaurant/sign-in/') #ensures that authentication happens before proceeding to next page
def restaurant_edit_meal(request, meal_id): #Function name with the parameters being passed
    form = MealForm(instance = Meal.objects.get(id = meal_id)) #search the Meal to be edited from the DB based on the ID

    if request.method == "POST": #execute this block when user submits data
        form = MealForm(request.POST, request.FILES, instance = Meal.objects.get(id = meal_id))

        if form.is_valid():
            form.save()
            return redirect(restaurant_meal)

    return render(request, 'restaurant/edit_meal.html', {
            "form": form
    }) #after successful login it renders the add_meal.html


@login_required(login_url='/restaurant/sign-in/') #ensures that authentication happens before proceeding to next page
def restaurant_order(request):
    if request.method == "POST": #triggered when the user clcks on the 'Ready' button displayed in the Orders page
        order = Order.objects.get(id = request.POST["id"], restaurant = request.user.restaurant) #this line searchd for the order that will be updated

        if order.status == Order.COOKING: #Checking to see that the order status is 'COOKING'
                order.status = Order.READY #update status to READY
                order.save() #then save to DB

    orders = Order.objects.filter(restaurant = request.user.restaurant).order_by("-id") #fetching all Orders that belong to Current User's Restaurant
    return render(request, 'restaurant/order.html', {"orders": orders}) #after successful login it renders the order.html and pass the list fetched from DB

@login_required(login_url='/restaurant/sign-in/') #ensures that authentication happens before proceeding to next page
def restaurant_report(request):
    return render(request, 'restaurant/report.html', {}) #after successful login it renders the report.html


#sign-up Function
def restaurant_sign_up (request):
    user_form = UserForm()
    restaurant_form = RestaurantForm()

    #when sign up button is clicked, this block is executed
    if request.method == "POST":
        user_form = UserForm(request.POST) #getting data from user form
        restaurant_form = RestaurantForm(request.POST, request.FILES) #getting data from restaurant form

        if user_form.is_valid() and restaurant_form.is_valid(): #check the data received from the forms before proceeding
            new_user = User.objects.create_user(**user_form.cleaned_data) #creates a new User object "restaurant owner"
            new_restaurant = restaurant_form.save(commit=False) #creates a new Restaurant BUT **'commit' to memory only**
            new_restaurant.user = new_user #attach the User of the restaurant object
            new_restaurant.save() #save Restaurant object - this saves to DB

            #Then login user
            login(request, authenticate(
                username = user_form.cleaned_data["username"],
                password = user_form.cleaned_data["password"],
            ))

            #Then redirect to 'restaurant_home' page
            return redirect(restaurant_home)

    return render(request, 'restaurant/sign_up.html', {
        "user_form": user_form,
        "restaurant_form": restaurant_form

    })
