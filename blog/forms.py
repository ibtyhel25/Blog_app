# blog/forms.py
from django import forms
from .models import CustomUser, Post, Comment, Message
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'bio', 'profile_picture')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])  # Hash the password
        if commit:
            user.save()
        return user


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'image']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content', 'image']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'bio', 'profile_picture']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'cols': 15}),
        }

    profile_picture = forms.ImageField(required=False)  # Optional


# class StartConversationForm(forms.Form):
#     recipient = forms.ModelChoiceField(queryset=User.objects.none(), label="Select Recipient")
#
#     def __init__(self, *args, **kwargs):
#         user = kwargs.pop('user')
#         super(StartConversationForm, self).__init__(*args, **kwargs)
#         self.fields['recipient'].queryset = User.objects.exclude(id=user.id)  # Exclude current user

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content', 'image']  # Include the fields you want to use
        widgets = {
            'content': forms.TextInput(attrs={'placeholder': 'Type your message...', 'required': True}),
        }

from django.contrib.auth import get_user_model

User = get_user_model()

class StartConversationForm(forms.Form):
    recipient = forms.ModelChoiceField(queryset=User.objects.all(), label="Select Recipient")
