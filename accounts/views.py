from django.shortcuts import render, HttpResponseRedirect, HttpResponse, redirect
# Registration
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .forms import UserCreateForm
from django.contrib import auth
from django.template.context_processors import csrf
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.core.mail import send_mail
import hashlib, random, datetime
from django.contrib.auth.models import User
from gameStore.models import UserProfile
from django.shortcuts import render_to_response, get_object_or_404
from django.utils import timezone

# Create your views here.

def register(request):
    args = {}
    args.update(csrf(request))

    #If HTTP POST, it's a registration
    if request.method == 'POST':
        # Get form data
        user_form = UserCreateForm(request.POST)
        args['form'] = user_form

    # If form is valid...
        if user_form.is_valid():
            user = user_form.save()
            if user.is_developer:
                user.groups.add(Group.objects.get(name='Developer'))

            username = user_form.cleaned_data['username']
            email = user_form.cleaned_data['email']
            random_string = str(random.random()).encode('utf8')
            salt = hashlib.sha1(random_string).hexdigest()[:5]
            salted = (salt + email).encode('utf8')
            activation_key = hashlib.sha1(salted).hexdigest()
            key_expires = datetime.datetime.today() + datetime.timedelta(2)

            #Get user by username
            user=User.objects.get(username=username)

            # Create and save user profile
            new_profile = UserProfile(user=user,
                                      activation_key=activation_key,
                                      key_expires=key_expires)
            new_profile.save()

            # Send email with activation key
            email_subject = 'Account confirmation'
            email_body = "Hey %s, thanks for signing up. To activate your account, click this link within \
            48hours http://127.0.0.1:8000/accounts/confirm/%s" % (username, activation_key)

            send_mail(email_subject,
                      email_body,
                      'myemail@example.com',
                      [email],
                      fail_silently=False)

            return HttpResponseRedirect('../../')
        # Invalid form? - mistakes? Print problems
        else:
            print(user_form.errors)
    # Not a HTTP POST -> Render form using ModelForm
    # These forms are blank
    else:
        user_form = UserCreateForm()

    return render(request, 'register.html', {'user_form': user_form})

def register_confirm(request, activation_key):
    #check if user is already logged in and if he is redirect him to some other url, e.g. home
    if request.user.is_authenticated():
        HttpResponseRedirect('../../')

    # check if there is UserProfile which matches the activation key (if not then display 404)
    user_profile = get_object_or_404(UserProfile, activation_key=activation_key)

    #check if the activation key has expired, if it hase then render confirm_expired.html
    if user_profile.key_expires < timezone.now():
        return render_to_response('accounts/confirm_expired.html')
    #if the key hasn't expired save user and set him as active and render some template to confirm activation
    user = user_profile.user
    user.is_active = True
    user.save()
    return render_to_response('confirm.html')

def user_login(request):
    if request.method == "POST":
        # Gather the info from the request
        username = request.POST['username']
        password = request.POST['password']

        # Django auth for validating input

        user = authenticate(username=username, password=password)

        if user is not None:
            #is active? Could've been disabled
            if user.is_active:
                # If the account is valid and active, log in the user
                login(request,user)
                return HttpResponseRedirect("../../")
            else:
                # An inactive account found - no logging in
                inactive_account = True
                tried_user = User.objects.get(username=username)
                return render(request, 'login.html', {'auth_form': AuthenticationForm, 'user': request.user,
                                                      'inactive_account': inactive_account, 'tried_user': tried_user})
        else:
            invalid_details = True
            return render(request, 'login.html', {'invalid_details': invalid_details, 'auth_form': AuthenticationForm, 'user': request.user})
    else:
        return render(request, 'login.html', {'auth_form': AuthenticationForm, 'user': request.user})

def user_logout(request):
    auth.logout(request)
    return render(request, 'index.html', {'auth_form': AuthenticationForm, 'user': request.user})
