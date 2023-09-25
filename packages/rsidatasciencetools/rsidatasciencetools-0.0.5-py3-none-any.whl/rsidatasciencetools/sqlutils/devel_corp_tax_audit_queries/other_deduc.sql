/* otherD

“Other Deductions” with Explanatory Text
For Criteria of “Questionable Deductions” */


USE MODRPE

Select B.business_id,
    B.business_legal_name,
    O.obligation_id,
    O.obl_year,
    O.obl_period,
    TRDD.Classification_ID,
    TRDD.deduction_type_id,
    TRDD.DeductAmount,
    TRDD.DeductReason

FROM stg.business B

INNER JOIN stg.BUSINESS_LOCATION AS BL ON B.business_id=BL.business_id
INNER JOIN stg.obligation AS O ON BL.bus_loc_id=O.bus_loc_id
INNER JOIN stg.TaxReturn AS TR ON O.obligation_id=TR.obligation_id
INNER JOIN stg.TaxReturnDetailDeduct AS TRDD ON TR.TaxReturnID=TRDD.TaxReturnID

-- WHERE O.obl_year='2020' 

GROUP BY B.business_id,
    B.business_legal_name,
    O.obligation_id,
    O.obl_year,
    O.obl_period,
    TRDD.Classification_ID,
    TRDD.deduction_type_id,
    TRDD.DeductAmount,
    TRDD.DeductReason

ORDER BY TRDD.deductreason DESC
;
