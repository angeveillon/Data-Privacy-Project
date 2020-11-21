import pandas as pd
import numpy as np


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
noisy= []
location=0
scale=(1/epsilon)*((sum(command_totals)/len(command_totals))-((sum(command_totals)-max(command_totals))/(len(command_totals)-1)))
for i in range (1000):
    Laplacian_noise = np.random.laplace(location,scale)
    noisy.append(sum(command_totals)/len(command_totals)+Laplacian_noise)

print("variance : ",np.var(noisy))