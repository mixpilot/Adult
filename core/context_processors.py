"""Template context processors."""
from connections.models import Connection


def connection_notifications(request):
    """Add pending connection requests count for navbar (escort sees when someone wants to connect)."""
    if request.user.is_authenticated:
        pending_count = Connection.objects.filter(
            to_user=request.user,
            status='pending'
        ).count()
        return {'pending_connection_requests_count': pending_count}
    return {'pending_connection_requests_count': 0}
