

def is_Superintendent(user):
    return user.groups.filter(name='Superintendent').exists()
def is_Hod(user):
    return user.groups.filter(name='HOD').exists()
def is_Faculty(user):
    return user.groups.filter(name='Faculty').exists()
def is_Co_ordinator(user):
    return user.groups.filter(name='Co-ordinator').exists()
def is_ExamStaff(user):
    return user.groups.filter(name='ExamStaff').exists()
def is_Associate_Dean(user):
    return user.groups.filter(name='Associate-Dean').exists()

def user_management_home_access(user):
    groups = user.groups.all().values_list('name', flat=True)
    if 'Superintendent' in groups or 'HOD' in groups:
        return True
    return False
def roll_list_access(user):
    groups = user.groups.all().values_list('name', flat=True)
    if 'Co-ordinator' in groups or 'Cycle-Co-ordinator' in groups:
        return True
    return  False

def roll_list_status_access(user):
    groups = user.groups.all().values_list('name', flat=True)
    if 'Superintendent' in groups or 'Co-ordinator' in groups or 'HOD' in groups or 'Cycle-Co-ordinator' in groups or 'Associate-Dean' in groups:
        return True
    return  False

def subject_access(user):
    groups = user.groups.all().values_list('name', flat=True)
    if 'Co-ordinator' in groups or 'Cycle-Co-ordinator' in groups :
        return True
    return False

def subject_home_access(user):
    groups = user.groups.all().values_list('name', flat=True)
    if 'Superintendent' in groups or 'Co-ordinator' in groups or 'Cycle-Co-ordinator' in groups or 'HOD' in groups or 'Associate-Dean' in groups:
        return True
    return False

def registration_access(user):
    groups = user.groups.all().values_list('name', flat=True)
    if 'Co-ordinator' in groups or 'Cycle-Co-ordinator' in groups:
        return True
    return False 

def registration_status_access(user):
    groups = user.groups.all().values_list('name', flat=True)
    if 'Co-ordinator' in groups or 'Cycle-Co-ordinator' in groups or 'Superintendent' in groups or 'HOD' in groups or 'Associate-Dean' in groups:
        return True
    return False 

def grades_finalize_access(user):
    groups = user.groups.all().values_list('name', flat=True)
    if 'HOD' in groups:
        return True
    return False 

def grades_threshold_access(user):
    groups = user.groups.all().values_list('name', flat=True)
    if 'Faculty' in groups:
        return True
    return False 

def grades_threshold_status_access(user):
    groups = user.groups.all().values_list('name', flat=True)
    if 'Faculty' in groups or 'Co-ordinator' in groups or 'Cycle-Co-ordinator' in groups or 'HOD' in groups or 'Superintendent' in groups\
        or 'Associate-Dean' in groups:
        return True
    return False 

def marks_upload_access(user):
    groups = user.groups.all().values_list('name', flat=True)
    if 'Faculty' in groups:
        return True
    return False

def attendance_shortage_status_access(user):
    groups = user.groups.all().values_list('name', flat=True)
    if 'Superintendent' in groups or 'Co-ordinator' in groups or 'HOD' in groups or 'Faculty' in groups or 'Cycle-Co-ordinator' in groups\
        or 'Associate-Dean' in groups:
        return True
    return  False

def pre_registrations_home_access(user):
    groups = user.groups.all().values_list('name', flat=True)
    if 'Superintendent' in groups or 'Co-ordinator' in groups or 'HOD' in groups or 'ExamStaff' in groups:
        return True
    return  False

def grades_home_access(user):
    groups = user.groups.all().values_list('name', flat=True)
    if 'Superintendent' in groups or 'Co-ordinator' in groups or 'HOD' in groups or 'ExamStaff' in groups or 'Cycle-Co-ordinator' in groups or\
        'Faculty' in groups:
        return True
    return  False

def ix_grade_student_status_access(user):
    groups = user.groups.all().values_list('name', flat=True)
    if 'Superintendent' in groups or 'Co-ordinator' in groups or 'HOD' in groups or 'ExamStaff' in groups or 'Faculty' in groups or 'Cycle-Co-ordinator' in groups \
        or 'Associate-Dean' in groups:
        return True
    return  False


def grades_status_access(user):
    groups = user.groups.all().values_list('name', flat=True)
    if 'Superintendent' in groups or 'Co-ordinator' in groups or 'HOD' in groups or 'Faculty' in groups or 'Cycle-Co-ordinator' in groups\
        or 'Associate-Dean' in groups:
        return True
    return  False

def faculty_home_access(user):
    groups = user.groups.all().values_list('name', flat=True)
    if 'Superintendent' in groups or 'Co-ordinator' in groups or 'HOD' in groups or 'Faculty' in groups or 'ExamStaff' in groups\
        or 'Cycle-Co-ordinator' in groups:
        return True
    return  False

def faculty_info_status_access(user):
    groups = user.groups.all().values_list('name', flat=True)
    if 'Superintendent' in groups or 'Co-ordinator' in groups or 'HOD' in groups or 'ExamStaff' in groups or 'Associate-Dean' in groups:
        return True
    return  False


def co_ordinator_assignment_access(user):
    groups = user.groups.all().values_list('name', flat=True)
    if 'Superintendent' in groups or 'HOD' in groups or 'Associate-Dean' in groups:
        return True
    return  False

def faculty_subject_assignment_access(user):
    groups = user.groups.all().values_list('name', flat=True)
    if 'Co-ordinator' in groups or 'HOD' in groups:
        return True
    return  False

def faculty_assignment_status_access(user):
    groups = user.groups.all().values_list('name', flat=True)
    if 'Superintendent' in groups or 'Co-ordinator' in groups or 'HOD' in groups or 'Cycle-Co-ordinator' in groups or 'Associate-Dean' in groups:
        return True
    return  False

def marks_home_access(user):
    groups = user.groups.all().values_list('name', flat=True)
    if 'Superintendent' in groups or 'Co-ordinator' in groups or 'HOD' in groups or 'Cycle-Co-ordinator' in groups or 'Faculty' in groups:
        return True
    return  False

def marks_status_access(user):
    groups = user.groups.all().values_list('name', flat=True)
    if 'Superintendent' in groups or 'Co-ordinator' in groups or 'HOD' in groups or 'Cycle-Co-ordinator' in groups or 'Faculty' in groups\
        or 'Associate-Dean' in groups:
        return True
    return  False

def not_promoted_access(user):
    groups = user.groups.all().values_list('name', flat=True)
    if 'Co-ordinator' in groups or 'Cycle-Co-ordinator' in groups:
        return True
    return  False

def not_promoted_status_access(user):
    groups = user.groups.all().values_list('name', flat=True)
    if 'HOD' in groups or 'Superintendent' in groups or 'Co-ordinator' in groups or 'Cycle-Co-ordinator' in groups or 'Associate-Dean' in groups:
        return True
    return  False

def not_promoted_home_access(user):
    groups = user.groups.all().values_list('name', flat=True)
    if 'HOD' in groups or 'Superintendent' in groups or 'Co-ordinator' in groups or 'Cycle-Co-ordinator' in groups:
        return True
    return  False


def sample_regno_sheet_access(user):
    groups = user.groups.all().values_list('name', flat=True)
    if 'Co-ordinator' in groups or 'Faculty' in groups or 'Cycle-Co-ordinator' in groups or 'Superintendent' in groups:
        return True
    return  False

def gpa_staging_access(user):
    groups = user.groups.all().values_list('name', flat=True)
    if 'Superintendent' in groups or 'HOD' in groups or 'Associate-Dean' in groups:
        return True
    return  False

def grade_challenge_status_access(user):
    groups = user.groups.all().values_list('name', flat=True)
    if 'Superintendent' in groups or 'Associate-Dean' in groups:
        return True
    return  False

def branch_change_status_access(user):
    groups = user.groups.all().values_list('name', flat=True)
    if 'Superintendent' in groups or 'Associate-Dean' in groups:
        return True
    return  False

def cycle_coordinator_assignment_status_access(user):
    groups = user.groups.all().values_list('name', flat=True)
    if 'Superintendent' in groups or 'Associate-Dean' in groups:
        return True
    return  False

def grade_points_status_access(user):
    groups = user.groups.all().values_list('name', flat=True)
    if 'Superintendent' in groups or 'Associate-Dean' in groups:
        return True
    return  False


def hod_assignment_status_access(user):
    groups = user.groups.all().values_list('name', flat=True)
    if 'Superintendent' in groups or 'Associate-Dean' in groups:
        return True
    return  False


def mark_distribution_status_access(user):
    groups = user.groups.all().values_list('name', flat=True)
    if 'Superintendent' in groups or 'Associate-Dean' in groups:
        return True
    return  False