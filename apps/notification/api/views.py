# views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ..models import Notification
from .serializer import NotificationSerializer


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class   = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user
        ).exclude(notif_type=Notification.Type.NEW_MESSAGE).select_related("sender", "project")

    @action(detail=False, methods=["get"])
    def unread_count(self, request):
        count = request.user.notifications.filter(
            is_read=False
        ).exclude(notif_type=Notification.Type.NEW_MESSAGE).count()
        return Response({"unread_count": count})
    
    @action(detail=False, methods=["get"])
    def unread_notification(self, request):
        notification = request.user.notifications.filter(
            is_read=False
        ).exclude(notif_type=Notification.Type.NEW_MESSAGE)
        
        page = self.paginate_queryset(notification)
        if page is not None:
            ser = self.get_serializer(page, many=True)
            return self.get_paginated_response(ser.data)
        
        ser = self.get_serializer(notification, many=True)
        return Response({"data": ser.data})

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        notif = self.get_object()
        notif.is_read = True
        notif.save()
        return Response({"detail": "Marked as read."})

    @action(detail=False, methods=["post"])
    def mark_all_read(self, request):
        request.user.notifications.filter(
            is_read=False
        ).update(is_read=True)
        return Response({"detail": "All marked as read."})

    @action(detail=False, methods=["delete"])
    def clear_all(self, request):
        request.user.notifications.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False,methods=['patch'])
    def nofifiction_off(self,request,pk=None):
        user=request.user
        user.notifiction_enable = not user.notifiction_enable
        user.save(update_fields=["notifiction_enable"])
        return Response({
        "notifications_enabled":user.notifiction_enable
         })
       