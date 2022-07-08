

def roll_list_access(user):
    groups = user.groups.all().values_list('name', flat=True)
    if 'Superintendent' in groups or 'Co_ordinator' in groups:
        return True
    return  False

def subject_access(user):
    groups = user.groups.all().values_list('name', flat=True)
    if 'Superintendent' in groups or 'Co_ordinator' in groups:
        return True
    return False

def registration_access(user):
    groups = user.groups.all().values_list('name', flat=True)
    if 'Superintendent' in groups or 'Co_ordinator' in groups:
        return True
    return False 

def grades_finalize_access(user):
    groups = user.groups.all().values_list('name', flat=True)
    if 'Superintendent' in groups or 'HOD' in groups:
        return True
    return False 

def grades_threshold_access(user):
    groups = user.groups.all().values_list('name', flat=True)
    if 'Superintendent' in groups or 'Faculty' in groups:
        return True
    return False 

def marks_upload_access(user):
    groups = user.groups.all().values_list('name', flat=True)
    if 'Superintendent' in groups or 'Faculty' in groups:
        return True
    return False

