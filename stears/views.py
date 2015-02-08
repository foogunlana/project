from django.shortcuts import render
from stears.forms import LoginForm, ArticleImageForm, AddWritersForm, RemoveWritersForm, \
    RegisterForm, KeyWordsForm, ChoiceForm, ForgotPasswordForm, CommentForm, SuggestForm, WritersArticleForm, \
    NseArticleForm, ChangePasswordForm, ArticleReviewForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, logout
from mongoengine.django.auth import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from stears.utils import article_key_words, revive_from_trash, rtf_edit_article, add_writers,\
    remove_writers, make_username, migrate_article, mongo_calls, make_comment, forgot_password_email,\
    save_writers_article, accept_to_write, request_json, make_url, move_to_trash, suggest_nse_article, \
    update_writers_article, edit_user, make_writer_id, make_writers_article, submit_writers_article, \
    handle_uploaded_file, put_in_review, new_member

from stears.permissions import approved_writer, is_a_boss, writer_can_edit_article
from stears.models import ArticleImageModel
from mongoengine.queryset import DoesNotExist

# from stears.utils import handle_uploaded_file

import params
import json

# ALL NOTIFICATIONS SHOULD RECORD THE TIME AS WELL

# Imaginary function to handle an uploaded file.


@user_passes_test(lambda u: approved_writer(u), login_url='/stears/noaccess/')
def upload_photo(request):
    if request.method == 'POST':
        form = ArticleImageForm(request.POST, request.FILES)
        if form.is_valid():
            # print request.FILES
            # handle_uploaded_file(request.FILES['article_image'])
            article_image = ArticleImageModel(
                docfile=request.FILES['article_image']
            )
            article_image.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            print "Invalid"
    else:
        form = ArticleImageForm()
    photos = ArticleImageModel.objects.all()
    return render(request, 'stears/photos.html', {'form': form, 'photos': photos})


@user_passes_test(lambda u: approved_writer(u), login_url='/stears/noaccess/')
def research(request):
    choices = [key for key in params.glo_trybe_data]
    form = ChoiceForm(choices=choices)
    writers_article_form = WritersArticleForm()
    return render(request, 'stears/research.html', {'form': form, 'writers_article_form': writers_article_form})


@user_passes_test(lambda u: approved_writer(u), login_url='/stears/noaccess/')
def gts(request):
    site = {}
    choices = [key for key in params.glo_trybe_data]
    if request.method == 'POST':
        form = ChoiceForm(request.POST, choices=choices)

        if form.is_valid():
            choice = form.cleaned_data['choice']
            # print choice
            # print choices
            URL = make_url(params.glo_trybe_data[choice], False)
            j_array = request_json(URL)
            site = json.dumps(j_array)
            print URL
            print j_array

    return render(request, 'stears/gts.html', {'site': site})


def change_password(request):
    errors = []

    if request.method == 'GET':
        change_password_form = ChangePasswordForm()

    if request.method == 'POST':
        change_password_form = ChangePasswordForm(
            request.POST
        )

        if change_password_form.is_valid():

            username = change_password_form.cleaned_data['username']
            password = change_password_form.cleaned_data['old_password']

            try:
                user = User.objects.get(username=username)
                if user.check_password(password):
                    user.backend = params.MONGOENGINE_BACKEND
                    if user:
                        user.set_password(str(
                            change_password_form.cleaned_data['new_password']))
                        user.save()
                        return HttpResponseRedirect(reverse('stears:login'))
                    else:
                        errors.append(
                            'Oops! something went wrong. please refresh')
                else:
                    errors.append('Invalid username and password combination')
            except DoesNotExist:
                errors.append('Invalid username and password combination')
            except Exception as e:
                return HttpResponse(str(e))

    context = {'change_password_form': change_password_form, 'errors': errors}
    return render(request, 'stears/change_password.html', context)
    # Return an 'invalid login' error message.


def forgot_password(request):
    errors = []

    if request.method == 'GET':
        forgot_password_form = ForgotPasswordForm()

    if request.method == 'POST':
        forgot_password_form = ForgotPasswordForm(
            request.POST
        )

        if forgot_password_form.is_valid():
            email = forgot_password_form.cleaned_data['email']
            forgot_password_email(email)
            forgot_password_form = {}
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    context = {'forgot_password_form': forgot_password_form, 'errors': errors}
    return render(request, 'stears/forgot_password.html', context)


def login_view(request):
    email = request.POST.get('email', '')
    password = request.POST.get('password', '')
    errors = []

    if request.method == 'POST':
        try:
            user = User.objects.get(email=email)

            if user.check_password(password):
                user.backend = params.MONGOENGINE_BACKEND
                if user.is_active:
                    login(request, user)
                if user:
                    request.session.set_expiry(
                        params.SESSION_AGE)  # 1 hour timeout
                    return HttpResponseRedirect(reverse('stears:articles_group',  args=(), kwargs={'group': 'peers'}))
                else:
                    errors.append('Oops! something went wrong. please refresh')
            else:
                errors.append('Invalid login')
        except DoesNotExist:
            errors.append('Invalid login')
        except Exception as e:
            return HttpResponse(str(e))

    login_form = LoginForm()
    context = {'login_form': login_form, 'errors': errors}
    return render(request, 'stears/login.html', context)
    # Return an 'invalid login' error message.


def register(request):
    errors = []
    if request.method == 'GET':
        if request.user.is_authenticated():
            logout(request)

    registered = False
    register_form = RegisterForm()

    if request.method == 'POST':
        register_form = RegisterForm(request.POST)

        if register_form.is_valid():

            member = User()
            email = register_form.cleaned_data['email']
            member.email = email
            member.first_name = register_form.cleaned_data['first_name']
            member.last_name = register_form.cleaned_data['last_name']
            member.username = make_username(
                member.first_name, member.last_name)
            # member.password = str(register_form.cleaned_data['password'])
            member.set_password(
                str(register_form.cleaned_data['password']))
            member.save()
            new_member(register_form)
            make_writer_id(member.username)

            registered = True
            # Notify boss that a new member has registered and is seeking
            # approval

            return HttpResponseRedirect(reverse('stears:writers_write'))

            # except Exception as e:
            #     errors.append(str(e))
            #     print e
            #     return render(request, 'stears/register.html', {
            #         'register_form': register_form, 'errors': errors})
        else:
            errors.append(register_form.errors)
            return render(request, 'stears/register.html', {
                'register_form': register_form, 'errors': errors})

    context = {'register_form': register_form, 'registered': registered}
    return render(request, 'stears/register.html', context)


@login_required(login_url='/stears/login')
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('stears:writers_write'))


@user_passes_test(lambda u: approved_writer(u), login_url='/stears/noaccess/')
def writers_home_test(request, group):
    user = request.user
    editable_fields = ['Headline', 'Content']
    visible_fields = ['headline', 'content', 'reporter', 'state']
    articles = []
    article_collection = mongo_calls('articles')
    nostates = False

    writers_article_form = WritersArticleForm()
    if request.method == 'GET':
        if not group:
            articles = [article for article in article_collection.find({
                '$query': {"$or": [{'type': 'writers_article'}, {'type': 'nse_article'}]},
                '$orderby': {'time': -1, 'state': 1}})]

        elif group == 'NSE':
            articles = [
                article for article in article_collection.find({'type': 'nse_article'})]
        elif group == 'peers':
            articles = [article for article in article_collection.find({
                '$query': {'type': 'writers_article'},
                '$orderby': {'time': -1, 'state': 1, }})]

    context = {'editable_fields': editable_fields, "writers_article_form": writers_article_form,
               'visible_fields': visible_fields, 'articles': articles, 'username': user, 'nostates': nostates}
    return render(request, 'stears/writers_home_test.html', context)


@user_passes_test(lambda u: approved_writer(u), login_url='/stears/noaccess/')
def writers_list(request):
    writers = []
    users = mongo_calls('user')
    if request.method == 'GET':
        writers = [writer for writer in users.find(
            {'$query': {}, '$orderby': {'state': 1}})]

        writers_article_form = WritersArticleForm()

    context = {
        'writers': writers, 'writers_article_form': writers_article_form}
    return render(request, 'stears/writers_list.html', context)


@user_passes_test(lambda u: approved_writer(u), login_url='/stears/noaccess/')
def writers_write(request):
    context = {}
    messages = []
    users = mongo_calls('user')
    article_collection = mongo_calls('articles')

    # USE group and aggregate to get suggestions and articles and reviews all
    # together!!
    if request.method == 'GET':
        username = str(request.user)
        # get suggested articles
        writer = users.find_one({'username': username})
        suggested_articles = writer.get('suggested_articles', [])
        suggestions = [article for article in article_collection.find(
            {'article_id': {'$in': suggested_articles}})]

        articles = [
            article for article in article_collection.find(
                {"$query": {'writer': username}, "$orderby": {"time": -1}})]

        reviews = [
            article for article in article_collection.find(
                {"$query": {'article_id': {'$in': writer['reviews']}}, "$orderby": {"time": -1}})
            if article['state'] == 'in_review'
        ]

        writers_article_form = WritersArticleForm()

        context = {"writers_article_form": writers_article_form, 'articles':
                   articles, 'suggestions': suggestions, 'messages': messages, 'reviews': reviews}

    return render(request, 'stears/writers_write.html', context)


@user_passes_test(lambda u: approved_writer(u), login_url='/stears/noaccess/')
def writers_post(request, nse):
    # Notify the boss that a writer has submitted/saved an article and what
    # article it is
    writer = str(request.user)

    if request.method == 'POST':
        form = WritersArticleForm(
            request.POST,
        )
        if form.is_valid():
            article_id = form.cleaned_data.get('article_id', 0)
            if article_id:
                update_writers_article(writer, form)
            else:
                new_article = make_writers_article(form, writer)
                article_id = save_writers_article(new_article)
            if request.POST.get('submit', '') == 'review':
                put_in_review(article_id)
        else:
            print form.errors

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@user_passes_test(lambda u: approved_writer(u), login_url='/stears/noaccess/')
def writer_detail(request, name):
    users = mongo_calls('user')
    article_collection = mongo_calls('articles')
    writer = users.find_one({'username': name})
    context = {}
    # GET ARTICLE STRAIGHT FROM WRITER
    # FOR NOW get articles by search
    if request.method == 'GET':
        writers_article_form = WritersArticleForm()

        articles = [
            article for article in article_collection.find({'writer': name})]

        context = {'writer': writer, 'articles': articles,
                   'writers_article_form': writers_article_form}
    return render(request, 'stears/writer_detail.html', context)


@user_passes_test(lambda u: is_a_boss(u), login_url='/stears/noaccess/')
def delete_article(request):
    # Notify everyone that the article has been deleted
    if request.method == 'POST':
        pk = request.POST.get('article_id', None)
        if not pk:
            raise Exception('Nothing to delete')
        pk = int(pk)
        move_to_trash(pk)
    return HttpResponseRedirect(reverse('stears:writers_home'))


@user_passes_test(lambda u: approved_writer(u), login_url='/stears/noaccess/')
def bin(request):
    username = str(request.user)
    bin = mongo_calls('bin')
    articles = [article for article in bin.find({
        '$query': {'type': 'writers_article', 'writer': username},
        '$orderby': {'time': -1, 'state': 1}})]

    context = {'articles': articles}
    return render(request, 'stears/bin.html', context)


@user_passes_test(lambda u: approved_writer(u), login_url='/stears/noaccess/')
def revive_article(request):
    if request.method == 'POST':
        pk = request.POST.get('article_id', None)
        if not pk:
            return HttpResponseRedirect(reverse('stears:noaccess'))
        pk = int(pk)
        revive_from_trash(pk)

    return HttpResponseRedirect(reverse('stears:bin'))


@user_passes_test(lambda u: approved_writer(u), login_url='/stears/noaccess/')
def article_detail(request, **kwargs):
    user = request.user
    article_collection = mongo_calls('articles')
    users = mongo_calls('users')

    if request.method == 'GET':
        pk = int(kwargs.pop('pk'))
        comment_form = CommentForm()
        key_words_form = KeyWordsForm()

    article = article_collection.find_one({'article_id': pk})

    if not article:
        return HttpResponseRedirect(reverse('stears:noaccess'))

    if article['type'] == 'writers_article':
        nse_id = article['nse_article_id']
        category = article['category']
    else:
        nse_id = pk
        category = "stearsTier_1"

    approved_writers = users.find(
        {'state': 'approved'}).distinct('username')
    suggest_form = SuggestForm(my_arg=approved_writers)

    locked_fields = ['nse_headlines', 'categories']

    if writer_can_edit_article(str(user), article):
        if article.get('type', '') == 'writers_article':
            writers_article_form = WritersArticleForm(
                initial={'nse_headlines': nse_id,
                         'categories': category,
                         'article_id': pk,
                         'content': article['content'],
                         'headline': article['headline']},
                lock=locked_fields,
            )

        elif article['type'] == 'nse_article':
            writers_article_form = NseArticleForm(
                initial={'nse_headlines': nse_id}
            )
    else:
        writers_article_form = {}

    add_writers_form = AddWritersForm(article_id=pk)
    remove_writers_form = RemoveWritersForm(article_id=pk)
    context = {'article': article, 'suggest_form': suggest_form, 'remove_writers_form': remove_writers_form, 'key_words_form': key_words_form,
               'writers_article_form': writers_article_form, 'add_writers_form': add_writers_form, 'comment_form': comment_form}

    return render(request, 'stears/article_detail.html', context)


@user_passes_test(lambda u: approved_writer(u), login_url='/stears/noaccess/')
def comment(request, pk):
    if request.method == 'POST':
        article_id = int(pk)
        comment_form = CommentForm(
            request.POST,
        )
        if comment_form.is_valid():
            make_comment(
                str(request.user), int(article_id),
                comment_form.cleaned_data['comment'])
        else:
            print "Invalid"
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def add_key_words(request, pk):
    if request.method == 'POST':
        key_words_form = KeyWordsForm(
            request.POST
        )
        if key_words_form.is_valid():
            article_key_words(
                int(pk),
                key_words_form.cleaned_data['tags'],
                other=key_words_form.cleaned_data['other'])
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            print "Invalid"
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@user_passes_test(lambda u: is_a_boss(u), login_url='/stears/noaccess/')
def approve_writer(request):
    # Notify boss and the writer that a new writer has been approved
    if request.method == 'POST':
        username_approve = request.POST.get('approve', '')
        username_revoke = request.POST.get('revoke', '')

        if username_approve:
            edit_user(username_approve, 'state', 'approved')
        if username_revoke:
            edit_user(username_revoke, 'state', 'request')

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@user_passes_test(lambda u: is_a_boss(u), login_url='/stears/noaccess/')
def approve_article(request):
    # Notify everyone that a new article has been committed or notify writer
    # that article was rejected
    if request.method == 'POST':
        commit_id = request.POST.get('commit_id', '')
        reject_id = request.POST.get('reject_id', '')
        article_collection = mongo_calls('articles')

        if reject_id:
            article_collection.update({
                "article_id": int(reject_id)
            }, {'$set': {"state": 'in_progress'}
                }, False, False
            )

        elif commit_id:
            migrate_article(int(commit_id))

    return HttpResponseRedirect(reverse('stears:articles_group', args=(), kwargs={'group': 'peers'}))

# Notify writer that an article has been suggested and by whom


@user_passes_test(lambda u: is_a_boss(u), login_url='/stears/noaccess/')
def suggest(request):
    users = mongo_calls('user')
    if request.method == 'POST':
        approved_writers = users.find(
            {'state': 'approved'}).distinct('username')
        suggest_form = SuggestForm(request.POST, my_arg=approved_writers)
        if suggest_form.is_valid():
            username = str(suggest_form.cleaned_data.get('user', ''))
            article_id = request.POST['article_id']
            suggest_nse_article(username, article_id)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@user_passes_test(lambda u: is_a_boss(u), login_url='/stears/noaccess/')
def accept_article_category(request):
    # Notify writer that he is now allowed to go ahead and write this article
    accept_id = request.POST.get('accept_id', '')
    not_accept_id = request.POST.get('not_accept_id', '')

    if accept_id:
        accept_to_write(int(accept_id))
    elif not_accept_id:
        move_to_trash(int(not_accept_id))
        pass

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@user_passes_test(lambda u: approved_writer(u), login_url='/stears/noaccess/')
def review_article(request, pk):
    username = str(request.user)
    pk = int(pk)
    articles = mongo_calls('articles')
    article = articles.find_one({'article_id': pk})
    if (not article.get('reviewer', '') == username) or article['state'] != 'in_review':
        return HttpResponseRedirect(reverse('stears:noaccess'))
    if request.method == "POST":
        article_review_form = ArticleReviewForm(request.POST)
        if article_review_form.is_valid():
            submit_writers_article(pk, article_review_form.cleaned_data)
        else:
            print "Invalid"
        return HttpResponseRedirect(reverse('stears:writers_write'))
    article_review_form = ArticleReviewForm()
    return render(request, 'stears/review_article.html', {'article': article, 'article_review_form': article_review_form})


@user_passes_test(lambda u: approved_writer(u), login_url='/stears/noaccess/')
def add_writer_to_article(request):
    if request.method == "POST":
        article_id = request.POST['article_id']
        if not article_id:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        add_writers_form = AddWritersForm(
            request.POST, article_id=article_id)
        if add_writers_form.is_valid():
            usernames = add_writers_form.cleaned_data['writers']
            add_writers(int(request.POST['article_id']), usernames)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@user_passes_test(lambda u: approved_writer(u), login_url='/stears/noaccess/')
def remove_writer_from_article(request):
    if request.method == "POST":
        remove_writers_form = RemoveWritersForm(
            request.POST, article_id=request.POST['article_id'])
        if remove_writers_form.is_valid():
            usernames = remove_writers_form.cleaned_data['writers']
            remove_writers(int(request.POST['article_id']), usernames)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@user_passes_test(lambda u: approved_writer(u), login_url='/stears/noaccess/')
def pipeline(request):
    if request.method == 'GET':
        migrations = mongo_calls('migrations')
        articles = [article for article in migrations.find(
            {'$query': {}, '$orderby': {'time': -1}})]
        # Articles here cannot be found in the article database and that will
        # cause a few problems!
    context = {'articles': articles, 'nostates': True}
    return render(request, 'stears/pipeline.html', context)


@user_passes_test(lambda u: is_a_boss(u), login_url='/stears/noaccess/')
def submissions(request):
    if request.method == 'GET':
        articles = mongo_calls('articles')
        submitted_articles = [article for article in articles.find(
            {'$query': {'state': 'submitted'}, '$orderby': {'time': -1}})]
    context = {'articles': submitted_articles, 'nostates': True}
    return render(request, 'stears/submissions.html', context)


@user_passes_test(lambda u: approved_writer(u), login_url='/stears/noaccess/')
def remove_tag(request):
    if request.method == 'POST':
        code = request.POST.get('data', None)
        if not code:
            print "Error!"
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        id_and_tag = code.split(',')
        print id_and_tag
        pk, tag = int(id_and_tag[0]), str(id_and_tag[1])

        articles = mongo_calls('articles')
        articles.update(
            {'article_id': pk},
            {'$pull': {'keywords': tag}},
            False,
            False
        )

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@user_passes_test(lambda u: approved_writer(u), login_url='/stears/noaccess/')
def edit_rich_text(request, pk):
    user = request.user
    articles = mongo_calls('articles')
    pk = int(pk)
    article = articles.find_one({'article_id': pk})

    if not writer_can_edit_article(str(user), article):
        return HttpResponseRedirect(reverse('stears:noaccess'))

    if request.method == "POST":
        rtf_content = request.POST.get('content', '')
        if not rtf_content:
            return HttpResponse("There wasn't any content")
        rtf_edit_article(article, rtf_content)
        return HttpResponse("Successfully updated")

    context = {'content': article.get(
        'rtf_content', article['content']), 'article': article}
    return render(request, 'stears/wym.html', context)


def noaccess(request):
    user = request.user
    if user.is_authenticated():
        return render(request, 'stears/noaccess.html', {})
    login_form = LoginForm()
    context = {'login_form': login_form}
    return render(request, 'stears/login.html', context)


def home(request):
    return render(request, 'stears/home.html', {})
