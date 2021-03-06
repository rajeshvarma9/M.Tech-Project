import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.cross_validation import train_test_split
from sklearn.preprocessing import scale
from sklearn.cross_validation import cross_val_score
from sklearn import metrics
from sklearn.naive_bayes import MultinomialNB
from sklearn.cross_validation import KFold
from sklearn.metrics.pairwise import euclidean_distances
from scipy.spatial import distance


#importing dataset and converting to datasframe
data = pd.read_csv('C:/Users/Welcome/Documents/Desktop/statlog.csv', header=None)
df = pd.DataFrame(data) #data frame


FP = 0
FN = 0
TN = 0
TP = 0

#def split_list(a_list):
   # half = int(len(a_list)/2)
   # return a_list[:half], a_list[half:]

def chunkIt(seq, num):
    avg = len(seq) / float(num)
    out = []
    last = 0.0

    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg

    return out

def nbkmh(train_index, test_index):
    dataPtx=[]
    dataPty=[]
    dataPtz=[]
    clusters = 2
    
    Centroid=[]
    #parts=[]
	#extracting columns x and y separately for kmeans and naive bayes classifiers
    x_kmeans = df.iloc[:,0:5]
    x_kmeans = x_kmeans.drop(x_kmeans.columns[1:3], axis=1)
    # x_kmeans = x_kmeans.drop(x_kmeans.columns[2], axis=1)
    x_kmeans = pd.DataFrame(scale(x_kmeans))
    
    x_naive = df.iloc[:,0:13]
    y = df.iloc[:,13]
    #y = pd.to_numeric(y)-1
    y_train = pd.Series(y.iloc[train_index])
    y_test = pd.Series(y.iloc[test_index])
    x_train_kmeans = x_kmeans.iloc[train_index, :]
    x_test_kmeans = x_kmeans.iloc[test_index, :]
    x_train_naive = x_naive.iloc[train_index, :]
    x_test_naive = x_naive.iloc[test_index, :]
    
    for index,row in x_kmeans.iterrows():
        dataPtx.append(row[0])
        dataPty.append(row[1])
        dataPtz.append(row[2])
    for i in range(clusters):
         xc=((max(dataPtx)-min(dataPtx))/clusters)*(i+1)
         yc=((max(dataPty)-min(dataPty))/clusters)*(i+1)
         zc=((max(dataPtz)-min(dataPtz))/clusters)*(i+1)
         ct=(xc,yc,zc)
         Centroid.append(ct)
    Centroid=np.asarray(Centroid)
        
    
    
    model_kmeans = KMeans(init=Centroid, n_clusters=clusters, n_init=1,random_state=10000)
    model_kmeans.fit(x_train_kmeans)
    kmean_predictions = model_kmeans.predict(x_train_kmeans)

	#building datset according to clusters
    x = [pd.DataFrame() for ii in range(0,clusters)]
    y = [pd.Series() for ii in range(0,clusters)]
    for kmean_prediction,i in zip(kmean_predictions, range(len(x_train_kmeans))):
        row_x =  x_train_naive.iloc[i, :]
        row_y = pd.Series(y_train.iloc[i])
        index = int(kmean_prediction)
        x[index] = x[index].append(row_x, ignore_index=True)
        y[index] = y[index].append(row_y)

	#applying naive bayes classifier
    clstr_n = [MultinomialNB(alpha=2,fit_prior=True) for ii in range(0,clusters)]
    for i in range(0,clusters):	
        clstr_n[i].fit(x[i], y[i])

	#calculating predictions for the testing based on the hybrid algorithm
    predicts = []
    c=0
    for i in range(len(x_test_kmeans)):	
        prediction = model_kmeans.predict(x_test_kmeans.iloc[i, :].reshape(1,-1))
        prediction = int(prediction)
        pred_naive = clstr_n[prediction].predict(x_test_naive.iloc[i, :].reshape(1,-1))
        predicts.append(pred_naive)
        if pred_naive == y_test.iloc[i]:
            c+=1
            
	# print ("Test set accuracy : ",  ((c*100.0)/len(x_test_kmeans)))
    print ((c*100.0)/len(x_test_kmeans))
	#metrics
    predicts = np.array(predicts)
    cm = metrics.confusion_matrix(y_test, predicts)/len(y_test)
	# print (cm)
    global FP
    global FN
    global TN
    global TP
    FP += cm[0][0]
    FN += cm[1][0]
    TN += cm[0][1]
    TP += cm[1][1]
    return ((c*100.0)/len(x_test_kmeans))

def main():
	scores = []
	kf = KFold(n=df.shape[0], n_folds=10)
	for (train_index,test_index),i in zip(kf,range(0,10)):
		print("Iteration " + str(i+1) + " : ")
		scores.append(nbkmh(train_index, test_index))
	print("\n 10 Fold Accuracy",np.array(scores).mean())
	print("FP", FP/10)
	print("FN", FN/10)
	print("TN", TN/10)
	print("TP", TP/10)


if __name__ == '__main__':
	main()
