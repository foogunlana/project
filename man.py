print type(None)


from django.shortcuts import render
from stears.forms import LoginForm, UserForm, RequestForm, AssignForm, EditArticleForm
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth import login,logout,authenticate
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from stears.utils import unique, retrieve_values, client as mclient
from stears.permissions import approved_writer, is_a_boss
from bson.objectid import ObjectId

import params



# def year_archive(request, year):
#     a_list = Article.objects.filter(pub_date__year=year)
#     context = {'year': year, 'article_list': a_list}
#     return render(request, 'stears/year_archive.html', context)

# def month_archive(request, year, month):
#     a_list = Article.objects.filter(pub_date__year=year, pub_date__month=month)
#     context = {'year': year,'month':month, 'article_list': a_list}
#     return render(request, 'stears/month_archive.html', context)

# def day_archive(request, year,month,day):
#     a_list = Article.objects.filter(pub_date__year=year, pub_date__month=month, pub_date__day=day)
#     context = {'year': year, 'month':month, 'day':day, 'article_list': a_list}
#     return render(request, 'stears/day_archive.html', context)

# def article_detail(request, pk):
# 	article = Article.objects.filter(pk=pk)
# 	context = {'article':article}
# 	return render(request, 'stears/article_detail.html',context)

def login_view(request):
	username = request.POST.get('username','')
	password = request.POST.get('password','')
	errors = []
	user = authenticate(username=username, password=password)
	if user:
		print 'user found'
		if user.is_active:
			login(request, user)
	        # Redirect to a success page.
			return HttpResponseRedirect(reverse('stears:writers_home'))
		else:
			print 'user inactive'
	    	pass
	    	# disabled account message
	
	if request.method == 'POST':
		print 'invalid login'
		errors.append('Invalid login')

	login_form = LoginForm()
	context = {'login_form':login_form, 'errors':errors}		
	return render(request, 'stears/login.html',context)
        # Return an 'invalid login' error message.

def register(request):
    registered = False

    if request.method == 'POST':
        user_form = UserForm(data=request.POST)

        if user_form.is_valid():	
			user = user_form.save()
			user.set_password(user.password)
			user.save()
			username = user_form.cleaned_data['username']

			if unique(username,'writer'):
				mclient.stears.writers.update({'writer':username},{'writer':username,'state':'request'},True)
				return HttpResponseRedirect(reverse('stears:writers_home'))
			else:
				user_form.errors.append('That username has been taken')

			registered = True
        else:
            print user_form.errors

    else:
        user_form = UserForm()

    context = {'user_form': user_form, 'registered': registered}
    return render(request, 'stears/register.html',context)

@login_required(login_url='/stears/login')
def logout_view(request):
	logout(request)
	login_form = LoginForm()
	context = {'login_form':login_form}
	return render(request, 'stears/login.html',context)

# @permission_required('stears.can_write', login_url='/stears/noaccess/')
@user_passes_test(lambda u: approved_writer(u), login_url='/stears/noaccess/')
def writers_home(request):	
	user = request.user
	edit_article_form = EditArticleForm()
	editable_fields = ['Headline','Content']

	if user.is_authenticated():	
		if user.is_staff:
			return HttpResponseRedirect(reverse('stears:writers_boss',args=()))

		if request.method == 'GET':
			articles = [article for article in mclient.stears.articles.find({'reporter':str(user)})]
	
	context = {'editable_fields':editable_fields,'edit_article_form':edit_article_form,'data':{'article_list':articles}}
	return render(request, 'stears/writers_home.html',context)

@user_passes_test(lambda u: approved_writer(u), login_url='/stears/noaccess/')
def writers_home_test(request,group):	
	user = request.user
	editable_fields = ['Headline','Content']
	visible_fields = ['headline','content','reporter','state']

	if user.is_authenticated():	
		if user.is_staff:
			return HttpResponseRedirect(reverse('stears:writers_boss',args=()))

		if request.method == 'GET':
			if not group:
				pass
			elif group == 'reporter':
				articles = [article for article in mclient.stears.articles.find({'reporter':str(user)})]
			
		
	context = {'editable_fields':editable_fields,'visible_fields':visible_fields, 'Articles':articles, 'username':user}
	return render(request, 'stears/writers_home_test.html',context)


@user_passes_test(lambda u: approved_writer(u), login_url='/stears/noaccess/')
def edit_article(request):
	if request.method == 'POST':
		print 'bla'
		edit_article_form = EditArticleForm(request.POST)
		print edit_article_form

		if edit_article_form.is_valid():
			mongo_id = request.POST['article_id']
			article = mclient.stears.articles.find_one({'_id':ObjectId(mongo_id)})
			article['Headline'] = edit_article_form.cleaned_data['headline']
			article['Content'] = edit_article_form.cleaned_data['content']
			article['state'] = 'commited'
			mclient.stears.articles.save(article)

	return HttpResponseRedirect(reverse('stears:writers_home',args=()))

@user_passes_test(lambda u: is_a_boss(u), login_url='/stears/noaccess/')
def approve_writer(request):
	if request.method =='POST':

		writer_requests = retrieve_values('writer',{'state':'request'},mclient.stears.writers)

		form = RequestForm(request.POST,my_arg=writer_requests)
		if form.is_valid():
			approved_users = form.cleaned_data['users']
			for username in approved_users:
				# user = User.objects.get(username=username)
				# user.groups.add('can_write')
				mclient.stears.writers.update({'writer':username},{'writer':username,'state':'approved'})
			
			return HttpResponseRedirect(reverse('stears:writers_boss',args=()))

	return HttpResponseRedirect(reverse('stears:writers_boss',args=()))

@user_passes_test(lambda u: is_a_boss(u), login_url='/stears/noaccess/')
def assign(request):
	if request.method =='POST':

		approved_writers = retrieve_values('writer',{'state':'approved'},mclient.stears.writers)

		form = AssignForm(request.POST,my_arg=approved_writers)
		if form.is_valid():
			assigned_user = form.cleaned_data.get('user','')

			mongo_id = request.POST['article_id']
			article = mclient.stears.articles.find_one({'_id':ObjectId(mongo_id)})
			article['reporter'] = assigned_user
			article['state'] = 'assigned'
			mclient.stears.articles.save(article)

				# user = User.objects.get(username=username)
				# user.groups.add('can_write')

			# mclient.stears.writers.update({'writer':username},{'writer':username,'state':'approved'})
			return HttpResponseRedirect(reverse('stears:writers_boss',args=()))

	return HttpResponseRedirect(reverse('stears:writers_boss',args=()))

@user_passes_test(lambda u: is_a_boss(u), login_url='/stears/noaccess/')
def approve_article(request):
	if request.method =='POST':
		mongo_id = request.POST.get('article_id','')
		if mongo_id:
			print mongo_id
			article = mclient.stears.articles.find_one({'_id':ObjectId(mongo_id)})
			article['state'] = 'approved'
			mclient.stears.articles.save(article)

			return HttpResponseRedirect(reverse('stears:writers_boss',args=()))
		print "mongo_id was null"

	return HttpResponseRedirect(reverse('stears:writers_boss',args=()))


@user_passes_test(lambda u: is_a_boss(u), login_url='/stears/noaccess/')
def writers_boss(request):
	pre_article_list = {}
	assigned_article_list = {}
	approved_article_list = {}
	edit_article_form = EditArticleForm()

	if request.method == 'GET':
		pre_article_list = [article for article in mclient.stears.articles.find({'state':'pre_article'})]
		assigned_article_list = [article for article in mclient.stears.articles.find({'state':'assigned'})]
		commited_article_list = [article for article in mclient.stears.articles.find({'state':'commited'})]
		approved_article_list = [article for article in mclient.stears.articles.find({'state':'approved'})]

	writer_requests = retrieve_values('writer',{'state':'request'},mclient.stears.writers)
	approved_writers = retrieve_values('writer',{'state':'approved'},mclient.stears.writers)
	
	request_form = RequestForm(my_arg=writer_requests)
	assign_form = AssignForm(my_arg=approved_writers)

	context = {'request_form':request_form, 'assign_form':assign_form,'edit_article_form':edit_article_form,
	'data':{'pre_article_list':pre_article_list,'assigned_article_list':assigned_article_list,'commited_article_list':commited_article_list,
	'approved_article_list':approved_article_list}, 'writer_requests':writer_requests, 'approved_writers':approved_writers}

	return render(request, 'stears/writers_boss.html', context )

@user_passes_test(lambda u: is_a_boss(u), login_url='/stears/noaccess/')
def writers_boss_test(request):
	visible_fields = params.writers_page_fields
	article_list = []

	if request.method == 'GET':
		article_list = [article for article in mclient.stears.articles.find()]

	context = {'article_list':article_list, 'visible_fields': visible_fields}

	return render(request, 'stears/writers_boss_test.html', context )

def noaccess(request):
	user = request.user
	if user.is_authenticated():
		return render(request, 'stears/noaccess.html',{})
	login_form = LoginForm()
	context = {'login_form':login_form}
	return render(request, 'stears/login.html',context)


def details(request):
	data = request.META
	return render(request, 'stears/details.html', {'data':data})

def home(request):
	return render(request, 'stears/home.html', {})



