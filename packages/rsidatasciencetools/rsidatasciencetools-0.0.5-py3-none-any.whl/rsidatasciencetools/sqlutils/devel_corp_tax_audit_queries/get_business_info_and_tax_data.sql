/* taxDeducBusInfo

get business data, obligations, tax due/paid, and relevant credits/deductions */

USE MODRPE

;WITH LOCCNT AS (
	SELECT COUNT(BLL.bus_loc_id) AS nLocations
		, BB.business_id
	FROM stg.BUSINESS_LOCATION AS BLL
		INNER JOIN stg.business as BB ON BB.business_id=BLL.business_id
	WHERE BLL.business_id{}{}
	GROUP BY BB.business_id

), BINFO AS (
SELECT B.business_id
		,BL.bus_loc_id
		,LOCCNT.nLocations AS maxNumLoc
		,B.business_legal_name
		,BL.dlis_branch_number
		,BL.business_status_id
		,BL.naics_code
		,B.legal_name_entry_date as bus_legal_open
		,B.bus_close_date
        ,BL.open_date AS loc_open_date
        ,BL.close_date AS loc_close_date

	FROM LOCCNT
		INNER JOIN stg.BUSINESS_LOCATION AS BL 
					ON BL.business_id=LOCCNT.business_id
		INNER JOIN stg.business AS B
					ON B.business_id=LOCCNT.business_id

	GROUP BY B.business_id
		,BL.bus_loc_id
		,LOCCNT.nLocations
		,B.business_legal_name
		,BL.dlis_branch_number
		,BL.business_status_id
		,BL.naics_code
		,B.legal_name_entry_date
		,B.bus_close_date
        ,BL.open_date
        ,BL.close_date

), OBL_DATA AS (
	SELECT BI.business_id
		,BI.bus_loc_id
		,O.Obligation_ID
		,O.obl_year
		,O.obl_period
		,TP.tax_period_cd
		,TR.TaxReturnID
		,O.obl_type_id
		,O.obl_source_code_id
		-- ,STRING_AGG(str(D.classification_id),',') as class_ids
		,Sum(D.gross_amount) AS sum_of_gross_amount
		,Sum(D.deduction_amount) AS sum_of_deduc_amount
		,Sum(D.taxable_amount) AS sum_of_taxable_amount
		,Sum(D.tax_due_amount) AS sum_of_tax_due
		,O.paid_amt

	FROM stg.obligation AS O
		INNER JOIN BINFO AS BI ON O.bus_loc_id=BI.bus_loc_id
		INNER JOIN stg.LICENSE AS L ON L.LICENSE_ID=O.license_id
		INNER JOIN stg.TAX_PERIOD_CODE AS TP ON TP.tax_period_cd_id=L.tax_period_cd_id
		--LEFT JOIN stg.AccountPeriod AS AP ON AP.obligation_id=O.obligation_id
		--INNER JOIN stg.OBL_TYPE_CODE as OT ON O.obl_type_id=OT.obl_type_id
		LEFT JOIN stg.tax_detail_charge AS D ON O.obligation_id=D.obligation_id
		LEFT JOIN stg.TaxReturn AS TR ON TR.obligation_id=O.obligation_id

    WHERE O.obl_source_code_id In (5,9,10,15) -- 15=tax return,10=license renewnal
		AND O.obl_type_id In (1,3,5,6,8,10,12,13,14,16,17,18,19,20,21,22,
            23,24,25,26,27,28,29,34,39,40,46,47,102,116,117,118,119,120,
            121,122,123,124,125,128,129,130,131,132,133,134,135,136,137,
            138,169,170,171,172,173,174)
        -- (5,9,10,133) -- 9=bus license renewnal fees (annual)
		AND (O.delq_excptn_cd_id IS Null OR O.delq_excptn_cd_id=10)
		AND D.detail_date is NULL Or D.detail_date = (SELECT MAX(Di.detail_date)
												FROM stg.tax_detail_charge AS Di  
												WHERE Di.obligation_id = D.obligation_id)

	GROUP BY BI.business_id
		,BI.bus_loc_id
		,O.obligation_id
		,O.obl_year
		,O.obl_period
		,TP.tax_period_cd
		--,AP.PERIOD_BEGIN_DT
		--,AP.PERIOD_END_DT
		--  ,OT.obl_type_code
		,TR.TaxReturnID
		,O.obl_source_code_id
		,O.obl_type_id
		,O.paid_amt

), DEDUC_DATA AS (
    
	SELECT TR.TaxReturnID
		,TR.obligation_id
		-- ,STRING_AGG(str(TaxReturnDetailDeductID),',') as TRDD_ID
		,STRING_AGG(str(TRD.Classification_ID),',') AS class_ids
		,STRING_AGG(str(TRD.Deduction_Type_ID),',') AS deduc_ids
		,sum(DeductAmount) AS deduc_amt_total
		--,DeductReason

    FROM stg.TaxReturnDetailDeduct AS TRD
        INNER JOIN stg.TaxReturn AS TR ON TR.TaxReturnID=TRD.TaxReturnID
        INNER JOIN OBL_DATA ON OBL_DATA.obligation_id=TR.obligation_id

    GROUP BY TR.TaxReturnID  
        ,TR.obligation_id
	
), TRWSHEET AS (
    SELECT TRWS.TaxReturnID
        ,DEDUC_DATA.obligation_id
        -- ,TRWS.WorksheetId
        ,STRING_AGG(str(TRWS.WorksheetId) + ':' + str(TRWS.FieldId) + '=' + str(TRWS.FieldValue),',') as WorksheetFields

    FROM stg.TaxReturnWorksheet AS TRWS
        INNER JOIN DEDUC_DATA ON DEDUC_DATA.TaxReturnID=TRWS.TaxReturnID

    WHERE TRWS.FieldValue <> 0.0 AND TRWS.FieldValue is not NULL

    GROUP BY TRWS.TaxReturnID
        , DEDUC_DATA.obligation_id
)

SELECT OD.business_id
    ,OD.bus_loc_id
    ,BI.maxNumLoc
    ,BI.business_status_id
    ,BI.naics_code
    ,BI.business_legal_name
    ,BI.dlis_branch_number
    ,OD.obligation_id
    ,OD.obl_year
    ,OD.obl_period
	,OD.tax_period_cd
	--,OD.PERIOD_BEGIN_DT
	--,OD.PERIOD_END_DT
	--,OD.num_locs
	,OD.obl_type_id
	,OD.obl_source_code_id
    ,STRING_AGG(str(OD.TaxReturnID),',') AS TaxRetIDs
    ,STRING_AGG(DD.class_ids,',') AS ded_class_ids 
    ,STRING_AGG(DD.deduc_ids,',') AS ded_type_ids  
    ,TWS.WorksheetFields --STRING_AGG(str(TWS.WorksheetFields),',') 
		AS ws_info
    ,sum(OD.sum_of_gross_amount) AS sumsum_gross
	,sum(OD.sum_of_deduc_amount) AS sumsum_deduc
    ,sum(OD.sum_of_taxable_amount) AS sumsum_taxable
    ,sum(OD.sum_of_tax_due) AS sumsum_taxdue
    ,sum(OD.paid_amt) AS sumsum_paid
    ,BI.bus_legal_open
    ,BI.bus_close_date
	,BI.loc_open_date
    ,BI.loc_close_date

    FROM OBL_DATA AS OD
        INNER JOIN BINFO AS BI ON BI.bus_loc_id=OD.bus_loc_id
        LEFT JOIN DEDUC_DATA AS DD ON DD.obligation_id=OD.obligation_id
        LEFT JOIN TRWSHEET AS TWS ON TWS.obligation_id=OD.obligation_id
    
    GROUP BY OD.business_id
        ,OD.bus_loc_id
		,BI.maxNumLoc
		,BI.business_status_id
		,BI.naics_code
		,BI.business_legal_name
		,BI.dlis_branch_number
        ,OD.obligation_id
        ,OD.obl_year
        ,OD.obl_period
		,OD.tax_period_cd
		--,OD.PERIOD_BEGIN_DT
		--,OD.PERIOD_END_DT
		--,OD.num_locs
		,OD.obl_type_id
		,OD.obl_source_code_id
		,TWS.WorksheetFields
		,BI.bus_legal_open
		,BI.bus_close_date
		,BI.loc_open_date
		,BI.loc_close_date

	ORDER BY
		OD.business_id
		,OD.bus_loc_id
		,OD.obl_year
		,OD.obl_period

;

