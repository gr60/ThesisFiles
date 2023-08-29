data = [{'A':'B'},{'A':'C'},{'A':'D'},{'A':'E'}]
rule = ''
for alternative in data:
    for drugA, drugB in alternative.items():
        rule = f'((Xor({drugA} Or {drugB})),{rule})'
        print (rule)