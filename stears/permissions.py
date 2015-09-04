from utils import mongo_calls
from mongoengine.django.auth import User


def approved_writer(username):
    if username.is_superuser or username.is_staff:
        return True

    users = mongo_calls('user')
    writer = users.find_one({'username': str(username)})
    if writer:
        if writer.get('state', "") == 'approved':
            return True
    return False


def is_a_boss(username):
    if username.is_superuser or username.is_staff:
        return True
    return False


def editor(username):
    writer = User.objects.get(username=str(username))
    if not writer:
        return False
    if writer.is_superuser or writer.is_staff:
        return True
    return False

#Optimisation needed! Checked for each article button. Extremely inefficient


def editor2(username):
    users = mongo_calls('user')
    writer = users.find_one({'username': str(username)})
    if not writer:
        return False
    if writer['state'] == 'admin':
        return True
    return False


def get_article_perms(username, article):
    perms = {}
    is_editor = editor2(username)
    can_edit = writer_can_edit_article(username, article)
    is_writer = (username == article['writer'])

    perms['edit'] = can_edit
    perms['editor'] = is_editor
    perms['tag'] = can_edit
    perms['editor_or_writer'] = (is_editor or is_writer)
    perms['add_writer'] = is_writer
    perms['delete'] = is_editor
    perms['approve'] = is_editor and (article['state'] == 'submitted')
    perms['review'] = (
        article['state'] == 'in_review') and (article['reviewer'] == username)
    perms['view_review'] = is_editor

    return perms


def writer_can_edit_article(username, article):
    state = article['state']
    writer = article.get('writer', '')

    if (state == 'submitted') or (state == 'in_review'):
        return editor(username)

    if not writer:
        return True

    if not article.get('visible', True):
        return False

    elif (username == writer) or (username in article['writers']['others']):
        return True

    return False
