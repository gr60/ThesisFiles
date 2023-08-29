
import sqlite3
#import xlsxwriter
import pandas as pd
from config import DBNAME
DIR = 'CDSS'
conn = sqlite3.connect(DBNAME)



def list_Drugs():

    df = pd.read_sql_query("""SELECT CD_PATIENT, CD_PRESCRIPTION, DRUG
                              FROM   PRESCRIPTION
                              WHERE DRUG = "Nalbufina"
                               """ , conn)
    writer = pd.ExcelWriter(r'results/interactions/drug.xlsx')
    df.to_excel(writer, sheet_name='Sheet1')
    writer.close()



def  Interactions():    
    df = pd.read_sql_query("""SELECT DRUG, INTERACTION1,COUNT(INTERACTION1), INTERACTION2, COUNT(INTERACTION2), INTERACTION3, COUNT(INTERACTION3) , INTERACTION4, COUNT(INTERACTION4), ALTERNATIVE  
                              FROM PRESC_INTERACTION 
                              GROUP BY 1,2,4,6,8,10 """ , conn)
#    print(df.to_markdown())

    writer = pd.ExcelWriter(fr'results/{DIR}/interactions/interactionGroups.xlsx', engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1')
    writer.close()

def  InteractionsbyPatient():
    df = pd.read_sql_query("""SELECT CD_PATIENT,CD_PRESCRIPTION, DRUG, INTERACTION1,COUNT(INTERACTION1), INTERACTION2, COUNT(INTERACTION2), INTERACTION3, COUNT(INTERACTION3) , INTERACTION4, COUNT(INTERACTION4), ALTERNATIVE  
                              FROM PRESC_INTERACTION 
                              GROUP BY 1,2,3,6,8,10,12 """ , conn)
#    print(df.to_markdown())

    writer = pd.ExcelWriter(fr'results/{DIR}/interactions/InteractionsbyPatientv2.xlsx')
    df.to_excel(writer, sheet_name='Sheet1')
    writer.close()


def  InteractionswithPatientData():
    df = pd.read_sql_query("""SELECT A.CD_PATIENT, 
                                     A.DRUG, 
                                     A.INTERACTION1,COUNT(A.INTERACTION1), 
                                     A.INTERACTION2, COUNT(A.INTERACTION2), 
                                     A.INTERACTION3, COUNT(A.INTERACTION3) , 
                                     A.INTERACTION4, COUNT(A.INTERACTION4), 
                                     A.ALTERNATIVE, 
                                     B.AGE, 
                                     B.GENDER, 
                                     B.CLINIC, 
                                     B.MAIN_PROCEDURE, 
                                     B.CID, 
                                     B.discharge_reason  
                              FROM PRESC_INTERACTION A, PATIENT B
                              where  A.CD_PATIENT =  b.CD_PATIENT
                              GROUP BY 1,2,3,5,7,9,11,12,13,14,15,16,17 """ , conn)
#    print(df.to_markdown())

    writer = pd.ExcelWriter(fr'results/{DIR}/interactions/InteractionswithPatientData.xlsx', engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1')
    writer.close()

def patientStatistics():
    df = pd.read_sql_query("""SELECT AGE, count(AGE), GENDER,COUNT(GENDER), CLINIC, COUNT(CLINIC), MAIN_PROCEDURE, COUNT(MAIN_PROCEDURE) , CID, COUNT(CID), discharge_reason, count(discharge_reason),CD_PATIENT  
                              FROM PATIENT 
                              GROUP BY 1,3,5,7,9,11,13 """ , conn)
#    print(df.to_markdown())

    writer = pd.ExcelWriter(fr'results/{DIR}/interactions/patientStatistics.xlsx')
    df.to_excel(writer, sheet_name='Sheet1')
    writer.close()


def top10drugs():
    df = pd.read_sql_query("""SELECT drug, count(drug) 
                              FROM PRESCRIPTION 
                              GROUP BY 1
                              ORDER BY 2 DESC LIMIT 15;
                              """ , conn)
    print(df.to_markdown())

def top10diseases():
    df = pd.read_sql_query("""SELECT MAIN_PROCEDURE, count(MAIN_PROCEDURE) 
                              FROM PATIENT 
                              GROUP BY 1
                              ORDER BY 2 DESC LIMIT 12;
                              """ , conn)
    print(df.to_markdown())

   
def Drugs_processed():
    df = pd.read_sql_query("""SELECT count(B.DRUG)
                              FROM  PRESC_INTERACTION a,
                                    PRESCRIPTION b
                              WHERE A.CD_PRESCRIPTION = B.CD_PRESCRIPTION
                               """ , conn)
    print(df.to_markdown())

def Patient_processed():
    df = pd.read_sql_query("""SELECT count(DISTINCT A.CD_PATIENT)
                              FROM  PRESC_INTERACTION a
                               """ , conn)
    print(df.to_markdown())


def drugs_profile():
    df = pd.read_sql_query("""SELECT count(B.DRUG)
                              FROM   PRESCRIPTION b
                               """ , conn)
    print(df.to_markdown())

    df = pd.read_sql_query("""SELECT count(B.DRUG)/count(distinct B.CD_PRESCRIPTION)
                              FROM   PRESCRIPTION b
                               """ , conn)
    print(df.to_markdown())

    df = pd.read_sql_query("""SELECT DISTINCT(B.CD_PATIENT), count(distinct B.CD_PRESCRIPTION)
                              FROM   PRESCRIPTION b
                              GROUP BY B.CD_PATIENT
                               """ , conn)
    print(df.to_markdown())

    writer = pd.ExcelWriter(fr'results/{DIR}/interactions/patientPrescr.xlsx')
    df.to_excel(writer, sheet_name='Sheet1')
    writer.close()



    df = pd.read_sql_query("""SELECT DISTINCT(B.CD_PRESCRIPTION), count(distinct B.CD_DRUG)
                              FROM   PRESCRIPTION b
                              GROUP BY B.PRESCRIPTION
                               """ , conn)
    print(df.to_markdown())

    writer = pd.ExcelWriter(fr'results/{DIR}/interactions/PRESCDRUG.xlsx')
    df.to_excel(writer, sheet_name='Sheet1')
    writer.close()



def  PRESCRIPTION_PROCESSED():
    df = pd.read_sql_query("""SELECT distinct CD_PRESCRIPTION,  CD_PATIENT
                              FROM PRESCRIPTION_PROCESSED """ , conn)
#    print(df.to_markdown())

    writer = pd.ExcelWriter(fr'results/{DIR}/interactions/PRESCRIPTION_PROCESSED.xlsx')
    df.to_excel(writer, sheet_name='Sheet1')
    writer.close()


def  PRESCRIPTION():
    df = pd.read_sql_query("""SELECT * 
                              FROM PRESCRIPTION """ , conn)
    #    print(df.to_markdown())
    #Define the maximum number of rows per sheet
    max_rows_per_sheet = 1000000
    # Calculate the total number of sheets needed
    total_sheets = (len(df) // max_rows_per_sheet) + 1

    writer = pd.ExcelWriter(fr'results/{DIR}/interactions/PRESCRIPTION.xlsx')
    for sheet_number in range(total_sheets):
        # Calculate the start and end rows for the current sheet
        start_row = sheet_number * max_rows_per_sheet
        end_row = (sheet_number + 1) * max_rows_per_sheet

        # Extract the data for the current sheet
        sheet_data = df.iloc[start_row:end_row]

        # Write the data to the current sheet
        sheet_data.to_excel(writer, sheet_name=f'Sheet{sheet_number + 1}', index=False)

    writer.close()

def  PATIENT():
    df = pd.read_sql_query("""SELECT *
                              FROM PATIENT """ , conn)
#    print(df.to_markdown())

    writer = pd.ExcelWriter(fr'results/{DIR}/interactions/PATIENT.xlsx')
    df.to_excel(writer, sheet_name='Sheet1')
    writer.close()


def  DRUG_ALTERNATIVE():
    df = pd.read_sql_query("""SELECT 
                                CD_PATIENT,
                                CD_PRESCRIPTION,
                                DRUG,
                                ALTERNATIVE 
                              FROM DRUG_ALTERNATIVE """ , conn)
    writer = pd.ExcelWriter(fr'results/{DIR}/alternatives/DRUG_ALTERNATIVE.xlsx')
    df.to_excel(writer, sheet_name='Sheet1')
    writer.close()


def  PRESCRIPTION_MODELS():
    df = pd.read_sql_query("""SELECT  *
                              FROM PRESCRIPTION_MODELS """ , conn)

    writer = pd.ExcelWriter(fr'results/{DIR}/alternatives/PRESCRIPTION_MODELS.xlsx')
    df.to_excel(writer, sheet_name='Sheet1')
    writer.close()

def  PRESCRIPTION_RESCHEDULED():
    df = pd.read_sql_query("""SELECT  CD_PATIENT, CD_PRESCRIPTION, MODEL
                              FROM PRESCRIPTION_RESCHEDULED """ , conn)
    writer = pd.ExcelWriter(fr'results/{DIR}/reschedule/PRESCRIPTION_RESCHEDULED.xlsx')
    df.to_excel(writer, sheet_name='Sheet1')
    writer.close()


def  PRESC_INTERACTION():
    df = pd.read_sql_query("""SELECT  *
                              FROM PRESC_INTERACTION """ , conn)
    writer = pd.ExcelWriter(fr'results/{DIR}/interactions/PRESC_INTERACTION.xlsx')
    df.to_excel(writer, sheet_name='Sheet1')
    writer.close()

def  DRUG_DRUG_INTERACTION():
    df = pd.read_sql_query("""SELECT  *
                              FROM DRUG_DRUG_INTERACTION """ , conn)
    writer = pd.ExcelWriter(fr'results/{DIR}/interactions/DRUG_DRUG_INTERACTION.xlsx')
    df.to_excel(writer, sheet_name='Sheet1')
    writer.close()


def AltPrescr_processed():
    df = pd.read_sql_query("""SELECT CD_PATIENT, CD_PRESCRIPTION, MODEL
                              FROM   PRESCRIPTION_MODELS
                               """ , conn)
    writer = pd.ExcelWriter(fr'results/{DIR}/alternatives/PCAlternativeDrugs.xlsx')
    df.to_excel(writer, sheet_name='Sheet1')
    writer.close()

#AltPrescr_processed()



def getNumPrescriptioToReschedule(conn):
    df = pd.read_sql_query(f""" SELECT count(DISTINCT CD_PATIENT) FROM PRESCRIPTION_MODELS
                                where MODEL = "null" 
                                AND CD_PATIENT NOT IN (SELECT CD_PATIENT FROM PRESCRIPTION_RESCHEDULED)
                                AND CD_PATIENT IN (SELECT PATIENT FROM PRESC_INTERACTION WHERE INTERACTION1 = "DDI")
                                """, conn)
    print(f'Total:{df.to_markdown()} ')

#getNumPrescriptioToReschedule(conn)



def results():
    InteractionsbyPatient()
    DRUG_DRUG_INTERACTION()
    DRUG_ALTERNATIVE()
    PRESCRIPTION_MODELS()
    PRESCRIPTION_RESCHEDULED()

results()