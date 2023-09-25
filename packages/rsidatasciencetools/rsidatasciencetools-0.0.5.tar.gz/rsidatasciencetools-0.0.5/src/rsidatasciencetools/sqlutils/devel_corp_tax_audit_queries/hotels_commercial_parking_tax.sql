/* hotelPark

‘Hotels Paying Commercial Parking Tax’ 

Explanation: 
Taxpayers with NAICS codes for "Accommodations and Lodging" with zero KT obligations.
**Identify taxpayers with NAICS codes for "Accommodations and Lodging" associated 
with any branch. Remove those that have NO KT obligations at all or are reporting 
zero gross revenue on existing KT obligations.*/


-- STEP 1
USE MODRPE

;WITH accomodations AS (

	SELECT B.business_id, 
	   BL.bus_loc_id,
	   B.business_legal_name,
	   BL.dlis_branch_number,
	   BL.business_status_id,
	   BL.naics_code,
	   O.obligation_id,
	   O.obl_year,
	   O.obl_period,
	   O.obl_type_id,
	   -- OT.obl_type_code
	   O.paid_amt

	FROM stg.obligation AS O
	   INNER JOIN stg.BUSINESS_LOCATION AS BL ON O.bus_loc_id=BL.bus_loc_id
	   INNER JOIN stg.business AS B ON B.business_id=BL.business_id
	   -- INNER JOIN dbo.OBL_TYPE_CODE as OT ON O.obl_type_id=OT.obl_type_id


	WHERE  -- O.obl_year='2021' AND 
	   BL.naics_code LIKE '721%'
	   AND O.obl_source_code_id In (5,9,15)
	   AND O.obl_type_id In (10,133)
	   AND O.obl_source_code_id In (5,9,15)
	   AND (O.delq_excptn_cd_id Is Null Or O.delq_excptn_cd_id=10)
   
	GROUP BY B.business_id, 
	   BL.bus_loc_id,
	   B.business_legal_name,
	   BL.dlis_branch_number,
	   BL.business_status_id,
	   BL.naics_code,
	   O.obligation_id,
	   O.obl_year,
	   O.obl_period,
	   --  OT.obl_type_code
	   O.obl_type_id,
	   O.paid_amt

	-- ORDER BY B.business_id ASC
)

-- STEP 2

SELECT A.business_id, 
   A.bus_loc_id,
   A.business_legal_name,
   A.dlis_branch_number,
   A.business_status_id,
   A.naics_code,
   A.obligation_id,
   A.obl_year,
   A.obl_period,
   A.obl_type_id,
   -- A.obl_type_code,
   Sum(D.gross_amount) AS sum_of_gross_amount,
   Sum(D.taxable_amount) As sum_of_taxable_amount,
   Sum(D.tax_due_amount) AS sum_of_tax_due,
   A.paid_amt
      

FROM accomodations as A


LEFT JOIN stg.tax_detail_charge AS D ON A.obligation_id=D.obligation_id

-- WHERE  D.detail_date=(SELECT MAX(D.detail_date) FROM D)
WHERE D.detail_date=(SELECT MAX(Di.detail_date)  
                     FROM stg.tax_detail_charge AS Di  
                     WHERE Di.obligation_id=D.obligation_id)

GROUP BY A.business_id, 
   A.bus_loc_id,
   A.business_legal_name,
   A.dlis_branch_number,
   A.business_status_id,
   A.naics_code,
   A.obligation_id,
   A.obl_year,
   A.obl_period,
   A.obl_type_id,
   -- A.obl_type_code,
   D.gross_amount,
   D.taxable_amount,
   D.tax_due_amount,
   A.paid_amt
      
ORDER BY A.business_id ASC
;
