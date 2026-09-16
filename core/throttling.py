from rest_framework.throttling import UserRateThrottle,AnonRateThrottle ,ScopedRateThrottle




    
class PostCreatethrottle(UserRateThrottle):
    scope='post_create'
 
class PostUpdatethrottle(UserRateThrottle):
    scope='post_update'   

class PostDeletethrottle(UserRateThrottle):
    scope='post_delete'   
    
    
class ApplictionCreatethrottle(UserRateThrottle):
    scope='appliction_create'
    
class ApplictionAccpectthrottle(UserRateThrottle):
    scope='appliction_accpect'
    
    
class ApplictionRejectthrottle(UserRateThrottle):
    scope='appliction_reject'
    
    
    
class RoleCreatethrottle(UserRateThrottle):
    scope='role_create'
    
    
class RoleDeletethrottle(UserRateThrottle):
    scope='role_delete'

class RoleUpdatethrottle(UserRateThrottle):
    scope='role_update'


class commentCreatethrottle(UserRateThrottle):
    scope='comment_create'
    
class commentDeletethrottle(UserRateThrottle):
    scope='comment_delete'
class ProjectSaveThrottle(UserRateThrottle):
    scope='project_save'
    
    
class ProfileUpdateThrottle(UserRateThrottle):
    scope='profile_update'
    
class ProfileLikeThrottle(UserRateThrottle):
    scope='profile_like'