from utils import mongo_calls


def approved_writer(username):
    if username.is_superuser:
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


def writer_can_edit_article(user, article):
    if user.is_superuser or user.is_staff:
        return True
    if not article.get('writer', ''):
        return True
    if not article.get('visible', True):
        return False
    elif article.get('state', '') == 'submitted':
        return False
    elif user.username == article.get('writer', ''):
        return True
    return False
