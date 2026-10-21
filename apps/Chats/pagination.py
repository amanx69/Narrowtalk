from rest_framework.pagination import PageNumberPagination ,CursorPagination


class ChatPagination(PageNumberPagination):
    page_size = 10
