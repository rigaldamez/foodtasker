from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from foodtaskerapp.forms import UserForm, RestaurantForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

# Create your views here.

def home(request):
    return redirect(restaurant_home) #specifies a new redirect for 'home'

@login_required(login_url='/restaurant/sign-in/') #ensures that authentication happens before proceeding to next page
def restaurant_home(request):
    return render(request, 'restaurant/home.html') #after successful login it renders the "new" home.html

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
