from owlready2 import *
import json , csv
import pandas as pd

version = '16'

ONTOLOGY = f"BeersOntologyV{version}.owl"
ONTOLOGY_NAME = f"BeersOntologyV{version}."
FILENAME = f"BeersOntologyV{version}"
ONTO = get_ontology(fr'OntologyIntegration/OntologiesFiles/BeersOntologyV{version}.owl').load()

FULLPROCESS = False


def listClass(className):
    global FILENAME
    name = list(ONTO[className].descendants())
    dfs = []
    for className in name:
       className = str(className).replace(ONTOLOGY_NAME,'')
       individual_name = className.replace('(', '_').replace(')', '_').replace('%', '')
       dfs.append(individual_name) # append the data frame to the list
    df = pd.DataFrame(dfs)
    df.to_excel(fr'OntologyIntegration/ResultXlsFiles/Class{FILENAME}.xlsx', index = False)


def listLable(className):
    global FILENAME
    name = list(ONTO[className].descendants())
    dfs = []
    for className in name:
       lablePt = className.label.en
       className = str(className).replace(ONTOLOGY_NAME,'')
       individual_name = className.replace('(', '_').replace(')', '_').replace('%', '')
       if lablePt:
            for pt in lablePt:
                dfs.append([individual_name, pt])
    df = pd.DataFrame(dfs)
    df.to_excel(fr'OntologyIntegration/ResultXlsFiles/En{className}Lable{FILENAME}.xlsx', index = False)


def removeLabel(className):
    name = list(ONTO[className].descendants())
    for c in name:
        c = str(c).replace(ONTOLOGY_NAME,'') 
        classObj = ONTO.search(label = (c), _case_sensitive = False)
        if classObj:
            classObj = str(classObj[0]).replace(ONTOLOGY_NAME,'')
            ONTO[classObj].label.remove(classObj)

def createIndividuals(className, prefix):
    name = list(ONTO[className].descendants())
    for className in name:
       className = str(className).replace(ONTOLOGY_NAME,'')
       individual_name = className.replace('(', '_').replace(')', '_').replace('%', '')
       print(className + ' - ' + individual_name)
       individual = ONTO[className](prefix+str(individual_name))

def createDrugIndividuals(className, prefix):
    name = list(ONTO[className].descendants())
    for d1 in name:
        teste = isinstance(d1, ONTO["Drugs"])
        if isinstance(d1, ONTO["Drugs"]):
            d1 = str(d1).replace(ONTOLOGY_NAME,'')
            individual_name = d1.replace('(', '_').replace(')', '_').replace('%', '')
            individual = ONTO[d1](prefix+str(individual_name))
            individual.isAlternative.append(True)
        else:
            d1 = list(d1.descendants())
            for d2 in d1:
                if isinstance(d2, ONTO["Drugs"]):
                    d2 = str(d2).replace(ONTOLOGY_NAME,'')
                    individual_name = d2.replace('(', '_').replace(')', '_').replace('%', '')
                    individual = ONTO[d2](prefix+str(individual_name))
                    individual.isAlternative.append(True)
                else:
                    d2 = list(d2.descendants())
                    for d3 in d2:
                        if isinstance(d3, ONTO["Drugs"]):
                            d3 = str(d3).replace(ONTOLOGY_NAME,'')
                            individual_name = d3.replace('(', '_').replace(')', '_').replace('%', '')
                            individual = ONTO[d3](prefix+str(individual_name))
                            individual.isAlternative.append(True)
                        else:
                            d3 = list(d3.descendants())
                            for d4 in d3:
                                if isinstance(d4, ONTO["Drugs"]):
                                    d4 = str(d4).replace(ONTOLOGY_NAME,'')
                                    individual_name = d4.replace('(', '_').replace(')', '_').replace('%', '')
                                    individual = ONTO[d4](prefix+str(individual_name))
                                    individual.isAlternative.append(True)
                                else:
                                    d4 = list(d4.descendants())
                                    for d5 in d4:
                                        if isinstance(d5, ONTO["Drugs"]):
                                            d5 = str(d5).replace(ONTOLOGY_NAME,'')
                                            individual_name = d5.replace('(', '_').replace(')', '_').replace('%', '')
                                            individual = ONTO[d5](prefix+str(individual_name))
                                            individual.isAlternative.append(True)
                                        else:
                                            d5 = list(d5.descendants())
                                            for d6 in d5:
                                                if isinstance(d6, ONTO["Drugs"]):
                                                    d6 = str(d6).replace(ONTOLOGY_NAME,'')
                                                    individual_name = d6.replace('(', '_').replace(')', '_').replace('%', '')
                                                    individual = ONTO[d6](prefix+str(individual_name))
                                                    individual.isAlternative.append(True)
                                                else:
                                                    d6 = list(d6.descendants())
                                                    for d7 in d6:
                                                        if isinstance(d7, ONTO["Drugs"]):
                                                            d7 = str(d7).replace(ONTOLOGY_NAME,'')
                                                            individual_name = d7.replace('(', '_').replace(')', '_').replace('%', '')
                                                            individual = ONTO[d7](prefix+str(individual_name))
                                                            individual.isAlternative.append(True)



def changeClassName(className):
    name = list(ONTO[className].descendants())
    for className in name:
       className = str(className).replace(ONTOLOGY_NAME,'')
       individual_name = className.replace('(', '_').replace(')', '_').replace('%', '')
       #ONTO[className].name = individual_name
       ONTO[className].iri = "http://full.iri.com/"+individual_name 

def addClassNameLabel(className):
    name = list(ONTO[className].descendants())
    for c in name:
        c = str(c).replace(ONTOLOGY_NAME,'') 
        print(c)
        ONTO[c].label.en.append(c)



def OntoAddLabel(path):
    f = open(path)
    reader = csv.reader(f,  delimiter = ';')
    next(reader)
    with ONTO:
        for row in reader:
            Translation, name = row 
            name = name.strip()
            Translation = Translation.strip()
            name = name.replace(' ', '_').replace(',', '').replace(';', '')
            Translation = Translation.replace(' ', '_').replace(',', '').replace(';', '')
            print('name: ' + name + " Translation: "+ Translation)
            ONTO[name].label.pt.append(Translation)

def getDetails(teste):
    role = (ONTO[teste].comment)
    role =  (ONTO[teste].seeAlso)
    role =  (ONTO[teste].isDefinedBy)
    role =  (ONTO[teste].versionInfo)
    role =  (ONTO[teste].recomentation)
    role =  (ONTO[teste].NumberDrugs)
    print(NDrugs, Role)





#getDetails('DDI_CNS_Active_Drugs/CNS_Active_Drugs')

if FULLPROCESS:

    changeClassName('Drugs')
    createIndividuals('Drugs', 'i_')

    removeLabel('Drugs')
    removeLabel('Disease')
    removeLabel('AdministrationRoute')

    addClassNameLabel('Drugs')
    addClassNameLabel('Disease')
    addClassNameLabel('AdministrationRoute')
    createIndividuals('AdministrationRoute', 'i_')


    OntoAddLabel(r'OntologyIntegration/TranslationRoute.csv')
    OntoAddLabel(r'OntologyIntegration/TranslationDisease.csv')
    OntoAddLabel(r'OntologyIntegration/TranslationDrugsVT.csv')
    OntoAddLabel(r'OntologyIntegration/TranslationPrevDisease.csv')


#createIndividuals('Alt_Opioids', 'alt_')
#createIndividuals('Alt_Benzodiazepines', 'alt_')
#createIndividuals('Alt_Barbiturates', 'alt_')
#createIndividuals('Alt_Tertiary_amine_tricyclic_antidepressants', 'alt_')
#createIndividuals('Alt_First_generation_antihistamines', 'alt_')


#createDrugIndividuals('Alternatives', 'alt_')

#ONTO.save(r'OntologyIntegration/OntologiesFiles/BeersOntologyV17.owl', format = "rdfxml")


listLable('Drugs')







