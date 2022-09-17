#!/usr/bin/env python
# coding: utf-8

# In[187]:


import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm


# In[58]:


"""Plan:
1. Get fusion ticket stuff fixed 
-Add 3rd party votes to main total
-VA error
2. Drop all 3rd party candidates
3. Get to 1 row per race
-Desired data: State, District, Year, GOP Votes, Dem Votes, Result
4. Merge Ratings Data
5. Add ratings for unrated races, set as safe for winner
-Spot check all races 10 points & less in this category
6. Create individual dataframes for each category
7. Analysis
- figure out how to handle unopposed races
"""


# In[92]:


data = pd.read_csv('/Users/walkers/Downloads/houseData.csv', encoding= 'unicode_escape')
ratings = pd.read_csv('/Users/walkers/Downloads/house_ratings.csv')

data = data[data['year'].isin([2012, 2014, 2016, 2018, 2020])].reset_index()


# In[93]:


fusion = data[['candidate','year','candidatevotes']].copy()

fusion = fusion.groupby(['candidate','year']).sum()

#Confirm only states that allow fusion ticket voting are listed
print(data['state'][data['fusion_ticket'] == True].drop_duplicates())

#Confirm numbers match with actual result
print(fusion.loc['RANDY ALTSCHULER'])

update = pd.merge(data, fusion,  how='left', left_on=['candidate','year'], 
                  right_on = ['candidate','year'])

print(update)


# In[94]:


update = update.drop(['index','state_fips','state_cen', 'state_ic', 'office', 'stage', 'writein', 'mode',
             'candidatevotes_x', 'totalvotes', 'unofficial', 'version', 'fusion_ticket'],axis=1)

no_third = update[update['party'].isin(['REPUBLICAN', 'DEMOCRAT'])].reset_index()

no_third = no_third.drop(['index', 'state', 'runoff', 'special'], axis=1)
print(no_third)


# In[133]:


totals = no_third.groupby(['year', 'state_po', 'district']).sum()

refine = pd.merge(no_third, totals,  how='left', left_on=['year', 'state_po', 'district'],
                  right_on = ['year', 'state_po', 'district'])

#implicitly drops all races where GOP doesn't field a candidate
refine = refine[refine['party'] == 'REPUBLICAN'] 

refine = refine.drop(['candidate', 'party'], axis = 1)

#deals with 2 republicans advancing to general
refine = refine.groupby(['year', 'state_po', 'district','candidatevotes_y_y']).sum().reset_index()

#check with Washington's 4th CD
print(refine[(refine['state_po'] == 'WA') & (refine['district'] == 4)])

refine['GOP_voteshare'] = refine['candidatevotes_y_x'] / refine['candidatevotes_y_y']

refine['result'] = refine['GOP_voteshare'] > 0.5

refine = refine.drop(['candidatevotes_y_x','candidatevotes_y_y'], axis = 1)


# In[150]:


main = pd.merge(refine, ratings,  how='left', left_on=['year', 'state_po', 'district'],
                  right_on = ['year', 'state', 'district'])

main = main.drop(['state'], axis = 1)

main = main.fillna(1.0) #sets all unrated races to safe democrat

#makes all safe democrat races that GOP won safe GOP
main.loc[(main['GOP_voteshare'] > 0.5) & (main['rating'] == 1), 'rating'] = 6 

#drop uncontested races
main = main[main['GOP_voteshare'] != 1]

#check for any issues with safe seat logic
print("Safe Dem Rating:\n", main[(main['GOP_voteshare'] > 0.47) & (main['rating'] == 1)])
print("Safe GOP Rating:\n", main[(main['GOP_voteshare'] < 0.53) & (main['rating'] == 6)])


# In[159]:


safe_dem = main[main['rating'] == 1]
likely_dem = main[main['rating'] == 2]
leans_dem = main[main['rating'] == 3]
leans_gop = main[main['rating'] == 4]
likely_gop = main[main['rating'] == 5]
safe_gop = main[main['rating'] == 6]


# In[180]:


def myplot(df, name):
    plt.hist(df['GOP_voteshare'], bins=10)
    print(("%s Rating:") % name)
    plt.show()


# In[181]:


myplot(safe_dem, "Safe Dem")
myplot(likely_dem, "Likely Dem")
myplot(leans_dem, "Leans Dem")
myplot(leans_gop, "Leans GOP")
myplot(likely_gop, "Likely GOP")
myplot(safe_gop, "Safe GOP")


# In[172]:


def prob(df, name):
    print("P(GOP | %s):" % name)
    print(len(df[df['result'] == True]) / len(df))


# In[173]:


print("Overall Probabilities:")
prob(safe_dem, "Safe Dem")
prob(likely_dem, "Likely Dem")
prob(leans_dem, "Leans Dem")
prob(leans_gop, "Leans GOP")
prob(likely_gop, "Likely GOP")
prob(safe_gop, "Safe GOP")


# In[184]:


likely_dem_pres = likely_dem[likely_dem['year'].isin([2012, 2016, 2020])]
likely_dem_mid = likely_dem[likely_dem['year'].isin([2014, 2018])]
leans_dem_pres = leans_dem[leans_dem['year'].isin([2012, 2016, 2020])]
leans_dem_mid = leans_dem[leans_dem['year'].isin([2014, 2018])]
leans_gop_pres = leans_gop[leans_gop['year'].isin([2012, 2016, 2020])]
leans_gop_mid = leans_gop[leans_gop['year'].isin([2014, 2018])]
likely_gop_pres = likely_gop[likely_gop['year'].isin([2012, 2016, 2020])]
likely_gop_mid = likely_gop[likely_gop['year'].isin([2014, 2018])]

likely_dem_more = likely_dem[likely_dem['year'].isin([2012, 2016, 2018])]
likely_dem_less = likely_dem[likely_dem['year'].isin([2014, 2020])]
leans_dem_more = leans_dem[leans_dem['year'].isin([2012, 2016, 2018])]
leans_dem_less = leans_dem[leans_dem['year'].isin([2014, 2020])]
leans_gop_more = leans_gop[leans_gop['year'].isin([2012, 2016, 2018])]
leans_gop_less = leans_gop[leans_gop['year'].isin([2014, 2020])]
likely_gop_more = likely_gop[likely_gop['year'].isin([2012, 2016, 2020])]
likely_gop_less = likely_gop[likely_gop['year'].isin([2014, 2018])]

likely_dem_recent = likely_dem[likely_dem['year'].isin([2018, 2020])]
likely_dem_old = likely_dem[likely_dem['year'].isin([2012, 2014, 2016])]
leans_dem_recent = leans_dem[leans_dem['year'].isin([2018, 2020])]
leans_dem_old = leans_dem[leans_dem['year'].isin([2012, 2014, 2016])]
leans_gop_recent = leans_gop[leans_gop['year'].isin([2018, 2020])]
leans_gop_old = leans_gop[leans_gop['year'].isin([2012, 2014, 2016])]
likely_gop_recent = likely_gop[likely_gop['year'].isin([2018, 2020])]
likely_gop_old = likely_gop[likely_gop['year'].isin([2012, 2014, 2016])]

likely_dem_recent2 = likely_dem[likely_dem['year'].isin([2016, 2018, 2020])]
likely_dem_old2 = likely_dem[likely_dem['year'].isin([2012, 2014])]
leans_dem_recent2 = leans_dem[leans_dem['year'].isin([2016, 2018, 2020])]
leans_dem_old2 = leans_dem[leans_dem['year'].isin([2012, 2014])]
leans_gop_recent2 = leans_gop[leans_gop['year'].isin([2016, 2018, 2020])]
leans_gop_old2 = leans_gop[leans_gop['year'].isin([2012, 2014])]
likely_gop_recent2 = likely_gop[likely_gop['year'].isin([2016, 2018, 2020])]
likely_gop_old2 = likely_gop[likely_gop['year'].isin([2012, 2014])]


# In[175]:


print("Presidential Year Probabilities:")
prob(likely_dem_pres, "Likely Dem")
prob(leans_dem_pres, "Leans Dem")
prob(leans_gop_pres, "Leans GOP")
prob(likely_gop_pres, "Likely GOP")

print("Midterm Year Probabilities:")
prob(likely_dem_mid, "Likely Dem")
prob(leans_dem_mid, "Leans Dem")
prob(leans_gop_mid, "Leans GOP")
prob(likely_gop_mid, "Likely GOP")


# In[176]:


print("Democrat Seat Gain Probabilities:")
prob(likely_dem_more, "Likely Dem")
prob(leans_dem_more, "Leans Dem")
prob(leans_gop_more, "Leans GOP")
prob(likely_gop_more, "Likely GOP")

print("Democrat Seat Loss Probabilities:")
prob(likely_dem_less, "Likely Dem")
prob(leans_dem_less, "Leans Dem")
prob(leans_gop_less, "Leans GOP")
prob(likely_gop_less, "Likely GOP")


# In[177]:


print("Recent Probabilities (2018 & 2020):")
prob(likely_dem_recent, "Likely Dem")
prob(leans_dem_recent, "Leans Dem")
prob(leans_gop_recent, "Leans GOP")
prob(likely_gop_recent, "Likely GOP")

print("Older Probabilities (2012-2016):")
prob(likely_dem_old, "Likely Dem")
prob(leans_dem_old, "Leans Dem")
prob(leans_gop_old, "Leans GOP")
prob(likely_gop_old, "Likely GOP")


# In[183]:


print("Recent Probabilities (2016-2020):")
prob(likely_dem_recent2, "Likely Dem")
prob(leans_dem_recent2, "Leans Dem")
prob(leans_gop_recent2, "Leans GOP")
prob(likely_gop_recent2, "Likely GOP")

print("Older Probabilities (2012 & 2014):")
prob(likely_dem_old2, "Likely Dem")
prob(leans_dem_old2, "Leans Dem")
prob(leans_gop_old2, "Leans GOP")
prob(likely_gop_old2, "Likely GOP")


# In[ ]:


likely_dem_recent2020 = likely_dem[likely_dem['year'].isin([2020])]
likely_dem_old201x = likely_dem[likely_dem['year'].isin([2012, 2014, 2016, 2018])]
leans_dem_recent2020 = leans_dem[leans_dem['year'].isin([2020])]
leans_dem_old201x = leans_dem[leans_dem['year'].isin([2012, 2014, 2016, 2018])]
leans_gop_recent2020 = leans_gop[leans_gop['year'].isin([2020])]
leans_gop_old201x = leans_gop[leans_gop['year'].isin([2012, 2014, 2016, 2018])]
likely_gop_recent2020 = likely_gop[likely_gop['year'].isin([2020])]
likely_gop_old201x = likely_gop[likely_gop['year'].isin([2012, 2014, 2016, 2018])]


# In[186]:


print("2020 Probabilities:")
prob(likely_dem_recent2020, "Likely Dem")
prob(leans_dem_recent2020, "Leans Dem")
prob(leans_gop_recent2020, "Leans GOP")
prob(likely_gop_recent2020, "Likely GOP")

print("\nOther Probabilities:")
prob(likely_dem_old201x, "Likely Dem")
prob(leans_dem_old201x, "Leans Dem")
prob(leans_gop_old201x, "Leans GOP")
prob(likely_gop_old201x, "Likely GOP")


# In[266]:


def mle_normal(name, df, mean, std, direction):
    print("%s MLE Normal Approx:" % name)
    
    N = 0.005
    
    df.loc[:,'LL'] = 0.0
    
    for i in range(len(df)):
        df.iloc[i,6] = norm.logpdf(df.iloc[i,3], mean, std)
    
    last = df['LL'].sum()
    best = last
    
    while(last == best):
        if direction == 1:
            mean += N
        else:
            mean -= N
            
        for i in range(len(df)):
            df.iloc[i,6] = norm.logpdf(df.iloc[i,3], mean, std)
        last = df['LL'].sum()
        if (last > best):
            best = last
        
        
    if direction == 1:
        mean -= N
    else:
        mean += N
        
    last = best
      
    N /= 5    
    while(last == best): 
        std += N
        for i in range(len(df)):
            df.iloc[i,6] = norm.logpdf(df.iloc[i,3], mean, std)
        last = df['LL'].sum()
        if last > best:
            best = last
    
    std -= N
        
    print("N(%f,%f)" % (mean, std))


# In[270]:


mle_normal("Likely Dem", likely_dem, 0.7,0.001,0)
mle_normal("Likely Dem", likely_dem, 0.4,0.001,1)
mle_normal("Leans Dem", leans_dem, 0.7,0.001,0)
mle_normal("Leans Dem", leans_dem, 0.4,0.001,1)
mle_normal("Leans GOP", leans_gop, 0.7,0.001,0)
mle_normal("Leans GOP", leans_gop, 0.4,0.001,1)
mle_normal("Likely GOP", likely_gop, 0.7,0.001,0)
mle_normal("Likely GOP", likely_gop, 0.4,0.001,1)


# In[273]:


def compare(df, name, mean, std):
    print("%s:" % name)
    print("P(GOP | %s) " % name)
          
    gop_actual = len(df[df['result'] == True]) / len(df)
    #Normal cdf represents P(Dem_Win) in all cases LOTP to get GOP
    gop_approx = 1 - norm.cdf(0.5, mean, std)
    
    print("Observed = %f" % gop_actual)
    print("Approximated = %f" % gop_approx)
    diff = abs(gop_actual - gop_approx)
    print("Difference = %f" % diff)


# In[275]:


compare(likely_dem, "Likely Dem", 0.455, 0.026)
compare(leans_dem, "Leans Dem", 0.485, 0.03)
compare(leans_gop, "Leans GOP", 0.535, 0.031)
compare(likely_gop, "Likely GOP", 0.56, 0.035)

