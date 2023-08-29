import sqlite3, sys
import pandas as pd
import time
import re
from owlready2 import *
from z3_scheduling import schedulingDrugs
from config import DBNAME, BEERSVERSION


version = BEERSVERSION
ONTOLOGY = fr'inference_engines/ontology_files/BeersOntologyV{version}.owl'
ONTOLOGY_NAME = f"BeersOntologyV{version}"
ONTO = get_ontology(ONTOLOGY).load()

conn = sqlite3.connect(DBNAME, timeout=10)


def checkLabel(name, type): #check if exist the label drug on the onotlogy and return the class name
    ONTOLOGY = fr'inference_engines/ontology_files/BeersOntologyV{version}.owl'
    ONTOLOGY_NAME = f"BeersOntologyV{version}"
    ONTO = get_ontology(ONTOLOGY).load()
    ch = '.'
    pattern  = ".*" + ch 
    classObj = ONTO.search(label = (name), _case_sensitive = False)
    if not classObj:
        classObj = ONTO.search(label = (name.replace('-', '_')), _case_sensitive = False)
    if not classObj:
        classObj = ONTO.search(label = (name.replace('_', '-')), _case_sensitive = False)
    if classObj:
        classObj = str(classObj[0]).split('.', 1)[-1]

        if isinstance(ONTO[classObj], ONTO[type]):
            return classObj
    else:
        return(None)



def getTmax(drug, ontology):
    value = 0
    labeldrug = checkLabel(drug, 'Drugs')
    response = list(default_world.sparql(f"""
            SELECT DISTINCT ?value 
            WHERE {{{ontology}:{labeldrug} rdfs:subClassOf ?object.
                ?object a owl:Restriction . 
                ?object owl:onProperty {ontology}:hasTmax. 
                ?object owl:qualifiedCardinality ?value }}"""))

    for data in response:
          value = str(data[0]) 
    if value == 0:
        value = 120
    return(value)



def getPatients(conn, patient):
    df = pd.read_sql_query(f""" SELECT DISTINCT CD_PATIENT FROM PRESCRIPTION_MODELS
                                WHERE CD_PATIENT = {patient}
                                and CD_PATIENT NOT IN (SELECT CD_PATIENT FROM PRESCRIPTION_RESCHEDULED)
                                AND MODEL = "null" 
                                """, conn)
    patients = df.values.tolist()
    patients = [patient for patientList in patients for patient in patientList]
    return(patients)


def getUnsatPrescriptions(conn, patientInput):
    df = pd.read_sql_query(f""" SELECT DISTINCT CD_PRESCRIPTION FROM PRESCRIPTION_MODELS 
                                WHERE CD_PATIENT = "{patientInput}"
                                AND MODEL = "null" 
                                AND CD_PRESCRIPTION NOT IN (SELECT CD_PRESCRIPTION FROM PRESCRIPTION_RESCHEDULED)
                                                                """, conn)
                                
    prescriptions = df.values.tolist()
    prescriptions = [prescription for prescriptionList in prescriptions for prescription in prescriptionList]
    return(prescriptions)


def getInteractions(conn, prescription):
    df = pd.read_sql_query(f""" SELECT B.DRUG1, B.DRUG2
                                FROM DRUG_DRUG_INTERACTION AS B
                                WHERE B.CD_PRESCRIPTION = "{prescription}" 
                                AND B.DRUG2 <> B.DRUG1""", conn)
    interactions = df.values.tolist()
    return(interactions)

def getInteractionsWithoutAlternative(conn, prescription):
    df = pd.read_sql_query(f""" SELECT B.DRUG1, B.DRUG2
                                FROM DRUG_DRUG_INTERACTION AS B
                                WHERE B.CD_PRESCRIPTION = "{prescription}" 
                                AND B.DRUG2 <> B.DRUG1
                                and B.DRUG2 not in (SELECT DISTINCT A.DRUG from DRUG_ALTERNATIVE AS A
                                                    WHERE   A.CD_PRESCRIPTION = "{prescription}")                   
                                                    """, conn)
    interactions = df.values.tolist()
    return(interactions)


def getPrescDrugDetails(conn, prescription, drug):
    df = pd.read_sql_query(f""" SELECT DISTINCT FREQUENCY, SCHEDULE, FIXEDTIME
                                FROM PRESCRIPTION
                                WHERE CD_PRESCRIPTION = "{prescription}" 
                                AND DRUG = "{drug}" """, conn)
    interactions = df.values.tolist()
    return(interactions)


def getNumDrugprocessed(conn):
    df = pd.read_sql_query("SELECT count(CD_PATIENT) from PRESCRIPTION_MODELS", conn)
    patients = df.values.tolist()
    return(patients)

def getNumDrugs(conn):
    df = pd.read_sql_query("SELECT count(CD_PATIENT) from PRESCRIPTION", conn)
    patients = df.values.tolist()
    return(patients)




def checkRescheduling(patient):
    print(f'#########################Inference engine: SMT rescheduling solver######################### \n')
    totalDrugs = getNumDrugs(conn)
    patients = getPatients(conn, patient)
     
    for patient in patients:
        prescriptions = getUnsatPrescriptions(conn, patient)
        for prescription in prescriptions:
            print(f"Patient:{patient} - Prescription:{prescription} Time: {time.ctime(time.time()) } - Selecting inappropriate drugs")
            interaction = getInteractionsWithoutAlternative(conn, prescription)
            druglist = []
            drugdic = {}
            if interaction:
                for drug1, drug2 in interaction:
                    if sorted([drug1, drug2]) not in druglist:
                        druglist.append(sorted([drug1, drug2]))
                        print(f"Patient:{patient} - Prescription:{prescription} Time: {time.ctime(time.time()) } - Selecting drug parameters")
                        details = getPrescDrugDetails(conn, prescription, drug1)
                        drugdic[drug1] = [details]
                        print(f"Patient:{patient} - Prescription:{prescription} Time: {time.ctime(time.time()) } - SPARQL - Selecting Tmax value")
                        drugdic[drug1].append(getTmax(drug1, ONTOLOGY_NAME.replace('.', '')))
                        details = getPrescDrugDetails(conn, prescription, drug2)
                        drugdic[drug2] = [details]
                        drugdic[drug2].append(getTmax(drug2, ONTOLOGY_NAME.replace('.', '')))
                        patientPref = []
                print(f"Patient:{patient} - Prescription:{prescription} Time: {time.ctime(time.time()) } - Inserting drug into Z3 model")
                sat, result = schedulingDrugs(druglist, drugdic, patientPref)
                params = (patient, prescription,sat,str(result))
                print(f"Patient:{patient} - Prescription:{prescription} Time: {time.ctime(time.time()) } - Inserting results into the CDSS DB")
                conn.execute("INSERT INTO PRESCRIPTION_RESCHEDULED values (?,?,?,?)", params)
        conn.commit()

