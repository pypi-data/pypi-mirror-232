/* serviceApportFact

Service Apportionment Factors
For Criteria of “Low Income Factor”, “Zero Numerator for Payroll Factor” (Note: sometimes ratios  do not appear and must be calculated, depending on the year of the reporting. See table below.)

-- 7020 - Seattle service payroll
-- 7021 - total companywide service payroll
-- 7022 - payroll factor
-- 7030 - Seattle service revenue
-- 7031 - total companywide service revenue
-- 7032 - revenue factor */

USE MODRPE

SELECT B.business_id,
    B.business_legal_name,
    TR.TaxReturnID,
    O.obl_year,
    O.obl_period,
    WS.WorksheetID,
    WS.FieldID,
    WS.FieldValue

FROM stg.TaxReturn AS TR
    INNER JOIN stg.obligation AS O ON O.obligation_id=TR.Obligation_ID
    INNER JOIN stg.TaxReturnWorksheet AS WS ON WS.TaxReturnID=TR.TaxReturnID
    INNER JOIN stg.business as B ON B.business_id=TR.Business_ID

WHERE -- O.obl_year='2020' AND
    WS.FieldID IN ('7020','7021','7022','7030','7031', '7032')
;
