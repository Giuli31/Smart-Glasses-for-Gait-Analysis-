import pandas as pd
from sklearn import datasets
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn import metrics
#import excel file
dataframe = pd.read_excel('training_data.xlsx', header=0, names = ["minX", "minY", "minZ", "maxX", "maxY", "maxZ", "varX", "varY", "varZ", "minAcc", "maxAcc", "varAcc", "tempo", "passi","target"])
X = dataframe.drop('target', axis = 1)
y = dataframe.target
#split train and test data: train data are used to train the model 75% while test data are used to test the model and asses its accuracy 25% of the data
X_train, X_test, y_train, y_test = train_test_split(X,y, test_size = 0.20, stratify=y,random_state = 1)
print("samples used for training: " + str(len(X_train)))
print ("samples used for testing: " + str(len(X_test)))
#Build Decision tree model classifier
from sklearn.tree import DecisionTreeClassifier
dtree_model = DecisionTreeClassifier(max_depth = None).fit(X_train, y_train)
#dtree_model.fit(X_train, y_train)
dtree_predictions = dtree_model.predict(X_test)
#model evaluation
accuracy = metrics.accuracy_score(y_test, dtree_predictions)
cm = confusion_matrix(y_test, dtree_predictions)
print(cm)
print("decision tree accuracy:  "+str(accuracy))
##  plot tree  ##
#from sklearn import tree
#tree.plot_tree(dtree_model)


