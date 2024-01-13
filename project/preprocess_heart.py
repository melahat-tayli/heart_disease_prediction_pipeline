import numpy as np
from sklearn.feature_selection import chi2
from sklearn.preprocessing import MinMaxScaler
from statsmodels.stats.outliers_influence import variance_inflation_factor

"""Explanation of variables for heart.csv dataset:
1. age: Age in years
2. sex: 0 (female), 1 (male)
3. cp: Chest pain type, [0: Typical Angina, 1: Atypical Angina, 2: Non-Anginal Pain, 3: Asymptomatic]
4. trestbps: Resting Blood Pressure mm/hg
5. chol: Serum Cholesterol mg/dl
6. fps: Fasting Blood Sugar >120 mg/dl, 0 (no), 1 (yes)
7. restecg: Resting ECG,  [0: normal, 1: having ST-T wave abnormality , 2: showing probable or definite left ventricular hypertrophy]
8. thalach: Maximum heart rate
9. exang: Exercise Induced Angina, [1 = yes, 0 = no]
10. oldpeak: ST depression induced by exercise relative to rest
11. slope: the slope of the peak exercise ST segment
12. ca: number of major vessels (0–3)
13. thal: Thallium heart scan,  [1 = normal, 2 = fixed defect, 3 = reversible defect]
14. target: [0 = disease, 1 = no disease]

binary_columns = ['sex', 'fbs', 'exang']
categorical_columns = ['cp', 'restecg', 'slope', 'ca', 'thal']
continuous_columns = ['age', 'trestbps', 'chol', 'thalach', 'oldpeak']
"""


def preprocess(df, train_or_test):
    """ Preprocesses heart.csv data"""

    df.loc[
        ~df["ca"].isin([0, 1, 2, 3]), "ca"
    ] = (
        np.NaN
    )  # ca should range from 0-3. df['ca'].unique() shows ad addtional value 4. Change value 4 to NaN
    df.loc[
        ~df["thal"].isin([1, 2, 3]), "thal"
    ] = (
        np.NaN
    )  # thal should range from 1-3. df['thal'].unique() shows an additional value 0. Change 0 to NaN

    df = df.fillna(
        df.median(skipna=True, numeric_only=True)
    )  # df.isnull().sum() shows some missing values, change them to median

    # remove outliers from train
    continuous_columns = ["age", "trestbps", "chol", "thalach", "oldpeak"]
    if train_or_test == "train":
        quantile_25 = df[continuous_columns].quantile(0.25)
        quantile_75 = df[continuous_columns].quantile(0.75)
        inter_quantile = quantile_75 - quantile_25
        outlier_cutoff = inter_quantile * 1.5
        lower, upper = quantile_25 - outlier_cutoff, quantile_75 + outlier_cutoff

        df = df[
            ~((df[continuous_columns] < lower) | (df[continuous_columns] > upper)).any(
                axis=1
            )
        ]

    # Scale continuous variables
    scaler = MinMaxScaler()
    df[continuous_columns] = scaler.fit_transform(df[continuous_columns])

    # Correlations between categorical variables and label
    if train_or_test == "train":
        binary_and_categorical_columns = [
            "cp",
            "restecg",
            "slope",
            "ca",
            "thal",
            "sex",
            "fbs",
            "exang",
        ]

        chi2_scores, p_values = chi2(df[binary_and_categorical_columns], df["target"])
        # drop the columns which has p values higher than 0.05. Columns with higher p values are independent of label
        names_independent_categorical_columns = np.array(
            binary_and_categorical_columns
        )[p_values > 0.05]

    if train_or_test == "test":
        names_independent_categorical_columns = [
            "restecg",
            "fbs",
        ]  # the results obtained from training (needed to change if a different training data supplied)
    df = df.drop(names_independent_categorical_columns, axis=1, errors="ignore")

    # Correlations between continuous features
    if train_or_test == "train":
        ck = np.array(df[continuous_columns])
        vif = [variance_inflation_factor(ck, i) for i in range(ck.shape[1])]
        names_correlated_continuous_columns = np.array(continuous_columns)[
            np.array(vif) > 5
        ]

    if train_or_test == "test":
        names_correlated_continuous_columns = [
            "age",
            "trestbps",
            "chol",
        ]  # the results obtained from training (needed to change if a different training data supplied)

    df = df.drop(names_correlated_continuous_columns[:-1], axis=1)
    return df
