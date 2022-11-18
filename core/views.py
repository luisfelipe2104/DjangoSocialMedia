from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponse
from flask_login import user_loaded_from_header
from .models import Post, Profile, LikePost, FollowersCount
from django.contrib.auth.decorators import login_required
from itertools import chain
import random

# Create your views here.
@login_required(login_url='signin')   # makes it obrigatory to be logged in
def index(request):
    user_object = User.objects.get(username=request.user) # gets the current logged in user (the user object is the foreigh key)
    user_profile = Profile.objects.get(user=user_object)   # gets the user profile

    user_following_list = []
    feed = []

    # gets the users who is being followed by the current logged in user
    user_following = FollowersCount.objects.filter(follower=request.user.username)

    for user in user_following:
        user_following_list.append(user)

    # creates a feed with the posts only of the users who are being followed by the current logged in user
    for username in user_following_list:
        feed_lists = Post.objects.filter(user=username)
        feed.append(feed_lists)

    feed_list = list(chain(*feed))

    # posts = Post.objects.all()

    # user suggestion starts
    # gets all the users
    all_users = User.objects.all()
    user_following_all = []

    # gets the list of the users that are being followed by the current logged in user
    for user in user_following:
        user_list = User.objects.get(username=user.user)
        user_following_all.append(user_list)

    # separetes the users that are being followed from who aren't
    new_suggestions_list = [x for x in list(all_users) if (x not in list(user_following_all))]
    current_user = User.objects.filter(username=request.user.username)
    final_suggestions_list = [x for x in list(new_suggestions_list) if (x not in list(current_user))]
    random.shuffle(final_suggestions_list)

    username_profile = []
    username_profile_list = []

    # gets the id of each user from the suggestion list 
    for users in final_suggestions_list:
        username_profile.append(users.id)

    # gets the profile of each user from the suggestion list
    for ids in username_profile:
        profile_lists = Profile.objects.filter(id_user=ids)
        username_profile_list.append(profile_lists)

    suggestions_username_profile_list = list(chain(*username_profile_list))

    return render(request, 'index.html', {'user_profile':user_profile, 'posts':feed_list, 'suggestions_username_profile_list': suggestions_username_profile_list[:4]})

@login_required(login_url='signin')  # makes it obrigatory to be logged in
def upload(request):
    if request.method == 'POST':
        # gets the data of the form
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']

        # creates a new post and save it
        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()

        return redirect('/')

    else:
        return redirect('/')

    return HttpResponse("UPLOAD")

@login_required(login_url='signin')  # makes it obrigatory to be logged in
def search(request):
    # gets the user object and the user profile
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    if request.method == 'POST':
        username = request.POST['username'] # gets the data from the searching form
        username_object = User.objects.filter(username__icontains=username)

        username_profile = []
        username_profile_list = []

        # gets the id from each user who is being searched for
        for users in username_object:
            username_profile.append(users.id)

        # gets the user profile using the id
        for ids in username_profile:
            profile_lists = Profile.objects.filter(id_user=ids)
            username_profile_list.append(profile_lists)

        username_profile_list = list(chain(*username_profile_list))

    return render(request, 'search.html', {'user_profile': user_profile, 'username_profile_list' : username_profile_list})

@login_required(login_url='signin')    # makes it obrigatory to be logged in 
def like_post(request):
    username = request.user.username  # gets the current logged in user
    post_id = request.GET.get('post_id')    # gets the post id according with the url

    post = Post.objects.get(id=post_id)   # gets the post

    # checks if the post is already liked by the user
    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()

    # in case it's not liked by the user
    if like_filter == None:
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()
        post.num_of_likes += 1
        post.save()
        return redirect('/')

    # in case it's already liked by the user
    else:
        like_filter.delete()
        post.num_of_likes -= 1
        post.save()
        return redirect('/')

@login_required(login_url='signin')    # makes it obrigatory to be logged in 
def profile(request, pk):
    # gets the user profile
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=pk)
    user_post_length = len(user_posts)

    # gets the current logged in user
    follower = request.user.username
    # gets the user profile
    user = pk

    # gets the amount of followers and the amount of users the user is following 
    user_followers = len(FollowersCount.objects.filter(user=pk))
    user_following = len(FollowersCount.objects.filter(follower=pk))

    # changes the following button text depending if the user is already following
    if FollowersCount.objects.filter(follower=follower, user=user).first():
        button_text = 'Unfollow'

    else:
        button_text = 'Follow'


    context = {
        'user_following': user_following,
        'user_followers': user_followers,
        'button_text': button_text,
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
    }

    return render(request, 'profile.html', context)

@login_required(login_url='signin')    # makes it obrigatory to be logged in 
def follow(request):
    if request.method == 'POST':
        follower = request.POST['follower']   # gets the current logged in user
        user = request.POST['user']     # gets the user profile

        # in case the profile is already being followed by the current logged in user
        if FollowersCount.objects.filter(follower=follower, user=user).first():
            delete_follower = FollowersCount.objects.get(follower=follower, user=user)
            delete_follower.delete()
            return redirect('/profile/'+user)
        
        # in case the profile is not being followed by the current logged in user
        else:
            new_follower = FollowersCount.objects.create(follower=follower, user=user)
            new_follower.save()
            return redirect('/profile/'+user)

    else:
        return redirect('/')

@login_required(login_url='signin')   # makes it obrigatory to be logged in
def settings(request):
    user_profile = Profile.objects.get(user=request.user) # gets the current logged in user

    if request.method == 'POST':
        # Case there's no image being uploaded it'll upload the user's profile image
        if request.FILES.get('image') == None:
            # gets the data from the form
            image = user_profile.profileImg
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileImg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()

        # Case there's an image being uploaded
        if request.FILES.get('image') != None:
            # gets the data from the form
            image = request.FILES.get('image')
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileImg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()

        return redirect('settings')

    return render(request, 'setting.html', {'user_profile':user_profile})


def signup(request):
    if request.method == 'POST':
        # gets the data of the form
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        # checks if the password is valid
        if password == password2:
            # checks if the email already exists
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email Taken')
                return redirect('signup')

            # checks if the username already exists
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username Taken')
                return redirect('signup')

            else:
                # creates the user
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                # log user in and redirect to settings page
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)

                # create a Profile object for the new user
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                new_profile.save()
                return redirect('settings')
        else:
            # if the password is invalid
            messages.info(request, 'Password Not Matching')
            return redirect('signup')
        

    else:
        # renders the page
        return render(request, 'signup.html')


def signin(request):
    if request.method == 'POST':
        # gets the data of the form
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)

        if user is not None:
            # logs the user in
            auth.login(request, user)
            return redirect('/')
        else:
            # in case the user's info is invalid
            messages.info(request, 'Credentials Invalid')
            return redirect('signin')

    else:
        return render(request, 'signin.html')


@login_required(login_url='signin')   # makes it obrigatory to be logged in
def logout(request):
    # logs the user out
    auth.logout(request)
    return redirect('signin')