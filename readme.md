==========================================================================================================

git clone https://github.com/intern-bug/exam_section_btech.git
==========================================================================================================

update database name and password(preferably new)
==========================================================================================================

py manage.py createsuperuser

after creating superuser, add groups, and users(users and passwords mentioned below)
==========================================================================================================
py manage.py makemigrations
py manage.py migrate
===========================================================================================================
run new_views.sql, new_mtech_views.sql in pgadmin
===========================================================================================================
run these commands in pgadmin
(paste the excel file in public user and use that path.)
copy public."BTProgrammeModel" ("PID","ProgrammeName", "ProgrammeType", "Specialization", "Dept") FROM '<path>' DELIMITER ',' CSV HEADER QUOTE '"';

copy public."MTProgrammeModel" ("PID","ProgrammeName", "ProgrammeType", "Specialization", "Dept") FROM '<path>' DELIMITER ',' CSV HEADER QUOTE '"';

copy public."BTDepartments" ("Dept","Name", "Dept_Code") FROM '<path>' DELIMITER ',' CSV HEADER QUOTE '"';

copy public."MTDepartments" ("Dept","Name", "Dept_Code") FROM '<path>' DELIMITER ',' CSV HEADER QUOTE '"';

============================================================================================================

USERs and PASSWORDs

user: sup1
password: sup1@123

user: hod1
password: hod1@123

user: examsection1
password: examstaff1@123

user: cord1
password: coordinator1@123

user: fac1
password: faculty1@123

user: phy1
password: phycord1@123

user: che1
password: checord1@123

============================================================================================================
