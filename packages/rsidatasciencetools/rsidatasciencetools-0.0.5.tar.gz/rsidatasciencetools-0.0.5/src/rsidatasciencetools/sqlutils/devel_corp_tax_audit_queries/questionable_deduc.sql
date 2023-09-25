/* questD
For Criteria of “Questionable Deductions”
For Criteria of “No Prior Audit” and “Last Audit Before 2013” */

USE MODRPE

SELECT B.business_id,
    -- A.date_assigned,
    O.obligation_id,
    O.obl_source_code_id,
    -- OC.obl_source_desc,
    -- OT.obl_type_code,
    O.original_amt,
    O.delq_excptn_cd_id

FROM stg.business AS B

-- INNER JOIN stg.audit AS A ON A.business_id=B.business_id
INNER JOIN stg.BUSINESS_LOCATION AS BL ON B.business_id=BL.business_id
INNER JOIN stg.obligation AS O ON BL.bus_loc_id=O.bus_loc_id
-- INNER JOIN stg.OBL_TYPE_CODE AS OT on A.obl_type_id=OT.obl_type_id
-- INNER JOIN stg.obl_source_code AS OC ON O.obl_source_code_id=OC.obl_source_code_id

WHERE O.obl_source_code_id IN (7,11) AND (
    O.delq_excptn_cd_id IS NULL or O.delq_excptn_cd_id=10)
-- AND A.date_assigned>'1/1/2013'

GROUP BY 
    -- A.business_id,
    B.business_id,
    -- A.date_assigned,
    O.obligation_id,
    O.obl_source_code_id,
    -- OC.obl_source_desc,
    O.obl_type_id,
    O.original_amt,
    O.delq_excptn_cd_id

-- ORDER BY A.date_assigned ASC
ORDER BY B.business_id ASC
;