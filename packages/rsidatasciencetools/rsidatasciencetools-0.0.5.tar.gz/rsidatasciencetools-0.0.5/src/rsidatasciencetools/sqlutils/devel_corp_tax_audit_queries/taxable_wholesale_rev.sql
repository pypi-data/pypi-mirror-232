/* taxWSrev

Taxable Wholesale Revenue
For Criteria of “Taxable Wholesale Revenue Over 50 Percent Total Taxable Revenue” */

USE MODRPE

SELECT B.business_id, 
	BL.bus_loc_id,
	B.business_legal_name,
	BL.dlis_branch_number,
	BL.business_status_id,
	BL.naics_code,
	O.obligation_id,
	O.obl_year,
	O.obl_period,
	D.classification_id,
	O.obl_type_id,
	--OT.obl_type_code,
	Sum(D.gross_amount) AS sum_of_gross_amount,
	Sum(D.taxable_amount) As sum_of_taxable_amount,
	Sum(D.tax_due_amount) AS sum_of_tax_due
	--NAICS.Description


FROM stg.obligation AS O
  INNER JOIN stg.tax_detail_charge AS D
                ON O.obligation_id = D.obligation_id
  INNER JOIN stg.BUSINESS_LOCATION AS BL 
                ON O.bus_loc_id = BL.bus_loc_id
  INNER JOIN stg.business AS B
                ON B.business_id = BL.business_id
  --INNER JOIN dbo.OBL_TYPE_CODE as OT ON O.obl_type_id=OT.obl_type_id
  --INNER JOIN NAICS ON BL.naics_code=NAICS.Code
  
WHERE -- O.obl_year='2019' AND O.obl_period='03' AND 
	D.classification_id=03
	AND O.obl_type_id = 10
	AND O.obl_source_code_id In (5,9,15)
	AND (O.delq_excptn_cd_id Is Null Or O.delq_excptn_cd_id=10)
	AND D.detail_date = (SELECT MAX(TDC.detail_date)
							FROM stg.tax_detail_charge AS TDC  
							--INNER JOIN O ON O.obligation_id
							WHERE TDC.obligation_id = D.obligation_id 
							--AND TDC.detail_date <= O.obl_due_date
						)


GROUP BY B.business_id, 
BL.bus_loc_id,
       B.business_legal_name,
	   BL.dlis_branch_number,
	   BL.business_status_id,
	   BL.naics_code,
	   O.obligation_id,
       O.obl_year,
	   D.classification_id,
	   O.obl_period,
	   -- OT.obl_type_code,
	   -- NAICS.Description,
	   O.obl_type_id

ORDER BY B.business_id ASC
;
