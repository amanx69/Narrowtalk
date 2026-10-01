from rest_framework.pagination import PageNumberPagination


class ChatPagination(PageNumberPagination):
    page_size = 50
