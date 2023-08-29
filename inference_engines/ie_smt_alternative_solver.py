import json, sys, glob, io, os
import sqlite3
import pandas as pd
import time
from config import DBNAME


from z3_alternativeDrug import Solver_obj, check_prescription

conn = sqlite3.connect(DBNAME, timeout=10)


def getProcessedPatients(conn, patient):
    df = pd.read_sql_query(f"""  SELECT DISTINCT CD_PATIENT, CD_PRESCRIPTION 
                                from PRESC_INTERACTION
                                where CD_PATIENT = {patient}
                                and CD_PRESCRIPTION not in(SELECT CD_PRESCRIPTION FROM PRESCRIPTION_MODELS)
                                and  CD_PRESCRIPTION not in(SELECT CD_PRESCRIPTION FROM TIMEOUT_PRESCRIPTIONS)""", conn)
    patients = df.values.tolist()
    return(patients)
 

def getInteractionList(prescriptionPar, conn):
    df = pd.read_sql_query(f"""
            SELECT DRUG1, DRUG2 from DRUG_DRUG_INTERACTION
            WHERE CD_PRESCRIPTION =  "{prescriptionPar}"  """, conn)
    prescriptions = df.values.tolist()
    prescriptionList = []
    for prescription1 in prescriptions:
        temp = []
        for prescription2 in prescription1:
            temp.append(prescription2.replace(',','').replace('.','').replace('-','_').replace('/','_').replace("'",''))
        prescriptionList.append(temp)
    return(prescriptionList)

def getPrescrDrugsList(prescriptionPar, conn):
    df = pd.read_sql_query(f"""
            SELECT DISTINCT DRUG from PRESCRIPTION
            WHERE   CD_PRESCRIPTION =  "{prescriptionPar}"  """, conn)
    prescriptions = df.values.tolist()
    prescriptionList = []
    for prescription1 in prescriptions:
        for prescription2 in prescription1:
            prescriptionList.append(prescription2.replace(',','').replace('.','').replace('-','_').replace('/','_').replace("'",''))
    return(prescriptionList)

def getPrescrAlternativeList(prescriptionPar, conn):
    df = pd.read_sql_query(f"""
            SELECT DISTINCT DRUG from DRUG_ALTERNATIVE
            WHERE   CD_PRESCRIPTION =  "{prescriptionPar}"  """, conn)
    drugs = df.values.tolist()
    alternativeList = []
    
    for druglist in drugs:
        for drug in druglist:
            alternatives = []
            alternatives.append(drug.replace(',',''))
            df = pd.read_sql_query(f"""
                SELECT DISTINCT ALTERNATIVE from DRUG_ALTERNATIVE
                WHERE   CD_PRESCRIPTION =  "{prescriptionPar}"  
                AND DRUG = "{drug}" """, conn)
            for alterlist in df.values.tolist():
                for alter in alterlist:
                    alternatives.append(alter.replace(',','').replace('.','').replace('-','_').replace('/','_').replace("'",''))
            alternativeList.append(alternatives)
    return(alternativeList)

def getNumDrugprocessed(conn):
    df = pd.read_sql_query("SELECT count(CD_PATIENT) from PRESCRIPTION_MODELS", conn)
    patients = df.values.tolist()
    return(patients)

def getNumDrugs(conn):
    df = pd.read_sql_query("SELECT count(CD_PATIENT) from PRESCRIPTION", conn)
    patients = df.values.tolist()
    return(patients)

def checkAlternative(patient):
    print(f'#########################Inference engine: SMT alternative solver######################### \n')
    totalDrugs = getNumDrugs(conn)
    drugsProcessed = getNumDrugprocessed(conn)
    registers = getProcessedPatients(conn, patient)
    for patient, prescription in registers:
        print(f"Patient:{patient} - Prescription:{prescription} Time: {time.ctime(time.time()) } - Selecting patient inappropriate and alterantive drugs")
        drugs = getPrescrDrugsList(prescription, conn)
        alternative = getPrescrAlternativeList(prescription, conn)
        interaction = getInteractionList(prescription, conn)
        solverObject = Solver_obj
        solverObject.nr_prescription = prescription
        solverObject.prescription = drugs
        solverObject.interaction = interaction
        solverObject.alternative = alternative
        
        print(f"Patient:{patient} - Prescription:{prescription} Time: {time.ctime(time.time()) } - Inserting data into the SMT Solver")
        models = check_prescription(solverObject)

        print(f"Patient:{patient} - Prescription:{prescription} Time: {time.ctime(time.time()) } - Inserting results into the CDSS DB")
        if  models == 'canceled':
            params = (patient, prescription) 
            conn.execute("INSERT INTO TIMEOUT_PRESCRIPTIONS values (?,?)", params)
        elif models:
            for model in models:
                params = (patient, prescription,str(model)) 
                conn.execute("INSERT INTO PRESCRIPTION_MODELS values (?,?,?)", params)
        else:
            params = (patient, prescription,'null') 
            conn.execute("INSERT INTO PRESCRIPTION_MODELS values (?,?,?)", params)
        conn.commit()
