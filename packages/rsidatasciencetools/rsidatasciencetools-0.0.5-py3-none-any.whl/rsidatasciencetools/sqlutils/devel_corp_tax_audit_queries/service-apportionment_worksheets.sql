/* serviceApportWksh

QUERY #2 Tax Return - Advance/Reimb deduction claim - for Service Apportionment Worksheets
 
Explanation:
For querying the advance/reimbursement deduction claimed 
by service taxpayers on the service apportionment worksheet */


USE MODRPE
 
SELECT B.business_id,
    B.business_legal_name,
    O.obligation_id,
    O.obl_year,
    O.obl_period,
    TRW.worksheetid,
    TRW.FieldID,
    D.deduction_type_alpha,
    SUM(TRW.FieldValue) AS ttl_deduction
    -- TRWT.fieldtext

FROM stg.business B
INNER JOIN stg.BUSINESS_LOCATION AS BL ON B.business_id=BL.business_id
INNER JOIN stg.obligation AS O On  BL.bus_loc_id=O.bus_loc_id
INNER JOIN stg.TaxReturn AS TR ON O.obligation_id=TR.Obligation_ID
INNER JOIN stg.TaxReturnWorksheet AS TRW ON TR.TaxReturnId=TRW.TaxReturnID
-- INNER JOIN stg.TaxReturnWorksheetText AS TRWT ON TRW.TaxReturnID=TRWT.TaxReturnID
INNER JOIN stg.DEDUCTION_TYPE_CODE AS D ON TRW.FieldID=D.deduction_type_id
 
WHERE TRW.WorksheetId=8
AND (O.delq_excptn_cd_id IS NULL OR O.delq_excptn_cd_id=10)
-- AND O.obl_year=2020
AND TRW.FieldId=13
 
GROUP BY B.business_id,
    B.business_legal_name,
    O.obligation_id,
    O.obl_year,
    O.obl_period,
    TRW.worksheetid,
    TRW.FieldID,
    D.deduction_type_alpha
    -- TRWT.fieldtext
 
ORDER BY B.business_id
;