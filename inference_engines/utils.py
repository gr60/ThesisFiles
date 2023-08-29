def getInteractionList(data):
    interactionList = []
    prescription = {}
    drugs = []
    result = []
    dicInt={}
    for dtPrescription in data:
        drugs=[]
        for occurence in data[dtPrescription]:
            drug = occurence['Name']
            for interaction in occurence['Interaction']:
                if dtPrescription not in dicInt:
                    dicInt[dtPrescription]={}
                if interaction not in dicInt[dtPrescription]:
                    dicInt[dtPrescription][interaction]={}
                for group in occurence['Interaction'][interaction]['Role']:
                    if group not in dicInt[dtPrescription][interaction]:
                        dicInt[dtPrescription][interaction][group]={}
                        dicInt[dtPrescription][interaction][group]['Drugs']= set()
                    dicInt[dtPrescription][interaction][group]['Drugs'].add(str(drug).replace('/', '_').replace('.', '').replace('(', '').replace(')', '').replace(',', ''))
                dicInt[dtPrescription][interaction]['NumDrugs']= occurence['Interaction'][interaction]['NumDrugs']

            for alternative in occurence['Alternatives']:
                for interaction in alternative['Interaction']:
                    if dtPrescription not in dicInt:
                        dicInt[dtPrescription]={}
                    if interaction not in dicInt[dtPrescription]:
                        dicInt[dtPrescription][interaction]={}
                    for group in alternative['Interaction'][interaction]['Role']:
                        if group not in dicInt[dtPrescription][interaction]:
                            dicInt[dtPrescription][interaction][group]={}
                            dicInt[dtPrescription][interaction][group]['Drugs']= set()
                        dicInt[dtPrescription][interaction][group]['Drugs'].add(alternative['Alternative'])
                    dicInt[dtPrescription][interaction]['NumDrugs']= alternative['Interaction'][interaction]['NumDrugs']

    interactionDic = {}

    for date in dicInt:
        interactionDic[date]= []
        for interaction in dicInt[date]:
    #Add interaction without drug group
            if dicInt[date][interaction]['NumDrugs'] == 0:
                listDrug = []
                for group in dicInt[date][interaction]:
                    if group != 'NumDrugs':
                        for drug in dicInt[date][interaction][group]['Drugs']:
                            listDrug.append([str(drug).replace('/', '_').replace('.', ''), str(drug).replace('/', '_').replace('.', '').replace('(', '').replace(')', '').replace(',', '')])
                    if listDrug not in interactionDic[date]:
                            interactionDic[date].append(listDrug)

    #Add interaction 1 drug group
            if dicInt[date][interaction]['NumDrugs'] == 1:
                listDrug = []
                for group in dicInt[date][interaction]:
                    if group != 'NumDrugs':
                        for drug in dicInt[date][interaction][group]['Drugs']:
                            listDrug.append(drug)
                    if listDrug not in interactionDic[date]:
                        interactionDic[date].append([listDrug])
    #Add interaction 2 or more drugs
            if dicInt[date][interaction]['NumDrugs'] == 2:
                listDrug = []
                listgroup1 = []
                listgroup2 = []
                listTemp = []
                groupTemp = ''
                i = 0
                for group in dicInt[date][interaction]:
                    if group != 'NumDrugs':
                        if  groupTemp != group:
                            i += 1
                        for drug in dicInt[date][interaction][group]['Drugs']:
                            if i == 1:
                                listgroup1.append(str(drug).replace('/', '_').replace('.', '').replace('(', '').replace(')', '').replace(',', ''))
                            elif i ==2:
                                listgroup2.append(str(drug).replace('/', '_').replace('.', '').replace('(', '').replace(')', '').replace(',', ''))
                        if listgroup1 and listgroup2:
                            for list1interac in listgroup1:
                                for list2interac in listgroup2:
                                    listTemp = [list1interac, list2interac]
                                    if listTemp not in interactionDic[date]:
                                        interactionDic[date].append([listTemp])
    return(interactionDic)


def getInteractions(drug, dic):
    result = []
    for druglist in dic:
        if isinstance(druglist[0], str):
            if drug in druglist and druglist not in result:
                result.append(druglist)
        elif isinstance(druglist[0], list):
            tempList = []
            for drugs in druglist:
                for d in drugs:
                    tempList.append(d)
            if drug in tempList and tempList not in result:
                result.append(tempList)
    return(result)


def getPrescrDrugsList(data):
    prescription = {}
    for dtPrescription in data:
        if dtPrescription not in prescription:
            prescription[dtPrescription]= []
        for occurence in data[dtPrescription]:
            if occurence not in prescription[dtPrescription]:
                prescription[dtPrescription].append(str(occurence['Name']).replace('/', '_').replace('.', '').replace('(', '').replace(')', '').replace(',', ''))
    return(prescription)

def getPrescrAlternativeList(data):
    alternatives = {}
    for dtPrescription in data:
        if dtPrescription not in alternatives:
            alternatives[dtPrescription]= []
        for occurence in data[dtPrescription]:
            altList = []
            altList.append(str(occurence['Name']).replace('/', '_').replace('.', '').replace('(', '').replace(')', '').replace(',', ''))
            for alternative in occurence['Alternatives']:
                if alternative['Alternative']:
                    altList.append(str(alternative['Alternative']).replace('/', '_').replace('.', '').replace('(', '').replace(')', '').replace(',', ''))
            if len(altList) > 1:
                alternatives[dtPrescription].append(altList )
    return(alternatives)
