from asgiref.sync import async_to_sync
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404

from blogapp import settings
from .models import Post, Comment, CustomUser, Vote, Conversation, Message
from .forms import PostForm, CommentForm, ProfileForm, CustomUserCreationForm, MessageForm
from channels.layers import get_channel_layer
from django_redis import get_redis_connection
from django.template.loader import render_to_string
from django.http import JsonResponse

channel_layer = get_channel_layer()

# Authentication Views
def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect('home')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('main')
        else:
            return render(request, 'registration/login.html', {'error': 'Invalid username or password.'})
    return render(request, 'registration/login.html')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

# Blog Views
def home(request):
    posts = Post.objects.all().order_by('-upvotes')
    post_form = PostForm(request.POST or None, request.FILES or None)

    if request.method == 'POST' and post_form.is_valid():
        post = post_form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('main')

    return render(request, 'blog/home.html', {'posts': posts, 'post_form': post_form})

def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('home')
    else:
        form = PostForm()
    return render(request, 'blog/create_post.html', {'form': form})

def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.all()
    comment_form = CommentForm(request.POST or None)

    if request.method == 'POST' and comment_form.is_valid():
        comment = comment_form.save(commit=False)
        comment.post = post
        comment.user = request.user
        comment.save()
        return redirect('post_detail', post_id=post.pk)

    return render(request, 'blog/post_detail.html', {'post': post, 'comments': comments, 'comment_form': comment_form})

def update_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return HttpResponseForbidden("You are not allowed to edit this post.")

    post_form = PostForm(request.POST or None, request.FILES or None, instance=post)

    if request.method == 'POST' and post_form.is_valid():
        post_form.save()
        return redirect('post_detail', post_id=post.pk)

    return render(request, 'update_post.html', {'post_form': post_form, 'post': post})

def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return HttpResponseForbidden("You are not allowed to delete this post.")

    if request.method == 'POST':
        post.delete()
        return redirect('home')

    return render(request, 'delete_post.html', {'post': post})

# Comment Views
def add_comment(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, id=post_id)
        content = request.POST['content']
        image = request.FILES.get('image', None)

        Comment.objects.create(post=post, author=request.user, content=content, image=image)
        return redirect('main')

def update_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user != comment.author:
        return HttpResponseForbidden("You are not allowed to edit this comment.")

    if request.method == "POST":
        comment.content = request.POST['content']
        comment.image = request.FILES.get('image', comment.image)
        comment.save()
        return redirect('main')

def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user != comment.author:
        return HttpResponseForbidden("You are not allowed to delete this comment.")

    comment.delete()
    return redirect('main')

# Voting Views
def upvote_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if not Vote.objects.filter(post=post, user=request.user, vote_type='upvote').exists():
        Vote.objects.create(post=post, user=request.user, vote_type='upvote')
        post.upvotes += 1
        post.save()
    return redirect('main')

def downvote_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if not Vote.objects.filter(post=post, user=request.user, vote_type='downvote').exists():
        Vote.objects.create(post=post, user=request.user, vote_type='downvote')
        post.downvotes += 1
        post.save()
    return redirect('main')

def upvote_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if not Vote.objects.filter(comment=comment, user=request.user, vote_type='upvote').exists():
        Vote.objects.create(comment=comment, user=request.user, vote_type='upvote')
        comment.upvotes += 1
        comment.save()
    return redirect('post_detail', post_id=comment.post.pk)

def downvote_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if not Vote.objects.filter(comment=comment, user=request.user, vote_type='downvote').exists():
        Vote.objects.create(comment=comment, user=request.user, vote_type='downvote')
        comment.downvotes += 1
        comment.save()
    return redirect('post_detail', post_id=comment.post.pk)

@login_required
def main_view(request):
    posts = Post.objects.all().prefetch_related('comments')
    post_form = PostForm()
    return render(request, 'blog/main.html', {'posts': posts, 'post_form': post_form})

def profile(request, username):
    user = get_object_or_404(CustomUser, username=username)
    posts = Post.objects.filter(author=user)
    return render(request, 'blog/profile.html', {'user': user, 'posts': posts})

@login_required
def edit_profile(request, username):
    user = get_object_or_404(CustomUser, username=username)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile', username=user.username)
    else:
        form = ProfileForm(instance=user)

    return render(request, 'blog/edit_profile.html', {'form': form, 'user': user})

# Chat Views
@login_required
def chat_list_view(request):
    # Fetch conversations where the user is either user1 or user2
    conversations = Conversation.objects.filter(
        Q(user1=request.user) | Q(user2=request.user)
    )

    context = {
        'conversations': conversations,
    }
    return render(request, 'chat/chat_list.html', context)

@login_required
def start_conversation(request, user_id):
    other_user = get_object_or_404(CustomUser, id=user_id)

    # Explicitly check if the conversation exists
    existing_conversation = Conversation.objects.filter(
        (Q(user1=request.user) & Q(user2=other_user)) |
        (Q(user1=other_user) & Q(user2=request.user))
    ).first()

    if existing_conversation:
        conversation = existing_conversation
    else:
        # Create a new conversation if it doesn't exist
        conversation = Conversation.objects.create(user1=request.user, user2=other_user)

    # Redirect to the conversation view with the conversation ID
    return redirect('conversation_view', conversation_id=conversation.id)




@login_required
def conversation_view(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)
    messages = conversation.messages.all().order_by('timestamp')

    if request.method == "POST":
        content = request.POST.get("content")
        image = request.FILES.get("image")

        # Create the message and set sender and receiver
        Message.objects.create(
            conversation=conversation,
            content=content,
            sender=request.user,
            receiver=conversation.user2 if request.user == conversation.user1 else conversation.user1,
            image=image
        )
        return redirect('conversation_view', conversation_id=conversation_id)

    if request.GET.get("ajax"):  # For AJAX request
        html = render_to_string('chat/messages.html', {'messages': messages})
        return JsonResponse({'html': html}, safe=False)  # Wrap in dict and set safe=False

    return render(request, 'chat/conversation.html', {'conversation': conversation, 'messages': messages})

def search_user(request):
    if 'username' in request.GET:
        username = request.GET['username']
        try:
            user = CustomUser.objects.get(username=username)  # Now using the custom User model
            return redirect('start_conversation', user_id=user.id)
        except CustomUser.DoesNotExist:  # Ensure you're using the correct model
            return render(request, 'chat/chat_list.html', {
                'conversations': Conversation.objects.filter(
                    Q(user1=request.user) | Q(user2=request.user)
                ),
                'error': 'Utilisateur non trouvé.',
            })
    return redirect('chat_list')
