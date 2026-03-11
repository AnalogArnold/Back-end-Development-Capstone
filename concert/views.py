from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.hashers import make_password

from concert.forms import LoginForm, SignUpForm
from concert.models import Concert, ConcertAttending
import requests as req


# Create your views here.

def signup(request):
    if request.method == "POST":
        username = request.POST.get("username") # Get username from the request
        password = request.POST.get("password") # Get password from the request
        try:
            user = User.objects.filter(username=username).first() # Find user using User.objects.filter method
            if user:
                return render(request, "signup.html", {"form": SignUpForm, "message": "user already exist"})
            else:
                # Create new user with make_password method to create the password securely
                user = User.objects.create(username=username, password=make_password(password))
                login(request, user) # Login user with django.contrib.aut. module
                return HttpResponseRedirect(reverse("index")) # Return the user back to the index page
        except User.DoesNotExist:
            return render(request, "signup.html", {"form": SignUpForm})
    return render(request, "signup.html", {"form": SignUpForm})


def index(request):
    return render(request, "index.html")


def songs(request):
    songs = req.get("http://songs-sn-labs-michalvx3.labs-prod-openshift-san-a45631dc5778dc6371c67d206ba9ae5c-0000.us-east.containers.appdomain.cloud/songs").json()
    return render(request, "songs.html", {"songs": songs["songs"]})

def photos(request):
    photos = req.get("https://pictures.27dbcb93s83u.us-south.codeengine.appdomain.cloud/picture").json()
    return render(request, "photos.html", {"photos": photos})

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        try:
            user = User.objects.get(username=username) # Find user with username
            if user.check_password(password): # Check username and password
                login(request, user)
                return HttpResponseRedirect(reverse("index"))
        except User.DoesNotExist:
            return render(request, "login.html", {"form": LoginForm})
    return render(request, "login.html", {"form": LoginForm})


def logout_view(request):
    logout(request) # From django.contrib.auth module
    return HttpResponseRedirect(reverse("login")) # Redirect back to login screen

def concerts(request):
    if request.user.is_authenticated: # Check if user is authenticated
        lst_of_concert = []
        concert_objects = Concert.objects.all() # Get all Concerts using the Concert.objects object
        for item in concert_objects: # Loop over all concerts
            try:
                status = item.attendee.filter(user=request.user).first().attending # Check if user is attending
            except:
                status = "-"
            lst_of_concert.append({
                "concert": item,
                "status": status
            })
        return render(request, "concerts.html", {"concerts": lst_of_concert})
    else:
        return HttpResponseRedirect(reverse("login")) # Redirect to login page if user not authenticated



def concert_detail(request, id):
    if request.user.is_authenticated:
        obj = Concert.objects.get(pk=id)
        try:
            status = obj.attendee.filter(user=request.user).first().attending
        except:
            status = "-"
        return render(request, "concert_detail.html", {"concert_details": obj, "status": status, "attending_choices": ConcertAttending.AttendingChoices.choices})
    else:
        return HttpResponseRedirect(reverse("login"))
    pass


def concert_attendee(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            concert_id = request.POST.get("concert_id")
            attendee_status = request.POST.get("attendee_choice")
            concert_attendee_object = ConcertAttending.objects.filter(
                concert_id=concert_id, user=request.user).first()
            if concert_attendee_object:
                concert_attendee_object.attending = attendee_status
                concert_attendee_object.save()
            else:
                ConcertAttending.objects.create(concert_id=concert_id,
                                                user=request.user,
                                                attending=attendee_status)

        return HttpResponseRedirect(reverse("concerts"))
    else:
        return HttpResponseRedirect(reverse("index"))
