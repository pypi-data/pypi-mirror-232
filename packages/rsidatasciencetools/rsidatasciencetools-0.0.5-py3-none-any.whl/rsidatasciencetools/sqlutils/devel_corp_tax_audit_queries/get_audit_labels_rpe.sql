SELECT
	   EID.business_id
	  ,appr.APPROVAL_REQUEST_ID
      ,appr.[CASE_ID]
      ,appr.[APPROVAL_TYPE]
      ,appr.[CREATED_DATE]
      ,appr.[UPDATED_DATE]
FROM [modRPE].[dbo].[APPROVAL_REQUEST_QUEUE] as appr
INNER JOIN dbo.CASE_TO_TAXPAYER_RELATIONSHIP as C2A on C2A.CASE_ID=appr.CASE_ID
INNER JOIN (SELECT ENTITY_ID, ID AS business_id FROM dbo.ENTITY_IDS 
            WHERE dbo.ENTITY_IDS.ID_TYPE='BUSINESS_ID') AS EID on EID.ENTITY_ID=C2A.ENTITY_ID



-- trimmed down audit data


-- Labeled audit data fields
['case_id',
 'entity_name',
 'Auditor',
 'business_id',
 'case_type',
 'case_sub_type',
 'initial_approval_date',
 'reapproval_date',
 'NAICS',
 'naics_2',
 'naics2_description',
 'Location',
 'CRITERIA #1',
 'CRITERIA #2',
 'DETAILS',
 'issue_code',
 'assessment_amount']

/****** Script for SelectTopNRows command from SSMS  ******/

; WITH ids AS (
    SELECT 
          EID.ENTITY_ID
          ,EID.ID AS business_id
          ,EN.ENTITY_NAME AS entity_name
  FROM dbo.ENTITY_IDS AS EID
      INNER JOIN dbo.ENTITY_NAMES AS EN ON EN.ENTITY_ID=ids.ENTITY_ID
  WHERE id_Type='BUSINESS_ID'
)

SELECT ADM.case_id
      ,ids.entity_name
      ,ADM.case_type
      ,ADM.case_sub_type
      ,ADM.audit_flag
      ,ADM.case_status
      ,ADM.case_source
      ,ADM.case_flag
      ,ADM.view_result_item_id
      ,ADM.creation_date
      ,ADM.start_date
      ,ADM.created_by
      ,ADM.generic_source_code
      ,ADM.specific_source_code
      ,ADM.tp_name
      ,ADM.primary_id as business_id
      ,ADM.non_registrant_flag
      ,ADM.assigned_date
      ,ADM.case_age
      ,ADM.current_slim_stage
      ,ADM.tax_type
      ,ADM.filing_entity
      ,ADM.first_period
      ,ADM.last_period
      ,ADM.total_periods
      ,ADM.total_audit_assessment
      ,ADM.total_collected_return_amount
      ,ADM.total_collected_amount
      ,ADM.total_hours
      ,ADM.primary_auditor_hours
      ,ADM.issue_code_1
      ,ADM.issue_code_value_1
      ,ADM.issue_code_2
      ,ADM.issue_code_value_2
      ,ADM.last_approval_type
      ,ADM.last_approval_progress
      ,ADM.appeal_age
      ,ADM.final_approval_reject_date
      ,ADM.naics_code AS NAICS
  
  FROM dbo.AUDIT_DATAMART as ADM
    INNER JOIN ids id ON ids.business_id=ADM.primary_id


-- ALL DATAMART fields
      [case_id]
      ,[entity_id]
      ,[added_date]
      ,[updated_by]
      ,[updated_date]
      ,[case_type]
      ,[case_sub_type]
      ,[audit_flag]
      ,[case_status]
      ,[case_source]
      ,[case_flag]
      ,[view_result_item_id]
      ,[creation_date]
      ,[start_date]
      ,[created_by]
      ,[generic_source_code]
      ,[specific_source_code]
      ,[tp_name]
      ,[primary_id]
      ,[primary_id_type]
      ,[tp_address_line_1]
      ,[tp_city]
      ,[tp_state_province]
      ,[tp_postal_code]
      ,[tp_bi_flag]
      ,[primary_user_id]
      ,[supervisor_user_id]
      ,[chief_user_id]
      ,[non_registrant_flag]
      ,[original_sol_date]
      ,[current_sol_date]
      ,[days_to_sol]
      ,[assigned_date]
      ,[case_age]
      ,[current_slim_stage]
      ,[date_to_supervisor]
      ,[tax_type]
      ,[filing_entity]
      ,[first_period]
      ,[last_period]
      ,[total_periods]
      ,[total_audit_assessment]
      ,[total_audit_tax]
      ,[total_audit_penalty]
      ,[total_audit_interest]
      ,[total_manual_penalty_amount]
      ,[total_collected_return_amount]
      ,[total_collected_amount]
      ,[budgeted_hours]
      ,[total_hours]
      ,[taxpayer_hours]
      ,[district_office_hours]
      ,[home_office_hours]
      ,[unspecified_hours]
      ,[primary_auditor_hours]
      ,[primary_auditor_pct_credit]
      ,[primary_auditor_case_credit]
      ,[primary_auditor_tax_credit]
      ,[primary_auditor_pen_credit]
      ,[primary_auditor_int_credit]
      ,[primary_auditor_ta_credit]
      ,[secondary_auditor_1_user_id]
      ,[secondary_auditor_1_sup_id]
      ,[secondary_auditor_1_chief_id]
      ,[secondary_auditor_1_hours]
      ,[secondary_auditor_1_pct_credit]
      ,[secondary_auditor_1_cas_credit]
      ,[secondary_auditor_1_tax_credit]
      ,[secondary_auditor_1_pen_credit]
      ,[secondary_auditor_1_int_credit]
      ,[secondary_auditor_1_ta_credit]
      ,[secondary_auditor_2_user_id]
      ,[secondary_auditor_2_sup_id]
      ,[secondary_auditor_2_chief_id]
      ,[secondary_auditor_2_hours]
      ,[secondary_auditor_2_pct_credit]
      ,[secondary_auditor_2_cas_credit]
      ,[secondary_auditor_2_tax_credit]
      ,[secondary_auditor_2_pen_credit]
      ,[secondary_auditor_2_int_credit]
      ,[secondary_auditor_2_ta_credit]
      ,[secondary_auditor_3_user_id]
      ,[secondary_auditor_3_sup_id]
      ,[secondary_auditor_3_chief_id]
      ,[secondary_auditor_3_hours]
      ,[secondary_auditor_3_pct_credit]
      ,[secondary_auditor_3_cas_credit]
      ,[secondary_auditor_3_tax_credit]
      ,[secondary_auditor_3_pen_credit]
      ,[secondary_auditor_3_int_credit]
      ,[secondary_auditor_3_ta_credit]
      ,[issue_code_1]
      ,[issue_code_value_1]
      ,[issue_code_2]
      ,[issue_code_value_2]
      ,[issue_code_3]
      ,[issue_code_value_3]
      ,[issue_code_4]
      ,[issue_code_value_4]
      ,[issue_code_5]
      ,[issue_code_value_5]
      ,[issue_code_6]
      ,[issue_code_value_6]
      ,[issue_code_7]
      ,[issue_code_value_7]
      ,[final_approval_tax_man_user_id]
      ,[final_approval_aud_rev_user_id]
      ,[last_approval_request_id]
      ,[last_approval_type]
      ,[last_approval_type_decode]
      ,[last_approval_initiated_date]
      ,[last_approval_progress]
      ,[last_approval_updated_date]
      ,[date_appeal_started]
      ,[date_appeal_completed]
      ,[appeal_age]
      ,[its_status]
      ,[its_load_date]
      ,[close_reason_original]
      ,[close_reason_decode_original]
      ,[close_date_original]
      ,[close_reason_current]
      ,[close_reason_decode_current]
      ,[close_date_current]
      ,[last_activity_date]
      ,[days_of_inactivity]
      ,[final_approval_reject_date]
      ,[naics_code]
      ,[case_score]
  FROM [modRPE].[dbo].[AUDIT_DATAMART]