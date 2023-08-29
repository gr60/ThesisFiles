from z3 import (Solver, And, Or, Not, sat, Datatype, Function, BoolSort, Exists, Distinct, Const, Xor)
import re
#import signal
from contextlib import contextmanager


class Solver_obj(object):

    def __init__(self, interaction = [], variables = [], alternatives = [], prescription= [], opt_false= [], opt_true= [], nr_prescription = int):
        self.interaction = interaction
        self.alternatives = alternatives
        self.prescription = prescription
        self.nr_prescription = nr_prescription
        self.opt_false = opt_false
        self.opt_true = opt_true
        self.variables = variables


def check_prescription( Solver_obj):
    obj_solve = Solver_obj
    result = False
    if len(obj_solve.interaction) == 0:
        return ([True])
    else:
        result = solve_alternatives(obj_solve)
        return (result)


def get_true_values(model, num):
    characters_to_remove = "[" +  "]=[==,"+ "]"
    data_string = str(model)
    data_string = re.sub(characters_to_remove, "", data_string)
    split_data = data_string.split()
    drugs = set()
    try:
        for i in range (num):
            index = split_data.index('Drug'+str(i))
            drugs.add( str(split_data[index+1]))
    except Exception as e: print('err')
    return(drugs)

def remove_duplicate_sets(set_p): #remove alternative if it has inconsistency with itself, for example [[Aspirin, Aspirin]]
    result = []
    [result.append(x) for x in set_p if x not in result]
    return(result)

def solve_alternatives(self):
    sol = Solver()
    sol.set("timeout", 60000)
    Drug = Datatype('Drug')
# Inserting variables
#Add drug names to a set drug (prescription, interaction and alternatives)
    set_drugs = set()
    set_alternative = set()
    set_prescription = set()

    self.interaction = remove_duplicate_sets(self.interaction)

    for prel1 in self.prescription: #prescription
        set_drugs.add(prel1)
        set_prescription.add(prel1)

    for intl1 in self.interaction: #interaction
        for intl2 in intl1:
            set_drugs.add(intl2)

    for altl1 in self.alternative: #alternatives
        for altl2 in altl1:
            set_drugs.add(altl2)
            set_alternative.add(altl2)

#Declare drugs i1n Z3
    for drug in set_drugs:
        Drug.declare(str(drug))
    
    Drug = Drug.create()
    distinct_rules = []

    choice = Function('choice', Drug, BoolSort())

    for x in range(len(self.prescription)):
        exec("Drug"+str(x)+" = Const('Drug"+str(x)+"', Drug)")
        sol.assert_and_track(Exists([eval("Drug"+str(x))],choice(eval("Drug"+str(x)))), 'Exists_'+ str(x))
        sol.assert_and_track(And(choice(eval("Drug"+str(x))) == True), 'ExistsTrue_'+ str(x))
        distinct_rules.append(eval("Drug"+str(x)))
    sol.assert_and_track(Distinct([x for x in distinct_rules]), 'Distinct_'+ str(x))


#Insert true drugs on Z3  - drugs without alternatives
    sequence = 0
    trueDrugs = set_prescription.difference(set_alternative)
    for drug in trueDrugs:
        sol.assert_and_track(And(choice(eval("Drug."+str(drug))) == True), str(f'TRUE_{drug}'))
        sol.assert_and_track(Exists([eval(f"Drug{str(sequence)}")],choice(eval(f"Drug.{str(drug)}" ))), f'Exists_Drug{str(sequence)} / {str(drug)}')
        sequence += 1

# Inserting interaction rules
    for interactList in self.interaction:
        sol.assert_and_track(Or(Not(choice(eval("Drug."+str(interactList[0])))), (Not(choice(eval("Drug."+str(interactList[1])))))),str(f'NOT_{str(interactList[0])}/{str(interactList[1])}'))
      
 #Insert alternative rules on Z3
    drugAlternaitve = [["choice(Drug."+drug+")" for drug in group] for group in self.alternative]
    altSequence = 0
    for alternative in drugAlternaitve:
        if len(alternative) > 2:
            for value in alternative:
                altSequence += 1
                tempList = alternative.copy()
                tempList.remove(value)
                tempList2 = ','.join(str(e) for e in tempList)
                sol.assert_and_track(Xor(eval(value), Or(eval(tempList2))), str('XOR'+str(altSequence)))
        else:
            altSequence += 1
            sol.assert_and_track(Xor(eval(alternative[0]),eval(alternative[1])), str('XOR'+str(altSequence)))
    model = []
    check = sol.check()
    if check == sat:
        sequence = 0
        while sol.check() == sat:
            sequence += 1
            prescrModel = sorted(frozenset(get_true_values(sol.model(), len(self.prescription))))
            if len(self.prescription) == len(prescrModel):
                if prescrModel not in model:
                    model.append(prescrModel)
            else:
                break
            solution = "False"
            trueValues = get_true_values(sol.model(), len(self.prescription)).difference(trueDrugs)
            if trueValues:
                for i in trueValues:
                    i = 'choice(Drug.'+str(i)+')'
                    solution = f"Or(({i} != {True}), {solution})"
                f2 = eval(solution)
                sol.assert_and_track((f2), f'Models{sequence}')
            else:
                break
    if sol.reason_unknown() == 'canceled':
        return (sol.reason_unknown())
    else:
        return(model)
