from ..models import Emailverifiction
import secrets


#! gernate a otp
def gernate_otp(user):
    Emailverifiction.objects.filter(user=user).delete()
    otp= str(secrets.randbelow(900000) + 100000)
    Emailverifiction.objects.create(
        user=user,
        otp=otp
            
        )
    return otp
        

