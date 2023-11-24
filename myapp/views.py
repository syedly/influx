from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.contrib.auth import get_user_model, authenticate, logout
User = get_user_model()
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from myapp.models import User, Post, Report, Comment, Friendship, Messages
from django.core.mail import send_mail
from datetime import datetime
from django.db.models import Q
from django.http import JsonResponse
# Create your views here.

def login(request):
    return render(request, 'login.html')

def handlesignup(request):
    if request.method == 'POST':
        email = request.POST['email']
        name = request.POST['name']
        f_name = request.POST['fname']
        l_name = request.POST['lname']
        phone_num = request.POST['number']
        pass1= request.POST['pass1']
        pass2= request.POST['pass2']
        #checks impliment...
        if len(pass1) < 5:
            return HttpResponse("password is too weak")
        if User.objects.filter(email=email).exists():
            return HttpResponse("email already taken")
        if User.objects.filter(name=name).exists():
            return HttpResponse("username already taken")
        if pass1 != pass2:
            return HttpResponse('password not matched')
        if not email.endswith('@gmail.com'):
            return HttpResponse('Use @gmail.com')
        myuser = User(email=email, f_name=f_name, l_name=l_name, name=name, phone_num=phone_num)
        myuser.set_password(pass1)
        myuser.save()

        subject = 'About Registraction'
        message = f'Hi {name}, you have been registred successfully'
        email_from = 'influx@influx.com'
        rec_list = [email,]
        send_mail(subject,message,email_from,rec_list)

        return render(request,'login.html')
    
    else:
        return render(request,'404.html')

def handlelogin(request):
    if request.method == 'POST':
        loginemail = request.POST['loginemail']
        loginpassword = request.POST['loginpassword']

        user = authenticate(email=loginemail, password=loginpassword)
        if user is not None:
            auth_login(request, user)
            '''if user.is_superuser == True:
                return HttpResponse("this is super user")'''

        else:
            #messages.error(request,"invalid credentials, please check your username and password")
            return HttpResponse("invalid credentials, please check your username and password")
            #return redirect('/')
        return render(request,'profile.html')
        
    return render(request,'404.html')

def handlelogout(request):
    logout(request)
    return redirect('login')

@login_required(login_url="/")
def profile(request):
    current_user = request.user
    post = Post.objects.filter(user=current_user)
    posts = reversed(post)
    comments = Comment.objects.filter(post__in=post)
    follow_req = Friendship.objects.filter(to_user=current_user, accepted=False)

    context = {
        'Post':posts,
        'Comment' : comments,
        'follow_request': follow_req
    }
    return render(request,'profile.html',context)

def image(request):
    if request.method == "POST" and request.FILES['image']:
        profile_img = request.FILES.get('image')

        request.user.profile_img = profile_img  
        request.user.save()

        return render(request,"profile.html")
    
    else:
        return render(request,'404.html')
    
@login_required(login_url="/")
def home(request):
    friends = Friendship.objects.filter(from_user=request.user).values_list('to_user', flat=True)
    post = Post.objects.filter(user__in=friends).order_by('date')
    post_reversed = reversed(post)
    comments = Comment.objects.filter(post__in=post)
    context = {
        'Post':post_reversed,
        'Comment':comments,
    }
    return render(request,'home.html',context)
    
@login_required(login_url="/")
def messages(request):
    return render(request,'messages.html')

@login_required(login_url="/")
def settings(request):
    return render(request,'settings.html')

@login_required(login_url="/")
def create(request):
    if request.method == 'POST' and request.FILES['postimage']:
        post = request.FILES.get('postimage')
        caption = request.POST.get('caption')

        save = Post.objects.create(post=post, caption=caption, user=request.user)
        return render(request,"create.html")
    
    return render(request,'create.html')

@login_required(login_url="/")
def changeusername(request):
    if request.method == 'POST':
        newname = request.POST.get("changename")
        confirm_username = request.POST.get("confirmname")

        if newname != confirm_username:
            return HttpResponse("madarchod sehi name likh")
        
        user = User.objects.get(name=request.user.name)
        user.name = newname
        user.save()
        
    return render(request, 'changeusername.html')
login_required(login_url="/")
def report(request):
    if request.method == 'POST':
        email = request.user.email
        title = request.POST.get('report')

        Report.objects.create(email=email, title=title, date=datetime.today())

        subject = 'About Report'
        message = f'Hi {email}, your report have been received'
        email_from = "hassanshah9153@gmail.com"
        rec_list = [email,]
        send_mail(subject, message, email_from, rec_list)

    return render(request,'report.html')

@login_required(login_url="/")
def changepwd(request):
    if request.method =='POST':
        pwd = request.POST.get("pwd")
        new_pwd = request.POST.get("new_pwd")
        confirm_new_pwd = request.POST.get("confirm_new_pwd")

        if request.user.check_password(pwd):
            if new_pwd != confirm_new_pwd:
                return HttpResponse("password not match")
            else:
                user_password = User.objects.get(name=request.user.name)
                user_password.set_password(confirm_new_pwd)
                user_password.save()
        
        else:
            return HttpResponse("password not correct")

    return render(request,'changepwd.html')

@login_required(login_url="/")
def deactivate(request,id):
    delete = User.objects.get(id=id)
    delete.delete()
    return redirect(request.get_full_path())
    #return render(request,'login.html')

@login_required(login_url='/')
def delete_post(request,post_id):
    delete = get_object_or_404(Post, pk=post_id)
    delete.delete()
    return render(request,'profile.html')

@login_required(login_url="/")
def search(request):
    if request.method == 'POST':
        query = request.POST.get('query')
        data = User.objects.filter(name__icontains=query)
        print(data)
        context = {
            'query':data,
        }

        return render(request, 'search.html', context)
    
    else:
        return render(request, 'search.html',{})
        
@login_required(login_url="/")
def profile_view(request,name):
    user = get_object_or_404(User, name=name)
    post = Post.objects.filter(user=user)
    posts = reversed(post)
    current_page = request.META.get('HTTP_REFERER', '/')
    comments = Comment.objects.filter(post__in=post)
    from_user = Friendship.objects.filter(from_user=user, to_user=request.user)
    is_friend = Friendship.objects.filter(from_user=request.user, to_user=user).exists()
    is_accepted = Friendship.objects.filter(from_user=request.user, to_user=user, accepted = True)
    #it use in private profile if person.is_accepted then show the profile
    already_exists = Friendship.objects.filter(from_user=request.user, to_user=user)

    if user.private_account and user != request.user:
        if request.method == "POST":
            action = request.POST.get('action')

            if already_exists.exists():
                already_exists.delete()

            '''if action == "a":
                a = from_user.filter(to_user=request.user)
                print(a)
                print("private a")
                a.delete()'''

            if action == "remove":
                a = already_exists.filter(from_user=request.user, to_user=user)
                print(a)
                print("private remove")
                a.delete()

            if action == 'add':
                #Friendship.objects.create(from_user=request.user, to_user=user)
                send_follow_request(request, name)

        return render(request, 'private_profile.html',{'Comment':comments,'person':user,'Post':post if is_accepted else None})

    if request.method == "POST":
        action = request.POST.get('action')

        if already_exists.exists():
            already_exists.delete()

        '''if action == "a":#followers
            a = from_user.filter(to_user=request.user)
            print(a)
            print("normal a")
            a.delete()'''

        if action == "remove":#following
            a = already_exists.filter(from_user=request.user, to_user=user)
            print(a)
            print("normal remove")
            a.delete()

            return redirect(current_page)

        if action == 'add':
            Friendship.objects.create(from_user=request.user, to_user=user, accepted=True)

        return redirect(request.get_full_path())

    context ={
        'person':user,
        'Post':posts,
        'Comment':comments,
    }
    
    return render(request,'profile_view.html',context)

@login_required(login_url='/')
def send_follow_request(request, name):
    recipient = get_object_or_404(User, name=name)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "add":

            existing_request = Friendship.objects.filter(
                #from_user=request.user,
                to_user=recipient,
                accepted=False
            ).first()

            if not existing_request:
 
                Friendship.objects.create(
                    from_user=request.user,
                    to_user=recipient,
                    accepted=False
                )

    return redirect('profile_view', name=name)

@login_required(login_url="/")
def accept_follow_request(request, name):
    user = get_object_or_404(User, name=name)

    if request.method == "POST":
        action = request.POST.get('action')

        if action == "add":

            friendship_request = Friendship.objects.filter(
                from_user=user,
                to_user=request.user,
                accepted=False
            ).first()

            if friendship_request:

                friendship_request.accepted = True
                friendship_request.save()

                Friendship.objects.filter(
                    from_user=request.user,
                    to_user=user,
                    accepted=False
                ).update(accepted=True)

    return redirect('profile_view', name=name)

@login_required(login_url='/')
def reject_follow_request(request,name):
    current_page = request.META.get('HTTP_REFERER', '/')
    user = get_object_or_404(User, name=name)

    if request.method == "POST":
        action = request.POST.get('action')

        if action == "remove":
            Friendship.objects.filter(
                from_user=user,
                to_user=request.user
                ).delete()
            
    return redirect(current_page)

@login_required(login_url='/')
def viewfriends(request):
    user = request.user
    following = Friendship.objects.filter(from_user=user, accepted=True)
    followers = Friendship.objects.filter(to_user=user, accepted=True)

    if request.method == 'POST':
        action = request.POST.get('action')
        follower_id = request.POST.get('follower_id')

        if action == 'a' and follower_id:
            Friendship.objects.filter(id=follower_id).delete()

    context = {
        'following': following,
        'followers': followers,
    }
    return render(request, 'viewfriends.html', context)

@login_required(login_url="/")
def editbio(request):
    if request.method == 'POST':
        bio = request.POST.get('bio')

        user = User.objects.get(name=request.user.name)
        user.bio = bio
        user.save()

    return render(request,'bio.html')

@login_required(login_url='/')
def like(request,post_id):
    post = Post.objects.get(id=post_id)
    current_page = request.META.get('HTTP_REFERER', '/')

    if request.user in post.like.all():
        post.like.remove(request.user)
    else:
        post.like.add(request.user)

    return redirect(current_page)

@login_required(login_url='/')
def viewlikes(request,post_id):
    post = get_object_or_404(Post, pk=post_id)
    likes = post.like.all() 

    context = {
        'Post':post,
        'Like':likes,
    }

    return render(request,'viewlikes.html',context)

@login_required(login_url='/')
def chat(request):
    u2 = Friendship.objects.filter(from_user=request.user)
    u1 = Friendship.objects.filter(to_user=request.user)

    context = {
        'username': request.user.name,
        'following': u1,
        'followers': u2,
    }

    return render(request,'chat.html', context)

@login_required(login_url="/")
def comments(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    user = request.user
    current_page = request.META.get('HTTP_REFERER', '/')

    if request.method == 'POST':
        content = request.POST.get('comment')

        Comment.objects.create(user=user, post=post, comment=content)

    return redirect(current_page)

@login_required(login_url="/")
def message(request, name):
    user = request.user
    recipient = get_object_or_404(User, name=name)
    following = Friendship.objects.filter(to_user=user)

    if request.method == "POST":
        content = request.POST.get('content')

        message = Messages(recipient=recipient, sender=user, content=content)
        message.save()

        return JsonResponse({'status': 'success'})

    messages = Messages.objects.filter(Q(sender=user, recipient=recipient) | Q(sender=recipient, recipient=user)).order_by('timestamp')
    context = {
        'username': request.user.name,
        'recipient': recipient,
        'messages': messages,
        'followers': following
    }

    return render(request, 'messages.html', context)

@login_required(login_url="/")
def ajax_messages_refresh(request, sender, reciever):
    sender = get_object_or_404(User, name=sender)
    reciever = get_object_or_404(User, name=reciever)
    messages = Messages.objects.filter(Q(sender=sender, recipient=reciever) | Q(sender=reciever, recipient=sender)).order_by('timestamp')
    new_messages = []
    for message in messages:
        new_messages.append({
            "sender": message.sender.name,
            "recipient": message.recipient.name,
            "content": message.content,
            "timestamp": message.timestamp
        })
    return JsonResponse({"messages": new_messages})

@login_required(login_url="/")
def toggle_private_account(request):
    if request.method == "POST":

        current_private_account = request.user.private_account

        new_private_account = not current_private_account

        user = request.user
        user.private_account = new_private_account
        user.save()

    return render(request, 'settings.html')