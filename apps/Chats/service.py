from .models import GroupMember ,ChatGroup




def join_in_project_groupe(project,user,request):
    
    try:
        chat_group = ChatGroup.objects.get(project=project)
        if chat_group.project.owner == request.user:
            GroupMember.objects.get_or_create(
                chat_group=chat_group,
                user=user,
                defaults={'role': GroupMember.ChatRole.MEMBER}
            )
            
    except ChatGroup.DoesNotExist:
        pass
        
def remove_in_project_groupe(project,user,request=None): 
    try:
        chat_group = ChatGroup.objects.get(project=project)
        GroupMember.objects.filter(
            chat_group=chat_group,
            user=user
        ).delete()
            
    except ChatGroup.DoesNotExist:
        pass
    
    