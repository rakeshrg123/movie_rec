from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect
from .forms import EditProfileForm, RegistrationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages




  
def welcome(request):
    categories = Movie.objects.values_list('category__id', 'category__name').distinct()
    return render(request, 'welcome.html',{'categories': categories})


def home(request):
    return render(request, 'home.html')


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')  
        else:
            # Print form errors for debugging
            print("Form errors:", form.errors)
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

from django.contrib import messages

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            # Get username and password from form
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            # Authenticate user
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                # Log in the user
                login(request, user)
                return redirect('/')
            else:
                print("User authentication failed.")
        else:
            print("Form is invalid:", form.errors)
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})





from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Movie, Category, Comment, Rating
from .forms import MovieForm, CommentForm, RatingForm
from django.db.models import Avg


@login_required(login_url='/login/')
def movie_list(request):
    categories = Movie.objects.values_list('category__id', 'category__name').distinct()
    movies = Movie.objects.all()
    movie_ratings = {}  # Dictionary to store movie ratings
    for movie in movies:
        # Fetch ratings for each movie
        ratings = Rating.objects.filter(movie=movie)
        # Calculate average rating
        if ratings.exists():
            average_rating = ratings.aggregate(Avg('rating'))['rating__avg']
            movie_ratings[movie] = average_rating
        else:
            movie_ratings[movie] = None  # Or any default value for movies without ratings
    return render(request, 'movie_list.html', {'movies': movies, 'movie_ratings': movie_ratings, 'categories': categories})

@login_required(login_url='/login/')
def movie_detail(request, movie_id):
    categories = Movie.objects.values_list('category__id', 'category__name').distinct()
    movie = get_object_or_404(Movie, id=movie_id)
    comments = Comment.objects.filter(movie=movie)
    ratings = Rating.objects.filter(movie=movie)
    # Calculate average rating
    if ratings.exists():
        average_rating = ratings.aggregate(Avg('rating'))['rating__avg']
    else:
        average_rating = None  # Or any default value for movies without ratings
    return render(request, 'movie_detail.html', {'movie': movie, 'comments': comments, 'average_rating': average_rating, 'categories': categories})

@login_required(login_url='/login/')
def add_comments(request, movie_id):
    categories = Movie.objects.values_list('category__id', 'category__name').distinct()
    movie = get_object_or_404(Movie, id=movie_id)      
    comments = Comment.objects.filter(movie=movie)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.user = request.user
            new_comment.movie = movie
            new_comment.save()
            return render(request, 'comments.html', {'movie': movie, 'comments': comments, 'form': form, 'categories': categories})
    else:
        form = CommentForm()
    return render(request, 'comments.html', {'movie': movie, 'comments': comments, 'form': form, 'categories': categories})

@login_required(login_url='/login/')
def category_movies(request, category_id):
    categories = Movie.objects.values_list('category__id', 'category__name').distinct()
    category = get_object_or_404(Category, id=category_id)
    # Retrieve movies belonging to the specified category
    movies = Movie.objects.filter(category=category_id)
    movie_ratings = {}
    for movie in movies:
        # Fetch ratings for each movie
        ratings = Rating.objects.filter(movie=movie)
        # Calculate average rating
        if ratings.exists():
            average_rating = ratings.aggregate(Avg('rating'))['rating__avg']
            movie_ratings[movie] = average_rating
        else:
            movie_ratings[movie] = None  # Or any default value for movies without ratings
    context = {
        'category':category,
        'categories': categories,
        'movie_ratings': movie_ratings,
        'movies': movies
    }
    return render(request, 'category_movies.html', context)

@login_required(login_url='/login/')
def add_movie(request):
    categories = Movie.objects.values_list('category__id', 'category__name').distinct()
    if request.method == 'POST':
        form = MovieForm(request.POST, request.FILES)
        if form.is_valid():
            movie = form.save(commit=False)  # Create but don't save the movie object yet
            
            # Verify category existence
            category_id = form.cleaned_data.get('category').id
            if category_id is None:
                form.add_error('category', 'Category is required.')
                return render(request, 'add_movie.html', {'form': form, 'categoriess': Category.objects.all(),'categories': categories})
            
            # Ensure the category ID is an integer
            try:
                category_id = int(category_id)
            except ValueError:
                form.add_error('category', 'Invalid category selected.')
                return render(request, 'add_movie.html', {'form': form, 'categoriess': Category.objects.all(),'categories': categories})
            
            # Retrieve the Category object
            category = get_object_or_404(Category, id=category_id)
            movie.category = category

            # Assign the user who added the movie
            movie.added_by = request.user

            # Save the movie
            movie.save()
            return redirect('/movies')  # Redirect to the home page after successful movie addition
    else:
        form = MovieForm()
    return render(request, 'add_movie.html', {'form': form, 'categoriess': Category.objects.all(),'categories': categories})


@login_required(login_url='/login/')
def edit_movie(request, movie_id):
    categories = Movie.objects.values_list('category__id', 'category__name').distinct()
    movie = get_object_or_404(Movie, id=movie_id)
    if request.user == movie.added_by or request.user.is_superuser:
        if request.method == 'POST':
            form = MovieForm(request.POST, request.FILES, instance=movie)
            if form.is_valid():
                movie = form.save(commit=False)  # Create but don't save the movie object yet
                
                # Verify category existence
                category_id = form.cleaned_data.get('category').id
                if category_id is None:
                    form.add_error('category', 'Category is required.')
                    return render(request, 'edit_movie.html', {'form': form, 'categoriess': Category.objects.all(),'movie':movie,'categories': categories})
                
                # Ensure the category ID is an integer
                try:
                    category_id = int(category_id)
                except ValueError:
                    form.add_error('category', 'Invalid category selected.')
                    return render(request, 'edit_movie.html', {'form': form, 'categoriess': Category.objects.all(),'movie':movie,'categories': categories})
                
                # Retrieve the Category object
                category = get_object_or_404(Category, id=category_id)
                movie.category = category

                # Save the movie
                movie.save()
                return redirect('movie_details', movie_id=movie.id)  
        else:
            form = MovieForm(instance=movie)
    return render(request, 'edit_movie.html', {'form': form, 'categoriess': Category.objects.all(),'movie':movie,'categories': categories})


@login_required(login_url='/login/')
def delete_movie(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    if request.user == movie.added_by or request.user.is_superuser:
        if request.method == 'POST':
            movie.delete()
            return redirect('/movies')
    else:
        return redirect('movie_details', movie_id=movie.id)

@login_required(login_url='/login/')
def rate_movie(request, movie_id):
    categories = Movie.objects.values_list('category__id', 'category__name').distinct()
    movie = get_object_or_404(Movie, id=movie_id)
    user = request.user
    
    # Check if the user has already rated the movie
    if Rating.objects.filter(movie=movie, user=user).exists():
        return redirect('movie_details', movie_id=movie.id)
        # You can also display a message here if you want
    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            new_rating = form.save(commit=False)
            new_rating.user = request.user
            new_rating.movie = movie
            new_rating.save()
            return redirect('movie_details', movie_id=movie.id)
    else:
        form = RatingForm()
    return render(request, 'rate_movie.html', {'form': form, 'movie': movie,'categories': categories})

@login_required(login_url='/login/')
def search_movies(request):
    categories = Movie.objects.values_list('category__id', 'category__name').distinct()
    query = request.GET.get('q')
    movies = Movie.objects.all()
    movie_ratings = {}  # Dictionary to store movie ratings
    
    if query:
        movies = movies.filter(title__icontains=query)
    
    for movie in movies:
        # Fetch ratings for each movie
        ratings = Rating.objects.filter(movie=movie)
        # Calculate average rating
        if ratings.exists():
            average_rating = ratings.aggregate(Avg('rating'))['rating__avg']
            movie_ratings[movie] = average_rating
        else:
            movie_ratings[movie] = None 
    
    return render(request, 'movie_list.html', {'movies': movies, 'movie_ratings': movie_ratings, 'categories': categories})


@login_required(login_url='/login/')
def category_detail(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    movies = Movie.objects.filter(category=category)
    return render(request, 'category_detail.html', {'category': category, 'movies': movies})

@login_required(login_url='/login/')
def profile(request):
    categories = Movie.objects.values_list('category__id', 'category__name').distinct()
    user = request.user
    return render(request, 'profile.html', {'user': user,'categories': categories})


@login_required(login_url='/login/')
def edit_profile(request):
    categories = Movie.objects.values_list('category__id', 'category__name').distinct()
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Redirect to profile page after editing
    else:
        form = EditProfileForm(instance=request.user)
    return render(request, 'edit_profile.html', {'form': form ,'categories': categories})


from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

@login_required
def password_change(request):
    categories = Movie.objects.values_list('category__id', 'category__name').distinct()
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Update the session to maintain the user's login state
            update_session_auth_hash(request, user)
            return redirect('profile')  # Redirect to profile page after successful password change
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'password_change.html', {'form': form ,'categories': categories})

from django.contrib.auth import logout

@login_required(login_url='/login/')
def logout_view(request):
    logout(request)
    return redirect('/')  