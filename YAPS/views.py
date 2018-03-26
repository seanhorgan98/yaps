from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from YAPS.forms import UserForm, UserProfileForm, UserProfile, PodcastForm, MyRegistrationForm
from django.http import HttpResponse
from YAPS.models import Podcast,Category,User,UserProfile,Comment 
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.contrib import auth


def index(request):
    context_dict = {}

    visitor_cookie_handler(request)

    try:
        all_categories = Category.objects.all()
        context_dict["categories"] = all_categories

    except Category.DoesNotExist:
        context_dict['categories'] = None

    return render(request, 'YAPS/index.html')

def add_podcast(request, category_name_slug):

    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    form = PodcastForm()

    if request.method == 'POST':
        form = PodcastForm(request.POST, request.FILES)
        if form.is_valid():
            if category:
                podcast = form.save(commit=False)
                podcast.category = category
                podcast.save()
                return show_category(request, category_name_slug)
        else:
            print(form.errors)

    context_dict = {'form': form, 'category': category}
    return render(request, 'YAPS/add_podcast.html', context_dict)

def show_podcast(request, category_name_slug, podcast_name_slug):
    podcast = Podcast.objects.get(slug=podcast_name_slug)
    context_dict = {}
    context_dict['podcast'] = podcast



    response = render(request, 'YAPS/podcast.html', context_dict)

    return response

def show_category(request, category_name_slug):
    context_dict = {}

    try:
        category = Category.objects.get(slug=category_name_slug)
        podcasts = Podcast.objects.filter(category=category)

        context_dict['podcasts'] = podcasts
        context_dict['category'] = category

    except Category.DoesNotExist:
        context_dict['category'] = None
        context_dict['podcasts'] = None

    return  render(request, 'YAPS/category.html', context_dict)

def logout_user(request):
    logout(request)
    form = UserForm(request.POST or None)
    context = {
        "form": form,
    }
    return render(request, 'YAPS/login.html', context)


def login_user(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user :
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('index'))
            else:
                return render(request, 'YAPS/login.html', {'error_message': 'Your account has been disabled'})
        else:
            print("Invalid login details: {0}, {1}".format(username, password))
            return HttpResponse("Invalid login details supplied.")
    else:
        return render(request, 'YAPS/login.html', {})

    
@login_required
def restricted(request):
        return HttpResponse("Since you're logged in, you can see this text!")       


def register(request):
    if request.method == 'POST':
        form = MyRegistrationForm(request.POST)     # create form object
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('index'))
    args = {}
    args['form'] = MyRegistrationForm()
    print (args)
    return render(request, 'YAPS/register.html', args)
        
def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val



def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, 'visits', '1'))
    last_visit_cookie = get_server_side_cookie(request,'last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7],'%Y-%m-%d %H:%M:%S')
    if (datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        request.session['last_visit'] = str(datetime.now())
    else:
        visits = 1
        request.session['last_visit'] = last_visit_cookie
    request.session['visits'] = visits


                
    
