from rest_framework.pagination import CursorPagination ,PageNumberPagination

class FeedPegination(CursorPagination):
    page_size=20
    ordering='-created_at'
    
    
    
    
    
class HomeFeedPegination(CursorPagination):
    page_size=10
    ordering='-created_at'
    

class UserSearchPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50