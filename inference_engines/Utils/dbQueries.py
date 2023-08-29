import sqlite3
import ast
import pandas as pd

conn = sqlite3.connect('cdss.db')

conn2 = sqlite3.connect('cdssbkp.db')


def overview():

    df = pd.read_sql_query(f""" SELECT count (distinct PRESCRIPTION)
                                    from PRESCRIPTION_PROCESSED
                                    """, conn)
    print(df.to_markdown())

    df = pd.read_sql_query(f""" SELECT count (distinct PRESCRIPTION)
                                    from PRESCRIPTION
                                    """, conn)
    print(df.to_markdown())


    df = pd.read_sql_query(f""" SELECT count (distinct PATIENT)
                                    from PRESCRIPTION_PROCESSED
                                    """, conn)
    print(df.to_markdown())


    df = pd.read_sql_query(f""" SELECT count (B.DRUG)
                                    from PRESCRIPTION_PROCESSED A,
                                    PRESCRIPTION B
                                WHERE
                                    A.PRESCRIPTION = B.PRESCRIPTION
                                    """, conn)
    print(df.to_markdown())

    df = pd.read_sql_query(f""" SELECT count (B.DRUG)
                                    from 
                                    PRESCRIPTION B
                                    """, conn)
    print(df.to_markdown())

#3420608

    df = pd.read_sql_query("SELECT * FROM PRESCRIPTION_PROCESSED " , conn)
    print(df.to_markdown())

    df = pd.read_sql_query("""SELECT patient, count(INTER_DRUG_NUM) 
                                FROM PRESC_INTERACTION 
                                where patient = 3420608 """ , conn)
    print(df.to_markdown())

#### INTERACTIONS

df = pd.read_sql_query("""SELECT INTERACTION1, COUNT(INTERACTION1) 
                          FROM PRESC_INTERACTION 
                          GROUP BY 1 """ , conn)
print(df.to_markdown())

df = pd.read_sql_query("""SELECT distinct  
                                            INTERACTION2 
                            FROM PRESC_INTERACTION  """ , conn)
print(df.to_markdown())

df = pd.read_sql_query("""SELECT distinct  
                                            INTERACTION3 
                            FROM PRESC_INTERACTION  """ , conn)
print(df.to_markdown())

df = pd.read_sql_query("""SELECT distinct  
                                            INTERACTION4 
                            FROM PRESC_INTERACTION  """ , conn)
print(df.to_markdown())

df = pd.read_sql_query("""SELECT distinct PATIENT,
            DRUG ,
            INTER_DRUG_NUM ,
            INTERACTION1 ,
            INTERACTION2 ,
            INTERACTION3 ,
            INTERACTION4 ,
            QOE ,
            SOR ,
            ALTERNATIVE 
                            FROM PRESC_INTERACTION 
                            where patient = 3420608 """ , conn)
print(df.to_markdown())

df = pd.read_sql_query("SELECT * FROM DRUG_DRUG_INTERACTION order by 3" , conn)
print(df.to_markdown())


df = pd.read_sql_query("SELECT * FROM DRUG_ALTERNATIVE " , conn)
print(df.to_markdown())

rdf = pd.read_sql_query("SELECT * FROM PRESCRIPTION_MODELS where model <> 'null'" , conn)
print(df.to_markdown())

df = pd.read_sql_query("SELECT * FROM PRESCRIPTION_RESCHEDULED " , conn)
print(df.to_markdown())


df = pd.read_sql_query("SELECT * FROM TIMEOUT_PRESCRIPTIONS " , conn)
print(df.to_markdown())




df = pd.read_sql_query("SELECT * FROM PRESCRIPTION WHERE PRESCRIPTION like '1996234-92-F-210215' " , conn)
print(df.to_markdown())

df = pd.read_sql_query("SELECT * FROM PRESCRIPTION WHERE PRESCRIPTION = '3346025-70-F-010820'" , conn)
print(df.to_markdown())




df = pd.read_sql_query("SELECT distinct(FIXEDTIME) FROM PRESCRIPTIONV2 " , conn)
print(df.to_markdown())





df = pd.read_sql_query("SELECT distinct(SCHEDULE), FREQUENCY FROM PRESCRIPTION " , conn)
print(df.to_markdown())

df = pd.read_sql_query("SELECT * FROM PRESCRIPTION WHERE PRESCRIPTION = '1962249-94-F-20150105'" , conn)
print(df.to_markdown())

df = pd.read_sql_query("SELECT * FROM DRUG_DRUG_INTERACTION WHERE PRESCRIPTION = '1962249-94-F-20150105'" , conn2)
print(df.to_markdown())

df = pd.read_sql_query("SELECT COUNT(*) FROM DRUG_DRUG_INTERACTION" , conn)
print(df.to_markdown())


df = pd.read_sql_query("SELECT * FROM PRESCRIPTION_RESCHEDULED", conn)
print(df.to_markdown())




df = pd.read_sql_query("SELECT * FROM PRESCRIPTION_MODELS", conn)
print(df.to_markdown())


def getPrescriptionModels():
    df = pd.read_sql_query("SELECT * from PRESCRIPTION_MODELS", conn)
    print(df)
    teste = []
    for columns in df.itertuples():
        t= columns.MODEL
        t2 = t.strip('[]').replace('"', '').replace(' ', '').split(',')
        for a in t2:
            print(a)


df = pd.read_sql_query("SELECT PATIENT, PRESCRIPTION, DRUG from PRESCRIPTION", conn)

print(df)

patientInput = '1111111'
prescriptionInput = str("1111111-67-M-010115")

df = pd.read_sql_query("SELECT * from DRUG_DRUG_INTERACTION", conn)
print(df)


df = pd.read_sql_query(
    f"""SELECT PATIENT,PRESCRIPTION, DRUG, INTERACTION, INTERACTIONGROUP, ALTERNATIVE, INTER_DRUG_CAT, INTER_DRUG_NUM 
       FROM PRESC_INTERACTION
       WHERE PATIENT = {patientInput} 
       AND PRESCRIPTION = "{str(prescriptionInput)}" """, conn)
print(df)


df = pd.read_sql_query("SELECT COUNT(DISTINCT PATIENT) from PRESCRIPTION", conn)
print(df)

df = pd.read_sql_query("SELECT DISTINCT PATIENT from PRESCRIPTION", conn)
print(df)

df = pd.read_sql_query("SELECT * from PRESCRIPTION", conn)
print(df)

df = pd.read_sql_query("SELECT PATIENT, DRUG, INTERACTION, INTERACTION_GROUP, ALTERNATIVE from PRESC_INTERACTION", conn)
print(df)

print('getAlternatives')


df = pd.read_sql_query("SELECT PATIENT, DRUG, INTERACTION, INTERACTION_GROUP, ALTERNATIVE from PRESC_INTERACTION", conn)
print(df)

print('getAlternativeInteractions')


df = pd.read_sql_query("SELECT * from DRUG_ALTERNATIVE", conn)
print(df)

print('getPrescriptionDrugs')


df = pd.read_sql_query("SELECT * from PRESCRIPTION", conn)
print(df)
