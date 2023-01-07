


create materialized view if not exists "BTStudentGradePointsMV" as
SELECT row_number() OVER (ORDER BY (ROW (g."RegNo", g."AYASBYBS", g."SubName"))) AS id,
       g."RegNo",
       g.sub_id,
       g."SubCode",
       g."SubName",
       g."AYear",
       g."ASem",
       g."BYear",
       g."BSem",
       g."OfferedYear",
       g."Dept",
       g."Grade",
       g."AttGrade",
       g."Regulation",
       g."CourseStructure_id",
       g."count",
       g."Creditable",
       g."Course_Credits",
       g."Credits",
       g."Type",
       g."Category",
       g."Points",
       g."GP",
       g."AYASBYBS"
FROM (SELECT final_table."RegNo",
             final_table.sub_id,
             final_table."SubCode",
             final_table."SubName",
             final_table."AYear",
             final_table."ASem",
             final_table."BYear",
             final_table."BSem",
             final_table."OfferedYear",
             final_table."Dept",
             final_table."Grade",
             final_table."AttGrade",
             final_table."Regulation",
             final_table."CourseStructure_id",
             final_table."count",
             final_table."Creditable",
             final_table."Curriculum_Credits"as "Credits",
             final_table."Course_Credits",
             final_table."Type",
             final_table."Category",
             final_table."Points",
             final_table."Curriculum_Credits"::INTEGER * final_table."Points" * final_table."Creditable"                                AS "GP",
             ((final_table."AYear" * 10 + final_table."ASem") * 10 + final_table."BYear") * 10 +
             final_table."BSem"                                                                                     AS "AYASBYBS"
      FROM (((SELECT sg_reg."Regulation",
                     sg_reg."Grade",
                     sg_reg."AttGrade",
                     sg_reg."RegNo",
                     sg_reg."AYear",
                     sg_reg."ASem",
                     sg_reg."BYear",
                     sg_reg.sub_id,
			  sg_reg."SubCode",
			  sg_reg."SubName",
                    sg_reg."CourseStructure_id",
                    sg_reg."count",
			  sg_reg."Creditable",
			  sg_reg."Type",
			  sg_reg."Course_Credits",
			  sg_reg."Curriculum_Credits",
			  sg_reg."Category",
                     "BTGradePoints"."Points"
			         
              FROM (((SELECT "BTStudentGrades"."Grade",
                             "BTStudentGrades"."AttGrade",
                             "BTStudentGrades"."RegId",
                             "BTStudentGrades"."RegEventId"
                      FROM "BTStudentGrades") sg
                 JOIN (SELECT "BTStudentInfo"."RegNo","BTCourses"."SubCode" as "SubCode","BTCourses"."SubName" as "SubName" ,
                               "BTCourses"."CourseStructure_id" as "CourseStructure_id",
                               "BTCourses"."Credits" as "Course_Credits",
                               "BTCourseStructure"."count" as "count",     
					   "BTCourseStructure"."Creditable" as "Creditable",
					   "BTCourseStructure"."Type" as "Type",
					   "BTCourseStructure"."Credits" as "Curriculum_Credits",
					   "BTCourseStructure"."Category" as "Category",
                               "BTStudentRegistrations"."sub_id",
                               "BTStudentRegistrations"."id" from "BTStudentRegistrations" join "BTRollLists" on "BTStudentRegistrations"."student_id"="BTRollLists"."id" join "BTStudentInfo" on "BTRollLists"."student_id"="BTStudentInfo"."id" join "BTSubjects" on 
                               "BTStudentRegistrations"."sub_id" = "BTSubjects".id join "BTCourses" on "BTSubjects"."course_id" = "BTCourses".id join "BTCourseStructure" on "BTCourseStructure"."id" = "BTCourses"."CourseStructure_id"
                        ) sreg ON sg."RegId" = sreg.id) sg_regs
                  JOIN "BTRegistration_Status" ON "BTRegistration_Status".id = sg_regs."RegEventId") sg_reg
                       JOIN "BTGradePoints" ON sg_reg."Regulation" = "BTGradePoints"."Regulation" AND
                                             sg_reg."Grade"::text = "BTGradePoints"."Grade"::text) gp_table
          JOIN "BTSubjects" subs ON gp_table.sub_id::bigint = subs.id) grades
          JOIN (SELECT "BTRegistration_Status".id,
                       "BTRegistration_Status"."AYear" AS "OfferedYear",
                       "BTRegistration_Status"."Dept",
                       "BTRegistration_Status"."BSem"
                FROM "BTRegistration_Status") rg_status ON grades."RegEventId_id" = rg_status.id) final_table) g;


alter materialized view "BTStudentGradePointsMV" owner to postgres;

REFRESH MATERIALIZED VIEW public."BTStudentGradePointsMV" WITH DATA;


create materialized view if not exists "BTStudentGradePoints_StagingMV" as
SELECT row_number() OVER (ORDER BY (ROW (g."RegNo", g."AYASBYBS", g."SubName"))) AS id,
       g."RegNo",
       g.sub_id,
       g."SubCode",
       g."SubName",
       g."AYear",
       g."ASem",
       g."BYear",
       g."BSem",
       g."OfferedYear",
       g."Dept",
       g."Grade",
       g."AttGrade",
       g."Regulation",
       g."CourseStructure_id",
       g."count",
       g."Creditable",
       g."Course_Credits",
       g."Credits",
       g."Type",
       g."Category",
       g."Points",
       g."GP",
       g."AYASBYBS"
FROM (SELECT final_table."RegNo",
             final_table.sub_id,
             final_table."SubCode",
             final_table."SubName",
             final_table."AYear",
             final_table."ASem",
             final_table."BYear",
             final_table."BSem",
             final_table."OfferedYear",
             final_table."Dept",
             final_table."Grade",
             final_table."AttGrade",
             final_table."Regulation",
             final_table."CourseStructure_id",
             final_table."count",
             final_table."Creditable",
             final_table."Curriculum_Credits"as "Credits",
             final_table."Course_Credits",
             final_table."Type",
             final_table."Category",
             final_table."Points",
             final_table."Curriculum_Credits"::INTEGER * final_table."Points" * final_table."Creditable"                                AS "GP",
             ((final_table."AYear" * 10 + final_table."ASem") * 10 + final_table."BYear") * 10 +
             final_table."BSem"                                                                                     AS "AYASBYBS"
      FROM (((SELECT sg_reg."Regulation",
                     sg_reg."Grade",
                     sg_reg."AttGrade",
                     sg_reg."RegNo",
                     sg_reg."AYear",
                     sg_reg."ASem",
                     sg_reg."BYear",
                     sg_reg.sub_id,
			  sg_reg."SubCode",
			  sg_reg."SubName",
                    sg_reg."CourseStructure_id",
                    sg_reg."count",
			  sg_reg."Creditable",
			  sg_reg."Type",
			  sg_reg."Course_Credits",
			  sg_reg."Curriculum_Credits",
			  sg_reg."Category",
                     "BTGradePoints"."Points"
			         
              FROM (((SELECT "BTStudentGrades_Staging"."Grade",
                             "BTStudentGrades_Staging"."AttGrade",
                             "BTStudentGrades_Staging"."RegId",
                             "BTStudentGrades_Staging"."RegEventId"
                      FROM "BTStudentGrades_Staging") sg
                 JOIN (SELECT "BTStudentInfo"."RegNo","BTCourses"."SubCode" as "SubCode","BTCourses"."SubName" as "SubName" ,
                               "BTCourses"."CourseStructure_id" as "CourseStructure_id",
                               "BTCourses"."Credits" as "Course_Credits",
                               "BTCourseStructure"."count" as "count",     
					   "BTCourseStructure"."Creditable" as "Creditable",
					   "BTCourseStructure"."Type" as "Type",
					   "BTCourseStructure"."Credits" as "Curriculum_Credits",
					   "BTCourseStructure"."Category" as "Category",
                               "BTStudentRegistrations"."sub_id",
                               "BTStudentRegistrations"."id" from "BTStudentRegistrations" join "BTRollLists" on "BTStudentRegistrations"."student_id"="BTRollLists"."id" join "BTStudentInfo" on "BTRollLists"."student_id"="BTStudentInfo"."id" join "BTSubjects" on 
                               "BTStudentRegistrations"."sub_id" = "BTSubjects".id join "BTCourses" on "BTSubjects"."course_id" = "BTCourses".id join "BTCourseStructure" on "BTCourseStructure"."id" = "BTCourses"."CourseStructure_id"
                        ) sreg ON sg."RegId" = sreg.id) sg_regs
                  JOIN "BTRegistration_Status" ON "BTRegistration_Status".id = sg_regs."RegEventId") sg_reg
                       JOIN "BTGradePoints" ON sg_reg."Regulation" = "BTGradePoints"."Regulation" AND
                                             sg_reg."Grade"::text = "BTGradePoints"."Grade"::text) gp_table
          JOIN "BTSubjects" subs ON gp_table.sub_id::bigint = subs.id) grades
          JOIN (SELECT "BTRegistration_Status".id,
                       "BTRegistration_Status"."AYear" AS "OfferedYear",
                       "BTRegistration_Status"."Dept",
                       "BTRegistration_Status"."BSem"
                FROM "BTRegistration_Status") rg_status ON grades."RegEventId_id" = rg_status.id) final_table) g;

REFRESH MATERIALIZED VIEW public."BTStudentGradePoints_StagingMV" WITH DATA;

create materialized view "BTStudentExamEventsMV" as
SELECT "SS".id,
       "SS"."RegNo",
       "SS"."AYASBYBS",
       "SS"."BYear",
       "SS"."BSem",
       CASE
           WHEN "SS".bybscount > 1 THEN 0
           ELSE 1
           END AS "IsRegular"
FROM (SELECT row_number() OVER (ORDER BY s."RegNo", s."AYASBYBS")                                            AS id,
             s."RegNo",
             s."AYASBYBS",
             s."BYear",
             s."BSem",
             s."BYBS",
             row_number()
             OVER (PARTITION BY s."RegNo", s."BYBS" ORDER BY s."RegNo", s."BYBS", s."AYASBYBS")              AS bybscount
      FROM (SELECT DISTINCT "BTStudentGradePointsMV"."RegNo",
                            "BTStudentGradePointsMV"."AYASBYBS",
                            "BTStudentGradePointsMV"."BSem",
                            "BTStudentGradePointsMV"."BYear",
                            mod("BTStudentGradePointsMV"."AYASBYBS"::int, 100) AS "BYBS"
            FROM "BTStudentGradePointsMV") s) "SS";

alter materialized view "BTStudentExamEventsMV" owner to postgres;
REFRESH MATERIALIZED VIEW public."BTStudentExamEventsMV" WITH DATA;


create materialized view "BTStudentBacklogsMV" as
SELECT row_number() OVER (ORDER BY "final_table"."RegNo", "final_table"."SubCode") AS id,
       "final_table"."RegNo",
       "final_table"."RollNo",
       "final_table".sub_id,
       "final_table"."SubCode",
       "final_table"."SubName",
       "final_table"."Type",
       "final_table"."Category",
       "final_table"."Credits",
       "final_table"."Course_Credits",
       "final_table"."CourseStructure_id",
       "final_table"."count",
	 "final_table"."ClearedCourses",
       "final_table"."BYear",
       "final_table"."BSem",
       "final_table"."GP",
       "final_table"."Regulation",
       "final_table"."Grade",
       "final_table"."Dept",
       "final_table"."OfferedYear",
       "final_table"."AYASBYBS"
from(select "nested_table"."RegNo",
       "nested_table"."RollNo",
       "nested_table".sub_id,
       "nested_table"."SubCode",
       "nested_table"."SubName",
       "nested_table"."Type",
       "nested_table"."Category",
       "nested_table"."Course_Credits",
       "nested_table"."Credits",
       "nested_table"."CourseStructure_id",
       "nested_table"."count",
	   "nested_table"."ClearedCourses",
       "nested_table"."BYear",
       "nested_table"."BSem",
       "nested_table"."GP",
       "nested_table"."Regulation",
       "nested_table"."Grade",
       "nested_table"."Dept",
       "nested_table"."OfferedYear",
       "nested_table"."AYASBYBS",
       row_number()
       OVER (PARTITION BY "nested_table"."RegNo", "nested_table"."CourseStructure_id" ORDER BY "nested_table"."RegNo", "nested_table"."AYASBYBS", "nested_table"."CourseStructure_id" DESC) AS "RNK"
FROM ((SELECT "Q"."RegNo",
             "S"."RollNo",
             "Q".sub_id,
             "Q"."SubCode",
             "Q"."SubName",
             "Q"."Type",
             "Q"."Category",
             "Q"."Credits",
             "Q"."Course_Credits",
             "Q"."CourseStructure_id",
             "Q"."count",
             "Q"."BYear",
             "Q"."BSem",
             "Q"."GP",
             "Q"."Regulation",
             "Q"."Grade",
             "Q"."Dept",
             "Q"."OfferedYear",
             "Q"."AYASBYBS",
             row_number() over (partition by "Q"."RegNo", "Q"."SubCode" order by ("Q"."RegNo", "Q"."AYASBYBS", "Q"."CourseStructure_id") desc) as "RNK_1"
             FROM "BTStudentGradePointsMV" "Q",
           "BTStudentInfo" "S"
      WHERE "Q"."RegNo" = "S"."RegNo") "P" join 
      (SELECT  "Q"."RegNo" as "regd_no",
        "Q"."CourseStructure_id" as "cs_id",
        Sum(Case when not 
        ("Q"."Grade"::text = ANY
       (ARRAY ['F'::character varying::text, 'R'::character varying::text, 'I'::character varying::text, 'X'::character varying::text])) 
       then 1 else 0 end)
        as "ClearedCourses"
        FROM "BTStudentGradePointsMV" "Q",
           "BTStudentInfo" "S"
      WHERE "Q"."RegNo" = "S"."RegNo"
       group by "Q"."RegNo", "Q"."CourseStructure_id") "R" on "P"."RegNo"="R"."regd_no" and "P"."CourseStructure_id"="R"."cs_id" and "P"."RNK_1"=1)"nested_table"
WHERE "nested_table"."count" > "nested_table"."ClearedCourses"
  AND ("nested_table"."Grade"::text = ANY
       (ARRAY ['F'::character varying::text, 'R'::character varying::text, 'I'::character varying::text, 'X'::character varying::text]))) "final_table"
	where "final_table"."RNK" between 1 and ("final_table"."count"-"final_table"."ClearedCourses");

alter materialized view "BTStudentBacklogsMV" owner to postgres;

REFRESH MATERIALIZED VIEW public."BTStudentBacklogsMV" WITH DATA;






create materialized view "BTStudentMakeupBacklogsMV" as
SELECT row_number() OVER (ORDER BY "final_table"."RegNo", "final_table"."SubCode") AS id,
       "final_table"."RegNo",
       "final_table"."RollNo",
       "final_table".sub_id,
       "final_table"."SubCode",
       "final_table"."SubName",
       "final_table"."Type",
       "final_table"."Category",
       "final_table"."Credits",
       "final_table"."Course_Credits",
       "final_table"."CourseStructure_id",
       "final_table"."count",
	   "final_table"."ClearedCourses",
       "final_table"."BYear",
       "final_table"."BSem",
       "final_table"."GP",
       "final_table"."Regulation",
       "final_table"."Grade",
       "final_table"."Dept",
       "final_table"."OfferedYear",
       "final_table"."AYASBYBS"
from(select "nested_table"."RegNo",
       "nested_table"."RollNo",
       "nested_table".sub_id,
       "nested_table"."SubCode",
       "nested_table"."SubName",
       "nested_table"."Type",
       "nested_table"."Category",
       "nested_table"."Course_Credits",
       "nested_table"."Credits",
       "nested_table"."CourseStructure_id",
       "nested_table"."count",
	   "nested_table"."ClearedCourses",
       "nested_table"."BYear",
       "nested_table"."BSem",
       "nested_table"."GP",
       "nested_table"."Regulation",
       "nested_table"."Grade",
       "nested_table"."Dept",
       "nested_table"."OfferedYear",
       "nested_table"."AYASBYBS",
       row_number()
       OVER (PARTITION BY "nested_table"."RegNo", "nested_table"."CourseStructure_id" ORDER BY "nested_table"."RegNo", "nested_table"."AYASBYBS", "nested_table"."CourseStructure_id" DESC) AS "RNK"
FROM ((SELECT "Q"."RegNo",
             "S"."RollNo",
             "Q".sub_id,
             "Q"."SubCode",
             "Q"."SubName",
             "Q"."Type",
             "Q"."Category",
             "Q"."Course_Credits",
             "Q"."Credits",
             "Q"."CourseStructure_id",
             "Q"."count",
             "Q"."BYear",
             "Q"."BSem",
             "Q"."GP",
             "Q"."Regulation",
             "Q"."Grade",
             "Q"."Dept",
             "Q"."OfferedYear",
             "Q"."AYASBYBS",
             row_number() over (partition by "Q"."RegNo", "Q"."SubCode" order by ("Q"."RegNo", "Q"."AYASBYBS", "Q"."CourseStructure_id") desc) as "RNK_1"
             FROM "BTStudentGradePointsMV" "Q",
           "BTStudentInfo" "S"
      WHERE "Q"."RegNo" = "S"."RegNo") "P" join 
      (SELECT  "Q"."RegNo" as "regd_no",
        "Q"."CourseStructure_id" as "cs_id",
        Sum(Case when not 
        ("Q"."Grade"::text = ANY
       (ARRAY ['F'::character varying::text, 'R'::character varying::text, 'I'::character varying::text, 'X'::character varying::text])) 
       then 1 else 0 end)
        as "ClearedCourses"
        FROM "BTStudentGradePointsMV" "Q",
           "BTStudentInfo" "S"
      WHERE "Q"."RegNo" = "S"."RegNo"
       group by "Q"."RegNo", "Q"."CourseStructure_id") "R" on "P"."RegNo"="R"."regd_no" and "P"."CourseStructure_id"="R"."cs_id" and "P"."RNK_1"=1)"nested_table"
WHERE "nested_table"."count" > "nested_table"."ClearedCourses"
  AND ("nested_table"."Grade"::text = ANY
       (ARRAY ['F'::character varying::text, 'I'::character varying::text, 'X'::character varying::text]))) "final_table"
	where "final_table"."RNK" between 1 and ("final_table"."count"-"final_table"."ClearedCourses");

alter materialized view "BTStudentMakeupBacklogsMV" owner to postgres;

REFRESH MATERIALIZED VIEW public."BTStudentMakeupBacklogsMV" WITH DATA;


------------------------------------------------------------------------------------------------------------------------


CREATE MATERIALIZED VIEW public."BTStudentExamEvents_StagingMV"
AS
SELECT "SS"."id", "SS"."RegNo",
		"SS"."AYASBYBS","SS"."BYear","SS"."BSem",
		CASE WHEN("SS"."bybscount" > 1) THEN 0 ELSE 1 END AS "IsRegular"  
		from (
		SELECT row_number() OVER (ORDER BY s."RegNo", s."AYASBYBS") AS id,
			s."RegNo",
			s."AYASBYBS",
			s."BYear",
			s."BSem",
			s."BYBS",
			row_number() OVER (partition by s."RegNo", s."BYBS" ORDER BY s."RegNo", s."BYBS", s."AYASBYBS") AS "bybscount"
			FROM ( SELECT DISTINCT "BTStudentGradePoints_StagingMV"."RegNo",
					"BTStudentGradePoints_StagingMV"."AYASBYBS",
					"BTStudentGradePoints_StagingMV"."BYear",
					"BTStudentGradePoints_StagingMV"."BSem",
					MOD("BTStudentGradePoints_StagingMV"."AYASBYBS",100) as "BYBS"
				   FROM "BTStudentGradePoints_StagingMV") as s) as "SS"
WITH NO DATA;

REFRESH MATERIALIZED VIEW public."BTStudentExamEvents_StagingMV" WITH DATA;

------------------------------------------------------------------------------------------------------------------------

CREATE MATERIALIZED VIEW public."BTStudentPresentPastResults_StagingMV"
AS
SELECT ROW_NUMBER() OVER(order by ("RegNo","AYASBYBS","AYASBYBS_G")) as id, * from (
SELECT "BTStudentGradePoints_StagingMV"."RegNo",
    "BTStudentGradePoints_StagingMV"."SubCode",
    "BTStudentGradePoints_StagingMV"."SubName",
    "BTStudentGradePoints_StagingMV"."AYear",
    "BTStudentGradePoints_StagingMV"."ASem",
    "BTStudentGradePoints_StagingMV"."BYear",
    "BTStudentGradePoints_StagingMV"."BSem",
    "BTStudentGradePoints_StagingMV"."OfferedYear",
    "BTStudentGradePoints_StagingMV"."Dept",
    "BTStudentGradePoints_StagingMV"."Grade",
    "BTStudentGradePoints_StagingMV"."AttGrade",
    "BTStudentGradePoints_StagingMV"."Regulation",
    "BTStudentGradePoints_StagingMV"."Credits"::INTEGER * "BTStudentGradePoints_StagingMV"."Creditable" as "Credits",
    "BTStudentGradePoints_StagingMV"."Points",
    "BTStudentGradePoints_StagingMV"."GP",
    "BTStudentGradePoints_StagingMV"."AYASBYBS",
    "BTStudentExamEvents_StagingMV"."AYASBYBS" AS "AYASBYBS_G"
   FROM "BTStudentGradePoints_StagingMV",
    "BTStudentExamEvents_StagingMV"
  WHERE "BTStudentGradePoints_StagingMV"."AYASBYBS" <= "BTStudentExamEvents_StagingMV"."AYASBYBS" AND "BTStudentGradePoints_StagingMV"."BYear" = "BTStudentExamEvents_StagingMV"."BYear" AND "BTStudentGradePoints_StagingMV"."BSem" = "BTStudentExamEvents_StagingMV"."BSem" AND "BTStudentGradePoints_StagingMV"."RegNo" = "BTStudentExamEvents_StagingMV"."RegNo") as AA
WITH NO DATA;

REFRESH MATERIALIZED VIEW public."BTStudentPresentPastResults_StagingMV" WITH DATA;

------------------------------------------------------------------------------------------------------------------------


------------------------------------------------------------------------------------------------------------------------




create materialized view "BTStudentPresentPastResultsMV" as
SELECT row_number() OVER (ORDER BY (ROW (aa."RegNo", aa."AYASBYBS", aa."AYASBYBS_G"))) AS id,
       aa."RegNo",
       aa."SubCode",
       aa."SubName",
       aa."AYear",
       aa."ASem",
       aa."BYear",
       aa."BSem",
       aa."OfferedYear",
       aa."Dept",
       aa."Grade",
       aa."AttGrade",
       aa."Regulation",
       aa."Credits",
       aa."Points",
       aa."GP",
       aa."AYASBYBS",
       aa."AYASBYBS_G"
FROM (SELECT "BTStudentGradePointsMV"."RegNo",
             "BTStudentGradePointsMV"."SubCode",
             "BTStudentGradePointsMV"."SubName",
             "BTStudentGradePointsMV"."AYear",
             "BTStudentGradePointsMV"."ASem",
             "BTStudentGradePointsMV"."BYear",
             "BTStudentGradePointsMV"."BSem",
             "BTStudentGradePointsMV"."OfferedYear",
             "BTStudentGradePointsMV"."Dept",
             "BTStudentGradePointsMV"."Grade",
             "BTStudentGradePointsMV"."AttGrade",
             "BTStudentGradePointsMV"."Regulation",
             "BTStudentGradePointsMV"."Credits" * "BTStudentGradePointsMV"."Creditable" AS "Credits",
             "BTStudentGradePointsMV"."Points",
             "BTStudentGradePointsMV"."GP",
             "BTStudentGradePointsMV"."AYASBYBS",
             "BTStudentExamEventsMV"."AYASBYBS"                                       AS "AYASBYBS_G"
      FROM "BTStudentGradePointsMV",
           "BTStudentExamEventsMV"
      WHERE "BTStudentGradePointsMV"."AYASBYBS" <= "BTStudentExamEventsMV"."AYASBYBS"
        AND "BTStudentGradePointsMV"."BYear" = "BTStudentExamEventsMV"."BYear"
        AND "BTStudentGradePointsMV"."BSem" = "BTStudentExamEventsMV"."BSem"
        AND "BTStudentGradePointsMV"."RegNo" = "BTStudentExamEventsMV"."RegNo") aa;

alter materialized view "BTStudentPresentPastResultsMV" owner to postgres;

REFRESH MATERIALIZED VIEW public."BTStudentPresentPastResultsMV" WITH DATA;




------------------------------------------------------------------------------------------------------------------------

create or replace view "BTBacklogRegistrationSummaryV"(id, "RegNo", "RollNo", "Name", "BYear", "BSem", "Dept", "AYear", "ASem", "Regulation", "RegisteredSubjects") as
SELECT row_number() OVER () AS id,
       r."RegNo",
       r."RollNo",
       r."Name",
       q."BYear",
       q."BSem",
       q."Dept",
       q."AYear",
       q."ASem",
       q."Regulation",
       q."RegisteredSubjects"
FROM (SELECT 
	  		 p."RegNo",
             p."AYear",
             p."ASem",
             p."BYear",
             p."BSem",
             p."Dept",
             p."Regulation",
             string_agg(p."SubCode"::text||'('||p."Mode"||')', ','::text) AS "RegisteredSubjects"
      FROM ((SELECT 
                    reg_status."AYear",
                    reg_status."ASem",
                    reg_status."BYear",
                    reg_status."BSem",
                    reg_status."Dept",
                    reg_status."Regulation",
                    sreg.sub_id,
                    case when sreg."Mode"=1 then 'S' else 'E' end as "Mode",
                    "BTStudentInfo"."RegNo"
			 		
             FROM "BTStudentRegistrations_Staging" sreg join "BTRollLists_Staging" on sreg."student_id" = "BTRollLists_Staging"."id" join "BTStudentInfo" on "BTRollLists_Staging"."student_id"="BTStudentInfo"."id"
                      JOIN "BTRegistration_Status" reg_status ON sreg."RegEventId" = reg_status.id
             WHERE reg_status."Mode"::text = 'B'::text) sreg_status 
			
          JOIN (select bts."id" as "id",bts."RegEventId_id" as "RegEventId_id",btc."SubCode" as "SubCode",btc."SubName" as "SubName" from "BTSubjects" bts JOIN "BTCourses" btc on bts."course_id"=btc."id" )subs ON sreg_status.sub_id = subs.id) p
      GROUP BY p."RegNo"  ,p."AYear", p."ASem", p."BYear", p."BSem", p."Dept", p."Regulation") q,
     (SELECT "BTStudentInfo"."RegNo",
             "BTStudentInfo"."RollNo",
             "BTStudentInfo"."Name"
      FROM "BTStudentInfo") r
WHERE q."RegNo" = r."RegNo";

alter table "BTBacklogRegistrationSummaryV" owner to postgres;


create or replace view "BTMakeupRegistrationSummaryV"(id, "RegNo", "RollNo", "Name", "BYear", "BSem", "Dept", "AYear", "ASem", "Regulation", "RegisteredSubjects") as
SELECT row_number() OVER () AS id,
       q."RegNo",
       r."RollNo",
       r."Name",
       q."BYear",
       q."BSem",
       q."Dept",
       q."AYear",
       q."ASem",
       q."Regulation",
       q."RegisteredSubjects"
FROM (SELECT p."RegNo",
             p."AYear",
             p."ASem",
             p."BYear",
             p."BSem",
             p."Dept",
             p."Regulation",
             string_agg(p."SubCode"::text||'('||p."Mode"||')', ','::text) AS "RegisteredSubjects"
      FROM ((SELECT "BTStudentInfo"."RegNo",
                    reg_status."AYear",
                    reg_status."ASem",
                    reg_status."BYear",
                    reg_status."BSem",
                    reg_status."Dept",
                    reg_status."Regulation",
                    sreg.sub_id,
                    case when sreg."Mode"=1 then 'S' else 'E' end as "Mode"
                    
             FROM "BTStudentRegistrations_Staging" sreg join "BTRollLists_Staging" on sreg."student_id" = "BTRollLists_Staging"."id" join "BTStudentInfo" on "BTRollLists_Staging"."student_id"="BTStudentInfo"."id"
                      JOIN "BTRegistration_Status" reg_status ON sreg."RegEventId" = reg_status.id
             WHERE reg_status."Mode"::text = 'M'::text) sreg_status
          JOIN "BTSubjects" bts ON sreg_status.sub_id = bts.id JOIN "BTCourses" btc on bts."course_id"=btc."id" ) p
      GROUP BY p."RegNo", p."AYear", p."ASem", p."BYear", p."BSem", p."Dept", p."Regulation") q,
     (SELECT "BTStudentInfo"."RegNo",
             "BTStudentInfo"."RollNo",
             "BTStudentInfo"."Name"
      FROM "BTStudentInfo") r
WHERE q."RegNo" = r."RegNo";

alter table "BTMakeupRegistrationSummaryV" owner to postgres;

create or replace view "BTRegularRegistrationSummaryV"(id, "RegNo", "RollNo", "Name", "BYear", "BSem", "Dept", "AYear", "ASem", "Regulation", "RegisteredSubjects") as
SELECT row_number() OVER () AS id,
       q."RegNo",
       r."RollNo",
       r."Name",
       q."BYear",
       q."BSem",
       q."Dept",
       q."AYear",
       q."ASem",
       q."Regulation",
       q."RegisteredSubjects"
FROM (SELECT p."RegNo",
             p."AYear",
             p."ASem",
             p."BYear",
             p."BSem",
             p."Dept",
             p."Regulation",
             string_agg(p."SubCode"::text, ','::text) AS "RegisteredSubjects"
      FROM ((SELECT "BTStudentInfo"."RegNo",
                    reg_status."AYear",
                    reg_status."ASem",
                    reg_status."BYear",
                    reg_status."BSem",
                    reg_status."Dept",
                    reg_status."Regulation",
                    sreg.sub_id
			        
             FROM "BTStudentRegistrations_Staging" sreg join "BTRollLists_Staging" on sreg."student_id" = "BTRollLists_Staging"."id" join "BTStudentInfo" on "BTRollLists_Staging"."student_id"="BTStudentInfo"."id"
                      JOIN "BTRegistration_Status" reg_status ON sreg."RegEventId" = reg_status.id
             WHERE reg_status."Mode"::text = 'R'::text
                OR reg_status."Mode"::text = 'D'::text) sreg_status
          JOIN (select bts."id" as "id",bts."RegEventId_id" as "RegEventId_id",btc."SubCode" as "SubCode",btc."SubName" as "SubName" from "BTSubjects" bts JOIN "BTCourses" btc on bts."course_id"=btc."id" order by "SubCode") subs ON sreg_status.sub_id = subs.id) p
      GROUP BY p."RegNo", p."AYear", p."ASem", p."BYear", p."BSem", p."Dept", p."Regulation") q,
     (SELECT "BTStudentInfo"."RegNo",
             "BTStudentInfo"."RollNo",
             "BTStudentInfo"."Name"
      FROM "BTStudentInfo") r
WHERE q."RegNo" = r."RegNo";

alter table "BTRegularRegistrationSummaryV" owner to postgres;


CREATE MATERIALIZED VIEW "BTStudentSGPAs_StagingMV" as 
SELECT "H"."RegNo",
    "H"."AYASBYBS_G",
    mod("H"."AYASBYBS_G", 100) AS "BYBS",
    sum("H"."GP") AS "SGP",
    sum("H"."Credits") AS "SC",
    round(sum("H"."GP")::numeric / NULLIF(sum("H"."Credits"), 0)::numeric, 2) AS "SGPA"
   FROM ( SELECT f."Ind",
            f."RegNo",
            f."AYASBYBS_G",
            f."AYASBYBS",
            f."SubCode",
            f."Grade",
            f."Credits",
            f."Points",
            f."GP"
           FROM ( SELECT row_number() OVER (PARTITION BY "G"."RegNo", "G"."AYASBYBS_G", "G"."SubCode" ORDER BY "G"."RegNo", "G"."AYASBYBS_G", "G"."SubCode", "G"."AYASBYBS" DESC) AS "Ind",
                    "G"."RegNo",
                    "G"."AYASBYBS_G",
                    "G"."AYASBYBS",
                    "G"."SubCode",
                    "G"."Grade",
                    "G"."Credits",
                    "G"."Points",
                    "G"."GP"
                   FROM ( SELECT "BTStudentPresentPastResults_StagingMV".id,
                            "BTStudentPresentPastResults_StagingMV"."RegNo",
                            "BTStudentPresentPastResults_StagingMV"."SubCode",
                            "BTStudentPresentPastResults_StagingMV"."SubName",
                            "BTStudentPresentPastResults_StagingMV"."AYear",
                            "BTStudentPresentPastResults_StagingMV"."ASem",
                            "BTStudentPresentPastResults_StagingMV"."BYear",
                            "BTStudentPresentPastResults_StagingMV"."BSem",
                            "BTStudentPresentPastResults_StagingMV"."OfferedYear",
                            "BTStudentPresentPastResults_StagingMV"."Dept",
                            "BTStudentPresentPastResults_StagingMV"."Grade",
                            "BTStudentPresentPastResults_StagingMV"."AttGrade",
                            "BTStudentPresentPastResults_StagingMV"."Regulation",
                            "BTStudentPresentPastResults_StagingMV"."Credits",
                            "BTStudentPresentPastResults_StagingMV"."Points",
                            "BTStudentPresentPastResults_StagingMV"."GP",
                            "BTStudentPresentPastResults_StagingMV"."AYASBYBS",
                            "BTStudentPresentPastResults_StagingMV"."AYASBYBS_G"
                           FROM "BTStudentPresentPastResults_StagingMV") "G") f
          WHERE f."Ind" <= 1) "H"
  GROUP BY "H"."RegNo", "H"."AYASBYBS_G";

REFRESH MATERIALIZED VIEW public."BTStudentSGPAs_StagingMV" WITH DATA;



create materialized view if not exists "BTStudentSGPAsMV" as
SELECT "H"."RegNo",
       "H"."AYASBYBS_G",
       mod("H"."AYASBYBS_G"::int, 100)                                                AS "BYBS",
       sum("H"."GP")                                                             AS "SGP",
       sum("H"."Credits")                                                        AS "SC",
       round(sum("H"."GP")::numeric / NULLIF(sum("H"."Credits"), 0)::numeric, 2) AS "SGPA"
FROM (SELECT f."Ind",
             f."RegNo",
             f."AYASBYBS_G",
             f."AYASBYBS",
             f."SubCode",
             f."Grade",
             f."Credits",
             f."Points",
             f."GP"
      FROM (SELECT row_number()
                   OVER (PARTITION BY "G"."RegNo", "G"."AYASBYBS_G", "G"."SubCode" ORDER BY "G"."RegNo", "G"."AYASBYBS_G", "G"."SubCode", "G"."AYASBYBS" DESC) AS "Ind",
                   "G"."RegNo",
                   "G"."AYASBYBS_G",
                   "G"."AYASBYBS",
                   "G"."SubCode",
                   "G"."Grade",
                   "G"."Credits",
                   "G"."Points",
                   "G"."GP"
            FROM (SELECT "BTStudentPresentPastResultsMV".id,
                         "BTStudentPresentPastResultsMV"."RegNo",
                         "BTStudentPresentPastResultsMV"."SubCode",
                         "BTStudentPresentPastResultsMV"."SubName",
                         "BTStudentPresentPastResultsMV"."AYear",
                         "BTStudentPresentPastResultsMV"."ASem",
                         "BTStudentPresentPastResultsMV"."BYear",
                         "BTStudentPresentPastResultsMV"."BSem",
                         "BTStudentPresentPastResultsMV"."OfferedYear",
                         "BTStudentPresentPastResultsMV"."Dept",
                         "BTStudentPresentPastResultsMV"."Grade",
                         "BTStudentPresentPastResultsMV"."AttGrade",
                         "BTStudentPresentPastResultsMV"."Regulation",
                         "BTStudentPresentPastResultsMV"."Credits",
                         "BTStudentPresentPastResultsMV"."Points",
                         "BTStudentPresentPastResultsMV"."GP",
                         "BTStudentPresentPastResultsMV"."AYASBYBS",
                         "BTStudentPresentPastResultsMV"."AYASBYBS_G"
                  FROM "BTStudentPresentPastResultsMV") "G") f
      WHERE f."Ind" <= 1) "H"
GROUP BY "H"."RegNo", "H"."AYASBYBS_G";

alter materialized view "BTStudentSGPAsMV" owner to postgres;

REFRESH MATERIALIZED VIEW public."BTStudentSGPAsMV" WITH DATA;






CREATE MATERIALIZED VIEW "BTStudentCGPAs_StagingMV" as 
 SELECT row_number() OVER (ORDER BY cgpa."RegNo", cgpa."AYASBYBS_G") AS id,
    cgpa."RegNo",
    cgpa."AYASBYBS_G",
    cgpa."CGP",
    cgpa."CC",
    cgpa."CGPA",
    sgpa."SGP",
    sgpa."SC",
    sgpa."SGPA"
   FROM ( SELECT "U"."RegNo",
            "U"."AYASBYBS_G",
            sum("U"."SGP") AS "CGP",
            sum("U"."SC") AS "CC",
            round(sum("U"."SGP") / NULLIF(sum("U"."SC"), 0::numeric), 2) AS "CGPA"
           FROM ( SELECT "T"."RegNo",
                    "T"."AYASBYBS_G",
                    "T"."AYASBYBS_G_S",
                    "T"."SGP",
                    "T"."SC",
                    "T"."Ind"
                   FROM ( SELECT "R"."RegNo",
                            "R"."AYASBYBS_G",
                            "S"."AYASBYBS_G" AS "AYASBYBS_G_S",
                            "S"."SGP",
                            "S"."SC",
                            row_number() OVER (PARTITION BY "R"."RegNo", "R"."AYASBYBS_G", "S"."BYBS" ORDER BY "R"."RegNo", "R"."AYASBYBS_G", "S"."AYASBYBS_G" DESC) AS "Ind"
                           FROM "BTStudentSGPAs_StagingMV" "R",
                            "BTStudentSGPAs_StagingMV" "S"
                          WHERE "R"."RegNo" = "S"."RegNo" AND "R"."AYASBYBS_G" >= "S"."AYASBYBS_G" AND "R"."BYBS" >= "S"."BYBS") "T"
                  WHERE "T"."Ind" <= 1) "U"
          GROUP BY "U"."RegNo", "U"."AYASBYBS_G") cgpa
     JOIN "BTStudentSGPAs_StagingMV" sgpa USING ("RegNo", "AYASBYBS_G");

REFRESH MATERIALIZED VIEW public."BTStudentCGPAs_StagingMV" WITH DATA;


create materialized view "BTStudentCGPAsMV" as
SELECT row_number() OVER (ORDER BY cgpa."RegNo", cgpa."AYASBYBS_G") AS id,
       cgpa."RegNo",
       cgpa."AYASBYBS_G",
       cgpa."CGP",
       cgpa."CC",
       cgpa."CGPA",
       sgpa."SGP",
       sgpa."SC",
       sgpa."SGPA"
FROM (SELECT "U"."RegNo",
             "U"."AYASBYBS_G",
             sum("U"."SGP")                                               AS "CGP",
             sum("U"."SC")                                                AS "CC",
             round(sum("U"."SGP") / NULLIF(sum("U"."SC"), 0::numeric), 2) AS "CGPA"
      FROM (SELECT "T"."RegNo",
                   "T"."AYASBYBS_G",
                   "T"."AYASBYBS_G_S",
                   "T"."SGP",
                   "T"."SC",
                   "T"."Ind"
            FROM (SELECT "R"."RegNo",
                         "R"."AYASBYBS_G",
                         "S"."AYASBYBS_G"                                                                                                            AS "AYASBYBS_G_S",
                         "S"."SGP",
                         "S"."SC",
                         row_number()
                         OVER (PARTITION BY "R"."RegNo", "R"."AYASBYBS_G", "S"."BYBS" ORDER BY "R"."RegNo", "R"."AYASBYBS_G", "S"."AYASBYBS_G" DESC) AS "Ind"
                  FROM "BTStudentSGPAsMV" "R",
                       "BTStudentSGPAsMV" "S"
                  WHERE "R"."RegNo" = "S"."RegNo"
                    AND "R"."AYASBYBS_G" >= "S"."AYASBYBS_G"
                    AND "R"."BYBS" >= "S"."BYBS") "T"
            WHERE "T"."Ind" <= 1) "U"
      GROUP BY "U"."RegNo", "U"."AYASBYBS_G") cgpa
         JOIN "BTStudentSGPAsMV" sgpa USING ("RegNo", "AYASBYBS_G");

alter materialized view "BTStudentCGPAsMV" owner to postgres;
REFRESH MATERIALIZED VIEW public."BTStudentCGPAsMV" WITH DATA;



CREATE MATERIALIZED VIEW public."BTDeptExamEventsMV"
AS
SELECT ROW_NUMBER() over( order by ("Dept","AYASBYBS")) as id, * from (
SELECT DISTINCT "BTStudentGradePointsMV"."Dept",
    "BTStudentGradePointsMV"."AYASBYBS",
    "BTStudentGradePointsMV"."BYear",
    "BTStudentGradePointsMV"."BSem"
   FROM "BTStudentGradePointsMV"
) as S
WITH NO DATA;


REFRESH MATERIALIZED VIEW public."BTDeptExamEventsMV" WITH DATA;

CREATE MATERIALIZED VIEW public."BTDeptExamEventStudentsMV"
AS
SELECT row_number() OVER (ORDER BY (ROW(s."Dept", s."AYASBYBS", s."RegNo"))) AS id,
    s."Dept",
    s."AYASBYBS",
    s."BYear",
    s."BSem",
    s."RegNo",
    s."RollNo",
    s."Name"
   FROM ( SELECT DISTINCT "BTStudentGradePointsMV"."Dept",
            "BTStudentGradePointsMV"."AYASBYBS",
            "BTStudentGradePointsMV"."BYear",
            "BTStudentGradePointsMV"."BSem",
            "BTStudentGradePointsMV"."RegNo",
            "BTStudentInfo"."RollNo",
            "BTStudentInfo"."Name"
           FROM "BTStudentGradePointsMV",
            "BTStudentInfo"
          WHERE "BTStudentInfo"."RegNo" = "BTStudentGradePointsMV"."RegNo") s;


REFRESH MATERIALIZED VIEW public."BTDeptExamEventStudentsMV" WITH DATA;

create or replace view "BTStudentExcessSubjectsV" as 
select * from (
select ROW_NUMBER() over (partition by "RegNo" Order by "RegNo","GP" desc, "SubCode") as "RNK",
						  * from "BTStudentGradePointsMV" 
						  where "Category"='DEC' and "GP">0) as g 
						  where "RNK">(select "NumberOfSubjects" from "BTMandatoryCredits" as m, "BTStudentInfo" as s
									   where "m"."Regulation" = s."Regulation" and s."RegNo" =g."RegNo"); 



create or replace view "BTStudentBestGradesV" as
select sgp.*,sgp."BYear"*10+sgp."BSem" as "BYBS", CASE when ses."RegNo" is NULL THEN 1 ELSE 0 END as "Required" from "BTStudentGradePointsMV" as sgp LEFT OUTER JOIN "BTStudentExcessSubjectsV" ses 
	ON sgp."RegNo" = ses."RegNo" and sgp."SubCode"=ses."SubCode" where sgp."GP">0;



create or replace view "BTStudentFinalSGPAsV" as 
SELECT ROW_NUMBER() over (order by "RegNo","BYBS") as id, sbgv."RegNo",
    sbgv."BYBS",
    sum(sbgv."GP" * sbgv."Required") AS "SGP",
    sum(sbgv."Credits" * sbgv."Required") AS "SC",
    round(sum(sbgv."GP" * sbgv."Required")::numeric / NULLIF(sum(sbgv."Credits" * sbgv."Required")::numeric, 0::numeric), 2) AS "SGPA"
   FROM "BTStudentBestGradesV" sbgv
  GROUP BY sbgv."RegNo", sbgv."BYBS";

create or replace view "BTStudentFinalCGPAV" as 
select ROW_NUMBER() Over (order by "RegNo") as id, "RegNo", sum(sbgv."SGP") as "CGP", sum(sbgv."SC") as "TotalCredits", 
		round(sum(sbgv."SGP")/NULLIF(sum(sbgv."SC"),0::numeric),2) as "CGPA" 
		from "BTStudentFinalSGPAsV" as sbgv
		group by "RegNo";


create or replace view "BTSubjectsOrderV" as
SELECT btc."SubCode",
    btrs."AYear" as "OfferedYear",
    btrs."Dept",
    btrs."Regulation",
        CASE
            WHEN btcs."Type"::text = 'THEORY'::text THEN 1
            WHEN btcs."Type"::text = 'LAB'::text THEN 2
            ELSE 3
        END AS "Order"
   FROM "BTSubjects" s join "BTRegistration_Status" btrs on s."RegEventId_id" = btrs."id" join "BTCourses" btc on s."course_id"=btc."id" join "BTCourseStructure" btcs on btc."CourseStructure_id"=btcs."id";



create or replace view "BTStudentGradePointsV" as
SELECT sgp.id,
    sgp."RegNo",
    sgp."SubCode",
    sgp."SubName",
    sgp."Grade",
    sgp."Credits",
    sgp."AYASBYBS",
    sgp."Type",
    so."Order"
   FROM "BTStudentGradePointsMV" sgp,
    "BTSubjectsOrderV" so
  WHERE sgp."SubCode"::text = so."SubCode"::text AND sgp."OfferedYear" = so."OfferedYear" AND sgp."Dept" = so."Dept" AND sgp."Regulation" = so."Regulation"
  ORDER BY sgp."AYASBYBS", sgp."RegNo", so."Order", sgp."SubCode";



Create View public."BTStudentMakeupBacklogsVsRegistrationsV" AS
 SELECT row_number() OVER (PARTITION BY s."RegNo" ORDER BY s."RegNo") AS id,
    s."RegNo",
    s."RollNo",
    s."Name",
    s."BYear",
    s."Dept",
    s."MakeupSubjects",
    s."RegisteredSubjects"
   FROM ( SELECT p."RegNo",
            r."RollNo",
            r."Name",
            p."BYear",
            p."Dept",
            p."MakeupSubjects",
            q."RegisteredSubjects"
           FROM ( SELECT "BTStudentMakeupBacklogsMV"."RegNo",
                    "BTStudentMakeupBacklogsMV"."BYear",
                    "BTStudentMakeupBacklogsMV"."Dept",
                    string_agg("BTStudentMakeupBacklogsMV"."SubCode"::text, ','::text) AS "MakeupSubjects"
                   FROM "BTStudentMakeupBacklogsMV"
                  GROUP BY "BTStudentMakeupBacklogsMV"."RegNo", "BTStudentMakeupBacklogsMV"."BYear", "BTStudentMakeupBacklogsMV"."Dept") p,
            ( SELECT btsr."RegNo",
                    btrs."BYear",
                    btrs."Dept",
                    string_agg(btsub."SubCode"::text, ','::text) AS "RegisteredSubjects"
                   FROM ("BTStudentRegistrations"  join "BTRollLists" on "BTStudentRegistrations"."student_id"="BTRollLists"."id" join "BTStudentInfo" on "BTRollLists"."student_id"="BTStudentInfo"."id")btsr, "BTRegistration_Status" btrs, (select "BTCourses"."SubCode","BTSubjects"."id" from "BTSubjects" join "BTCourses" on "BTSubjects"."course_id" = "BTCourses".id)btsub  where btsr."RegEventId" = btrs."id" and
                   btsr."sub_id" = btsub."id" and
                   btrs."ASem" = 3
                  GROUP BY btsr."RegNo", btrs."BYear", btrs."Dept") q,
            ( SELECT "BTStudentInfo"."RegNo",
                    "BTStudentInfo"."RollNo",
                    "BTStudentInfo"."Name"
                   FROM "BTStudentInfo") r
          WHERE p."RegNo" = q."RegNo" AND p."RegNo" = r."RegNo" AND p."BYear" = q."BYear" AND p."Dept" = q."Dept") s;











create or replace view "BTStudentCreditsCompletionInfoV" as 
Select cgp.id, std.*, fsc."FailedSubjectCount", "PassedCredits", "CGPA",
		"Sem-I","Sem-II","Sem-III","Sem-IV", 
		"Sem-V","Sem-VI","Sem-VII", "Sem-VIII", 
		"PCC","BSC","HSC","ESC","DEC","PRC","OPC","MDC", "EPC"  from 
	(select "RegNo","RollNo","Name" from "BTStudentInfo") as std JOIN
(select "RegNo", SUM(CASE WHEN ("Points"=0) THEN 1 ELSE 0 END) as "FailedSubjectCount",
		SUM(CASE WHEN(("Points">0) and ("Creditable"=1)) THEN "Credits" ELSE 0 END) as "PassedCredits"
		from "BTStudentGradePointsMV"  
		group by "RegNo") as fsc USING("RegNo") JOIN 
	(select * from "BTStudentFinalCGPAV") as cgp USING("RegNo") JOIN 

(Select "RegNo", SUM(CASE WHEN "BYBS"=11 THEN "Credits" ELSE 0 END) as "Sem-I",
				SUM (CASE WHEN "BYBS"=12 THEN "Credits" ELSE 0 END) as "Sem-II",
				SUM (CASE WHEN "BYBS"=21 THEN "Credits" ELSE 0 END) as "Sem-III", 
				SUM (CASE WHEN "BYBS"=22 THEN "Credits" ELSE 0 END) as "Sem-IV",
				SUM (CASE WHEN "BYBS"=31 THEN "Credits" ELSE 0 END) as "Sem-V",
				SUM (CASE WHEN "BYBS"=32 THEN "Credits" ELSE 0 END) as "Sem-VI",
				SUM (CASE WHEN "BYBS"=41 THEN "Credits" ELSE 0 END) as "Sem-VII",
				SUM (CASE WHEN "BYBS"=42 THEN "Credits" ELSE 0 END) as "Sem-VIII"
				from	
(select "RegNo", "BYBS", 
		SUM(CASE WHEN ("Creditable" > 0) and ("Points">0) THEN "Credits" ELSE 0 END) as "Credits" 
		from  "BTStudentBestGradesV" 
		group by "RegNo", "BYBS") as g 
		group by "RegNo") as "SemCredits" using ("RegNo") Join (	

select "RegNo", 
		SUM(CASE WHEN "Points">0 and "Category"='DEC' THEN "Credits" ELSE 0 END) as "DEC",
		SUM(CASE WHEN "Points">0 and "Category"='PCC' THEN "Credits" ELSE 0 END) as "PCC",
		SUM(CASE WHEN "Points">0 and "Category"='BSC' THEN "Credits" ELSE 0 END) as "BSC",
		SUM(CASE WHEN "Points">0 and "Category"='HSC' THEN "Credits" ELSE 0 END) as "HSC",
		SUM(CASE WHEN "Points">0 and "Category"='ESC' THEN "Credits" ELSE 0 END) as "ESC",
		SUM(CASE WHEN "Points">0 and "Category"='OPC' THEN "Credits" ELSE 0 END) as "OPC",
		SUM(CASE WHEN "Points">0 and "Category"='PRC' THEN "Credits" ELSE 0 END) as "PRC",
		SUM(CASE WHEN "Points">0 and "Category"='MDC' THEN "Credits" ELSE 0 END) as "MDC",
		SUM(CASE WHEN "Points">0 and "Category"='EPC' THEN "Credits" ELSE 0 END) as "EPC"
		from "BTStudentBestGradesV" 
		group by "RegNo"
		order by "RegNo") as "CatCredits" using ("RegNo");








create materialized view "BTStudentGradesTestMV" as
select "RegId", 
"RegEventId", 
case 
when "RegId" in (select "Registration_id" from "BTAttendance_Shortage") then 'R'
when "RegId" in (select "Registration_id" from "BTIXGradeStudents") then (select "Grade" from "BTIXGradeStudents" where "Registration_id"="RegId")
else "Grade"
end "Grade"
from
(select row_number() over (order by(row(marks."id", grthr."Threshold_Mark"))desc) as id, 
marks."id" as "RegId", 
marks."RegEventId",
grthr."Grade",
grthr."Mode", 
grthr."Threshold_Mark"  from 
(select btsr."id", 
btsr."RegEventId", 
btsr."sub_id", 
btms."TotalMarks", 
btsr."Mode" 
from "BTStudentRegistrations" btsr, "BTMarks_Staging" btms 
where btsr."id"=btms."Registration_id") marks, 
(select btgt."Threshold_Mark", 
btgt."RegEventId_id", 
btgt."Subject_id", 
btgp."Grade",
case 
when btgt."Exam_Mode" then 0
else 1
end "Mode"
from 
"BTGradesThreshold" btgt, "BTGradePoints" btgp where btgt."Grade_id"=btgp."id" order by btgt."Threshold_Mark")grthr
where marks."RegEventId"=grthr."RegEventId_id" and marks."sub_id"=grthr."Subject_id" and marks."Mode"=grthr."Mode" and marks."TotalMarks">=grthr."Threshold_Mark")btg
where id=1;
REFRESH MATERIALIZED VIEW public."BTStudentGradesTestMV" WITH DATA;























create materialized view "BTStudentGradesMV" as
select "RegId", 
"RegEventId", 
case 
when "RegId" in (select "Registration_id" from "BTAttendance_Shortage") then 'R'
when "RegId" in (select "Registration_id" from "BTIXGradeStudents") then (select "Grade" from "BTIXGradeStudents" where "Registration_id"="RegId")
else 
case 
when "TotalMarks">="G1" then
  case 
  when "Regulation"=2.0 then 'S'
  else 'EX'
  end
when "TotalMarks">="G2" then 'A'
when "TotalMarks">="G3" then 'B'
when "TotalMarks">="G4" then 'C'
when "TotalMarks">="G5" then 'D'
when "TotalMarks">="G6" then
  case
  when "Regulation"=2.0 then 'E'
  else 'P'
  end
when "TotalMarks">="G7" and "Regulation"=2.0 then 'P'
else 'F'
end
end "Grade"
from
(select btsr."id" as "RegId", 
btsr."RegEventId", 
btsr."sub_id", 
btms."TotalMarks", 
btsr."Mode" 
from "BTStudentRegistrations" btsr, "BTMarks_Staging" btms 
where btsr."id"=btms."Registration_id") marks, 
(select 
btgt."RegEventId_id",
btgp."Regulation",
btgt."Subject_id", 
case
when btgt."Exam_Mode" then 0
else 1
end "Mode",
sum(case when "Grade"='EX' or "Grade"='S' then "Threshold_Mark" else 0 end) as "G1",
sum(case when "Grade"='A' then "Threshold_Mark" else 0 end) as "G2",
sum(case when "Grade"='B' then "Threshold_Mark" else 0 end) as "G3",
sum(case when "Grade"='C' then "Threshold_Mark" else 0 end) as "G4",
sum(case when "Grade"='D' then "Threshold_Mark" else 0 end) as "G5",
sum(case when "Grade"='E' or "Grade"='P' then "Threshold_Mark" else 0 end) as "G6",
sum(case when "Grade"='P' then "Threshold_Mark" else 0 end) as "G7"
from 
"BTGradesThreshold" btgt, "BTGradePoints" btgp where btgt."Grade_id"=btgp."id" 
group by btgt."RegEventId_id", btgt."Subject_id", btgp."Regulation",btgt."Exam_Mode"
)grthr
where marks."RegEventId"=grthr."RegEventId_id" and marks."sub_id"=grthr."Subject_id" and marks."Mode"=grthr."Mode"
;
REFRESH MATERIALIZED VIEW public."BTStudentGradesMV" WITH DATA;















create materialized view "BTStudentGradeDetailsMV" as
select btsrgs."RegNo",
btrs."AYear",
btrs."ASem",
btrs."BYear",
btrs."BSem",
btrs."Regulation",
btrs."Dept",
btrs."Mode",
btsrgs."SubCode",
btsrgs."SubName",
btsrgs."Grade"
from (select btsrg."RegNo", 
btsrg."Grade",
bts."SubCode",
bts."SubName",
btsrg."RegEventId"
from (select btsg."Grade",
btsr."RegNo",
btsg."RegEventId",
btsr."sub_id" from
"BTStudentGradesMV" btsg join (select "BTStudentRegistrations"."id","BTStudentInfo"."RegNo","BTStudentRegistrations"."sub_id" from "BTStudentRegistrations" join "BTRollLists" on "BTStudentRegistrations"."student_id"="BTRollLists"."id" join "BTStudentInfo" on "BTRollLists"."student_id"="BTStudentInfo"."id" )btsr on 
btsg."RegEventId"=btsr."id")btsrg join (select "BTCourses"."SubCode","BTCourses"."SubName","BTSubjects"."id" FROM "BTSubjects" join "BTCourses" on "BTSubjects"."course_id" = "BTCourses".id) bts
on btsrg."sub_id"=bts."id")btsrgs
 join "BTRegistration_Status" btrs on btrs."id"=btsrgs."RegEventId";

REFRESH MATERIALIZED VIEW public."BTStudentGradeDetailsMV" WITH DATA;


create or replace view "BTRegistrationDetailsV" as 
select sr."id",
       rs."AYear",
       rs."ASem",
       rs."BYear",
       rs."BSem",
       rs."Dept",
       rs."Regulation",
       rs."Mode",
       btc."SubCode",
       sr."Mode" as "RMode",
       bts."RegNo",
       bts."RollNo",
       bts."Name",
       sr."sub_id",
       sr."RegEventId",
       btc."SubName",
       btcs."Credits",
       btcs."Category",
       hi."HeldInMonth",
       hi."HeldInYear"
from "BTStudentRegistrations" sr join "BTSubjects" sub on sub."id"=sr."sub_id"
join "BTRegistration_Status" rs on sr."RegEventId"=rs."id"
join "BTCourses" btc on sub."course_id"=btc."id"
join "BTCourseStructure" btcs on btc."CourseStructure_id"=btcs."id"
join "BTRollLists" btr on sr."student_id"=btr."id"
join "BTStudentInfo" bts on bts."id"=btr."student_id"
join "BTHeldIn" hi on rs."AYear"=hi."AYear" and rs."ASem"=hi."ASem" and rs."BYear"=hi."BYear" and rs."BSem"=hi."BSem";

create or replace view "BTStudentSubjectMarkDetailsV" as
SELECT ms.id,
    rs."AYear",
    rs."ASem",
    rs."BYear",
    rs."BSem",
    rs."Regulation",
    rs."Dept",
    rs.id AS "RegEventId",
    rs."Mode",
    sub.id AS "SubId",
    btc."SubCode",
    sr."Mode" AS "RMode",
    md."Distribution",
    md."DistributionNames",
    btc."DistributionRatio",
    bts."RegNo",
    ms."Marks",
    ms."TotalMarks",
    ms."Registration_id"
   FROM "BTMarks_Staging" ms
     JOIN "BTStudentRegistrations" sr ON ms."Registration_id" = sr.id
     JOIN "BTSubjects" sub ON sr.sub_id = sub.id
     join "BTCourses" btc on sub."course_id" = btc."id"
     JOIN "BTRegistration_Status" rs ON rs.id = sr."RegEventId"
     JOIN "BTMarksDistribution" md ON btc."MarkDistribution_id" = md.id
     join "BTRollLists" btr on btr."id"=sr."student_id"
     join "BTStudentInfo" bts on bts."id"=btr."student_id";



CREATE OR REPLACE VIEW public."BTStudentGradeDetailsV"
 AS
 SELECT row_number() OVER () AS id,
    a."RegNo",
    a."AYear",
    a."ASem",
    a."BYear",
    a."BSem",
    a."Mode",
    a."Dept",
    a."Regulation",
    a."SubCode",
    a."Grade"
   FROM ( SELECT btsgrs."RegNo",
            btsgrs."AYear",
            btsgrs."ASem",
            btsgrs."BYear",
            btsgrs."BSem",
            btsgrs."Mode",
            btsgrs."Dept",
            btsgrs."Regulation",
            btc."SubCode",
            btsgrs."Grade"
           FROM ( SELECT btsgr."RegNo",
                    btsgr.sub_id,
                    btsgr."RegEventId",
                    btsgr."Grade",
                    btrs.id,
                    btrs."AYear",
                    btrs."ASem",
                    btrs."BYear",
                    btrs."BSem",
                    btrs."Regulation",
                    btrs."Dept",
                    btrs."Mode",
                    btrs."Status",
                    btrs."RollListStatus",
                    btrs."RollListFeeStatus",
                    btrs."RegistrationStatus",
                    btrs."MarksStatus",
                    btrs."GradeStatus"
                   FROM ( SELECT btst."RegNo",
                            btsr.sub_id,
                            btsr."RegEventId",
                            btsg."Grade"
                           FROM "BTStudentGrades_Staging" btsg
                             JOIN "BTStudentRegistrations" btsr ON btsg."RegId" = btsr.id
                             join "BTRollLists" btr on btr."id"=btsr."student_id"
                             join "BTStudentInfo" btst on btst."id"=btr."student_id") btsgr
                     JOIN "BTRegistration_Status" btrs ON btsgr."RegEventId" = btrs.id) btsgrs
             JOIN "BTSubjects" bts ON bts.id = btsgrs.sub_id
             join "BTCourses" btc on btc."id"=bts."course_id") a;

CREATE OR REPLACE VIEW public."BTGradeThresholdDetailsV"
 AS
 SELECT row_number() OVER () AS id,
    tv."AYear",
    tv."ASem",
    tv."BYear",
    tv."BSem",
    tv."Regulation",
    tv."Mode",
    tv."Dept",
    tv."RegEventId",
    tv."SubCode",
    max(
        CASE
            WHEN tv."Grade"::text = 'EX'::text OR tv."Grade"::text = 'S'::text THEN tv."Threshold_Mark"
            ELSE 0::double precision
        END) AS "G1",
    max(
        CASE
            WHEN tv."Grade"::text = 'A'::text THEN tv."Threshold_Mark"
            ELSE 0::double precision
        END) AS "G2",
    max(
        CASE
            WHEN tv."Grade"::text = 'B'::text THEN tv."Threshold_Mark"
            ELSE 0::double precision
        END) AS "G3",
    max(
        CASE
            WHEN tv."Grade"::text = 'C'::text THEN tv."Threshold_Mark"
            ELSE 0::double precision
        END) AS "G4",
    max(
        CASE
            WHEN tv."Grade"::text = 'D'::text THEN tv."Threshold_Mark"
            ELSE 0::double precision
        END) AS "G5",
    max(
        CASE
            WHEN tv."Grade"::text = 'E'::text OR tv."Grade"::text = 'P'::text THEN tv."Threshold_Mark"
            ELSE 0::double precision
        END) AS "G6",
    max(
        CASE
            WHEN tv."Grade"::text = 'P'::text THEN tv."Threshold_Mark"
            ELSE 0::double precision
        END) AS "G7"
   FROM ( SELECT gt."Threshold_Mark",
            gp."Grade",
            btc."SubCode",
            rs."AYear",
            rs."ASem",
            rs."BYear",
            rs."BSem",
            rs."Regulation",
            rs."Dept",
            rs.id AS "RegEventId",
            rs."Mode"
           FROM "BTGradesThreshold" gt
             JOIN "BTGradePoints" gp ON gt."Grade_id" = gp.id
             JOIN "BTSubjects" sub ON gt."Subject_id" = sub.id
             join "BTCourses" btc on btc."id" = sub."course_id"
             JOIN "BTRegistration_Status" rs ON rs.id = gt."RegEventId_id") tv
  GROUP BY tv."AYear", tv."ASem", tv."BYear", tv."BSem", tv."Regulation", tv."Dept", tv."Mode", tv."RegEventId", tv."SubCode";



CREATE OR REPLACE VIEW public."BTSubjectInfoV"
 AS
 SELECT row_number() OVER () AS id,
    rs."AYear",
    rs."ASem",
    rs."BYear",
    rs."BSem",
    rs."Dept",
    rs."Regulation",
    rs."Mode",
    sub.id AS "SubId",
    btc."SubCode",
    btc."SubName",
    btcs."Credits",
    btc."OfferedBy",
    btcs."Type",
    btcs."Category",
    btc."DistributionRatio",
    md."Distribution",
    md."DistributionNames",
    md."PromoteThreshold"
   FROM "BTSubjects" sub
     JOIN "BTRegistration_Status" rs ON sub."RegEventId_id" = rs.id
     join "BTCourses" btc on sub."course_id"=btc."id"
     join "BTCourseStructure" btcs on btc."CourseStructure_id"=btcs."id"
	 JOIN "BTMarksDistribution" md ON btc."MarkDistribution_id" = md.id;