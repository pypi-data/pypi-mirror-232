import numpy as np
import pandas as pd
from typing import Union
import math
from dataclasses import dataclass
from typing import Literal
import matplotlib.pyplot as plt

def entropy(Y):
    unique_response={}
    total=Y.size
    for j in range(Y.size):
        if Y.iat[j] not in unique_response:    
            unique_response[Y.iat[j]]=1       
        else:
            unique_response[Y.iat[j]]+=1
    entropy=0
    for i in unique_response:
        probab=(unique_response[i]/total)
        entropy+=(-(probab)*np.log2(probab))
    return entropy



def gini_index(Y):
    unique_response={}
    total=Y.size
    for j in range(Y.size):
        if Y.iat[j] not in unique_response:    
            unique_response[Y.iat[j]]=1        
        else:
            unique_response[Y.iat[j]]+=1
    gini=0
    for i in unique_response:
        probab=(unique_response[i]/total)
        gini+=probab**2
    return gini

def information_gain(Y, attr):
    info_gain=entropy(Y)
    tot_size=Y.size
    weighted_attr={}
    for i in range(attr.size):
        if attr.iat[i] not in weighted_attr:
            weighted_attr[attr.iat[i]]=[Y.iat[i]]
        else:
            weighted_attr[attr.iat[i]].append(Y.iat[i])
    for i in weighted_attr:
        info_gain-=(len(weighted_attr[i])/tot_size)*entropy(pd.Series(weighted_attr[i]))
    return info_gain



def accuracy(y_hat, y):
    assert(y_hat.size == y.size)
    # TODO: Write here
    c=0
    for i in range(y.size):
        if y_hat.iloc[i]==y.iloc[i]:
            c+=1
    return c/y.size

def precision(y_hat: pd.Series, y: pd.Series, cls: Union[int, str]) -> float:
    assert y_hat.size == y.size
    c=0
    for i in range(y.size):
        if y.iloc[i]==y_hat.iloc[i] and y.iloc[i]==cls:
            c+=1
    return c/y_hat.value_counts()[cls]
        

def recall(y_hat: pd.Series, y: pd.Series, cls: Union[int, str]) -> float:
    assert y_hat.size == y.size
    c=0
    for i in range(y.size):
        if y.iloc[i]==y_hat.iloc[i] and y.iloc[i]==cls:
            c+=1
    return c/y.value_counts()[cls]

def rmse(y_hat: pd.Series, y: pd.Series) -> float:
    assert y_hat.size == y.size
    rms=0
    for i in range(y.size):
        rms+=math.pow(y_hat.iloc[i]-y.iloc[i],2)
    return math.sqrt(rms/y.size)

    

def mae(y_hat: pd.Series, y: pd.Series) -> float:
    assert y_hat.size == y.size
    m_ae=0
    for i in range(y.size):
        m_ae+=abs(y_hat.iloc[i]-y.iloc[i])
    return m_ae/y.size



np.random.seed(42)

@dataclass
class Node():
    def __init__(self):
        self.children = {}
        self.Split_Value = None
        self.attr_id = None
        self.value = None
        self.isLeaf = False
        self.isAttrCategory = False

class DecisionTree():
    criterion: Literal["information_gain", "gini_index"]  
    max_depth: int  
    
    def __init__(self, criterion, max_depth=None):
       
        self.criterion = criterion
        self.max_depth = max_depth
        self.head = None


    def fit_data(self,X,y,currdepth):

        Current_Node = Node()  

        attr_id = -1
        split_value = None
        optimal_measure = None
        if(y.dtype.name=="category"):
            """
            Classification Problem
            """
            classes = np.unique(y)
            if(classes.size==1):
                Current_Node.isLeaf, Current_Node.isAttrCategory, Current_Node.value = True, True, classes[0]
                return Current_Node
            if(self.max_depth!=None):
                if(self.max_depth==currdepth):
                    Current_Node.isLeaf, Current_Node.isAttrCategory, Current_Node.value = True, True, y.value_counts().idxmax()
                    return Current_Node
            if(len(X.columns)==0):
                Current_Node.isLeaf, Current_Node.isAttrCategory, Current_Node.value = True, True, y.value_counts().idxmax()
                return Current_Node

            for i in X.columns:
                X_attribute = X[i]

                if(X_attribute.dtype.name=="category"):
                    measure = None
                    if(self.criterion=="information_gain"):         
                        measure = information_gain(y,X_attribute)
                    else:                                           
                        classes_i = np.unique(X_attribute)
                        s = 0
                        for j in classes_i:
                            y_sub = pd.Series([y[k] for k in range(y.size) if X_attribute[k]==j])
                            s += y_sub.size*gini_index(y_sub)
                        measure = (s/X_attribute.size)
                    if(optimal_measure!=None):
                        if(optimal_measure<measure):
                            attr_id = i
                            optimal_measure = measure
                            split_value = None
                    else:
                        attr_id = i
                        optimal_measure = measure
                        split_value = None
                
                else:
                    X_attribute_sort = X_attribute.sort_values()
                    for j in range(X_attribute_sort.size-1):
                        curr_index = X_attribute_sort.index[j]
                        next_index = X_attribute_sort.index[j+1]
                        if(y[curr_index]!=y[next_index]):
                            measure = None
                            Split_Value = (X_attribute[curr_index]+X_attribute[next_index])/2
                            
                            if(self.criterion=="information_gain"):                 
                                temp_attr = pd.Series(X_attribute<=Split_Value)
                                measure = information_gain(y,temp_attr)
                            
                            else:                                                  
                                y_sub1 = pd.Series([y[k] for k in range(y.size) if X_attribute[k]<=Split_Value])
                                y_sub2 = pd.Series([y[k] for k in range(y.size) if X_attribute[k]>Split_Value])
                                measure = y_sub1.size*gini_index(y_sub1) + y_sub2.size*gini_index(y_sub2)
                                measure =  (measure/y.size)
                            if(optimal_measure!=None):
                                if(optimal_measure<measure):
                                    attr_id, optimal_measure, split_value = i, measure, Split_Value
                            else:
                                attr_id, optimal_measure, split_value = i, measure, Split_Value
        
        # Regression Problems
        else:
            if(self.max_depth!=None):
                if(self.max_depth==currdepth):
                    Current_Node.isLeaf, Current_Node.value = True, y.mean()
                    return Current_Node
            if(y.size==1):
                Current_Node.isLeaf, Current_Node.value = True, y[0]
                return Current_Node
            if(len(X.columns)==0):
                Current_Node.isLeaf, Current_Node.value = True, y.mean()
                return Current_Node

            for i in X.columns:
                X_attribute = X[i]
                if(X_attribute.dtype.name=="category"):
                    classes_i = np.unique(X_attribute)
                    measure = 0
                    for j in classes_i:
                        y_sub = pd.Series([y[k] for k in range(y.size) if X_attribute[k]==j])
                        measure += y_sub.size*np.var(y_sub)
                    if(optimal_measure!=None):
                        if(optimal_measure>measure):
                            optimal_measure, attr_id, split_value = measure, i, None
                    else:
                        optimal_measure, attr_id, split_value = measure, i, None
                
                else:
                    X_attribute_sort = X_attribute.sort_values()
                    for j in range(y.size-1):
                        curr_index = X_attribute_sort.index[j]
                        next_index = X_attribute_sort.index[j+1]
                        Split_Value = (X_attribute[curr_index]) + (X_attribute[next_index]) / 2

                        y_sub1 = pd.Series([y[k] for k in range(y.size) if X_attribute[k]<=Split_Value])
                        y_sub2 = pd.Series([y[k] for k in range(y.size) if X_attribute[k]>Split_Value])
                        measure = y_sub1.size*np.var(y_sub1) + y_sub2.size*np.var(y_sub2)
                        if(optimal_measure!=None):
                            if(optimal_measure>measure):
                                attr_id, optimal_measure, split_value = i, measure, Split_Value
                        else:
                            attr_id, optimal_measure, split_value = i, measure, Split_Value
        if(split_value==None): 
            Current_Node.isAttrCategory = True
            Current_Node.attr_id = attr_id
            classes = np.unique(X[attr_id])
            for j in classes:
                y_new = pd.Series([y[k] for k in range(y.size) if X[attr_id][k]==j], dtype=y.dtype)
                X_new = X[X[attr_id]==j].reset_index().drop(['index',attr_id],axis=1)
                Current_Node.children[j] = self.fit_data(X_new, y_new, currdepth+1)
        
        else:
            Current_Node.attr_id = attr_id
            Current_Node.Split_Value = split_value
            y_new1 = pd.Series([y[k] for k in range(y.size) if X[attr_id][k]<=split_value], dtype=y.dtype)
            X_new1 = X[X[attr_id]<=split_value].reset_index().drop(['index'],axis=1)
            y_new2 = pd.Series([y[k] for k in range(y.size) if X[attr_id][k]>split_value], dtype=y.dtype)
            X_new2 = X[X[attr_id]>split_value].reset_index().drop(['index'],axis=1)
            Current_Node.children["lessThan"] = self.fit_data(X_new1, y_new1, currdepth+1)
            Current_Node.children["greaterThan"] = self.fit_data(X_new2, y_new2, currdepth+1)
        
        return Current_Node


    def fit(self, X, y):
        assert(y.size>0)
        assert(X.shape[0]==y.size)
        self.head = self.fit_data(X,y,0)


    def predict(self, X):
        y_hat = []                  
        for i in range(X.shape[0]):
            X_Sample = X.iloc[i,:]          
            head = self.head
            while(not head.isLeaf):                            
                if(head.isAttrCategory):                       
                    head = head.children[X_Sample[head.attr_id]]
                else:                                      
                    if(X_Sample[head.attr_id]<=head.Split_Value):
                        head = head.children["lessThan"]
                    else:
                        head = head.children["greaterThan"]
            
            y_hat.append(head.value) 
        y_hat = pd.Series(y_hat)
        return y_hat


    def plotTree(self, root, depth):
        if(root.isLeaf):
            if(root.isAttrCategory):
                return "Class "+str(root.value)
            else:
                return "Value "+str(root.value)

        s = ""
        if(root.isAttrCategory):
            for i in root.children.keys():
                s += "?("+str(root.attr_id)+" == "+str(i)+")\n" 
                s += "\t"*(depth+1)
                s += str(self.plotTree(root.children[i], depth+1)).rstrip("\n") + "\n"
                s += "\t"*(depth)
            s = s.rstrip("\t")
        else:
            s += "?("+str(root.attr_id)+" <= "+str(root.Split_Value)+")\n"
            s += "\t"*(depth+1)
            s += "Y: " + str(self.plotTree(root.children["lessThan"], depth+1)).rstrip("\n") + "\n"
            s += "\t"*(depth+1)
            s += "N: " + str(self.plotTree(root.children["greaterThan"], depth+1)).rstrip("\n") + "\n"
        
        return s
           

    def plot(self):
        head = self.head
        tree = self.plotTree(head,0)
        print(tree)


def train_decision_tree(X, y, criterion='information_gain', max_depth=None):
    tree = DecisionTree(criterion=criterion, max_depth=max_depth)
    tree.fit(X, y)
    return tree

def evaluate_decision_tree(tree, X, y):
    y_hat = tree.predict(X)
    metrics = {
        'Accuracy': accuracy(y_hat, y),
        'Precision': {cls: precision(y_hat, y, cls) for cls in y.unique()},
        'Recall': {cls: recall(y_hat, y, cls) for cls in y.unique()},
        'RMSE': rmse(y_hat, y),
        'MAE': mae(y_hat, y),
    }
    return metrics



