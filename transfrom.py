import csv
import json

file = open('school2.csv', 'r')
csvreader = csv.reader(file, delimiter=';')
dict_id = {}
for row in csvreader:
    dict_id[row[0]] = row[5]
json.dump(dict_id,open('schools_mapping.json','w',encoding='utf-8'))
