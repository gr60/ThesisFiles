import sys, json, io, glob
import time
from owlready2 import *
from dateutil import parser
from import_files import importFile, listOccurence, listPatients, listExams, listPreviousDisease, listPrescrDays
from datetime import datetime
import pandas as pd
import sqlite3
from config import DBNAME, BEERSVERSION


conn = sqlite3.connect(DBNAME, timeout=10)
c = conn.cursor()
default_world.set_backend(filename = fr'inference_engines/ontology_files/t.sqlite3', exclusive = False)

version =  BEERSVERSION


ONTOLOGY = fr'inference_engines/ontology_files/BeersOntologyV{version}.owl'
ONTOLOGY_NAME = f"BeersOntologyV{version}."
ONTO = get_ontology(ONTOLOGY).load()
DRUGS = 'Drugs'
ROUTE = 'AdministrationRoute'
DISEASE = 'Disease'
BEERS = 'BeersCriteria'
EXAMS = 'Exams'
PATIENT = 'Patient'
PROCESSED_ROWS = 0

DrugNotRegistered = set()
RouteNotRegistered = set()
DiseaseNotRegistered = set()
ExamNotRegistered = set()
PacientNotRegisted = set()
Exceptions = set()




################################################################################################################
#################################ONTOLOGY FUNCTIONS#############################################################
################################################################################################################

def checkLabel(name, type): #check if exist the label drug on the onotlogy and return the class name
    classObj = ONTO.search(label = (name))
    if not classObj:
        classObj = ONTO.search(label = (name.replace('-', '_')), _case_sensitive = False)
    if not classObj:
        classObj = ONTO.search(label = (name.replace('_', '-')), _case_sensitive = False)
    if classObj:
        classObj = str(classObj[0]).replace(ONTOLOGY_NAME,'')

        if isinstance(ONTO[classObj], ONTO[type]):
            return classObj
    else:
        return(None)

def checkIndividual(name): #check if exist the label drug on the onotlogy and return the class name
    classObj = ONTO.search(iri = '*'+str(name), _case_sensitive = False)
    if classObj:
        return(True)
    else:
        return(False)


def addOntologyPatients(patientList): #Select patient data and send to the function addIndividualPatient
        for index, row in patientList.iterrows():
            name = row['CD_PATIENT']
            age = int(row['AGE'])
            gender = row['GENDER']
            composeName = str(name)+"-"+str(age)+"-"+str(gender)
            hospitalizationDate = row['DT_Admission']
            dischargeDate = row['DT_discharge']
            procedureName = row['MAIN_PROCEDURE']
            duration = pd.to_datetime(row['DT_discharge']) - pd.to_datetime(row['DT_Admission']) 
            lenghtTreatment = duration.days
            #Insert parameters into the ontology
            individual = ONTO.Patient(composeName)
            individual.hasPatientAgeValue = age
            individual.hasLenghtTreatment = lenghtTreatment
            addOntologyDisease(procedureName, composeName)
            if gender == 'M':
                individual.hasGender.append(ONTO.iMale)
            else:
                individual.hasGender.append(ONTO.iFemale)

def addOntologyDisease(name, patient):
    if checkIndividual(patient):
        diseaseName = (str(patient)+"-"+str(name))
        if checkIndividual(diseaseName):
            ONTO[patient].hasDisease.append(ONTO[diseaseName])
            return('Disease already registered')
        else:
            classObj = checkLabel(name, DISEASE)
            if classObj:
                individualdisease = ONTO[classObj](diseaseName)
                ONTO[patient].hasDisease.append(individualdisease)
                return('Disease registered')
            else:
                DiseaseNotRegistered.add(name) 
                return(None)
    else:
        PacientNotRegisted.add(patient) 
        print(f'{PacientNotRegisted} PacientNotRegisted')
        return(None)

def addOntologyExam(examList, age, gender):
    for index, row in examList.iterrows():
        patient = row['CD_PATIENT']
        seqResult = row['seq_Result']
        exam = row['nm_Exam']
        result = float(row['qt_Result'])
        date = row['dt_Result']
        composeName = str(patient)+"-"+str(age)+"-"+str(gender)
        examName = str(composeName) +"-"+ exam+"-"+str(seqResult)
               
        if checkIndividual(examName):
            ONTO[examName].hasExamValue.append(result)
            ONTO[composeName].hasExam.append(ONTO[examName])
            return('Exam already registered')
        else:
            classObj = checkLabel(exam, EXAMS)
            if classObj:
                if checkIndividual(composeName):
                    individualexam = ONTO[classObj](examName)
                    ONTO[composeName].hasExam.append(individualexam)
                    individualexam.hasExamValue.append(result)
                else:
                    ExamNotRegistered.add(exam)

    
## Prescription functions
def addOntologyDrug(name, patient, prescription, age, route, dose, gender, drugNameOriginal, typeDrug, drugLenght,criticalPatient,firstLine,release ):
    classDrug = checkLabel(name, DRUGS)
    classRoute = checkLabel(route, ROUTE)
    classRelease = checkLabel(release, 'ReleaseDrug')
    global PROCESSED_ROWS
    PROCESSED_ROWS += 1
    if typeDrug == 'S' or typeDrug =='C':
        if classDrug and classRoute:
            individual = ONTO[classDrug](str((str(prescription)+"-"+str(name))).replace('/', "-"))
            individual.hasPatientAgeValue = age
            individual.hasLenghtDrugTherapie = drugLenght
            individual.isAlternative.append(False)
            individual.hasGender.append(gender)
            currentDose = individual.hasDailydoseValue
            if criticalPatient == 'False' or criticalPatient == 'false' or criticalPatient == 'F':
                individual.isCriticalPatient.append(False)
            else:
                individual.isCriticalPatient.append(True)
            
            if firstLine == 'False' or firstLine == 'false' or firstLine == 'F':
                individual.isFirstLine.append(False)
            else:
                individual.isFirstLine.append(True)
            
            individual.toRelease.append(ONTO[classRelease]) 
            if currentDose:
                dose = int(currentDose) + dose
            individual.hasDailydoseValue = dose
            individual.hasRoute.append(ONTO[classRoute])
            if checkIndividual(prescription):
                ONTO[patient].hasPrescription.append(ONTO[prescription])
            else:
                individualPrescr = ONTO['Prescription'](str(prescription))
                ONTO[patient].hasPrescription.append(individualPrescr)
            ONTO[prescription].hasDrug.append(ONTO[(str((str(prescription)+"-"+str(name))).replace('/', "-"))])
            return(individual)
        else: 
            if not classDrug:
                DrugNotRegistered.add(name)
                print(f'{DrugNotRegistered} DrugNotRegistered')
            if not classRoute:
                RouteNotRegistered.add(route)
                print(f'{RouteNotRegistered} RouteNotRegistered')
            return(None)
    else:
        individual = ONTO[name](str((str(prescription)+'_ALT_'+str(name))).replace('/', "-"))
        individual.hasPatientAgeValue = age
        individual.hasLenghtDrugTherapie = drugLenght
        individual.isAlternative.append(False)
        currentDose = individual.hasDailydoseValue
        if currentDose:
            dose = currentDose + dose
        individual.hasDailydoseValue.append(dose)
        individual.hasRoute.append(ONTO[classRoute])
        if checkIndividual(prescription):
            ONTO[patient].hasPrescription.append(ONTO[prescription])
        else:
            individualPrescr = ONTO['Prescription'](str(prescription))
            ONTO[patient].hasPrescription.append(individualPrescr)
        ONTO[prescription].hasDrug.append(ONTO[(str(str(prescription)+'_ALT_'+str(name)).replace('/', "-"))])
        

def addOntologyDrugAssertions(patient, day, age, gender): #Add an individual patient
        if gender == 'M':
            Indvgender = ONTO.iMale
        else:
            Indvgender = ONTO.iFemale
        
        presc_day = str(patient)+"-"+str(age)+"-"+str(gender) +"-"+str(day).replace("-", "").replace("/", "")
        patientName = str(patient)+"-"+str(age)+"-"+str(gender)
        if patient:
            drugs = ONTO[presc_day].hasDrug
            diseases = ONTO[patientName].hasDisease
            for drug in drugs:
                drug.hasGender.append(Indvgender)
                for disease in diseases:
                    drug.hasTreatmentIndication.append(disease)
        alternatives = ONTO.search(iri = '*alt_*', _case_sensitive = False, isAlternative = True )
        for alternative in alternatives:
            if isinstance(alternative, ONTO['Alternative_Drugs']):
                alternative.hasPatientAgeValue = age
                alternative.hasGender.append(Indvgender)

def addPrescription(prescription_df, age, gender): #Select patient data and send to the function 
        if gender == 'M':
            Indvgender = ONTO.iMale
        else:
            Indvgender = ONTO.iFemale
        prescrdata={}
        header = {}
        body = []
        index = prescription_df.index.tolist()
        counter = int(prescription_df["CD_PATIENT"][index[0]])
        header = {"Counter": counter, "Gender": gender,"Age": age}
        for i in index:
            drugName = ''.join(str(prescription_df["DRUG"][i]).rstrip().lstrip()).replace(" ", "_") 
            drugNameOriginal = ''.join(str(prescription_df["DS_DRUG_ORIGINAL"][i]).rstrip().lstrip()).replace(" ", "_")
            composeName = str(counter)+"-"+str(age)+"-"+str(gender)
            route = ''.join(str(prescription_df["ROUTE"][i]).rstrip().lstrip()).replace(" ", "_") 
            startDateInt = str(prescription_df['START_DATE'][i]).replace("/", "").replace("-", "")  
            startDate = str(prescription_df['START_DATE'][i])
            endDate = str(prescription_df['END_DATE'][i])
            schedule = str(prescription_df['SCHEDULE'][i])
            frequency = str(prescription_df['FREQUENCY'][i])
            typeDrug =  str(prescription_df['TYPE_DRUG'][i])
            criticalPatient =  str(prescription_df['CRITICAL_PATIENT'][i])
            firstLine =  str(prescription_df['FIRST_LINE'][i])
            release =  str(prescription_df['RELEASE'][i])
            drugLenght = int(prescription_df['Drug_Lenght'][i])
            presc_day = str(counter)+"-"+str(age)+"-"+str(gender) +"-"+str(startDateInt)
            if typeDrug == 'S':
                dose = int(prescription_df['DOSE'][i])
                addOntologyDrug(drugName, composeName, presc_day, age, route, dose, Indvgender, drugNameOriginal, typeDrug, drugLenght,criticalPatient,firstLine,release )
                body.append({'DrugName': drugName , 'DrugNameOriginal':drugNameOriginal, 'Route' :route, 'Dose' :dose, 'TypeDrug':typeDrug, 'StartDate':startDate, 'EndDate':endDate, 'Schedule':schedule, 'Frequency':frequency, 'CriticalPatient':criticalPatient , 'FirstLine':firstLine , 'Release':release  })
            else:
                drugName = ''.join(str(prescription_df["DRUG"][i]).rstrip().lstrip()).replace(" ", "-") 
                dose = int(prescription_df['DOSE'][i])
                addOntologyDrug(drugName, composeName, presc_day, age, route, dose, Indvgender, drugNameOriginal, typeDrug, drugLenght,criticalPatient,firstLine,release )
                body.append({'DrugName': drugName , 'DrugNameOriginal':drugNameOriginal, 'Route' :route, 'Dose' :dose, 'TypeDrug':typeDrug, 'StartDate':startDate, 'EndDate':endDate, 'Schedule':schedule, 'Frequency':frequency, 'CriticalPatient':criticalPatient , 'FirstLine':firstLine , 'Release':release  })
                try:
                    for x in range(3):
                        if len(str(prescription_df['DS_COM_DRUG'+str(x)][i])) > 3:
                            drugName = ''.join(str(prescription_df['DS_COM_DRUG'+str(x)][i]).rstrip().lstrip()).replace(" ", "-")
                            dose = int(prescription_df['DOSE_COM'+str(x)][i])
                            addOntologyDrug(drugName, composeName, presc_day, age, route, dose, Indvgender, drugNameOriginal, typeDrug, drugLenght,criticalPatient,firstLine,release )
                            body.append({'DrugName': drugName , 'DrugNameOriginal':drugNameOriginal, 'Route' :route, 'Dose' :dose, 'TypeDrug':typeDrug, 'StartDate':startDate, 'EndDate':endDate, 'Schedule':schedule, 'Frequency':frequency, 'CriticalPatient':criticalPatient , 'FirstLine':firstLine , 'Release':release  })
                except Exception as e: Exceptions.add('')
        prescrdata = {'Header': header, 'Drugs': body}
        return (prescrdata)

def addDisease(diseaseList, age, gender): #Select patient data and send to the function addIndividualPatient
        for index, row in diseaseList.iterrows():
            patient = row['CD_PATIENT']
            disease = row['nm_Disease']
            composeName = str(patient)+"-"+str(age)+"-"+str(gender)
            addOntologyDisease(disease, composeName)


################################################################################################################
#################################get Results - SPARQL####################################################################
################################################################################################################

def getPrescriptionInteractions(patient, prescription, ontology, dbcon):
    queryDrug1 = list(default_world.sparql(f"""
            SELECT DISTINCT ?Drug ?Interaction1 ?Interaction2 ?QualityofEvidence ?StrengthofRecommendation ?quant  ?recommendation ?detail
            WHERE {{{ontology}:{prescription} {ontology}:hasDrug ?Drug . 
                ?Drug rdf:type   ?Interaction1 . 
                ?Interaction1 rdfs:subClassOf  ?Interaction2 . 
                ?Interaction2 rdfs:subClassOf  {ontology}:BeersCriteria . 
                ?Interaction1 rdfs:subClassOf ?QoF . 
                ?Interaction1 rdfs:subClassOf ?SoR . 
                ?QoF a owl:Restriction . 
                ?QoF owl:onProperty {ontology}:hasQualityofEvidence. 
                ?QoF owl:someValuesFrom ?QualityofEvidence . 
                ?SoR a owl:Restriction . 
                ?SoR owl:onProperty {ontology}:hasStrengthofRecommendation. 
                ?SoR owl:someValuesFrom ?StrengthofRecommendation.
                optional {{?Interaction1 {ontology}:intDrugQuantity  ?quant}}
                optional {{?Interaction1 {ontology}:recommendation  ?recommendation}}
                optional {{?Interaction1 rdfs:comment  ?detail}}
                FILTER( CONTAINS( STR(?Interaction1), STR(?Interaction2) ) ) 
                }} """))
    queryDrug2 = list(default_world.sparql(f"""
            SELECT DISTINCT  ?Drug ?Interaction1 ?Interaction2 ?Interaction3 ?QualityofEvidence ?StrengthofRecommendation ?quant  ?recommendation ?detail
            WHERE {{{ontology}:{prescription} {ontology}:hasDrug ?Drug . 
                ?Drug rdf:type   ?Interaction1 . 
                ?Interaction1 rdfs:subClassOf  ?Interaction2 .  
                ?Interaction2 rdfs:subClassOf  ?Interaction3 . 
                ?Interaction3 rdfs:subClassOf  {ontology}:BeersCriteria . 
                ?Interaction1 rdfs:subClassOf ?QoF . 
                ?Interaction1 rdfs:subClassOf ?SoR . 
                ?QoF a owl:Restriction . 
                ?QoF owl:onProperty {ontology}:hasQualityofEvidence. 
                ?QoF owl:someValuesFrom ?QualityofEvidence . 
                ?SoR a owl:Restriction . 
                ?SoR owl:onProperty {ontology}:hasStrengthofRecommendation. 
                ?SoR owl:someValuesFrom ?StrengthofRecommendation.  
                optional {{?Interaction1 {ontology}:intDrugQuantity  ?quant}}
                optional {{?Interaction1 {ontology}:recommendation  ?recommendation}}
                optional {{?Interaction1 rdfs:comment  ?detail}}
                FILTER( CONTAINS( STR(?Interaction1), STR(?Interaction3) ) ) 
                }} """))
    queryDrug3 = list(default_world.sparql(f"""
            SELECT DISTINCT  ?Drug ?Interaction1 ?Interaction2 ?Interaction3 ?Interaction4 ?QualityofEvidence ?StrengthofRecommendation ?quant  ?recommendation ?detail
            WHERE {{{ontology}:{prescription} {ontology}:hasDrug ?Drug . 
                ?Drug rdf:type   ?Interaction1 . 
                ?Interaction1 rdfs:subClassOf  ?Interaction2 .  
                ?Interaction2 rdfs:subClassOf  ?Interaction3 . 
                ?Interaction3 rdfs:subClassOf  ?Interaction4 .
                ?Interaction4 rdfs:subClassOf  {ontology}:BeersCriteria . 
                ?Interaction1 rdfs:subClassOf ?QoF . 
                ?Interaction1 rdfs:subClassOf ?SoR . 
                ?QoF a owl:Restriction . 
                ?QoF owl:onProperty {ontology}:hasQualityofEvidence. 
                ?QoF owl:someValuesFrom ?QualityofEvidence . 
                ?SoR a owl:Restriction . 
                ?SoR owl:onProperty {ontology}:hasStrengthofRecommendation. 
                ?SoR owl:someValuesFrom ?StrengthofRecommendation.  
                optional {{?Interaction1 {ontology}:intDrugQuantity  ?quant}}
                optional {{?Interaction1 {ontology}:recommendation  ?recommendation}}
                optional {{?Interaction1 rdfs:comment  ?detail}} 
                FILTER( CONTAINS( STR(?Interaction1), STR(?Interaction4) ) ) 
                }} 
                """))
    queryDrug4 = list(default_world.sparql(f"""
            SELECT DISTINCT  ?Drug ?Interaction2 ?Interaction3 ?Interaction4 ?QualityofEvidence ?StrengthofRecommendation ?quant  ?recommendation ?detail
            WHERE {{{ontology}:{prescription} {ontology}:hasDrug ?Drug . 
                ?Drug rdf:type   ?Interaction1 . 
                ?Interaction1 rdfs:subClassOf  ?Interaction2 .  
                ?Interaction2 rdfs:subClassOf  ?Interaction3 .
                ?Interaction3 rdfs:subClassOf  ?Interaction4 .
                ?Interaction4 rdfs:subClassOf  {ontology}:BeersCriteria .
                ?Interaction2 rdfs:subClassOf ?QoF . 
                ?Interaction2 rdfs:subClassOf ?SoR . 
                ?QoF a owl:Restriction . 
                ?QoF owl:onProperty {ontology}:hasQualityofEvidence. 
                ?QoF owl:someValuesFrom ?QualityofEvidence . 
                ?SoR a owl:Restriction . 
                ?SoR owl:onProperty {ontology}:hasStrengthofRecommendation. 
                ?SoR owl:someValuesFrom ?StrengthofRecommendation. 
                optional {{?Interaction2 {ontology}:intDrugQuantity  ?quant}}
                optional {{?Interaction2 {ontology}:recommendation  ?recommendation}}
                optional {{?Interaction2 rdfs:comment  ?detail}}
                FILTER( CONTAINS( STR(?Interaction2), STR(?Interaction4) ) ) 
                }} """))
    queryDrug5 = list(default_world.sparql(f"""
            SELECT DISTINCT  ?Drug ?Interaction2 ?Interaction3 ?QualityofEvidence ?StrengthofRecommendation ?quant  ?recommendation ?detail
            WHERE {{{ontology}:{prescription} {ontology}:hasDrug ?Drug . 
                ?Drug rdf:type   ?Interaction1 . 
                ?Interaction1 rdfs:subClassOf  ?Interaction2 .  
                ?Interaction2 rdfs:subClassOf  ?Interaction3 .
                ?Interaction3 rdfs:subClassOf  ?Interaction4 .
                ?Interaction3 rdfs:subClassOf  {ontology}:BeersCriteria .
                ?Interaction2 rdfs:subClassOf ?QoF . 
                ?Interaction2 rdfs:subClassOf ?SoR . 
                ?QoF a owl:Restriction . 
                ?QoF owl:onProperty {ontology}:hasQualityofEvidence. 
                ?QoF owl:someValuesFrom ?QualityofEvidence . 
                ?SoR a owl:Restriction . 
                ?SoR owl:onProperty {ontology}:hasStrengthofRecommendation. 
                ?SoR owl:someValuesFrom ?StrengthofRecommendation. 
                optional {{?Interaction2 {ontology}:intDrugQuantity  ?quant}}
                optional {{?Interaction2 {ontology}:recommendation  ?recommendation}}
                optional {{?Interaction2 rdfs:comment  ?detail}}
                FILTER( CONTAINS( STR(?Interaction2), STR(?Interaction3) ) ) 
                }} """))
    queryAlternative1 = list(default_world.sparql(f"""
            SELECT DISTINCT ?Alternative ?Interaction1 ?Interaction2 ?QualityofEvidence ?StrengthofRecommendation ?quant  ?recommendation ?detail
            WHERE {{{ontology}:{prescription} {ontology}:hasDrug ?Drug .
                ?Drug  {ontology}:hasAlternative ?Alternative  
                ?Alternative rdf:type   ?Interaction1 .
                ?Interaction1 rdfs:subClassOf  ?Interaction2 . 
                ?Interaction2 rdfs:subClassOf  {ontology}:BeersCriteria . 
                ?Interaction1 rdfs:subClassOf ?QoF . 
                ?Interaction1 rdfs:subClassOf ?SoR . 
                ?QoF a owl:Restriction . 
                ?QoF owl:onProperty {ontology}:hasQualityofEvidence. 
                ?QoF owl:someValuesFrom ?QualityofEvidence . 
                ?SoR a owl:Restriction . 
                ?SoR owl:onProperty {ontology}:hasStrengthofRecommendation. 
                ?SoR owl:someValuesFrom ?StrengthofRecommendation.
                optional {{?Interaction1 {ontology}:intDrugQuantity  ?quant}}
                optional {{?Interaction1 {ontology}:recommendation  ?recommendation}}
                optional {{?Interaction1 rdfs:comment  ?detail}}
                FILTER( CONTAINS( STR(?Interaction1), STR(?Interaction2) ) ) 
                }} """))
    queryAlternative2 = list(default_world.sparql(f"""
            SELECT DISTINCT  ?Alternative ?Interaction1 ?Interaction2 ?Interaction3 ?QualityofEvidence ?StrengthofRecommendation ?quant  ?recommendation ?detail
            WHERE {{{ontology}:{prescription} {ontology}:hasDrug ?Drug .
                ?Drug  {ontology}:hasAlternative ?Alternative  
                ?Alternative rdf:type   ?Interaction1 . 
                ?Interaction1 rdfs:subClassOf  ?Interaction2 .  
                ?Interaction2 rdfs:subClassOf  ?Interaction3 . 
                ?Interaction3 rdfs:subClassOf  {ontology}:BeersCriteria . 
                ?Interaction1 rdfs:subClassOf ?QoF . 
                ?Interaction1 rdfs:subClassOf ?SoR . 
                ?QoF a owl:Restriction . 
                ?QoF owl:onProperty {ontology}:hasQualityofEvidence. 
                ?QoF owl:someValuesFrom ?QualityofEvidence . 
                ?SoR a owl:Restriction . 
                ?SoR owl:onProperty {ontology}:hasStrengthofRecommendation. 
                ?SoR owl:someValuesFrom ?StrengthofRecommendation.  
                optional {{?Interaction1 {ontology}:intDrugQuantity  ?quant}}
                optional {{?Interaction1 {ontology}:recommendation  ?recommendation}}
                optional {{?Interaction1 rdfs:comment  ?detail}}
                FILTER( CONTAINS( STR(?Interaction1), STR(?Interaction3) ) ) 
                }} """))
    queryAlternative3 = list(default_world.sparql(f"""
            SELECT DISTINCT  ?Alternative ?Interaction1 ?Interaction2 ?Interaction3 ?Interaction4 ?QualityofEvidence ?StrengthofRecommendation ?quant  ?recommendation ?detail
            WHERE {{{ontology}:{prescription} {ontology}:hasDrug ?Drug .
                ?Drug  {ontology}:hasAlternative ?Alternative  
                ?Alternative rdf:type   ?Interaction1 .
                ?Interaction1 rdfs:subClassOf  ?Interaction2 .  
                ?Interaction2 rdfs:subClassOf  ?Interaction3 . 
                ?Interaction3 rdfs:subClassOf  ?Interaction4 .
                ?Interaction4 rdfs:subClassOf  {ontology}:BeersCriteria . 
                ?Interaction1 rdfs:subClassOf ?QoF . 
                ?Interaction1 rdfs:subClassOf ?SoR . 
                ?QoF a owl:Restriction . 
                ?QoF owl:onProperty {ontology}:hasQualityofEvidence. 
                ?QoF owl:someValuesFrom ?QualityofEvidence . 
                ?SoR a owl:Restriction . 
                ?SoR owl:onProperty {ontology}:hasStrengthofRecommendation. 
                ?SoR owl:someValuesFrom ?StrengthofRecommendation.  
                optional {{?Interaction1 {ontology}:intDrugQuantity  ?quant}}
                optional {{?Interaction1 {ontology}:recommendation  ?recommendation}}
                optional {{?Interaction1 rdfs:comment  ?detail}} 
                FILTER( CONTAINS( STR(?Interaction1), STR(?Interaction4) ) ) 
                }} 
                """))
    queryAlternative4 = list(default_world.sparql(f"""
            SELECT DISTINCT  ?Alternative ?Interaction2 ?Interaction3 ?Interaction4 ?QualityofEvidence ?StrengthofRecommendation ?quant  ?recommendation ?detail
            WHERE {{{ontology}:{prescription} {ontology}:hasDrug ?Drug .
                ?Drug  {ontology}:hasAlternative ?Alternative  
                ?Alternative rdf:type   ?Interaction1 .
                ?Interaction1 rdfs:subClassOf  ?Interaction2 .  
                ?Interaction2 rdfs:subClassOf  ?Interaction3 .
                ?Interaction3 rdfs:subClassOf  ?Interaction4 .
                ?Interaction4 rdfs:subClassOf  {ontology}:BeersCriteria .
                ?Interaction2 rdfs:subClassOf ?QoF . 
                ?Interaction2 rdfs:subClassOf ?SoR . 
                ?QoF a owl:Restriction . 
                ?QoF owl:onProperty {ontology}:hasQualityofEvidence. 
                ?QoF owl:someValuesFrom ?QualityofEvidence . 
                ?SoR a owl:Restriction . 
                ?SoR owl:onProperty {ontology}:hasStrengthofRecommendation. 
                ?SoR owl:someValuesFrom ?StrengthofRecommendation. 
                optional {{?Interaction2 {ontology}:intDrugQuantity  ?quant}}
                optional {{?Interaction2 {ontology}:recommendation  ?recommendation}}
                optional {{?Interaction2 rdfs:comment  ?detail}}
                FILTER( CONTAINS( STR(?Interaction2), STR(?Interaction4) ) ) 
                }} """))
    queryAlternative5 = list(default_world.sparql(f"""
            SELECT DISTINCT  ?Alternative ?Interaction2 ?Interaction3 ?QualityofEvidence ?StrengthofRecommendation ?quant  ?recommendation ?detail
            WHERE {{{ontology}:{prescription} {ontology}:hasDrug ?Drug .
                ?Drug  {ontology}:hasAlternative ?Alternative  
                ?Alternative rdf:type   ?Interaction1 .
                ?Interaction1 rdfs:subClassOf  ?Interaction2 .  
                ?Interaction2 rdfs:subClassOf  ?Interaction3 .
                ?Interaction3 rdfs:subClassOf  ?Interaction4 .
                ?Interaction3 rdfs:subClassOf  {ontology}:BeersCriteria .
                ?Interaction2 rdfs:subClassOf ?QoF . 
                ?Interaction2 rdfs:subClassOf ?SoR . 
                ?QoF a owl:Restriction . 
                ?QoF owl:onProperty {ontology}:hasQualityofEvidence. 
                ?QoF owl:someValuesFrom ?QualityofEvidence . 
                ?SoR a owl:Restriction . 
                ?SoR owl:onProperty {ontology}:hasStrengthofRecommendation. 
                ?SoR owl:someValuesFrom ?StrengthofRecommendation. 
                optional {{?Interaction2 {ontology}:intDrugQuantity  ?quant}}
                optional {{?Interaction2 {ontology}:recommendation  ?recommendation}}
                optional {{?Interaction2 rdfs:comment  ?detail}}
                FILTER( CONTAINS( STR(?Interaction2), STR(?Interaction3) ) ) 
                }} """))

    for data in queryDrug1:
        patientDb = patient
        drug =  str(data[0]).replace(f"{ontology}.", '').replace(f"{prescription}-", '')
        interaction1 = str(data[2]).replace(f"{ontology}.", '')
        interaction2 =  str(data[1]).replace(f"{ontology}.", '')
        interaction3 =  str(data[1]).replace(f"{ontology}.", '')
        interaction4 =  str(data[1]).replace(f"{ontology}.", '')
        QoF = str(data[3]).replace(f"{ontology}.", '')
        SoR =  str(data[4]).replace(f"{ontology}.", '')
        intDrugNum = str(data[5]).replace(f"{ontology}.", '')
        #intDrugCat =  str(data[6]).replace(f"{ontology}.", '')
        recommendation =  str(data[6]).replace(f"{ontology}.", '')
        detail =  str(data[7]).replace(f"{ontology}.", '')
        params = (patientDb, prescription, drug,intDrugNum, interaction1, interaction2, interaction3, interaction4, QoF, SoR, detail, recommendation, "F") 
        dbcon.execute("INSERT INTO PRESC_INTERACTION values (?,?,?,?,?,?,?,?,?,?,?,?,?)", params)
        
    for data in queryDrug2:
        patientDb = patient
        drug =  str(data[0]).replace(f"{ontology}.", '').replace(f"{prescription}-", '')
        interaction4 = str(data[1]).replace(f"{ontology}.", '')
        interaction3 = str(data[1]).replace(f"{ontology}.", '')
        interaction2 =  str(data[2]).replace(f"{ontology}.", '')
        interaction1 =  str(data[3]).replace(f"{ontology}.", '')
        QoF = str(data[4]).replace(f"{ontology}.", '')
        SoR =  str(data[5]).replace(f"{ontology}.", '')
        intDrugNum = str(data[6]).replace(f"{ontology}.", '')
        #intDrugCat =  str(data[6]).replace(f"{ontology}.", '')
        recommendation =  str(data[7]).replace(f"{ontology}.", '')
        detail =  str(data[8]).replace(f"{ontology}.", '')
        params = (patientDb, prescription, drug,intDrugNum, interaction1, interaction2, interaction3, interaction4, QoF, SoR, detail, recommendation, "F") 
        dbcon.execute("INSERT INTO PRESC_INTERACTION values (?,?,?,?,?,?,?,?,?,?,?,?,?)", params)

    for data in queryDrug3:
        patientDb = patient
        drug =  str(data[0]).replace(f"{ontology}.", '').replace(f"{prescription}-", '')
        interaction4 = str(data[1]).replace(f"{ontology}.", '')
        interaction3 = str(data[1]).replace(f"{ontology}.", '')
        interaction2 =  str(data[2]).replace(f"{ontology}.", '')
        interaction1 =  str(data[4]).replace(f"{ontology}.", '')
        QoF = str(data[5]).replace(f"{ontology}.", '')
        SoR =  str(data[6]).replace(f"{ontology}.", '')
        intDrugNum = str(data[7]).replace(f"{ontology}.", '')
        #intDrugCat =  str(data[6]).replace(f"{ontology}.", '')
        recommendation =  str(data[8]).replace(f"{ontology}.", '')
        detail =  str(data[9]).replace(f"{ontology}.", '')
        params = (patientDb, prescription, drug,intDrugNum, interaction1, interaction2, interaction3, interaction4, QoF, SoR, detail, recommendation, "F") 
        dbcon.execute("INSERT INTO PRESC_INTERACTION values (?,?,?,?,?,?,?,?,?,?,?,?,?)", params)

    for data in queryDrug4:
        patientDb = patient
        drug =  str(data[0]).replace(f"{ontology}.", '').replace(f"{prescription}-", '')
        interaction4 = str(data[1]).replace(f"{ontology}.", '')
        interaction3 = str(data[1]).replace(f"{ontology}.", '')
        interaction2 =  str(data[2]).replace(f"{ontology}.", '')
        interaction1 =  str(data[3]).replace(f"{ontology}.", '')
        QoF = str(data[4]).replace(f"{ontology}.", '')
        SoR =  str(data[5]).replace(f"{ontology}.", '')
        intDrugNum = str(data[6]).replace(f"{ontology}.", '')
        #intDrugCat =  str(data[6]).replace(f"{ontology}.", '')
        recommendation =  str(data[7]).replace(f"{ontology}.", '')
        detail =  str(data[8]).replace(f"{ontology}.", '')
        params = (patientDb, prescription, drug,intDrugNum, interaction1, interaction2, interaction3, interaction4, QoF, SoR, detail, recommendation, "F") 
        dbcon.execute("INSERT INTO PRESC_INTERACTION values (?,?,?,?,?,?,?,?,?,?,?,?,?)", params)

    for data in queryDrug5:
        patientDb = patient
        drug =  str(data[0]).replace(f"{ontology}.", '').replace(f"{prescription}-", '')
        interaction1 = str(data[2]).replace(f"{ontology}.", '')
        interaction2 =  str(data[1]).replace(f"{ontology}.", '')
        interaction3 =  str(data[1]).replace(f"{ontology}.", '')
        interaction4 =  str(data[1]).replace(f"{ontology}.", '')
        QoF = str(data[3]).replace(f"{ontology}.", '')
        SoR =  str(data[4]).replace(f"{ontology}.", '')
        intDrugNum = str(data[5]).replace(f"{ontology}.", '')
        #intDrugCat =  str(data[6]).replace(f"{ontology}.", '')
        recommendation =  str(data[6]).replace(f"{ontology}.", '')
        detail =  str(data[7]).replace(f"{ontology}.", '')
        params = (patientDb, prescription, drug,intDrugNum, interaction1, interaction2, interaction3, interaction4, QoF, SoR, detail, recommendation, "F") 
        dbcon.execute("INSERT INTO PRESC_INTERACTION values (?,?,?,?,?,?,?,?,?,?,?,?,?)", params)

    for data in queryAlternative1:
        patientDb = patient
        drug =  str(data[0]).replace(f"{ontology}.", '').replace(f"{prescription}-", '')
        interaction1 = str(data[2]).replace(f"{ontology}.", '')
        interaction2 =  str(data[1]).replace(f"{ontology}.", '')
        interaction3 =  str(data[1]).replace(f"{ontology}.", '')
        interaction4 =  str(data[1]).replace(f"{ontology}.", '')
        QoF = str(data[3]).replace(f"{ontology}.", '')
        SoR =  str(data[4]).replace(f"{ontology}.", '')
        intDrugNum = str(data[5]).replace(f"{ontology}.", '')
        #intDrugCat =  str(data[6]).replace(f"{ontology}.", '')
        recommendation =  str(data[6]).replace(f"{ontology}.", '')
        detail =  str(data[7]).replace(f"{ontology}.", '')
        params = (patientDb, prescription, drug,intDrugNum, interaction1, interaction2, interaction3, interaction4, QoF, SoR, detail, recommendation, "T") 
        dbcon.execute("INSERT INTO PRESC_INTERACTION values (?,?,?,?,?,?,?,?,?,?,?,?,?)", params)
        
    for data in queryAlternative2:
        patientDb = patient
        drug =  str(data[0]).replace(f"{ontology}.", '').replace(f"{prescription}-", '')
        interaction4 = str(data[1]).replace(f"{ontology}.", '')
        interaction3 = str(data[1]).replace(f"{ontology}.", '')
        interaction2 =  str(data[2]).replace(f"{ontology}.", '')
        interaction1 =  str(data[3]).replace(f"{ontology}.", '')
        QoF = str(data[4]).replace(f"{ontology}.", '')
        SoR =  str(data[5]).replace(f"{ontology}.", '')
        intDrugNum = str(data[6]).replace(f"{ontology}.", '')
        #intDrugCat =  str(data[6]).replace(f"{ontology}.", '')
        recommendation =  str(data[7]).replace(f"{ontology}.", '')
        detail =  str(data[8]).replace(f"{ontology}.", '')
        params = (patientDb, prescription, drug,intDrugNum, interaction1, interaction2, interaction3, interaction4, QoF, SoR, detail, recommendation, "T") 
        dbcon.execute("INSERT INTO PRESC_INTERACTION values (?,?,?,?,?,?,?,?,?,?,?,?,?)", params)

    for data in queryAlternative3:
        patientDb = patient
        drug =  str(data[0]).replace(f"{ontology}.", '').replace(f"{prescription}-", '')
        interaction4 = str(data[1]).replace(f"{ontology}.", '')
        interaction3 = str(data[1]).replace(f"{ontology}.", '')
        interaction2 =  str(data[2]).replace(f"{ontology}.", '')
        interaction1 =  str(data[4]).replace(f"{ontology}.", '')
        QoF = str(data[5]).replace(f"{ontology}.", '')
        SoR =  str(data[6]).replace(f"{ontology}.", '')
        intDrugNum = str(data[7]).replace(f"{ontology}.", '')
        #intDrugCat =  str(data[6]).replace(f"{ontology}.", '')
        recommendation =  str(data[8]).replace(f"{ontology}.", '')
        detail =  str(data[9]).replace(f"{ontology}.", '')
        params = (patientDb, prescription, drug,intDrugNum, interaction1, interaction2, interaction3, interaction4, QoF, SoR, detail, recommendation, "T") 
        dbcon.execute("INSERT INTO PRESC_INTERACTION values (?,?,?,?,?,?,?,?,?,?,?,?,?)", params)

    for data in queryAlternative4:
        patientDb = patient
        drug =  str(data[0]).replace(f"{ontology}.", '').replace(f"{prescription}-", '')
        interaction4 = str(data[1]).replace(f"{ontology}.", '')
        interaction3 = str(data[1]).replace(f"{ontology}.", '')
        interaction2 =  str(data[2]).replace(f"{ontology}.", '')
        interaction1 =  str(data[3]).replace(f"{ontology}.", '')
        QoF = str(data[4]).replace(f"{ontology}.", '')
        SoR =  str(data[5]).replace(f"{ontology}.", '')
        intDrugNum = str(data[6]).replace(f"{ontology}.", '')
        #intDrugCat =  str(data[6]).replace(f"{ontology}.", '')
        recommendation =  str(data[7]).replace(f"{ontology}.", '')
        detail =  str(data[8]).replace(f"{ontology}.", '')
        params = (patientDb, prescription, drug,intDrugNum, interaction1, interaction2, interaction3, interaction4, QoF, SoR, detail, recommendation, "T") 
        dbcon.execute("INSERT INTO PRESC_INTERACTION values (?,?,?,?,?,?,?,?,?,?,?,?,?)", params)

    for data in queryAlternative5:
        patientDb = patient
        drug =  str(data[0]).replace(f"{ontology}.", '').replace(f"{prescription}-", '')
        interaction1 = str(data[2]).replace(f"{ontology}.", '')
        interaction2 =  str(data[1]).replace(f"{ontology}.", '')
        interaction3 =  str(data[1]).replace(f"{ontology}.", '')
        interaction4 =  str(data[1]).replace(f"{ontology}.", '')
        QoF = str(data[3]).replace(f"{ontology}.", '')
        SoR =  str(data[4]).replace(f"{ontology}.", '')
        intDrugNum = str(data[5]).replace(f"{ontology}.", '')
        #intDrugCat =  str(data[6]).replace(f"{ontology}.", '')
        recommendation =  str(data[6]).replace(f"{ontology}.", '')
        detail =  str(data[7]).replace(f"{ontology}.", '')
        params = (patientDb, prescription, drug,intDrugNum, interaction1, interaction2, interaction3, interaction4, QoF, SoR, detail, recommendation, "T") 
        dbcon.execute("INSERT INTO PRESC_INTERACTION values (?,?,?,?,?,?,?,?,?,?,?,?,?)", params)


def getAlternatives(patient,prescription, ontology, dbcon):
    response = list(default_world.sparql(f"""
            SELECT DISTINCT ?Drug ?Alternative 
            WHERE {{{ontology}:{prescription} {ontology}:hasDrug ?Drug . 
                ?Drug  {ontology}:hasAlternative ?Alternative }}"""))

    for data in response:
        drug =  str(data[0]).replace(f"{ontology}.", '').replace(f"{prescription}-", '') 
        alternative = str(data[1]).replace(f"{ontology}.", '') 
        params = (patient, prescription, drug,alternative) 
        dbcon.execute("INSERT INTO DRUG_ALTERNATIVE values (?,?,?,?)", params)


def getPrescriptionDrugs(patient, prescription, ontology, prescFile, dbcon):
        params = (patient, prescription) 
        dbcon.execute("INSERT INTO PRESCRIPTION_PROCESSED values (?,?)", params)


def getDrugDrugInteraction(patient, prescription, ontology, dbcon):
    response = list(default_world.sparql(f"""
        SELECT DISTINCT ?Drug ?DrugInt  
        WHERE {{{ontology}:{prescription} {ontology}:hasDrug ?Drug . 
              ?Drug {ontology}:hasInteractionWith ?DrugInt }} """))
    for data in response:
        drug1 =  str(data[0]).replace(f"{ontology}.", '').replace(f"{prescription}-", '') 
        drug2 =  str(data[1]).replace(f"{ontology}.", '').replace(f"{prescription}-", '') 
        params = (patient, prescription, drug1, drug2) 
        dbcon.execute("INSERT INTO DRUG_DRUG_INTERACTION values (?,?,?,?)", params)


def current_time():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    return(current_time)


def get_prescriptions(patient):
    df = pd.read_sql_query(f"""SELECT * 
                                    FROM PRESCRIPTION A
                                    WHERE CD_PATIENT = {patient}
                                    AND CD_PRESCRIPTION NOT IN (SELECT DISTINCT(CD_PRESCRIPTION) FROM PRESCRIPTION_PROCESSED WHERE CD_PATIENT = {patient})""", conn)
    return(df)

def get_patient(patient):
    df = pd.read_sql_query(f"SELECT * FROM PATIENT WHERE CD_PATIENT = {patient}", conn)
    return(df)

def get_exam(patient, day):
    df = pd.read_sql_query(f"SELECT * FROM PATIENT_EXAMS WHERE CD_PATIENT = {patient} and dt_Result = '{day}'", conn)
    return(df)

def get_previousDiseases(patient):
    df = pd.read_sql_query(f"SELECT * FROM PATIENT_PREVIOUS_DISEASES WHERE CD_PATIENT = {patient}", conn)
    return(df)

def getpatientProcessed(conn):
    df = pd.read_sql_query("SELECT DISTINCT CD_PATIENT from PRESCRIPTION_PROCESSED", conn)
    patients = df.values.tolist()
    patientlist = []
    for patientl1 in patients:
        for patientl2 in patientl1:
            patientlist.append(int(patientl2))
    return(patientlist)


def getNumDrugprocessed(conn):
    df = pd.read_sql_query("SELECT count( DISTINCT CD_PRESCRIPTION) from PRESCRIPTION_PROCESSED", conn)
    patients = df.values.tolist()
    return(patients)

def getNumDrugs(conn):
    df = pd.read_sql_query("SELECT count( DISTINCT CD_PRESCRIPTION) from PRESCRIPTION", conn)
    patients = df.values.tolist()
    return(patients)


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

##################MAIN APPLICATION##################

def checkInteraction(key):
    print(f'#########################Inference engine: Beers Criteria Interactions######################### \n')
    patient_prescriptions = get_prescriptions(key)
    if not patient_prescriptions.empty:
        startTime = datetime.now()
        totalRows = getNumDrugs(conn)
        print(f'Total prescription:{totalRows} / Prescription processed: {getNumDrugprocessed(conn)}')
        prescDays = listPrescrDays(patient_prescriptions)
        age = getPatientAge(key)
        gender = getPatientGender(key)
        for day in prescDays:
            print(f"Patient:{key} - Day:{day} Time: {time.ctime(time.time())} - Inserting patient data into the ontology")
            daystr = str(day).replace('/','').replace("-",'')
            #Add patient into the ontology
            patientData = get_patient(key)
            patient = addOntologyPatients(patientData)
        
            #Add exam into the ontology filter by patient and date
            examData = get_exam(key, day)
            addOntologyExam(examData,  age, gender)        
            
            #Add disease into the ontology filter by patient and date
            diseaseData = get_previousDiseases(key)
            addDisease(diseaseData,  age, gender)

            #Add prescription drugs into the ontology filter by patient and date
            dtFilterPrescriptions = patient_prescriptions.loc[patient_prescriptions.START_DATE == day, :]
            index = dtFilterPrescriptions.index.tolist()
            json_prescriptions = addPrescription(dtFilterPrescriptions,   age, gender)

            #Save a copy of the ontology with patient data
            ONTO.save(rf'inference_engines/ontology_files/{key}.owl', format = "rdfxml")
            addOntologyDrugAssertions(key, daystr, age, gender)
            composeName = str(key)+"-"+str(age)+"-"+gender            
            classObjDrugs = ONTO.search(iri = '*'+str(composeName)+'*', _case_sensitive = False)

            diff = datetime.now() - startTime
            days, seconds = diff.days, diff.seconds
            hours = days * 24 + seconds // 3600
            minutes = (seconds % 3600) // 60

            print(f"Patient:{key} - Day:{day}  Time: {time.ctime(time.time())}  - Sync reasoner pellet")
            AllDifferent(classObjDrugs)
            sync_reasoner_pellet(infer_property_values = True, infer_data_property_values = True)


            #ADD PRESCRIPTION
            print(f"Patient:{key} - Day:{day}  Time: {time.ctime(time.time())}  - SPARQL - Querying results and inserting into the CDSS DB ")
            presc_day = str(key)+"-"+str(age)+"-"+gender+"-"+str(daystr)
            result = getPrescriptionInteractions(key,presc_day, ONTOLOGY_NAME.replace('.', ''), c)
            result = getAlternatives(key, presc_day,ONTOLOGY_NAME.replace('.', ''), c)
            result = getPrescriptionDrugs(key,presc_day, ONTOLOGY_NAME.replace('.', ''),json_prescriptions, c)
            result = getDrugDrugInteraction(key,presc_day, ONTOLOGY_NAME.replace('.', ''), c)
                    
            print(f"Patient:{key} - Day:{day} Time: {time.ctime(time.time())} - Deleting patient data from the ontology \n")
            classObj = ONTO.search(iri = '*'+str(composeName)+'*', _case_sensitive = False)
            for individual in classObj:
                destroy_entity(individual)
        conn.commit()
                

        print(f'DrugNotRegistered: {DrugNotRegistered}')
        print(f'RouteNotRegistered: {RouteNotRegistered}')
        print(f'DiseaseNotRegistered: {DiseaseNotRegistered}')
        print(f'ExamNotRegistered: {ExamNotRegistered}')
        print(f'PacientNotRegisted: {PacientNotRegisted}')
    #print(f'Exceptions: {Exceptions}')
        print(current_time())
    #conn.close()
