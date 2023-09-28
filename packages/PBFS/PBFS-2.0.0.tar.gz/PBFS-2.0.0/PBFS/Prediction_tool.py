#Importing required libraries

#Pandas for dataframe operations
import pandas as pd
#Importing label Encoder
from sklearn.preprocessing import LabelEncoder
#Import resources to access files as a library
from importlib import resources
#Import h5py
import h5py
#Import io
import io
#Numpy for array operations
import numpy as np
# Import sequential from keras for neural network
from keras.models import Sequential
# Import dense from keras for neural network
from keras.layers import Dense
#Train Test import from Scikit-learn
from sklearn.model_selection import train_test_split
#import joblib
import joblib
# Linear regression import from Scikit-learn
from sklearn.linear_model import LinearRegression
#Metrics Import from Sklearn
import sklearn.metrics as met
# Import tensorflow for neural network
import tensorflow as tf
#Import warning to ignore specific warnings
import warnings

#Import OS for Excel operations
import os
#Import datetime for getting system date and time
import datetime
from keras import utils as ut
from keras.utils import to_categorical


#Function to handle numerical and categorical columns of the dataset
def handle_columns(df, continuous_threshold=0.05, categorical_threshold=0.05):
    """
    This function handles columns as numerical or categorical type.
    Function input -  * - mandatory
    df * -- Dataframe name
    continuous_threshold = 0.05 (default), threshold to determine 
                            whether a column is continuous or not
    categorical_threshold = 0.05 (default), Threshold to determine 
                            whether a column is categorical or not
    
    Function takes input of a dataframe and computes the ratio of 
    unique values to total values. Using this ratio and threshold, 
    it classifies every column of the dataframe as numerical or categorical. 
    May have bugs.
    This function is useful as when reading data from any flatfile/excel 
    file, the column datatypes may be read wrong
    
    *** Ensure there is no overlap between the 2 given thresholds. 
    0 <categorical_threshold < continuous_threshold < 1 - 
    Follow this rule always ***
    If there is overlap, columns may not be classified as expected.
    
    Examples:
    happiness = read_excel("Happiness_report_2015.xlsx)
    happiness = handle_columns(happiness)
    print(happiness.info())
    
    stroke = read_excel("Stroke_prediction_v1.xlsx)
    stoke = handle_columns(stroke_prediction, continuous_threshold = 0.06, 
    categorical_threshold = 0.04)
    print(stroke.info())
    """

    continuous_columns = []
    categorical_columns = []

    for col in df.columns:
        unique_ratio = df[col].nunique() / len(df)
        if (unique_ratio > continuous_threshold) and df[col].dtypes !='object':
            continuous_columns.append(col)
            #print("col : " + str(col) + " ratio : " + str(unique_ratio) + " continuous")
        elif (0 < unique_ratio <= categorical_threshold) or df[col].dtypes == 'object':
            categorical_columns.append(col)
            #print("col : " + str(col) + " ratio : " + str(unique_ratio) + " categorical")

    #Factorise columns to encode them into numerical values.
    df[categorical_columns] = df[categorical_columns].apply(lambda x : pd.factorize(x, sort = True)[0])

    # Convert categorical columns to 'category' data type
    df[categorical_columns] = df[categorical_columns].astype('category')

    return df
#
#def load_nn_model(model_name):
#    # Open the .h5 model file using resources and io
#    with resources.open_binary('Models', model_name) as file:
#        # Wrap the file in h5py.File to read it
#        with h5py.File(file, 'r') as h5_file:
#            # Load the Keras model from the HDF5 file
#            model = h5_file.get(model_name)  # Replace 'model_name' with the actual model name/key
#            loaded_model = tf.keras.models.load_model(model)
#    return loaded_model
#

def load_nn_model(model_name):
    # Open the .h5 model file using resources and io
    with resources.open_binary('PBFS',model_name) as file:
        # Wrap the file in h5py.File to read it
        with h5py.File(io.BytesIO(file.read()), 'r') as h5_file:
            # Load the Keras model from the HDF5 file
            loaded_model = tf.keras.models.load_model(h5_file)
    return loaded_model



def predict_effect(df_in, outcome, model_in = LinearRegression(), type = 1,test_split = 0.2, random_st = 343, neural_net = 1, fname = 'feature_ranking', predict = 0):
    """ 
    # Predict effect function  -  
    This function will compute pre-requisite values for a dataset and predict the ranking of features against an outcome column.
    This function module takes input in following sequence , (*  - mandatory)

    *** Check Copyright details for usage permissions ***

        * df_in     - the input Data frame (df_in), 
        * outcome   - dependant/outcome variable (outcome),
        model_in    - The type of machine learning model. The ML model (model_in) (default = LinearRegression()) - can define any model before using. 
                        DO NOT TRAIN THE MODEL. Just build/create instance and input.
        * Type      - Type of prediction needed. Predict on regression data or Classification data.
                        Regression (default) = 1, Classification = 2.
        test_split  - defaulted to 20% of dataset size. 
        random_st   - defaulted to 343. (if you need to regenerate same results, use same random state)
        neural_net  - If model is neural network, please select 1 for field.
        *fname      - Filename for data to be dumped.
        predict     - Specific to neural network models. 0 - regression, 1 for binary classification, 2 for multiclass classification.

    # Description:
    It will calculate pre-requisites using the input dataframe and input model. 
    Here pre-requisites are referred to as column values which the predictive ML model will use to predict the ranking
    These are a set of performance-based columns depending on type of classification.
    Based on computed values and type of ML(regression or classification), 
    it will then predict the ranks of the features using pre-trained model and then produce feature ranking for the dataset.
    This is a prototype tool and not full-fledged.
    Code is still in development stage so may have bugs.

    # Examples to use :
    E.g., 1: input your dataset, create your model, call the predict effect function with relevant values.
    *PS: function call is not using Neural network
    stroke = pd.read_csv('healthcare-dataset-stroke-data.csv')
    rfclass = RandomForestClassifier(n_estimators=160, random_state=7632)
    predict_effect(stroke,'stroke',rfclass,type = 2,neural_net=0,fname = 'feature_ranking_rf160_v1')

    E.g., 2:
    *PS: Function call is using inbuilt neural network model
    predict_effect(stroke,'stroke',type = 2,neural_net=1,fname = 'feature_ranking_rf160_v3', predict = 1)
    """


    #Defining start time to record runtime of function
    start_time = datetime.datetime.now()
    print("------------------------------------------------------------------------------------------------------")
    print("Effect Prediction Call Initiated. Time : " + str(start_time))

    #check if column present in dataframe; if not break and exit function
    if outcome not in df_in:
        print("Outcome column : '" + str(outcome) + "' is not present in input Dataframe.\nPlease input correct value of Outcome column")
        return
    
    #Defining pre-requisite dataframe structure which will be used to predict the ranks
    reg_prereq = pd.DataFrame(columns=['ML_Model', 'Outcome_col','missing_feature', 'Column_type', 
                                       'Category_count', 'row_count', 'subset_size_variance',
                                       'R2_Subset_var', 'MSE_Subset_var', 'MAE_Subset_var',
                                       'RMSE_Subset_var', 'EVS_Subset_var', 'MSLE_Subset_var',
                                       'Test_split', 'Random_state_split'])

    cls_prereq = pd.DataFrame(columns=['ML_Model', 'Outcome_col','missing_feature', 'Column_type', 
                                        'Category_count', 'row_count', 'subset_size_variance',
                                        'ACC_Subset_var', 'PRE_Subset_var', 'REC_Subset_var',
                                        'F1_Subset_var', 'AUC-ROC_Subset_var', 'CEL_Subset_var',
                                       'Test_split', 'Random_state_split'])

    #drops all NAN with rows
    df_in = df_in.dropna(axis = 0)
    df = df_in

    #Ignores all warnings.
    warnings.simplefilter('ignore')
    
    #Handles categorical and continuous variables and updates the original dataframe.
    df_in = handle_columns(df_in)

    #pre-processing by getting column related information except Outcome column
    all_cols = list(df_in.loc[:,df_in.columns != outcome])
    dtype_cols = list(df_in.loc[:,df_in.columns != outcome].dtypes)

    columns_info = pd.DataFrame({'Columns' : all_cols, 'Datatypes': dtype_cols})

    if type == 1: #Regression dataset prediction
        #itrates over all columns except the outcome column
        for ind, row in columns_info.iterrows():
            r2 = []
            mse = []
            mae = []
            rmse = []
            evs = []
            msle = []

            #Pre-processing for with and without missing feature testing.
            X_without = df_in.drop(columns = [row['Columns'],outcome]).values
            X_with = df_in.drop(columns = [outcome]).values
            y = df_in[outcome].values
            if neural_net == 1 and predict ==2:
                y = to_categorical(y)
            else:
                y = y.reshape(-1,1)


            #model with missing feature
            X_train, X_test, y_train, y_test = train_test_split(X_with, y, test_size= test_split, random_state= random_st)
            #Handling neural network requirements with the missing feature
            if neural_net == 1:
                model_in, model_str = neural_network_build(df_in, X_train, y_train, row['Columns'], predict = predict)
                model_in.fit(X_train, y_train, verbose = 0)
                y_pred_with = model_in.predict(X_test, verbose = 0)
            else:
                model_in.fit(X_train, y_train)
                y_pred_with = model_in.predict(X_test)

            #Computing initial pre-requisites
            r2_with = round(met.r2_score(y_test,  y_pred_with)*100,3)
            mse_with = round(met.mean_squared_error(y_test,y_pred_with),3)
            mae_with = round(met.mean_absolute_error(y_test,y_pred_with),3)
            rmse_with = round(np.sqrt(mse_with),3)
            evs_with = round(met.explained_variance_score(y_test,y_pred_with),3)
            try:
                msle_with = round(met.mean_squared_log_error(abs(y_test),abs(y_pred_with)),3)
            except TypeError:
                msle_with = round(met.mean_squared_log_error(y_test,y_pred_with),3)

            #model without missing feature
            X_train, X_test, y_train, y_test = train_test_split(X_without, y, test_size= test_split, random_state= random_st)
            #Handling neural network requirements without the missing feature
            if neural_net == 1:
                model_in, model_str = neural_network_build(df_in, X_train, y_train, row['Columns'],predict = predict)
                model_in.fit(X_train, y_train, verbose = 0)
                y_pred_without = model_in.predict(X_test, verbose = 0)
            else:
                model_in.fit(X_train, y_train)
                y_pred_without = model_in.predict(X_test)

            # Computing initial pre-requisites
            r2_without = round(met.r2_score(y_test,  y_pred_without)*100,3)
            mse_without = round(met.mean_squared_error(y_test,y_pred_without),3)
            mae_without = round(met.mean_absolute_error(y_test,y_pred_without),3)
            rmse_without = round(np.sqrt(mse_without),3)
            evs_without = round(met.explained_variance_score(y_test,y_pred_without),3)
            try:
                msle_without = round(met.mean_squared_log_error(abs(y_test),abs(y_pred_without)),3)
            except TypeError:
                msle_without = round(met.mean_squared_log_error(y_test,y_pred_without),3)
            
            # Computing intermediate pre-requisites
            r2.append(r2_with)
            r2.append(r2_without)

            mse.append(mse_with)
            mse.append(mse_without)

            mae.append(mae_with)
            mae.append(mae_without)

            rmse.append(rmse_with)
            rmse.append(rmse_without)

            evs.append(evs_with)
            evs.append(evs_without)

            msle.append(msle_with)
            msle.append(msle_without)

            r2_var = np.abs(np.std(r2)/np.mean(r2))
            mse_var = np.abs(np.std(mse)/np.mean(mse))
            mae_var = np.abs(np.std(mae)/np.mean(mae))
            rmse_var = np.abs(np.std(rmse)/np.mean(rmse))
            evs_var = np.abs(np.std(evs)/np.mean(evs))
            msle_var = np.abs(np.std(msle)/np.mean(msle))

            #compute row count
            row_count = len(df)
            #compute distinct values count
            cat_count = len(list(df[row['Columns']].unique()))         

            # Computing initial pre-requisites for numerical type columns of dataframe
            if (row['Datatypes'] == 'int64') or (row['Datatypes'] == 'float64'):

                column_type = 'Numerical'
                #Initialising lists and other variables.
                r2_list = []
                mse_list = []
                mae_list = []
                rmse_list = []
                evs_list = []
                msle_list = []
                subset = []
                subset_size = []
                i = 0

                #Sort based on missing feature column
                df = df.sort_values(row['Columns'])
                
                #making 10 chunks for subsets
                chunk_size = 10
                
                #Splitting dataset in 10 chunks
                split_labels = pd.qcut(df[row['Columns']], chunk_size, labels=False, duplicates='drop')

                # Computing initial pre-requisites
                for sub_label in range(chunk_size):

                    chunk = df[split_labels == sub_label]
                    sub_size = len(chunk)

                    if sub_size != 0:

                        Xsub_test = chunk.drop(columns = [row['Columns'], outcome]).values
                        ysub_test = chunk[outcome].values
                        ysub_test = ysub_test.reshape(-1,1)
                        if neural_net == 1:
                            ysub_pred = model_in.predict(Xsub_test, verbose = 0)
                        else:
                            ysub_pred = model_in.predict(Xsub_test)

                        r2_sub = round(met.r2_score(ysub_test,  ysub_pred)*100,3)
                        mse_sub = round(met.mean_squared_error(ysub_test,  ysub_pred)*100,3)
                        mae_sub = round(met.mean_absolute_error(ysub_test,  ysub_pred)*100,3)
                        rmse_sub = round(np.sqrt(mse_sub),3)
                        evs_sub = round(met.explained_variance_score(ysub_test,  ysub_pred)*100,3)
                        try:
                            msle_sub = round(met.mean_squared_log_error(abs(ysub_test), abs(ysub_pred))*100,3)
                        except:
                            msle_sub = round(met.mean_squared_log_error(ysub_test, ysub_pred)*100,3)
                            
                        #Storing initial pre-requisites temporarily
                        r2_list.append(r2_sub)
                        mse_list.append(mse_sub)
                        mae_list.append(mae_sub)
                        rmse_list.append(rmse_sub)
                        evs_list.append(evs_sub)
                        msle_list.append(msle_sub)

                        subset.append(i)
                        i = i + 1
                        subset_size.append(sub_size)

                # Computing final pre-requisites
                r2_svar = np.abs(np.std(r2_list)/np.mean(r2_list))
                mse_svar = np.abs(np.std(mse_list)/np.mean(mse_list))
                mae_svar = np.abs(np.std(mae_list)/np.mean(mae_list))
                rmse_svar = np.abs(np.std(rmse_list)/np.mean(rmse_list))
                evs_svar = np.abs(np.std(evs_list)/np.mean(evs_list))
                msle_svar = np.abs(np.std(msle_list)/np.mean(msle_list))

                subset_size_var = np.std(subset_size)/np.mean(subset_size)
                
            # Computing initial pre-requisites for Categorical type columns of dataframe
            elif (row['Datatypes'] == 'O') or (row['Datatypes'] == 'c' or row['Datatypes'] == 'object') or (row['Datatypes'] == 'category'):

                column_type = 'Categorical'
                #Declaring variables.
                object_list = list(df[row['Columns']].unique())

                #Initialising lists and other variables.
                r2_list = []
                mse_list = []
                mae_list = []
                rmse_list = []
                evs_list = []
                msle_list = []
                subset = []
                subset_size = []

                #loop to perform testing on subsets of object/categorical variables.
                for index, val in enumerate(object_list):
                    Xsub = df[df[row['Columns']] == val]
                    sub_size = len(df[df[row['Columns']]==val])
                    Xsub_test = Xsub.drop(columns = [row['Columns'],outcome]).values
                    ysub_test = Xsub[outcome].values
                    ysub_test = ysub_test.reshape(-1,1)
                    if neural_net == 1:
                        ysub_pred = model_in.predict(Xsub_test, verbose = 0)
                    else:
                        ysub_pred = model_in.predict(Xsub_test)


                    r2_sub = round(met.r2_score(ysub_test,  ysub_pred)*100,3)
                    mse_sub = round(met.mean_squared_error(ysub_test,  ysub_pred)*100,3)
                    mae_sub = round(met.mean_absolute_error(ysub_test,  ysub_pred)*100,3)
                    rmse_sub = round(np.sqrt(mse_sub),3)
                    evs_sub = round(met.explained_variance_score(ysub_test,  ysub_pred)*100,3)
                    try:
                        msle_sub = round(met.mean_squared_log_error(abs(ysub_test),  abs(ysub_pred))*100,3)
                    except:
                        msle_sub = round(met.mean_squared_log_error(ysub_test,  ysub_pred)*100,3)
                    # Storing initial pre-requisites temporarily
                    r2_list.append(r2_sub)
                    mse_list.append(mse_sub)
                    mae_list.append(mae_sub)
                    rmse_list.append(rmse_sub)
                    evs_list.append(evs_sub)
                    msle_list.append(msle_sub)

                    subset.append(index)
                    subset_size.append(sub_size)

                #Computing final pre-requisites
                r2_svar = np.abs(np.std(r2_list)/np.mean(r2_list))
                mse_svar = np.abs(np.std(mse_list)/np.mean(mse_list))
                mae_svar = np.abs(np.std(mae_list)/np.mean(mae_list))
                rmse_svar = np.abs(np.std(rmse_list)/np.mean(rmse_list))
                evs_svar = np.abs(np.std(evs_list)/np.mean(evs_list))
                msle_svar = np.abs(np.std(msle_list)/np.mean(msle_list))    

                subset_size_var = np.std(subset_size)/np.mean(subset_size)


            if neural_net == 1:
                model_in = model_str

            #Populating data in regression dataframe for further use
            reg_prereq_row = [model_in,outcome,row['Columns'],column_type,
                                cat_count,row_count,subset_size_var,
                                r2_svar,mse_svar,mae_svar,rmse_svar,evs_svar,msle_svar,
                                test_split, random_st]
            reg_prereq.loc[len(reg_prereq)] = reg_prereq_row
            reg_prereq = reg_prereq.reset_index(drop = True)
    
    elif type == 2:#Classification Dataset prediction
        for ind, row in columns_info.iterrows():

            acc = []
            pre = []
            rec = []
            f1 = []
            aucroc = []
            cel = []


            #Pre-processing for with and without missing feature testing.
            X_without = df.drop(columns = [row['Columns'],outcome]).values
            X_with = df.drop(columns = [outcome]).values
            y = df[outcome].values
            y = y.reshape(-1,1)

            #Categorise labels for multiclass classification.
            if neural_net ==1 and predict ==2:
                y = to_categorical(y)
            elif neural_net ==1 and predict == 1:
                label_encoder = LabelEncoder()
                y = label_encoder.fit_transform(y)
            else:
                y = y.reshape(-1,1)

            #model with missing feature
            X_train, X_test, y_train, y_test = train_test_split(X_with, y, test_size= test_split, random_state= random_st)

            # Handling neural network requirements with missing feature
            if neural_net == 1:
                model_in, model_str = neural_network_build(df_in,X_train,y_train,outcome, predict = predict)
                model_in.fit(X_train, y_train, verbose = 0)
                y_pred_with = np.argmax(model_in.predict(X_test, verbose = 0), axis = 1)
                y_pred_with_proba = model_in.predict(X_test, verbose = 0)
                y_test_proba = y_test
                y_test = np.argmax(y_test, axis = 1)
                try:
                    acc_with = round(met.accuracy_score(y_test,  y_pred_with)*100,3)
                except ValueError:
                    acc_with = 0
                try:
                    pre_with = round(met.precision_score(y_test,y_pred_with, average = 'weighted'),3)
                except ValueError:
                    pre_with = 0
                try:
                    rec_with = round(met.recall_score(y_test,y_pred_with, average = 'weighted'),3)
                except ValueError:
                    rec_with = 0
                try:
                    f1_with = round(met.f1_score(y_test,y_pred_with, average = 'weighted'),3)
                except ValueError:
                    f1_with = 0
                try:
                    aucroc_with =round(met.average_precision_score(y_test_proba,y_pred_with_proba, average = 'macro'),3)
                except ValueError:
                    aucroc_with = 0
                try:
                    cel_with = round(met.log_loss(abs(y_test_proba),abs(y_pred_with_proba)),3)
                except ValueError:
                    cel_with = 0

            else:
                model_in.fit(X_train, y_train)
                y_pred_with = model_in.predict(X_test)
                y_pred_proba_with = model_in.predict_proba(X_test)

                try:
                    acc_with = round(met.accuracy_score(y_test,  y_pred_with)*100,3)
                except ValueError:
                    acc_with = 0
                try:
                    pre_with = round(met.precision_score(y_test,y_pred_with),3)
                except ValueError:
                    pre_with = 0
                try:
                    rec_with = round(met.recall_score(y_test,y_pred_with),3)
                except ValueError:
                    rec_with = 0
                try:
                    f1_with = round(met.f1_score(y_test,y_pred_proba_with),3)
                except ValueError:
                    f1_with = 0
                try:
                    aucroc_with = round(met.roc_auc_score(y_test,y_pred_proba_with[:,-1]),3)
                except ValueError:
                    aucroc_with = 0
                try:
                    cel_with = round(met.log_loss(y_test,y_pred_with),3)
                except ValueError:
                    cel_with = 0

            #model without missing feature
            X_train, X_test, y_train, y_test = train_test_split(X_without, y, test_size= test_split, random_state= random_st)
            # Handling neural network requirements without missing feature
            if neural_net == 1:
                model_in, model_str = neural_network_build(df_in,X_train,y_train,outcome, predict = predict)
                model_in.fit(X_train, y_train, verbose = 0)
                y_pred_without = np.argmax(model_in.predict(X_test, verbose = 0), axis = 1)
                y_pred_without_proba = model_in.predict(X_test, verbose = 0)
                y_test_proba = y_test
                y_test = np.argmax(y_test,axis = 1)

                try:
                    acc_without = round(met.accuracy_score(y_test,y_pred_without)*100,3)
                except ValueError:
                    acc_without = 0
                try:
                    pre_without = round(met.precision_score(y_test,y_pred_without, average = 'weighted'),3)
                except ValueError:
                    pre_without = 0
                try:
                    rec_without = round(met.recall_score(y_test,y_pred_without, average = 'weighted'),3)
                except ValueError:
                    rec_without = 0
                try:
                    f1_without = round(met.f1_score(y_test,y_pred_without, average = 'weighted'),3)
                except ValueError:
                    f1_without = 0
                try:
                    aucroc_without = round(met.average_precision_score(y_test_proba,y_pred_without_proba, average = 'macro'),3)
                except ValueError:
                    aucroc_without = 0
                try:
                    cel_without = round(met.log_loss(abs(y_test),abs(y_pred_without_proba)),3)
                except ValueError:
                    cel_without = 0

            else:
                model_in.fit(X_train, y_train)
                y_pred_without = model_in.predict(X_test)
                y_pred_proba_without = model_in.predict_proba(X_test)     

                try:
                    acc_without = round(met.accuracy_score(y_test,y_pred_without)*100,3)
                except ValueError:
                    acc_without = 0
                try:
                    pre_without = round(met.precision_score(y_test,y_pred_without),3)
                except ValueError:
                    pre_without = 0
                try:
                    rec_without = round(met.recall_score(y_test,y_pred_without),3)
                except ValueError:
                    rec_without = 0
                try:
                    f1_without = round(met.f1_score(y_test,y_pred_proba_without),3)
                except ValueError:
                    f1_without = 0    
                try:
                    aucroc_without = round(met.roc_auc_score(y_test,y_pred_proba_without[:,-1]),3)
                except ValueError:
                    aucroc_without = 0
                try:
                    cel_without = round(met.log_loss(y_test,y_pred_without),3)
                except ValueError:
                    cel_without = 0

            #Storing initial pre-requsities temporarily
            acc.append(acc_with)
            acc.append(acc_without)

            pre.append(pre_with)
            pre.append(pre_without)

            rec.append(rec_with)
            rec.append(rec_without)

            f1.append(f1_with)
            f1.append(f1_without)

            aucroc.append(aucroc_with)
            aucroc.append(aucroc_without)

            cel.append(cel_with)
            cel.append(cel_without)


            acc_var = np.abs(np.std(acc)/np.mean(acc))
            pre_var = np.abs(np.std(pre)/np.mean(pre))
            rec_var = np.abs(np.std(rec)/np.mean(rec))
            f1_var = np.abs(np.std(f1)/np.mean(f1))
            aucroc_var = np.abs(np.std(aucroc)/np.mean(aucroc))
            cel_var = np.abs(np.std(cel)/np.mean(cel))

            #compute row count
            row_count = len(df)
            #compute distinct values count
            cat_count = len(list(df[row['Columns']].unique()))         

            # Computing initial pre-requisites for Numerical type columns of dataframe
            if (row['Datatypes'] == 'int64') or (row['Datatypes'] == 'float64'):

                column_type = 'Numerical'
                #Initialising lists and other variables.
                acc_list = []
                pre_list = []
                rec_list = []
                f1_list = []
                aucroc_list = []
                cel_list = []
                subset = []
                subset_size = []
                i = 0

                #Sort based on missing feature column
                df = df.sort_values(row['Columns'])
                
                #number of subsets
                chunk_size = 10

                #Splits entire df in 10 chunks of same size.
                split_labels = pd.qcut(df[row['Columns']], chunk_size, labels=False, duplicates='drop')

                for sub_label in range(chunk_size):

                    chunk = df[split_labels == sub_label]
                    sub_size = len(chunk)

                    if sub_size !=0:
                        Xsub_test = chunk.drop(columns = [row['Columns'], outcome]).values
                        ysub_test = chunk[outcome].values
                        if predict ==2:
                            ysub_test = to_categorical(ysub_test)
                        else:
                            ysub_test = ysub_test.reshape(-1,1)

                        if neural_net == 1:
                            ysub_pred = np.argmax(model_in.predict(Xsub_test, verbose = 0), axis = 1)
                            ysub_pred_proba = model_in.predict(Xsub_test, verbose = 0)
                            ysub_test_proba = ysub_test
                            ysub_test = np.argmax(ysub_test, axis = 1)

                            try:
                                acc_sub = round(met.accuracy_score(ysub_test,  ysub_pred)*100,3)
                            except ValueError:
                                acc_sub = 0
                            try:
                                pre_sub = round(met.precision_score(ysub_test,  ysub_pred, average = 'weighted')*100,3)
                            except ValueError:
                                pre_sub = 0
                            try:
                                rec_sub = round(met.recall_score(ysub_test,  ysub_pred, average = 'weighted')*100,3)
                            except ValueError:
                                rec_sub = 0
                            try:
                                f1_sub = round(met.f1_score(ysub_test,ysub_pred, average = 'weighted'),3)
                            except ValueError:
                                f1_sub = 0
                            try:
                                aucroc_sub = round(met.average_precision_score(ysub_test_proba,ysub_pred_proba, average = 'macro'),3)
                            except ValueError:    
                                aucroc_sub = 0
                            try:
                                cel_sub = round(met.log_loss(abs(ysub_test),abs(ysub_pred_proba)),3)
                            except ValueError:
                                cel_sub = 0

                        else:
                            ysub_pred = model_in.predict(Xsub_test)
                            ysub_pred_proba = model_in.predict_proba(Xsub_test)

                            try:
                                acc_sub = round(met.accuracy_score(ysub_test,  ysub_pred)*100,3)
                            except ValueError:
                                acc_sub = 0
                            try:
                                pre_sub = round(met.precision_score(ysub_test,  ysub_pred)*100,3)
                            except ValueError:
                                pre_sub = 0
                            try:
                                rec_sub = round(met.recall_score(ysub_test,  ysub_pred)*100,3)
                            except ValueError:
                                rec_sub = 0
                            try:
                                f1_sub = round(met.f1_score(ysub_test,ysub_pred_proba),3)
                            except ValueError:
                                f1_sub = 0
                            try:
                                aucroc_sub = round(met.roc_auc_score(ysub_test,ysub_pred_proba[:,-1]),3)
                            except ValueError:
                                aucroc_sub = 0
                            try:
                                cel_sub = round(met.log_loss(ysub_test,ysub_pred),3)
                            except ValueError:
                                cel_sub = 0

                        #Storing intermediate pre-requisites
                        acc_list.append(acc_sub)
                        pre_list.append(pre_sub)
                        rec_list.append(rec_sub)
                        f1_list.append(f1_sub)
                        aucroc_list.append(aucroc_sub)
                        cel_list.append(cel_sub)

                        subset.append(i)
                        i = i + 1
                        subset_size.append(sub_size)

                #Storing final pre-requisites
                acc_svar = np.abs(np.std(acc_list)/np.mean(acc_list))
                pre_svar = np.abs(np.std(pre_list)/np.mean(pre_list))
                rec_svar = np.abs(np.std(rec_list)/np.mean(rec_list))
                f1_svar = np.abs(np.std(f1_list)/np.mean(f1_list))
                aucroc_svar = np.abs(np.std(aucroc_list)/np.mean(aucroc_list))
                cel_svar = np.abs(np.std(cel_list)/np.mean(cel_list))

                subset_size_var = np.std(subset_size)/np.mean(subset_size)

            # Computing initial pre-requisites for Categorical type columns of dataframe
            elif (row['Datatypes'] == 'O') or (row['Datatypes'] == 'c' or row['Datatypes'] == 'object') or (row['Datatypes'] == 'category'):

                column_type = 'Categorical'
                #Declaring variables.
                object_list = list(df[row['Columns']].unique())

                #Initialising lists and other variables.
                acc_list = []
                pre_list = []
                rec_list = []
                f1_list = []
                aucroc_list = []
                cel_list = []
                subset = []
                subset_size = []

                #loop to perform testing on subsets of object/categorical variables.
                for index, val in enumerate(object_list):
                    Xsub = df[df[row['Columns']] == val]
                    sub_size = len(df[df[row['Columns']]==val])
                    Xsub_test = Xsub.drop(columns = [row['Columns'],outcome]).values
                    ysub_test = Xsub[outcome].values

                    #Handling requirements for multiclass clasification
                    if predict == 2:
                        ysub_test = to_categorical(ysub_test)
                    else:
                        ysub_test = ysub_test.reshape(-1,1)

                    if neural_net == 1:
                        ysub_pred = np.argmax(model_in.predict(Xsub_test, verbose = 0), axis = 1)
                        ysub_pred_proba = model_in.predict(Xsub_test, verbose = 0)
                        ysub_test_proba = ysub_test
                        ysub_test = np.argmax(ysub_test, axis = 1)

                        try:
                            acc_sub = round(met.accuracy_score(ysub_test,  ysub_pred)*100,3)
                        except ValueError:
                            acc_sub = 0
                        try:
                            pre_sub = round(met.precision_score(ysub_test,  ysub_pred, average = 'weighted')*100,3)
                        except ValueError:
                            pre_sub = 0
                        try:
                            rec_sub = round(met.recall_score(ysub_test,  ysub_pred, average = 'weighted')*100,3)
                        except ValueError:
                            rec_sub = 0
                        try:
                            f1_sub = round(met.f1_score(ysub_test,ysub_pred, average = 'weighted'),3)
                        except ValueError:
                            f1_sub = 0
                        try:
                            aucroc_sub = round(met.average_precision_score(ysub_test_proba,ysub_pred_proba, average = 'weighted'),3)
                        except ValueError:
                            aucroc_sub = 0
                        except IndexError:
                            aucroc_sub = 0

                        try:
                            cel_sub = round(met.log_loss(abs(ysub_test_proba),abs(ysub_pred_proba)),3)
                        except ValueError:
                            cel_sub = 0
                    else:
                        ysub_pred = model_in.predict(Xsub_test)
                        ysub_pred_proba = model_in.predict_proba(Xsub_test)

                        try:
                            acc_sub = round(met.accuracy_score(ysub_test,  ysub_pred)*100,3)
                        except ValueError:
                            acc_sub = 0
                        try:
                            pre_sub = round(met.precision_score(ysub_test,  ysub_pred)*100,3)
                        except ValueError:
                            pre_sub = 0
                        try:
                            rec_sub = round(met.recall_score(ysub_test,  ysub_pred)*100,3)
                        except ValueError:
                            rec_sub = 0
                        try:
                            f1_sub = round(met.f1_score(ysub_test,ysub_pred_proba),3)
                        except ValueError:
                            f1_sub = 0
                        try:
                            aucroc_sub = round(met.roc_auc_score(ysub_test,ysub_pred_proba[:,-1]),3)
                        except ValueError:
                            aucroc_sub = 0
                        try:
                            cel_sub = round(met.log_loss(ysub_test,ysub_pred),3)
                        except ValueError:
                            cel_sub = 0

                    #Storing intermediate pre-requisites
                    acc_list.append(acc_sub)
                    pre_list.append(pre_sub)
                    rec_list.append(rec_sub)
                    f1_list.append(f1_sub)
                    aucroc_list.append(aucroc_sub)
                    cel_list.append(cel_sub)

                    subset.append(index)
                    subset_size.append(sub_size)

                #Storing final pre-requisites
                acc_svar = np.abs(np.std(acc_list)/np.mean(acc_list))
                pre_svar = np.abs(np.std(pre_list)/np.mean(pre_list))
                rec_svar = np.abs(np.std(rec_list)/np.mean(rec_list))
                f1_svar = np.abs(np.std(f1_list)/np.mean(f1_list))
                aucroc_svar = np.abs(np.std(aucroc_list)/np.mean(aucroc_list))
                try:
                    cel_svar = np.abs(np.std(cel_list)/np.mean(cel_list))
                except ZeroDivisionError:
                    cel_svar = 0

                subset_size_var = np.std(subset_size)/np.mean(subset_size)

            if neural_net == 1:
                model_in = model_str
           
            # Populating data in classification dataframe for further use
            cls_prereq_row = [model_in, outcome, row['Columns'], column_type,
                              cat_count, row_count, subset_size_var,
                              acc_svar, pre_svar, rec_svar, f1_svar, aucroc_svar, cel_svar,
                              test_split, random_st]
            cls_prereq.loc[len(cls_prereq)] = cls_prereq_row
            cls_prereq = cls_prereq.reset_index(drop=True)


#----------------------------------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------------------------


    #Start here for prediction and output
    #==================================================================================================================

    if type ==1:#Regression prediction

        #Pre-trained regression prediction neural_network model
        reg_model ="neuralnetwork_Regress_model_39.999.h5"
        reg_trained_model = load_nn_model(reg_model)
        #tf.keras.models.load_model(reg_model)
        #joblib.load(reg_model)

        #handling data
        reg_prereq_upd = reg_prereq.fillna(0)
        reg_prereq_upd.replace([float('inf'), -float('inf')], 0)

        cat_columns = reg_prereq_upd.select_dtypes(['object', 'category']).columns
        reg_prereq_upd[cat_columns] = reg_prereq_upd[cat_columns].apply(lambda x: pd.factorize(x, sort=True)[0])

        #Predict output for feature ranking
        reg_predicted = reg_trained_model.predict(reg_prereq_upd, verbose =0)
        reg_prereq['predicted'] = reg_predicted

        #Group output for printing and publishing
        reg_prereq.sort_values(['predicted'], ascending=True, inplace=True)
        prediction = reg_prereq[['missing_feature','predicted']]
        prediction.columns = ['Features','Percentage change in RMSE']
        output = reg_prereq

    elif type ==2:#Classification prediction

        # Pre-trained classification prediction neural_network model
        cls_model = "neuralnetwork_Classify_model_13.91.h5"
        cls_trained_model = load_nn_model(cls_model)
        #tf.keras.models.load_model(cls_model)
        
        #Handling data
        cls_prereq_upd = cls_prereq.fillna(0)
        cls_prereq_upd.replace([float('inf'), -float('inf')], 0)
    
        cat_columns = cls_prereq_upd.select_dtypes(['object', 'category']).columns
        cls_prereq_upd[cat_columns] = cls_prereq_upd[cat_columns].apply(lambda x: pd.factorize(x, sort=True)[0])
        
        #Predict output for feature ranking    
        cls_predicted = cls_trained_model.predict(cls_prereq_upd, verbose = 0)
        cls_prereq['predicted'] = cls_predicted
        
        # Group output for printing and publishing
        cls_prereq.sort_values(['predicted'], ascending=False, inplace=True)
        prediction = cls_prereq[['missing_feature', 'predicted']]
        prediction.columns = ['Features','Percentage change in Accuracy']
        output = cls_prereq


    #Print outcome of your prediction here.
    print("--------------------------------------------------------------------")
    print("\nFeature ranking for input dataset is as follows;\n")
    print(prediction)
    print("\n--------------------------------------------------------------------")

    #paste data in output excel file for further processing.
    fname = fname + ".xlsx"
    wd = os.getcwd()
    path = str(wd) + "/" + str(fname)
    #paste data in excel.
    if os.path.exists(path):
        with pd.ExcelWriter(fname,mode='a', if_sheet_exists='replace') as writer:
            output.to_excel(writer, sheet_name='Ranked_features', index = False)
    else:
        with pd.ExcelWriter(fname) as writer:
            #write data to different sheets.
            output.to_excel(writer, sheet_name='Ranked_features', index=False)

    end_time = datetime.datetime.now()
    time_taken = end_time - start_time
    print("\nProcess completed and data populated. Time taken = " + str(time_taken) + 
          "\nFile path = " + str(path))



def neural_network_build(df, X_train,y_train, outcome, predict = 0, epochs = 100):
    """
    (* - Mandatory input)
    Input: (*Input Dataset,*Training_dataset*, *Training_labels, *'Outcome_Variable', 
    Predict = (0 - Regress (default), 1 - Binary Classification, 2 - Multiclass Classification)), 
    epochs = default(100)

    Function module for Neural network ML Model. 
    This module will then be called inside the main module. The main module will pass input such as whether the Neural network
    model needs to be of Regression or classification (binary or multiclass) type.
    
    This function will compile, fit and return the Neural network model.
    """

    #Defining initial empty Neural network
    model = Sequential()
    #Input layer, you can adjust neurons but don't touch input shape
    model.add(Dense(32,input_shape = (X_train.shape[1],)))

    #------------------------Defining model neurons and activation functions-----------------------------
    #Only edit this section within the commented hypens. Add or remove your activation functions and neurons as per liking if using neural network.
    activation_func = ['LeakyReLU','LeakyReLU','LeakyReLU']
    neurons_per_layer = [64,128,64]
    #----------------------------------------------------------------------------------------------------

    layer = pd.DataFrame(zip(neurons_per_layer,activation_func),columns=['Neurons','ActivationFunc'])
    model_str = ""

    #Hidden layers: add/remove/edit anything that you wish to.
    for ind,val in layer.iterrows():
        model.add(Dense(val['Neurons'],activation=val['ActivationFunc']))
        model_str += str(val['Neurons']) + ":" + str(val['ActivationFunc']) +","

    model_str = "Neural_Network(" + model_str[:-1] + ")"
    #print(model_str)

    #last/output layer for neural network and compilation of model.
    if predict == 0:#Regression
        model.add(Dense(1))
        model.compile(loss = 'mse', optimizer='adam', metrics=['mse', 'mae','mape'])
    elif predict == 1:#Binary Classification
        model.add(Dense(1, activation='sigmoid'))
        model.compile(loss = 'binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    elif predict == 2:#Categorical Classification
        model.add(Dense(df[outcome].unique(), activation='softmax'))
        model.compile(loss = 'categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        y_train = ut.to_categorical(y_train)

    return model, model_str

