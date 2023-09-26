#!/usr/bin/env python
# coding: utf-8

# In[14]:


import pandas as pd
import numpy as np
import math


# In[15]:


def get_training_set():
    iris_data = pd.read_csv("iris_flower.csv")
    iris_data = iris_data[iris_data.columns[1:]].to_numpy()
    return iris_data


# In[16]:


def get_testing_set():
    iris_test = pd.read_csv("iris_flower.csv")
    iris_test = iris_test[iris_test.columns[1:]].to_numpy()
    return iris_test


# In[17]:


def get_generated_set():
    sampled_data = pd.read_csv("Samples/guassian_copula_iris-sample.csv")
    sampled_data = sampled_data[sampled_data.columns[2:]].to_numpy()
    return sampled_data

