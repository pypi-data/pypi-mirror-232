/* TRapportWksh

QUERY #1 for Tax Returns claiming Adv/Reimb deduction for tax returns
 
Explanation:
for querying the advance/reimbursement deduction claimed on tax returns */


USE MODRPE
 
SELECT B.business_id, 
    B.business_legal_name, 
    O.obl_year,
    O.obl_period,
    O.obl_type_id,
    --OT.obl_type_code,
    D.classification_id,
    D.gross_amount,
    D.deduction_amount,
    I.deduction_type_id,
    DTC.deduction_type_desc
 
FROM stg.obligation AS O
    INNER JOIN stg.tax_detail_charge AS D ON O.obligation_id = D.obligation_id
    INNER JOIN stg.BUSINESS_LOCATION AS BL ON O.bus_loc_id = BL.bus_loc_id
    INNER JOIN stg.business AS B ON B.business_id = BL.business_id
    --INNER JOIN dbo.OBL_TYPE_CODE AS OT ON O.obl_type_id=OT.obl_type_id 
    INNER JOIN stg.ITEMIZED_DEDUCTION AS I ON D.tax_detail_chg_id=I.tax_detail_chg_id 
    INNER JOIN stg.DEDUCTION_TYPE_CODE AS DTC ON I.deduction_type_id=DTC.deduction_type_id
 
WHERE -- O.obl_year='2020' AND 
    O.obl_type_id=10  
    AND O.obl_source_code_id IN (5,9,15)
    AND I.deduction_type_id=13
    AND (O.delq_excptn_cd_id IS Null OR O.delq_excptn_cd_id=10)
    AND D.detail_date = (SELECT MAX(TDC.detail_date)  
                          FROM stg.tax_detail_charge AS TDC  
                          WHERE TDC.obligation_id = D.obligation_id)
 
GROUP BY B.business_id, 
    B.business_legal_name, 
    O.obl_year,
    O.obl_period,
    O.obl_type_id,
    --OT.obl_type_code,
    D.classification_id,
    D.gross_amount,
    D.deduction_amount,
    I.deduction_type_id,
    DTC.deduction_type_desc
 
ORDER BY B.business_id ASC
; 
