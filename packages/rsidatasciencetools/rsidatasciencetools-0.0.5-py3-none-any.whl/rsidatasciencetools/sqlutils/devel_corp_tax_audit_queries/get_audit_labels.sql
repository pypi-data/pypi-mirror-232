/* auditLabels

Script for getting labeled audit outcomes - from case issue code table 

Adding this to document method of translating entity IDs 
into business IDs, but can't mixed old legacy audit data
with new RPE case data - inconsistencies occur
*/

; WITH IDtrans AS (
    SELECT 
          EID.ENTITY_ID
          ,EID.ID AS business_id
  FROM dbo.ENTITY_IDS AS EID
  WHERE id_Type='BUSINESS_ID'

), CASE2BID AS (
	SELECT IDtrans.business_id
	  /*,rel.CAS2E_ID
      ,rel.AUDIT_ASSESSMENT AS ASSESSMENT_VALUE
	  */
      ,code.CASE_ID
	  ,code.CASE_IC_RELSHIP_ID AS case_sub_id
      ,code.EFFECTIVE_BEGIN_DT
      ,code.EFFECTIVE_END_DT
      ,code.UPDATED_DATE
      ,code.ISSUE_CODE
      ,code.ASSESSMENT_VALUE

    FROM dbo.CASE_ISSUE_CODE_RELSHIP AS code
  --FROM dbo.CASE_TO_ACCOUNT_PD_RELSHIP AS rel
		INNER JOIN dbo.CASE_TO_TAXPAYER_RELATIONSHIP AS c2a 
			--ON c2a.CASE_ID=rel.CASE_ID
			  ON c2a.CASE_ID=code.CASE_ID
		INNER JOIN IDtrans ON IDtrans.ENTITY_ID=c2a.ENTITY_ID
    
)

SELECT
      code.business_id
      ,code.CASE_ID
      --,code.CASE_IC_RELSHIP_ID
	  ,code.case_sub_id
      ,code.ASSESSMENT_VALUE
      ,code.EFFECTIVE_BEGIN_DT
      ,code.EFFECTIVE_END_DT
      ,code.UPDATED_DATE
      ,code.ISSUE_CODE
	  

      ,aud.audit_id
      ,aud.obl_type_id
      ,aud.audit_src_id
      ,aud.stage
      ,aud.date_started_work
      ,aud.period_from_date
      ,aud.period_to_date
FROM CASE2BID AS code
     INNER JOIN dbo.SLIM_AUDIT_EXTRACT AS aud ON aud.business_id=code.business_id

WHERE aud.stage>=5 AND code.business_id=57

ORDER BY code.business_id, code.CASE_ID