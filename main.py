import pandas as pd
import numpy as np
from collections import Counter


#read csv
dataset = pd.read_csv("Online Retail.csv",sep=',',dtype={"voiceNo":int,"StockCode":str, "Description":str, "Quantity":int, "InvoiceDate":str, "UnitPrice":float,
"CustomerID":float, "Country": str})

#filling empty slots with zeroes (most likely doesnt work)
dataset.fillna('0')

#feel free to use the dataset with pandas if you are more comfortable with it / think it's better for the project. I can learn and switch to it.

dataprov=[]
command_totals=[]

#open csv
with open('Online Retail.csv',"r") as source:
  for row in source:
    #remove last line
    if len(row)>1 :
    #split into lists
      currentrow = row.split(",")
      #only keep rows without missing data
      if len(currentrow)==8:
        dataprov.append(currentrow)

print('oui',len(dataprov))
#remove first row ( names of columns )
dataprov=dataprov[1:]
data=[]

#only keep rows with positive quantities (there are negative ones in the dataset), and with unit price >0
for i in dataprov:
    if (float(i[3])>0.0) & (float(i[5])>0.0):
        data.append(i)


commands=[[data[0]]]

#create a list of commands. each command is a list of rows with same voiceNo
for i in range(1,len(data)):
    #if VoiceNo of current row corresponds to the one of last command in commands ( = it isnt a new command), append current row to the last commend
    if data[i][0]!=commands[-1][0][0]:
        commands.append([data[i]])
    #else: append a new command with current row
    else:
        commands[-1].append(data[i])

#calculate the price of each command, and create a list with them
for x in commands:
    command_totals.append(sum([float(i[5])*float(i[3])for i in x]))
    #command_totals.append(sum([float(i[5]) for i in x]))

print(max(command_totals),min(command_totals))

#EPSILON
epsilon = 5

#print(sum(command_totals)/len(command_totals))

#some laplace noise 
noisy= []
location=0
scale=(1/epsilon)*((sum(command_totals)/len(command_totals))-((sum(command_totals)-max(command_totals))/(len(command_totals)-1)))
for i in range (1000):
    Laplacian_noise = np.random.laplace(location,scale)
    noisy.append(sum(command_totals)/len(command_totals)+Laplacian_noise)

print("variance : ",np.var(noisy))

#give, for each item, the item msot likely to be bought with, with Exponential mechanism
commands_items=[]
#create list for each command, only with the items bought
for i in commands:
    commands_items.append([x[2]for x in i])

list1=[]
for x in commands_items:
    for i in x:
        list1.append(i)

#this one stores all the different items (no duplicate) that have been sold
all_items=list(set(list1))
#print(len(all_items))

all_items.sort()

#lists of items that are bought along with each item
#link is made via index
relatives=[[] for i in range(len(all_items))]
for x in range(len(all_items)):
    for y in commands_items:
        if (all_items[x] in y):
            for a in y:
                if a !=all_items[x]:
                    relatives[x].append(a)


#remove items that are bought alone
to_be_removed=[]
count_rem=0
for x in range(len(relatives)):
    if relatives[x]==[]:
        to_be_removed.append(x-count_rem)
        count_rem+=1

for i in to_be_removed:
    del(all_items[i])
relatives=[x for x in relatives if not x==[]]



#df = pd.DataFrame(commands_items)
#print(commands_items[0])
print(relatives[0])
print(all_items[0])


#counters of occurences of each item per "bought-along " list
counters=[Counter(i).most_common() for i in relatives]


#transform tuples returned by most common into lists
for i in range(len(counters)):
    for j in range(len(counters[i])):
        counters[i][j]=list(counters[i][j])

print(counters[-1])

#exponential mechanism
for x in range(len(counters)):
    sigma=0
    for y in range(len(counters[x])):
        counters[x][y].append(np.exp(epsilon*counters[x][y][1]/2))
    for y in range(len(counters[x])):
        sigma+=counters[x][y][-1]
    alpha = 1/sigma
    for y in range(len(counters[x])):
        counters[x][y][-1]*=alpha


choices=[]
for i in range (len(all_items)):
    choices.append([all_items[i],[x[0]for x in counters[i]],[x[2]for x in counters[i]]])

print(choices[-1])
