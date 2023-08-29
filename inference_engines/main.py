from ie_beers_criteria_interactions import checkInteraction
from ie_smt_alternative_solver import checkAlternative
from ie_smt_rescheduling_solver import checkRescheduling
from Utils.dbInsert import importPatients
from Utils.dbCreate import resetDB
from result_queries import results
import sqlite3
import pandas as pd
from config import DBNAME
import time

resetDB() # Recreate the DB
importPatients(True) # Insert patient data into the DB - Folder: /data/patient_data

conn = sqlite3.connect(DBNAME, timeout=10) 

def getPatients(conn): # Get patients from the CDSS DB
    df = pd.read_sql_query("""
                            SELECT distinct (A.CD_PATIENT)
                            FROM PATIENT A""", conn)
    patients = df.values.tolist()
    return(patients)

patients = getPatients(conn)

for patient in patients:
    checkInteraction(patient[0]) #Check if there are inappropriate medications in each prescription
    checkAlternative(patient[0]) #Check if SAT prescriptions can be found with alternative drugs
    checkRescheduling(patient[0]) #Reschedule drug-drug interaction
    
results() #Folder: /results/CDSS
