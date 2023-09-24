import pandas as pd
import chardet
import numpy as np
import time
from sklearn.utils import resample
from sklearn.preprocessing import MinMaxScaler


def line():
    print("*=========*=========**=========*=========*")
# Function to detect encoding
def detect_encoding(file_name):
    with open(file_name, 'rb') as f:
        result = chardet.detect(f.read())
        return result['encoding']

# Function to read CSV file with encoding detection
def read_csv_with_encoding(file_name):
    encoding = detect_encoding(file_name)
    data = pd.read_csv(file_name, delimiter=",", encoding=encoding)
    return data

# Function for Task#1: Display Dataset
def display_dataset(data):
    print("First 5 Rows:")
    print(data.head(5))
    print("Last 5 Rows:")
    print(data.tail(5))

# Function for Task#2: Shape of Data
def get_data_shape(data):
    return data.shape



def handle_categorical_values(data, col):
    one_hot = pd.get_dummies(data[col], prefix=col)
    data = pd.concat([data, one_hot], axis=1)
    data.drop(col, axis=1, inplace=True)  # Drop the original column in place
    #return data  # Remove this line, as it's not needed


# Function for Task#7: Fill Null Values with 0
# Function to fill null values in each column with the mean of that column
def fill_null_values_with_mean(data):
    for col in data.columns:
        if data[col].isna().any():
            if pd.api.types.is_numeric_dtype(data[col]):
                mean = data[col].mean()
                data[col].fillna(mean, inplace=True)
            else:
                print("Column ",col," is not numeric and cannot be filled with mean.")

    return data


# Function for Task#8: Manage Categorical Values (One Hot Encoding)
def one_hot_encoding(data, col):
    if col in data.columns:
        dummies = pd.get_dummies(data[col], prefix=col, drop_first=False)
        data = pd.concat([data, dummies], axis=1)
        data.drop(col, axis=1, inplace=True)
        data[dummies.columns] = data[dummies.columns].astype(int)
        print("Now converting to numerical from booleans")
        for dum in dummies.columns:
            data[dum] = data[dum].astype(int)
        print("Conversion Done")
    return data  # Return the modified data




# Function for Task#11: Remove Column
def remove_columns(data, columns_to_remove):
    data.drop(columns=columns_to_remove, inplace=True)
    return data

# Function for Task#13: Normalize Data
# Function to normalize each column in the DataFrame
def normalize_column(data, col_name):
    if pd.api.types.is_numeric_dtype(data[col_name]):
        # Create a MinMaxScaler
        scaler = MinMaxScaler()

        # Reshape the column to a 2D array (required by the scaler)
        column_data = data[col_name].values.reshape(-1, 1)

        # Fit and transform the data
        normalized_data = scaler.fit_transform(column_data)

        # Replace the original column with the normalized data
        data[col_name] = normalized_data

        return data
    else:
        print("Column", col_name, " is not numeric and cannot be normalized.")
        return data



# Function for Task#14: Balance Data


# Function to balance data using random oversampling
def balance_data(data, target_column):
    if target_column not in data.columns:
        print("Target column", target_column," not found in the dataset.")
        return data

    class_counts = data[target_column].value_counts()

    if len(class_counts) != 2:
        print("Target column should have exactly two unique values for binary classification.")
        return data

    majority_class = class_counts.idxmax()
    minority_class = class_counts.idxmin()

    if class_counts[majority_class] > class_counts[minority_class]:
        majority_data = data[data[target_column] == majority_class]
        minority_data = data[data[target_column] == minority_class]
        minority_data_oversampled = resample(minority_data, replace=True, n_samples=class_counts[majority_class],
                                             random_state=42)
        balanced_data = pd.concat([majority_data, minority_data_oversampled])
    else:
        # If minority class is larger or equal, return the original data
        balanced_data = data

    return balanced_data



def check_for_string_values(data):
    for col in data.columns:
        if pd.api.types.is_string_dtype(data[col]):
            line()
            print("Column", col," contains string values.")
            line()
            print("Choose an action:")
            print("1. Convert to Numeric")
            print("2. Categorize (One-Hot Encoding)")
            print("3. Delete Column")
            print("4. Keep as String")
            choice = input("Enter your choice (1/2/3/4): ")
            line()
            if choice == "1":
                # Convert to numeric
                data[col] = pd.to_numeric(data[col], errors='coerce')
                line()
                print("Filling null values with thier mean")
                data = fill_null_values_with_mean(col)
                print("Filling done")
                line()
                print("Do you want to normalize it?")
                chioce = input("Enter your choice (y/press enter)")
                if (choice == "1"):
                    line()
                    data = normalize_column(data, col)
                    print("Normalization Done")
                    line()
            elif choice == "2":
                # Categorize (One-Hot Encoding)
                line()
                print("Handling Categorical Values")
                data = one_hot_encoding(data, col)
                print("Handling Done")
                line()
            elif choice == "3":
                # Delete Column
                print("Droping Column")
                data.drop(columns=[col], inplace=True)
                print("Column Dropped")
                line()
            # For choice "4", keep the column as a string
        else:
            line()
            print("Column", col," contains Numeric values.")
            line()
            print("Choose an action:")
            print("1. Delete Column")
            print("2. Normalize colum")
            choice = input("Enter your choice (1/2): ")
            if choice == "1":
                # Convert to numeric
                line()
                data[col] = pd.to_numeric(data[col], errors='coerce')
                line()
                print("Do you want to normalize it?")
                choice = input("Enter your choice (y/press enter)")
                if (choice.lower() == "y"):
                    data = normalize_column(data, col)

            elif choice == "2":
                # Categorize (One-Hot Encoding)
                data = data.drop(columns=[col], inplace=True)
            else:
                print("No operations selected")
    return data


# Main function
def main(link_to_data):

    data = read_csv_with_encoding(link_to_data)
    print("File Not Found Error")
    line()
    print("Task#1: Display Dataset")
    display_dataset(data)
    line()
    line()
    print("Task#2: Shape of Data")
    print(get_data_shape(data))
    line()
    line()
    print("Task#6: Check for String Values")
    data = check_for_string_values(data)
    line()
    line()
    print("Task#14: Balance Data")
    target_column = ""  # Define the target column for data balancing
    data = balance_data(data, target_column)
    line()
    line()
    print("Task#15: Export Data Set")
    data.to_csv("exported1.csv", index=False)
    line()
    line()
if __name__ == "__main__":
    link_to_data = "dataSet/dataset.csv"
    main(link_to_data)



#
