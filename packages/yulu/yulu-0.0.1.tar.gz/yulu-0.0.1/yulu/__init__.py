# Program 1: Data Preprocessing
def p1():
    return """
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import MinMaxScaler

diamond_data = pd.read_csv("D:\\Ms214419\\diamonds.csv")
print("\\n Before Preprocessing")
print("-----------------------")
print(diamond_data.head(50))
diamond_data['price'] = diamond_data['price'].fillna(diamond_data['price'].mean())
l = LabelEncoder()
diamond_data['cut'] = l.fit_transform(diamond_data['cut'])
n = MinMaxScaler(feature_range=(0, 1))
diamond_data['depth'] = n.fit_transform(diamond_data[['depth']])
print("\\n After preprocessing data")
print("---------------------------")
print("\\n 1. Replacing null values in price column with the mean")
print("\\n 2. Changing categorical data in the Cut column to numerical data")
print("\\n 3. Normalizing the Depth column to fit in the range[0,1]\\n\\n")
print(diamond_data.head(50))
print("--------------------------")
"""

# Program 2: KNN
def p2():
    return """
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn import metrics

diabetes_data = pd.read_csv("D:\\MS214419\\diabetes.csv")
features_cols = diabetes_data[['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI', 'Age']]
x = features_cols
y = diabetes_data['Outcome']

print("K Nearest Neighbors Classification")
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25)

model = KNeighborsClassifier(n_neighbors=5)
model.fit(x_train, y_train)
y_pred = model.predict(x_test)

df = pd.DataFrame({'Actual value': y_test, 'Predicted ': y_pred})
print(df.to_string())

cnf_matrix = metrics.confusion_matrix(y_test, y_pred)
accuracy = metrics.accuracy_score(y_test, y_pred)
precision = metrics.precision_score(y_test, y_pred)
recall = metrics.recall_score(y_test, y_pred)

print("Confusion Matrix: -")
print(cnf_matrix)
print("Accuracy: ", accuracy)
print("Precision: ", precision)
print("Recall : ", recall)
"""

# Program 3: Decision Tree
def p3():
    return """
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn import metrics

diabetes_data = pd.read_csv("D:\\MS214419\\diabetes.csv")
features_cols = diabetes_data[['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI', 'Age']]
x = features_cols
y = diabetes_data['Outcome']

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25)

model = DecisionTreeClassifier()
model.fit(x_train, y_train)
y_pred = model.predict(x_test)

df = pd.DataFrame({'Actual value': y_test, 'Predicted ': y_pred})
print(df.to_string())

cnf_matrix = metrics.confusion_matrix(y_test, y_pred)
accuracy = metrics.accuracy_score(y_test, y_pred)
precision = metrics.precision_score(y_test, y_pred)
recall = metrics.recall_score(y_test, y_pred)

print("Confusion Matrix: -")
print(cnf_matrix)
print("Accuracy: ", accuracy)
print("Precision: ", precision)
print("Recall : ", recall)
"""

# Program 4: Naive Bayes
def p4():
    return """
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn import metrics

diabetes_data = pd.read_csv("D:\\Ms214419\\diabetes.csv")
Featurecol = diabetes_data[['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI', 'Age']]
x = Featurecol
y = diabetes_data['Outcome']

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25)

model = GaussianNB()
model.fit(x_train, y_train)
y_pred = model.predict(x_test)

df = pd.DataFrame({'Actual': y_test, 'Predicted': y_pred})
print(df.to_string())

cnf_matrix = metrics.confusion_matrix(y_test, y_pred)
accuracy = metrics.accuracy_score(y_test, y_pred)
precision = metrics.precision_score(y_test, y_pred)
recall = metrics.recall_score(y_test, y_pred)

print("Confusion Matrix")
print(cnf_matrix)
print("Accuracy:", accuracy)
print("Precision:", precision)
print("Recall:", recall)
"""

# Usage:
# program_string = p1()  # Replace 'p1' with 'p2', 'p3', or 'p4' to get the corresponding program as a string.
# print(program_string)

print(p1())