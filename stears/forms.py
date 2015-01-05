from django import forms
# from django.contrib.auth.models import User
from mongoengine.django.auth import User
from django.core.exceptions import ValidationError
import utils
import params
import re
# from django.core.validators import email_re


class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50, required=True)
    file = forms.FileField()


class LoginForm(forms.Form):
    username = forms.CharField(label='username', max_length=20, widget=forms.TextInput(
        attrs={'data-validation': 'length', 'data-validation-length': 'min1'}))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'data-validation': 'length', 'data-validation-length': 'min1'}))

# class UserForm(forms.ModelForm):
#     password = forms.CharField(widget=forms.PasswordInput())

#     class Meta:
#         model = User
#         fields = ('username', 'email', 'password')


class ChoiceForm(forms.Form):

    def __init__(self, *args, **kwargs):
        choices = kwargs.pop('choices')
        super(ChoiceForm, self).__init__(*args, **kwargs)
        self.fields['choice'] = forms.ChoiceField(
            choices=[(x, x) for x in choices],
            label='Choose what to research',
        )


class RegisterForm(forms.Form):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    name = forms.CharField(label='Your username', max_length=30, required=True)
    email = forms.EmailField(label='Your email', max_length=30, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    confirm = forms.CharField(widget=forms.PasswordInput, required=True)

    def clean_name(self):
        name = self.cleaned_data['name']
        if name in User.objects.distinct('username'):
            raise ValidationError("That username is already taken")
        if not re.match(r'^[a-zA-Z0-9]+$', name):
            raise forms.ValidationError(
                "Username should include only alphanumeric characters, letters and numbers")
        return name

    def clean_email(self):
        email = self.cleaned_data['email']
        if email in User.objects.distinct('email'):
            raise ValidationError("That email address is already registered")
        # if not email_re.match(email):
        # 	raise ValidationError("That email address is not valid")
        return email

    def clean_confirm(self):
        confirm = self.cleaned_data['confirm']
        if confirm != self.cleaned_data['password']:
            raise ValidationError("Sorry, the passwords did not match")
        return confirm


class RequestForm(forms.Form):

    def __init__(self, *args, **kwargs):
        my_arg = kwargs.pop('my_arg')
        super(RequestForm, self).__init__(*args, **kwargs)
        self.fields['users'] = forms.MultipleChoiceField(
            choices=[(x, x) for x in my_arg],
            label='Writer requests pending',
            widget=forms.CheckboxSelectMultiple()
        )


class SuggestForm(forms.Form):

    def __init__(self, *args, **kwargs):
        my_arg = kwargs.pop('my_arg')
        super(SuggestForm, self).__init__(*args, **kwargs)
        self.fields['user'] = forms.ChoiceField(
            choices=[(x, x) for x in my_arg],
            label='Assign to',
        )


class ChangePasswordForm(forms.Form):
    username = forms.CharField(label='Username', max_length=20)
    old_password = forms.CharField(widget=forms.PasswordInput, required=True)
    new_password = forms.CharField(widget=forms.PasswordInput, required=True)
    confirm = forms.CharField(
        widget=forms.PasswordInput, label='Confirm new password', required=True)

    def clean_new_password(self):
        old_password = self.cleaned_data['old_password']
        new_password = self.cleaned_data['new_password']
        if old_password == new_password:
            raise ValidationError("That's the same password :-(")
        return new_password

    def clean_confirm(self):
        confirm = self.cleaned_data['confirm']
        new_password = self.cleaned_data['new_password']
        if confirm != new_password:
            raise ValidationError("These two passwords aren't the same")
        return confirm


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(label='Your email', max_length=30, required=True)

    def clean_email(self):
        email = self.cleaned_data['email']
        if email not in User.objects.distinct('email'):
            raise ValidationError("That email address is not registered")
        # if not email_re.match(email):
        #   raise ValidationError("That email address is not valid")
        return email


class NseArticleForm(forms.Form):
    headline = forms.CharField(max_length=200)
    content = forms.CharField(widget=forms.Textarea)
    nse_headlines = forms.CharField(
        max_length=30, initial=None, required=False)

    def __init__(self, *args, **kwargs):
        nse_headlines = kwargs.pop('nse_headlines')

        super(NseArticleForm, self).__init__(*args, **kwargs)
        self.fields['nse_headlines'] = forms.CharField(
            max_length=30, initial=nse_headlines, required=False)


class WritersArticleForm(forms.Form):

    headline = forms.CharField(max_length=200, widget=forms.TextInput(attrs={
        'data-validation': 'length',
        'data-validation-length': 'min5'}))
    content = forms.CharField(widget=forms.Textarea(attrs={
        'data-validation': 'length',
        'data-validation-length': 'min10',
        'class': 'wymeditor',
        'data-wym-initialized': 'yes',
    }))
    article_id = forms.CharField(
        max_length=30, initial=None, required=False)

    def __init__(self, *args, **kwargs):
        lock = False

        if 'lock' in kwargs:
            lock = kwargs.pop('lock')

        super(WritersArticleForm, self).__init__(*args, **kwargs)
        nse_headlines = utils.get_nse_headlines()
        categories = params.article_category_tuples

        self.fields['nse_headlines'] = forms.ChoiceField(
            choices=nse_headlines,
            label='NSE headlines. See "Articles" tab for content',
            required=False,
        )
        self.fields['categories'] = forms.ChoiceField(
            choices=categories,
            label='Pick a primary category',
            required=False
        )

        if lock:
            for field in lock:
                self.fields[field].widget.attrs = {'disabled': 'disabled'}


class CommentForm(forms.Form):
    comment = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'small_textarea',
            'data-validation': 'length',
            'data-validation-length': 'min10'
        }), max_length=300, required=True, error_messages={
            'required': 'You did not enter any comment',
            'invalid': 'Your comment entry was invalid',
        })


class KeyWordsForm(forms.Form):
    keywords = forms.CharField(
        widget=forms.TextInput(attrs={
            'data-validation': 'length',
            'data-validation-length': 'min2'
        }), max_length=200, required=True, error_messages={
            'required': 'You did not enter any key word',
            'invalid': 'Your key word was invalid and was not saved'
        })

    def clean_keywords(self):
        keywords = self.cleaned_data['keywords']
        if not re.match(r'^[a-zA-Z]+$', keywords):
            raise forms.ValidationError(
                "Key words should include only letters")
        return keywords
