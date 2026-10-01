from rest_framework.throttling import UserRateThrottle,AnonRateThrottle ,ScopedRateThrottle




    #! project
class ProjectCreatethrottle(UserRateThrottle):
    scope='Project_create'
 
class ProjectUpdatethrottle(UserRateThrottle):
    scope='Project_update'   

class ProjectDeletethrottle(UserRateThrottle):
    scope='Project_delete'   
    
#! appliction    
class ApplictionCreatethrottle(UserRateThrottle):
    scope='appliction_create'
    
class ApplictionAccpectthrottle(UserRateThrottle):
    scope='appliction_accpect'
    
    
class ApplictionRejectthrottle(UserRateThrottle):
    scope='appliction_reject'
    
    
    #! role
class RoleCreatethrottle(UserRateThrottle):
    scope='role_create'
    
    
class RoleDeletethrottle(UserRateThrottle):
    scope='role_delete'

class RoleUpdatethrottle(UserRateThrottle):
    scope='role_update'

#! for post feathures
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
    
class RemoveMemberThrottle(UserRateThrottle):
    scope="remove_owner"
    
    
    
#TODO chatGroupe throttle 




# feedBack Throttle

class FeedbackThrottle(UserRateThrottle):
    scope="feedback"
    