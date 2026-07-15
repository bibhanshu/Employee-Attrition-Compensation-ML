
import numpy as np
import pandas as pd
import xgboost
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sqlalchemy import create_engine
import urllib
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from sklearn.neighbors import KNeighborsClassifier
import numpy as np

## Reading the Data from SQL :
params = urllib.parse.quote_plus(
    r"DRIVER={ODBC Driver 17 for SQL Server};"
    r"SERVER=DESKTOP-J1C95IE\SQLEXPRESS01;"
    r"DATABASE=EmployeeDB;"
    r"Trusted_Connection=yes;"
)

engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

df = pd.read_sql("SELECT * FROM employees_clean", engine)
print(df)
##keep and drop
Y = df['left_company']
X = df.drop(columns=['employee_id', 'name', 'left_company'])

## Hot Encoding as 2 columns are having strings as values
X_encoding = pd.get_dummies(X, columns=['department', 'job_role'], drop_first=True)
pd.set_option('display.max_columns', None)
#print(X_encoding.head())
X_encoding_train,X_encoding_test,Y_train,Y_test = train_test_split(X_encoding,Y,test_size=0.3,random_state=7)

##LogisticRegression
Model_LoggRegg =LogisticRegression(class_weight='balanced')
Model_LoggRegg.fit(X_encoding_train,Y_train)
Pred_LoggRegg = Model_LoggRegg.predict(X_encoding_test)
print("Actual")
print(Y_test[:10].values)
print("Predicted LogisticRegression")
print(Pred_LoggRegg[:10])
print('Accuracy Score', accuracy_score(Y_test,Pred_LoggRegg)) ##0.68

#determine whether your model is learning properly, overfitting, or underfitting
predicted_train_LoggRegg = Model_LoggRegg.predict(X_encoding_train) ## predicting from Data learned from
print('LoggRegg Train Accuracy', accuracy_score(Y_train,predicted_train_LoggRegg)) ##compares actual with learned predicted
print('LoggRegg Test Accuracy', accuracy_score(Y_test,Pred_LoggRegg)) ## test accuracy

#classification_report
print(classification_report(Y_test, Pred_LoggRegg))
##1 _ accuracy - 0.49 that is 49% bad model performance
##2-Support - False 102 , true 48 --Dataset have more false than true
##3-Recall - False 0.48 , true 0.50, out of all actual false my model predicted only 48% correct
# and out of all actual true my model predicted only 50% true --- BAD
##4 - Precession - Flase 0.67, true 0.31(after using blanced class) when Model predicts 67% of false
# is correct which is understandable as large chunk of data is false and true is just 31%
#over all Logg regression is abit below oky and a bit above bad ! we need random forest

##Random Forest
Model_Random_Forest = RandomForestClassifier(random_state=42, class_weight='balanced')
Model_Random_Forest.fit(X_encoding_train,Y_train)
Pred_Random_Forest = Model_Random_Forest.predict(X_encoding_test)
print(' Random Forest Accuracy Score : ', accuracy_score(Y_test,Pred_Random_Forest)) ##0.68
predicted_train_random_forest  = Model_Random_Forest.predict(X_encoding_train)
print('Random Forest Train Accuracy :', accuracy_score(Y_train,predicted_train_random_forest) ) ##1.00
print('Random Forest Test Accuracy :', accuracy_score(Y_test,Pred_Random_Forest)) ##0.68

#classification_report
print(classification_report(Y_test, Pred_Random_Forest))

##Random forest Accuracy score 0.68 similar to logg regression
#train accuracy 100% means if we ask question on data it traied its able to ans 100% but in test its 60%
#While Logg regression training was 59% and test was 49% ... I see progress here !!
#Now about classification report :
#Accuracy is 0.68 better that Logg reggression but still lagging or poor model
#Support  False is 102  true 48 similar as this is a fact that 102 are false and 48 are true
#recall Most imp 98% false and just 4% true for false its working good but for true is bad its
#like just the model that predicts false most of the time and trying to win
#pressision false 68% and true 50%
#When Model Predicts False 68% its correct and when it predicts truw 50% its correct  Still bad for true
#F1 - over all score for each class False is good 81% true is just 8%  bad

#we need True to be strong as thats the most imp thing we are looking for we are intrested to know who will leave and there model fails
#This is where I have not use class_weight='balanced' after that it will improve a bit but not wonders this looks like XGB can do wonders here lets seeeeee

##GB
Model_GB = GradientBoostingClassifier(
    n_estimators=400,
    learning_rate=0.05,
    max_depth=5,
    random_state=42,
)
Model_GB.fit(X_encoding_train,Y_train)
Pred_GB = Model_GB.predict(X_encoding_test)
print("Actual")
print(Y_test[:10].values)
print("Predicted")
print(Pred_GB[:10])
print(' GB Accuracy Score : ', accuracy_score(Y_test,Pred_GB)) ##0.68
predicted_train_GB  = Model_GB.predict(X_encoding_train)
print('GB Train Accuracy :', accuracy_score(Y_train,predicted_train_GB) ) ##1.00
print('GB Test Accuracy :', accuracy_score(Y_test,Pred_GB)) ##0.68

#classification_report
print(classification_report(Y_test, Pred_GB))
##Pattern is very clear now:
##All models stuck at 68% accuracy, True Recall consistently poor
##This is a data problem not a model problem — 500 rows with 28% minority class is genuinely hard

##XG boost
Value_counts = df['left_company'].value_counts() ## True 359 false 141
true_value_has_leftcompany = (df["left_company"] == True).sum()
false_value_presemt_in_company = (df["left_company"] == False).sum()
#print(true_value_has_leftcompany)
#print(false_value_presemt_in_company)

Model_XGB = XGBClassifier(
    n_estimators=300,
    learning_rate=0.05,
    max_depth=5,
    random_state=42,
    scale_pos_weight = false_value_presemt_in_company/true_value_has_leftcompany
)
Model_XGB.fit(X_encoding_train,Y_train)
Pred_XGB = Model_XGB.predict(X_encoding_test) ## this gives 1,0,1,0
Pred_XGB_bool = Pred_XGB.astype(bool) ##convert 1,0 to true ,false
print(' XGB Accuracy Score : ', accuracy_score(Y_test,Pred_XGB_bool)) ##59%
predicted_train_XGB  = Model_XGB.predict(X_encoding_train)
print('XGB Train Accuracy :', accuracy_score(Y_train,predicted_train_XGB ) ) ##99%
print('XGB Test Accuracy :', accuracy_score(Y_test,Pred_XGB_bool)) ##59%

#clasification report
print(classification_report(Y_test, Pred_XGB_bool))

##KNN
##we are checking multiple values of K to get the best :
for k in range(1,30):
    model_KNN = KNeighborsClassifier(
        n_neighbors=k,
        weights="uniform"
    )
    model_KNN.fit(X_encoding_train, Y_train)
    Pred_KNN = model_KNN.predict(X_encoding_test)
    print('When K is : ',k, 'Accuracy Score is :', accuracy_score(Y_test,Pred_KNN))
    ## Outcome K = 6 = 68%

model_KNN = KNeighborsClassifier(
    n_neighbors=6,
    weights="uniform",
    metric="minkowski",
)
model_KNN.fit(X_encoding_train,Y_train)
Pred_KNN = model_KNN.predict(X_encoding_test)
print('KNN Accuracy Score : ', accuracy_score(Y_test,Pred_KNN)) ##KNN Accuracy Score :  0.68
predicted_train_KNN  = model_KNN.predict(X_encoding_train)
print('KNN Train Accuracy :', accuracy_score(Y_train,predicted_train_KNN ) ) ##74%
print('KNN Test Accuracy :', accuracy_score(Y_test,Pred_KNN)) ##68%%

#clasification report
print(classification_report(Y_test, Pred_KNN))

## We will move forward with LR Balanced
##LR (balanced)49%48%0.38No

##Feature Imp:
imp_Logg_regg = np.abs(Model_LoggRegg.coef_[0])
feature_Logg_regg = X_encoding.columns
Feature_Importance_Logg_Regg = pd.DataFrame(
    {
        'Feature': feature_Logg_regg,
        'Importance': imp_Logg_regg
    }
).sort_values(by='Importance', ascending=False)
HR_Model_Features = Feature_Importance_Logg_Regg.head(10)
print(HR_Model_Features)

##Random Forest feature Imp
imp_RF = Model_Random_Forest.feature_importances_
Feature_Importance_RF = pd.DataFrame({
    'Feature': X_encoding.columns,
    'Importance': imp_RF
}).sort_values(by='Importance', ascending=False)
print(Feature_Importance_RF.head(10))

## Conclusion:
## - "Two stage approach" — one model for prediction, one for explanation!
#Model 1 — LR (balanced) for ALERTS
##"Flag these employees as flight risk"
##High Recall = catches more potential leavers
##HR can intervene early!

##Model 2 — Random Forest for INSIGHTS

##"Here's WHY employees are leaving"
##Feature importance = actionable insights
##Fix pay, reduce overwork, focus on HR dept!

#("Logistic Regression (balanced) selected as final classification model due to superior recall on minority "
 #"class — critical for HR intervention use case. Random Forest used for feature importance and business insights.")
