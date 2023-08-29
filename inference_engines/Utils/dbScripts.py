

import sqlite3
import pandas as pd
import shutil
from config import DBNAME

conn = sqlite3.connect(DBNAME)
cur = conn.cursor()


def addInteraction():
    df = pd.read_sql_query("""SELECT CD_PATIENT, CD_PRESCRIPTION, DRUG
                              FROM   PRESCRIPTION
                              WHERE DRUG IN ('Omeprazol', 'Pantoprazol')
                               """ , conn)
    result = df.values.tolist()
    for index in df.index:
        prescription = df['PRESCRIPTION'][index]
        patientDb = df['PATIENT'][index]
        drug = df['DRUG'][index]
        params = (patientDb, prescription, drug,"1", "PIM", "PIM_Gastrointestinal",  "PIM_Proton-pump_inhibitors", "PIM_Proton-pump_inhibitors", "High", "Strong", "Risk of Clostridium difficile infection and bone loss and fractures", 'recommendation', "F") 
        conn.execute("INSERT INTO PRESC_INTERACTION values (?,?,?,?,?,?,?,?,?,?,?,?,?)", params)
    conn.commit()


def duplicateDrugDrugInteractionsII():
    df4 = pd.read_sql_query(""" 
        select distinct(CD_PRESCRIPTION) CD_PRESCRIPTION ,DRUG1, DRUG2
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

def dbScritp():
    #duplicateDrugDrugInteractionsII()
    #copyDBtoGUI()
    conn.execute("UPDATE PRESCRIPTION SET FIXEDTIME = 'N' WHERE SCHEDULE = 'SN'")
    conn.commit()
    
def copyDBtoGUI():
    original = r'/Users/gr60/Documents/Beers/cdss.db'
    target = r'/Users/gr60/Documents/BeersGUI/cdss.db'
    shutil.copyfile(original, target)

def updateDrugName(Original, NewName):
    conn.execute('UPDATE PRESCRIPTION SET DRUG = ? WHERE DRUG = ?', (NewName, Original))
    conn.execute(f'UPDATE PRESCRIPTION SET DRUG = ? WHERE DRUG = ?', (NewName, Original))
    conn.execute(f'UPDATE PRESC_INTERACTION SET DRUG = ? WHERE DRUG = ?', (NewName, Original))
    conn.execute(f'UPDATE DRUG_DRUG_INTERACTION SET DRUG1 = ? WHERE DRUG1 = ?', (NewName, Original))
    conn.execute(f'UPDATE DRUG_DRUG_INTERACTION SET DRUG2 = ? WHERE DRUG2 = ?', (NewName, Original))
    conn.execute(f'UPDATE DRUG_ALTERNATIVE SET DRUG = ? WHERE DRUG = ?', (NewName, Original))
    conn.commit()

#updateDrugName("Fosfato_de_Potassio_(K)", "Fosfato_de_Potassio")

def removeDuplicatePatient():
    conn.execute(""" DELETE FROM PATIENT
                      WHERE EXISTS (
                      SELECT 1 FROM PATIENT p2 
                      WHERE PATIENT.CD_PATIENT = p2.CD_PATIENT
                      AND PATIENT.DT_Admission = p2.DT_Admission
                      AND PATIENT.rowid > p2.rowid
                    );""")
    conn.commit()

def CheckDuplicatePatient():
    df = pd.read_sql_query(""" 
                     SELECT count(patient) FROM PATIENT
                    WHERE EXISTS (
                     SELECT 1 FROM PATIENT p2 
                      WHERE PATIENT.CD_PATIENT = p2.CD_PATIENT
                      AND PATIENT.DT_Admission = p2.DT_Admission
                      AND PATIENT.rowid > p2.rowid);""", conn)
    print(df.to_markdown())

dbScritp()