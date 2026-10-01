from rest_framework.pagination import CursorPagination

class FeedPegination(CursorPagination):
    page_size=20
    ordering='created_at'
    
    
    
    
    
class HomeFeedPegination(CursorPagination):
    page_size=10
    ordering='created_at'
    