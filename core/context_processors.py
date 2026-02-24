def notifications_ctx(request):
    if request.user.is_authenticated:
        unread_notifs = request.user.notifications.filter(is_read=False).count()
    else:
        unread_notifs = 0
    return {'unread_notifs': unread_notifs}
