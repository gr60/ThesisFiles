import sqlite3
import pandas as pd

conn = sqlite3.connect('cdss.db')

cur = conn.cursor()


#sql = 'DELETE FROM PRESCRIPTION_MODELS WHERE MODEL LIKE "%No interactions found%"'
#cur = conn.cursor()
#cur.execute(sql)
#conn.commit()


#sql = 'DELETE FROM TIMEOUT_PRESCRIPTIONS'
#cur = conn.cursor()
#cur.execute(sql)
#conn.commit()
 





def duplicateDrugDrugInteractions():
    df4 = pd.read_sql_query(""" 
    
        select distinct(a.PRESCRIPTION),  a.INTERACTION4, a.INTERACTION1, 
            a.DRUG1, a.FREQUENCY, a.SCHEDULE, 
            b.DRUG2, b.FREQUENCY, b.SCHEDULE 
        from (
            SELECT distinct (a.PRESCRIPTION) prescription, b.INTERACTION1, b.INTERACTION4, c.DRUG1, c.DRUG2, d.FREQUENCY, d.SCHEDULE
            from PRESCRIPTION_PROCESSED a,
            PRESC_INTERACTION b, 
            DRUG_DRUG_INTERACTION c,
            PRESCRIPTION d
            where a.PRESCRIPTION = b.PRESCRIPTION
            and a.PRESCRIPTION = c.PRESCRIPTION
            and a.PRESCRIPTION = d.PRESCRIPTION
            and c.DRUG1 <> c.DRUG2
            and c.DRUG1 = b.DRUG
            and b.DRUG = d.DRUG ) a,
            (SELECT distinct (a.PRESCRIPTION) prescription,b.INTERACTION1, b.INTERACTION4, c.DRUG1, c.DRUG2, d.FREQUENCY, d.SCHEDULE
            from PRESCRIPTION_PROCESSED a,
            PRESC_INTERACTION b, 
            DRUG_DRUG_INTERACTION c,
            PRESCRIPTION d
            where a.PRESCRIPTION = b.PRESCRIPTION
            and a.PRESCRIPTION = c.PRESCRIPTION
            and a.PRESCRIPTION = d.PRESCRIPTION
            
            and c.DRUG1 <> c.DRUG2
            and c.DRUG2 = b.DRUG
            and b.DRUG = d.DRUG ) b
        where a.prescription = b.prescription
        and a.DRUG1 = b.DRUG1
        and a.DRUG2 = b.DRUG2 
        ORDER BY 1""", conn)
    print(df4.to_markdown())
    result = df4.values.tolist()
    indexlist = []
    for index in df4.index:
        prescription = df4['prescription'][index]
        drug1 = df4['DRUG1'][index]
        drug2 = df4['DRUG2'][index]
        dfindex = df4.index[(df4['prescription'] == prescription) & (df4['DRUG1'] == drug2) & (df4['DRUG2'] == drug1 )].tolist()
        if dfindex:
            if index not in indexlist:
                indexlist.append(dfindex[0])
                sql = f'DELETE FROM DRUG_DRUG_INTERACTION WHERE DRUG1 = "{drug2}" and DRUG2 = "{drug1}" and PRESCRIPTION = "{prescription}"'
                cur = conn.cursor()
                cur.execute(sql)
                conn.commit()


def duplicateDrugDrugInteractionsII():
    df4 = pd.read_sql_query(""" 
        select distinct(PRESCRIPTION) PRESCRIPTION ,DRUG1, DRUG2
        from 
            DRUG_DRUG_INTERACTION
            where DRUG1 <> DRUG2""", conn)
    print(df4.to_markdown())
    result = df4.values.tolist()
    indexlist = []
    for index in df4.index:
        prescription = df4['PRESCRIPTION'][index]
        drug1 = df4['DRUG1'][index]
        drug2 = df4['DRUG2'][index]
        dfindex = df4.index[(df4['PRESCRIPTION'] == prescription) & (df4['DRUG1'] == drug2) & (df4['DRUG2'] == drug1 )].tolist()
        if dfindex:
            if index not in indexlist:
                indexlist.append(dfindex[0])
                sql = f'DELETE FROM DRUG_DRUG_INTERACTION WHERE DRUG1 = "{drug2}" and DRUG2 = "{drug1}" and PRESCRIPTION = "{prescription}"'
                cur = conn.cursor()
                cur.execute(sql)
                conn.commit()

       
    
duplicateDrugDrugInteractionsII()