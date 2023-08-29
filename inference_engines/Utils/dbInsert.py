import sqlite3
import pandas as pd
from datetime import datetime

conn = sqlite3.connect('cdss.db')
c = conn.cursor()

def importFile(fileName, sheetName):
    df = pd.read_excel(fileName, sheet_name=sheetName)
    return(df)

def insertPatients(fileName):
    patient_df = fileName
    patientNumber = 0
    for index, row in patient_df.iterrows():
        patient = str(row["NR_ATENDIMENTO"])
        age = str(row["AGE"])
        gender = row["GENDER"]
        clinic = row["CLINIC"]
        dt_discharge = str(row["DT_ALTA"].to_pydatetime().date())
        dt_hospitalization = str(row["DT_ENTRADA"].to_pydatetime().date())
        dischage_reason = row["MOTIVO_ALTA"]
        cd_procedure =  row["CD_PROCEDIMENTO"]
        ds_procedure =  ''.join(str(row["DS_PROCEDIMENTO"]).rstrip().lstrip()).replace(" ", "_").replace('(','').replace(')','')
        cd_cid =  row["CD_CID_PRIMARIO"]
        params = (patient, age, gender, dt_hospitalization, dt_discharge, clinic, dischage_reason, ds_procedure,cd_cid ) 
        #print(params)
        c.execute("INSERT INTO PATIENT values (?,?,?,?,?,?,?,?,?)", params)
        patientNumber += 1
    return(f'Total patients imported {patientNumber}')

def insertExams(fileName):
    exam_df = fileName
    examNumber = 0
    for index, row in exam_df.iterrows():
        patient =  int(row["NR_ATENDIMENTO"])
        seqResult =int(row["NR_SEQ_RESULTADO"])
        nmExam = ''.join(str(row["NM_EXAME"]).rstrip().lstrip()).replace(" ", "_") 
        qtResult = float(str(row["QT_RESULTADO"]).replace(",", "."))
        dtResult = str(row["DT_RESULTADO"].to_pydatetime().date())
        params = (patient, seqResult, nmExam, qtResult, dtResult) 
        c.execute("INSERT INTO PATIENT_EXAMS values (?,?,?,?,?)", params)
        examNumber += 1
    return(f'Total exams imported {examNumber}')

def insertPreviousDisease(fileName):
    disease_df = fileName
    diseaseNumber = 0
    for index, row in disease_df.iterrows():
        patient =  int(row["NR_ATENDIMENTO"])
        nmDisease = ''.join(str(row["DOENCA"]).rstrip().lstrip()).replace(" ", "_") 
        diseaseNumber += 1
        params = (patient, nmDisease) 
        c.execute("INSERT INTO PATIENT_PREVIOUS_DISEASES values (?,?)", params)
    return(f'Total exams imported {diseaseNumber}')


def extract_values(row):
    #print(row["INDEX"])
    counter = int(row["NR_TREATMENT_INSTANCE"])
    age = getPatientAge(counter)
    gender = getPatientGender(counter)
    drugName = ''.join(str(row["DS_DRUG"]).rstrip().lstrip()).replace(" ", "_") 
    drugNameOriginal = ''.join(str(row["DS_DRUG_ORIGINAL"]).rstrip().lstrip()).replace(" ", "_")
    composeName = str(counter)+"-"+str(age)+"-"+str(gender)
    route = ''.join(str(row["ROUTE"]).rstrip().lstrip()).replace(" ", "_") 
    startDate = pd.to_datetime(row["DT_START"])
    startDateInt = str(startDate.to_pydatetime().date()).replace("/", "").replace("-", "")  
    startDate = str(startDate.to_pydatetime().date())
    endDate = pd.to_datetime(row["DT_END"])
    endDate = str(endDate.to_pydatetime().date())
    schedule = str(row['SCHEDULE'])
    for z in range(0, 60):
        schedule = schedule.replace(':'+str(z), '')
    frequency = str(row['FREQUENCY'])
    typeDrug =  str(row['TYPE_DRUG'])
    drugLenght = int(row['DrugLenght'])
    fixedTime =  str(row["FIXED_TIME"])
    dsInterval =  str(row["DS_INTERVALO"])
    drugUnit =  str(row["CD_UNIDADE_MEDIDA_DOSE"])
    presc_day = str(counter)+"-"+str(age)+"-"+str(gender) +"-"+str(startDateInt)
    firstLine =  str(row['FIRST_LINE'])
    release =  str(row['RELEASE'])
    criticalPatient = str(row['CRITICAL_PATIENT'])
    dose = int(row['DOSE'])
    values =  (counter, presc_day, drugName,dose,frequency,schedule, startDate, endDate,fixedTime,dsInterval, typeDrug, drugUnit, drugNameOriginal, drugLenght, route, composeName, presc_day, criticalPatient,firstLine, release)
    
    return (values) 


def insertPrescription(prescription_df): 
    prescription_df['Extracted'] = prescription_df.apply(extract_values, axis=1)
    for extracted_value in prescription_df['Extracted']:
        conn.execute("INSERT INTO PRESCRIPTION values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", extracted_value)


def getPatientAge(patient):
    df = pd.read_sql_query(f'SELECT distinct(age) from PATIENT WHERE CD_PATIENT = {patient}', conn)
    patients = df.values.tolist()
    if patients:
        return(int(patients[0][0]))
    else:
        return(999)

def getPatientGender(patient):
    df = pd.read_sql_query(f'SELECT distinct(gender) from PATIENT WHERE CD_PATIENT = {patient}', conn)
    patients = df.values.tolist()
    if patients:
        return(str(patients[0][0]))
    else:
        return('M')


def importPatients(test):
    print ("PROD DB")
    print(f"Importing prescriptions \n Current Time = {datetime.now()}")
    prescriptions = importFile(r'data/patient_data/Prescriptions.xlsx', ['Sheet1'])
    print(f"Importing patients \n Current Time = {datetime.now()}")
    patients = importFile(r'data/patient_data/Patients.xlsx', 'Sheet1')
    print(f"Importing exams \n Current Time = {datetime.now()}")
    exams = importFile(r'data/patient_data/Exams.xlsx', 'Sheet1')
    print(f"Importing diseases \n Current Time = {datetime.now()}")
    diseases = importFile(r'data/patient_data/PrevDisease.xlsx', 'Sheet1')
    prescriptions = pd.concat(prescriptions, axis=0, ignore_index=True)
    insertPatients(patients)
    insertExams(exams)
    insertPreviousDisease(diseases)
    insertPrescription(prescriptions)
    conn.commit()
    conn.close()