from django import forms
# from django.contrib.auth.models import User
from mongoengine.django.auth import User
from django.core.exceptions import ValidationError
import utils
import params
# from django.core.validators import email_re


class LoginForm(forms.Form):
    username = forms.CharField(label='username', max_length=20)
    password = forms.CharField(widget=forms.PasswordInput)

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
    name = forms.CharField(label='Your username', max_length=30, required=True)
    email = forms.EmailField(label='Your email', max_length=30, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    confirm = forms.CharField(widget=forms.PasswordInput, required=True)

    def clean_name(self):
        name = self.cleaned_data['name']
        if name in User.objects.distinct('username'):
            raise ValidationError("That username is already taken")
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


# class NseArticleForm(forms.Form):
#     headline = forms.CharField(max_length=200, label='Headline')
#     content = forms.CharField(widget=forms.Textarea, label='Content')
#     article_id = forms.CharField(max_length=30, initial=None)

#     def __init__(self, *args, **kwargs):
#         nse_headlines = kwargs.pop('nse_headlines')
#         nse_headline = kwargs.pop('nse_headline')
#         categories = kwargs.pop('categories')
#         category = kwargs.pop('category')

#         super(WritersArticleForm, self).__init__(*args, **kwargs)

#         self.fields['nse_headlines'] = forms.ChoiceField(
#             choices=[choice for choice in nse_headlines],
#             label='NSE headlines. See "Articles" tab for content',
#             initial=(nse_headline),
#         )
#         self.fields['categories'] = forms.ChoiceField(
#             choices=[choice for choice in categories],
#             label='Pick a primary category',
#             initial=(category),
#         )


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

    headline = forms.CharField(max_length=200)
    content = forms.CharField(widget=forms.Textarea)
    article_id = forms.CharField(max_length=30, initial=None, required=False)

    def __init__(self, *args, **kwargs):
        edit = False
        lock = False

        if 'edit' in kwargs:
            headline = kwargs.pop('headline')
            content = kwargs.pop('content')
            article_id = kwargs.pop('article_id')
            kwargs.pop('edit')
            edit = True

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

        if edit:
            self.fields['headline'] = forms.CharField(
                max_length=200, initial=headline)
            self.fields['content'] = forms.CharField(
                widget=forms.Textarea, initial=content)
            self.fields['article_id'] = forms.CharField(
                max_length=30, initial=article_id, required=False)

        if lock:
            for field in lock:
                self.fields[field].widget.attrs = {'disabled': 'disabled'}
