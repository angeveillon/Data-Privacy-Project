import pandas as pd
import numpy as np
from collections import Counter
from copy import deepcopy

# please not that code execution is very long (~10 mins maybe ?)because of one step in particular. This is explained later at said step, but an apology is mandatory here.
# So, sorry!





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


#remove first row ( names of columns )
dataprov=dataprov[1:]
data=[]

#only keep rows with positive quantities (there are negative ones in the dataset), and with unit price >0
for i in dataprov:
    if (float(i[3])>0.0) & (float(i[5])>0.0):
        data.append(i)


# query : give the average invoice price made on the website.

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



#EPSILON
epsilon = 5



#some laplace noise 
noisy= []
location=0
scale=(1/epsilon)*((sum(command_totals)/len(command_totals))-((sum(command_totals)-max(command_totals))/(len(command_totals)-1)))

# we give 1000 results of the average with Laplace noise added
for i in range (1000):
    Laplacian_noise = np.random.laplace(location,scale)
    noisy.append(sum(command_totals)/len(command_totals)+Laplacian_noise)

print("variance : ",np.var(noisy))
with open('output_laplace.csv',"w") as output:
    for i in noisy:
        output.write(str(i))
        output.write("\n")
    output.close()

#give, for each item, the item most likely to be bought with, with Exponential mechanism
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
print(len(all_items))

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






#counters of occurences of each item per "bought-along " list
counters=[Counter(i).most_common() for i in relatives]


#transform tuples returned by most common into lists
for i in range(len(counters)):
    for j in range(len(counters[i])):
        counters[i][j]=list(counters[i][j])
        counters[i][j][1]/=50

# for association rule
counters2= deepcopy(counters)
for i in range(len(counters2)):
    sommation =sum([k[1]for k in counters2[i]])
    for j in range(len(counters2[i])):
        counters2[i][j][1]*=50
        counters2[i][j][1]/=sommation


#exponential mechanism
for x in range(len(counters)):
    sigma=0
    for y in range(len(counters[x])):
        counters[x][y].append(np.exp(epsilon*counters[x][y][1]/2))
    for y in range(len(counters[x])):
        sigma+=counters[x][y][-1]
    # ponderation to get sum(probabilities)=1
    alpha = 1/sigma
    for y in range(len(counters[x])):
        counters[x][y][-1]*=alpha


choices=[]
for i in range (len(all_items)):
    choices.append([all_items[i],[x[0]for x in counters[i]],[x[2]for x in counters[i]]])

#generate a choice for each vialid item

choice_for_each_item=[]
for i in range(len(choices)):
    choice_for_each_item.append([choices[i][0],np.random.choice(choices[i][1],1,p=choices[i][2])])



with open('output_expo.csv',"w") as output:
    for i in choice_for_each_item:
        output.write(str(i))
        output.write("\n")
    output.close()


 
# association rule:

#create a list filled with [item i, # of occurences of item i]
# calculate support of item i: # of occurences of item i / #total of items
# add Laplace noise to this support
#for the sensitivity, adding an extra item can either increase both # of occurences of items i and #total of items, or just #total of items if it is not i. 
#We can deduce that the highest impact is when it increases both # of occurences of items i and #total of items. Then the difference is 1/#total of items which is in our code also 1/len(commands)
epsilon2=10

supports=Counter(list1).most_common()


for i in range(len(supports)):
    Laplacian_noise_1 = np.random.laplace(0,8/(epsilon2*len(commands)))
    supports[i]=list(supports[i])
    a=round((supports[i][1]/len(commands))+Laplacian_noise_1,5)
    if a>0:
        supports[i][1]=a
    else:
        supports[i][1]=0.0
supports.sort( key = lambda x: x[0])




# calculate support of item i bought along with item j : # of occurences of items i and j / #total of items
#for the sensitivity, adding an extra item can either increase both # of occurences of items i and j and #total of items, or just #total of items if it is neither i nor j
#we add Laplace noise here
#please note that the time complexity of this step is, if not horrible, huge. This one actually takes several minutes because we keep checking back supports to get the correct object.
# So complexity explodes(count reaches ~7,000,000 and is used here to indicate you that code does not crash). Sorry for that...
supp_combs=[]
count=0
for i in range(len(counters2)):
    for j in range(len(counters2[i])):
        Laplacian_noise_2 = np.random.laplace(0,8/(epsilon2*len(commands)))
        b=round((counters2[i][j][1]*supports[i][1])+Laplacian_noise_2,5)
        #if b>0.5:
        for k in supports:
            if counters2[i][j][0]==k[0]:
                count+=1
                if count%100000==0:
                    print(count)
                support2=k[1]
                break
        if b>1:
            b=1
        if b>0:
            supp_combs.append([all_items[i],counters2[i][j][0],b,supports[i][1],support2])
        else:
            supp_combs.append([all_items[i],counters2[i][j][0],0,supports[i][1],support2])





#confidence(i,j) = support ( i,j)/support (i)
#we add Laplace noise here

confidences=[]
for i in supp_combs:
    Laplacian_noise_3 = np.random.laplace(0,4/(3*epsilon2*len(commands)))
    if i[3]!=0:
        confidences.append([i[0],i[1],round(i[2]/i[3]+Laplacian_noise_3,5)])
    else:
        confidences.append([i[0],i[1],round(Laplacian_noise_3/2,5)])

#print(confidences[0])

# lift(i,j) = confidence(i,j)/support(j)=support ( i,j)/(support (i)*support(j))
#we add Laplace noise here
lifts=[]
for i in supp_combs:
    Laplacian_noise_3 = np.random.laplace(0,8/(5*epsilon2*len(commands)))
    if (i[3]*i[4])!=0:
        lifts.append([i[0],i[1],round(i[2]/(i[3]*i[4])+Laplacian_noise_3,5)])
    else:
        lifts.append([i[0],i[1],round(Laplacian_noise_3/2,5)])
#print(lifts[0])

# leverage(i,j) = support (i,j)-(support(i)*support(j))
#we add Laplace noise here
leverages=[]
for i in supp_combs:
    Laplacian_noise_3 = np.random.laplace(0,5/(5*epsilon2*len(commands)))
    leverages.append([i[0],i[1],round(i[2]-(i[3]*i[4])+Laplacian_noise_3,5)])

#print(leverages[0])

# conviction(i,j) = (1- support(j))/(1- confidence(i,j))
#we add Laplace noise here
convictions=[]
for i in supp_combs:
    Laplacian_noise_3 = np.random.laplace(0,4/(3*epsilon2*len(commands)))
    if i[2]!=1.0:
        convictions.append([i[0],i[1],round((1-i[4])/(1.0-i[2])+Laplacian_noise_3,5)])
    else:
        convictions.append([i[0],i[1],"inf"])
#print(convictions[0])


#create suggestions by returning the pair ith the highest confidence for each item
max_confidences = [[confidences[0]]]
for i in range(1, len(confidences)):
    if confidences[i][0]==max_confidences[-1][0][0]:
        max_confidences[-1].append(confidences[i])
    else:
        max_confidences.append([confidences[i]])
suggest_conf=[]
for i in max_confidences:
    suggest_conf.append(max(i,  key=lambda x:x[2]))

with open('output_confidence.csv',"w") as output:
    for i in suggest_conf:
        output.write(str(i))
        output.write("\n")
    output.close()