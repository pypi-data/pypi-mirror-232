/* naics

NAICS Codes
For Criteria of “Temporary Help NAICS Code”, “Travel Arrangements NAICS Codes”, “Direct Health and Medical Insurance NAICS Codes,” “Offices of Lawyers NAICS Code,” “Insurance Agencies NAICS Code,” (Note: See table below for codes.)

temporary help      - 561320
travel agencies     - 561510
all other travel arrangement and reservation services - 524210
offices of lawyers  - 541110
insurance agencies  - 524210 */


USE MODRPE

SELECT B.business_id, 
       B.business_legal_name,
       BL.trade_name,
       BL.business_status_id,
       BL.dlis_branch_number,
       BL.naics_code,
       O.delq_excptn_cd_id

FROM stg.obligation AS O
       INNER JOIN stg.BUSINESS_LOCATION AS BL ON O.bus_loc_id=BL.bus_loc_id
       INNER JOIN stg.business AS B ON BL.business_id=B.business_id
  
WHERE O.obl_type_id IN (5,9,10)
       AND O.obl_source_code_id=15
       AND (O.delq_excptn_cd_id IS Null OR O.delq_excptn_cd_id=10)
       AND BL.business_status_id IN (1,9)
       AND BL.NAICS_code=561320

GROUP BY B.business_id, 
       B.business_legal_name,
       BL.trade_name,
       BL.business_status_id,
       BL.dlis_branch_number,
       BL.naics_code,
       O.delq_excptn_cd_id
;
