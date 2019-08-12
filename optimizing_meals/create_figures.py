#!/usr/bin/env python
# coding: utf-8

# ## Imports and settings

# In[1]:


import pandas as pd
from pprint import pprint
import os
import numpy as np
import math
import matplotlib.pyplot as plt

from optimizing_meals import optimize_mealplan, print_results
from classes import Meal, Food


# In[2]:


pd.set_option("display.max_rows", 64)
pd.set_option("display.max_columns", 64)
pd.set_option('precision', 1)

FIGSIZE = (9, 3)


# In[3]:


if not os.path.exists("figures"):
    os.makedirs("figures")


# ## Functions

# In[4]:


def plot_results(x, meals, results_data, filename=None):
    """Plot the results"""
    COLORS = plt.rcParams['axes.prop_cycle'].by_key()['color']
    
    num_meals, num_days = len(x), len(x[0])
    
    
    for day_num in range(num_days):
        
        # Get the quantities
        x_day = [x[i][day_num] for i in range(num_meals)]
        
        # Prepare results
        result = list((m, qnty) for (m, qnty) in zip(meals, x_day))
        price = int(sum(meal.price * qnty for (meal, qnty) in result))
        
        meal_names = [meal.name for (meal, qnty) in result]
        x_ticks = list(range(len(meal_names)))
        
        fig = plt.figure(figsize=FIGSIZE)
        
        # PLOT 1 - Foods and quantities
        ax1 = plt.subplot(1, 3, 1)
        ax1.set_title(f"Day {day_num+1} - Price: {price} NOK")
        
        quantities = [qnty for (meal, qnty) in result]
        colors = [COLORS[2] if meal.discrete else COLORS[0] for (meal, qnty) in result]
        
        ax1.barh(x_ticks, quantities, color=colors, zorder=15, alpha=0.75)
        
        max_quant = int(math.ceil(max(quantities)))
        ax1.set_xticks(list(range(0, max_quant+1)))
        
        ax1.set_yticks(x_ticks)
        ax1.set_yticklabels(meal_names)
        ax1.yaxis.set_tick_params(rotation=0)
        ax1.grid(True, ls="--", alpha=0.5, zorder=5)
        ax1.set_xlabel("Quantities")
        
        # PLOT 2 - Calories
        ax2 = plt.subplot(1, 3, 2)
        calories = [meal.kcal * qnty for (meal, qnty) in result]
        ax2.set_title(f"Total calories: {int(round((sum(calories))))} kcal")
        
        ax2.barh(x_ticks, calories, color=colors, zorder=15, alpha=0.75)
        ax2.set_yticklabels(['' for meal in meal_names])
        ax2.yaxis.set_tick_params(rotation=90)
        
        ax2.grid(True, ls="--", alpha=0.5, zorder=5)
        ax2.set_xlabel("Calories")
        
        # PLOT 3 - Protein
        ax3 = plt.subplot(1, 3, 3)
        protein = [meal.protein * qnty for (meal, qnty) in result]
        ax3.set_title(f"Total protein: {int(round((sum(protein))))} g")
        
        ax3.barh(x_ticks, protein, color=colors, zorder=15, alpha=0.75)
        ax3.set_yticklabels(['' for meal in meal_names])
        ax3.yaxis.set_tick_params(rotation=90)
        
        ax3.grid(True, ls="--", alpha=0.5, zorder=5)
        ax3.set_xlabel("Protein")
        
        plt.tight_layout()
        
        if filename:
            plt.savefig(os.path.join("figures", f"{filename}.pdf"))
            plt.savefig(os.path.join("figures", f"{filename}.png"), dpi=300)
        # Only plot first day
        break


# ## Data

# In[5]:


from data import meals


# In[6]:


dietary_constraints = {"kcal": (1800, 1800), "protein": (100, None), "fat": (65 , None)}
meals = list(meals.values())


# ## Prin the meals to a markdown table

# In[7]:


print(' | '.join(["Name", "Discrete", "Grams per base meal", "Description"]))
print(' | '.join(["-----"] * 4))

for meal in meals:
    
    print(' | '.join([meal.name, str(meal.discrete), str(meal.grams), str(meal.foods)]))


# ## Example - constraint on nutrition only

# In[8]:


dietary_constraints = {"kcal": (1800, 1800), "protein": (100, None), "fat": (60 , None)}


# In[9]:


params = {"num_days":1, 
          "num_meals":4,

          "weight_price":-0.01,
          "weight_nutrients":1,
          "weight_range":0,
          "epsilon": 0.1
          }

x, results_data = optimize_mealplan(meals=meals, 
                  meals_limits=None, 
                  dietary_constraints=dietary_constraints, 
                  params=params)

print(results_data)
plot_results(x, meals, results_data, "single_day_constrained_nutrients")


#  ## Example - nutrient constraints and price constraint

# In[10]:


params = {"num_days":1, 
          "num_meals":4,

          "weight_price":0.01,
          "weight_nutrients":1,
          "weight_range":0,
          "epsilon": 0.1
          }

x, results_data = optimize_mealplan(meals=meals, 
                  meals_limits=None, 
                  dietary_constraints=dietary_constraints, 
                  params=params)

print(results_data)
plot_results(x, meals, results_data, "single_day_constrained_nutrients_price")


# ## Example - nutrient constraints and price constraint and range constraint

# In[11]:


params = {"num_days":1, 
          "num_meals":4,

          "weight_price":0.1,
          "weight_nutrients":2.0,
          "weight_range":0.1,
          "epsilon": 0.1
          }

x, results_data = optimize_mealplan(meals=meals, 
                  meals_limits=None, 
                  dietary_constraints=dietary_constraints, 
                  params=params)

print(results_data)
plot_results(x, meals, results_data, "single_day_constrained_nutrients_price_range")


# ## Example - serveral days

# In[12]:


num_days = 8

params = {"num_days": num_days, 
          "num_meals": 4,

          "weight_price": 0.1,
          "weight_nutrients": 2.0,
          "weight_range": 0.1,
          "epsilon": 0.001,
          "time_limit_secs": 60
          }

meals_limits = [(None, i+2) for i in range(len(meals))]


# In[13]:


# Running the cell block once gives: RuntimeError: Infeasible problem.
# Running it again works. This is strange.

x, results_data = optimize_mealplan(meals=meals, 
                  meals_limits=meals_limits, 
                  dietary_constraints=dietary_constraints, 
                  params=params)


# In[14]:


results_data


# In[15]:


def get_kcals(x, meals):
    """Get kcals and protein"""
    num_meals, num_days = len(x), len(x[0])
    
    for day_num in range(num_days):
        
        # Get the quantities
        x_day = [x[i][day_num] for i in range(num_meals)]
        result = list((m, qnty) for (m, qnty) in zip(meals, x_day))
        calories = [meal.kcal * qnty for (meal, qnty) in result]
        yield int(round(sum(calories)))


# In[16]:


meals


# In[17]:


# Get calories for each day
kcals = list(get_kcals(x, meals))

# Convert results to array for vectorized where
x = np.array(x)

plt.figure(figsize=(12, 5))

plt.title("Meals and days (meal $i$ used at most $i+1$ times)")

# Paired, 
x_plot = np.sqrt(x)
plt.imshow(x_plot, alpha=1, cmap=plt.get_cmap("BuGn"),
           vmin=0, vmax=np.max(x_plot) + 1)

days_ticks = list(range(num_days))
plt.xticks(days_ticks, 
           [f"Day {i+1} ({c} kcal)" for i, c in 
            zip(days_ticks, kcals)], 
           rotation=90)

meals_ticks = list(range(len(meals)))
plt.yticks(meals_ticks, 
           [f"Meal {i+1} ({m.name})" for i, m in zip(meals_ticks, meals)])

for (j, i), label in np.ndenumerate(x):
    if label <= 0:
        continue
    label = np.round(label, 1)
    if label % 1 == 0:
        label = int(label)
        
    plt.text(i, j, label, ha='center',va='center')

plt.tight_layout()
filename = "many_days_w_constraints"
plt.savefig(os.path.join("figures", f"{filename}.pdf"))
plt.savefig(os.path.join("figures", f"{filename}.png"), dpi=300)
plt.show()


# In[18]:


print_results(x, meals, results_data)

