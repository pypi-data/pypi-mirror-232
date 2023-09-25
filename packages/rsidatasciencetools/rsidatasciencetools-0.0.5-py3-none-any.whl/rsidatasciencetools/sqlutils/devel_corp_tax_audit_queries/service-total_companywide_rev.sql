/* cWideRev

TOTAL COMPANYWIDE SERVICE REVENUE FROM APPORTIONMENT WORKSHEETS
For Criteria of "Gross Sales" */


USE MODRPE

SELECT TR.Business_ID,
    B.business_id,
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
INNER JOIN stg.business AS B ON B.business_id=TR.Business_ID
WHERE -- O.obl_year='2020' AND
    WS.FieldId='7010'
;
