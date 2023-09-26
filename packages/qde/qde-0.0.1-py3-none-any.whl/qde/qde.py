#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import math
def warn(*args, **kwargs):
    pass
import warnings
warnings.warn = warn
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split


# In[4]:


class quality_data_extractor:
    def __init__(self):
        self._n_samples = 0
        self._n_train = 0
        self._n_test = 0
        self._n_features = 0
  
    def _get_distinct_outputs(self, data_set):
        return np.unique(data_set)

    def _check_error(self):
        pass

    def _initialize_dataset(self, training_set, sampled_set, test_set):
        self._check_error()
        self._n_features = len(training_set[0])
        self.train_x = training_set[:, range(0,self._n_features-1)]
        self.train_y = training_set[:,-1].T
        if test_set is not None:
            self.test_x = test_set[:, range(0,self._n_features-1)]
            self.test_y = test_set[:,-1].T
        else:
            self.train_x, self.test_x, self.train_y, self.test_y = train_test_split(self.train_x, self.train_y, 
                                                                                  test_size=0.33, random_state=42)
        self.sample_x = sampled_set[:, range(0,self._n_features-1)]
        self.sample_y = sampled_set[:,-1].T
        self._n_samples = len(self.sample_x)
        self._n_train = len(self.train_x)
        self._n_test = len(self.test_x)
        self._distinct_outputs = self._get_distinct_outputs(self.train_y)
  
    def fit(self, training_set, sampled_set, test_set = None):
        self._initialize_dataset(training_set, sampled_set, test_set)

    def _get_pred_with_model(self, data_x, data_y, accuracy = True):
        self.model.fit(data_x, data_y)
        pred = self.model.predict(self.test_x)
        if accuracy:
            return accuracy_score(self.test_y, pred)
        return pred

    def get_accuracy(self, model = GaussianNB(), _type = 0):
        self.model = model
        if _type== 0:
            accuracy = self._get_pred_with_model(np.concatenate((self.train_x, self.sample_x)), np.concatenate((self.train_y, self.sample_y)))
        elif _type == 1:
            accuracy = self._get_pred_with_model(self.train_x, self.train_y)
        elif _type == 2:
            accuracy = self._get_pred_with_model(self.sample_x, self.sample_y)
        else:
            print("_type can only have 0, 1 or 2.")
            return
        return accuracy

    def get_data_optimal_approach(self, model):
        self.model = model
        original_acc = self.get_accuracy(model, _type = 1)
        temp_train_x = np.copy(self.train_x)
        temp_train_y = np.copy(self.train_y)
        combined_x = np.copy(self.train_x)
        combined_y = np.copy(self.train_y)
        

        for i in range(self._n_samples):
            temp_train_x = np.r_[temp_train_x,[self.sample_x[i]]]
            temp_train_y = np.r_[temp_train_y,[self.sample_y[i]]]
            temp_acc = self._get_pred_with_model(temp_train_x, temp_train_y)
            acc_diff = original_acc - temp_acc
            if acc_diff <= 0:
                combined_x = np.r_[combined_x,[self.sample_x[i]]]
                combined_y = np.r_[combined_y,[self.sample_y[i]]]
            temp_train_x = np.delete(temp_train_x, len(temp_train_x)-1,0)
            temp_train_y = np.delete(temp_train_y, len(temp_train_y)-1,0)
        combined_data = np.hstack((combined_x, np.atleast_2d(combined_y).T))
        return combined_data, self._get_pred_with_model(combined_x, combined_y) 

  
    def get_data_quick_approach(self):
        self.model = KNeighborsClassifier(n_neighbors=5)
        combined_x = np.copy(self.train_x)
        combined_y = np.copy(self.train_y)
        pred_sample = self._get_pred_with_model(self.sample_x, self.sample_y, False)
        _selected_indeces = []
        for i in range(self._n_test):
            if pred_sample[i] == self.test_y[i]:
                indeces = self.model.kneighbors([self.test_x[i]], return_distance=False)
                selected_index = -1
                for j in indeces[0]:
                    if self.sample_y[j] == self.test_y[i]:
                        selected_index = j
                        break
                if selected_index not in _selected_indeces:
                    _selected_indeces.append(selected_index)
                    combined_x = np.r_[combined_x,[self.sample_x[selected_index]]]
                    combined_y = np.r_[combined_y,[self.sample_y[selected_index]]]

        combined_data = np.hstack((combined_x, np.atleast_2d(combined_y).T))
        return combined_data, self._get_pred_with_model(combined_x, combined_y) 


    def get_combined_data(self, model = GaussianNB(), recipe = 0):
        if recipe == 0:
            self.combined_data, self._combined_accuracy = self.get_data_optimal_approach(model)
        elif recipe == 1:
            self.combined_data, self._combined_accuracy = self.get_data_quick_approach()
        else:
            print("'recipe' attibute can only accept 0 or 1.")
        return self.combined_data, self._combined_accuracy


# In[ ]:




