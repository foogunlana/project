from django.shortcuts import render
from stears.forms import LoginForm, ArticleImageForm, AddWritersForm, \
    RemoveWritersForm, RegisterForm, KeyWordsForm, ChoiceForm, \
    ForgotPasswordForm, CommentForm, SuggestForm, WritersArticleForm, \
    NseArticleForm, ChangePasswordForm, ArticleReviewForm, EditWriterForm, \
    AllocationForm, AddPhotoForm, NewQuoteForm, ReportForm, DailyColumnForm, \
    ColumnForm, EconomicDataForm

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, logout
from mongoengine.django.auth import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from stears.utils import article_key_words, revive_from_trash, add_writers,\
    remove_writers, make_username, migrate_article, mongo_calls, \
    make_comment, forgot_password_email, save_writers_article, \
    accept_to_write, request_json, make_url, move_to_trash, \
    suggest_nse_article, update_writers_article, edit_user, \
    make_writer_id, make_writers_article, submit_writers_article, \
    new_member, \
    make_new_quote, edit_writer_registration_details

from news.utils import put_article_on_page

from stears.permissions import approved_writer, is_a_boss, \
    writer_can_edit_article

from stears.models import ArticleImageModel, ReportModel
from mongoengine.queryset import DoesNotExist


import datetime
import params
import json



@user_passes_test(lambda u: approved_writer(u), login_url='/weal/noaccess/')
def upload_photo(request):
    if request.method == 'POST':
        form = ArticleImageForm(request.POST, request.FILES)
        if form.is_valid():
            article_image = ArticleImageModel(
                docfile=request.FILES['article_image']
            )
            article_image.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            try:
                photos = ArticleImageModel.objects.all()
            except Exception as e:
                photos = []
                print e
                print "*********** COULDN'T LOAD PICTURES *************"
            return render(request, 'stears/photos.html',
                          {'form': form, 'photos': photos})
    else:
        form = ArticleImageForm()
    try:
        photos = ArticleImageModel.objects.all()
    except Exception as e:
        photos = []
        print e
        print "*********** COULDN'T LOAD PICTURES *************"
    return render(request, 'stears/photos.html',
                  {'form': form, 'photos': photos})


@user_passes_test(lambda u: approved_writer(u), login_url='/weal/noaccess/')
def add_photo(request, pk):
    if request.method == 'POST':
        pk = int(pk)
        add_photo_form = AddPhotoForm(request.POST)
        if add_photo_form.is_valid():
            photo = add_photo_form.cleaned_data['photo_link']
            articles = mongo_calls('articles')
            articles.update({'article_id': pk},
                            {'$set': {'photo': photo}},
                            False, False)
        else:
            print 'not Ok'

    if request.method == 'GET':
        add_photo_form = AddPhotoForm()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@user_passes_test(lambda u: approved_writer(u), login_url='/weal/noaccess/')
def research(request):
    choices = [key for key in params.glo_trybe_data]
    form = ChoiceForm(choices=choices)
    writers_article_form = WritersArticleForm()
    return render(request, 'stears/research.html',
                    {'form': form,
                    'writers_article_form': writers_article_form})


@user_passes_test(lambda u: approved_writer(u), login_url='/weal/noaccess/')
def gts(request):
    site = {}
    choices = [key for key in params.glo_trybe_data]
    if request.method == 'POST':
        form = ChoiceForm(request.POST, choices=choices)

        if form.is_valid():
            choice = form.cleaned_data['choice']
            URL = make_url(params.glo_trybe_data[choice], False)
            j_array = request_json(URL)
            site = json.dumps(j_array)

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
                        return HttpResponseRedirect(reverse('weal:login'))
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
    errors = []

    if request.method == 'POST':
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        next = request.POST.get('next', '')
        try:
            user = User.objects.get(email=email)

            if user.check_password(password):
                user.backend = params.MONGOENGINE_BACKEND
                if user.is_active:
                    login(request, user)
                if user:
                    request.session.set_expiry(
                        params.SESSION_AGE)  
                    if next:
                        return HttpResponseRedirect(next)
                    else:
                        return HttpResponseRedirect(
                            reverse('weal:articles_group',
                              args=(), kwargs={'group': 'peers'}))
                else:
                    errors.append(
                        'Oops! something went wrong. please refresh')
            else:
                errors.append('Invalid login')
        except DoesNotExist:
            errors.append('Invalid login')
        except Exception as e:
            return HttpResponse(str(e))

    login_form = LoginForm()
    context = {'login_form': login_form, 'errors': errors}
    return render(request, 'stears/login.html', context)


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
            member.set_password(
                str(register_form.cleaned_data['password']))
            member.save()
            new_member(register_form)
            make_writer_id(member.username)

            registered = True

            return HttpResponseRedirect(reverse('weal:writers_write'))

        else:
            errors.append(register_form.errors)
            return render(request, 'stears/register.html', {
                'register_form': register_form, 'errors': errors})

    context = {'register_form': register_form, 'registered': registered}
    return render(request, 'stears/register.html', context)


@login_required(login_url='/weal/login')
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('weal:writers_write'))


@user_passes_test(lambda u: approved_writer(u), login_url='/weal/noaccess/')
def writers_home_test(request, group):
    articles = []
    article_collection = mongo_calls('articles')
    nostates = False

    writers_article_form = WritersArticleForm()

    if request.method == 'GET':
        if group == 'NSE':
            articles = list(article_collection.find(
                {'type': 'nse_article'}))
        else:
            articles = list(article_collection.find({
                '$query': {'type': 'writers_article'},
                '$orderby': {'time': -1}},
                params.article_button_items).limit(50))

    context = {"writers_article_form": writers_article_form,
               'articles': articles, 'nostates': nostates}

    return render(request, 'stears/writers_home_test.html', context)


@user_passes_test(lambda u: approved_writer(u), login_url='/weal/noaccess/')
def writers_list(request):
    writers = []
    users = mongo_calls('user')
    if request.method == 'GET':
        writers = list(users.find(
            {'$query': {}, '$orderby': {'state': 1}}))

        writers_article_form = WritersArticleForm()

    context = {
        'writers': writers, 'writers_article_form': writers_article_form}
    return render(request, 'stears/writers_list.html', context)


@user_passes_test(lambda u: approved_writer(u), login_url='/weal/noaccess/')
def writers_write(request):
    context = {}
    messages = []
    users = mongo_calls('user')
    article_collection = mongo_calls('articles')
    daily_column_form = None

    if request.method == 'GET':
        username = str(request.user)
        writer = users.find_one(
            {'username': username},
            {'suggested_articles': 1, 'reviews': 1, '_id': 0, 'role': 1})

        if writer['role'] in ['Editor', 'Admin', 'Columnist']:
            daily_column_form = DailyColumnForm()

        suggested_articles = writer.get('suggested_articles', [])
        suggestions = list(article_collection.find(
            {'article_id': {'$in': suggested_articles}},
            params.article_button_items))

        articles = list(article_collection.find(
                {"$query": {'writer': username}, "$orderby": {"time": -1}},
                params.article_button_items))

        reviews = list(article_collection.find({
                "$query": {'article_id': {'$in': writer['reviews']},
                 'state':'in_review'},
                "$orderby": {"time": -1}}, params.article_button_items))

        writers_article_form = WritersArticleForm()

        context = {"writers_article_form": writers_article_form, 'articles':
                   articles, 'suggestions': suggestions, 'messages': messages,
                   'reviews': reviews, 'daily_column_form': daily_column_form}

    return render(request, 'stears/writers_write.html', context)


@user_passes_test(lambda u: approved_writer(u), login_url='/weal/noaccess/')
def writer_detail(request, name):
    users = mongo_calls('user')
    article_collection = mongo_calls('articles')
    writer = users.find_one({'username': name})
    context = {}

    username = str(request.user)
    edit_writer_form = None
    if username == name:
        writer_data = {
            'username': writer['username'],
            'first_name': writer['first_name'],
            'last_name': writer['last_name'],
            'dob': writer.get('dob', datetime.datetime.now()),
            'study': writer.get('study', 'None'),
            'interests': writer.get('interests', 'None'),
            'role': writer.get('role', 'None'),
            'occupation': writer.get('occupation', 'None'),
            'sex': writer.get('sex', 'None'),
            'email': writer['email'],
            'new_email': writer['email']
        }
        edit_writer_form = EditWriterForm(writer_data)

    if request.method == 'GET':
        writers_article_form = WritersArticleForm()

        articles = list(article_collection.find({
                "$query": {'writer': name},
                "$orderby": {"time": -1}}, params.article_button_items))

        context = {'writer': writer, 'articles': articles,
        'edit_writer_form': edit_writer_form,'writers_article_form': writers_article_form}
    return render(request, 'stears/writer_detail.html', context)


@user_passes_test(lambda u: approved_writer(u), login_url='/weal/noaccess/')
def daily_column(request):
    writers = mongo_calls('user')
    writer = str(request.user)
    if request.method == 'POST':
        author = str(request.user)
        daily_column = DailyColumnForm(request.POST)
        if daily_column.is_valid():
            title = daily_column.cleaned_data['title']
            if title:
                writers.update({'username': writer},
                               {'$set': {'column': title}})
        else:
            print 'not valid'
    return HttpResponseRedirect(reverse('weal:writers_write'))


@user_passes_test(lambda u: is_a_boss(u), login_url='/weal/noaccess/')
def select_column(request):
    if request.method == 'POST':
        column_form = ColumnForm(request.POST)
        if column_form.is_valid():
            day = column_form.cleaned_data['day']
            writer = column_form.cleaned_data['author']
            onsite = mongo_calls('onsite')
            onsite.update({'page': 'home'},
                          {'$set': {'daily_column.{}'.format(day): writer}})
        else:
            HttpResponse(column_form.errors)
    return HttpResponse('Ok')

@user_passes_test(lambda u: approved_writer(u), login_url='/weal/noaccess/')
def edit_writer_detail(request):
    username = str(request.POST['username'])
    if request.method == 'POST':
        edit_writer_form = EditWriterForm(request.POST)
        if edit_writer_form.is_valid():
            if username != str(request.user):
                return HttpResponseRedirect(reverse(
                    'weal:writer_detail', args=(), kwargs={'name': username}))
            edit_writer_registration_details(edit_writer_form)
        else:
            print edit_writer_form.errors

    return HttpResponseRedirect(reverse(
        'weal:writer_detail', args=(), kwargs={'name': username}))


@user_passes_test(lambda u: is_a_boss(u), login_url='/weal/noaccess/')
def delete_article(request):
    if request.method == 'POST':
        pk = request.POST.get('article_id', None)
        if not pk:
            raise Exception('Nothing to delete')
        pk = int(pk)
        move_to_trash(pk)
    return HttpResponseRedirect(reverse('weal:writers_home'))


@user_passes_test(lambda u: approved_writer(u), login_url='/weal/noaccess/')
def bin(request):
    username = str(request.user)
    bin = mongo_calls('bin')
    articles = list(bin.find({
        '$query': {'type': 'writers_article', 'writer': username},
        '$orderby': {'time': -1}},
        dict(params.article_button_items, **{'binned': 1})))

    context = {'articles': articles}
    return render(request, 'stears/bin.html', context)


@user_passes_test(lambda u: approved_writer(u), login_url='/weal/noaccess/')
def revive_article(request):
    if request.method == 'POST':
        pk = request.POST.get('article_id', None)
        if not pk:
            return HttpResponseRedirect(reverse('weal:noaccess'))
        pk = int(pk)
        revive_from_trash(pk)

    return HttpResponseRedirect(reverse('weal:bin'))


@user_passes_test(lambda u: approved_writer(u), login_url='/weal/noaccess/')
def article_detail(request, **kwargs):
    user = request.user
    article_collection = mongo_calls('articles')
    users = mongo_calls('users')

    pk = int(kwargs.pop('pk'))
    comment_form = CommentForm()
    key_words_form = KeyWordsForm()
    add_photo_form = AddPhotoForm()

    article = article_collection.find_one({'article_id': pk})

    if not article:
        return HttpResponseRedirect(reverse('weal:noaccess'))

    if article['type'] == 'writers_article':
        nse_id = article['nse_article_id']
        category = article['category']
    else:
        nse_id = pk
        category = "stearsOther"

    approved_writers = users.find(
        {'state': 'approved'}).distinct('username')
    suggest_form = SuggestForm(my_arg=approved_writers)

    locked_fields = ['nse_headlines']
    # s_cat = lambda x: 'stears' + x.replace(' ', '_')
    print category
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

    context = {'article': article, 'suggest_form': suggest_form,
         'remove_writers_form': remove_writers_form,
         'key_words_form': key_words_form, 'add_photo_form': add_photo_form,
         'writers_article_form': writers_article_form,
         'add_writers_form': add_writers_form, 'comment_form': comment_form}

    return render(request, 'stears/article_detail.html', context)


@user_passes_test(lambda u: approved_writer(u), login_url='/weal/noaccess/')
def comment(request, pk):
    article_id = int(pk)
    if request.method == 'POST':
        comment_form = CommentForm(
            request.POST,
        )
        if comment_form.is_valid():
            make_comment(
                str(request.user), int(article_id),
                comment_form.cleaned_data['comment'])
            return HttpResponse('reload')
        else:
            return HttpResponse("Sorry, comment could not be saved! \
                Please alert the aministrator")
    return HttpResponse('reload')


@user_passes_test(lambda u: approved_writer(u), login_url='/weal/noaccess/')
def add_tag(request, pk):
    pk = int(pk)
    if request.method == 'POST':
        key_words_form = KeyWordsForm(
            request.POST
        )
        if key_words_form.is_valid():
            article_key_words(
                pk,
                key_words_form.cleaned_data['tags'],
                other=key_words_form.cleaned_data['other'])
        else:
            print "Invalid"
    return HttpResponseRedirect(reverse(
        'weal:article_detail', args=(), kwargs={'pk': pk}))


@user_passes_test(lambda u: is_a_boss(u), login_url='/weal/noaccess/')
def approve_writer(request):
    if request.method == 'POST':
        username_approve = request.POST.get('approve', '')
        username_revoke = request.POST.get('revoke', '')

        if username_approve:
            username = username_approve
            edit_user(username_approve, 'state', 'approved')
            writers = mongo_calls('user')
            writer = writers.find_one({'username': username_approve})
            if writer['role'].lower() == 'editor':
                writers.update(
                    {'username': username_approve},
                    {'$set': {'state': 'admin', 'is_staff': True}},
                    False,
                    False)

        if username_revoke:
            username = username_revoke
            edit_user(username_revoke, 'state', 'request')

    return HttpResponseRedirect(reverse('weal:writer_detail', args=(), kwargs={'name': username}))


@user_passes_test(lambda u: is_a_boss(u), login_url='/weal/noaccess/')
def approve_article(request):
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

    return HttpResponseRedirect(reverse('weal:submissions'))

# Notify writer that an article has been suggested and by whom


@user_passes_test(lambda u: is_a_boss(u), login_url='/weal/noaccess/')
def suggest(request):
    users = mongo_calls('user')
    article_id = request.POST['article_id']
    if request.method == 'POST':
        approved_writers = users.find(
            {'state': 'approved'}).distinct('username')
        suggest_form = SuggestForm(request.POST, my_arg=approved_writers)
        if suggest_form.is_valid():
            username = str(suggest_form.cleaned_data.get('user', ''))
            suggest_nse_article(username, article_id)
    else:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return HttpResponseRedirect(reverse(
        'weal:article_detail', args=(), kwargs={'pk': article_id}))


@user_passes_test(lambda u: is_a_boss(u), login_url='/weal/noaccess/')
def accept_article_category(request):
    accept_id = request.POST.get('accept_id', '')
    not_accept_id = request.POST.get('not_accept_id', '')

    if accept_id:
        accept_to_write(int(accept_id))
        article_id = accept_id
    elif not_accept_id:
        move_to_trash(int(not_accept_id))
        article_id = not_accept_id

    return HttpResponseRedirect(reverse(
        'weal:article_detail', args=(), kwargs={'pk': article_id}))


@user_passes_test(lambda u: approved_writer(u), login_url='/weal/noaccess/')
def review_article(request, pk):
    username = str(request.user)
    pk = int(pk)
    articles = mongo_calls('articles')
    article = articles.find_one({'article_id': pk})
    if (not article.get('reviewer', '') == username) or article['state'] != 'in_review':
        return HttpResponseRedirect(reverse('weal:noaccess'))
    if request.method == "POST":
        article_review_form = ArticleReviewForm(request.POST)
        if article_review_form.is_valid():
            # submit_writers_article(pk, article_review_form.cleaned_data)
            pass
        else:
            print "Invalid"
        return HttpResponseRedirect(reverse('weal:writers_write'))
    article_review_form = ArticleReviewForm()
    return render(request, 'stears/review_article.html',
        {'article': article, 'article_review_form': article_review_form})


@user_passes_test(lambda u: approved_writer(u), login_url='/weal/noaccess/')
def add_writer_to_article(request):
    article_id = int(request.POST['article_id'])
    if request.method == "POST":
        article_id = request.POST['article_id']
        if not article_id:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        add_writers_form = AddWritersForm(
            request.POST, article_id=article_id)
        if add_writers_form.is_valid():
            usernames = add_writers_form.cleaned_data['writers']
            add_writers(article_id, usernames)
    return HttpResponseRedirect(reverse(
        'weal:article_detail', args=(), kwargs={'pk': article_id}))


@user_passes_test(lambda u: approved_writer(u), login_url='/weal/noaccess/')
def remove_writer_from_article(request):
    article_id = int(request.POST['article_id'])
    if request.method == "POST":
        remove_writers_form = RemoveWritersForm(
            request.POST, article_id=request.POST['article_id'])
        if remove_writers_form.is_valid():
            usernames = remove_writers_form.cleaned_data['writers']
            remove_writers(article_id, usernames)
    return HttpResponseRedirect(reverse(
        'weal:article_detail', args=(), kwargs={'pk': article_id}))


@user_passes_test(lambda u: approved_writer(u), login_url='/weal/noaccess/')
def pipeline(request):
    if request.method == 'GET':
        migrations = mongo_calls('migrations')
        articles = list(migrations.find(
            {'$query': {}, '$orderby': {'time': -1}}, 
            params.article_button_items))

    context = {'articles': articles, 'nostates': True}
    return render(request, 'stears/pipeline.html', context)


@user_passes_test(lambda u: approved_writer(u), login_url='/weal/noaccess/')
def preview_article(request, pk):
    if request.method == 'GET':
        pk = int(pk)
        migrations = mongo_calls('migrations')
        article = migrations.find_one(
            {'article_id': pk},
            {'content': 1, '_id': 0, 'headline': 1, 'writers': 1})

    context = {'article': article, 'writers': article['writers']}
    return render(request, 'news/article.html', context)


@user_passes_test(lambda u: is_a_boss(u), login_url='/weal/noaccess/')
def allocate_articles(request, pk):
    if request.method == 'GET':
        pk = int(pk)

    context = {'pk': pk}
    return render(request, 'stears/allocator.html', context)


@user_passes_test(lambda u: is_a_boss(u), login_url='/weal/noaccess/')
def allocate_article(request):
    multiples = ['features', 'tertiaries']
    if request.method == 'POST':
        allocation_form = AllocationForm(request.POST)
        print request.POST
        if allocation_form.is_valid():
            section = allocation_form.cleaned_data['section']
            article_id = int(allocation_form.cleaned_data['article_id'])
            page = allocation_form.cleaned_data['page']
            sector = allocation_form.cleaned_data.get('sector', None)
            number = allocation_form.cleaned_data.get('number', None)
            try:
                put_article_on_page(page=page, section=section,
                         article_id=article_id, sector=sector, number=number)
            except Exception as e:
                print e, 'error'
        else:
            print 'not valid'
            return HttpResponse(allocation_form.errors)
    return HttpResponse('reload')


@user_passes_test(lambda u: is_a_boss(u), login_url='/weal/noaccess/')
def allocate_report(request):
    if request.method == 'POST':
        report_form = ReportForm(request.POST, request.FILES)
        if report_form.is_valid():
            pdf = report_form.cleaned_data['pdf']
            if pdf:
                author = report_form.cleaned_data['author']
                report = ReportModel(**report_form.cleaned_data)
                report.save()
                week_ending = str(report_form.cleaned_data['week_ending'])
                d = datetime.datetime.strptime(week_ending, "%Y-%m-%d")
                string = "Week ending {}".format(d.strftime('%B %-d'), )
                onsite = mongo_calls('onsite')
                onsite.update({'page': 'home'},
                              {'$set': {'report': {
                                        'date': string,
                                        'author': author}}})
            else:
                return HttpResponse('No pdf')
        else:
            return HttpResponse(json.dumps(report_form.errors))
    return HttpResponse('reload')


@user_passes_test(lambda u: is_a_boss(u), login_url='/weal/noaccess/')
def economic_data(request):
    if request.method == 'POST':
        economic_data_form = EconomicDataForm(request.POST)
        if economic_data_form.is_valid():
            data = economic_data_form.cleaned_data
            onsite = mongo_calls('onsite')
            onsite.update({'page': 'b_e'},
                          {'$set': {'economic_data': data}}, multi=True)
        else:
            return HttpResponseRedirect(reverse('weal:allocator'))
    return HttpResponseRedirect(reverse('weal:allocator'))


@user_passes_test(lambda u: is_a_boss(u), login_url='/weal/noaccess/')
def new_quote(request):
    onsite = mongo_calls('onsite')
    if request.method == 'POST':
        new_quote_form = NewQuoteForm(request.POST)
        if new_quote_form.is_valid():
            quote = new_quote_form.cleaned_data['quote']
            author = new_quote_form.cleaned_data['author']
            make_new_quote(body=quote, author=author)
        else:
            print new_quote_form.errors
            return HttpResponse(new_quote_form.errors)
    return HttpResponse('reload')

@user_passes_test(lambda u: is_a_boss(u), login_url='/weal/noaccess/')
def allocator(request):
    onsite = mongo_calls('onsite')
    # pipeline = mongo_calls('migrations')
    pipeline = mongo_calls('articles')
    writers = mongo_calls('user')
    pages = list(onsite.find({'active': True}))
    report_form = ReportForm()
    economic_data_form = EconomicDataForm()

    articles = list(pipeline.find({
                '$query': {'type': 'writers_article', 'state':'submitted'},
                '$orderby': {'time': -1}},
                {'headline': 1, '_id': 0, 'article_id': 1, 'category':1}))
    context = {}
    for item in pages:
        item.pop('_id')
        item.pop('active')
        page = item.pop('page')
        context[page] = item

    cats = params.article_categories.values()
    groups = {}
    for cat in cats: groups[cat] = []
    for article in articles:
        groups[article['category']] = groups.get(
                        article['category'], []) + [article]
    context['cats'] = groups
    context['quote_form'] = NewQuoteForm()
    context['sectors'] = params.sectors.values()
    context['report_form'] = report_form
    context['economic_data_form'] = economic_data_form
    context['columns'] = params.columns  #Needs to reflect actual columns ...
    context['writers_columns'] = {
            writer['username']: writer['column'] for writer in writers.find(
            {}, {'column': 1, 'username': 1}) if writer.get('column')}

    return render(request, 'stears/allocator2.html', context)


@user_passes_test(lambda u: is_a_boss(u), login_url='/weal/noaccess/')
def submissions(request):
    if request.method == 'GET':
        articles = mongo_calls('articles')
        submitted_articles = list(articles.find(
            {'$query': {'state': 'submitted'}, '$orderby': {'time': -1}}))
    context = {'articles': submitted_articles, 'nostates': True}
    return render(request, 'stears/submissions.html', context)


@user_passes_test(lambda u: approved_writer(u), login_url='/weal/noaccess/')
def remove_tag(request):
    if request.method == 'POST':
        code = request.POST.get('data', None)
        if not code:
            print "Error!"
            return HttpResponse('No tag specified')

        id_and_tag = code.split(',')
        pk, tag = int(id_and_tag[0]), str(id_and_tag[1])

        articles = mongo_calls('articles')
        articles.update(
            {'article_id': pk},
            {'$pull': {'keywords': tag}},
            False,
            False
        )

    return HttpResponse('%s was deleted!' % (tag))


@user_passes_test(lambda u: approved_writer(u), login_url='/weal/noaccess/')
def submit_article(request):
    writer = str(request.user)

    if request.method == 'POST':
        form = WritersArticleForm(
            request.POST,
        )
        if form.is_valid():
            article_id = int(form.cleaned_data.get('article_id', 0))
            sor = request.POST.get('save_or_review', '')
            if article_id:
                update_writers_article(writer, form)
            else:
                new_article = make_writers_article(form, writer)
                article_id = save_writers_article(new_article)
                if sor == 'save':
                    return HttpResponse("reload")
            if sor == 'review':
                submit_writers_article(article_id)
                return HttpResponse("reload")
            return HttpResponse(request.POST['content'])
        else:
            return HttpResponse("Please fill required fields")
    return HttpResponse("Error")


def noaccess(request):
    user = request.user
    next = request.GET.get('next', '')
    if user.is_authenticated():
        return render(request, 'stears/noaccess.html', {})
    login_form = LoginForm()
    context = {'login_form': login_form, 'next': next}
    return render(request, 'stears/login.html', context)
