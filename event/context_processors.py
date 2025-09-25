from .models import Notification

def unread_notifications_count(request):
    """
    A context processor to add the unread notification count to the context of every template.
    """
    if request.user.is_authenticated:
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return {'unread_count': count}
    return {}