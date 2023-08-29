from z3 import *
import re
s = Optimize()
s.set("timeout", 15000)
intervalIndex = 0
intervalIndexavg = 0
drugList = []
intervalList = []
intervalAvg = []

def createDrugInstances(drugName, interval, schedule, fixedtime, Tmax):
    try:
        global drugList
        if fixedtime == 'N' or (interval != len(schedule) and fixedtime == 'F'):
            drugInterval = (24/interval)*60
            interval = interval + 1 
            for x in range(1,interval):
                drugTmax = str(drugName+str(x)+'Tmax')
                drugList.append(drugTmax)
                globals()[f"{drugTmax}"] = Int(drugTmax)
                drugTmax = eval(drugTmax)
                drug = str(drugName+str(x))
                globals()[f"{drug}"] = Int(drug)
                drugList.append(drug)
                if x > 1:
                    prevDrug =  str(drugName+str(x-1))
                    s.add(eval(drug) - eval(prevDrug) == drugInterval)
                s.add(eval(drug) == (drugTmax - Tmax)%1440)
                s.add(eval(drug) <= 1440,eval(drug) >= 1)
                s.add(drugTmax <= 1440, drugTmax>= 1)
                s.add_soft(eval(drug) % 120 == 0)

        elif interval == len(schedule) and fixedtime == 'F':
            schedindex = 0
            interval = interval + 1 
            for x in range(1,interval):
                drugTmax = str(drugName+str(x)+'Tmax')
                drugList.append(drugTmax)
                globals()[f"{drugTmax}"] = Int(drugTmax)
                drugTmax = eval(drugTmax)
                drug = str(drugName+str(x))
                globals()[f"{drug}"] = Int(drug)
                drugList.append(drug)
                s.add(And(eval(drug) <= 1440, eval(drug) >= 1))
                s.add(drugTmax <= 1440, drugTmax>= 1)
                s.add(eval(drug) == (drugTmax - Tmax)%1440)
                s.add_soft(eval(drug) % 2 == 0)
                s.add(eval(drug) == (int(schedule[schedindex]))*60)
                schedindex += 1
    except Exception as e: print(drugName,drug, interval, schedule, fixedtime, Tmax)         

def definePatientPreference(drugName, list):
    interval = int(list[0]) + 1 
    for x in range(1,interval):
         drug = str(drugName+str(x))
         globals()[f"{drugName}"] = Int(drugName)
         s.add_soft(And(eval(drugName) == (list[x])*60))

def createInterval(name, freq):
    global intervalIndex
    intervalIndex += 1
    interval = str(name+str(intervalIndex))
    globals()[f"{interval}"] = Int(interval)
    interval = eval(interval)
    s.add_soft(interval >= 720/freq, 5)
    return(interval)


def createDrugRules(dicDrug, total_intervals):
        global intervalList
        global intervalIndexavg
        global intervalAvg
        drugs = list(dicDrug.keys())
        drug1Name = drugs[0]
        drug1Freq = dicDrug[drug1Name]
        drug2Name = drugs[1]
        drug2Freq = dicDrug[drug2Name]
        if drug2Freq> drug1Freq:freq = drug2Freq
        else: freq = drug1Freq
        for x in range(1, int(drug1Freq)+1):
            drug1 = eval(drug1Name+str(x)+'Tmax')
            for i in range(1, int(drug2Freq)+1):
                drug2 = eval(drug2Name+str(i)+'Tmax')
                interval = createInterval('interval', freq)
                intervalList.append(interval)
                s.add( If( (drug1 - drug2)%1440 <= 720, interval == (drug1 - drug2)%1440, interval == (drug2 - drug1)%1440))
                s.add(Distinct(drug1,drug2))

def schedulingDrugs(interactions, drugDetails, patientPref):
    global s
    global intervalIndex
    global drugList
    global intervalList
    s.set("timeout", 15000)
    drugDic = {}
    total_intervals = 0
    for drug, values in drugDetails.items():
            inner_lists, tmax =  values
            #for i in  inner_lists:  # iterate over each nested list in the value
            sum_of_first_values = sum(int(item[0]) for item in inner_lists)
            # Concatenate the second values of each nested set
            concatenated_second_values = " ".join(item[1] for item in inner_lists)
            last_element = inner_lists[0][2]
            # Create a new merged list with the sum of the first values and concatenated second values
            merged_list = [sum_of_first_values, concatenated_second_values, last_element]
            # iterate over each nested list in the value
            freq, schedule, fixedTime = merged_list
            schedule = schedule.rstrip().split()
            drug = drug.replace(',','')
            createDrugInstances(drug,int(freq),schedule,fixedTime,tmax)
            drugDic[drug] = freq
            total_intervals = int(freq)  +total_intervals

    total_intervals  = (24/total_intervals)*60
    
    if patientPref:
        for drug, values in patientPref.items():
            definePatientPreference(drug, values)
    
    
    for interaction in interactions:
        interacDic = {}
        for drug in interaction:
            drug = drug.replace(',','')
            interacDic[drug] = drugDic[drug]
        createDrugRules(interacDic, total_intervals)
    obj = Sum(intervalList)
    s.maximize(obj)
    checkSat = s.check()
    m = s.model()
    result = []
    if len(m)> 0:
        for drug in drugList:
            value = int(str(m[eval(drug)]))/60
            result.append(drug)
            result.append(round(value))
    s = Optimize()
    if len(m) == 0:
        result = 'null'
    intervalIndex = 0
    drugList = []
    intervalList = []
    return(str(checkSat), str(result))
