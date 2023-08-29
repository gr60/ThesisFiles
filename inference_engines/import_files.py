import pandas 
import  tkinter as tk
from tkinter import filedialog




def importFile(fileName, sheetName):
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()
    print(file_path)

    df = pandas.read_excel(fileName, sheet_name=sheetName)
    return(df)
    
def listOccurence(fileName):
    patient_df = fileName
    patientList = []
    for patientID in patient_df["NR_ATENDIMENTO"]:
        patientList.append(patientID)
    return(patientList)


def listPrescrDays(fileName):
    prescription_df = fileName
    prescriptionDic = []
    index = prescription_df.index.tolist()
    for i in index:
        prescDay = str(prescription_df["START_DATE"][i])
        if prescDay not in prescriptionDic:
            prescriptionDic.append(prescDay)
    return(prescriptionDic)



def listPatients(fileName, register):
    patient_df = fileName
    if register != None:
        patient_df = patient_df.loc[patient_df.NR_ATENDIMENTO == register, :]
    patientDic = {}
    patientDic['Patient'] = {}
    i = patient_df["NR_ATENDIMENTO"].index[0]
    for patientID in patient_df["NR_ATENDIMENTO"]:
        patientDic['Patient'][patientID] = []
        patientDic['Patient'][patientID].append({
            'CD_PATIENT': patient_df["CD_PESSOA_FISICA"][i],
            'AGE': patient_df["AGE"][i], 
            'GENDER': patient_df["GENDER"][i],
            'CLINIC': patient_df["CLINIC"][i],
            'DT_DISCHARGE': patient_df["DT_ALTA"][i].to_pydatetime().date(),
            'DT_HOSPITALIZATION': patient_df["DT_ENTRADA"][i].to_pydatetime().date(),
            'CD_DISCHARGE_REASON': patient_df["MOTIVO_ALTA"][i],
            'CD_PROCEDURE': patient_df["CD_PROCEDIMENTO"][i],
            'DS_PROCEDURE': ''.join(str(patient_df["DS_PROCEDIMENTO"][i]).rstrip().lstrip()).replace(" ", "_") , 
            'CD_CID': patient_df["CD_CID_PRIMARIO"][i],
        })
        i += 1
    return(patientDic)



def listPrescriptions(fileName, register ):
    prescription_df = fileName
    prescriptionDic = {} 
    prescriptionDic['Prescription'] = {}
    prescrName = str(register)
    prescriptionDic['Prescription'][prescrName] = []
    index = prescription_df.index.tolist()
    for i in index:
        prescriptionDic['Prescription'][prescrName].append({
                         'NR_TREATMENT_INSTANCE': int(prescription_df["NR_ATENDIMENTO"][i]),
                         'TYPE_DRUG': prescription_df["TYPE_DRUG"][i],
                         'DS_DRUG_ORIGINAL': ''.join(str(prescription_df["DS_DRUG_ORIGINAL"][i]).rstrip().lstrip()).replace(" ", "_") , 
                         'DS_DRUG': ''.join(str(prescription_df["DS_DRUG"][i]).rstrip().lstrip()).replace(" ", "_") , 
                         'DS_COM_DRUG0': ''.join(str(prescription_df["DS_COM_DRUG1"][i]).rstrip().lstrip()).replace(" ", "_") , 
                         'DS_COM_DRUG1': ''.join(str(prescription_df["DS_COM_DRUG2"][i]).rstrip().lstrip()).replace(" ", "_") , 
                         'DS_COM_DRUG2': ''.join(str(prescription_df["DS_COM_DRUG3"][i]).rstrip().lstrip()).replace(" ", "_") , 
                         'DS_COM_DRUG3': ''.join(str(prescription_df["DS_COM_DRUG4"][i]).rstrip().lstrip()).replace(" ", "_") , 
                         'ROUTE': ''.join(str(prescription_df["DS_VIA_APLICACAO"][i]).rstrip().lstrip()).replace(" ", "_") , 
                         'DOSE': (prescription_df["DOSE"][i]),
                         'DOSE_COM0': (prescription_df["DOSE_COM1"][i]),
                         'DOSE_COM1': (prescription_df["DOSE_COM2"][i]),
                         'DOSE_COM2': (prescription_df["DOSE_COM3"][i]),
                         'DOSE_COM3': (prescription_df["DOSE_COM4"][i]),
                         'SCHEDULE': prescription_df["DS_HORARIOS"][i],
                         'FREQUENCY': prescription_df["FREQUENCIA"][i],
                         'DURATION': prescription_df["DURATION"][i],
                         'DT_START': str(prescription_df["DT_INICIO_PRESCR"][i].to_pydatetime().date()) ,
                         'DT_END': str(prescription_df["DT_VALIDADE_PRESCR"][i].to_pydatetime().date()),
                         'CRITICAL_PATIENT': prescription_df["CRITICAL_PATIENT"][i],
                         'FIRST_LINE': prescription_df["FIRST_LINE"][i],
                         'RELEASE': prescription_df["RELEASE"][i],
                         })
    return(prescriptionDic)


def listExams(fileName, register):
    exam_df = fileName
    #if register != None:
    #    exam_df = exam_df.loc[exam_df.NR_ATENDIMENTO == register, :]
    examDic = {}
    examDic['Exam'] = {}
    prescrName = str(register)
    examDic['Exam'][prescrName] = []
    index = exam_df.index.tolist()
    for i in index:          
        examDic['Exam'][prescrName].append({

                         'NR_ATEND': int(exam_df["NR_ATENDIMENTO"][i]),
                         'NR_SEQ_RESULT': int(exam_df["NR_SEQ_RESULTADO"][i]),
                         'NM_EXAME': ''.join(str(exam_df["NM_EXAME"][i]).rstrip().lstrip()).replace(" ", "_") , 
                         'QT_RESULTADO': float(str(exam_df["QT_RESULTADO"][i]).replace(",", ".")) , 
                         'DT_RESULTADO': str(exam_df["DT_RESULTADO"][i].to_pydatetime().date())
                         })
    return(examDic)


def listPreviousDisease(fileName, register):
    disease_df = fileName.sort_values(by ="NR_ATENDIMENTO", ascending=False)
    #if register != None:
    #    disease_df = disease_df.loc[disease_df.NR_ATENDIMENTO == register, :]
    diseaseDic = {}
    diseaseDic['Disease'] = {}
    prescrName = str(register)
    diseaseDic['Disease'][prescrName] = []
    index = disease_df.index.tolist()
    for i in index:
        diseaseDic['Disease'][prescrName].append({
                         'NR_ATEND': int(disease_df["NR_ATENDIMENTO"][i]),
                         'NM_DISEASE': ''.join(str(disease_df["DOENCA"][i]).rstrip().lstrip()).replace(" ", "_") 
                         })
    return(diseaseDic)




