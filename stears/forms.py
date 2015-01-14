from django import forms
# from django.contrib.auth.models import User
from mongoengine.django.auth import User
from django.core.exceptions import ValidationError
from utils import mongo_calls
import utils
import params
import re
# from django.core.validators import email_re


class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50, required=True)
    file = forms.FileField()


class LoginForm(forms.Form):
    email = forms.EmailField(label='Email', max_length=20, widget=forms.TextInput(
        attrs={'data-validation': 'length', 'data-validation-length': 'min1'}))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'data-validation': 'length', 'data-validation-length': 'min1'}))


class AddWritersForm(forms.Form):
    users = mongo_calls('user')
    writers_list = users.find(
        {'$or': [{'state': 'approved'}, {'state': 'admin'}]}).distinct('username')
    writers = forms.MultipleChoiceField(
        required=True,
        widget=forms.CheckboxSelectMultiple, choices=[(x, x) for x in writers_list])


class RemoveWritersForm(forms.Form):

    def __init__(self, *args, **kwargs):
        articles = mongo_calls('articles')
        article_id = int(kwargs.pop('article_id'))
        article = articles.find_one({'article_id': article_id})
        super(RemoveWritersForm, self).__init__(*args, **kwargs)
        writers_list = [(x, x) for x in article['writers']['others']]
        self.fields['writers'] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            choices=writers_list,
        )


class ChoiceForm(forms.Form):

    def __init__(self, *args, **kwargs):
        choices = kwargs.pop('choices')
        super(ChoiceForm, self).__init__(*args, **kwargs)
        self.fields['choice'] = forms.ChoiceField(
            choices=[(x, x) for x in choices],
            label='Choose what to research',
        )


class RegisterForm(forms.Form):
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(
        attrs={'data-validation': 'length', 'data-validation-length': 'min2'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(
        attrs={'data-validation': 'length', 'data-validation-length': 'min2'}))
    email = forms.EmailField(label='Your email', max_length=30, required=True)
    password = forms.CharField(required=True, widget=forms.PasswordInput(
        attrs={'data-validation': 'length', 'data-validation-length': 'min2'}))
    confirm = forms.CharField(required=True, widget=forms.PasswordInput(
        attrs={'data-validation': 'length', 'data-validation-length': 'min2'}))

    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']
        if not re.match(r'^[a-zA-Z]+$', first_name):
            raise forms.ValidationError(
                "Name should include only alphanumeric characters, letters and numbers")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data['first_name']
        if not re.match(r'^[a-zA-Z]+$', last_name):
            raise forms.ValidationError(
                "Name should include only alphanumeric characters, letters and numbers")
        return last_name

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
    other = forms.CharField(
        widget=forms.TextInput(attrs={
            'data-validation': 'alphanumeric', 'class': 'other-choice'
        }), max_length=200, initial='None', required=True, error_messages={
            'invalid': 'Your key word was invalid and was not saved'
        })

    def __init__(self, *args, **kwargs):
        super(KeyWordsForm, self).__init__(*args, **kwargs)
        collection = mongo_calls('nse_news')
        tag_doc = collection.find_one({'type': 'tags'})
        # key_words = key_word_doc.get('tags','')
        if tag_doc:
            tags = tag_doc.get('keywords', []) + ['None']
        else:
            tags = ['None', 'One', 'two', 'three']

        self.fields['tags'] = forms.ChoiceField(
            widget=forms.Select(attrs={'class': 'standard-choice'}),
            choices=[(tag, tag) for tag in tags],
            required=False,
        )

    def clean_keywords(self):
        other = self.cleaned_data['other']
        if not re.match(r'^[a-zA-Z0-9]+$', other):
            raise forms.ValidationError(
                "Key words should include only alphanumeric characters")
        return other
