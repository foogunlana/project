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
    if writer.is_superuser or writer.is_staff:
        return True
    return False


def editor2(username):
    users = mongo_calls('user')
    writer = users.find_one({'username': username})
    if writer['state'] == 'admin':
        return True
    return False


def writer_can_edit_article(username, article):
    state = article['state']
    writer = article.get('writer', '')
    if (state == 'submitted'):
        return editor(username)

    if (state == 'in_review'):
        return False

    if not writer:
        return True

    if not article.get('visible', True):
        return False

    elif (username == writer) or (username in article['writers']['others']):
        return True

    return False


def writer_can_view_article(username, article):
    state = article['state']
    writer = article.get('writer', '')
    others = article.get('writers', '')['others']

    if not writer:
        return True

    elif (state == 'in_progress'):
        return ((writer == username) or (writer in others) or (editor(writer)))

    elif (state == 'in_review'):
        return True

    elif (state == 'submitted'):
        return editor(username)

    return False
