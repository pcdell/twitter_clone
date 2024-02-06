from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Profile, Tweet
from .forms import TweetForm, SignUpForm, ProfilePicForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User

# Create your views here.
def home(request):
    if request.user.is_authenticated:
        form = TweetForm(request.POST or None)
        if request.method =="POST":
            if form.is_valid():
                tweet = form.save(commit=False)
                tweet.user = request.user
                tweet.save()
                messages.success(request, ("Your Tweet has been posted"))
                return redirect('home')
        tweets = Tweet.objects.all().order_by("-created_at")
        return render (request, 'twitter_app/home.html', {"tweets":tweets, "form":form})
    else:
        tweets = Tweet.objects.all().order_by("-created_at")
        return render (request, 'twitter_app/home.html', {"tweets":tweets})

def profile_list(request):
    if request.user.is_authenticated:
        profiles = Profile.objects.exclude(user = request.user)
        return render(request, 'twitter_app/profile_list.html', {"profiles":profiles})
    else:
        messages.success(request, ("You must be log in to use this page"))
        return redirect('home')
    
def profile(request, pk):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user_id=pk)
        tweets = Tweet.objects.filter(user_id=pk).order_by("-created_at")
        if request.method == "POST":
            current_user_profile = request.user.profile
            action = request.POST['follow']
            if action == "unfollow":
                current_user_profile.follows.remove(profile)
            else:
                current_user_profile.follows.add(profile)
            current_user_profile.save()
        
        return render(request, 'twitter_app/profile.html', {"profile":profile, "tweets":tweets})
    else:
        messages.success(request, ("You must be log in to use this page"))
        return redirect('home')

def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, ("You have logged In"))
            return redirect('home')
        else:
            messages.success(request, ("Error Loggin In"))
            return redirect('login')


    else:
        return render(request, 'twitter_app/login.html', {})

def logout_user(request):
    logout(request)
    messages.success(request, ("You have Logged Out. See you later!"))
    return redirect('home')

def register_user(request):
    form = SignUpForm()
    if request.method =="POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, ("Registered Success. Welcome!"))
            return redirect('home')
    

    return render(request, 'twitter_app/register.html', {'form':form})

def update_user(request):
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        profile_user = Profile.objects.get(user__id=request.user.id)
        user_form = SignUpForm(request.POST or None, request.FILES or None, instance=current_user)
        profile_form = ProfilePicForm(request.POST or None, request.FILES or None, instance=profile_user)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            login(request, current_user)
            messages.success(request, ("Your profile has been updated"))
            return redirect('home')
        return render(request, 'twitter_app/update_user.html', {'user_form':user_form, 'profile_form':profile_form})
    else:
        messages.success(request, ("You must me logged in to update your profile"))
        return redirect('home')

def tweet_like(request, pk):
    if request.user.is_authenticated:
        tweet = get_object_or_404(Tweet, id=pk)
        if tweet.likes.filter(id=request.user.id):
            tweet.likes.remove(request.user)
        else:
            tweet.likes.add(request.user)
        return redirect('home')
    else:
        messages.success(request, ("You must me logged in to update your profile"))
        return redirect('home')