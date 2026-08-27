import random
#! gernate random string for room uniqe id


def gernate_uniqe_number():
    from .models import Room  

    while True:
     
        code = str(random.randint(1000000000, 9999999999))
        if not Room.objects.filter(uniqe_id=code).exists():
            return code
    
