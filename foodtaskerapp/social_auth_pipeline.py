from foodtaskerapp.models import Customer, Driver

def create_user_by_type(backend, user, request, response, *args, **kwargs):
    #if we're login via facebook then do this...get avatar
    if backend.name == 'facebook':
        avatar = 'https://graph.facebook.com/%s/picture?type=large' % response['id']


    #If the user type is a Driver and it does NOT exist in the DB then create a new Driver with user_id and avatar fetched
    if request['user_type'] == "driver" and not Driver.objects.filter(user_id=user.id):
        Driver.objects.create(user_id=user.id, avatar = avatar)

    #Otherwise then create a Customer in the db as it would NOT be a Driver based on the if above
    elif not Customer.objects.filter(user_id=user.id):
        Customer.objects.create(user_id=user.id, avatar = avatar)
