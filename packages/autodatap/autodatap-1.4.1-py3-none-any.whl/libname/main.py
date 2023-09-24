# automating Data preprocessing with python
import pandas as pd
from sklearn.preprocessing import normalize
import time
numericColumns = []
stringColumns = []
namesOfColumnsWantsToConvert = []
noString = False

def line():
    print("*========*========*========*========*")

def checkingForNumericalValue(data):
    print("Checking the values")
    try:
        numericColumns.clear()
        stringColumns.clear()
        for col in data.columns:
            if pd.api.types.is_numeric_dtype(data[col]):
                numericColumns.append(col)
            else:
                stringColumns.append(col)

    except pd.errors:
        print("Error Occured: ", pd.errors)

    return data

# displaying both the vlues (String, and Numeric)
def displayingColumns(stringColumns, numericColumns, data):
    print("Numeric Columns: ", numericColumns)
    print("String Columns: ", stringColumns)
    print("Task 02#: Successfull")
    line()
    return data


# checking for cetagorical values
def checkForCetagoricalValues(data):
    cols = data.select_dtypes(include=object)
    for col in cols:
        lengthOfUniqeValues = cols[col].unique()
        if len(lengthOfUniqeValues) < 2:
            print("Categorical Values found:")
            print(cols[lengthOfUniqeValues])
            line()

        else:
            print("System does not recognize any categorical values")
            print("you can chose data to convert below")
            line()

    return data


# Checking for string values
def checkForStringValues(data):
    if len(stringColumns) == 0:
        print("No more String Values")
    else:
        print("Still have String values")
        noString = True
    return data



def doingOneHotEncoding(data):
    forEncoding = []
    print("Type names of the columns exact Spelling (if you don't want to categorize just press enter"
          "):")
    print("Data Columns are: ", data.columns)

    value2 = input("Should be comma separeted: ")
    forEncoding.extend(value2.strip().split(","))
    if value2!="":
        # one hot encoding process goes here
        for col in forEncoding:
            try:
                # data = pd.get_dummies(data, columns=[col], inplace=True)
                dummies = pd.get_dummies(data[col], prefix=col)
                print("Dummies Columns: ", dummies)
                data = pd.concat([data, dummies], axis=1)
                data.drop(col, axis=1, inplace=True)
                print("Converted successfully: ", data.head(5))
                print("Converted successfully")
                print("Now converting to numerical from booleans")
                try:
                    for dum in dummies.columns:
                        data[dum] = data[dum].astype(int)
                    # data["gender_female"] = data["gender_female"].astype(int)
                except pd.errors:
                    print(pd.errors)
                print("Conversion Done")
                print("Converted successfully: ")
                checkingForNumericalValue(data)
            except pd.errors:
                print("Error occrd: ", pd.errors)
    else:
        line()
        print("No Columns selected")
        line()
    return data


def removalOfColumn(data):
    line()
    print("to remove some columns ('columns Name') (multiple names would be comma separated)")
    value1 = input("Answer here: ")
    if value1!="":
        try:
            namesOfColumnsWantsToConvert.extend(value1.strip().split(","))
            columns_to_remove = namesOfColumnsWantsToConvert
            data.drop(columns=columns_to_remove, inplace=True)
            print("Column Removed Sucessfully")
        except pd.errors:
            print("Key Error")
        finally:
            print("Maybe: Key Error")
    else:
        print("No Column Selected")
        line()
    return data



def checkForNullValues(data):
    print("Sum of total Null values: ", data.isnull().sum())
    return data

def fillNullValues(data):
    print(data.fillna(0, inplace=True))
    return data


def normalizeData(data):
    line()
    normalizeColumns = []
    print("Which columns do you want to normalize (if you don't want to normalize just press enter): ")
    answer = input("Answer Here: ")
    normalizeColumns.extend(answer.strip().split(","))
    if answer != "":
        try:
            data[normalizeColumns] = data[normalizeColumns].apply(pd.to_numeric)
            data[normalizeColumns] = normalize(data[normalizeColumns])
            print("Normalizaiton for the columns Done")
        except pd.errors.NullFrequencyError:
            print("The Data may contain NaN values or try again")
    else:
        print("No Columns selected")
    return data

# Checking for imblanced Data and also solving
def balanceAndCheckData(data):
    print("Which one is the target class?")
    print("Column Names: ", data.columns)
    className = input("Answer Here (enter the name of the target class column): ")

    if className not in data.columns:
        print(f"Column '{className}' not found in the dataset.")
        return data
        balanceAndCheckData()

    class_counts = data[className].value_counts()

    if len(class_counts) != 2:
        print("Target class should have exactly two unique values for binary classification.")
        return data

    majority_class = class_counts.idxmax()
    minority_class = class_counts.idxmin()

    if class_counts[majority_class] > class_counts[minority_class]:
        imbalance_ratio = class_counts[majority_class] / class_counts[minority_class]
    else:
        imbalance_ratio = class_counts[minority_class] / class_counts[majority_class]

    print(f"Majority Class: {majority_class}")
    print(f"Minority Class: {minority_class}")
    print(f"Imbalance Ratio: {imbalance_ratio:.2f}")

    if imbalance_ratio > 5.0:  # You can adjust this threshold as needed
        print("Data is Imbalanced")
        print(f"ratio {imbalance_ratio}")
    else:
        print("Data is Balanced")
        print(f"ratio {imbalance_ratio}")

    return data

def dropDuplicateValues(data):
        data.drop_duplicates()
        return data


def checkForFeaturesSelection():
    print("Feature selection is not supported yet.")

def mainMethod(linkToData):
    # global data
    line()
    print("Data processing....")
    line()
    time.sleep(2)
    try:
        data = pd.read_csv(f"{linkToData}", delimiter=",")

        print("Task 01# Data read: Successfull")
        line()
    except FileNotFoundError:
        print("File Not Found Error")
        print("Task 01# Data read: Un-Successfull")
        line()
    except pd.errors.EmptyDataError:
        print("There is no data in the dataset")
        print("Task 01# Data read: Un-Successfull")
        line()
    except pd.errors.ParserError:
        print("Error while parsing the file")
        print("Task 01# Data read: Un-Successfull")
        line()

    print("Task#1) Display Dataset")
    line()
    time.sleep(2)
    print("First 5 Columns and rows")
    print(data.head(5))
    print("Last 5 Columns and rows")
    print(data.tail(5))
    line()

    print("Task#2) SHape of Data")
    line()
    time.sleep(2)
    print(data.shape)
    line()

    print("Task#3) Describe Data")
    line()
    time.sleep(2)
    print(data.describe())
    line()

    print("Task#4) Information of Data")
    line()
    time.sleep(2)
    print(data.info)
    line()

    print("Task#5) Show Columns Names")
    line()
    time.sleep(2)
    print(data.columns)
    line()

    print("Task#6) Check for Null Values")
    line()
    time.sleep(2)
    data = checkForStringValues(data)
    print(data.head(5))
    line()


    print("Task#7) Fill null values with 0 (mean coming soon)")
    line()
    time.sleep(2)
    data = fillNullValues(data)
    print(data.head(5))
    line()

    print("Task#8) Manage categorical Values (One Hot Encoding)")
    line()
    time.sleep(2)
    checkForCetagoricalValues(data)
    time.sleep(2)
    data = doingOneHotEncoding(data)
    print(data.head(5))
    line()

    print("Task#9) Check for String Values (if any)")
    line()
    time.sleep(2)
    data = checkForStringValues(data)
    print(data.head(5))
    line()

    print("Task#10) Drop duplicate Values (if any)")
    line()
    time.sleep(2)
    data = dropDuplicateValues(data)
    print(data.head(5))
    line()

    print("Task#11) Remove Column")
    line()
    time.sleep(2)
    data = removalOfColumn(data)
    print(data.head(5))
    line()

    print("Task#12) Check for feature Selection (not yet implemented)")
    line()
    time.sleep(2)
    checkForFeaturesSelection()
    print(data.head(5))
    line()

    print("Task#13) Normalization")
    line()
    time.sleep(2)
    data = normalizeData(data)
    print(data.head(5))
    line()

    print("Task#14) Balance Data")
    line()
    time.sleep(2)
    data = balanceAndCheckData(data)
    print(data.head(5))
    line()

    print("Task#15) Export Data set")
    line()
    time.sleep(2)
    data.to_csv("exported.csv", index=False)

    line()


    return data


# linkToData = "dataSet/dataset.csv"
# mainMethod(linkToData)

