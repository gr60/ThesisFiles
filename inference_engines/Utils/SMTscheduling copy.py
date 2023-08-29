#ass 2x per day
#ibu 2x per day

from z3 import *


s = Optimize()
intervalIndex = 0
avgintIndex = 0
drugIntervals = []
optmzList = ''
drugList = []



def createDrugInstances(drug, interval, schedule, fixedtime, freqRange):
    global drugList
    if fixedtime == 'N':
        drugInterval = 24/interval
        interval = interval + freqRange
        for x in range(freqRange,interval):
            DNameMax = str(drug+str(x))
            drugList.append(DNameMax)
            globals()[f"{DNameMax}"] = Real(DNameMax)
            DNameMax = eval(DNameMax)
            s.add(And(DNameMax <= 24, DNameMax >= 1))
            if x == 1:
                DNameMaxD2 = str(drug+str(x)+'D2')
                globals()[f"{DNameMaxD2}"] = Real(DNameMaxD2)
                DNameMaxD2 = eval(DNameMaxD2)
                s.add(And(DNameMaxD2 <= 48, DNameMaxD2 >= 25))
                s.add(DNameMaxD2 - DNameMax == 24)
            elif x > 1:
                prevDNameMax =  str(drug+str(x-1))
                s.add(DNameMax - eval(prevDNameMax) == drugInterval)
    if fixedtime == 'F':
        interval = interval + freqRange
        for x in range(freqRange,interval):
            DNameMax = str(drug+str(x))
            drugList.append(DNameMax)
            globals()[f"{DNameMax}"] = Real(DNameMax)
            DNameMax = eval(DNameMax)
            s.add(And(DNameMax <= 24, DNameMax >= 1))
            s.add_soft(And(DNameMax == int(schedule[x])))
            if x == 1:
                DNameMaxD2 = str(drug+str(x)+'D2')
                globals()[f"{DNameMaxD2}"] = Real(DNameMaxD2)
                DNameMaxD2 = eval(DNameMaxD2)
                s.add(And(DNameMaxD2 <= 48, DNameMaxD2 >= 25))
                s.add(DNameMaxD2 - DNameMax == 24)
            if x > 1:
                scheduleInternval = int(schedule[x]) - int(schedule[x-1])
                prevDNameMax =  str(drug+str(x-1))
                s.add(DNameMax - eval(prevDNameMax) == scheduleInternval)



def createInterval(name, number):
    interval = str(name+str(number))
    globals()[f"{interval}"] = Real(interval)
    interval = eval(interval)
    return(interval)


def createDrugRules(dicDrug):
    global intervalIndex
    global drugIntervals
    global avgintIndex
    global optmzList

    
    drugs = list(dicDrug.keys())
    drug1Name = drugs[0]
    drug1Freq = dicDrug[drug1Name]

    drug2Name = drugs[1]
    drug2Freq = dicDrug[drug2Name]

    if drug1Freq ==1 and drug2Freq == 1:
        oldintervalIndex = intervalIndex
        intervalList = ''
        avgintIndex += 1
        intervalIndex += 1
        avgint = createInterval('avgint',avgintIndex )
        optmzList = str(f"{optmzList} + 'avgint'{str(avgintIndex)}")

        interval = createInterval('interval',intervalIndex )
        intervalList = str(f"{intervalList} + 'interval'{str(intervalIndex)}")
        drug1NameSol = eval(drug1Name+'1')
        drug2NameSol = eval(drug2Name+'1')
        s.add_soft( If( drug1NameSol > drug2NameSol, interval == (drug1NameSol - drug2NameSol), interval == (drug2NameSol - drug1NameSol)))
        s.add_soft(drug1NameSol != drug2NameSol, 2)
 
        drug1NameD2 = str(drug1Name+'1'+'D2')
        drug2NameD2 =str(drug2Name+'1'+'D2')
        drug1NameD2Sol = eval(drug1NameD2)
        drug2NameD2Sol = eval(drug2NameD2)
        
        intervalIndex += 1
        interval = createInterval('interval',intervalIndex )
        intervalList = str(f"{intervalList} + 'interval'{str(intervalIndex)}")
        s.add_soft(interval == drug2NameD2Sol - drug1NameSol, 2)

        intervalIndex += 1
        interval = createInterval('interval',intervalIndex )
        intervalList = str(f"{intervalList} + 'interval'{str(intervalIndex)}")
        s.add_soft(interval == drug1NameD2Sol - drug2NameSol, 2)
        s.add_soft(drug2NameD2Sol != drug1NameD2Sol, 2)
        
        intervalList = intervalList.replace("'", '').replace('"', '')
        
        s.add_soft(avgint == (eval(intervalList.replace("'", '').replace('"', '')))/3)
        for i in range(oldintervalIndex +1,intervalIndex+1):
            s.add_soft(avgint == eval('interval'+ str(i)))
       
    
    if (drug1Freq ==1 and drug2Freq > 1) or (drug1Freq >1 and drug2Freq == 1):
        intercount = 0
        if drug1Freq > 1:
            temp = drug1Freq
            drug1Freq = drug2Freq
            drug2Freq = drug1Freq
            temp = drug1Name
            drug1Name = drug2Name
            drug2Name = temp
        oldintervalIndex = intervalIndex
        intervalList = ''
        avgintIndex += 1
        intervalIndex += 1
        avgint = createInterval('avgint',avgintIndex )
        optmzList = str(f"{optmzList} + 'avgint'{str(avgintIndex)}")
        drug1NameSol = eval(drug1Name+'1')
        for i in range(1, drug2Freq+1):
            interval = createInterval('interval',intervalIndex )
            intervalList = str(f"{intervalList} + 'interval'{str(intervalIndex)}")
            intercount += 1
            drug2NameSol = eval(drug2Name+str(i))
            s.add_soft( If( drug1NameSol > drug2NameSol, interval == (drug1NameSol - drug2NameSol), interval == (drug2NameSol - drug1NameSol)))
            s.add_soft(drug1NameSol != drug2NameSol, 2)
 
        drug1NameD2 = str(drug1Name+'1'+'D2')
        drug2NameD2 =str(drug2Name+'1'+'D2')
        drug1NameD2Sol = eval(drug1NameD2)
        drug2NameD2Sol = eval(drug2NameD2)
        
        intervalIndex += 1
        interval = createInterval('interval',intervalIndex )
        intervalList = str(f"{intervalList} + 'interval'{str(intervalIndex)}")
        intercount += 1
        s.add_soft(interval == drug2NameD2Sol - drug1NameSol, 2)

        intervalIndex += 1
        interval = createInterval('interval',intervalIndex )
        intervalList = str(f"{intervalList} + 'interval'{str(intervalIndex)}")
        intercount += 1
        s.add_soft(interval == drug1NameD2Sol - drug2NameSol, 2)
        s.add_soft(drug2NameD2Sol != drug1NameD2Sol, 2)
        
        intervalList = intervalList.replace("'", '').replace('"', '')
        
        s.add_soft(avgint == (eval(intervalList.replace("'", '').replace('"', '')))/intercount)
        for i in range(oldintervalIndex +1,intervalIndex+1):
            s.add_soft(avgint == eval('interval'+ str(i)))
        
    if drug1Freq >1 and drug2Freq > 1:
        intercount = 0 
        oldintervalIndex = intervalIndex
        intervalList = ''
        avgintIndex += 1
        
        avgint = createInterval('avgint',avgintIndex )
        optmzList = str(f"{optmzList} + 'avgint'{str(avgintIndex)}")
        for x in range(1, drug1Freq+1):
            drug1NameSol = eval(drug1Name+str(x))
            for i in range(1, drug2Freq+1):
                intervalIndex += 1
                interval = createInterval('interval',intervalIndex )
                intervalList = str(f"{intervalList} + 'interval'{str(intervalIndex)}")
                intercount += 1
                drug2NameSol = eval(drug2Name+str(i))
                s.add_soft( If( drug1NameSol > drug2NameSol, interval == (drug1NameSol - drug2NameSol), interval == (drug2NameSol - drug1NameSol)))
                s.add_soft(drug1NameSol != drug2NameSol, 2)
 
        drug1NameD2 = str(drug1Name+'1'+'D2')
        drug2NameD2 =str(drug2Name+'1'+'D2')
        drug1NameD2Sol = eval(drug1NameD2)
        drug2NameD2Sol = eval(drug2NameD2)
        
        intervalIndex += 1
        interval = createInterval('interval',intervalIndex )
        intervalList = str(f"{intervalList} + 'interval'{str(intervalIndex)}")
        intercount += 1
        s.add_soft(interval == drug2NameD2Sol - drug1NameSol, 2)

        intervalIndex += 1
        interval = createInterval('interval',intervalIndex )
        intervalList = str(f"{intervalList} + 'interval'{str(intervalIndex)}")
        intercount += 1
        s.add_soft(interval == drug1NameD2Sol - drug2NameSol, 2)
        s.add_soft(drug2NameD2Sol != drug1NameD2Sol, 2)
        
        intervalList = intervalList.replace("'", '').replace('"', '')
        
        s.add_soft(avgint == (eval(intervalList.replace("'", '').replace('"', '')))/intercount)
        for i in range(oldintervalIndex +1,intervalIndex+1):
            s.add_soft(avgint == eval('interval'+ str(i)))



def schedulingDrugs(interactions, drugDetails):
    print(interactions)
    print(drugDetails)
    global s
    global intervalIndex
    global avgintIndex
    global drugIntervals
    global optmzList
    global drugList
    drugDic = {}
    s.push()
    for drug in drugDetails.keys():
        index = len(drugDetails[drug])
        prevfreq = 0
        for i in range(index):
            freq = int(float(drugDetails[drug][i-1][0]))
            if len(drugDetails[drug][i-1][1]) > 2:
                schedule = drugDetails[drug][i-1][1].rstrip()
                schedule = schedule.split()
            else:
                schedule = drugDetails[drug][i-1][1]
            fixedTime = drugDetails[drug][i-1][2]
            if drug in drugDic:
                createDrugInstances(drug,freq,schedule,fixedTime, drugDic[drug]+1)
                drugDic[drug] = freq + drugDic[drug]
                
            else:
                drugDic[drug] = freq
                createDrugInstances(drug,freq,schedule,fixedTime, 1)

           

    for interaction in interactions:
        dList = {}
        for drug in interaction:
            dList[drug] = drugDic[drug]
        createDrugRules(dList)
    s.maximize(eval((optmzList).replace("'", '').replace('"', '')))
    print(s.sexpr())
    print (s.check())
    m = s.model()
    result = []
    print (drugList)
    for drug in drugList:
        print (f"{drug} = {m[ eval(drug)]}")
        result.append(drug)
        result.append(m[ eval(drug)])
    s = Optimize()
    intervalIndex = 0
    avgintIndex = 0
    drugIntervals = []
    optmzList = ''
    drugList = []
    s.pop()
    return(str(result))
    




