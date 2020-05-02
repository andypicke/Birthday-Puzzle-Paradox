# Code to simulate the 'birthday puzzle paradox' and generate some plots

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
import seaborn as sns

# make plots look nice
plt.rcParams['font.size'] = 14
plt.rcParams['axes.labelsize'] = 'large'
plt.rcParams['xtick.labelsize'] = 'large'
plt.rcParams['ytick.labelsize'] = 'large'
plt.rcParams['lines.linewidth'] = 3
plt.style.use('ggplot')

def prob_shared_birthday(N_in_room, N_simulations=5000, probs=None):
    '''
    Simulate the 'Birthday Puzzle Paradox'
    
    INPUT
    N_in_room (integer) : Number of People in room
    N_simulations (integer)(optional) : Number of Simulations to run (default = 5000)
    probs (numpy array)(optional): Array of probabilities for each yday (1-365). 
        Defaults to 'None' (uniform probability distribution)
    
    RETURNS
    (p_gte2, p_gte3) (tuple of floats) : Probabilites of >=2, >=3 people sharing birthdays
    '''
    n_gte2 = []
    n_gte3  = []
    possible_ydays = np.arange(1,366)
    for _ in range(N_simulations):
        x = np.random.choice(possible_ydays, size = N_in_room,  replace=True, p=probs)
        vals = np.array(list(Counter(x).values()))
        n_gte2.append(np.sum(vals>=2))
        n_gte3.append(np.sum(vals>=3))
    p_gte2 = np.mean(np.array(n_gte2)>0)
    p_gte3 = np.mean(np.array(n_gte3)>0)
    return (p_gte2, p_gte3)


if __name__=='__main__':

    plt_size = (6,6)
    N_sims = 5000
    room_sizes = list(range(1,101))

    # Simulate w/ uniform distribution of birthdays
    p2_unif = []
    p3_unif = []
    for N_in_room in room_sizes:
        p_gte2, p_gte3 = prob_shared_birthday(N_in_room, N_simulations=N_sims)
        p2_unif.append(p_gte2)
        p3_unif.append(p_gte3)
    
    fig, ax = plt.subplots(1, figsize=plt_size)
    ax.plot(room_sizes, p2_unif, linewidth=3)
    ax.set_xlabel('# People in Room')
    ax.set_ylabel('Probability')
    ax.set_title('Prob. >=2 People Share Birthday (' + str(N_sims) + ' Simulations)')
    plt.savefig('./images/p_gte2_vs_N_uniform.png')

    fig, ax = plt.subplots(1, figsize=plt_size)
    ax.plot(room_sizes, p2_unif, linewidth=3, label='>=2')
    ax.plot(room_sizes, p3_unif, linewidth=3, label='>=3')
    ax.set_xlabel('# People in Room')
    ax.set_ylabel('Probability')
    ax.legend()
    ax.set_title('Prob >=N People Share Birthday (' + str(N_sims) + ' Simulations)')
    plt.savefig('./images/p_gte2_gte3_vs_N_uniform.png')
    
    # Load actual birth data
    df_births = pd.read_csv('./data/US_births_2000-2014_SSA.csv')
    df_births.drop(['day_of_week'], axis=1, inplace=True)
    df_births.rename( columns={'date_of_month':'day'},inplace=True)
    df_births['date'] = pd.to_datetime(df_births[['year', 'month', 'day']])
    df_births['leap_year'] = df_births['date'].dt.is_leap_year
    df_births['yearday'] = df_births['date'].dt.dayofyear
    df_births = df_births[df_births['leap_year']==False]
    df_births.drop('leap_year', axis=1, inplace=True)
    
    # Make heatmap of total births by month and day
    df2 = df_births.groupby(['month','day']).sum().reset_index()
    fig,ax = plt.subplots(1, figsize=(14,8))
    sns.heatmap(df2.pivot('month','day','births'), ax=ax)
    ax.invert_yaxis()
    ax.set_xlabel('Day of Month')
    ax.set_ylabel('Month')
    ax.set_title('Number of Births Vs. Month and Day')
    plt.savefig('images/births_heatmap.png')

    # calculate probability of being born each day from data
    total_births = df_births['births'].sum()
    df_births.drop(['year', 'month', 'day'], axis=1, inplace=True)
    df_gb_yday = df_births.groupby('yearday').sum().reset_index()
    df_gb_yday['birth_prob'] = df_gb_yday['births']/total_births
    df_gb_yday

    # Plot probabilities vs yearday
    fig, ax = plt.subplots(1, figsize=plt_size)
    ax.scatter(df_gb_yday['yearday'], df_gb_yday['birth_prob'], label='Actual Probs')
    ax.set_ylim(0,0.0035)
    ax.axhline(1/365, color='black', label='Uniform P (1/365)')
    ax.set_xlabel('Yearday')
    ax.set_ylabel('Probability')
    ax.legend()
    plt.savefig('images/birth_prob_vs_yday.png')

    # Run simulations w/ actual probs
    p2_prob=[]
    for N_in_room in room_sizes:
        p_gte2, p_gte3 = prob_shared_birthday(N_in_room, N_simulations=N_sims, probs = df_gb_yday['birth_prob'].values)
        p2_prob.append(p_gte2)

    fig, ax = plt.subplots(1, figsize=plt_size)
    ax.plot(room_sizes, p2_unif, linewidth=3, label='Uniform Dist.')
    ax.plot(room_sizes, p2_prob, linewidth=3, label='W/ Probs')
    ax.set_xlabel('# People in Room')
    ax.set_ylabel('Probability')
    ax.legend()
    ax.set_title('Prob >=2 People Share Birthday (' + str(N_sims) + ' Simulations)')
    plt.savefig('images/p_gte2_vs_N_uniform_actual.png')

    # Create a fake prob. distribution with larger differences to test if there is an effect
    ydays = np.arange(1,366)
    test_probs = np.sin(ydays/120)
    test_probs = test_probs/np.sum(test_probs)

    fig, ax = plt.subplots(1, figsize=plt_size)
    ax.plot(ydays,test_probs)
    ax.set_xlabel('Yearday')
    ax.set_ylabel('Probability')
    ax.set_title('Fake Probability Distribution')
    plt.savefig('images/fake_birth_prob_vs_yday.png')

    # Run simulations w/ fake probs
    p2_fake=[]
    for N_in_room in room_sizes:
        p_gte2, p_gte3 = prob_shared_birthday(N_in_room, N_simulations=N_sims, probs = test_probs)
        p2_fake.append(p_gte2)

    fig, ax = plt.subplots(1, figsize=plt_size)
    ax.plot(room_sizes, p2_unif, linewidth=3, label='Uniform Dist.')
    ax.plot(room_sizes, p2_fake, linewidth=3, label='W/ Fake Probs')
    ax.set_xlabel('# People in Room')
    ax.set_ylabel('Probability')
    ax.legend()
    ax.set_title('Prob >=2 People Share Birthday (' + str(N_sims) + ' Simulations)')
    plt.savefig('images/p_gte2_vs_N_uniform_fakeprobs.png')