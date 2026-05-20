
def map(DATE_FROM,DATE_TO,CURRENT_YEAR,YEAR_STRING,TABLE):
    mapstr = (f'''
    DECLARE @latest_from DATE ='{DATE_FROM}' 
    DECLARE @latest_to   DATE = '{DATE_TO}'
    DECLARE @latest_year VARCHAR(4) = '{str(CURRENT_YEAR-1)}' 
    DECLARE @FYEAR VARCHAR(MAX) = '{YEAR_STRING}' 

    SET ANSI_NULLS ON
    SET ANSI_WARNINGS ON
    SET NOCOUNT ON 

    EXEC('
    SELECT * INTO #HES_EPS FROM
    (
    select 
    CASE WHEN GROUPING(_P_PROCODE) = 0 THEN _P_PROCODE ELSE ''England'' END AS ''H1_Org'',
    case when PROMS_PROC_CODE =''HR'' and PROC_REVISION_FLAG = 0 then ''HR-PRIM''
        when PROMS_PROC_CODE =''HR'' and PROC_REVISION_FLAG = 1 then ''HR-REV''
        when PROMS_PROC_CODE =''KR'' and PROC_REVISION_FLAG = 0 then ''KR-PRIM''
        when PROMS_PROC_CODE =''KR'' and PROC_REVISION_FLAG = 1 then ''KR-REV''
        else PROMS_PROC_CODE
    end as ''H2_Proc'',
    COUNT (EPIKEY) as ''H3_Episodes''
    from proms.HES_PROCEDURES_{TABLE}
    where EPISTART between \'\'\'+@latest_from+\'\'\' and \'\'\'+@latest_to+\'\'\'
    group by rollup(_P_PROCODE), PROMS_PROC_CODE, PROC_REVISION_FLAG

    union

    select 
    CASE WHEN GROUPING(_P_PROCODE) = 0 THEN _P_PROCODE ELSE ''England'' END AS ''H1_Org'',
    PROMS_PROC_CODE as ''H2_Proc'',
    COUNT (EPIKEY) as ''H3_Episodes''
    from proms.HES_PROCEDURES_{TABLE}
    where EPISTART between \'\'\'+@latest_from+\'\'\' and \'\'\'+@latest_to+\'\'\' and PROMS_PROC_CODE in (''hr'',''kr'')
    group by rollup(_P_PROCODE), PROMS_PROC_CODE

    union


    select 
    CASE WHEN GROUPING(CCG_CODE) = 0 THEN CCG_CODE ELSE ''England_CCG'' END AS ''H1_Org'',
    PROMS_PROC_CODE as ''H2_Proc'',
    COUNT (EPIKEY) as ''H3_Episodes''
    from proms.HES_PROCEDURES_{TABLE}
    where EPISTART between \'\'\'+@latest_from+\'\'\' and \'\'\'+@latest_to+\'\'\' and PROMS_PROC_CODE in (''hr'',''kr'')
    group by rollup(CCG_CODE), PROMS_PROC_CODE

    union


    select 
    CASE WHEN GROUPING(CCG_CODE) = 0 THEN CCG_CODE ELSE ''England_CCG'' END AS ''H1_Org'',
    case when PROMS_PROC_CODE =''HR'' and PROC_REVISION_FLAG = 0 then ''HR-PRIM''
        when PROMS_PROC_CODE =''HR'' and PROC_REVISION_FLAG = 1 then ''HR-REV''
        when PROMS_PROC_CODE =''KR'' and PROC_REVISION_FLAG = 0 then ''KR-PRIM''
        when PROMS_PROC_CODE =''KR'' and PROC_REVISION_FLAG = 1 then ''KR-REV''
        else PROMS_PROC_CODE
        end as ''H2_Proc'',
    COUNT (EPIKEY) as ''H3_Episodes''
    from proms.HES_PROCEDURES_{TABLE}
    where EPISTART between \'\'\'+@latest_from+\'\'\' and \'\'\'+@latest_to+\'\'\'
    group by rollup(CCG_CODE), PROMS_PROC_CODE, PROC_REVISION_FLAG)_

    select * into #Union from (
    select *
    from proms.PROMS_AGGREGATED_STATS_{TABLE} a 
    join #hes_eps b on a.orgcode = b.H1_Org and a.ProcGroup = b.H2_Proc
    where FYear=\'\'\'+@latest_year+\'\'\')_


    select * into #supp1 from(select
    CONVERT(nvarchar(50),a.OrgCode)+ CONVERT(nvarchar(50),ProcGroup)+ CONVERT(nvarchar(50),Measure) as [Lookup]
    ,FYear,
    ProcGroup,
    Measure,
    [Version],
    AggMethod,
    OrgType,
    case when a.OrgType=''England'' then ''England'' else b.OrgName end as ''OrgName'',
    a.OrgCode,
    case when a.OrgType=''England'' then ''England'' else OrgName end as OrgNameSC,
    --CONVERT(nvarchar(50),OrgName)+'' (''+ CONVERT(nvarchar(50),a.OrgCode)+'')'' end as OrgNameSC,
    H3_Episodes as ''Episodes'',
    case when H3_Episodes in (1,2,3,4,5) then ''-99'' else InputCount end as InputCount,
    case when H3_Episodes in (1,2,3,4,5) then ''-99'' else AvgQ1 end as Avg01,
    case when H3_Episodes in (1,2,3,4,5) then ''-99'' else AvgQ2 end as Avg02,
    case when H3_Episodes in (1,2,3,4,5) then ''-99'' else Change end as Change,
    case when H3_Episodes in (1,2,3,4,5) then ''-99'' else Improved end as Improved,
    case when H3_Episodes in (1,2,3,4,5) then ''-99'' else Same end as Same,
    case when H3_Episodes in (1,2,3,4,5) then ''-99'' else Worse end as Worse,
    case when H3_Episodes in (1,2,3,4,5) then ''-99'' when InputCount between 1 and 29 then ''-99'' else AdjQ2 end as Adj02,
    case when H3_Episodes in (1,2,3,4,5) then ''-99'' when InputCount between 1 and 29 then ''-99'' else AdjHG end as AdjHG,
    case when H3_Episodes in (1,2,3,4,5) then ''-99'' when InputCount between 1 and 29 then ''-99'' else StdDev end as StdDev,
    case when H3_Episodes in (1,2,3,4,5) then ''-99'' when InputCount between 1 and 29 then ''-99'' else Q2Predicted end as Q2Predicted,
    case when H3_Episodes in (1,2,3,4,5) then ''-99'' when InputCount between 1 and 29 then ''-99'' else LCL95 end as LCL95,
    case when H3_Episodes in (1,2,3,4,5) then ''-99'' when InputCount between 1 and 29 then ''-99'' else UCL95 end as UCL95,
    case when H3_Episodes in (1,2,3,4,5) then ''-99'' when InputCount between 1 and 29 then ''-99'' else LCL998 end as LCL998,
    case when H3_Episodes in (1,2,3,4,5) then ''-99'' when InputCount between 1 and 29 then ''-99'' else UCL998 end as UCL998,
    case when H3_Episodes in (1,2,3,4,5) then ''-99'' when InputCount between 1 and 29 then ''-99'' else [Outlier 95%] end as [Outlier 95%],
    case when H3_Episodes in (1,2,3,4,5) then ''-99'' when InputCount between 1 and 29 then ''-99'' else [Outlier 99.8%] end as [Outlier 99.8%]

    from #Union a
    left join proms.REF_ORGS_{TABLE} b on a.OrgCode=b.OrgCode)_

    select * INTO #SUPP2 FROM(SELECT

    Lookup,
    FYear,
    ProcGroup,
    Measure,
    Version,
    AggMethod,
    OrgType,
    OrgName,
    OrgCode,
    Episodes,
    convert(varchar, InputCount) as InputCount,
    convert(varchar, Avg01) as Avg01,
    convert(varchar, Avg02) as Avg02,
    convert(varchar, Change) as Change,
    convert(varchar, Improved) as Improved,
    convert(varchar, Same) as Same,
    convert(varchar, Worse) as Worse,
    convert(varchar, Adj02) as Adj02,
    convert(varchar, AdjHG) as AdjHG,
    convert(varchar, StdDev) as StdDev,
    convert(varchar, Q2Predicted) as Q2Predicted,
    convert(varchar, LCL95) as LCL95,
    convert(varchar, UCL95) as UCL95,
    convert(varchar, LCL998) as LCL998,
    convert(varchar, UCL998) as UCL998,
    convert(varchar, [Outlier 95%]) as [Outlier 95%],
    convert(varchar, [Outlier 99.8%]) as [Outlier 99.8%]

    from #supp1)_




    SELECT 
    \'\'\'+@FYEAR+\'\'\' as ''Financial Year'',
    case 
    when ProcGroup = ''gh'' then ''Groin Hernia'' 
    when ProcGroup = ''vv'' then ''Varicose Vein''
    when ProcGroup = ''hr-prim'' then ''Hip Replacement Primary''
    when ProcGroup = ''hr-rev'' then ''Hip Replacement Revision''
    when ProcGroup = ''hr'' then ''Total Hip Replacement''
    when ProcGroup = ''kr-prim'' then ''Knee Replacement Primary''
    when ProcGroup = ''kr-rev'' then ''Knee Replacement Revision''
    when ProcGroup = ''kr'' then ''Total Knee Replacement''
    else null end as ''Procedure''
    ,OrgType as ''Organisation Type'',
    OrgCode  as ''Organisation Code'',
    case when orgtype = ''England'' then ''England'' else	OrgName end as ''Organisation Name'' ,
    --else OrgName+'' (''+orgcode+'')'' end  as ''Organisation Name'',
    b.NAME as Region,
    case
    when Measure = ''vas'' then ''EQ VAS''
    when Measure = ''index'' then ''EQ-5D Index''
    when Measure = ''avvq'' then ''Aberdeen Varicose Vein Questionnaire''
    when Measure = ''oks'' then ''Oxford Knee Score''
    when Measure = ''ohs'' then ''Oxford Hip Score''
    else null end as ''Measure'',
    CASE WHEN InputCount IN (''-99'') THEN ''*'' when InputCount =''0'' then ''-'' ELSE InputCount end as ''Modelled Records'',
    Case When Avg01 IN (''-99'') THEN ''*'' when InputCount =''0'' then ''-'' ELSE Avg01 end as ''Average Pre-Op Q Score'',
    Case When Avg02 IN (''-99'') THEN ''*'' when InputCount =''0'' then ''-'' ELSE Avg02 end as ''Average Post-Op Q Score'',
    Case When Change IN (''-99'') THEN ''*'' when InputCount =''0'' then ''-'' ELSE Change end as ''Health Gain'',
    Case When Improved IN (''-99'') THEN ''*'' when InputCount =''0'' then ''-'' ELSE Improved end as Improved,
    Case When Same IN (''-99'') THEN ''*'' when InputCount =''0'' then ''-'' ELSE Same end as Same,
    Case When Worse IN (''-99'') THEN ''*'' when InputCount =''0'' then ''-'' ELSE Worse end as Worse,
    Case When Adj02 IN (''-99'') THEN ''*'' when InputCount =''0'' then ''-'' ELSE Adj02 end as ''Adjusted Post-Op Q Score'',
    Case When AdjHG IN (''-99'') THEN ''*'' when InputCount =''0'' then ''-'' ELSE AdjHG end as ''Adjusted Average Health Gain'',
    Case When StdDev IN (''-99'') THEN ''*'' when InputCount =''0'' then ''-'' ELSE StdDev end as ''Standard Deviation''
    --d.CCG13CD as ''ONS''

    FROM #SUPP2 a
    left join PROMS_HES.dbo.ORG_RELATIONSHIP_DAILY c
    on a.OrgCode=c.REL_FROM_ORG_CODE and c.REL_TO_ORG_TYPE_CODE=''CF'' and REL_IS_CURRENT=1
    left join PROMS_HES.dbo.ORG_DAILY b
    on c.REL_TO_ORG_CODE=b.ORG_CODE and ORG_IS_CURRENT=1
    --left join PROMS_HES.dbo.ONS_LSOA_CCG_LAD as d
    --on a.OrgCode=d.CCG13CDH and d.RECORD_END_DATE is null

    where procgroup NOT in (''gh'',''vv'') and OrgType=''CCG of GP Practice'' 
    order by OrgName, ProcGroup, measure
    ')
    ''')
    return mapstr

def ind_quest_KR(DATE_TO,DATE_FROM, YEAR_STRING,TABLE):
    indquest_kr_str = f'''
        DECLARE @TABLE				VARCHAR(MAX) = '{TABLE}'
        DECLARE @YR1_START			DATE = '{DATE_FROM}';
        DECLARE @YR1_END			DATE = '{DATE_TO}'
        DECLARE @YR1				VARCHAR (MAX) = '{YEAR_STRING}'
        DECLARE @PROC VARCHAR(2) = 'KR'
        
        SET NOCOUNT ON
        
        IF OBJECT_ID ('tempdb..##OKS') IS NOT NULL DROP TABLE ##OKS

        EXEC('SELECT * INTO ##OKS FROM
        (
            SELECT *,
            \'\'\'+@YR1+\'\'\' AS ''Financial Year''
            FROM proms.QUESTS_'+@TABLE+'
            WHERE
                _Q1_PROXY_DATE BETWEEN \'\'\'+@YR1_START+\'\'\' AND \'\'\'+@YR1_END+\'\'\' 
                AND PROMS_PROC_CODE = \'\'\'+@PROC+\'\'\'
                AND Q1_CS_SCORE IS NOT NULL
                AND Q2_CS_SCORE IS NOT NULL
                
        ) T1

        IF OBJECT_ID (''tempdb..#Provider'') IS NOT NULL DROP TABLE #Provider

        SELECT * INTO #Provider FROM
        (
        SELECT 
            [Financial Year] as ''Financial Year'',
            ''Extremely difficult or impossible to wash and dry yourself'' AS Question,
            CAST(CAST(CAST(COUNT(CASE WHEN '+@PROC+'_Q1_WASHING IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q1,
            CAST(CAST(CAST(COUNT(CASE WHEN '+@PROC+'_Q2_WASHING IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q2,
            _Q1_PROCODE AS PROVIDER
        FROM ##OKS
        GROUP BY _Q1_PROCODE, [Financial Year]

        UNION ALL

        SELECT
            [Financial Year] as ''Financial Year'',
            ''Extremely difficult or impossible to do household shopping on your own'' AS Question,
            CAST(CAST(CAST(COUNT(CASE WHEN '+@PROC+'_Q1_SHOPPING IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q1,
            CAST(CAST(CAST(COUNT(CASE WHEN '+@PROC+'_Q2_SHOPPING IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q2,
            _Q1_PROCODE AS PROVIDER
        FROM ##OKS
        GROUP BY _Q1_PROCODE, [Financial Year]

        UNION ALL

        SELECT
            [Financial Year] as ''Financial Year'',
            ''Extremely difficult or impossible to climb a flight of stairs'' AS Question,
            CAST(CAST(CAST(COUNT(CASE WHEN '+@PROC+'_Q1_STAIRS IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q1,
            CAST(CAST(CAST(COUNT(CASE WHEN '+@PROC+'_Q2_STAIRS IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q2,
            _Q1_PROCODE AS PROVIDER
        FROM ##OKS
        GROUP BY _Q1_PROCODE, [Financial Year]
            
        UNION ALL

        SELECT 
            [Financial Year] as ''Financial Year'',
            ''Extremely difficult or impossible to kneel down and get up again'' AS Question,
            CAST(CAST(CAST(COUNT(CASE WHEN '+@PROC+'_Q1_KNEELING IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q1,
            CAST(CAST(CAST(COUNT(CASE WHEN '+@PROC+'_Q2_KNEELING IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q2,
            _Q1_PROCODE AS PROVIDER
        FROM ##OKS
        GROUP BY _Q1_PROCODE, [Financial Year]
            
        UNION ALL

        SELECT
            [Financial Year] as ''Financial Year'',
            ''Extremely difficult or impossible to use car or public transport'' AS Question,
            CAST(CAST(CAST(COUNT(CASE WHEN '+@PROC+'_Q1_TRANSPORT IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q1,
            CAST(CAST(CAST(COUNT(CASE WHEN '+@PROC+'_Q2_TRANSPORT IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q2,
            _Q1_PROCODE AS PROVIDER
        FROM ##OKS
        GROUP BY _Q1_PROCODE, [Financial Year]
            
        UNION ALL

        SELECT
            [Financial Year] as ''Financial Year'',
            ''Limping when walking most or all of the time'' AS Question,
            CAST(CAST(CAST(COUNT(CASE WHEN '+@PROC+'_Q1_LIMPING IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q1,
            CAST(CAST(CAST(COUNT(CASE WHEN '+@PROC+'_Q2_LIMPING IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q2,
            _Q1_PROCODE AS PROVIDER
        FROM ##OKS
        GROUP BY _Q1_PROCODE, [Financial Year]
            
        UNION ALL

        SELECT
            [Financial Year] as ''Financial Year'',
            ''Can walk around the house only or not at all before knee pain becomes severe'' AS Question,
            CAST(CAST(CAST(COUNT(CASE WHEN '+@PROC+'_Q1_WALKING IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q1,
            CAST(CAST(CAST(COUNT(CASE WHEN '+@PROC+'_Q2_WALKING IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q2,
            _Q1_PROCODE AS PROVIDER
        FROM ##OKS
        GROUP BY _Q1_PROCODE, [Financial Year]
            
        UNION ALL

        SELECT
            [Financial Year] as ''Financial Year'',
            ''Very painful or unbearable to stand up from a chair'' AS Question,
            CAST(CAST(CAST(COUNT(CASE WHEN '+@PROC+'_Q1_STANDING IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q1,
            CAST(CAST(CAST(COUNT(CASE WHEN '+@PROC+'_Q2_STANDING IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q2,
            _Q1_PROCODE AS PROVIDER
        FROM ##OKS
        GROUP BY _Q1_PROCODE, [Financial Year]
            
        UNION ALL

        SELECT
            [Financial Year] as ''Financial Year'',
            ''Felt that your knee might suddenly give way or let you down most or all of the time'' AS Question,
            CAST(CAST(CAST(COUNT(CASE WHEN '+@PROC+'_Q1_CONFIDENCE IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q1,
            CAST(CAST(CAST(COUNT(CASE WHEN '+@PROC+'_Q2_CONFIDENCE IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q2,
            _Q1_PROCODE AS PROVIDER
        FROM ##OKS
        GROUP BY _Q1_PROCODE, [Financial Year]
            
        UNION ALL

        SELECT
            [Financial Year] as ''Financial Year'',
            ''Great or total interference with work from pain in knee'' AS Question,
            CAST(CAST(CAST(COUNT(CASE WHEN '+@PROC+'_Q1_WORK IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q1,
            CAST(CAST(CAST(COUNT(CASE WHEN '+@PROC+'_Q2_WORK IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q2,
            _Q1_PROCODE AS PROVIDER
        FROM ##OKS
        GROUP BY _Q1_PROCODE, [Financial Year]
            
        UNION ALL

        SELECT
            [Financial Year] as ''Financial Year'',
            ''Troubled by pain in knee when in bed on most nights or every night'' AS Question,
            CAST(CAST(CAST(COUNT(CASE WHEN '+@PROC+'_Q1_NIGHT_PAIN IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q1,
            CAST(CAST(CAST(COUNT(CASE WHEN '+@PROC+'_Q2_NIGHT_PAIN IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q2,
            _Q1_PROCODE AS PROVIDER
        FROM ##OKS
        GROUP BY _Q1_PROCODE, [Financial Year]
            
        UNION ALL

        SELECT
            [Financial Year] as ''Financial Year'',
            ''Usually moderate or severe pain from knee'' AS Question,
            CAST(CAST(CAST(COUNT(CASE WHEN '+@PROC+'_Q1_PAIN IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q1,
            CAST(CAST(CAST(COUNT(CASE WHEN '+@PROC+'_Q2_PAIN IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q2,
            _Q1_PROCODE AS PROVIDER
        FROM ##OKS
        GROUP BY _Q1_PROCODE, [Financial Year]
        )_

        IF OBJECT_ID (''tempdb..#England'') IS NOT NULL DROP TABLE #England

        SELECT * INTO #England FROM 
        (
        SELECT 
            [Financial Year] as ''Financial Year'',
            ''Extremely difficult or impossible to wash and dry yourself'' AS Question,
            CAST(CAST(CAST(COUNT(CASE WHEN '+@PROC+'_Q1_WASHING IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q1,
            CAST(CAST(CAST(COUNT(CASE WHEN '+@PROC+'_Q2_WASHING IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q2,
            ''ENGLAND'' AS PROVIDER
            
        FROM ##OKS
        GROUP BY [Financial Year]


        UNION ALL

        SELECT
            [Financial Year] as ''Financial Year'',
            ''Extremely difficult or impossible to do household shopping on your own'' AS Question,
            CAST(CAST(CAST(COUNT(CASE WHEN '+@PROC+'_Q1_SHOPPING IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q1,
            CAST(CAST(CAST(COUNT(CASE WHEN '+@PROC+'_Q2_SHOPPING IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q2,
            ''ENGLAND'' AS PROVIDER
            
        FROM ##OKS
        GROUP BY [Financial Year]

        UNION ALL

        SELECT
            [Financial Year] as ''Financial Year'',
            ''Extremely difficult or impossible to climb a flight of stairs'' AS Question,
            CAST(CAST(CAST(COUNT(CASE WHEN '+@PROC+'_Q1_STAIRS IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q1,
            CAST(CAST(CAST(COUNT(CASE WHEN '+@PROC+'_Q2_STAIRS IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q2,
            ''ENGLAND'' AS PROVIDER
            
        FROM ##OKS
        GROUP BY [Financial Year]
            
            
        UNION ALL

        SELECT 
            [Financial Year] as ''Financial Year'',
            ''Extremely difficult or impossible to kneel down and get up again'' AS Question,
            CAST(CAST(CAST(COUNT(CASE WHEN '+@PROC+'_Q1_KNEELING IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q1,
            CAST(CAST(CAST(COUNT(CASE WHEN '+@PROC+'_Q2_KNEELING IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q2,
            ''ENGLAND'' AS PROVIDER
            
        FROM ##OKS
        GROUP BY [Financial Year]
            
        UNION ALL

        SELECT
            [Financial Year] as ''Financial Year'',
            ''Extremely difficult or impossible to use car or public transport'' AS Question,
            CAST(CAST(CAST(COUNT(CASE WHEN '+@PROC+'_Q1_TRANSPORT IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q1,
            CAST(CAST(CAST(COUNT(CASE WHEN '+@PROC+'_Q2_TRANSPORT IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q2,
            ''ENGLAND'' AS PROVIDER
            
        FROM ##OKS
        GROUP BY [Financial Year]
            
        UNION ALL

        SELECT
            [Financial Year] as ''Financial Year'',
            ''Limping when walking most or all of the time'' AS Question,
            CAST(CAST(CAST(COUNT(CASE WHEN '+@PROC+'_Q1_LIMPING IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q1,
            CAST(CAST(CAST(COUNT(CASE WHEN '+@PROC+'_Q2_LIMPING IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q2,
            ''ENGLAND'' AS PROVIDER
            
        FROM ##OKS
        GROUP BY [Financial Year]  
            
        UNION ALL

        SELECT
            [Financial Year] as ''Financial Year'',
            ''Can walk around the house only or not at all before knee pain becomes severe'' AS Question,
            CAST(CAST(CAST(COUNT(CASE WHEN '+@PROC+'_Q1_WALKING IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q1,
            CAST(CAST(CAST(COUNT(CASE WHEN '+@PROC+'_Q2_WALKING IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q2,
            ''ENGLAND'' AS PROVIDER
            
        FROM ##OKS
        GROUP BY [Financial Year]
              
        UNION ALL

        SELECT
            [Financial Year] as ''Financial Year'',
            ''Very painful or unbearable to stand up from a chair'' AS Question,
            CAST(CAST(CAST(COUNT(CASE WHEN '+@PROC+'_Q1_STANDING IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q1,
            CAST(CAST(CAST(COUNT(CASE WHEN '+@PROC+'_Q2_STANDING IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q2,
            ''ENGLAND'' AS PROVIDER
            
        FROM ##OKS
        GROUP BY [Financial Year]
             
        UNION ALL

        SELECT
            [Financial Year] as ''Financial Year'',
            ''Felt that your knee might suddenly give way or let you down most or all of the time'' AS Question,
            CAST(CAST(CAST(COUNT(CASE WHEN '+@PROC+'_Q1_CONFIDENCE IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q1,
            CAST(CAST(CAST(COUNT(CASE WHEN '+@PROC+'_Q2_CONFIDENCE IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q2,
            ''ENGLAND'' AS PROVIDER
            
        FROM ##OKS
        GROUP BY [Financial Year]
            
        UNION ALL

        SELECT
            [Financial Year] as ''Financial Year'',
            ''Great or total interference with work from pain in knee'' AS Question,
            CAST(CAST(CAST(COUNT(CASE WHEN '+@PROC+'_Q1_WORK IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q1,
            CAST(CAST(CAST(COUNT(CASE WHEN '+@PROC+'_Q2_WORK IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q2,
            ''ENGLAND'' AS PROVIDER
            
        FROM ##OKS
        GROUP BY [Financial Year]
             
        UNION ALL

        SELECT
            [Financial Year] as ''Financial Year'',
            ''Troubled by pain in knee when in bed on most nights or every night'' AS Question,
            CAST(CAST(CAST(COUNT(CASE WHEN '+@PROC+'_Q1_NIGHT_PAIN IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q1,
            CAST(CAST(CAST(COUNT(CASE WHEN '+@PROC+'_Q2_NIGHT_PAIN IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q2,
            ''ENGLAND'' AS PROVIDER
            
        FROM ##OKS
        GROUP BY [Financial Year]
             
        UNION ALL

        SELECT
            [Financial Year] as ''Financial Year'',
            ''Usually moderate or severe pain from knee'' AS Question,
            CAST(CAST(CAST(COUNT(CASE WHEN '+@PROC+'_Q1_PAIN IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q1,
            CAST(CAST(CAST(COUNT(CASE WHEN '+@PROC+'_Q2_PAIN IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q2,
            ''ENGLAND'' AS PROVIDER
            
        FROM ##OKS
        GROUP BY [Financial Year]
        )_

        IF OBJECT_ID (''tempdb..#ALL'') IS NOT NULL DROP TABLE #ALL

        SELECT a.*, case when a.[PROVIDER]=''ENGLAND'' then ''England'' else b.OrgName end as ''NAME'' INTO #ALL FROM
        (
        SELECT * FROM #Provider
        UNION ALL
        SELECT * FROM #England
        ) a 
        left join PROMS_PUBLICATION.proms.REF_ORGS_'+@TABLE+' as b
        on a.[PROVIDER]=b.OrgCode

        SELECT A.[Financial Year], A.PROVIDER, ''Oxford Knee Score'' AS ''Measure'', A.Question, A.Q1, A.Q2, 
            B.Q1 AS ''England Q1'', B.Q2 AS ''England Q2'', [NAME]
        FROM #ALL AS A
        LEFT JOIN #England AS B
        ON A.Question=B.Question AND A.[Financial Year]=B.[Financial Year] 
            
        DROP TABLE ##OKS
        ')
    '''
    return indquest_kr_str

def ind_quest_HR(DATE_TO,DATE_FROM, YEAR_STRING,TABLE):
    inquest_hr_str = f'''
        DECLARE @TABLE				VARCHAR(MAX) = '{TABLE}'
        DECLARE @YR1_START			DATE = '{DATE_FROM}';
        DECLARE @YR1_END			DATE = '{DATE_TO}'
        DECLARE @YR1				VARCHAR (MAX) = '{YEAR_STRING}'

        SET NOCOUNT ON

        IF OBJECT_ID ('tempdb..##OHS') IS NOT NULL DROP TABLE ##OHS

        EXEC('SELECT * INTO ##OHS FROM
        (
            SELECT *,
                \'\'\'+@YR1+\'\'\' AS ''Financial Year''
            FROM proms.QUESTS_'+@TABLE+'  
            WHERE
                _Q1_PROXY_DATE BETWEEN \'\'\'+@YR1_START+\'\'\' AND \'\'\'+@YR1_END+\'\'\' 
                AND PROMS_PROC_CODE = ''HR''
                AND Q1_CS_SCORE IS NOT NULL
                AND Q2_CS_SCORE IS NOT NULL
                
        ) T1
        IF OBJECT_ID (''tempdb..#Provider'') IS NOT NULL DROP TABLE #Provider

        SELECT * INTO #Provider FROM
        (
        SELECT 
            [Financial Year] as ''Financial Year'',
            ''Extremely difficult or impossible to wash and dry yourself'' AS Question,
            CAST(CAST(CAST(COUNT(CASE WHEN HR_Q1_WASHING IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q1,
            CAST(CAST(CAST(COUNT(CASE WHEN HR_Q2_WASHING IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q2,
            _Q1_PROCODE AS PROVIDER
        FROM ##OHS
        GROUP BY _Q1_PROCODE, [Financial Year]

        UNION ALL

        SELECT
            [Financial Year] as ''Financial Year'',
            ''Extremely difficult or impossible to do household shopping on your own'' AS Question,
            CAST(CAST(CAST(COUNT(CASE WHEN HR_Q1_SHOPPING IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q1,
            CAST(CAST(CAST(COUNT(CASE WHEN HR_Q2_SHOPPING IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q2,
            _Q1_PROCODE AS PROVIDER
        FROM ##OHS
        GROUP BY _Q1_PROCODE, [Financial Year]

        UNION ALL

        SELECT
            [Financial Year] as ''Financial Year'',
            ''Extremely difficult or impossible to climb a flight of stairs'' AS Question,
            CAST(CAST(CAST(COUNT(CASE WHEN HR_Q1_STAIRS IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q1,
            CAST(CAST(CAST(COUNT(CASE WHEN HR_Q2_STAIRS IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q2,
            _Q1_PROCODE AS PROVIDER
        FROM ##OHS
        GROUP BY _Q1_PROCODE, [Financial Year]
            
        UNION ALL

        SELECT 
            [Financial Year] as ''Financial Year'',
            ''Extremely difficult or impossible to put on a pair of socks, stockings, or tights'' AS Question,
            CAST(CAST(CAST(COUNT(CASE WHEN HR_Q1_DRESSING IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q1,
            CAST(CAST(CAST(COUNT(CASE WHEN HR_Q2_DRESSING IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q2,
            _Q1_PROCODE AS PROVIDER
        FROM ##OHS
        GROUP BY _Q1_PROCODE, [Financial Year]
            
        UNION ALL

        SELECT
            [Financial Year] as ''Financial Year'',
            ''Extremely difficult or impossible to use car or public transport'' AS Question,
            CAST(CAST(CAST(COUNT(CASE WHEN HR_Q1_TRANSPORT IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q1,
            CAST(CAST(CAST(COUNT(CASE WHEN HR_Q2_TRANSPORT IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q2,
            _Q1_PROCODE AS PROVIDER
        FROM ##OHS
        GROUP BY _Q1_PROCODE, [Financial Year]
            
        UNION ALL

        SELECT
            [Financial Year] as ''Financial Year'',
            ''Limping when walking most or all of the time'' AS Question,
            CAST(CAST(CAST(COUNT(CASE WHEN HR_Q1_LIMPING IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q1,
            CAST(CAST(CAST(COUNT(CASE WHEN HR_Q2_LIMPING IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q2,
            _Q1_PROCODE AS PROVIDER
        FROM ##OHS
        GROUP BY _Q1_PROCODE, [Financial Year]
            
        UNION ALL

        SELECT
            [Financial Year] as ''Financial Year'',
            ''Can walk around the house only or not at all before hip pain becomes severe'' AS Question,
            CAST(CAST(CAST(COUNT(CASE WHEN HR_Q1_WALKING IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q1,
            CAST(CAST(CAST(COUNT(CASE WHEN HR_Q2_WALKING IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q2,
            _Q1_PROCODE AS PROVIDER
        FROM ##OHS
        GROUP BY _Q1_PROCODE, [Financial Year]
            
        UNION ALL

        SELECT
            [Financial Year] as ''Financial Year'',
            ''Very painful or unbearable to stand up from a chair'' AS Question,
            CAST(CAST(CAST(COUNT(CASE WHEN HR_Q1_STANDING IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q1,
            CAST(CAST(CAST(COUNT(CASE WHEN HR_Q2_STANDING IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q2,
            _Q1_PROCODE AS PROVIDER
        FROM ##OHS
        GROUP BY _Q1_PROCODE, [Financial Year]
            
        UNION ALL

        SELECT
            [Financial Year] as ''Financial Year'',
            ''Sudden severe pain on most days or every day'' AS Question,
            CAST(CAST(CAST(COUNT(CASE WHEN HR_Q1_SUDDEN_PAIN IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q1,
            CAST(CAST(CAST(COUNT(CASE WHEN HR_Q2_SUDDEN_PAIN IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q2,
            _Q1_PROCODE AS PROVIDER
        FROM ##OHS
        GROUP BY _Q1_PROCODE, [Financial Year]
            
        UNION ALL

        SELECT
            [Financial Year] as ''Financial Year'',
            ''Great or total interference with work from pain in hip'' AS Question,
            CAST(CAST(CAST(COUNT(CASE WHEN HR_Q1_WORK IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q1,
            CAST(CAST(CAST(COUNT(CASE WHEN HR_Q2_WORK IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q2,
            _Q1_PROCODE AS PROVIDER
        FROM ##OHS
        GROUP BY _Q1_PROCODE, [Financial Year]
            
        UNION ALL

        SELECT
            [Financial Year] as ''Financial Year'',
            ''Troubled by pain in hip when in bed on most nights or every night'' AS Question,
            CAST(CAST(CAST(COUNT(CASE WHEN HR_Q1_NIGHT_PAIN IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q1,
            CAST(CAST(CAST(COUNT(CASE WHEN HR_Q2_NIGHT_PAIN IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q2,
            _Q1_PROCODE AS PROVIDER
        FROM ##OHS
        GROUP BY _Q1_PROCODE, [Financial Year]
            
        UNION ALL

        SELECT
            [Financial Year] as ''Financial Year'',
            ''Usually moderate or severe pain from hip'' AS Question,
            CAST(CAST(CAST(COUNT(CASE WHEN HR_Q1_PAIN IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q1,
            CAST(CAST(CAST(COUNT(CASE WHEN HR_Q2_PAIN IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q2,
            _Q1_PROCODE AS PROVIDER
        FROM ##OHS
        GROUP BY _Q1_PROCODE, [Financial Year]
        )_

        IF OBJECT_ID (''tempdb..#England'') IS NOT NULL DROP TABLE #England

        SELECT * INTO #England FROM 
        (
        SELECT 
            [Financial Year] as ''Financial Year'',
            ''Extremely difficult or impossible to wash and dry yourself'' AS Question,
            CAST(CAST(CAST(COUNT(CASE WHEN HR_Q1_WASHING IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q1,
            CAST(CAST(CAST(COUNT(CASE WHEN HR_Q2_WASHING IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q2,
            ''ENGLAND'' AS PROVIDER
            
        FROM ##OHS
        GROUP BY [Financial Year]


        UNION ALL

        SELECT
            [Financial Year] as ''Financial Year'',
            ''Extremely difficult or impossible to do household shopping on your own'' AS Question,
            CAST(CAST(CAST(COUNT(CASE WHEN HR_Q1_SHOPPING IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q1,
            CAST(CAST(CAST(COUNT(CASE WHEN HR_Q2_SHOPPING IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q2,
            ''ENGLAND'' AS PROVIDER
            
        FROM ##OHS
        GROUP BY [Financial Year]


        UNION ALL

        SELECT
            [Financial Year] as ''Financial Year'',
            ''Extremely difficult or impossible to climb a flight of stairs'' AS Question,
            CAST(CAST(CAST(COUNT(CASE WHEN HR_Q1_STAIRS IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q1,
            CAST(CAST(CAST(COUNT(CASE WHEN HR_Q2_STAIRS IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q2,
            ''ENGLAND'' AS PROVIDER
            
        FROM ##OHS
        GROUP BY [Financial Year]
            
            
        UNION ALL

        SELECT 
            [Financial Year] as ''Financial Year'',
            ''Extremely difficult or impossible to put on a pair of socks, stockings, or tights'' AS Question,
            CAST(CAST(CAST(COUNT(CASE WHEN HR_Q1_DRESSING IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q1,
            CAST(CAST(CAST(COUNT(CASE WHEN HR_Q2_DRESSING IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q2,
            ''ENGLAND'' AS PROVIDER
            
        FROM ##OHS
        GROUP BY [Financial Year]
            
            
        UNION ALL

        SELECT
            [Financial Year] as ''Financial Year'',
            ''Extremely difficult or impossible to use car or public transport'' AS Question,
            CAST(CAST(CAST(COUNT(CASE WHEN HR_Q1_TRANSPORT IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q1,
            CAST(CAST(CAST(COUNT(CASE WHEN HR_Q2_TRANSPORT IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q2,
            ''ENGLAND'' AS PROVIDER
            
        FROM ##OHS
        GROUP BY [Financial Year]
            
            
        UNION ALL

        SELECT
            [Financial Year] as ''Financial Year'',
            ''Limping when walking most or all of the time'' AS Question,
            CAST(CAST(CAST(COUNT(CASE WHEN HR_Q1_LIMPING IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q1,
            CAST(CAST(CAST(COUNT(CASE WHEN HR_Q2_LIMPING IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q2,
            ''ENGLAND'' AS PROVIDER
            
        FROM ##OHS
        GROUP BY [Financial Year]
            
            
        UNION ALL

        SELECT
            [Financial Year] as ''Financial Year'',
            ''Can walk around the house only or not at all before hip pain becomes severe'' AS Question,
            CAST(CAST(CAST(COUNT(CASE WHEN HR_Q1_WALKING IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q1,
            CAST(CAST(CAST(COUNT(CASE WHEN HR_Q2_WALKING IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q2,
            ''ENGLAND'' AS PROVIDER
            
        FROM ##OHS
        GROUP BY [Financial Year]
            
            
        UNION ALL

        SELECT
            [Financial Year] as ''Financial Year'',
            ''Very painful or unbearable to stand up from a chair'' AS Question,
            CAST(CAST(CAST(COUNT(CASE WHEN HR_Q1_STANDING IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q1,
            CAST(CAST(CAST(COUNT(CASE WHEN HR_Q2_STANDING IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q2,
            ''ENGLAND'' AS PROVIDER
            
        FROM ##OHS
        GROUP BY [Financial Year]
            
            
        UNION ALL

        SELECT
            [Financial Year] as ''Financial Year'',
            ''Sudden severe pain on most days or every day'' AS Question,
            CAST(CAST(CAST(COUNT(CASE WHEN HR_Q1_SUDDEN_PAIN IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q1,
            CAST(CAST(CAST(COUNT(CASE WHEN HR_Q2_SUDDEN_PAIN IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q2,
            ''ENGLAND'' AS PROVIDER
            
        FROM ##OHS
        GROUP BY [Financial Year]
            
            
        UNION ALL

        SELECT
            [Financial Year] as ''Financial Year'',
            ''Great or total interference with work from pain in hip'' AS Question,
            CAST(CAST(CAST(COUNT(CASE WHEN HR_Q1_WORK IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q1,
            CAST(CAST(CAST(COUNT(CASE WHEN HR_Q2_WORK IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q2,
            ''ENGLAND'' AS PROVIDER
            
        FROM ##OHS
        GROUP BY [Financial Year]
            
            
        UNION ALL

        SELECT
            [Financial Year] as ''Financial Year'',
            ''Troubled by pain in hip when in bed on most nights or every night'' AS Question,
            CAST(CAST(CAST(COUNT(CASE WHEN HR_Q1_NIGHT_PAIN IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q1,
            CAST(CAST(CAST(COUNT(CASE WHEN HR_Q2_NIGHT_PAIN IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q2,
            ''ENGLAND'' AS PROVIDER
            
        FROM ##OHS
        GROUP BY [Financial Year]
            
            
        UNION ALL

        SELECT
            [Financial Year] as ''Financial Year'',
            ''Usually moderate or severe pain from hip'' AS Question,
            CAST(CAST(CAST(COUNT(CASE WHEN HR_Q1_PAIN IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q1,
            CAST(CAST(CAST(COUNT(CASE WHEN HR_Q2_PAIN IN (0,1) THEN 1 ELSE NULL END) AS DECIMAL(18,10)) / COUNT(*) * 100 AS DECIMAL(10,1)) AS VARCHAR(6)) AS Q2,
            ''ENGLAND'' AS PROVIDER
            
        FROM ##OHS
        GROUP BY [Financial Year]
        )_

        IF OBJECT_ID (''tempdb..#ALL'') IS NOT NULL DROP TABLE #ALL

        SELECT a.*, case when a.[PROVIDER]=''ENGLAND'' then ''England'' else b.OrgName end as ''NAME''
        INTO #ALL FROM
        (
        SELECT * FROM #Provider
        UNION ALL
        SELECT * FROM #England
        ) a 
        left join PROMS_PUBLICATION.proms.REF_ORGS_'+@TABLE+' as b
        on a.[PROVIDER]=b.OrgCode

        SELECT A.[Financial Year], A.PROVIDER, ''Oxford Hip Score'' AS ''Measure'', A.Question, A.Q1, A.Q2, 
            B.Q1 AS ''England Q1'', B.Q2 AS ''England Q2'', [NAME]
        FROM #ALL AS A
        LEFT JOIN #England AS B
        ON A.Question=B.Question AND A.[Financial Year]=B.[Financial Year] 

        DROP TABLE ##OHS
        ')
    '''
    return inquest_hr_str

def key_facts(FYEAR,DATE_TO,TABLE):
    keystr = f'''
    DECLARE @NINE INTEGER
    DECLARE @FYEAR  VARCHAR (4)
    DECLARE @END  VARCHAR (10)
    DECLARE @table VARCHAR (15)
    DECLARE @sql NVARCHAR(MAX)

    ----------------------- Update these variables as required --------------------------

    SET @NINE = '8388607'
	--CAST(0x7fffffff AS INT) -- numeric value to be suppressed
    SET @FYEAR = '{FYEAR}'	                 -- represents a financial year, the year selected is the first year of the period e.g. 2012-13 is @FYEAR 2012
	SET @END = '{DATE_TO}'				 -- year and month of the last month for this dateset
	SET @table = '{TABLE}'	         -- processing run with X suffix
    -------------------------------------------------------------------------------------
    SET NOCOUNT ON

    EXEC('
    SELECT * INTO ##proms_processing_KF1a
    FROM
    (
        SELECT 
                    Q.PROMS_PROC_CODE,Q._PRIM_REV_PROC_CODE,
                ''Provider'' AS [Organisation Type], 
                Q._Q1_PROCODE AS [Organisation Code],
                ''Index'' AS Measure,		
                CASE WHEN COUNT(Q.Q2_EQ5D_INDEX) BETWEEN 1 AND 5 
                        AND  COUNT(CASE WHEN Q.Q2_EQ5D_INDEX > Q.Q1_EQ5D_INDEX THEN ''I'' END)BETWEEN 1 AND 5 
                        THEN '+@NINE+'
                        ELSE COUNT(CASE WHEN Q.Q2_EQ5D_INDEX > Q.Q1_EQ5D_INDEX THEN ''I'' END) 
                END AS Improved,
                    
                CASE WHEN COUNT(Q.Q2_EQ5D_INDEX) BETWEEN 1 AND 5 
                        AND  COUNT(CASE WHEN Q.Q2_EQ5D_INDEX = Q.Q1_EQ5D_INDEX THEN ''S'' END) BETWEEN 1 AND 5 
                        THEN '+@NINE+'
                        ELSE COUNT(CASE WHEN Q.Q2_EQ5D_INDEX = Q.Q1_EQ5D_INDEX THEN ''S'' END) 
                END AS Unchanged,
                    
                CASE WHEN COUNT(Q.Q2_EQ5D_INDEX) BETWEEN 1 AND 5
                        AND  COUNT(CASE WHEN Q.Q2_EQ5D_INDEX < Q.Q1_EQ5D_INDEX THEN ''D'' END) BETWEEN 1 AND 5 
                        THEN '+@NINE+'
                        ELSE COUNT(CASE WHEN Q.Q2_EQ5D_INDEX < Q.Q1_EQ5D_INDEX THEN ''D'' END) 
                END AS Worsened,
                    
                CASE WHEN COUNT(Q.Q2_EQ5D_INDEX) BETWEEN 1 AND 5 
                        THEN '+@NINE+'
                        ELSE COUNT(Q.Q2_EQ5D_INDEX) 
                END AS TOTAL

        FROM proms.QUESTS_'+@table+' Q
        WHERE Q._Q1_FYEAR = \'\'\'+@FYEAR+\'\'\'
        AND Q._Q1_YEAR_MONTH <= \'\'\'+@END+\'\'\'
        AND Q._INDEX_CHANGE_FLAG = 1
        AND Q._Q1_PROCODE IS NOT NULL
        AND Q.PROMS_PROC_CODE in (''hr'',''kr'')
        GROUP BY  Q.PROMS_PROC_CODE,Q._PRIM_REV_PROC_CODE,Q._Q1_PROCODE

    UNION
    
        SELECT 
                Q.PROMS_PROC_CODE,Q._PRIM_REV_PROC_CODE,
                ''CCG of GP Practice'' AS [Organisation Type], 
                P.ccg_code AS [Organisation Code],
                ''Index'' AS Measure,
                CASE WHEN COUNT(Q.Q2_EQ5D_INDEX) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_EQ5D_INDEX > Q.Q1_EQ5D_INDEX THEN ''I'' END)BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_EQ5D_INDEX > Q.Q1_EQ5D_INDEX THEN ''I'' END) 
                END AS Improved,
                    
                CASE WHEN COUNT(Q.Q2_EQ5D_INDEX) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_EQ5D_INDEX = Q.Q1_EQ5D_INDEX THEN ''S'' END) BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_EQ5D_INDEX = Q.Q1_EQ5D_INDEX THEN ''S'' END)
                END AS Unchanged,
                    
                CASE WHEN COUNT(Q.Q2_EQ5D_INDEX) BETWEEN 1 AND 5
                    AND  COUNT(CASE WHEN Q.Q2_EQ5D_INDEX < Q.Q1_EQ5D_INDEX THEN ''D'' END) BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_EQ5D_INDEX < Q.Q1_EQ5D_INDEX THEN ''D'' END) 
                END AS Worsened,
                    
                CASE WHEN COUNT(Q.Q2_EQ5D_INDEX) BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(Q.Q2_EQ5D_INDEX) 
                END AS TOTAL

        FROM proms.QUESTS_'+@table+' Q
        LEFT JOIN proms.HES_PROCEDURES_'+@table+' P
        ON Q._P_REF_PROM = P._P_REF_PROM
        WHERE  Q._Q1_FYEAR = \'\'\'+@FYEAR+\'\'\'
        AND Q._Q1_YEAR_MONTH <= \'\'\'+@END+\'\'\'
        AND Q._INDEX_CHANGE_FLAG = 1
        AND P.ccg_code IS NOT NULL
        AND Q.PROMS_PROC_CODE in (''hr'',''kr'')
        GROUP BY  Q.PROMS_PROC_CODE,Q._PRIM_REV_PROC_CODE,P.ccg_code
    
    UNION
    
        SELECT 
                Q.PROMS_PROC_CODE,Q._PRIM_REV_PROC_CODE,
            ''England'' AS [Organisation Type], 
            ''England'' AS [Organisation Code],
            ''Index'' AS Measure,
            COUNT(CASE WHEN Q.Q2_EQ5D_INDEX > Q.Q1_EQ5D_INDEX THEN ''I'' END) AS Improved,
            COUNT(CASE WHEN Q.Q2_EQ5D_INDEX = Q.Q1_EQ5D_INDEX THEN ''S'' END) AS Unchanged,
            COUNT(CASE WHEN Q.Q2_EQ5D_INDEX < Q.Q1_EQ5D_INDEX THEN ''D'' END) AS Worsened,
            COUNT(Q.Q2_EQ5D_INDEX) AS TOTAL
            
    FROM proms.QUESTS_'+@table+' Q
    WHERE Q._Q1_FYEAR = \'\'\'+@FYEAR+\'\'\'
        AND Q._Q1_YEAR_MONTH <= \'\'\'+@END+\'\'\'
    AND Q._INDEX_CHANGE_FLAG = 1
    AND Q.PROMS_PROC_CODE in (''hr'',''kr'')
    GROUP BY Q.PROMS_PROC_CODE,Q._PRIM_REV_PROC_CODE
    
    UNION
        SELECT 
                Q.PROMS_PROC_CODE,Q._PRIM_REV_PROC_CODE,  
            ''Provider'' AS [Organisation Type],   
            Q._Q1_PROCODE AS [Organisation Code],
            ''VAS'' AS Measure,
            CASE WHEN COUNT(Q.Q2_EQ5D_HEALTH_SCALE) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE > Q.Q1_EQ5D_HEALTH_SCALE THEN ''I'' END)BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE > Q.Q1_EQ5D_HEALTH_SCALE THEN ''I'' END) 
            END AS Improved,
                
            CASE WHEN COUNT(Q.Q2_EQ5D_HEALTH_SCALE) BETWEEN 1 AND 5 
                AND  COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE = Q.Q1_EQ5D_HEALTH_SCALE THEN ''S'' END)BETWEEN 1 AND 5 
                THEN '+@NINE+'
                ELSE COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE = Q.Q1_EQ5D_HEALTH_SCALE THEN ''S'' END) 
            END AS Unchanged,
                
            CASE WHEN COUNT(Q.Q2_EQ5D_HEALTH_SCALE) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE < Q.Q1_EQ5D_HEALTH_SCALE THEN ''D'' END)BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE < Q.Q1_EQ5D_HEALTH_SCALE THEN ''D'' END) 
            END AS Worsened,
                
            CASE WHEN COUNT(Q.Q2_EQ5D_HEALTH_SCALE) BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(Q.Q2_EQ5D_HEALTH_SCALE) 
            END AS TOTAL

        FROM proms.QUESTS_'+@table+' Q
        WHERE  Q._Q1_FYEAR = \'\'\'+@FYEAR+\'\'\'
        AND Q._Q1_YEAR_MONTH <= \'\'\'+@END+\'\'\'
        AND Q._SCALE_CHANGE_FLAG = 1
        AND Q._Q1_PROCODE IS NOT NULL
        AND Q.PROMS_PROC_CODE in (''hr'',''kr'')
        GROUP BY Q._Q1_FYEAR, Q.PROMS_PROC_CODE,Q._PRIM_REV_PROC_CODE,Q._Q1_PROCODE
    
    UNION
    
        SELECT 
                Q.PROMS_PROC_CODE,Q._PRIM_REV_PROC_CODE,  
                ''CCG of GP Practice'' AS [Organisation Type], 
                P.ccg_code AS [Organisation Code],
                ''VAS'' AS Measure,
                CASE WHEN COUNT(Q.Q2_EQ5D_HEALTH_SCALE) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE > Q.Q1_EQ5D_HEALTH_SCALE THEN ''I'' END)BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE > Q.Q1_EQ5D_HEALTH_SCALE THEN ''I'' END) 
                END AS Improved,
                
                CASE WHEN COUNT(Q.Q2_EQ5D_HEALTH_SCALE) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE = Q.Q1_EQ5D_HEALTH_SCALE THEN ''S'' END)BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE = Q.Q1_EQ5D_HEALTH_SCALE THEN ''S'' END) 
                END AS Unchanged,
                
                CASE WHEN COUNT(Q.Q2_EQ5D_HEALTH_SCALE) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE < Q.Q1_EQ5D_HEALTH_SCALE THEN ''D'' END)BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE < Q.Q1_EQ5D_HEALTH_SCALE THEN ''D'' END) 
                END AS Worsened,
                
                CASE WHEN COUNT(Q.Q2_EQ5D_HEALTH_SCALE) BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(Q.Q2_EQ5D_HEALTH_SCALE) 
                END AS TOTAL

        FROM proms.QUESTS_'+@table+' Q
        LEFT JOIN proms.HES_PROCEDURES_'+@table+' P
        ON Q._P_REF_PROM = P._P_REF_PROM
        WHERE  Q._Q1_FYEAR = \'\'\'+@FYEAR+\'\'\'
        AND Q._Q1_YEAR_MONTH <= \'\'\'+@END+\'\'\'
        AND Q._SCALE_CHANGE_FLAG = 1
        AND P.ccg_code IS NOT NULL
        AND Q.PROMS_PROC_CODE in (''hr'',''kr'')
        GROUP BY  Q.PROMS_PROC_CODE,Q._PRIM_REV_PROC_CODE,P.ccg_code

    UNION
    
        SELECT 
                Q.PROMS_PROC_CODE,Q._PRIM_REV_PROC_CODE,  
                ''England'' AS [Organisation Type], 
                ''England'' AS [Organisation Code],
                ''VAS'' AS Measure,
                COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE > Q.Q1_EQ5D_HEALTH_SCALE THEN ''I'' END) AS Improved,
                COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE = Q.Q1_EQ5D_HEALTH_SCALE THEN ''S'' END) AS Unchanged,
                COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE < Q.Q1_EQ5D_HEALTH_SCALE THEN ''D'' END) AS Worsened,
                COUNT(Q.Q2_EQ5D_HEALTH_SCALE) AS TOTAL
            
        FROM proms.QUESTS_'+@table+' Q
        WHERE  Q._Q1_FYEAR = \'\'\'+@FYEAR+\'\'\'
        AND Q._Q1_YEAR_MONTH <= \'\'\'+@END+\'\'\'
        AND Q._SCALE_CHANGE_FLAG = 1
        AND Q.PROMS_PROC_CODE in (''hr'',''kr'')
        GROUP BY Q.PROMS_PROC_CODE,Q._PRIM_REV_PROC_CODE
            
    UNION
        SELECT 
                Q.PROMS_PROC_CODE,Q._PRIM_REV_PROC_CODE,  
                ''Provider'' AS [Organisation Type], 	 
                Q._Q1_PROCODE AS [Organisation Code],
                Q._CS_CODE AS Measure,
                CASE WHEN COUNT(Q.Q2_CS_SCORE) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                    OR Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV'' THEN ''I'' END) BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                        OR Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV'' THEN ''I'' END) 
                END AS Improved,
                        
                CASE WHEN COUNT(Q.Q2_CS_SCORE) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_CS_SCORE = Q.Q1_CS_SCORE THEN ''S'' END) BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_CS_SCORE = Q.Q1_CS_SCORE THEN ''S'' END) 
                END AS Unchanged,
                
                CASE WHEN COUNT(Q.Q2_CS_SCORE) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                    OR Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV'' THEN ''D'' END) BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                    OR Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV'' THEN ''D'' END) 
                END AS Worsened,
                        
                CASE WHEN COUNT(Q.Q2_CS_SCORE) BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(Q.Q2_CS_SCORE) 
                END AS TOTAL
                        
        FROM proms.QUESTS_'+@table+' Q
        WHERE Q.PROMS_PROC_CODE IN (''hr'',''kr'')
        AND Q._Q1_FYEAR = \'\'\'+@FYEAR+\'\'\'
        AND Q._Q1_YEAR_MONTH <= \'\'\'+@END+\'\'\'
        AND Q._SCORE_CHANGE_FLAG = 1
        AND Q._Q1_PROCODE IS NOT NULL
        GROUP BY  Q.PROMS_PROC_CODE,Q._PRIM_REV_PROC_CODE, Q._Q1_PROCODE,Q._CS_CODE
        
    UNION
    
        SELECT 
                    Q.PROMS_PROC_CODE,Q._PRIM_REV_PROC_CODE,  
                    ''CCG of GP Practice'' AS [Organisation Type],	
                    P.ccg_code AS [Organisation Code],
                    Q._CS_CODE AS Measure,
                    CASE WHEN COUNT(Q.Q2_CS_SCORE) BETWEEN 1 AND 5 
                        AND  COUNT(CASE WHEN Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                        OR Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV'' THEN ''I'' END) BETWEEN 1 AND 5 
                        THEN '+@NINE+'
                        ELSE COUNT(CASE WHEN Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                        OR Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV'' THEN ''I'' END) 
                    END AS Improved,
                            
                    CASE WHEN COUNT(Q.Q2_CS_SCORE) BETWEEN 1 AND 5 
                        AND COUNT(CASE WHEN Q.Q2_CS_SCORE = Q.Q1_CS_SCORE THEN ''S'' END) BETWEEN 1 AND 5 
                        THEN '+@NINE+'
                        ELSE COUNT(CASE WHEN Q.Q2_CS_SCORE = Q.Q1_CS_SCORE THEN ''S'' END) 
                    END AS Unchanged,
                    
                    CASE WHEN COUNT(Q.Q2_CS_SCORE) BETWEEN 1 AND 5 
                        AND  COUNT(CASE WHEN Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                        OR Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV'' THEN ''D'' END) BETWEEN 1 AND 5 
                        THEN '+@NINE+'
                        ELSE COUNT(CASE WHEN Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                        OR   Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV''THEN ''D'' END) 
                    END AS Worsened,
                            
                    CASE WHEN COUNT(Q.Q2_CS_SCORE) BETWEEN 1 AND 5 
                        THEN '+@NINE+'
                        ELSE COUNT(Q.Q2_CS_SCORE) 
                    END AS TOTAL
                    
        FROM proms.QUESTS_'+@table+' Q
        LEFT JOIN proms.HES_PROCEDURES_'+@table+' P
        ON Q._P_REF_PROM = P._P_REF_PROM
        WHERE Q.PROMS_PROC_CODE IN (''hr'',''kr'')
        AND Q._Q1_FYEAR = \'\'\'+@FYEAR+\'\'\'
        AND Q._Q1_YEAR_MONTH <= \'\'\'+@END+\'\'\'
        AND Q._SCORE_CHANGE_FLAG = 1
        AND P.ccg_code IS NOT NULL
        GROUP BY  Q.PROMS_PROC_CODE,Q._PRIM_REV_PROC_CODE,P.ccg_code,Q._CS_CODE
        
    UNION
    
        SELECT 
                    Q.PROMS_PROC_CODE,Q._PRIM_REV_PROC_CODE,  
                    ''England'' AS [Organisation Type], 
                    ''England'' AS [Organisation Code],
                    Q._CS_CODE AS Measure,

                    COUNT(CASE WHEN Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                    OR Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV'' THEN ''I'' END) AS Improved,

                    COUNT(CASE WHEN Q.Q2_CS_SCORE = Q.Q1_CS_SCORE THEN ''S'' END) AS Unchanged,

                    COUNT(CASE WHEN Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                    OR Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV'' THEN ''D'' END) AS Worsened,

                    COUNT(Q.Q2_CS_SCORE) AS TOTAL
                
        FROM proms.QUESTS_'+@table+' Q
        WHERE Q.PROMS_PROC_CODE IN (''hr'',''kr'')
        AND Q._Q1_FYEAR = \'\'\'+@FYEAR+\'\'\'
        AND Q._Q1_YEAR_MONTH <= \'\'\'+@END+\'\'\'
        AND Q._SCORE_CHANGE_FLAG = 1
        GROUP BY  Q.PROMS_PROC_CODE,Q._PRIM_REV_PROC_CODE,Q._CS_CODE
    )_


    SELECT * INTO ##proms_processing_KF1b
    FROM
    (
        SELECT 
                    Q.PROMS_PROC_CODE,
                ''Provider'' AS [Organisation Type], 
                Q._Q1_PROCODE AS [Organisation Code],
                ''Index'' AS Measure,		
                CASE WHEN COUNT(Q.Q2_EQ5D_INDEX) BETWEEN 1 AND 5 
                        AND  COUNT(CASE WHEN Q.Q2_EQ5D_INDEX > Q.Q1_EQ5D_INDEX THEN ''I'' END)BETWEEN 1 AND 5 
                        THEN '+@NINE+'
                        ELSE COUNT(CASE WHEN Q.Q2_EQ5D_INDEX > Q.Q1_EQ5D_INDEX THEN ''I'' END) 
                END AS Improved,
                    
                CASE WHEN COUNT(Q.Q2_EQ5D_INDEX) BETWEEN 1 AND 5 
                        AND  COUNT(CASE WHEN Q.Q2_EQ5D_INDEX = Q.Q1_EQ5D_INDEX THEN ''S'' END) BETWEEN 1 AND 5 
                        THEN '+@NINE+'
                        ELSE COUNT(CASE WHEN Q.Q2_EQ5D_INDEX = Q.Q1_EQ5D_INDEX THEN ''S'' END) 
                END AS Unchanged,
                    
                CASE WHEN COUNT(Q.Q2_EQ5D_INDEX) BETWEEN 1 AND 5
                        AND  COUNT(CASE WHEN Q.Q2_EQ5D_INDEX < Q.Q1_EQ5D_INDEX THEN ''D'' END) BETWEEN 1 AND 5 
                        THEN '+@NINE+'
                        ELSE COUNT(CASE WHEN Q.Q2_EQ5D_INDEX < Q.Q1_EQ5D_INDEX THEN ''D'' END) 
                END AS Worsened,
                    
                CASE WHEN COUNT(Q.Q2_EQ5D_INDEX) BETWEEN 1 AND 5 
                        THEN '+@NINE+'
                        ELSE COUNT(Q.Q2_EQ5D_INDEX) 
                END AS TOTAL

        FROM proms.QUESTS_'+@table+' Q
        WHERE Q._Q1_FYEAR = \'\'\'+@FYEAR+\'\'\'
        AND Q._Q1_YEAR_MONTH <= \'\'\'+@END+\'\'\'
        AND Q._INDEX_CHANGE_FLAG = 1
        AND Q._Q1_PROCODE IS NOT NULL
        AND Q.PROMS_PROC_CODE in (''hr'',''kr'')
        GROUP BY  Q.PROMS_PROC_CODE,Q._Q1_PROCODE

    UNION
    
        SELECT 
                Q.PROMS_PROC_CODE,
                ''CCG of GP Practice'' AS [Organisation Type], 
                P.ccg_code AS [Organisation Code],
                ''Index'' AS Measure,
                CASE WHEN COUNT(Q.Q2_EQ5D_INDEX) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_EQ5D_INDEX > Q.Q1_EQ5D_INDEX THEN ''I'' END)BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_EQ5D_INDEX > Q.Q1_EQ5D_INDEX THEN ''I'' END) 
                END AS Improved,
                    
                CASE WHEN COUNT(Q.Q2_EQ5D_INDEX) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_EQ5D_INDEX = Q.Q1_EQ5D_INDEX THEN ''S'' END) BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_EQ5D_INDEX = Q.Q1_EQ5D_INDEX THEN ''S'' END)
                END AS Unchanged,
                    
                CASE WHEN COUNT(Q.Q2_EQ5D_INDEX) BETWEEN 1 AND 5
                    AND  COUNT(CASE WHEN Q.Q2_EQ5D_INDEX < Q.Q1_EQ5D_INDEX THEN ''D'' END) BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_EQ5D_INDEX < Q.Q1_EQ5D_INDEX THEN ''D'' END) 
                END AS Worsened,
                    
                CASE WHEN COUNT(Q.Q2_EQ5D_INDEX) BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(Q.Q2_EQ5D_INDEX) 
                END AS TOTAL

        FROM proms.QUESTS_'+@table+' Q
        LEFT JOIN proms.HES_PROCEDURES_'+@table+' P
        ON Q._P_REF_PROM = P._P_REF_PROM
        WHERE  Q._Q1_FYEAR = \'\'\'+@FYEAR+\'\'\'
        AND Q._Q1_YEAR_MONTH <= \'\'\'+@END+\'\'\'
        AND Q._INDEX_CHANGE_FLAG = 1
        AND P.ccg_code IS NOT NULL
        AND Q.PROMS_PROC_CODE in (''hr'',''kr'')
        GROUP BY  Q.PROMS_PROC_CODE,P.ccg_code
    
    UNION
    
        SELECT 
                Q.PROMS_PROC_CODE,
            ''England'' AS [Organisation Type], 
            ''England'' AS [Organisation Code],
            ''Index'' AS Measure,
            COUNT(CASE WHEN Q.Q2_EQ5D_INDEX > Q.Q1_EQ5D_INDEX THEN ''I'' END) AS Improved,
            COUNT(CASE WHEN Q.Q2_EQ5D_INDEX = Q.Q1_EQ5D_INDEX THEN ''S'' END) AS Unchanged,
            COUNT(CASE WHEN Q.Q2_EQ5D_INDEX < Q.Q1_EQ5D_INDEX THEN ''D'' END) AS Worsened,
            COUNT(Q.Q2_EQ5D_INDEX) AS TOTAL
            
    FROM proms.QUESTS_'+@table+' Q
    WHERE Q._Q1_FYEAR = \'\'\'+@FYEAR+\'\'\'
        AND Q._Q1_YEAR_MONTH <= \'\'\'+@END+\'\'\'
    AND Q._INDEX_CHANGE_FLAG = 1
    AND Q.PROMS_PROC_CODE in (''hr'',''kr'')
    GROUP BY Q.PROMS_PROC_CODE
    
    UNION
        SELECT 
                Q.PROMS_PROC_CODE, 
            ''Provider'' AS [Organisation Type],   
            Q._Q1_PROCODE AS [Organisation Code],
            ''VAS'' AS Measure,
            CASE WHEN COUNT(Q.Q2_EQ5D_HEALTH_SCALE) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE > Q.Q1_EQ5D_HEALTH_SCALE THEN ''I'' END)BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE > Q.Q1_EQ5D_HEALTH_SCALE THEN ''I'' END) 
            END AS Improved,
                
            CASE WHEN COUNT(Q.Q2_EQ5D_HEALTH_SCALE) BETWEEN 1 AND 5 
                AND  COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE = Q.Q1_EQ5D_HEALTH_SCALE THEN ''S'' END)BETWEEN 1 AND 5 
                THEN '+@NINE+'
                ELSE COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE = Q.Q1_EQ5D_HEALTH_SCALE THEN ''S'' END) 
            END AS Unchanged,
                
            CASE WHEN COUNT(Q.Q2_EQ5D_HEALTH_SCALE) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE < Q.Q1_EQ5D_HEALTH_SCALE THEN ''D'' END)BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE < Q.Q1_EQ5D_HEALTH_SCALE THEN ''D'' END) 
            END AS Worsened,
                
            CASE WHEN COUNT(Q.Q2_EQ5D_HEALTH_SCALE) BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(Q.Q2_EQ5D_HEALTH_SCALE) 
            END AS TOTAL

        FROM proms.QUESTS_'+@table+' Q
        WHERE  Q._Q1_FYEAR = \'\'\'+@FYEAR+\'\'\'
        AND Q._Q1_YEAR_MONTH <= \'\'\'+@END+\'\'\'
        AND Q._SCALE_CHANGE_FLAG = 1
        AND Q._Q1_PROCODE IS NOT NULL
        AND Q.PROMS_PROC_CODE in (''hr'',''kr'')
        GROUP BY Q._Q1_FYEAR, Q.PROMS_PROC_CODE,Q._Q1_PROCODE
    
    UNION
    
        SELECT 
                Q.PROMS_PROC_CODE,
                ''CCG of GP Practice'' AS [Organisation Type], 
                P.ccg_code AS [Organisation Code],
                ''VAS'' AS Measure,
                CASE WHEN COUNT(Q.Q2_EQ5D_HEALTH_SCALE) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE > Q.Q1_EQ5D_HEALTH_SCALE THEN ''I'' END)BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE > Q.Q1_EQ5D_HEALTH_SCALE THEN ''I'' END) 
                END AS Improved,
                
                CASE WHEN COUNT(Q.Q2_EQ5D_HEALTH_SCALE) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE = Q.Q1_EQ5D_HEALTH_SCALE THEN ''S'' END)BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE = Q.Q1_EQ5D_HEALTH_SCALE THEN ''S'' END) 
                END AS Unchanged,
                
                CASE WHEN COUNT(Q.Q2_EQ5D_HEALTH_SCALE) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE < Q.Q1_EQ5D_HEALTH_SCALE THEN ''D'' END)BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE < Q.Q1_EQ5D_HEALTH_SCALE THEN ''D'' END) 
                END AS Worsened,
                
                CASE WHEN COUNT(Q.Q2_EQ5D_HEALTH_SCALE) BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(Q.Q2_EQ5D_HEALTH_SCALE) 
                END AS TOTAL

        FROM proms.QUESTS_'+@table+' Q
        LEFT JOIN proms.HES_PROCEDURES_'+@table+' P
        ON Q._P_REF_PROM = P._P_REF_PROM
        WHERE  Q._Q1_FYEAR = \'\'\'+@FYEAR+\'\'\'
        AND Q._Q1_YEAR_MONTH <= \'\'\'+@END+\'\'\'
        AND Q._SCALE_CHANGE_FLAG = 1
        AND P.ccg_code IS NOT NULL
        AND Q.PROMS_PROC_CODE in (''hr'',''kr'')
        GROUP BY  Q.PROMS_PROC_CODE,P.ccg_code

    UNION
    
        SELECT 
                Q.PROMS_PROC_CODE, 
                ''England'' AS [Organisation Type], 
                ''England'' AS [Organisation Code],
                ''VAS'' AS Measure,
                COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE > Q.Q1_EQ5D_HEALTH_SCALE THEN ''I'' END) AS Improved,
                COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE = Q.Q1_EQ5D_HEALTH_SCALE THEN ''S'' END) AS Unchanged,
                COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE < Q.Q1_EQ5D_HEALTH_SCALE THEN ''D'' END) AS Worsened,
                COUNT(Q.Q2_EQ5D_HEALTH_SCALE) AS TOTAL
            
        FROM proms.QUESTS_'+@table+' Q
        WHERE  Q._Q1_FYEAR = \'\'\'+@FYEAR+\'\'\'
        AND Q._Q1_YEAR_MONTH <= \'\'\'+@END+\'\'\'
        AND Q._SCALE_CHANGE_FLAG = 1
        AND Q.PROMS_PROC_CODE in (''hr'',''kr'')
        GROUP BY Q.PROMS_PROC_CODE
            
    UNION
        SELECT 
                Q.PROMS_PROC_CODE,
                ''Provider'' AS [Organisation Type], 	 
                Q._Q1_PROCODE AS [Organisation Code],
                Q._CS_CODE AS Measure,
                CASE WHEN COUNT(Q.Q2_CS_SCORE) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                    OR Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV'' THEN ''I'' END) BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                        OR Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV'' THEN ''I'' END) 
                END AS Improved,
                        
                CASE WHEN COUNT(Q.Q2_CS_SCORE) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_CS_SCORE = Q.Q1_CS_SCORE THEN ''S'' END) BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_CS_SCORE = Q.Q1_CS_SCORE THEN ''S'' END) 
                END AS Unchanged,
                
                CASE WHEN COUNT(Q.Q2_CS_SCORE) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                    OR Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV'' THEN ''D'' END) BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                    OR Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV'' THEN ''D'' END) 
                END AS Worsened,
                        
                CASE WHEN COUNT(Q.Q2_CS_SCORE) BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(Q.Q2_CS_SCORE) 
                END AS TOTAL
                        
        FROM proms.QUESTS_'+@table+' Q
        WHERE Q.PROMS_PROC_CODE IN (''hr'',''kr'')
        AND Q._Q1_FYEAR = \'\'\'+@FYEAR+\'\'\'
        AND Q._Q1_YEAR_MONTH <= \'\'\'+@END+\'\'\'
        AND Q._SCORE_CHANGE_FLAG = 1
        AND Q._Q1_PROCODE IS NOT NULL
        GROUP BY  Q.PROMS_PROC_CODE, Q._Q1_PROCODE,Q._CS_CODE
        
    UNION
    
        SELECT 
                    Q.PROMS_PROC_CODE, 
                    ''CCG of GP Practice'' AS [Organisation Type],	
                    P.ccg_code AS [Organisation Code],
                    Q._CS_CODE AS Measure,
                    CASE WHEN COUNT(Q.Q2_CS_SCORE) BETWEEN 1 AND 5 
                        AND  COUNT(CASE WHEN Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                        OR Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV'' THEN ''I'' END) BETWEEN 1 AND 5 
                        THEN '+@NINE+'
                        ELSE COUNT(CASE WHEN Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                        OR Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV'' THEN ''I'' END) 
                    END AS Improved,
                            
                    CASE WHEN COUNT(Q.Q2_CS_SCORE) BETWEEN 1 AND 5 
                        AND COUNT(CASE WHEN Q.Q2_CS_SCORE = Q.Q1_CS_SCORE THEN ''S'' END) BETWEEN 1 AND 5 
                        THEN '+@NINE+'
                        ELSE COUNT(CASE WHEN Q.Q2_CS_SCORE = Q.Q1_CS_SCORE THEN ''S'' END) 
                    END AS Unchanged,
                    
                    CASE WHEN COUNT(Q.Q2_CS_SCORE) BETWEEN 1 AND 5 
                        AND  COUNT(CASE WHEN Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                        OR Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV'' THEN ''D'' END) BETWEEN 1 AND 5 
                        THEN '+@NINE+'
                        ELSE COUNT(CASE WHEN Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                        OR   Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV''THEN ''D'' END) 
                    END AS Worsened,
                            
                    CASE WHEN COUNT(Q.Q2_CS_SCORE) BETWEEN 1 AND 5 
                        THEN '+@NINE+'
                        ELSE COUNT(Q.Q2_CS_SCORE) 
                    END AS TOTAL
                    
        FROM proms.QUESTS_'+@table+' Q
        LEFT JOIN proms.HES_PROCEDURES_'+@table+' P
        ON Q._P_REF_PROM = P._P_REF_PROM
        WHERE Q.PROMS_PROC_CODE IN (''hr'',''kr'')
        AND Q._Q1_FYEAR = \'\'\'+@FYEAR+\'\'\'
        AND Q._Q1_YEAR_MONTH <= \'\'\'+@END+\'\'\'
        AND Q._SCORE_CHANGE_FLAG = 1
        AND P.ccg_code IS NOT NULL
        GROUP BY  Q.PROMS_PROC_CODE,P.ccg_code,Q._CS_CODE
        
    UNION
    
        SELECT 
                    Q.PROMS_PROC_CODE,
                    ''England'' AS [Organisation Type], 
                    ''England'' AS [Organisation Code],
                    Q._CS_CODE AS Measure,

                    COUNT(CASE WHEN Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                    OR Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV'' THEN ''I'' END) AS Improved,

                    COUNT(CASE WHEN Q.Q2_CS_SCORE = Q.Q1_CS_SCORE THEN ''S'' END) AS Unchanged,

                    COUNT(CASE WHEN Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                    OR Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV'' THEN ''D'' END) AS Worsened,

                    COUNT(Q.Q2_CS_SCORE) AS TOTAL
                
        FROM proms.QUESTS_'+@table+' Q
        WHERE Q.PROMS_PROC_CODE IN (''hr'',''kr'')
        AND Q._Q1_FYEAR = \'\'\'+@FYEAR+\'\'\'
        AND Q._Q1_YEAR_MONTH <= \'\'\'+@END+\'\'\'
        AND Q._SCORE_CHANGE_FLAG = 1
        GROUP BY  Q.PROMS_PROC_CODE,Q._CS_CODE
    ) KF1

    SELECT * INTO ##proms_processing_KF2
    FROM
    (
    SELECT
            RP.[Description] AS [Procedure],
            K.[Organisation Type],
            [Organisation Code],
        
            CASE WHEN K.[Organisation Type]= ''England'' THEN ''England''
                WHEN K.[Organisation Type]= ''CCG of GP Practice'' AND K.[Organisation Code]= ''---'' THEN ''Unknown''
                ELSE ISNULL(O.OrgName,''Unknown'')
            END AS [Organsation Name],
        
            RM.[Description] AS [Measure],
            K.[Improved],
            K.[Unchanged],
            K.[Worsened],
            K.[Total],
            CASE WHEN K.[Organisation Type] = ''Provider'' AND K.[Improved] = '+@NINE+' THEN RP.[Description]+RM.[Description] END AS IFLAG,
            CASE WHEN K.[Organisation Type] = ''Provider'' AND K.[Unchanged] = '+@NINE+' THEN RP.[Description]+RM.[Description] END AS UFLAG,
            CASE WHEN K.[Organisation Type] = ''Provider'' AND K.[Worsened] = '+@NINE+' THEN RP.[Description]+RM.[Description] END AS WFLAG
        
    FROM ##proms_processing_KF1b K
    LEFT JOIN proms.REF_ORGS_'+@table+' O
    ON o.OrgCode = K.[Organisation Code]
    LEFT JOIN proms.REF_PROCEDURES RP
    ON K.PROMS_PROC_CODE = RP.PROMs_PROC_CODE
    LEFT JOIN proms.REF_MEASURES RM
    ON K.[Measure] = RM.Measure

    union

    SELECT
            RP.[Description] AS [Procedure],
            K.[Organisation Type],
            [Organisation Code],
        
            CASE WHEN K.[Organisation Type]= ''England'' THEN ''England''
                WHEN K.[Organisation Type]= ''CCG of GP Practice'' AND K.[Organisation Code]= ''---'' THEN ''Unknown''
                ELSE ISNULL(O.OrgName,''Unknown'')
            END AS [Organsation Name],
        
            RM.[Description] AS [Measure],
            K.[Improved],
            K.[Unchanged],
            K.[Worsened],
            K.[Total],
            CASE WHEN K.[Organisation Type] = ''Provider'' AND K.[Improved] = '+@NINE+' THEN RP.[Description]+RM.[Description] END AS IFLAG,
            CASE WHEN K.[Organisation Type] = ''Provider'' AND K.[Unchanged] = '+@NINE+' THEN RP.[Description]+RM.[Description] END AS UFLAG,
            CASE WHEN K.[Organisation Type] = ''Provider'' AND K.[Worsened] = '+@NINE+' THEN RP.[Description]+RM.[Description] END AS WFLAG
        
    FROM ##proms_processing_KF1a K
    LEFT JOIN proms.REF_ORGS_'+@table+' O
    ON o.OrgCode = K.[Organisation Code]
    LEFT JOIN proms.REF_PROCEDURES RP
    ON K._PRIM_REV_PROC_CODE = RP.PROMs_PROC_CODE
    LEFT JOIN proms.REF_MEASURES RM
    ON K.[Measure] = RM.Measure
    where k._PRIM_REV_PROC_CODE not in (''hr'',''kr'')


    )KF2

    DROP TABLE ##proms_processing_KF1a
    DROP TABLE ##proms_processing_KF1b

    --Contains all the Improved Flags that need secondary suppression
    SELECT * INTO #KFX
    FROM
    (
    SELECT
        CASE WHEN COUNT('+@NINE+') OVER (PARTITION BY IFLAG) = 1 
            THEN IFLAG END AS IFLAG
    FROM ##proms_processing_KF2)KFX
    --Contains all the Unchanged Flags that need secondary suppression
    SELECT * INTO #KFY
    FROM
    (
    SELECT
        CASE WHEN COUNT('+@NINE+') OVER (PARTITION BY UFLAG) = 1 
            THEN UFLAG END AS UFLAG
    FROM ##proms_processing_KF2)KFY
    --Contains all the Worsened Flags that need secondary suppression
    SELECT * INTO #KFZ
    FROM
    (
    SELECT
        CASE WHEN COUNT('+@NINE+') OVER (PARTITION BY WFLAG) = 1 
            THEN WFLAG END AS WFLAG
    FROM ##proms_processing_KF2)KFZ

    SELECT * INTO #KF3
    FROM
    (
        SELECT 
                CASE WHEN KF2.[Organisation Type] = ''England''
                    THEN KF2.[Organisation Type]+KF2.[Organsation Name]+KF2.[Procedure]+KF2.[Measure]
                    ELSE KF2.[Organisation Type]+KF2.[Organsation Name]+'' (''+KF2.[Organisation Code]+'')''+KF2.[Procedure]+KF2.[Measure]
                END AS [Lookup],
                KF2.[Procedure],
                KF2.[Organisation Type],
                KF2.[Organisation Code],
                KF2.[Organsation Name],
                KF2.[Measure],
                KF2.[Improved],
                KF2.[Unchanged],
                KF2.[Worsened],
                KF2.[Total],
                KFX.IFLAG,
                KFY.UFLAG,
                KFZ.WFLAG

        FROM ##proms_processing_KF2 KF2
        LEFT JOIN #KFX KFX
        ON KF2.IFLAG = KFX.IFLAG
        LEFT JOIN #KFY KFY
        ON KF2.UFLAG = KFY.UFLAG
        LEFT JOIN #KFZ KFZ
        ON KF2.WFLAG = KFZ.WFLAG
    )KF3

    DROP TABLE ##proms_processing_KF2
    DROP TABLE #KFX
    DROP TABLE #KFY
    DROP TABLE #KFZ


    --Applies secondary suppression for Provider Improved, if needed
    --Identifies Procedures and Measures to be supressed

    SELECT * INTO #IFLAG
    FROM
    (
        SELECT
            IFLAG
        FROM #KF3 
        WHERE IFLAG IS NOT NULL
    )KF3A

    --Applies suppression to seleced dataset and joins to main data set
    SELECT 
            [Lookup],
            [Procedure],
            [Organisation Type],
            [Organisation Code],
            [Organsation Name],
            [Measure],
            CASE WHEN IFLAG IS NOT NULL AND CLASS = 1 THEN '+@NINE+' ELSE [Improved] END AS [Improved],
            [Unchanged],
            [Worsened],
            CASE WHEN IFLAG IS NOT NULL AND CLASS = 1 THEN '+@NINE+' ELSE [Total] END AS [Total],
            IFLAG,
            UFLAG,
            WFLAG
    INTO #KF4
    FROM
    (
        SELECT 
                KF3B.[Lookup],
                KF3B.[Procedure],
                KF3B.[Organisation Type],
                KF3B.[Organisation Code],
                KF3B.[Organsation Name],
                KF3B.[Measure],
                KF3B.[Improved],
                KF3B.[Unchanged],
                KF3B.[Worsened],
                KF3B.[Total],
                KF3A.IFLAG,
                KF3B.UFLAG,
                KF3B.WFLAG,
                ROW_NUMBER()OVER(PARTITION BY [Procedure], [Measure]
                                    ORDER BY [Total]ASC)AS CLASS
        FROM #KF3 KF3B
        LEFT JOIN #IFLAG KF3A
        ON KF3A.IFLAG = KF3B.[Procedure]+KF3B.Measure
        WHERE KF3B.WFLAG IS NULL
        AND KF3B.[Organisation Type]= ''Provider''
        AND KF3B.Improved > 0
        AND KF3B.Improved < '+@NINE+'
    )_

    UNION

    SELECT 
            [Lookup],
            [Procedure],
            [Organisation Type],
            [Organisation Code],
            [Organsation Name],
            [Measure],
            [Improved],
            [Unchanged],
            [Worsened],
            [Total],
            IFLAG,
            UFLAG,
            WFLAG 
    FROM #KF3
    WHERE [Lookup] NOT IN
    (
        SELECT 
            KF3B.[Lookup]
            FROM #KF3 KF3B
            LEFT JOIN #IFLAG KF3A
            ON KF3A.IFLAG = KF3B.[Procedure]+KF3B.Measure
            WHERE KF3B.WFLAG IS NULL
            AND KF3B.[Organisation Type]= ''Provider''
            AND KF3B.Improved > 0
            AND KF3B.Improved < '+@NINE+'
    )

    DROP TABLE #KF3
    DROP TABLE #IFLAG


    --SELECT * FROM #KF4
    --DROP TABLE #KF4
    --Applies secondary suppression for Provider Unchanged, if needed
    --Identifies Procedures and Measures to be supressed

    SELECT * INTO #UFLAG
    FROM
    (
        SELECT
            UFLAG
        FROM #KF4 
        WHERE UFLAG IS NOT NULL
    )KF4A


    --SELECT * FROM #UFLAG
    --Applies suppression to seleced dataset and joins to main data set
    SELECT 
            [Lookup],
            [Procedure],
            [Organisation Type],
            [Organisation Code],
            [Organsation Name],
            [Measure],
            [Improved],
            CASE WHEN UFLAG IS NOT NULL AND CLASS = 1 THEN '+@NINE+' ELSE [Unchanged] END AS [Unchanged],
            [Worsened],
            CASE WHEN UFLAG IS NOT NULL AND CLASS = 1 THEN '+@NINE+' ELSE [Total] END AS [Total],
            IFLAG,
            UFLAG,
            WFLAG
    INTO #KF5
    FROM
    (
        SELECT 
            KF4B.[Lookup],
            KF4B.[Procedure],
            KF4B.[Organisation Type],
            KF4B.[Organisation Code],
            KF4B.[Organsation Name],
            KF4B.[Measure],
            KF4B.[Improved],
            KF4B.[Unchanged],
            KF4B.[Worsened],
            KF4B.[Total],
            KF4B.IFLAG,
            KF4A.UFLAG,
            KF4B.WFLAG,
            ROW_NUMBER()OVER(PARTITION BY [Procedure], [Measure]
                                ORDER BY [Total]ASC)AS CLASS
        FROM #KF4 KF4B
        LEFT JOIN #UFLAG KF4A
        ON KF4A.UFLAG = KF4B.[Procedure]+KF4B.Measure
        WHERE KF4B.WFLAG IS NULL
        AND KF4B.[Organisation Type]= ''Provider''
        AND KF4B.Unchanged > 0
        AND KF4B.Improved < '+@NINE+'
    )_

    UNION

    SELECT 
            [Lookup],
            [Procedure],
            [Organisation Type],
            [Organisation Code],
            [Organsation Name],
            [Measure],
            [Improved],
            [Unchanged],
            [Worsened],
            [Total],
            IFLAG,
            UFLAG,
            WFLAG 
    FROM #KF4
    WHERE [Lookup] NOT IN
    (
        SELECT 
            KF4B.[Lookup]
            FROM #KF4 KF4B
            LEFT JOIN #UFLAG KF4A
            ON KF4A.UFLAG = KF4B.[Procedure]+KF4B.Measure
            WHERE KF4B.WFLAG IS NULL
            AND KF4B.[Organisation Type]= ''Provider''
            AND KF4B.Unchanged > 0
            AND KF4B.Unchanged < '+@NINE+'
    )

    DROP TABLE #KF4
    DROP TABLE #UFLAG

    --Applies secondary suppression for Provider Worsened, if needed
    --Identifies Procedures and Measures to be supressed

    SELECT * INTO #WFLAG
    FROM
    (
    SELECT
        WFLAG
    FROM #KF5 
    WHERE WFLAG IS NOT NULL
    )KF5A

    --Applies suppression to seleced dataset and joins to main data set

    SELECT 
            [Lookup],
            [Procedure],
            [Organisation Type],
            [Organisation Code],
            [Organsation Name],
            [Measure],
            [Improved],
            [Unchanged],
            CASE WHEN WFLAG IS NOT NULL AND CLASS = 1 THEN '+@NINE+' ELSE [Worsened] END AS [Worsened],
            CASE WHEN WFLAG IS NOT NULL AND CLASS = 1 THEN '+@NINE+' ELSE [Total] END AS [Total],
            IFLAG,
            UFLAG,
            WFLAG
    INTO #KF6
    FROM
    (
        SELECT 
            KF5B.[Lookup],
            KF5B.[Procedure],
            KF5B.[Organisation Type],
            KF5B.[Organisation Code],
            KF5B.[Organsation Name],
            KF5B.[Measure],
            KF5B.[Improved],
            KF5B.[Unchanged],
            KF5B.[Worsened],
            KF5B.[Total],
            KF5B.IFLAG,
            KF5B.UFLAG,
            KF5A.WFLAG,
            ROW_NUMBER()OVER(PARTITION BY [Procedure], [Measure]
                                ORDER BY [Total]ASC)AS CLASS
        FROM #KF5 KF5B
        LEFT JOIN #WFLAG KF5A
        ON KF5A.WFLAG = KF5B.[Procedure]+KF5B.Measure
        WHERE KF5B.WFLAG IS NULL
        AND KF5B.[Organisation Type]= ''Provider''
        AND KF5B.Worsened > 0
        AND KF5B.Worsened < '+@NINE+'
    )_

    UNION

    SELECT 
            [Lookup],
            [Procedure],
            [Organisation Type],
            [Organisation Code],
            [Organsation Name],
            [Measure],
            [Improved],
            [Unchanged],
            [Worsened],
            [Total],
            IFLAG,
            UFLAG,
            WFLAG 
    FROM #KF5
    WHERE [Lookup] NOT IN
    (
    SELECT 
        KF5B.[Lookup]
        FROM #KF5 KF5B
        LEFT JOIN #WFLAG KF5A
        ON KF5A.WFLAG = KF5B.[Procedure]+KF5B.Measure
        WHERE KF5B.WFLAG IS NULL
        AND KF5B.[Organisation Type]= ''Provider''
        AND KF5B.Worsened > 0
        AND KF5B.Worsened < '+@NINE+'
    )

    DROP TABLE #KF5
    DROP TABLE #WFLAG

    SELECT * INTO #KF6a
    FROM
    (
    SELECT	
            ''ENGLANDENGLAND''+[Procedure]+[Measure] AS ''Lookup'',
            CASE WHEN SUM(ENGIFLAG) = 1 THEN '+@NINE+' ELSE 0 END AS ENGIFLAG,
            CASE WHEN SUM(ENGUFLAG) = 1 THEN '+@NINE+' ELSE 0 END AS ENGUFLAG,
            CASE WHEN SUM(ENGWFLAG) = 1 THEN '+@NINE+' ELSE 0 END AS ENGWFLAG,
            CASE WHEN (SUM(ENGIFLAG) = 1 OR SUM(ENGUFLAG) = 1 OR SUM(ENGWFLAG) = 1) THEN '+@NINE+' ELSE 0 END AS ENGTFLAG
    FROM
    (
    SELECT  
            [Procedure],
            [Measure],
            CASE WHEN [Improved] = '+@NINE+' THEN 1 ELSE 0 END AS ENGIFLAG,
            CASE WHEN [Unchanged] = '+@NINE+' THEN 1 ELSE 0 END AS ENGUFLAG,
            CASE WHEN [Worsened] = '+@NINE+' THEN 1 ELSE 0 END AS ENGWFLAG

    FROM #KF6
    WHERE [Organisation Type] = ''Provider''
    )_
    GROUP BY [Procedure],[Measure] 
    )_

    SELECT * INTO #KF6b
    FROM
    (
    SELECT
            KF6.[Lookup],
            [Procedure],
            [Organisation Type],
            [Organisation Code],
            [Organsation Name],
            [Measure],
            CASE WHEN ENGIFLAG = '+@NINE+' THEN '+@NINE+' ELSE [Improved] END AS [Improved] ,
            CASE WHEN ENGUFLAG = '+@NINE+' THEN '+@NINE+' ELSE [Unchanged] END AS [Unchanged] ,
            CASE WHEN ENGWFLAG = '+@NINE+' THEN '+@NINE+' ELSE [Worsened] END AS [Worsened] ,
            CASE WHEN ENGTFLAG = '+@NINE+' THEN '+@NINE+' ELSE [Total] END AS [Total]


    FROM #KF6 KF6
    LEFT JOIN #KF6a KF6a
    ON KF6.[Lookup] = KF6a.[Lookup]
    )_
    DROP TABLE #KF6a

    SELECT

        [Lookup],
        [Procedure],
        [Organisation Type],
        [Organisation Code],
        [Organsation Name],
        [Measure],
        [Improved],
        [Unchanged],
        [Worsened],
        [Total],
        CASE WHEN [Improved] = '+@NINE+' OR [Total] = '+@NINE+'
            THEN '+@NINE+'
            ELSE CAST(CAST([Improved] AS DECIMAL (10,1))/CAST([Total] AS DECIMAL (10,1))*100 AS DECIMAL (10,1))
        END AS [% Improved],
        
        CASE WHEN [Unchanged] = '+@NINE+' OR [Total] = '+@NINE+'
            THEN '+@NINE+'
            ELSE CAST(CAST([Unchanged] AS DECIMAL (10,1))/CAST([Total] AS DECIMAL (10,1))*100 AS DECIMAL (10,1))
        END AS [% Unchanged],
        
        CASE WHEN [Worsened] = '+@NINE+' OR [Total] = '+@NINE+'
            THEN '+@NINE+'
            ELSE CAST(CAST([Worsened] AS DECIMAL (10,1))/CAST([Total] AS DECIMAL (10,1))*100 AS DECIMAL (10,1))
        END AS [% Worsened]

    INTO #KF7
    FROM #KF6b

    DROP TABLE #KF6b

    select * into #KF8 from (

    SELECT

        [Lookup],
        [Procedure],
        [Organisation Type],
        [Organisation Code],
        CASE WHEN [Organisation Code] = ''England''
            THEN ''England''
            ELSE [Organsation Name]+'' (''+ [Organisation Code]+'')''
        END AS [Organsation Name],
        [Measure],
        CASE WHEN [Improved] = '+@NINE+'
            THEN ''*''
            ELSE CAST([Improved] AS varchar (10))
        END AS [Improved],
        
        CASE WHEN [Unchanged] = '+@NINE+'
            THEN ''*''
            ELSE CAST([Unchanged] AS varchar (10))
        END AS [Unchanged],
        
        CASE WHEN [Worsened] = '+@NINE+'
            THEN ''*''
            ELSE CAST([Worsened] AS varchar (10))
        END AS [Worsened],
        
        CASE WHEN [Total] = '+@NINE+'
            THEN ''*''
            ELSE CAST([Total] AS varchar (10))
        END AS [Total],
        
        CASE WHEN [% Improved] = '+@NINE+'
            THEN ''*''
            ELSE CAST([% Improved] AS varchar (10))+''%''
        END AS [% Improved],
        
        CASE WHEN [% Unchanged] = '+@NINE+'
            THEN ''*''
            ELSE CAST([% Unchanged] AS varchar (10))+''%''
        END AS [% Unchanged],
        
        CASE WHEN [% Worsened] = '+@NINE+'
            THEN ''*''
            ELSE CAST([% Worsened] AS varchar (10))+''%''
        END AS [% Worsened]
        
    FROM #KF7)_

    DROP TABLE #KF7

    select * into #KF9a1 from #KF8 where [procedure]=''Hip Replacement''
    select * into #KF9a2 from #KF8 where [procedure]=''Hip Replacement Primary''
    select * into #KF9a3 from #KF8 where [procedure]=''Hip Replacement Revision''

    select * into #KF9b1 from #KF8 where [procedure]=''Knee Replacement''
    select * into #KF9b2 from #KF8 where [procedure]=''Knee Replacement Primary''
    select * into #KF9b3 from #KF8 where [procedure]=''Knee Replacement Revision''


    select * into #KF10 from (

    select * from #KF9a1 
    union
    select 
    b.[lookup]
    ,b.[Procedure]
    ,b.[Organisation Type]
    ,b.[Organisation Code]
    ,b.[Organsation Name]
    ,b.[Measure]
    ,case when c.[Improved] = ''*'' then ''*'' else b.[Improved] end as [Improved]
    ,case when c.[Unchanged] = ''*'' then ''*'' else b.[Unchanged] end as [Unchanged]
    ,case when c.[Worsened] = ''*'' then ''*'' else b.[Worsened] end as [Worsened]
    ,case when c.[Total] = ''*'' then ''*'' else b.[Total] end as [Total]
    ,case when c.[% Improved] = ''*'' then ''*'' else b.[% Improved] end as [% Improved]
    ,case when c.[% Unchanged] = ''*'' then ''*'' else b.[% Unchanged] end as [% Unchanged]
    ,case when c.[% Worsened] = ''*'' then ''*'' else b.[% Worsened] end as [% Worsened]

    from #KF9a2 b 
    left join #KF9a3 c on b.[Organisation Code]=c.[Organisation Code] and b.[Measure]=c.[Measure]

    union 
    select * from #KF9a3

    union

    select * from #KF9b1 
    union
    select 
    b.[lookup]
    ,b.[Procedure]
    ,b.[Organisation Type]
    ,b.[Organisation Code]
    ,b.[Organsation Name]
    ,b.[Measure]
    ,case when c.[Improved] = ''*''then ''*''else b.[Improved] end as [Improved]
    ,case when c.[Unchanged] = ''*''then ''*''else b.[Unchanged] end as [Unchanged]
    ,case when c.[Worsened] = ''*''then ''*''else b.[Worsened] end as [Worsened]
    ,case when c.[Total] = ''*''then ''*''else b.[Total] end as [Total]
    ,case when c.[% Improved] = ''*''then ''*''else b.[% Improved] end as [% Improved]
    ,case when c.[% Unchanged] = ''*''then ''*''else b.[% Unchanged] end as [% Unchanged]
    ,case when c.[% Worsened] = ''*''then ''*''else b.[% Worsened] end as [% Worsened]

    from #KF9b2 b 
    left join #KF9b3 c on b.[Organisation Code]=c.[Organisation Code] and b.[Measure]=c.[Measure]

    union 
    select * from #KF9b3)_

    select * from #KF10
    --WHERE [Organsation Name] = ''England''
    ORDER BY
            CASE WHEN [Organsation Name] = ''England'' THEN 1
                ELSE 2
            END ASC,
            [Organisation Type],
            [Procedure],
            Measure


    DROP TABLE #KF6
    DROP TABLE #KF8
    DROP TABLE #KF9a1
    DROP TABLE #KF9a2
    DROP TABLE #KF9a3
    DROP TABLE #KF9b1
    DROP TABLE #KF9b2
    DROP TABLE #KF9b3
    Drop Table #KF10')
    '''
    return keystr

def mapping(FYEAR,FYEAR_STRING,TABLE):
    FYEAR1_STRING = f"{FYEAR-4}-{FYEAR-2003} Final"
    FYEAR2_STRING = f"{FYEAR-3}-{FYEAR-2002} Final"
    FYEAR3_STRING = f"{FYEAR-2}-{FYEAR-2001} Final"
    FYEAR4_STRING = f"{FYEAR-1}-{FYEAR-2000} Final"

    mapping_str=f'''
        DECLARE @FYEAR1 VARCHAR(MAX) = '{FYEAR1_STRING}' 
        DECLARE @FYEAR2 VARCHAR(MAX) = '{FYEAR2_STRING}'
        DECLARE @FYEAR3 VARCHAR(MAX) = '{FYEAR3_STRING}'
        DECLARE @FYEAR4 VARCHAR(MAX) = '{FYEAR4_STRING}'
        DECLARE @FYEAR5 VARCHAR(MAX) = '{FYEAR_STRING}'

        SET NOCOUNT ON

        EXEC('
        IF OBJECT_ID (''tempdb..#TS'') IS NOT NULL DROP TABLE #TS
        select * into #TS from
        (
        -- FYEAR1
        select 
        \'\'\'+@FYEAR1+\'\'\' as FYEAR,
        OrgCode, [ProcGroup], [Measure], 
        Modelled_Records_{FYEAR1_STRING[0:4]} as Modelled_Records,
        Adjusted_Health_Gain_{FYEAR1_STRING[0:4]} as AHG, 
        Outlier_{FYEAR1_STRING[0:4]} as Outlier_Status 
        from PROMS_PUBLICATION.proms.TIME_SERIES_{FYEAR1_STRING[0:4]}
        where OrgType = ''Provider''

        union all

        -- FYEAR2
        select 
        \'\'\'+@FYEAR2+\'\'\' as FYEAR, -- UPDATE HERE
        OrgCode, [ProcGroup], [Measure], 
        Modelled_Records_{FYEAR2_STRING[0:4]} as Modelled_Records, -- UPDATE HERE
        Adjusted_Health_Gain_{FYEAR2_STRING[0:4]} as AHG,  -- UPDATE HERE
        Outlier_{FYEAR2_STRING[0:4]} as Outlier_Status  -- UPDATE HERE
        from PROMS_PUBLICATION.proms.TIME_SERIES_{FYEAR2_STRING[0:4]} -- UPDATE HERE
        where OrgType = ''Provider''

        union all

        -- FYEAR3
        select 
        \'\'\'+@FYEAR3+\'\'\' as FYEAR, -- UPDATE HERE
        OrgCode, [ProcGroup], [Measure], 
        Modelled_Records_{FYEAR3_STRING[0:4]} as Modelled_Records, -- UPDATE HERE
        Adjusted_Health_Gain_{FYEAR3_STRING[0:4]} as AHG,  -- UPDATE HERE
        Outlier_{FYEAR3_STRING[0:4]} as Outlier_Status  -- UPDATE HERE
        from PROMS_PUBLICATION.proms.TIME_SERIES_{FYEAR3_STRING[0:4]} -- UPDATE HERE
        where OrgType = ''Provider''

        union all

        -- FYEAR4
        select 
        \'\'\'+@FYEAR4+\'\'\' as FYEAR, -- UPDATE HERE
        OrgCode, [ProcGroup], [Measure], 
        Modelled_Records_{FYEAR4_STRING[0:4]} as Modelled_Records, -- UPDATE HERE
        Adjusted_Health_Gain_{FYEAR4_STRING[0:4]} as AHG,  -- UPDATE HERE
        Outlier_{FYEAR4_STRING[0:4]} as Outlier_Status  -- UPDATE HERE
        from PROMS_PUBLICATION.proms.TIME_SERIES_{FYEAR4_STRING[0:4]} -- UPDATE HERE
        where OrgType = ''Provider''

        union all

        -- FYEAR5
        select 
        \'\'\'+@FYEAR5+\'\'\' as FYEAR, -- UPDATE HERE
        OrgCode, [ProcGroup], [Measure], 
        Modelled_Records_{FYEAR_STRING[0:4]} as Modelled_Records, -- UPDATE HERE
        Adjusted_Health_Gain_{FYEAR_STRING[0:4]} as AHG,  -- UPDATE HERE
        Outlier_{FYEAR_STRING[0:4]} as Outlier_Status  -- UPDATE HERE
        from PROMS_PUBLICATION.proms.TIME_SERIES_{FYEAR_STRING[0:4]} -- UPDATE HERE
        where OrgType = ''Provider''
        )a

        IF OBJECT_ID (''tempdb..#Supp'') IS NOT NULL DROP TABLE #Supp

        select 
        a.OrgCode, 
        case when a.OrgCode = ''England'' then ''England'' else b.OrgName end as OrgName, ProcGroup, Measure, FYEAR, 
        case when Modelled_Records = ''-1'' then ''*'' when Modelled_Records is null then ''-'' else Modelled_Records end as Modelled_Records, 
        case when AHG = ''-30.000'' then ''-'' when AHG = ''-999.000'' then ''-'' when AHG is null then ''-'' else AHG end as AHG,
        Outlier_Status
        into #Supp
        from #TS as a
        left join proms.REF_ORGS_{TABLE} as b -- UPDATE HERE
        on a.OrgCode=b.OrgCode

        IF OBJECT_ID (''tempdb..#PC'') IS NOT NULL DROP TABLE #PC

        select a.OrgCode, a.OrgName, a.ProcGroup, postcode, a.Measure, a.FYEAR, a.Modelled_Records, a.AHG, a.Outlier_Status
        into #PC
        from #Supp as a
        left join 
        ( SELECT
            org_code,
            postcode
            FROM
            (
            SELECT
                org_code,
                postcode,
                ROW_NUMBER() OVER
                (PARTITION BY org_code ORDER BY COALESCE(contact_close_date, ''9999-12-31'') DESC)
                    AS rn
            FROM  [PROMS_HES].[dbo].[ORG_CONTACTS_DAILY]
            WHERE contact_type_code = ''PA''
            ) _
            WHERE rn = 1) as pc 
            on a.OrgCode = pc.org_code
            where OrgCode<>''England''

        IF OBJECT_ID (''tempdb..#T1'') IS NOT NULL DROP TABLE #T1
        IF OBJECT_ID (''tempdb..#T2'') IS NOT NULL DROP TABLE #T2
        IF OBJECT_ID (''tempdb..#T3'') IS NOT NULL DROP TABLE #T3 
        IF OBJECT_ID (''tempdb..#T4'') IS NOT NULL DROP TABLE #T4

        select ''1. NON'' as OrgCode, ''No provider selected'' as OrgName, ''-'' as postcode, ''-'' as Modelled_Records, ''-'' as AHG, ''-'' as Outlier_Status into #T1 
        select distinct ProcGroup into #T2 from #PC
        select distinct case when Measure like ''Oxford%'' then ''Oxford Score'' else Measure end as Measure into #T3 from #PC
        select distinct FYEAR into #T4 from #PC

        IF OBJECT_ID (''tempdb..#Cross'') IS NOT NULL DROP TABLE #Cross

        select distinct * into #Cross
        from #T1 
        cross join #T2
        cross join #T3
        cross join #T4

        -- FINAL OUTPUT

        select *
        from
        (
        select OrgCode, OrgName, ProcGroup, postcode, Measure, FYEAR, Modelled_Records, AHG, Outlier_Status
        from #Cross

        union all

        select OrgCode, OrgName, ProcGroup, postcode, Measure, FYEAR, Modelled_Records, AHG, Outlier_Status
        from #PC
        )a
        order by OrgCode, ProcGroup, Measure, FYEAR
        ')
    '''
    return mapping_str

def annualreportahg(TABLE,DATE_FROM,DATE_TO,FYEAR,YEAR_STRING):
    annualreportahg_str = f'''
        SET NOCOUNT ON
        DECLARE @TABLE				VARCHAR(MAX) = '{TABLE}'
        DECLARE @YR1_START			DATE = '{DATE_FROM}'
        DECLARE @YR1_END			DATE = '{DATE_TO}'
        DECLARE @YR1				VARCHAR (4) = '{str(FYEAR)}'
        DECLARE @YEARSTR            VARCHAR (MAX) = '{YEAR_STRING}'

        EXEC('
        select  \'\'\'+@YEARSTR+\'\'\' as ''Financial Year'',''Hip Replacement'' as ''Procedure'', ''Hip Replacement'' as ''Breakdown'', 
        1 as ''Sort Order'',''Oxford Hip Score'' AS Measure, avg(_CS_SCORE_CHANGE) AS ''Average Health Gain''
        from PROMS_PUBLICATION.proms.QUESTS_'+@TABLE+'
        where _Q1_PROXY_DATE between \'\'\'+@YR1_START+\'\'\' and \'\'\'+@YR1_END+\'\'\' and PROMS_PROC_CODE=''HR''
        GROUP BY PROMS_PROC_CODE

        union

        select  \'\'\'+@YEARSTR+\'\'\' as ''Financial Year'',''Knee Replacement'' as ''Procedure'', ''Knee Replacement'' as ''Breakdown'', 
        1 as ''Sort Order'',''Oxford Knee Score'' AS Measure, avg(_CS_SCORE_CHANGE) AS ''Average Health Gain''
        from PROMS_PUBLICATION.proms.QUESTS_'+@TABLE+'
        where _Q1_PROXY_DATE between \'\'\'+@YR1_START+\'\'\' and \'\'\'+@YR1_END+\'\'\' and PROMS_PROC_CODE=''KR''
        GROUP BY PROMS_PROC_CODE

        union

        /* EQ-5D */
        select  \'\'\'+@YEARSTR+\'\'\' as ''Financial Year'',''Hip Replacement'' as ''Procedure'', ''Hip Replacement'' as ''Breakdown'', 
        1 as ''Sort Order'',''EQ-5D Index'' AS Measure,  avg(EQ5D_INDEX_CHANGE)  AS ''Average Health Gain''
        from PROMS_PUBLICATION.proms.QUESTS_'+@TABLE+'
        where _Q1_PROXY_DATE between \'\'\'+@YR1_START+\'\'\' and \'\'\'+@YR1_END+\'\'\' and PROMS_PROC_CODE=''HR''
        GROUP BY PROMS_PROC_CODE

        union

        select  \'\'\'+@YEARSTR+\'\'\' as ''Financial Year'',''Knee Replacement'' as ''Procedure'', ''Knee Replacement'' as ''Breakdown'', 
        1 as ''Sort Order'',''EQ-5D Index'' AS Measure,  avg(EQ5D_INDEX_CHANGE)  AS ''Average Health Gain''
        from PROMS_PUBLICATION.proms.QUESTS_'+@TABLE+'
        where _Q1_PROXY_DATE between \'\'\'+@YR1_START+\'\'\' and \'\'\'+@YR1_END+\'\'\' and PROMS_PROC_CODE=''KR''
        GROUP BY PROMS_PROC_CODE

        union

        /* EQ VAS */
        select  \'\'\'+@YEARSTR+\'\'\' as ''Financial Year'',''Hip Replacement'' as ''Procedure'', ''Hip Replacement'' as ''Breakdown'', 
        1 as ''Sort Order'',''EQ VAS'' AS Measure,  avg((EQ5D_SCALE_CHANGE*1.0))  AS ''Average Health Gain''
        from PROMS_PUBLICATION.proms.QUESTS_'+@TABLE+'
        where _Q1_PROXY_DATE between \'\'\'+@YR1_START+\'\'\' and \'\'\'+@YR1_END+\'\'\' and PROMS_PROC_CODE=''HR''

        union

        select  \'\'\'+@YEARSTR+\'\'\' as ''Financial Year'',''Knee Replacement'' as ''Procedure'', ''Knee Replacement'' as ''Breakdown'', 
        1 as ''Sort Order'',''EQ VAS'' AS Measure,  avg((EQ5D_SCALE_CHANGE*1.0))  AS ''Average Health Gain''
        from PROMS_PUBLICATION.proms.QUESTS_'+@TABLE+'
        where _Q1_PROXY_DATE between \'\'\'+@YR1_START+\'\'\' and \'\'\'+@YR1_END+\'\'\' and PROMS_PROC_CODE=''KR''

        union

        /*** Primary/Revision ***/
        /* OHS/OKS */
        select  \'\'\'+@YEARSTR+\'\'\' as ''Financial Year'',''Hip Replacement'' as ''Procedure'', ''Hip Replacement Primary'' as ''Breakdown'', 
        2 as ''Sort Order'',''Oxford Hip Score'' AS Measure, avg(_CS_SCORE_CHANGE)  AS ''Average Health Gain''
        from PROMS_PUBLICATION.proms.QUESTS_'+@TABLE+'
        where _Q1_PROXY_DATE between \'\'\'+@YR1_START+\'\'\' and \'\'\'+@YR1_END+\'\'\' and PROMS_PROC_CODE=''HR'' and _PRIM_REV_PROC_CODE=''HR-PRIM''

        union

        select  \'\'\'+@YEARSTR+\'\'\' as ''Financial Year'',''Hip Replacement'' as ''Procedure'', ''Hip Replacement Revision'' as ''Breakdown'', 
        3 as ''Sort Order'',''Oxford Hip Score'' AS Measure, avg(_CS_SCORE_CHANGE)  AS ''Average Health Gain''
        from PROMS_PUBLICATION.proms.QUESTS_'+@TABLE+'
        where _Q1_PROXY_DATE between \'\'\'+@YR1_START+\'\'\' and \'\'\'+@YR1_END+\'\'\' and PROMS_PROC_CODE=''HR'' and _PRIM_REV_PROC_CODE=''HR-REV''

        union

        select  \'\'\'+@YEARSTR+\'\'\' as ''Financial Year'',''Knee Replacement'' as ''Procedure'', ''Knee Replacement Primary'' as ''Breakdown'', 
        2 as ''Sort Order'',''Oxford Knee Score'' AS Measure, avg(_CS_SCORE_CHANGE)  AS ''Average Health Gain''
        from PROMS_PUBLICATION.proms.QUESTS_'+@TABLE+'
        where _Q1_PROXY_DATE between \'\'\'+@YR1_START+\'\'\' and \'\'\'+@YR1_END+\'\'\' and PROMS_PROC_CODE=''KR'' and _PRIM_REV_PROC_CODE=''KR-PRIM''

        union

        select  \'\'\'+@YEARSTR+\'\'\' as ''Financial Year'',''Knee Replacement'' as ''Procedure'', ''Knee Replacement Revision'' as ''Breakdown'', 
        3 as ''Sort Order'',''Oxford Knee Score'' AS Measure, avg(_CS_SCORE_CHANGE)  AS ''Average Health Gain''
        from PROMS_PUBLICATION.proms.QUESTS_'+@TABLE+'
        where _Q1_PROXY_DATE between \'\'\'+@YR1_START+\'\'\' and \'\'\'+@YR1_END+\'\'\' and PROMS_PROC_CODE=''KR'' and _PRIM_REV_PROC_CODE=''KR-REV''

        union

        /* EQ-5D */
        select  \'\'\'+@YEARSTR+\'\'\' as ''Financial Year'',''Hip Replacement'' as ''Procedure'', ''Hip Replacement Primary'' as ''Breakdown'', 
        2 as ''Sort Order'',''EQ-5D Index'' AS Measure, avg(EQ5D_INDEX_CHANGE)  AS ''Average Health Gain''
        from PROMS_PUBLICATION.proms.QUESTS_'+@TABLE+'
        where _Q1_PROXY_DATE between \'\'\'+@YR1_START+\'\'\' and \'\'\'+@YR1_END+\'\'\' and PROMS_PROC_CODE=''HR'' and _PRIM_REV_PROC_CODE=''HR-PRIM''

        union

        select  \'\'\'+@YEARSTR+\'\'\' as ''Financial Year'',''Hip Replacement'' as ''Procedure'', ''Hip Replacement Revision'' as ''Breakdown'', 
        3 as ''Sort Order'',''EQ-5D Index'' AS Measure, avg(EQ5D_INDEX_CHANGE)  AS ''Average Health Gain''
        from PROMS_PUBLICATION.proms.QUESTS_'+@TABLE+'
        where _Q1_PROXY_DATE between \'\'\'+@YR1_START+\'\'\' and \'\'\'+@YR1_END+\'\'\' and PROMS_PROC_CODE=''HR'' and _PRIM_REV_PROC_CODE=''HR-REV''

        union

        select  \'\'\'+@YEARSTR+\'\'\' as ''Financial Year'',''Knee Replacement'' as ''Procedure'', ''Knee Replacement Primary'' as ''Breakdown'', 
        2 as ''Sort Order'',''EQ-5D Index'' AS Measure, avg(EQ5D_INDEX_CHANGE)  AS ''Average Health Gain''
        from PROMS_PUBLICATION.proms.QUESTS_'+@TABLE+'
        where _Q1_PROXY_DATE between \'\'\'+@YR1_START+\'\'\' and \'\'\'+@YR1_END+\'\'\' and PROMS_PROC_CODE=''KR'' and _PRIM_REV_PROC_CODE=''KR-PRIM''

        union

        select  \'\'\'+@YEARSTR+\'\'\' as ''Financial Year'',''Knee Replacement'' as ''Procedure'', ''Knee Replacement Revision'' as ''Breakdown'', 
        3 as ''Sort Order'',''EQ-5D Index'' AS Measure, avg(EQ5D_INDEX_CHANGE)  AS ''Average Health Gain''
        from PROMS_PUBLICATION.proms.QUESTS_'+@TABLE+'
        where _Q1_PROXY_DATE between \'\'\'+@YR1_START+\'\'\' and \'\'\'+@YR1_END+\'\'\' and PROMS_PROC_CODE=''KR'' and _PRIM_REV_PROC_CODE=''KR-REV''

        union

        /* EQ-VAS */

        select  \'\'\'+@YEARSTR+\'\'\' as ''Financial Year'',''Hip Replacement'' as ''Procedure'', ''Hip Replacement Primary'' as ''Breakdown'', 
        2 as ''Sort Order'',''EQ VAS'' AS Measure, avg((EQ5D_SCALE_CHANGE*1.0))  AS ''Average Health Gain''
        from PROMS_PUBLICATION.proms.QUESTS_'+@TABLE+'
        where _Q1_PROXY_DATE between \'\'\'+@YR1_START+\'\'\' and \'\'\'+@YR1_END+\'\'\' and PROMS_PROC_CODE=''HR'' and _PRIM_REV_PROC_CODE=''HR-PRIM''

        union

        select  \'\'\'+@YEARSTR+\'\'\' as ''Financial Year'',''Hip Replacement'' as ''Procedure'', ''Hip Replacement Revision'' as ''Breakdown'', 
        3 as ''Sort Order'',''EQ VAS'' AS Measure, avg((EQ5D_SCALE_CHANGE*1.0))  AS ''Average Health Gain''
        from PROMS_PUBLICATION.proms.QUESTS_'+@TABLE+'
        where _Q1_PROXY_DATE between \'\'\'+@YR1_START+\'\'\' and \'\'\'+@YR1_END+\'\'\' and PROMS_PROC_CODE=''HR'' and _PRIM_REV_PROC_CODE=''HR-REV''

        union

        select  \'\'\'+@YEARSTR+\'\'\' as ''Financial Year'',''Knee Replacement'' as ''Procedure'', ''Knee Replacement Primary'' as ''Breakdown'', 
        2 as ''Sort Order'',''EQ VAS'' AS Measure, avg((EQ5D_SCALE_CHANGE*1.0))  AS ''Average Health Gain''
        from PROMS_PUBLICATION.proms.QUESTS_'+@TABLE+'
        where _Q1_PROXY_DATE between \'\'\'+@YR1_START+\'\'\' and \'\'\'+@YR1_END+\'\'\' and PROMS_PROC_CODE=''KR'' and _PRIM_REV_PROC_CODE=''KR-PRIM''

        union

        select  \'\'\'+@YEARSTR+\'\'\' as ''Financial Year'',''Knee Replacement'' as ''Procedure'', ''Knee Replacement Revision'' as ''Breakdown'', 
        3 as ''Sort Order'',''EQ VAS'' AS Measure, avg((EQ5D_SCALE_CHANGE*1.0))  AS ''Average Health Gain''
        from PROMS_PUBLICATION.proms.QUESTS_'+@TABLE+'
        where _Q1_PROXY_DATE between \'\'\'+@YR1_START+\'\'\' and \'\'\'+@YR1_END+\'\'\' and PROMS_PROC_CODE=''KR'' and _PRIM_REV_PROC_CODE=''KR-REV''
        ')
    '''
    return annualreportahg_str

def successatisf(YEAR_STRING,TABLE,DATE_FROM,DATE_TO):
    successatisf_str=f'''
        SET NOCOUNT ON
        EXEC('
        select ''{YEAR_STRING}'' AS ''Financial Year'', ''Hip Replacement'' AS ''Procedure'',
        ''Success'' AS ''Breakdown'', Q2_SUCCESS AS Sort,
        case when Q2_SUCCESS = 1 then ''Much Better''
            when Q2_SUCCESS = 2 then ''Little Better''
            when Q2_SUCCESS = 3 then ''About the Same''
            when Q2_SUCCESS = 4 THEN ''Little Worse''
            when Q2_SUCCESS = 5 THEN ''Much Worse''
            else '' ''
        END AS ''Answer'', 
        count(*) * 100.0 / sum(count(*)) over() AS ''Percentage''
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between ''{DATE_FROM}'' and ''{DATE_TO}'' and 
        PROMS_PROC_CODE=''HR'' AND Q2_SUCCESS IN (1,2,3,4,5)
        group by Q2_SUCCESS

        union

        select ''{YEAR_STRING}'' AS ''Financial Year'', ''Knee Replacement'' AS ''Procedure'',
        ''Success'' AS ''Breakdown'', Q2_SUCCESS AS Sort,
        case when Q2_SUCCESS = 1 then ''Much Better''
            when Q2_SUCCESS = 2 then ''Little Better''
            when Q2_SUCCESS = 3 then ''About the Same''
            when Q2_SUCCESS = 4 THEN ''Little Worse''
            when Q2_SUCCESS = 5 THEN ''Much Worse''
            else '' ''
        END AS ''Answer'', 
        count(*) * 100.0 / sum(count(*)) over() AS ''Percentage''
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between ''{DATE_FROM}'' and ''{DATE_TO}'' and 
        PROMS_PROC_CODE=''KR'' AND Q2_SUCCESS IN (1,2,3,4,5)
        group by Q2_SUCCESS

        union

        /*** Satisfaction ***/
        select ''{YEAR_STRING}'' AS ''Financial Year'', ''Hip Replacement'' AS ''Procedure'',
        ''Satisfaction'' AS ''Breakdown'', Q2_SATISFACTION AS Sort, 
        case when Q2_SATISFACTION = 1 then ''Excellent''
            when Q2_SATISFACTION = 2 then ''Very Good''
            when Q2_SATISFACTION = 3 then ''Good''
            when Q2_SATISFACTION = 4 THEN ''Fair''
            when Q2_SATISFACTION = 5 THEN ''Poor''
            else '' ''
        END AS ''Answer'',
        count(*) * 100.0 / sum(count(*)) over() AS ''Percentage''
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between ''{DATE_FROM}'' and ''{DATE_TO}'' and 
        PROMS_PROC_CODE=''HR'' AND Q2_SATISFACTION IN (1,2,3,4,5)
        group by Q2_SATISFACTION

        union

        select ''{YEAR_STRING}'' AS ''Financial Year'', ''Knee Replacement'' AS ''Procedure'',
        ''Satisfaction'' AS ''Breakdown'', Q2_SATISFACTION AS Sort, 
        case when Q2_SATISFACTION = 1 then ''Excellent''
            when Q2_SATISFACTION = 2 then ''Very Good''
            when Q2_SATISFACTION = 3 then ''Good''
            when Q2_SATISFACTION = 4 THEN ''Fair''
            when Q2_SATISFACTION = 5 THEN ''Poor''
            else '' ''
        END AS ''Answer'',
        count(*) * 100.0 / sum(count(*)) over() AS ''Percentage''
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between ''{DATE_FROM}'' and ''{DATE_TO}'' 
        and PROMS_PROC_CODE=''KR'' AND Q2_SATISFACTION IN (1,2,3,4,5)
        group by Q2_SATISFACTION')
    '''

    return successatisf_str

def complications_stats(TABLE,DATE_FROM,DATE_TO,YEAR_STRING):
    complications_stats_str = f'''
    EXEC('
        DECLARE @Total_q2s_hr FLOAT
        SELECT @Total_q2s_hr = SUM(_Q2_RETURNED_FLAG) FROM PROMS_PUBLICATION.proms.QUESTS_{TABLE} WHERE  _Q1_PROXY_DATE 
        between ''{DATE_FROM}'' and ''{DATE_TO}'' and PROMS_PROC_CODE=''HR''

        DECLARE @total_complications_hr FLOAT 
        SELECT @total_complications_hr = COUNT(*) from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between ''{DATE_FROM}'' and ''{DATE_TO}'' and PROMS_PROC_CODE=''HR''
            and (Q2_ALLERGY=1 or Q2_BLEEDING=1 or Q2_WOUND=1 or Q2_URINE=1)
            
        DECLARE @Total_q2s_kr FLOAT
        SELECT @Total_q2s_kr = SUM(_Q2_RETURNED_FLAG) FROM PROMS_PUBLICATION.proms.QUESTS_{TABLE} WHERE  _Q1_PROXY_DATE 
        between ''{DATE_FROM}'' and ''{DATE_TO}'' and PROMS_PROC_CODE=''KR''

        DECLARE @total_complications_kr FLOAT 
        SELECT @total_complications_kr = COUNT(*) from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between ''{DATE_FROM}'' and ''{DATE_TO}'' and PROMS_PROC_CODE=''KR''
            and (Q2_ALLERGY=1 or Q2_BLEEDING=1 or Q2_WOUND=1 or Q2_URINE=1)
            
        --- HR 
        /** At least 1 **/
        select ''{YEAR_STRING}'' AS ''Financial Year'', ''Hip Replacement'' AS ''Procedure'', ''Further'' AS ''Breakdown'', ''One or more post-surgical problems'' AS ''Complication'', ROUND((count(*)*100/@Total_q2s_hr),1)  AS ''Percentage''
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between ''{DATE_FROM}'' and ''{DATE_TO}'' and PROMS_PROC_CODE=''HR''
            and (Q2_ALLERGY=1 or Q2_BLEEDING=1 or Q2_WOUND=1 or Q2_URINE=1)

        union all
        /** Wound **/
        select ''{YEAR_STRING}'' AS ''Financial Year'', ''Hip Replacement'' AS ''Procedure'', ''Complication'' AS ''Breakdown'', ''Wound'' AS ''Complication'', ROUND((count(*)*100/@total_complications_hr),1)
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between ''{DATE_FROM}'' and ''{DATE_TO}'' and PROMS_PROC_CODE=''HR''
            and Q2_WOUND=1 

        union all
        /** Urinary **/
        select ''{YEAR_STRING}'' AS ''Financial Year'', ''Hip Replacement'' AS ''Procedure'', ''Complication'' AS ''Breakdown'', ''Urinary'' AS ''Complication'', ROUND((count(*)*100/@total_complications_hr),1)
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between ''{DATE_FROM}'' and ''{DATE_TO}'' and PROMS_PROC_CODE=''HR''
            and Q2_URINE=1

        union all
        /** Bleeding **/
        select ''{YEAR_STRING}'' AS ''Financial Year'', ''Hip Replacement'' AS ''Procedure'', ''Complication'' AS ''Breakdown'', ''Bleeding'' AS ''Complication'', ROUND((count(*)*100/@total_complications_hr),1)
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between ''{DATE_FROM}'' and ''{DATE_TO}'' and PROMS_PROC_CODE=''HR''
            and Q2_BLEEDING=1

        union all
        /** Allergy **/
        select ''{YEAR_STRING}'' AS ''Financial Year'', ''Hip Replacement'' AS ''Procedure'', ''Complication'' AS ''Breakdown'', ''Allergy'' AS ''Complication'', ROUND((count(*)*100/@total_complications_hr),1)
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between ''{DATE_FROM}'' and ''{DATE_TO}'' and PROMS_PROC_CODE=''HR''
            and Q2_ALLERGY=1

        union all
        /** Readmitted **/
        select ''{YEAR_STRING}'' AS ''Financial Year'', ''Hip Replacement'' AS ''Procedure'', ''Further'' AS ''Breakdown'', ''Readmitted'' AS ''Complication'', ROUND((count(*)*100/@Total_q2s_hr),1)
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between ''{DATE_FROM}'' and ''{DATE_TO}'' and PROMS_PROC_CODE=''HR''
            and Q2_READMITTED=1

        union all
        /** Further surgery **/
        select ''{YEAR_STRING}'' AS ''Financial Year'', ''Hip Replacement'' AS ''Procedure'', ''Further'' AS ''Breakdown'', ''Further Surgery'' AS ''Complication'', ROUND((count(*)*100/@Total_q2s_hr),1)
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between ''{DATE_FROM}'' and ''{DATE_TO}'' and PROMS_PROC_CODE=''HR''
            and Q2_FURTHER_SURGERY=1


        --- KR ---
        union all
        /** At least 1 **/
        select ''{YEAR_STRING}'' AS ''Financial Year'', ''Knee Replacement'' AS ''Procedure'', ''Further'' AS ''Breakdown'', ''One or more post-surgical problems'' AS ''Complication'', ROUND((count(*)*100/@Total_q2s_kr),1)  AS ''Percentage''
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between ''{DATE_FROM}'' and ''{DATE_TO}'' and PROMS_PROC_CODE=''KR''
            and (Q2_ALLERGY=1 or Q2_BLEEDING=1 or Q2_WOUND=1 or Q2_URINE=1)

        union all
        /** Wound **/
        select ''{YEAR_STRING}'' AS ''Financial Year'', ''Knee Replacement'' AS ''Procedure'', ''Complication'' AS ''Breakdown'', ''Wound'' AS ''Complication'', ROUND((count(*)*100/@total_complications_kr),1)  AS ''Percentage''
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between ''{DATE_FROM}'' and ''{DATE_TO}'' and PROMS_PROC_CODE=''KR''
            and Q2_WOUND=1 

        union all
        /** Urinary **/
        select ''{YEAR_STRING}'' AS ''Financial Year'', ''Knee Replacement'' AS ''Procedure'', ''Complication'' AS ''Breakdown'', ''Urinary'' AS ''Complication'', ROUND((count(*)*100/@total_complications_kr),1)  AS ''Percentage''
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between ''{DATE_FROM}'' and ''{DATE_TO}'' and PROMS_PROC_CODE=''KR''
            and Q2_URINE=1

        union all
        /** Bleeding **/
        select ''{YEAR_STRING}'' AS ''Financial Year'', ''Knee Replacement'' AS ''Procedure'', ''Complication'' AS ''Breakdown'', ''Bleeding'' AS ''Complication'', ROUND((count(*)*100/@total_complications_kr),1)  AS ''Percentage''
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between ''{DATE_FROM}'' and ''{DATE_TO}'' and PROMS_PROC_CODE=''KR''
            and Q2_BLEEDING=1

        union all
        /** Allergy **/
        select ''{YEAR_STRING}'' AS ''Financial Year'', ''Knee Replacement'' AS ''Procedure'', ''Complication'' AS ''Breakdown'', ''Allergy'' AS ''Complication'', ROUND((count(*)*100/@total_complications_kr),1)  AS ''Percentage''
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between ''{DATE_FROM}'' and ''{DATE_TO}'' and PROMS_PROC_CODE=''KR''
            and Q2_ALLERGY=1

        union all
        /** Readmitted **/
        select ''{YEAR_STRING}'' AS ''Financial Year'', ''Knee Replacement'' AS ''Procedure'', ''Further'' AS ''Breakdown'', ''Readmitted'' AS ''Complication'', ROUND((count(*)*100/@Total_q2s_kr),1)  AS ''Percentage''
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between ''{DATE_FROM}'' and ''{DATE_TO}'' and PROMS_PROC_CODE=''KR''
            and Q2_READMITTED=1

        union all
        /** Further surgery **/
        select ''{YEAR_STRING}'' AS ''Financial Year'', ''Knee Replacement'' AS ''Procedure'', ''Further'' AS ''Breakdown'', ''Further Surgery'' AS ''Complication'', ROUND((count(*)*100/@Total_q2s_kr),1)  AS ''Percentage''
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between ''{DATE_FROM}'' and ''{DATE_TO}'' and PROMS_PROC_CODE=''KR''
            and Q2_FURTHER_SURGERY=1')
    '''
    return complications_stats_str