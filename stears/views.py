from django.shortcuts import render
from stears.forms import LoginForm, RegisterForm, ChoiceForm, ForgotPasswordForm, SuggestForm, WritersArticleForm, NseArticleForm, ChangePasswordForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, logout
from mongoengine.django.auth import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from stears.utils import migrate_article, forgot_password_email, save_writers_article, accept_to_write, get_nse_headlines, request_json, make_url, move_to_trash, suggest_nse_article, update_writers_article, retrieve_values, edit_user, make_writer_id, make_writers_article, submit_writers_article, client as mclient
from stears.permissions import approved_writer, is_a_boss, writer_can_edit_article
from mongoengine.queryset import DoesNotExist


import params
import json

# ALL NOTIFICATIONS SHOULD RECORD THE TIME AS WELL


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
        # FIX CHECK_PASSWORD FUNCTION if
        # user.check_password(request.POST['password']):
                if user.password == password:
                    user.backend = params.MONGOENGINE_BACKEND
                    if user:
                        user.password = str(
                            change_password_form.cleaned_data['new_password'])
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

    context = {'forgot_password_form': forgot_password_form, 'errors': errors}
    return render(request, 'stears/forgot_password.html', context)


def login_view(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    errors = []

    if request.method == 'POST':
        try:
            user = User.objects.get(username=username)
        # FIX CHECK_PASSWORD FUNCTION if
        # user.check_password(request.POST['password']):
            if user.password == password:
                user.backend = params.MONGOENGINE_BACKEND
                if user.is_active:
                    login(request, user)
                if user:
                    request.session.set_expiry(
                        params.SESSION_AGE)  # 1 hour timeout
                    return HttpResponseRedirect(reverse('stears:writers_write'))
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
            try:
                member = User()
                member.username = register_form.cleaned_data['name']
                member.email = register_form.cleaned_data['email']
                member.password = str(register_form.cleaned_data['password'])
                member.save()
                edit_user(member.username, 'state', 'request')
                # edit_user(member.username,'account','request')
                make_writer_id(member.username)

                registered = True
                # Notify boss that a new member has registered and is seeking
                # approval

                return HttpResponseRedirect(reverse('stears:writers_write'))

            except Exception as e:
                errors.append(str(e))
                return render(request, 'stears/register.html', {
                    'register_form': register_form, 'errors': errors})

    context = {'register_form': register_form, 'registered': registered}
    return render(request, 'stears/register.html', context)


@login_required(login_url='/stears/login')
def logout_view(request):
    logout(request)
    login_form = LoginForm()
    context = {'login_form': login_form}
    return render(request, 'stears/login.html', context)


@user_passes_test(lambda u: approved_writer(u), login_url='/stears/noaccess/')
def writers_home_test(request, group):
    user = request.user
    editable_fields = ['Headline', 'Content']
    visible_fields = ['headline', 'content', 'reporter', 'state']
    articles = []

    writers_article_form = WritersArticleForm()
    if request.method == 'GET':
        if not group:
            articles = [article for article in mclient.stears.articles.find(
                {'type': 'writers_article'})] + [article for article in mclient.stears.articles.find({'type': 'nse_article'})]
        elif group == 'NSE':
            articles = [
                article for article in mclient.stears.articles.find({'type': 'nse_article'})]
        elif group == 'peers':
            articles = [article for article in mclient.stears.articles.find(
                {'type': 'writers_article'})]
        else:
            articles = [article for article in mclient.stears.articles.find(
                {'type': 'writers_article', 'category': params.article_categories[group]})]

    context = {'editable_fields': editable_fields, "writers_article_form": writers_article_form,
               'visible_fields': visible_fields, 'articles': articles, 'username': user}
    return render(request, 'stears/writers_home_test.html', context)


@user_passes_test(lambda u: is_a_boss(u), login_url='/stears/noaccess/')
def writers_list(request):
    writers = []
    if request.method == 'GET':
        writers = [writer for writer in mclient.stears.user.find()]

        writers_article_form = WritersArticleForm()

    context = {
        'writers': writers, 'writers_article_form': writers_article_form}
    return render(request, 'stears/writers_list.html', context)


@user_passes_test(lambda u: approved_writer(u), login_url='/stears/noaccess/')
def writers_write(request):
    context = {}
    messages = []

    if request.method == 'GET':
        username = str(request.user)
        # get articles specific to writer
        writer = mclient.stears.user.find_one({'username': username})
        suggested_articles = writer.get('suggested_articles', [])
        suggestions = [mclient.stears.articles.find_one({'article_id': int(
            article_id), 'type': 'nse_article'}) for article_id in suggested_articles]

        articles = [
            article for article in mclient.stears.articles.find({'writer': username})]

        writers_article_form = WritersArticleForm()

        context = {"writers_article_form": writers_article_form, 'articles':
                   articles, 'suggestions': suggestions, 'messages': messages}

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
            if request.POST.get('submit', '') == 'submit':
                submit_writers_article(article_id)
        else:
            print form.errors

    return HttpResponseRedirect(reverse('stears:writers_write'))


@user_passes_test(lambda u: is_a_boss(u), login_url='/stears/noaccess/')
def writer_detail(request, name):
    writer = mclient.stears.user.find_one({'username': name})
    context = {}
    # GET ARTICLE STRAIGHT FROM WRITER
    # FOR NOW get articles by search
    if request.method == 'GET':
        writers_article_form = WritersArticleForm()

        articles = [
            article for article in mclient.stears.articles.find({'writer': name})]
        context = {'writer': writer, 'articles': articles,
                   'writers_article_form': writers_article_form}
    return render(request, 'stears/writer_detail.html', context)


@user_passes_test(lambda u: is_a_boss(u), login_url='/stears/noaccess/')
def delete_article(request):
    # Notify everyone that the article has been deleted
    if request.method == 'POST':
        pk = int(request.POST.get('article_id', 0))
        move_to_trash(pk)
    return HttpResponseRedirect(reverse('stears:writers_home'))


@user_passes_test(lambda u: approved_writer(u), login_url='/stears/noaccess/')
def article_detail(request, pk):
    article = mclient.stears.articles.find_one({'article_id': int(pk)})
    if article['type'] == 'writers_article':
        nse_id = article['nse_article_id']
        category = article['category']
    else:
        nse_id = pk
        category = "Tier 1"

    approved_writers = retrieve_values(
        'username', {'state': 'approved'}, mclient.stears.user)
    suggest_form = SuggestForm(my_arg=approved_writers)

    user = request.user
    locked_fields = ['nse_headlines', 'categories']

    if writer_can_edit_article(user, article):
        if article.get('type', '') == 'writers_article':
            writers_article_form = WritersArticleForm(
                headline=article['headline'],
                content=article['content'],
                article_id=int(pk),
                initial={'nse_headlines': nse_id,
                         'categories': category},
                edit=True,
                lock=locked_fields,
            )

        elif article['type'] == 'nse_article':
            writers_article_form = NseArticleForm(
                nse_headlines=nse_id,
            )
    else:
        writers_article_form = {}

    if not article:
        article = mclient.stears.articles.find_one(
            {'article_id': int(pk), 'type': 'nse_article'})
    context = {'article': article, 'suggest_form': suggest_form,
               'writers_article_form': writers_article_form}
    return render(request, 'stears/article_detail.html', context)


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

    return HttpResponseRedirect(reverse('stears:writers_list'))


@user_passes_test(lambda u: is_a_boss(u), login_url='/stears/noaccess/')
def approve_article(request):
    # Notify everyone that a new article has been committed or notify writer
    # that article was rejected
    if request.method == 'POST':
        commit_id = request.POST.get('commit_id', '')
        reject_id = request.POST.get('reject_id', '')
        articles = mclient.stears.articles

        if reject_id:
            # change state to in progress
            article = articles.find_one({"article_id": int(reject_id)})
            article['state'] = 'in_progress'
            articles.save(article)
        elif commit_id:
            migrate_article(int(commit_id))

    return HttpResponseRedirect(reverse('stears:articles_group', args=(), kwargs={'group': 'peers'}))

# Notify writer that an article has been suggested and by whom


@user_passes_test(lambda u: is_a_boss(u), login_url='/stears/noaccess/')
def suggest(request):
    if request.method == 'POST':
        approved_writers = retrieve_values(
            'username', {'state': 'approved'}, mclient.stears.user)
        suggest_form = SuggestForm(request.POST, my_arg=approved_writers)
        if suggest_form.is_valid():
            username = str(suggest_form.cleaned_data.get('user', ''))
            article_id = request.POST['article_id']
            suggest_nse_article(username, article_id)

    return HttpResponseRedirect(reverse('stears:writers_home', args=()))


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

    return HttpResponseRedirect(reverse('stears:writers_home', args=()))


def noaccess(request):
    user = request.user
    if user.is_authenticated():
        return render(request, 'stears/noaccess.html', {})
    login_form = LoginForm()
    context = {'login_form': login_form}
    return render(request, 'stears/login.html', context)


def home(request):
    return render(request, 'stears/home.html', {})
