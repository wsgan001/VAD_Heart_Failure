import sys
import operator
from collections import *

database = list()
maxCount = 0
alpha = 0.9
sim_choice = 1
top_n = 10

# jaccard similarity
def jaccardSimilarity(l1, l2):
    #note: (11.2) avoid using the last element in l1! it is timestamp!
    l11 = l1[0 : len(l1) - 1]
    return float(len(set(l11)&set(l2))) / len(set(l11)|set(l2))

"""
def cosineSimilarity(l1, l2):
    sim = 0
    for d in l2:
        if d in l1:
            sim += 1
    for d in l1:
        if d not in l2:
            sim -= 1
    return sim
"""

# will only have non-zero score if patient's diagnoses totally cover diagnoses in the sequence
def containSimilarity(pattern, patient):
    #avoid timestamp in pattern!
    ppattern = pattern[0 : len(pattern) - 1]
    if set(pattern).issubset(set(patient)):  # patient contains pattern
        return float(len(pattern))/len(patient)
    else:
        return 0


def calSimilarity(pattern, patient):
    #note: (11.2) avoid using the last element in pattern['sequence'][i]! it is timestamp!
    #if len(pattern['sequence']) <= len(patient):

    if len(pattern['sequence']) < len(patient):  #please at least allow self-retrieving in sanity check...
        return 0
    sim = 0
    if (int(patient[0]) != int(pattern['age_bin'])):
        return 0.0
    for i, diagnosis in enumerate(patient):
        if (i == 0):
            continue
        if sim_choice == 1:
            sim += jaccardSimilarity(pattern['sequence'][i], diagnosis)
        else:
            sim += containSimilarity(pattern['sequence'][i], diagnosis)
    score = (alpha * sim + (1-alpha) * pattern['count']/maxCount)  # count between 0-1, sim between 0-1
    return score



#For 11.2:
# for testing: create the testing instance here, put the timestamp in comment,
# format for patients is the same as before
# in parsing, keep track of timestamps separately, do not involve it in any matching,
# just put it back in output!

# preprocess existing sequential data
with open('spade_diagnose_from_heart_to_death_final_revised_with_dob.out') as f:
    for line in f:
        sequence, count = line.strip().split('#SUP: ')
        count = int(count)
        if count > maxCount:
            maxCount = count
        pattern = {}
        pattern['count'] = count
        pattern['sequence'] = list()
        tms = 0
        for s in sequence.split('->'):
            tms += 1
            if (tms == 1):
                pattern['age_bin'] = int(s.strip())
                continue
            sr = s[0:s.index('[')]
            timestamp = s[s.index('[') : s.index(']') + 1]
            diagnose_timestamp_list = sr.strip()[1:-1].split('\" \"')
            diagnose_timestamp_list.append(timestamp)
            pattern['sequence'].append(diagnose_timestamp_list) 
            #a timestamp is attached after every transaction
            #avoid this in pattern matching!
            #but it is easy to enable timestamp matching in this way.....
        database.append(pattern)

# match a new patient to current sequential data
# 261
#patient = [['Ac/subac bact endocard','CHF NOS','Atrial fibrillation','Atrial flutter','Protein-cal malnutr NOS','Dis tympanic memb NOS','Mal neo esophagus NEC','DMII wo cmp nt st uncntr']]

# 1024:[51884, 42833, 40391, 42731, 5845, 2767, 486, 25092, 03811, 70705, 5990, 99591, 4168, 32723, 27800, V5413, V1251, 56400]
# [82021, 42832, 4280, 5990, 2851, 42731, 5859, 99811, 5849, 9980, E8859, 2449, 25000, 4414, 73300, 40390, E8788]
# patient = [['Intertrochanteric fx-cl', 'Chr diastolic hrt fail', 'CHF NOS', 'Urin tract infection NOS', 'Ac posthemorrhag anemia', 'Atrial fibrillation', 'Chronic kidney dis NOS', 'Hemorrhage complic proc', 'Acute kidney failure NOS', 'Fall from slipping NEC', 'Hypothyroidism NOS', 'DMII wo cmp nt st uncntr', 'Abdom aortic aneurysm', 'Osteoporosis NOS', 'Hy kid NOS w cr kid I-IV', 'Abn react-surg proc NEC'],\
# ['Acute & chronc resp fail', 'Ac on chr diast hrt fail', 'Hyp kid NOS w cr kid V', 'Atrial fibrillation', 'Ac kidny fai', 'Hyperpotassemia', 'Pneumoni', 'DMII unspf uncntrld', 'Meth susc Staph aur sept', 'Pressure ulce', 'Urin tract infection NOS', 'Sepsis', 'Chr pulmon heart dis NEC', 'Obstructive sleep apnea', 'Obesity NOS', 'Aftrcre traumatic fx hip', 'Hx-ven thrombosis/embols', 'Constipation NOS']
# ]

patient = [2, ['Intertrochanteric fx-cl', 'Chr diastolic hrt fail', 'CHF NOS', 'Urin tract infection NOS', 'Ac posthemorrhag anemia', 'Atrial fibrillation', 'Chronic kidney dis NOS', 'Hemorrhage complic proc', 'Acute kidney failure NOS', 'Fall from slipping NEC', 'Hypothyroidism NOS', 'DMII wo cmp nt st uncntr', 'Abdom aortic aneurysm', 'Osteoporosis NOS', 'Hy kid NOS w cr kid I-IV', 'Abn react-surg proc NEC'],\
['Acute & chronc resp fail', 'Ac on chr diast hrt fail', 'Hyp kid NOS w cr kid V', 'Atrial fibrillation', 'Ac kidny fai', 'Hyperpotassemia', 'Pneumoni', 'DMII unspf uncntrld', 'Meth susc Staph aur sept', 'Pressure ulce', 'Urin tract infection NOS', 'Sepsis', 'Chr pulmon heart dis NEC', 'Obstructive sleep apnea', 'Obesity NOS', 'Aftrcre traumatic fx hip', 'Hx-ven thrombosis/embols', 'Constipation NOS']
]

# 10174
# [99592,41071,42613,78559,2765,4160,4240,25001,2767]
# [9724,5849,2767,5997,2765,E8583,4019,412,25000]
# [41071,60000,2720,4019,07032,41401,4280,4240,25060,3572,53081,V5867]
# [6823,6983,79093,53081,60001,78820,2809,27651,42789,5849,34982,2763,2762,5859,40310,25002,V4581]
# [42689,E9424,40390,5859,25000,2724,V4581,53081]
# patient = [['Severe sepsis', 'Subendo infarc', 'Av block-2nd degree NEC', 'Shock w/o trauma NEC', 'Prim pulm hypertension', 'Mitral valve disorder', 'DMI wo cmp nt st uncntrl', 'Hyperpotassemia'],\
# ['Pois-coronary vasodilat', 'Acute kidney failure NOS', 'Hyperpotassemia', 'Acc poisn-cardiovasc agt', 'Hypertension NOS', 'Old myocardial infarct', 'DMII wo cmp nt st uncntr'],\
# ['Subendo infarc', 'BPH w/o urinary obs/LUTS', 'Pure hypercholesterolem', 'Hypertension NOS', 'Hpt B chrn wo cm wo dlta', 'Crnry athrscl natve vssl', 'CHF NOS', 'Mitral valve disorder', 'DMII neuro nt st uncntrl', 'Neuropathy in diabetes', 'Esophageal reflux', 'Long-term use of insulin'],\
# ['Cellulitis of arm', 'Lichenification', 'Elvtd prstate spcf antgn', 'Esophageal reflux', 'BPH w urinary obs/LUTS', 'Retention urine NOS', 'Iron defic anemia NOS', 'Dehydration', 'Cardiac dysrhythmias NEC', 'Acute kidney failure NOS', 'Toxic encephalopathy', 'Alkalosis', 'Acidosis', 'Chronic kidney dis NOS', 'Ben hy kid w cr kid I-IV', 'DMII wo cmp uncntrld', 'Aortocoronary bypass'],
# ['Conduction disorder NEC', 'Adv eff coronary vasodil', 'Hy kid NOS w cr kid I-IV', 'Chronic kidney dis NOS', 'DMII wo cmp nt st uncntr', 'Hyperlipidemia NEC/NOS', 'Aortocoronary bypass', 'Esophageal reflux']\
# ]


#For 11.2:
# for testing: create the testing instance here, put the timestamp in comment,
# format for patients is the same as before
# in parsing, keep track of timestamps separately, do not involve it in any matching,
# just put it back in output!

#For sanity check
#"CHF NOS" [0] -> "Cardiac dysrhythmias NEC" [0] -> "DEATH" [0] #SUP: 8
#patient = [['CHF NOS'],\
#['Atrial fibrillation'],
#['DEATH']]


pattern_scores = dict()
for i, pattern in enumerate(database):  #i is "iteration number"
    score = calSimilarity(pattern, patient)
    pattern_scores[i] = score
    

# sort and print out top 10 result with scores 
sorted_score = sorted(pattern_scores.items(), key=operator.itemgetter(1))
sorted_score.reverse()

for index, score in sorted_score[:top_n]:
    print "%f\t%s" % (score, database[index])


