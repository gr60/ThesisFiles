import pandas as pd
from owlready2 import *
import json , csv
import pandas as pd
from datetime import datetime

version = '19'

ONTOLOGY = f"BeersOntologyV{version}.owl"
ONTOLOGY_NAME = f"BeersOntologyV{version}."
FILENAME = f"BeersOntologyV{version}"
ONTO = get_ontology(fr'OntologyIntegration/OntologiesFiles/BeersOntologyV{version}.owl').load()


def sortValues(path, Sheet):

    df = pd.read_excel(path, Sheet)
    df = pd.concat(df, axis=0, ignore_index=True)

    print(df)


    df.sort_values(by = ['NR_TREATMENT_INSTANCE','DT_START','DS_DRUG_ORIGINAL'])

    df1 = pd.DataFrame(df[0:1000000])
    df2 = pd.DataFrame(df[1000000:2000000])

    #df.to_excel(r'OntologyIntegration/ResultXlsFiles/Prescriptions.xlsx', index = False)

    writer = pd.ExcelWriter(r'PatientData/Import/PrescriptionsSort.xlsx', engine='xlsxwriter')

    df1.to_excel(writer, sheet_name='Sheet1')
    df2.to_excel(writer, sheet_name='Sheet2')

    writer.save()


def checkLabel(name, type): #check if exist the label drug on the onotlogy and return the class name
    classObj = ONTO.search(label = (name), _case_sensitive = False)
    if classObj:
        classObj = str(classObj[0]).replace(ONTOLOGY_NAME,'')
        if isinstance(ONTO[classObj], ONTO[type]):
            return classObj
    else:
        return(None)


def checkDrugsOntology():
    df = pd.read_excel(r'PatientData/Import/PrescricoesNew.xlsx', ['Sheet1', 'Sheet2'])
    df = pd.concat(df, axis=0, ignore_index=True)

    uniqueValues = df['DS_DRUG'].unique()
    listDrugOk= []
    listDrugErro= []
    for value in uniqueValues:
        value = ''.join(str(value).rstrip().lstrip()).replace(" ", "_") 
        if checkLabel(value, 'Drugs'):
            listDrugOk.append(value)
        else:
            listDrugErro.append(value)
            print(listDrugErro)
    print(listDrugErro)


def checkDrugsOntologyII():
    df = pd.read_excel(r'PatientData/Import/PrescriptionsSort.xlsx', ['Sheet1', 'Sheet2'])
    df = pd.concat(df, axis=0, ignore_index=True)

    dsDrug = df['DS_DRUG'].unique()
    dsDrug1 = df['DS_COM_DRUG0'].unique()
    dsDrug2 = df['DS_COM_DRUG1'].unique()
    dsDrug3 = df['DS_COM_DRUG2'].unique()
    dsDrug4 = df['DS_COM_DRUG3'].unique()
    listDrugOk= []
    listDrugErro= []
    for value in dsDrug:
        value = ''.join(str(value).rstrip().lstrip()).replace(" ", "_") 
        if checkLabel(value, 'Drugs'):
            listDrugOk.append(value)
        else:
            listDrugErro.append(value)
    print(listDrugErro)
    for value in dsDrug1:
        value = ''.join(str(value).rstrip().lstrip()).replace(" ", "_") 
        if checkLabel(value, 'Drugs'):
            listDrugOk.append(value)
        else:
            listDrugErro.append(value)
    print(listDrugErro)
    for value in dsDrug2:
        value = ''.join(str(value).rstrip().lstrip()).replace(" ", "_") 
        if checkLabel(value, 'Drugs'):
            listDrugOk.append(value)
        else:
            listDrugErro.append(value)
    print(listDrugErro)
    for value in dsDrug3:
        value = ''.join(str(value).rstrip().lstrip()).replace(" ", "_") 
        if checkLabel(value, 'Drugs'):
            listDrugOk.append(value)
        else:
            listDrugErro.append(value)
    print(listDrugErro)
    for value in dsDrug4:
        value = ''.join(str(value).rstrip().lstrip()).replace(" ", "_") 
        if checkLabel(value, 'Drugs'):
            listDrugOk.append(value)
        else:
            listDrugErro.append(value)
    print(listDrugErro)


def checkRouteOntology():
    df = pd.read_excel(r'PatientData/Import/PrescriptionsSort.xlsx', ['Sheet1', 'Sheet2'])
    df = pd.concat(df, axis=0, ignore_index=True)

    uniqueValues = df['ROUTE'].unique()
    listDrugOk= []
    listDrugErro= []
    for value in uniqueValues:
        value = ''.join(str(value).rstrip().lstrip()).replace(" ", "_") 
        if checkLabel(value, 'AdministrationRoute'):
            listDrugOk.append(value)
        else:
            listDrugErro.append(value)
            print(listDrugErro)
    print(listDrugErro)





def setDrugLenght(path, Sheet):

    df = pd.read_excel(path, Sheet)
    df = pd.concat(df, axis=0, ignore_index=True)

    df.sort_values(by = ['NR_TREATMENT_INSTANCE','DS_DRUG','DT_START'], inplace=True)
    
    df.reset_index(drop=True, inplace=True)
    
    index = df.index.tolist()
    prevDate = df["DT_START"][0]
    prevValue =  df["NR_TREATMENT_INSTANCE"][0]
    dtValue = 0
    prevDrug = df["DS_DRUG"][0]
    df['DrugLenght'] = 0

    for i in index:
        days = (pd.to_datetime(prevDate, format='%d/%m/%y') - pd.to_datetime(df["DT_START"][i], format='%d/%m/%y')).days
        currentEncounter =  df["NR_TREATMENT_INSTANCE"][i]
        currentDrug = str(df["DS_DRUG"][i])
        if currentEncounter ==  prevValue and (days == 1 or days == -1)  and (currentDrug ==prevDrug) :
            dtValue += 1
            df["DrugLenght"][i] = dtValue
        else:
            dtValue = 0
        prevDate = df["DT_START"][i]
        prevDrug = str(df["DS_DRUG"][i])
        prevValue =  df["NR_TREATMENT_INSTANCE"][i]

    df1 = pd.DataFrame(df[0:1000000])
    df2 = pd.DataFrame(df[1000000:2000000])

    writer = pd.ExcelWriter(r'PatientData/Import/PrescricoesNew.xlsx', engine='xlsxwriter')

    df1.to_excel(writer, sheet_name='Sheet1')
    df2.to_excel(writer, sheet_name='Sheet2')

    writer.save()



def setTreatmentLenght(path, Sheet):

    df = pd.read_excel(path, Sheet)
    df = pd.concat(df, axis=0, ignore_index=True)
    df.sort_values(by = ['NR_TREATMENT_INSTANCE','DT_START'], inplace=True)
    df.reset_index(drop=True, inplace=True)
    index = df.index.tolist()
    prevValue =  df["NR_TREATMENT_INSTANCE"][0]
    dtStart = None
    df['TreatmentLenght'] = 0
    listIndex = []
    for i in index:
        currentEncounter =  df["NR_TREATMENT_INSTANCE"][i]
        if prevValue == currentEncounter:
            listIndex.append(i)
            if dtStart == None:
                dtStart = df["DT_START"][i]
            prevValue = currentEncounter
            dtEnd = df["DT_START"][i]
            days = (pd.to_datetime(dtEnd, format='%d/%m/%y') - pd.to_datetime(dtStart, format='%d/%m/%y')).days
            df["TreatmentLenght"][i] = days
        else:
            listIndex = []
            listIndex.append(i)
            dtStart = df["DT_START"][i]
            prevValue = currentEncounter

    df1 = pd.DataFrame(df[0:1000000])
    df2 = pd.DataFrame(df[1000000:2000000])

    writer = pd.ExcelWriter(r'OntologyIntegration/ResultXlsFiles/PrescriptionsTreatLenght.xlsx', engine='xlsxwriter')

    df1.to_excel(writer, sheet_name='Sheet1')
    df2.to_excel(writer, sheet_name='Sheet2')

    writer.save()


#setDrugLenght(r'PatientData/Import/Prescricoes.xlsx', ['Dados1', 'Dados2', 'Dados3'])
#setTreatmentLenght(r'PatientData/Import/PrescricoesNew.xlsx', ['Sheet1', 'Sheet2'])
sortValues(r'PatientData/Import/PrescriptionsSort2.xlsx', ['Sheet1', 'Sheet2'])

#checkDrugsOntologyII()
#checkRouteOntology()