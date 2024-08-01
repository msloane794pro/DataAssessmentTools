SELECT 
    v.name AS TableName,
    (SELECT COUNT(*) FROM sys.columns AS c WHERE c.object_id = v.object_id) AS NumberOfColumns,
    CASE 
        WHEN v.name IN (
            'vINLLockshopServiceRequest2',
            'vINLMaintenanceWorkRequest2',
            'vINLCACR',
            'vINLObjective',
            'vINLNonConformanceReport2',
            'vINLBaseFreightWorkRequest',
            'vINLImprovementAgenda2',
            'vINLRisk2',
            'vINLAssessment2',
            'vINLCA2',
            'vINLConditionIssues_Rev2',
            'vINLHPIScreening2',
            'vINLINR2',
            'vINLLessonsLearned2',
            'vINLSuggestion2',
            'vINLGeneralAction2',
            'vINLRegulatoryScreen2',
            'vINLOperabilityReviews2',
            'vINLObservation2'
        ) THEN 1 ELSE 0 
    END AS Include
FROM 
    sys.views AS v
WHERE 
    v.type = 'V'
    AND v.name NOT LIKE 'dt%' 
ORDER BY 
    Include desc, v.name;
