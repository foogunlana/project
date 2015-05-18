from django import forms
from django.forms.extras.widgets import SelectDateWidget
# from django.contrib.auth.models import User
from mongoengine.django.auth import User
from django.core.exceptions import ValidationError
from django.template.defaultfilters import filesizeformat
from utils import mongo_calls
from writers import settings
import utils
import params
import re
# from django.core.validators import email_re

BIRTH_YEAR_CHOICES = ('1991', '1992', '1993')


class ProfileImageForm(forms.Form):
    title = forms.CharField(max_length=50, required=True)
    profile_image = forms.FileField(label="Please select an image")


class ArticleImageForm(forms.Form):
    title = forms.CharField(max_length=50, required=True)
    article_image = forms.FileField(label="Please select an image: ")

    def clean_article_image(self):
        image = self.cleaned_data['article_image']
        if image.content_type in settings.CONTENT_TYPES:
            if image._size > settings.MAX_UPLOAD_SIZE:
                raise forms.ValidationError('Please keep filesize under %s. Current filesize %s' % (
                    filesizeformat(settings.MAX_UPLOAD_SIZE), filesizeformat(image._size)))
        else:
            raise forms.ValidationError(
                'Not supported, image must be jpeg or png')
        return image


class LoginForm(forms.Form):
    email = forms.EmailField(label='Email', max_length=30, widget=forms.TextInput(
        attrs={'data-validation': 'length', 'data-validation-length': 'min1'}))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'data-validation': 'length', 'data-validation-length': 'min1'}))


class ArticleReviewForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(ArticleReviewForm, self).__init__(*args, **kwargs)
        for field in params.review_statements:
            field_dict = params.review_statements[field]
            self.fields[field] = forms.ChoiceField(
                widget=forms.Select(attrs={
                    'class': 'standard-choice',
                    'title': '<p><h6 style="color:white">%s</h6>%s</p>'
                    '<p><h6 style="color:white">%s</h6>%s</p>'
                    '<p><h6 style="color:white">%s</h6>%s</p>'
                    % (field_dict['a'][0], field_dict['a'][1],
                        field_dict['b'][0], field_dict['b'][1],
                        field_dict['c'][0], field_dict['c'][1]),
                }),
                choices=[
                    ('None', None), ('a', field_dict['a'][0]), ('b', field_dict['b'][0]), ('c', field_dict['c'][0])],
                required=True,
                label=field
            )

    def clean(self):
        for field in self.fields:
            print field, self.cleaned_data
            if (not self.cleaned_data[field]) or (self.cleaned_data[field] == 'None'):
                raise ValidationError("All fields are required")
        else:
            return self.cleaned_data


class AddWritersForm(forms.Form):

    def __init__(self, *args, **kwargs):
        users = mongo_calls('user')
        articles = mongo_calls('articles')
        approved_writers = users.find(
            {'$or': [{'state': 'approved'}, {'state': 'admin'}]}).distinct('username')
        article_id = int(kwargs.pop('article_id'))
        article = articles.find_one({'article_id': article_id})
        super(AddWritersForm, self).__init__(*args, **kwargs)
        writers_list = list(
            set(approved_writers) - set(article['writers']['others']))
        self.fields['writers'] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            choices=[(x, x) for x in writers_list],
        )

class AllocationForm(forms.Form):
    page = forms.CharField(max_length=30, required=True)
    section = forms.CharField(max_length=30, required=True)
    article_id = forms.CharField(max_length=10, required=True)

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
    email = forms.EmailField(max_length=30, required=True, widget=forms.TextInput(
        attrs={'data-validation': 'email'}), label="Email Address")
    password = forms.CharField(required=True, widget=forms.PasswordInput(
        attrs={'data-validation': 'length', 'data-validation-length': 'min2'}))
    confirm = forms.CharField(required=True, widget=forms.PasswordInput(
        attrs={'data-validation': 'length', 'data-validation-length': 'min2'}))

    # EXTRAS

    dob = forms.DateField(
        required=True,
        label='Date of birth',
        widget=forms.DateInput(attrs={'data-validation': 'required'}))
    study = forms.CharField(max_length=50, label="University degree", required=True, widget=forms.TextInput(
        attrs={'data-validation': 'required'}))
    occupation = forms.CharField(max_length=50, required=True, widget=forms.TextInput(
        attrs={'data-validation': 'required'}))
    interests = forms.CharField(
        required=True,
        label="Intellectual interests",
        widget=forms.Textarea(attrs={
            'data-validation': 'length',
            'data-validation-length': 'min10',
            'style': 'height:100px;'
        }))

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields['role'] = forms.ChoiceField(
            choices=params.writer_category_tuples,
            label='Role',
            required=True,
        )
        self.fields['sex'] = forms.ChoiceField(
            choices=[('M', 'Male'), ('F', 'Female')],
            label='Gender',
            required=True,
        )

    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']
        if not re.match(r'^[a-zA-Z]+$', first_name):
            raise forms.ValidationError(
                "Name should include only alphanumeric characters, letters and numbers")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data['last_name']
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


class DateForm(forms.Form):
    dob = forms.DateField(required=True)


class EditWriterForm(forms.Form):
    username = forms.CharField(max_length=30, required=True, widget=forms.TextInput(
        attrs={'data-validation': 'length', 'data-validation-length': 'min2'}))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(
        attrs={'data-validation': 'length', 'data-validation-length': 'min2'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(
        attrs={'data-validation': 'length', 'data-validation-length': 'min2'}))
    email = forms.EmailField(max_length=30, required=True, widget=forms.TextInput(
        attrs={'data-validation': 'email'}), label="Email Address")
    new_email = forms.EmailField(max_length=30, required=True, widget=forms.TextInput(
        attrs={'data-validation': 'email'}), label="Email Address")

    # EXTRAS

    dob = forms.DateField(
        required=True,
        label='Date of birth',
        widget=forms.DateInput(attrs={'data-validation': 'required'}))
    study = forms.CharField(max_length=50, label="University degree", required=True, widget=forms.TextInput(
        attrs={'data-validation': 'required'}))
    occupation = forms.CharField(max_length=50, required=True, widget=forms.TextInput(
        attrs={'data-validation': 'required'}))
    interests = forms.CharField(
        required=True,
        label="Intellectual interests",
        widget=forms.Textarea(attrs={
            'data-validation': 'length',
            'data-validation-length': 'min10',
            'style': 'height:100px;'
        }))

    def __init__(self, *args, **kwargs):
        super(EditWriterForm, self).__init__(*args, **kwargs)
        self.fields['role'] = forms.ChoiceField(
            choices=params.writer_category_tuples,
            label='Role',
            required=True,
        )
        self.fields['sex'] = forms.ChoiceField(
            choices=[('M', 'Male'), ('F', 'Female')],
            label='Gender',
            required=True,
        )

    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']
        if not re.match(r'^[a-zA-Z]+$', first_name):
            raise forms.ValidationError(
                "Name should include only letters ")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data['last_name']
        if not re.match(r'^[a-zA-Z]+$', last_name):
            raise forms.ValidationError(
                "Name should include only letters ")
        return last_name

    def clean_new_email(self):
        new_email = self.cleaned_data['new_email']
        if new_email == self.cleaned_data['email']:
            return new_email
        elif new_email in User.objects.distinct('email'):
            raise ValidationError("That email address is already registered")
        # if not email_re.match(email):
        #   raise ValidationError("That email address is not valid")
        return new_email


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
        # 'class': 'wymeditor',
        # 'data-wym-initialized': 'yes',
    }))
    article_id = forms.CharField(
        max_length=30, initial=0, required=False)

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
        }), required=True, error_messages={
            'required': 'You did not enter any comment',
            'invalid': 'Your comment entry was invalid',
        })


class KeyWordsForm(forms.Form):
    other = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'other-choice'
        }), max_length=40, initial='None', required=True, error_messages={
            'invalid': 'Your key word was invalid and was not saved'
        })

    def __init__(self, *args, **kwargs):
        super(KeyWordsForm, self).__init__(*args, **kwargs)
        collection = mongo_calls('nse_news')
        tag_doc = collection.find_one(
            {'type': 'tags'}, {'keywords': 1, '_id': 0})
        if tag_doc:
            tags = ['None'] + tag_doc.get('keywords', [])
        else:
            tags = ['None']

        self.fields['tags'] = forms.ChoiceField(
            widget=forms.Select(attrs={'class': 'standard-choice'}),
            choices=[(tag, tag) for tag in tags],
            required=False,
        )

    def clean_other(self):
        other = self.cleaned_data['other']
        if not re.match(r'^[a-zA-Z\d\-_\s]+$', other):
            raise forms.ValidationError(
                "Key words should include only alphanumeric characters and spaces")
        return other
