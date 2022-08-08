create materialized view "MTStudentGradePointsMV" as
SELECT row_number() OVER (ORDER BY (ROW (g."RegNo", g."AYASMYMS", g."SubName"))) AS id,
       g."RegNo",
       g.sub_id,
       g."SubCode",
       g."SubName",
       g."AYear",
       g."ASem",
       g."MYear",
       g."MSem",
       g."OfferedYear",
       g."Dept",
       g."Grade",
       g."AttGrade",
       g."Regulation",
       g."Creditable",
       g."Credits",
       g."Type",
       g."Category",
       g."Points",
       g."GP",
       g."AYASMYMS"
FROM (SELECT final_table."RegNo",
             final_table.sub_id,
             final_table."SubCode",
             final_table."SubName",
             final_table."AYear",
             final_table."ASem",
             final_table."MYear",
             final_table."MSem",
             final_table."OfferedYear",
             final_table."Dept",
             final_table."Grade",
             final_table."AttGrade",
             final_table."Regulation",
             final_table."Creditable",
             final_table."Credits",
             final_table."Type",
             final_table."Category",
             final_table."Points",
             final_table."Credits" * final_table."Points" * final_table."Creditable"                                AS "GP",
             ((final_table."AYear" * 10 + final_table."ASem") * 10 + final_table."MYear") * 10 +
             final_table."MSem"                                                                                     AS "AYASMYMS"
      FROM (((SELECT sg_reg."Regulation",
                     sg_reg."Grade",
                     sg_reg."AttGrade",
                     sg_reg."RegNo",
                     sg_reg."AYear",
                     sg_reg."ASem",
                     sg_reg."MYear",
                     sg_reg.sub_id,
                     "MTGradePoints"."Points"
              FROM (((SELECT "MTStudentGrades"."Grade",
                             "MTStudentGrades"."AttGrade",
                             "MTStudentGrades"."RegId",
                             "MTStudentGrades"."RegEventId"
                      FROM "MTStudentGrades") sg
                  JOIN (SELECT "MTStudentRegistrations"."RegNo",
                               "MTStudentRegistrations".sub_id,
                               "MTStudentRegistrations".id
                        FROM "MTStudentRegistrations") sreg ON sg."RegId" = sreg.id) sg_regs
                  JOIN "MTRegistration_Status" ON "MTRegistration_Status".id = sg_regs."RegEventId") sg_reg("Grade",
                                                                                                        "AttGrade",
                                                                                                        "RegId",
                                                                                                        "RegEventId",
                                                                                                        "RegNo", sub_id,
                                                                                                        id, id_1,
                                                                                                        "AYear", "ASem",
                                                                                                        "MYear", "MSem",
                                                                                                        "Regulation",
                                                                                                        "Dept", "Mode",
                                                                                                        "Status",
                                                                                                        "RegistrationStatus",
                                                                                                        "MarksStatus",
                                                                                                        "GradeStatus",
                                                                                                        "RollListStatus",
                                                                                                        "RollListFeeStatus")
                       JOIN "MTGradePoints" ON sg_reg."Regulation" = "MTGradePoints"."Regulation" AND
                                             sg_reg."Grade"::text = "MTGradePoints"."Grade"::text) gp_table
          JOIN "MTSubjects" subs ON gp_table.sub_id = subs.id) grades
          JOIN (SELECT "MTRegistration_Status".id,
                       "MTRegistration_Status"."AYear" AS "OfferedYear",
                       "MTRegistration_Status"."Dept",
                       "MTRegistration_Status"."MSem"
                FROM "MTRegistration_Status") rg_status ON grades."RegEventId_id" = rg_status.id) final_table("Regulation",
                                                                                                            "Grade",
                                                                                                            "AttGrade",
                                                                                                            "RegNo",
                                                                                                            "AYear",
                                                                                                            "ASem",
                                                                                                            "MYear",
                                                                                                            sub_id,
                                                                                                            "Points",
                                                                                                            id,
                                                                                                            "SubCode",
                                                                                                            "SubName",
                                                                                                            "Creditable",
                                                                                                            "Credits",
                                                                                                            "Type",
                                                                                                            "Category",
                                                                                                            "OfferedBy",
                                                                                                            "ProgrammeCode",
                                                                                                            "DistributionRatio",
                                                                                                            "MarkDistribution_id",
                                                                                                            "RegEventId_id",
                                                                                                            id_1,
                                                                                                            "OfferedYear",
                                                                                                            "Dept",
                                                                                                            "MSem")) g;

alter materialized view "MTStudentGradePointsMV" owner to postgres;

REFRESH MATERIALIZED VIEW public."MTStudentGradePointsMV" WITH DATA;


create materialized view "MTStudentGradePoints_StagingMV" as
SELECT row_number() OVER (ORDER BY (ROW (g."RegNo", g."AYASMYMS", g."SubName"))) AS id,
       g."RegNo",
       g.sub_id,
       g."SubCode",
       g."SubName",
       g."AYear",
       g."ASem",
       g."MYear",
       g."MSem",
       g."OfferedYear",
       g."Dept",
       g."Grade",
       g."AttGrade",
       g."Regulation",
       g."Creditable",
       g."Credits",
       g."Type",
       g."Category",
       g."Points",
       g."GP",
       g."AYASMYMS"
FROM (SELECT final_table."RegNo",
             final_table.sub_id,
             final_table."SubCode",
             final_table."SubName",
             final_table."AYear",
             final_table."ASem",
             final_table."MYear",
             final_table."MSem",
             final_table."OfferedYear",
             final_table."Dept",
             final_table."Grade",
             final_table."AttGrade",
             final_table."Regulation",
             final_table."Creditable",
             final_table."Credits",
             final_table."Type",
             final_table."Category",
             final_table."Points",
             final_table."Credits" * final_table."Points" * final_table."Creditable"                                AS "GP",
             ((final_table."AYear" * 10 + final_table."ASem") * 10 + final_table."MYear") * 10 +
             final_table."MSem"                                                                                     AS "AYASMYMS"
      FROM (((SELECT sg_reg."Regulation",
                     sg_reg."Grade",
                     sg_reg."AttGrade",
                     sg_reg."RegNo",
                     sg_reg."AYear",
                     sg_reg."ASem",
                     sg_reg."MYear",
                     sg_reg.sub_id,
                     "MTGradePoints"."Points"
              FROM (((SELECT "MTStudentGrades_Staging"."Grade",
                             "MTStudentGrades_Staging"."AttGrade",
                             "MTStudentGrades_Staging"."RegId",
                             "MTStudentGrades_Staging"."RegEventId"
                      FROM "MTStudentGrades_Staging") sg
                  JOIN (SELECT "MTStudentRegistrations"."RegNo",
                               "MTStudentRegistrations".sub_id,
                               "MTStudentRegistrations".id
                        FROM "MTStudentRegistrations") sreg ON sg."RegId" = sreg.id) sg_regs
                  JOIN "MTRegistration_Status" ON "MTRegistration_Status".id = sg_regs."RegEventId") sg_reg("Grade",
                                                                                                        "AttGrade",
                                                                                                        "RegId",
                                                                                                        "RegEventId",
                                                                                                        "RegNo", sub_id,
                                                                                                        id, id_1,
                                                                                                        "AYear", "ASem",
                                                                                                        "MYear", "MSem",
                                                                                                        "Regulation",
                                                                                                        "Dept", "Mode",
                                                                                                        "Status",
                                                                                                        "RegistrationStatus",
                                                                                                        "MarksStatus",
                                                                                                        "GradeStatus",
                                                                                                        "RollListStatus",
                                                                                                        "RollListFeeStatus")
                       JOIN "MTGradePoints" ON sg_reg."Regulation" = "MTGradePoints"."Regulation" AND
                                             sg_reg."Grade"::text = "MTGradePoints"."Grade"::text) gp_table
          JOIN "MTSubjects" subs ON gp_table.sub_id = subs.id) grades
          JOIN (SELECT "MTRegistration_Status".id,
                       "MTRegistration_Status"."AYear" AS "OfferedYear",
                       "MTRegistration_Status"."Dept",
                       "MTRegistration_Status"."MSem"
                FROM "MTRegistration_Status") rg_status ON grades."RegEventId_id" = rg_status.id) final_table("Regulation",
                                                                                                            "Grade",
                                                                                                            "AttGrade",
                                                                                                            "RegNo",
                                                                                                            "AYear",
                                                                                                            "ASem",
                                                                                                            "MYear",
                                                                                                            sub_id,
                                                                                                            "Points",
                                                                                                            id,
                                                                                                            "SubCode",
                                                                                                            "SubName",
                                                                                                            "Creditable",
                                                                                                            "Credits",
                                                                                                            "Type",
                                                                                                            "Category",
                                                                                                            "OfferedBy",
                                                                                                            "ProgrammeCode",
                                                                                                            "DistributionRatio",
                                                                                                            "MarkDistribution_id",
                                                                                                            "RegEventId_id",
                                                                                                            id_1,
                                                                                                            "OfferedYear",
                                                                                                            "Dept",
                                                                                                            "MSem")) g;

alter materialized view "MTStudentGradePoints_StagingMV" owner to postgres;
REFRESH MATERIALIZED VIEW public."MTStudentGradePoints_StagingMV" WITH DATA;


create materialized view "MTStudentBacklogsMV" as
SELECT row_number() OVER (ORDER BY "P"."RegNo", "P"."SubCode") AS id,
       "P"."RegNo",
       "P".sub_id,
       "P"."SubCode",
       "P"."SubName",
       "P"."Credits",
       "P"."MYear",
       "P"."MSem",
       "P"."GP",
       "P"."Regulation",
       "P"."Grade",
       "P"."Dept",
       "P"."OfferedYear",
       "P"."AYASMYMS"
FROM (SELECT "Q"."RegNo",
             "Q".sub_id,
             "Q"."SubCode",
             "Q"."SubName",
             "Q"."Credits",
             "Q"."MYear",
             "Q"."MSem",
             "Q"."GP",
             "Q"."Regulation",
             "Q"."Grade",
             "Q"."Dept",
             "Q"."OfferedYear",
             "Q"."AYASMYMS",
             row_number()
             OVER (PARTITION BY "Q"."RegNo", "Q"."SubCode" ORDER BY "Q"."RegNo", "Q"."SubCode", "Q"."AYASMYMS" DESC) AS "RNK"
      FROM "MTStudentGradePointsMV" "Q",
           "MTStudentInfo" "S"
      WHERE "Q"."RegNo" = "S"."RegNo") "P"
WHERE "P"."RNK" = 1
  AND ("P"."Grade"::text = ANY
       (ARRAY ['F'::character varying::text, 'R'::character varying::text, 'I'::character varying::text, 'X'::character varying::text]));

alter materialized view "MTStudentBacklogsMV" owner to postgres;
REFRESH MATERIALIZED VIEW public."MTStudentBacklogsMV" WITH DATA;


create materialized view "MTStudentMakeupBacklogsMV" as
SELECT row_number() OVER (ORDER BY "P"."RegNo", "P"."SubCode") AS id,
       "P"."RegNo",
       "P".sub_id,
       "P"."SubCode",
       "P"."SubName",
       "P"."Regulation",
       "P"."Credits",
       "P"."MYear",
       "P"."MSem",
       "P"."GP",
       "P"."RNK",
       "P"."Grade",
       "P"."Dept",
       "P"."OfferedYear",
       "P"."AYASMYMS"
FROM (SELECT "Q"."RegNo",
             "Q".sub_id,
             "Q"."SubCode",
             "Q"."SubName",
             "Q"."Regulation",
             "Q"."Credits",
             "Q"."MYear",
             "Q"."MSem",
             "Q"."GP",
             "Q"."Grade",
             "Q"."Dept",
             "Q"."OfferedYear",
             "Q"."AYASMYMS",
             row_number()
             OVER (PARTITION BY "Q"."RegNo", "Q"."SubCode" ORDER BY "Q"."RegNo", "Q"."SubCode", "Q"."AYASMYMS" DESC) AS "RNK"
      FROM "MTStudentGradePointsMV" "Q",
           "MTStudentInfo" "S"
      WHERE "Q"."RegNo" = "S"."RegNo") "P"
WHERE "P"."RNK" = 1
  AND ("P"."Grade"::text = ANY
       (ARRAY ['F'::character varying::text, 'I'::character varying::text, 'X'::character varying::text]));

alter materialized view "MTStudentMakeupBacklogsMV" owner to postgres;
REFRESH MATERIALIZED VIEW public."MTStudentMakeupBacklogsMV" WITH DATA;


create materialized view "MTStudentExamEventsMV" as
SELECT "SS".id,
       "SS"."RegNo",
       "SS"."AYASMYMS",
       "SS"."MYear",
       "SS"."MSem",
       CASE
           WHEN "SS".bybscount > 1 THEN 0
           ELSE 1
           END AS "IsRegular"
FROM (SELECT row_number() OVER (ORDER BY s."RegNo", s."AYASMYMS")                                            AS id,
             s."RegNo",
             s."AYASMYMS",
             s."MYear",
             s."MSem",
             s."MYMS",
             row_number()
             OVER (PARTITION BY s."RegNo", s."MYMS" ORDER BY s."RegNo", s."MYMS", s."AYASMYMS")              AS bybscount
      FROM (SELECT DISTINCT "MTStudentGradePointsMV"."RegNo",
                            "MTStudentGradePointsMV"."AYASMYMS",
                            "MTStudentGradePointsMV"."MYear",
                            "MTStudentGradePointsMV"."MSem",
                            mod("MTStudentGradePointsMV"."AYASMYMS", 100) AS "MYMS"
            FROM "MTStudentGradePointsMV") s) "SS";

alter materialized view "MTStudentExamEventsMV" owner to postgres;

REFRESH MATERIALIZED VIEW public."MTStudentExamEventsMV" WITH DATA;


create materialized view "MTStudentPresentPastResultsMV" as
SELECT row_number() OVER (ORDER BY (ROW (aa."RegNo", aa."AYASMYMS", aa."AYASMYMS_G"))) AS id,
       aa."RegNo",
       aa."SubCode",
       aa."SubName",
       aa."AYear",
       aa."ASem",
       aa."MYear",
       aa."MSem",
       aa."OfferedYear",
       aa."Dept",
       aa."Grade",
       aa."AttGrade",
       aa."Regulation",
       aa."Credits",
       aa."Points",
       aa."GP",
       aa."AYASMYMS",
       aa."AYASMYMS_G"
FROM (SELECT "MTStudentGradePointsMV"."RegNo",
             "MTStudentGradePointsMV"."SubCode",
             "MTStudentGradePointsMV"."SubName",
             "MTStudentGradePointsMV"."AYear",
             "MTStudentGradePointsMV"."ASem",
             "MTStudentGradePointsMV"."MYear",
             "MTStudentGradePointsMV"."MSem",
             "MTStudentGradePointsMV"."OfferedYear",
             "MTStudentGradePointsMV"."Dept",
             "MTStudentGradePointsMV"."Grade",
             "MTStudentGradePointsMV"."AttGrade",
             "MTStudentGradePointsMV"."Regulation",
             "MTStudentGradePointsMV"."Credits" * "MTStudentGradePointsMV"."Creditable" AS "Credits",
             "MTStudentGradePointsMV"."Points",
             "MTStudentGradePointsMV"."GP",
             "MTStudentGradePointsMV"."AYASMYMS",
             "MTStudentExamEventsMV"."AYASMYMS"                                       AS "AYASMYMS_G"
      FROM "MTStudentGradePointsMV",
           "MTStudentExamEventsMV"
      WHERE "MTStudentGradePointsMV"."AYASMYMS" <= "MTStudentExamEventsMV"."AYASMYMS"
        AND "MTStudentGradePointsMV"."MYear" = "MTStudentExamEventsMV"."MYear"
        AND "MTStudentGradePointsMV"."MSem" = "MTStudentExamEventsMV"."MSem"
        AND "MTStudentGradePointsMV"."RegNo" = "MTStudentExamEventsMV"."RegNo") aa;

alter materialized view "MTStudentPresentPastResultsMV" owner to postgres;

REFRESH MATERIALIZED VIEW public."MTStudentPresentPastResultsMV" WITH DATA;


create materialized view "MTStudentExamEvents_StagingMV" as
SELECT "SS".id,
       "SS"."RegNo",
       "SS"."AYASMYMS",
       "SS"."MYear",
       "SS"."MSem",
       CASE
           WHEN "SS".bybscount > 1 THEN 0
           ELSE 1
           END AS "IsRegular"
FROM (SELECT row_number() OVER (ORDER BY s."RegNo", s."AYASMYMS")                                            AS id,
             s."RegNo",
             s."AYASMYMS",
             s."MYear",
             s."MSem",
             s."MYMS",
             row_number()
             OVER (PARTITION BY s."RegNo", s."MYMS" ORDER BY s."RegNo", s."MYMS", s."AYASMYMS")              AS bybscount
      FROM (SELECT DISTINCT "MTStudentGradePoints_StagingMV"."RegNo",
                            "MTStudentGradePoints_StagingMV"."AYASMYMS",
                            "MTStudentGradePoints_StagingMV"."MYear",
                            "MTStudentGradePoints_StagingMV"."MSem",
                            mod("MTStudentGradePoints_StagingMV"."AYASMYMS", 100) AS "MYMS"
            FROM "MTStudentGradePoints_StagingMV") s) "SS";

alter materialized view "MTStudentExamEvents_StagingMV" owner to postgres;

REFRESH MATERIALIZED VIEW public."MTStudentExamEvents_StagingMV" WITH DATA;


create materialized view "MTStudentPresentPastResults_StagingMV" as
SELECT row_number() OVER (ORDER BY (ROW (aa."RegNo", aa."AYASMYMS", aa."AYASMYMS_G"))) AS id,
       aa."RegNo",
       aa."SubCode",
       aa."SubName",
       aa."AYear",
       aa."ASem",
       aa."MYear",
       aa."MSem",
       aa."OfferedYear",
       aa."Dept",
       aa."Grade",
       aa."AttGrade",
       aa."Regulation",
       aa."Credits",
       aa."Points",
       aa."GP",
       aa."AYASMYMS",
       aa."AYASMYMS_G"
FROM (SELECT "MTStudentGradePoints_StagingMV"."RegNo",
             "MTStudentGradePoints_StagingMV"."SubCode",
             "MTStudentGradePoints_StagingMV"."SubName",
             "MTStudentGradePoints_StagingMV"."AYear",
             "MTStudentGradePoints_StagingMV"."ASem",
             "MTStudentGradePoints_StagingMV"."MYear",
             "MTStudentGradePoints_StagingMV"."MSem",
             "MTStudentGradePoints_StagingMV"."OfferedYear",
             "MTStudentGradePoints_StagingMV"."Dept",
             "MTStudentGradePoints_StagingMV"."Grade",
             "MTStudentGradePoints_StagingMV"."AttGrade",
             "MTStudentGradePoints_StagingMV"."Regulation",
             "MTStudentGradePoints_StagingMV"."Credits" * "MTStudentGradePoints_StagingMV"."Creditable" AS "Credits",
             "MTStudentGradePoints_StagingMV"."Points",
             "MTStudentGradePoints_StagingMV"."GP",
             "MTStudentGradePoints_StagingMV"."AYASMYMS",
             "MTStudentExamEvents_StagingMV"."AYASMYMS"                                               AS "AYASMYMS_G"
      FROM "MTStudentGradePoints_StagingMV",
           "MTStudentExamEvents_StagingMV"
      WHERE "MTStudentGradePoints_StagingMV"."AYASMYMS" <= "MTStudentExamEvents_StagingMV"."AYASMYMS"
        AND "MTStudentGradePoints_StagingMV"."MYear" = "MTStudentExamEvents_StagingMV"."MYear"
        AND "MTStudentGradePoints_StagingMV"."MSem" = "MTStudentExamEvents_StagingMV"."MSem"
        AND "MTStudentGradePoints_StagingMV"."RegNo" = "MTStudentExamEvents_StagingMV"."RegNo") aa;

alter materialized view "MTStudentPresentPastResults_StagingMV" owner to postgres;

REFRESH MATERIALIZED VIEW public."MTStudentPresentPastResults_StagingMV" WITH DATA;



create view "MTRegularRegistrationSummaryV"(id, "RegNo", "Name", "MYear", "MSem", "Dept", "AYear", "ASem", "Regulation", "RegisteredSubjects") as
SELECT row_number() OVER () AS id,
       q."RegNo",
       r."Name",
       q."MYear",
       q."MSem",
       q."Dept",
       q."AYear",
       q."ASem",
       q."Regulation",
       q."RegisteredSubjects"
FROM (SELECT p."RegNo",
             p."AYear",
             p."ASem",
             p."MYear",
             p."MSem",
             p."Dept",
             p."Regulation",
             string_agg(p."SubCode"::text, ','::text) AS "RegisteredSubjects"
      FROM ((SELECT sreg."RegNo",
                    reg_status."AYear",
                    reg_status."ASem",
                    reg_status."MYear",
                    reg_status."MSem",
                    reg_status."Dept",
                    reg_status."Regulation",
                    sreg.sub_id
             FROM "MTStudentRegistrations_Staging" sreg
                      JOIN "MTRegistration_Status" reg_status ON sreg."RegEventId" = reg_status.id
             WHERE reg_status."Mode"::text = 'R'::text
                OR reg_status."Mode"::text = 'D'::text) sreg_status
          JOIN "MTSubjects" subs ON sreg_status.sub_id = subs.id) p
      GROUP BY p."RegNo", p."AYear", p."ASem", p."MYear", p."MSem", p."Dept", p."Regulation") q,
     (SELECT "MTStudentInfo"."RegNo",
             "MTStudentInfo"."Name"
      FROM "MTStudentInfo") r
WHERE q."RegNo" = r."RegNo";

alter table "MTRegularRegistrationSummaryV" owner to postgres;

create view "MTBacklogRegistrationSummaryV"(id, "RegNo", "Name", "MYear", "MSem", "Dept", "AYear", "ASem", "Regulation", "RegisteredSubjects") as
SELECT row_number() OVER () AS id,
       q."RegNo",
       r."Name",
       q."MYear",
       q."MSem",
       q."Dept",
       q."AYear",
       q."ASem",
       q."Regulation",
       q."RegisteredSubjects"
FROM (SELECT p."RegNo",
             p."AYear",
             p."ASem",
             p."MYear",
             p."MSem",
             p."Dept",
             p."Regulation",
             string_agg(p."SubCode"::text, ','::text) AS "RegisteredSubjects"
      FROM ((SELECT sreg."RegNo",
                    reg_status."AYear",
                    reg_status."ASem",
                    reg_status."MYear",
                    reg_status."MSem",
                    reg_status."Dept",
                    reg_status."Regulation",
                    sreg.sub_id
             FROM "MTStudentRegistrations_Staging" sreg
                      JOIN "MTRegistration_Status" reg_status ON sreg."RegEventId" = reg_status.id
             WHERE reg_status."Mode"::text = 'B'::text) sreg_status
          JOIN "MTSubjects" subs ON sreg_status.sub_id = subs.id) p
      GROUP BY p."RegNo", p."AYear", p."ASem", p."MYear", p."MSem", p."Dept", p."Regulation") q,
     (SELECT "MTStudentInfo"."RegNo",
             "MTStudentInfo"."Name"
      FROM "MTStudentInfo") r
WHERE q."RegNo" = r."RegNo";

alter table "MTBacklogRegistrationSummaryV" owner to postgres;

create view "MTMakeupRegistrationSummaryV"(id, "RegNo", "Name", "MYear", "MSem", "Dept", "AYear", "ASem", "Regulation", "RegisteredSubjects") as
SELECT row_number() OVER () AS id,
       q."RegNo",
       r."Name",
       q."MYear",
       q."MSem",
       q."Dept",
       q."AYear",
       q."ASem",
       q."Regulation",
       q."RegisteredSubjects"
FROM (SELECT p."RegNo",
             p."AYear",
             p."ASem",
             p."MYear",
             p."MSem",
             p."Dept",
             p."Regulation",
             string_agg(p."SubCode"::text, ','::text) AS "RegisteredSubjects"
      FROM ((SELECT sreg."RegNo",
                    reg_status."AYear",
                    reg_status."ASem",
                    reg_status."MYear",
                    reg_status."MSem",
                    reg_status."Dept",
                    reg_status."Regulation",
                    sreg.sub_id
             FROM "MTStudentRegistrations_Staging" sreg
                      JOIN "MTRegistration_Status" reg_status ON sreg."RegEventId" = reg_status.id
             WHERE reg_status."Mode"::text = 'M'::text) sreg_status
          JOIN "MTSubjects" subs ON sreg_status.sub_id = subs.id) p
      GROUP BY p."RegNo", p."AYear", p."ASem", p."MYear", p."MSem", p."Dept", p."Regulation") q,
     (SELECT "MTStudentInfo"."RegNo",
             "MTStudentInfo"."Name"
      FROM "MTStudentInfo") r
WHERE q."RegNo" = r."RegNo";

alter table "MTMakeupRegistrationSummaryV" owner to postgres;


create materialized view "MTStudentSGPAsMV" as
SELECT "H"."RegNo",
       "H"."AYASMYMS_G",
       mod("H"."AYASMYMS_G", 100)                                                AS "MYMS",
       sum("H"."GP")                                                             AS "SGP",
       sum("H"."Credits")                                                        AS "SC",
       round(sum("H"."GP")::numeric / NULLIF(sum("H"."Credits"), 0)::numeric, 2) AS "SGPA"
FROM (SELECT f."Ind",
             f."RegNo",
             f."AYASMYMS_G",
             f."AYASMYMS",
             f."SubCode",
             f."Grade",
             f."Credits",
             f."Points",
             f."GP"
      FROM (SELECT row_number()
                   OVER (PARTITION BY "G"."RegNo", "G"."AYASMYMS_G", "G"."SubCode" ORDER BY "G"."RegNo", "G"."AYASMYMS_G", "G"."SubCode", "G"."AYASMYMS" DESC) AS "Ind",
                   "G"."RegNo",
                   "G"."AYASMYMS_G",
                   "G"."AYASMYMS",
                   "G"."SubCode",
                   "G"."Grade",
                   "G"."Credits",
                   "G"."Points",
                   "G"."GP"
            FROM (SELECT "MTStudentPresentPastResultsMV".id,
                         "MTStudentPresentPastResultsMV"."RegNo",
                         "MTStudentPresentPastResultsMV"."SubCode",
                         "MTStudentPresentPastResultsMV"."SubName",
                         "MTStudentPresentPastResultsMV"."AYear",
                         "MTStudentPresentPastResultsMV"."ASem",
                         "MTStudentPresentPastResultsMV"."MYear",
                         "MTStudentPresentPastResultsMV"."MSem",
                         "MTStudentPresentPastResultsMV"."OfferedYear",
                         "MTStudentPresentPastResultsMV"."Dept",
                         "MTStudentPresentPastResultsMV"."Grade",
                         "MTStudentPresentPastResultsMV"."AttGrade",
                         "MTStudentPresentPastResultsMV"."Regulation",
                         "MTStudentPresentPastResultsMV"."Credits",
                         "MTStudentPresentPastResultsMV"."Points",
                         "MTStudentPresentPastResultsMV"."GP",
                         "MTStudentPresentPastResultsMV"."AYASMYMS",
                         "MTStudentPresentPastResultsMV"."AYASMYMS_G"
                  FROM "MTStudentPresentPastResultsMV") "G") f
      WHERE f."Ind" <= 1) "H"
GROUP BY "H"."RegNo", "H"."AYASMYMS_G";

alter materialized view "MTStudentSGPAsMV" owner to postgres;

REFRESH MATERIALIZED VIEW public."MTStudentSGPAsMV" WITH DATA;


create materialized view "MTStudentSGPAs_StagingMV" as
SELECT "H"."RegNo",
       "H"."AYASMYMS_G",
       mod("H"."AYASMYMS_G", 100)                                                AS "MYMS",
       sum("H"."GP")                                                             AS "SGP",
       sum("H"."Credits")                                                        AS "SC",
       round(sum("H"."GP")::numeric / NULLIF(sum("H"."Credits"), 0)::numeric, 2) AS "SGPA"
FROM (SELECT f."Ind",
             f."RegNo",
             f."AYASMYMS_G",
             f."AYASMYMS",
             f."SubCode",
             f."Grade",
             f."Credits",
             f."Points",
             f."GP"
      FROM (SELECT row_number()
                   OVER (PARTITION BY "G"."RegNo", "G"."AYASMYMS_G", "G"."SubCode" ORDER BY "G"."RegNo", "G"."AYASMYMS_G", "G"."SubCode", "G"."AYASMYMS" DESC) AS "Ind",
                   "G"."RegNo",
                   "G"."AYASMYMS_G",
                   "G"."AYASMYMS",
                   "G"."SubCode",
                   "G"."Grade",
                   "G"."Credits",
                   "G"."Points",
                   "G"."GP"
            FROM (SELECT "MTStudentPresentPastResults_StagingMV".id,
                         "MTStudentPresentPastResults_StagingMV"."RegNo",
                         "MTStudentPresentPastResults_StagingMV"."SubCode",
                         "MTStudentPresentPastResults_StagingMV"."SubName",
                         "MTStudentPresentPastResults_StagingMV"."AYear",
                         "MTStudentPresentPastResults_StagingMV"."ASem",
                         "MTStudentPresentPastResults_StagingMV"."MYear",
                         "MTStudentPresentPastResults_StagingMV"."MSem",
                         "MTStudentPresentPastResults_StagingMV"."OfferedYear",
                         "MTStudentPresentPastResults_StagingMV"."Dept",
                         "MTStudentPresentPastResults_StagingMV"."Grade",
                         "MTStudentPresentPastResults_StagingMV"."AttGrade",
                         "MTStudentPresentPastResults_StagingMV"."Regulation",
                         "MTStudentPresentPastResults_StagingMV"."Credits",
                         "MTStudentPresentPastResults_StagingMV"."Points",
                         "MTStudentPresentPastResults_StagingMV"."GP",
                         "MTStudentPresentPastResults_StagingMV"."AYASMYMS",
                         "MTStudentPresentPastResults_StagingMV"."AYASMYMS_G"
                  FROM "MTStudentPresentPastResults_StagingMV") "G") f
      WHERE f."Ind" <= 1) "H"
GROUP BY "H"."RegNo", "H"."AYASMYMS_G";

alter materialized view "MTStudentSGPAs_StagingMV" owner to postgres;

REFRESH MATERIALIZED VIEW public."MTStudentSGPAs_StagingMV" WITH DATA;


create materialized view "MTStudentCGPAs_StagingMV" as
SELECT row_number() OVER (ORDER BY cgpa."RegNo", cgpa."AYASMYMS_G") AS id,
       cgpa."RegNo",
       cgpa."AYASMYMS_G",
       cgpa."CGP",
       cgpa."CC",
       cgpa."CGPA",
       sgpa."SGP",
       sgpa."SC",
       sgpa."SGPA"
FROM (SELECT "U"."RegNo",
             "U"."AYASMYMS_G",
             sum("U"."SGP")                                               AS "CGP",
             sum("U"."SC")                                                AS "CC",
             round(sum("U"."SGP") / NULLIF(sum("U"."SC"), 0::numeric), 2) AS "CGPA"
      FROM (SELECT "T"."RegNo",
                   "T"."AYASMYMS_G",
                   "T"."AYASMYMS_G_S",
                   "T"."SGP",
                   "T"."SC",
                   "T"."Ind"
            FROM (SELECT "R"."RegNo",
                         "R"."AYASMYMS_G",
                         "S"."AYASMYMS_G"                                                                                                            AS "AYASMYMS_G_S",
                         "S"."SGP",
                         "S"."SC",
                         row_number()
                         OVER (PARTITION BY "R"."RegNo", "R"."AYASMYMS_G", "S"."MYMS" ORDER BY "R"."RegNo", "R"."AYASMYMS_G", "S"."AYASMYMS_G" DESC) AS "Ind"
                  FROM "MTStudentSGPAs_StagingMV" "R",
                       "MTStudentSGPAs_StagingMV" "S"
                  WHERE "R"."RegNo" = "S"."RegNo"
                    AND "R"."AYASMYMS_G" >= "S"."AYASMYMS_G"
                    AND "R"."MYMS" >= "S"."MYMS") "T"
            WHERE "T"."Ind" <= 1) "U"
      GROUP BY "U"."RegNo", "U"."AYASMYMS_G") cgpa
         JOIN "MTStudentSGPAs_StagingMV" sgpa USING ("RegNo", "AYASMYMS_G");

alter materialized view "MTStudentCGPAs_StagingMV" owner to postgres;

REFRESH MATERIALIZED VIEW public."MTStudentCGPAs_StagingMV" WITH DATA;


create materialized view "MTStudentCGPAsMV" as
SELECT row_number() OVER (ORDER BY cgpa."RegNo", cgpa."AYASMYMS_G") AS id,
       cgpa."RegNo",
       cgpa."AYASMYMS_G",
       cgpa."CGP",
       cgpa."CC",
       cgpa."CGPA",
       sgpa."SGP",
       sgpa."SC",
       sgpa."SGPA"
FROM (SELECT "U"."RegNo",
             "U"."AYASMYMS_G",
             sum("U"."SGP")                                               AS "CGP",
             sum("U"."SC")                                                AS "CC",
             round(sum("U"."SGP") / NULLIF(sum("U"."SC"), 0::numeric), 2) AS "CGPA"
      FROM (SELECT "T"."RegNo",
                   "T"."AYASMYMS_G",
                   "T"."AYASMYMS_G_S",
                   "T"."SGP",
                   "T"."SC",
                   "T"."Ind"
            FROM (SELECT "R"."RegNo",
                         "R"."AYASMYMS_G",
                         "S"."AYASMYMS_G"                                                                                                            AS "AYASMYMS_G_S",
                         "S"."SGP",
                         "S"."SC",
                         row_number()
                         OVER (PARTITION BY "R"."RegNo", "R"."AYASMYMS_G", "S"."MYMS" ORDER BY "R"."RegNo", "R"."AYASMYMS_G", "S"."AYASMYMS_G" DESC) AS "Ind"
                  FROM "MTStudentSGPAsMV" "R",
                       "MTStudentSGPAsMV" "S"
                  WHERE "R"."RegNo" = "S"."RegNo"
                    AND "R"."AYASMYMS_G" >= "S"."AYASMYMS_G"
                    AND "R"."MYMS" >= "S"."MYMS") "T"
            WHERE "T"."Ind" <= 1) "U"
      GROUP BY "U"."RegNo", "U"."AYASMYMS_G") cgpa
         JOIN "MTStudentSGPAsMV" sgpa USING ("RegNo", "AYASMYMS_G");

alter materialized view "MTStudentCGPAsMV" owner to postgres;

REFRESH MATERIALIZED VIEW public."MTStudentCGPAsMV" WITH DATA;


CREATE MATERIALIZED VIEW public."MTDeptExamEventsMV"
AS
SELECT ROW_NUMBER() over( order by ("Dept","AYASMYMS")) as id, * from (
SELECT DISTINCT "MTStudentGradePointsMV"."Dept",
    "MTStudentGradePointsMV"."AYASMYMS",
    "MTStudentGradePointsMV"."MYear",
    "MTStudentGradePointsMV"."MSem"
   FROM "MTStudentGradePointsMV"
) as S
WITH NO DATA;


REFRESH MATERIALIZED VIEW public."MTDeptExamEventsMV" WITH DATA;


CREATE MATERIALIZED VIEW public."MTDeptExamEventStudentsMV"
AS
SELECT row_number() OVER (ORDER BY (ROW(s."Dept", s."AYASMYMS", s."RegNo"))) AS id,
    s."Dept",
    s."AYASMYMS",
    s."MYear",
    s."MSem",
    s."RegNo",
    s."Name"
   FROM ( SELECT DISTINCT "MTStudentGradePointsMV"."Dept",
            "MTStudentGradePointsMV"."AYASMYMS",
            "MTStudentGradePointsMV"."MYear",
            "MTStudentGradePointsMV"."MSem",
            "MTStudentGradePointsMV"."RegNo",
            "MTStudentInfo"."Name"
           FROM "MTStudentGradePointsMV",
            "MTStudentInfo"
          WHERE "MTStudentInfo"."RegNo" = "MTStudentGradePointsMV"."RegNo") s;


REFRESH MATERIALIZED VIEW public."MTDeptExamEventStudentsMV" WITH DATA;


create or replace view "MTSubjectsOrderV" as
SELECT s."SubCode",
    mtrs."AYear" as "OfferedYear",
    mtrs."Dept",
    mtrs."Regulation",
        CASE
            WHEN s."Type"::text = 'THEORY'::text THEN 1
            WHEN s."Type"::text = 'LAB'::text THEN 2
            ELSE 3
        END AS "Order"
   FROM "MTSubjects" s join "MTRegistration_Status" mtrs on s."RegEventId_id" = mtrs."id";

create or replace view "MTStudentGradePointsV" as
SELECT sgp.id,
    sgp."RegNo",
    sgp."SubCode",
    sgp."SubName",
    sgp."Grade",
    sgp."Credits",
    sgp."AYASMYMS",
    sgp."Type",
    so."Order"
   FROM "MTStudentGradePointsMV" sgp,
    "MTSubjectsOrderV" so
  WHERE sgp."SubCode"::text = so."SubCode"::text AND sgp."OfferedYear" = so."OfferedYear" AND sgp."Dept" = so."Dept" AND sgp."Regulation" = so."Regulation"
  ORDER BY sgp."AYASMYMS", sgp."RegNo", so."Order", sgp."SubCode";



Create View public."MTStudentMakeupBacklogsVsRegistrationsV" AS
 SELECT row_number() OVER (PARTITION BY s."RegNo" ORDER BY s."RegNo") AS id,
    s."RegNo",
    s."Name",
    s."MYear",
    s."Dept",
    s."MakeupSubjects",
    s."RegisteredSubjects"
   FROM ( SELECT p."RegNo",
            r."Name",
            p."MYear",
            p."Dept",
            p."MakeupSubjects",
            q."RegisteredSubjects"
           FROM ( SELECT "MTStudentMakeupBacklogsMV"."RegNo",
                    "MTStudentMakeupBacklogsMV"."MYear",
                    "MTStudentMakeupBacklogsMV"."Dept",
                    string_agg("MTStudentMakeupBacklogsMV"."SubCode"::text, ','::text) AS "MakeupSubjects"
                   FROM "MTStudentMakeupBacklogsMV"
                  GROUP BY "MTStudentMakeupBacklogsMV"."RegNo", "MTStudentMakeupBacklogsMV"."MYear", "MTStudentMakeupBacklogsMV"."Dept") p,
            ( SELECT mtsr."RegNo",
                    mtrs."MYear",
                    mtrs."Dept",
                    string_agg(mtsub."SubCode"::text, ','::text) AS "RegisteredSubjects"
                   FROM "MTStudentRegistrations" mtsr, "MTRegistration_Status" mtrs, "MTSubjects" mtsub where mtsr."RegEventId" = mtrs."id" and
                   mtsr."sub_id" = mtsub."id" and
                   mtrs."ASem" = 3
                  GROUP BY mtsr."RegNo", mtrs."MYear", mtrs."Dept") q,
            ( SELECT "MTStudentInfo"."RegNo",
                    "MTStudentInfo"."Name"
                   FROM "MTStudentInfo") r
          WHERE p."RegNo" = q."RegNo" AND p."RegNo" = r."RegNo" AND p."MYear" = q."MYear" AND p."Dept" = q."Dept") s;
