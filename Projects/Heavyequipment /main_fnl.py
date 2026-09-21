# %%
# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python Docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

# Input data files are available in the read-only "../input/" directory
# For example, running this (by clicking run or pressing Shift+Enter) will list all files under the input directory

import os
for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))

# You can write up to 20GB to the current directory (/kaggle/working/) that gets preserved as output when you create a version using "Save & Run All" 
# You can also write temporary files to /kaggle/temp/, but they won't be saved outside of the current session

# Use the kagglehub client library to attach Kaggle resources like competitions, datasets, and models to your session
# Learn more about kagglehub: https://github.com/Kaggle/kagglehub/blob/main/README.md

import kagglehub
# kagglehub.dataset_download('<owner>/<dataset-slug>')

# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
%matplotlib inline



# %%
train= pd.read_csv("/kaggle/input/competitions/heavy-equipment-selling-price-prediction-challenge/train.csv")
test = pd.read_csv("/kaggle/input/competitions/heavy-equipment-selling-price-prediction-challenge/test.csv")
meta = pd.read_csv("/kaggle/input/competitions/heavy-equipment-selling-price-prediction-challenge/metadata.csv")
smpl = pd.read_csv("/kaggle/input/competitions/heavy-equipment-selling-price-prediction-challenge/sample_submission.csv")

# %%
# sample = pd.read_csv("datasets/sample.csv")
train["is_train"]=1
test["is_train"]=0

# %%
df = pd.concat([train, test], axis= 0)
df.head()

# %%
#just to verify
display(train.shape, test.shape)
display(df.shape)

# %%
df.info()

# %% [markdown]
# ## **EDA and Feature Engineering**

# %%
df.describe().T

# %%
num_cols = df.select_dtypes(include = ["int64", "float64"]).columns.to_list()
cat_cols = [i for i in df.columns if i not in num_cols]

print(num_cols)
display(cat_cols)

# %%
df.nunique().sort_values(ascending = True)

# %%
df["TransactionDate"] = pd.to_datetime(df["TransactionDate"])

# %%
df["Trans_Month"] = df["TransactionDate"].dt.month
df["Trans_Quarter"] = df["TransactionDate"].dt.quarter
df["Trans_DayOfWeek"] = df["TransactionDate"].dt.dayofweek

# %%
# df.groupby(["TransactionDate"])["TargetValue"].sum()
df["ProductConfigID"] = df["ProductConfigID"].astype("object")
df["AssetID"] = df["AssetID"].astype("object")

# %%
# df["ManufactureYear"].unique()
df["ManufactureYear"] = df["ManufactureYear"].replace(1001, np.nan)

# %%
#outliers:
def iqr(s):
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr  = q3 - q1
    lower, upper = q1-1.5*iqr, q3+1.5*iqr 
    return lower, upper, (s<lower).sum(), (s>upper).sum()

# %%
iqr(df["OperationalHoursMeter"])

# %%
# meta[meta["Variable"]=="TransactionDate"]
df["SalesYear"] = pd.to_datetime(df["TransactionDate"]).dt.year

# %%
df["AssetAge"] = df["SalesYear"] - df["ManufactureYear"]

# df[df["SalesYear"] < df["ManufactureYear"]]
df.loc[df["AssetAge"] == -1, "AssetAge"] = 0 #as the data only have year..
df.loc[df["AssetAge"]<-1, "AssetAge"] = np.nan #not logical to book a car 

# %%
df["HoursPerYear"] = df["OperationalHoursMeter"]/df["AssetAge"].clip(lower=1)

# %%
not_possible = df["HoursPerYear"] > 365*24
df.loc[not_possible, "OperationalHoursMeter"] = np.nan
df["HoursPerYear"] = df["OperationalHoursMeter"] / df["AssetAge"].clip(lower=1)

# %%
# Age_Sq = AssetAge**2
# log_age = ln(AssetAge+1)
# HoursAge_ration = OperationalHoursMeter/(AssetAge+1)
# trying nonlinear depreciation..
df["Age_Sq"] = df["AssetAge"]**2
df["log_age"]= np.log1p(df["AssetAge"])
df["Hour_age_ratio"] = df["OperationalHoursMeter"]/(df["AssetAge"]+1)

# %%

meta

# %% [markdown]
# 

# %%
# [print(f"{i} cols values ",df[i].unique())for i in df.columns[df.columns.str.startswith("col")]]
# df["col30"].unique()
#extracting numerical data from objects dtypes
obj_nums = ["col7", "col15","col21", "col22", "col10"]
df[obj_nums]

# %%
import re
def parse_to_num(val):
    if pd.isna(val) or val in ['None or Unspecified', '<12\'']:
        return np.nan
    if str(val).strip() == "<12'":
        return 11.5
    nums = re.findall(r'[-+]?\d*\.\d+|\d+', str(val))
    if nums:
        return float(nums[0]) #34 inch
    return np.nan


# %%
# for i in ['None or Unspecified','16 inch' ]:
    # print(parse_to_num(i))
df["col21_inch"] = df["col21"].apply(parse_to_num)

# %%
# df['col7'].apply(parse_to_num).unique()
df['col7_ft']=df["col7"].apply(lambda x: "11.5" if x=="<12'" else x)
df['col7_ft'].apply(parse_to_num).unique()

# %%
df["col15_size"]=df["col15"].apply(parse_to_num)

# %%
df["col22"].unique()

# %%
# patse col22 - '10\' 10"' -> 10feet 10inches converting to total inches.. 
df["col22"].unique()
def parse_total_inch(val):
    if pd.isna(val) or val == "None or Unspecified":
        return np.nan
    matches = re.findall(r'(\d+)\'\s*(\d+)"', str(val))
    if matches:
        feet, inch = matches[0]
        return (float(feet)*12 + float(inch))
    only_ft = re.findall(r'(\d+)\'', str(val))
    if only_ft:
        return float(only_ft[0]) * 12
    return np.nan
    
df["col22_inch"] = df["col22"].apply(parse_total_inch)

# %%
df["col10"].unique() #hydrolic complexity
col10_mapping = {
    'Standard': 1, 'Auxiliary': 2, '2 Valve': 2, '3 Valve': 3, '4 Valve': 4,
    'Base + 1 Function': 3, 'Base + 2 Function': 4, 'Base + 3 Function': 5,
    'Base + 4 Function': 6, 'Base + 5 Function': 7, 'Base + 6 Function': 8
}
df['col10_complexity'] = df['col10'].map(col10_mapping)

# %%
df["reach_width_ratio"] = df["col22_inch"]/(df["col21_inch"]+0.1)
# now we can safely remove obj_nums

# %%
df.drop(obj_nums, axis = 1, inplace = True)

# %%
# df["LogOperationalHoursMeter"] = np.log1p(df["OperationalHoursMeter"])
# df["AgeBucket"] = pd.qcut(df["AssetAge"],q=5,duplicates="drop")

# %%
df["Base_Function"]=(df["Spec_BaseClass"].astype(str)+ "_"+ df["FunctionalClassification"].astype(str))
# df["Base_Region"]=(df["Spec_BaseClass"].astype(str)+ "_"+ df["RegionCode"].astype(str))
# df["Vendor_Product"]=(df["VendorPartnerID"].astype(str)+ "_"+ df["Spec_BaseClass"].astype(str))
#df[["Vendor_Product","Base_Region","Base_Function"]]

# %%
# df["RegionCode"].astype(str)+"_"+df["FunctionalClassification"].astype(str)
df["Region_Function"]=(df["RegionCode"].astype(str)+"_"+df["FunctionalClassification"].astype(str))
df["Base_Sub"]=(df["Spec_BaseClass"].astype(str)+"_"+df["Spec_SubClass"].astype(str))
df["Base_Release"]=(df["Spec_BaseClass"].astype(str)+"_"+df["Spec_ReleaseSeries"].astype(str))
# df[["Region_Function", "Base_Sub", "Base_Release"]]

# %%
# df[cat_cols].isna().corr()
# # let's create a heatman to better visualise
# sns.heatmap(df[cat_cols].isna().corr(), annot = False, cmap = "coolwarm") 

# %%
# from heatmap
specs_col = ["Spec_SubClass","Spec_ReleaseSeries","Spec_VariantModifier"]
col_block_1 = ["col3", "col10"]
col_block_2 = ["col15", "col20", "col21", "col22", "col23", "col24", "col25"]

df["spec_missing_cnt"] = df[specs_col].isna().sum(axis=1)
# df["col3_col10_missing_cnt"] = df[col_block_1].isna().sum(axis=1) #not eff
# df["col15_25_missing_cnt"] = df[col_block_2].isna().sum(axis=1) 
# df["specs_complete"] = (df[specs_col].notna().all(axis=1).astype(int))

# %%
df.columns[df.isna().mean()>0.8].to_list()

# %%
# to_remove = df.columns[df.isna().mean()>0.8].to_list() #removing data with more than 80% missing values
df.drop(["TransactionDate", "AssetID", "TransactionID"], axis = 1, inplace = True) #"AssetID" can be removed  , +to_remove

# %% [markdown]
# ### Imputation
# 

# %%
cat_cols = df.select_dtypes(include = ["object"]).columns.to_list()
num_cols = [i for i in df.columns if (i not in cat_cols + ["TargetValue", "is_train"])]
num_cols, cat_cols

# %%
# df.isna().sum()
df.dtypes

# %% [markdown]
# #### Checking the correlations 
# 

# %%
df[cat_cols].isna().corr()
# let's create a heatman to better visualise
sns.heatmap(df[cat_cols].isna().corr(), annot = False, cmap = "coolwarm") 

# %% [markdown]
# we found that:
# - col20/22/24(/21/23/25) + col15 (moderate positive correlation with each other)
# - col3 + col10 (correlate with each other)
# when one fields are missing, the other tends to be present, and vice versa.

# %%
for c in ['col3', 'col10', 'col15', 'col20', 'Spec_ReleaseSeries', 'AssetScaleFactor']:
    print(c)
    print(train.groupby('InventoryGroupCategory')[c].apply(lambda x: x.isna().mean()))
    print()

# %% [markdown]
# #### saparating the columns into 2 types one with low cardinality and the other with high cardinality

# %%
# cat1_cols = [i for i in df[cat_cols].columns if df[i].nunique() <= 20]
# cat2_cols = [i for i in df[cat_cols].columns if df[i].nunique() > 20]
# later fone

# %%
# [i for i in num_cols+cat1_cols+cat2_cols if i not in df.columns.to_list()]
# len(num_cols+cat1_cols+cat2_cols), len(df.columns.to_list()) #these are na "TargetValue", "is_train"

# %% [markdown]
# #### df -> train + test back
# 

# %%
train_df = df[df["is_train"]==1].drop(['is_train'], axis = 1).copy()
test_df = df[df["is_train"]==0].drop(['is_train', 'TargetValue'], axis = 1).copy()

# %%
train.shape, train_df.shape, test.shape, test_df.shape

# %%
## Data Preprocessing
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler, TargetEncoder, RobustScaler
from sklearn.impute import SimpleImputer


num_pipe = Pipeline([
    ('impute', SimpleImputer(strategy='median', add_indicator=True)),  
    ('scale', RobustScaler()),
])

cat1_pipe = Pipeline([
    ('impute', SimpleImputer(strategy='constant', fill_value='Missing')),
    ('encode', OneHotEncoder(handle_unknown='ignore', sparse_output=False)),
])

cat2_pipe = Pipeline([
    ('impute', SimpleImputer(strategy='constant', fill_value='Missing')),
    ('encode', TargetEncoder(target_type='continuous')),  
    ('scale', RobustScaler()),
])

# %%
print("These are all the cat cols:", cat_cols)

# %%
from sklearn.model_selection import train_test_split
X = train_df.drop(['TargetValue'], axis = 1)
y = np.log1p(train_df['TargetValue'])
X_train, X_val, y_train, y_val = train_test_split(
    X, 
    y, 
    test_size=0.2, 
    random_state=42
)
X_test = test_df.copy(deep=True)

# %%
X_train["AgeBucket"], age_bins = pd.qcut(X_train["AssetAge"], q =5, duplicates="drop", retbins=True)
X_val["AgeBucket"] = pd.cut(X_val["AssetAge"],bins=age_bins,include_lowest=True)
X_test["AgeBucket"] = pd.cut(X_test["AssetAge"],bins=age_bins,include_lowest=True)

# %%
from sklearn.preprocessing import TargetEncoder
calbi_feat = {
    'Region_Base': ['RegionCode', 'Spec_BaseClass'],
    'Vendor_Base': ['VendorPartnerID', 'Spec_BaseClass'],
    'Func_AgeBucket': ['FunctionalClassification', 'AgeBucket'],
}

for new_col, group_cols in calbi_feat.items():
    for d in [X_train, X_val, X_test]:
        d[new_col] = d[group_cols].astype(str).agg('_'.join, axis=1)
    te = TargetEncoder(target_type='continuous')
    X_train[f'{new_col}_TE'] = te.fit_transform(X_train[[new_col]], y_train)
    X_val[f'{new_col}_TE']   = te.transform(X_val[[new_col]])
    X_test[f'{new_col}_TE']  = te.transform(X_test[[new_col]])

for d in [X_train, X_val, X_test]:
    d.drop(columns=['Region_Base', 'Region_Base_TE', 'Vendor_Base', 'Vendor_Base_TE'], errors='ignore', inplace=True) #from recent test

# %%
X_train.head(1).T

# %%
X_train.dtypes

# %%
# num_col = X_train.select_dtypes(["int64", "int32", "float64"]).columns

# corr = X_train[num_col].corr()
# # mask = np.triu(np.ones_like(corr, dtype=bool))
# sns.heatmap(corr, fmt=".2f", cmap='coolwarm', center=0, linewidths=0.5)

# %%


# %%
# preprocessor

# %%
# drop_model_cols = ["TransactionID", "AssetID"]
for d in [X_train, X_val, X_test]:
    d["OperationalHoursMeter_missing"] = d["OperationalHoursMeter"].isna().astype(int)

# %%
# drop_model_cols = ["TransactionID", "AssetID"]
product_freq = X_train["ProductConfigID"].value_counts()
vendor_freq = X_train["VendorPartnerID"].value_counts()
baseclass_freq = X_train["Spec_BaseClass"].value_counts()
region_freq = X_train["RegionCode"].value_counts()
func_freq = X_train["FunctionalClassification"].value_counts()

# %%
for d in [X_train, X_val, X_test]:
    d["ProductFreq"] = d["ProductConfigID"].map(product_freq).fillna(0)
    d["VendorFreq"] = d["VendorPartnerID"].map(vendor_freq).fillna(0)
    d["BaseClassFreq"] = d["Spec_BaseClass"].map(baseclass_freq).fillna(0)
    d["RegionFreq"] = d["RegionCode"].map(region_freq).fillna(0)
    d["FuncFreq"] = d["FunctionalClassification"].map(func_freq).fillna(0)

# %%
# by base class + age bucket
train_expected = (X_train.groupby(["Spec_BaseClass", "AgeBucket"], observed=True)["OperationalHoursMeter"].median().replace(0, np.nan))

# for d in [X_train, X_val, X_test]:
#     idx = d.set_index(["Spec_BaseClass", "AgeBucket"]).index
#     expected = idx.map(train_expected)
#     d["UsageRatio"] = d["OperationalHoursMeter"] / expected
#     d["UsageRatio"] = d["UsageRatio"].replace([np.inf, -np.inf], np.nan).fillna(1.0)

# %%
base_hours_median = (X_train.groupby("Spec_BaseClass", observed=True)["OperationalHoursMeter"].median().replace(0, np.nan))

# %%
global_hours_median = X_train["OperationalHoursMeter"].median()

# for d in [X_train, X_val, X_test]:
#     expected_base = d["Spec_BaseClass"].map(base_hours_median).fillna(global_hours_median)
#     d["Hours_vs_BaseMedian"] = d["OperationalHoursMeter"] / expected_base
#     d["Hours_vs_BaseMedian"] = d["Hours_vs_BaseMedian"].replace([np.inf, -np.inf], np.nan).fillna(1.0)
# X_train.dtypes

# %%
cat_cols = X_train.select_dtypes(include=["object", "category"]).columns.tolist()
num_cols = X_train.select_dtypes(include=["int", "float"]).columns.tolist()

# %%
for d in [X_train, X_val, X_test]:
    d[cat_cols] = d[cat_cols].astype(str).replace("nan", "Missing")

for d in [X_train, X_val, X_test]:
    d[cat_cols] = d[cat_cols].fillna("Missing").astype(str)
    for c in num_cols:
        if c == "HoursPerYear":
            continue  # skip — recomputed below from the now-imputed inputs
        d[c] = d[c].fillna(X_train[c].median())

# Recompute AFTER OperationalHoursMeter and AssetAge are both imputed,
# so HoursPerYear is internally consistent instead of carrying its own
# disconnected median fill
for d in [X_train, X_val, X_test]:
    d["HoursPerYear"] = d["OperationalHoursMeter"] / d["AssetAge"].clip(lower=1)

# %%
# these are the blind spots i found from model..
for d in [X_train, X_val, X_test]:
    d['is_PC_series'] = d['Spec_BaseClass'].astype(str).str.startswith('PC').astype(int)
    d['is_high_error_class'] = d['Spec_BaseClass'].isin(['235', 'D6', 'PC300', 'PC200']).astype(int)
    
    logical_max_hours = d['AssetAge'].clip(lower=1) * 5000
    d['is_garbage_hours'] = (d['OperationalHoursMeter'] > logical_max_hours).astype(int)
    d['is_salvage_risk'] = ((d['AssetAge'] > 20) | (d['spec_missing_cnt'] > 3)).astype(int)
    d['is_premium_proxy'] = ((d['AssetAge'] <= 3) & (d['OperationalHoursMeter'] < 3000)).astype(int)

# %%
# for d in [X_train, X_val, X_test]:
#     logical_max_hours = d['AssetAge'].clip(lower=1) * 5000
#     d['is_garbage_hours'] = (d['OperationalHoursMeter'] > logical_max_hours).astype(int)
#     cap_value = X_train['OperationalHoursMeter'].quantile(0.99)
#     d['OperationalHoursMeter_Capped'] = d['OperationalHoursMeter'].clip(upper=cap_value)

# %%
# for d in [X_train, X_val, X_test]:
#     # Proxy for Older than 20 years OR missing crucial specs
#     d['is_salvage_risk'] = ((d['AssetAge'] > 20) | (d['spec_missing_cnt'] > 3)).astype(int)
#     d['is_premium_proxy'] = ((d['AssetAge'] <= 3) & (d['OperationalHoursMeter'] < 3000)).astype(int)

# %%
# X_train.dtypes

# %%
cat_features = X_train.select_dtypes(["object"]).columns.tolist()
cat_features = [c for c in cat_features if c not in ['Region_Base', 'Vendor_Base']]

cat1_cols = [c for c in cat_features if X_train[c].nunique() <= 20]
cat2_cols = [c for c in cat_features if X_train[c].nunique() > 20]


num_cols = X_train.select_dtypes(include=["int64", "int32", "float64"]).columns.tolist()
cat_features

# %%
from sklearn.compose import ColumnTransformer

preprocessor = ColumnTransformer([
    ('num', num_pipe, num_cols),
    ('low_card', cat1_pipe, cat1_cols),
    ('high_card', cat2_pipe, cat2_cols),
], remainder='drop')

# %%
X_train_fnl= preprocessor.fit_transform(X_train, y_train)
X_val_fnl = preprocessor.transform(X_val)
X_test_fnl = preprocessor.transform(X_test)

# %%
preprocessor

# %% [markdown]
# ### Visualizing the data
# 

# %%
# for i in num_cols:
#     plt.title(f"{i} v/s frequency")
#     # print(i)
#     sns.histplot(data=train_df, x=i)
#     plt.show()

# %% [markdown]
# ### Boxplots
# 

# %%
# for i in num_cols:
#     plt.title(f"{i} v/s frequency")
#     # print(i)
#     sns.boxplot(data=train_df, y=i)
#     plt.show()

# %%
X_train.columns.to_list()

# %%
# import pandas as pd
# from sklearn.model_selection import train_test_split
# from sklearn.preprocessing import OrdinalEncoder
# from sklearn.feature_selection import SelectKBest, mutual_info_regression


# X = X_train.copy()
# y = y_train.copy()
# encoder = OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)
# X_encoded = encoder.fit_transform(X)
# mi_scores = mutual_info_regression(X_encoded, y, discrete_features=True)
# feature_scores = pd.Series(mi_scores, index=X.columns).sort_values(ascending=False)
# print("Feature Scores (Higher is better):\n", feature_scores)
# selector = SelectKBest(score_func=lambda X, y: mutual_info_regression(X, y, discrete_features=True), k=5)
# X_selected = selector.fit_transform(X_encoded, y)
# kept_features = X.columns[selector.get_support()]
# print("\nFeatures to keep:", list(kept_features))

# %%
pd.set_option('display.max_rows', None)

# display(kept_features)

# %%
from catboost import CatBoostRegressor, Pool
from sklearn.model_selection import KFold
from sklearn.metrics import root_mean_squared_error

from sklearn.preprocessing import TargetEncoder

base_cat_features = [
    'ProductConfigID', 'DataOriginCode', 'VendorPartnerID', 'UtilizationTier',
    'Spec_FullDescriptor', 'Spec_BaseClass', 'Spec_SubClass', 'Spec_ReleaseSeries',
    'Spec_VariantModifier', 'FunctionalClassification', 'RegionCode', 
    'InventoryGroupCategory', 'InventoryGroupDescription', 'CabinType', 'Forks',
    'AgeBucket', 'Func_AgeBucket', 'Base_Function', 'Region_Function', 'Base_Sub', 'Base_Release', 
    'AssetScaleFactor'
]

numeric_engineered_cols = ['col7_ft', 'col15_size', 'col21_inch', 'col22_inch', 'col10_complexity', 'reach_width_ratio']

dead_weight_features = [
    'DrivetrainType', 'col7_ft', 'col18', 'col19', 'reach_width_ratio', 
    'col5', 'col8', 'col3', 'Forks', 'col29', 'col4', 
    'OperationalHoursMeter_missing', 'col27', 'col21_inch', 'col11', 
    'col30', 'col15_size', 'col28', 'InventoryGroupDescription', 'col14'
]

X_train_lean = X_train.drop(columns=dead_weight_features, errors='ignore').copy()
X_val_lean   = X_val.drop(columns=dead_weight_features, errors='ignore').copy()
X_test_lean  = X_test.drop(columns=dead_weight_features, errors='ignore').copy()

for d in [X_train_lean, X_val_lean, X_test_lean]:
    d['Year_Base_Combo'] = d['SalesYear'].astype(str) + "_" + d['Spec_BaseClass'].astype(str)
    d['Year_Vendor_Combo'] = d['SalesYear'].astype(str) + "_" + d['VendorPartnerID'].astype(str)

te_time = TargetEncoder(target_type='continuous', smooth=10.0)

X_train_lean['Year_Base_TE'] = te_time.fit_transform(X_train_lean[['Year_Base_Combo']], y_train)
X_val_lean['Year_Base_TE'] = te_time.transform(X_val_lean[['Year_Base_Combo']])
X_test_lean['Year_Base_TE'] = te_time.transform(X_test_lean[['Year_Base_Combo']])

te_vendor = TargetEncoder(target_type='continuous', smooth=10.0)
X_train_lean['Year_Vendor_TE'] = te_vendor.fit_transform(X_train_lean[['Year_Vendor_Combo']], y_train)
X_val_lean['Year_Vendor_TE'] = te_vendor.transform(X_val_lean[['Year_Vendor_Combo']])
X_test_lean['Year_Vendor_TE'] = te_vendor.transform(X_test_lean[['Year_Vendor_Combo']])

for d in [X_train_lean, X_val_lean, X_test_lean]:
    d.drop(columns=['Year_Base_Combo', 'Year_Vendor_Combo'], inplace=True)

# Auto-fetch text 'col__' variables
col_cats = [c for c in X_train_lean.columns if c.startswith('col') and c not in numeric_engineered_cols and c not in dead_weight_features]
cat_features = base_cat_features + col_cats
cat_features = [col for col in cat_features if col in X_train_lean.columns]

for col in X_train_lean.columns:
    if col in cat_features:
        X_train_lean[col] = X_train_lean[col].astype(str).str.strip().replace('nan', 'MISSING_CAT')
        X_val_lean[col]   = X_val_lean[col].astype(str).str.strip().replace('nan', 'MISSING_CAT')
        X_test_lean[col]  = X_test_lean[col].astype(str).str.strip().replace('nan', 'MISSING_CAT')
    else:
        X_train_lean[col] = pd.to_numeric(X_train_lean[col], errors='coerce').fillna(0.0)
        X_val_lean[col]   = pd.to_numeric(X_val_lean[col], errors='coerce').fillna(0.0)
        X_test_lean[col]  = pd.to_numeric(X_test_lean[col], errors='coerce').fillna(0.0)
        
y_train_log = y_train.copy()

# cross-validation
# kf = KFold(n_splits=5, shuffle=True, random_state=42)
# oof_predictions = np.zeros(len(X_train_clean))
# test_predictions = np.zeros(len(X_test_clean))

# print("!Initializing high-speed Kaggle GPU modeling sequence...")

# for fold, (train_idx, val_idx) in enumerate(kf.split(X_train_clean, y_train_log)):
#     X_tr, X_va = X_train_clean.iloc[train_idx], X_train_clean.iloc[val_idx]
#     y_tr, y_va = y_train_log.iloc[train_idx], y_train_log.iloc[val_idx]
    
#     # Pools will parse without error as data types are locked
#     train_pool = Pool(X_tr, y_tr, cat_features=cat_features)
#     val_pool = Pool(X_va, y_va, cat_features=cat_features)
#     test_pool = Pool(X_test_clean, cat_features=cat_features)

#     model = CatBoostRegressor(
#         iterations=8000,    
#         learning_rate=0.05,     
#         depth=8,                   
#         loss_function='RMSE',
#         eval_metric='RMSE',
#         random_seed=42,
#         task_type='GPU',        
#         max_ctr_complexity=2,    
#         early_stopping_rounds=150, 
#         verbose=400
#     )
    
#     model.fit(train_pool, eval_set=val_pool, use_best_model=True)
    
#     oof_predictions[val_idx] = model.predict(val_pool)
#     test_predictions += model.predict(test_pool) / kf.n_splits
#     print(f"✔ Fold {fold+1} processed successfully.")

# y_train_true = np.expm1(y_train_log)
# oof_predictions_true = np.expm1(oof_predictions)

# cv_rmse = root_mean_squared_error(y_train_true, oof_predictions_true)
# print(f"\n\ validation Result, RMSE: {cv_rmse:.5f}")
# final_test_preds = np.expm1(test_predictions)

# %% [markdown]
# ```markdown
# ⚡ Initializing high-speed Kaggle GPU modeling sequence...
# 0:	learn: 0.0572011	test: 0.0572136	best: 0.0572136 (0)	total: 132ms	remaining: 17m 38s
# 400:	learn: 0.0202853	test: 0.0206185	best: 0.0206185 (400)	total: 16.4s	remaining: 5m 10s
# 800:	learn: 0.0189907	test: 0.0198756	best: 0.0198756 (800)	total: 30.8s	remaining: 4m 37s
# 1200:	learn: 0.0181884	test: 0.0195478	best: 0.0195478 (1200)	total: 45.5s	remaining: 4m 17s
# 1600:	learn: 0.0175178	test: 0.0193302	best: 0.0193302 (1600)	total: 1m	remaining: 3m 59s
# 2000:	learn: 0.0169272	test: 0.0191577	best: 0.0191577 (2000)	total: 1m 14s	remaining: 3m 43s
# 2400:	learn: 0.0163953	test: 0.0190388	best: 0.0190388 (2400)	total: 1m 29s	remaining: 3m 28s
# 2800:	learn: 0.0159106	test: 0.0189370	best: 0.0189370 (2800)	total: 1m 44s	remaining: 3m 13s
# 3200:	learn: 0.0154955	test: 0.0188585	best: 0.0188580 (3198)	total: 1m 59s	remaining: 2m 58s
# 3600:	learn: 0.0150952	test: 0.0187960	best: 0.0187960 (3600)	total: 2m 13s	remaining: 2m 43s
# 4000:	learn: 0.0147171	test: 0.0187506	best: 0.0187502 (3998)	total: 2m 28s	remaining: 2m 28s
# 4400:	learn: 0.0143514	test: 0.0187099	best: 0.0187099 (4400)	total: 2m 44s	remaining: 2m 14s
# 4800:	learn: 0.0140256	test: 0.0186742	best: 0.0186740 (4795)	total: 2m 59s	remaining: 1m 59s
# 5200:	learn: 0.0137077	test: 0.0186414	best: 0.0186414 (5200)	total: 3m 15s	remaining: 1m 45s
# 5600:	learn: 0.0134082	test: 0.0186070	best: 0.0186070 (5600)	total: 3m 30s	remaining: 1m 30s
# 6000:	learn: 0.0131203	test: 0.0185843	best: 0.0185841 (5992)	total: 3m 46s	remaining: 1m 15s
# 6400:	learn: 0.0128464	test: 0.0185648	best: 0.0185647 (6396)	total: 4m 2s	remaining: 1m
# 6800:	learn: 0.0125845	test: 0.0185563	best: 0.0185539 (6735)	total: 4m 18s	remaining: 45.6s
# 7200:	learn: 0.0123252	test: 0.0185402	best: 0.0185402 (7192)	total: 4m 34s	remaining: 30.5s
# 7600:	learn: 0.0120784	test: 0.0185236	best: 0.0185235 (7592)	total: 4m 50s	remaining: 15.2s
# 7999:	learn: 0.0118434	test: 0.0185070	best: 0.0185067 (7996)	total: 5m 6s	remaining: 0us
# bestTest = 0.01850670326
# bestIteration = 7996
# Shrink model to first 7997 iterations.
# ✔ Fold 1 processed successfully.
# 0:	learn: 0.0572206	test: 0.0571142	best: 0.0571142 (0)	total: 61.2ms	remaining: 8m 9s
# 400:	learn: 0.0202604	test: 0.0206059	best: 0.0206059 (400)	total: 15s	remaining: 4m 44s
# 800:	learn: 0.0189302	test: 0.0198825	best: 0.0198825 (800)	total: 29.6s	remaining: 4m 26s
# 1200:	learn: 0.0180734	test: 0.0195389	best: 0.0195389 (1200)	total: 44.5s	remaining: 4m 11s
# 1600:	learn: 0.0174160	test: 0.0193249	best: 0.0193249 (1600)	total: 59.4s	remaining: 3m 57s
# 2000:	learn: 0.0168263	test: 0.0191563	best: 0.0191563 (2000)	total: 1m 14s	remaining: 3m 42s
# 2400:	learn: 0.0163175	test: 0.0190365	best: 0.0190365 (2400)	total: 1m 29s	remaining: 3m 27s
# 2800:	learn: 0.0158354	test: 0.0189429	best: 0.0189429 (2800)	total: 1m 44s	remaining: 3m 13s
# 3200:	learn: 0.0154030	test: 0.0188638	best: 0.0188638 (3200)	total: 1m 59s	remaining: 2m 58s
# 3600:	learn: 0.0150033	test: 0.0187947	best: 0.0187947 (3600)	total: 2m 14s	remaining: 2m 43s
# 4000:	learn: 0.0146264	test: 0.0187417	best: 0.0187417 (4000)	total: 2m 29s	remaining: 2m 29s
# 4400:	learn: 0.0142834	test: 0.0186950	best: 0.0186950 (4400)	total: 2m 45s	remaining: 2m 15s
# 4800:	learn: 0.0139360	test: 0.0186559	best: 0.0186558 (4799)	total: 3m	remaining: 2m
# 5200:	learn: 0.0136254	test: 0.0186226	best: 0.0186226 (5200)	total: 3m 16s	remaining: 1m 45s
# 5600:	learn: 0.0133213	test: 0.0185940	best: 0.0185934 (5592)	total: 3m 32s	remaining: 1m 30s
# 6000:	learn: 0.0130370	test: 0.0185657	best: 0.0185654 (5995)	total: 3m 47s	remaining: 1m 15s
# 6400:	learn: 0.0127611	test: 0.0185433	best: 0.0185433 (6370)	total: 4m 3s	remaining: 1m
# 6800:	learn: 0.0124920	test: 0.0185263	best: 0.0185256 (6751)	total: 4m 19s	remaining: 45.8s
# 7200:	learn: 0.0122299	test: 0.0185108	best: 0.0185103 (7195)	total: 4m 36s	remaining: 30.6s
# 7600:	learn: 0.0119721	test: 0.0184909	best: 0.0184909 (7600)	total: 4m 52s	remaining: 15.3s
# 7999:	learn: 0.0117346	test: 0.0184786	best: 0.0184786 (7989)	total: 5m 8s	remaining: 0us
# bestTest = 0.01847861106
# bestIteration = 7989
# Shrink model to first 7990 iterations.
# ✔ Fold 2 processed successfully.
# 0:	learn: 0.0571340	test: 0.0572419	best: 0.0572419 (0)	total: 55.6ms	remaining: 7m 24s
# 400:	learn: 0.0202402	test: 0.0206160	best: 0.0206160 (400)	total: 15s	remaining: 4m 44s
# 800:	learn: 0.0189638	test: 0.0199135	best: 0.0199135 (800)	total: 29.7s	remaining: 4m 27s
# 1200:	learn: 0.0181140	test: 0.0195771	best: 0.0195768 (1199)	total: 44.4s	remaining: 4m 11s
# 1600:	learn: 0.0174272	test: 0.0193671	best: 0.0193671 (1600)	total: 59s	remaining: 3m 55s
# 2000:	learn: 0.0168347	test: 0.0192129	best: 0.0192129 (2000)	total: 1m 13s	remaining: 3m 41s
# 2400:	learn: 0.0163233	test: 0.0191063	best: 0.0191062 (2399)	total: 1m 28s	remaining: 3m 26s
# 2800:	learn: 0.0158441	test: 0.0190206	best: 0.0190206 (2800)	total: 1m 43s	remaining: 3m 12s
# 3200:	learn: 0.0154234	test: 0.0189530	best: 0.0189530 (3200)	total: 1m 58s	remaining: 2m 58s
# 3600:	learn: 0.0150166	test: 0.0189002	best: 0.0189002 (3599)	total: 2m 14s	remaining: 2m 43s
# 4000:	learn: 0.0146399	test: 0.0188518	best: 0.0188518 (4000)	total: 2m 29s	remaining: 2m 29s
# 4400:	learn: 0.0142842	test: 0.0188154	best: 0.0188154 (4400)	total: 2m 44s	remaining: 2m 14s
# 4800:	learn: 0.0139440	test: 0.0187777	best: 0.0187777 (4800)	total: 3m	remaining: 2m
# 5200:	learn: 0.0136117	test: 0.0187407	best: 0.0187406 (5163)	total: 3m 15s	remaining: 1m 45s
# 5600:	learn: 0.0133040	test: 0.0187161	best: 0.0187159 (5596)	total: 3m 31s	remaining: 1m 30s
# 6000:	learn: 0.0130152	test: 0.0186960	best: 0.0186960 (6000)	total: 3m 47s	remaining: 1m 15s
# 6400:	learn: 0.0127324	test: 0.0186819	best: 0.0186817 (6395)	total: 4m 3s	remaining: 1m
# 6800:	learn: 0.0124663	test: 0.0186639	best: 0.0186639 (6800)	total: 4m 19s	remaining: 45.7s
# 7200:	learn: 0.0122063	test: 0.0186484	best: 0.0186483 (7199)	total: 4m 35s	remaining: 30.5s
# 7600:	learn: 0.0119587	test: 0.0186359	best: 0.0186357 (7599)	total: 4m 51s	remaining: 15.3s
# 7999:	learn: 0.0117165	test: 0.0186268	best: 0.0186263 (7929)	total: 5m 7s	remaining: 0us
# bestTest = 0.01862633894
# bestIteration = 7929
# Shrink model to first 7930 iterations.
# ✔ Fold 3 processed successfully.
# 0:	learn: 0.0571097	test: 0.0573189	best: 0.0573189 (0)	total: 56ms	remaining: 7m 27s
# 400:	learn: 0.0203795	test: 0.0204453	best: 0.0204453 (400)	total: 15s	remaining: 4m 44s
# 800:	learn: 0.0190687	test: 0.0196512	best: 0.0196512 (800)	total: 29.9s	remaining: 4m 28s
# 1200:	learn: 0.0182259	test: 0.0192982	best: 0.0192982 (1200)	total: 44.6s	remaining: 4m 12s
# 1600:	learn: 0.0175458	test: 0.0190711	best: 0.0190709 (1598)	total: 59.2s	remaining: 3m 56s
# 2000:	learn: 0.0169641	test: 0.0189180	best: 0.0189180 (2000)	total: 1m 14s	remaining: 3m 41s
# 2400:	learn: 0.0164427	test: 0.0187948	best: 0.0187948 (2400)	total: 1m 28s	remaining: 3m 27s
# 2800:	learn: 0.0159611	test: 0.0186989	best: 0.0186987 (2799)	total: 1m 43s	remaining: 3m 12s
# 3200:	learn: 0.0155196	test: 0.0186222	best: 0.0186222 (3200)	total: 1m 58s	remaining: 2m 58s
# 3600:	learn: 0.0151164	test: 0.0185473	best: 0.0185473 (3600)	total: 2m 14s	remaining: 2m 44s
# 4000:	learn: 0.0147375	test: 0.0184917	best: 0.0184914 (3998)	total: 2m 29s	remaining: 2m 29s
# 4400:	learn: 0.0143822	test: 0.0184461	best: 0.0184458 (4387)	total: 2m 45s	remaining: 2m 15s
# 4800:	learn: 0.0140390	test: 0.0184072	best: 0.0184072 (4799)	total: 3m	remaining: 2m
# 5200:	learn: 0.0137092	test: 0.0183666	best: 0.0183666 (5200)	total: 3m 16s	remaining: 1m 45s
# 5600:	learn: 0.0134034	test: 0.0183413	best: 0.0183412 (5577)	total: 3m 32s	remaining: 1m 31s
# 6000:	learn: 0.0130996	test: 0.0183140	best: 0.0183140 (5999)	total: 3m 48s	remaining: 1m 16s
# 6400:	learn: 0.0128197	test: 0.0182875	best: 0.0182874 (6398)	total: 4m 4s	remaining: 1m 1s
# 6800:	learn: 0.0125518	test: 0.0182690	best: 0.0182690 (6800)	total: 4m 20s	remaining: 45.9s
# 7200:	learn: 0.0122942	test: 0.0182476	best: 0.0182465 (7168)	total: 4m 36s	remaining: 30.7s
# 7600:	learn: 0.0120363	test: 0.0182267	best: 0.0182265 (7599)	total: 4m 52s	remaining: 15.4s
# 7999:	learn: 0.0117935	test: 0.0182164	best: 0.0182155 (7962)	total: 5m 9s	remaining: 0us
# bestTest = 0.01821545357
# bestIteration = 7962
# Shrink model to first 7963 iterations.
# ✔ Fold 4 processed successfully.
# 0:	learn: 0.0572531	test: 0.0570383	best: 0.0570383 (0)	total: 60.8ms	remaining: 8m 6s
# 400:	learn: 0.0202834	test: 0.0206212	best: 0.0206212 (400)	total: 15.1s	remaining: 4m 46s
# 800:	learn: 0.0190537	test: 0.0198556	best: 0.0198556 (800)	total: 29.7s	remaining: 4m 26s
# 1200:	learn: 0.0182449	test: 0.0195122	best: 0.0195122 (1200)	total: 44.1s	remaining: 4m 9s
# 1600:	learn: 0.0175912	test: 0.0193068	best: 0.0193068 (1600)	total: 58.8s	remaining: 3m 54s
# 2000:	learn: 0.0169922	test: 0.0191400	best: 0.0191399 (1999)	total: 1m 13s	remaining: 3m 39s
# 2400:	learn: 0.0164749	test: 0.0190101	best: 0.0190101 (2400)	total: 1m 28s	remaining: 3m 26s
# 2800:	learn: 0.0159962	test: 0.0189089	best: 0.0189089 (2800)	total: 1m 43s	remaining: 3m 11s
# 3200:	learn: 0.0155578	test: 0.0188311	best: 0.0188311 (3200)	total: 1m 58s	remaining: 2m 57s
# 3600:	learn: 0.0151694	test: 0.0187654	best: 0.0187653 (3598)	total: 2m 13s	remaining: 2m 43s
# 4000:	learn: 0.0147934	test: 0.0187156	best: 0.0187150 (3991)	total: 2m 28s	remaining: 2m 28s
# 4400:	learn: 0.0144306	test: 0.0186664	best: 0.0186664 (4400)	total: 2m 44s	remaining: 2m 14s
# 4800:	learn: 0.0140817	test: 0.0186333	best: 0.0186333 (4800)	total: 2m 59s	remaining: 1m 59s
# 5200:	learn: 0.0137569	test: 0.0185961	best: 0.0185951 (5192)	total: 3m 15s	remaining: 1m 45s
# 5600:	learn: 0.0134565	test: 0.0185719	best: 0.0185719 (5599)	total: 3m 31s	remaining: 1m 30s
# 6000:	learn: 0.0131729	test: 0.0185462	best: 0.0185461 (5999)	total: 3m 46s	remaining: 1m 15s
# 6400:	learn: 0.0129009	test: 0.0185282	best: 0.0185277 (6387)	total: 4m 2s	remaining: 1m
# 6800:	learn: 0.0126267	test: 0.0185091	best: 0.0185084 (6758)	total: 4m 18s	remaining: 45.6s
# 7200:	learn: 0.0123744	test: 0.0184964	best: 0.0184964 (7200)	total: 4m 34s	remaining: 30.5s
# 7600:	learn: 0.0121161	test: 0.0184880	best: 0.0184874 (7560)	total: 4m 50s	remaining: 15.3s
# 7999:	learn: 0.0118867	test: 0.0184773	best: 0.0184770 (7990)	total: 5m 7s	remaining: 0us
# bestTest = 0.0184769947
# bestIteration = 7990
# Shrink model to first 7991 iterations.
# ✔ Fold 5 processed successfully.
# 
# \ Validation Result (Target < 0.15) -> Actual OOF RMSE: 0.20667
# the above result have an issues that they have been double loged
# ```

# %% [markdown]
# ## Model
# 

# %%
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
# from xgboost import XGBRegressor
# from lightgbm import LGBMRegressor
from catboost import CatBoostRegressor

models = {
    "baseline_median": DummyRegressor(strategy="median"),
    "linear_reg": LinearRegression(),
    "ridge": Ridge(alpha=1.0, random_state=42),
    "lasso": Lasso(alpha=0.01, random_state=42),
    "random_forest": RandomForestRegressor(n_estimators=300, max_depth=None, n_jobs=-1, random_state=42),
    "hist_gbm": HistGradientBoostingRegressor(random_state=42),
}

# %%
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

results = []
# for name, model in models.items():
#     print(name, "---")
#     model.fit(X_train_fnl, y_train)
#     preds = model.predict(X_val_fnl)
#     results.append({
#         "Model": name,
#         "MAE": mean_absolute_error(y_val, preds),
#         "RMSE": np.sqrt(mean_squared_error(y_val, preds)),
#         "R2": r2_score(y_val, preds)
#     })

# results_df = pd.DataFrame(results).sort_values("RMSE").reset_index(drop=True)
# results_df

# %%
X_test.shape, X_train.shape

# %%
train_pool = Pool(X_train_lean, y_train_log, cat_features=cat_features)
val_pool = Pool(X_val_lean, y_val, cat_features=cat_features)
test_pool = Pool(X_test_lean, cat_features=cat_features)

cat_model = CatBoostRegressor(
    iterations=12000,
    learning_rate=0.03,
    depth=10,
    loss_function='RMSE',
    random_seed=42,
    max_ctr_complexity=2,           
    verbose=400     
)
cat_model.fit(train_pool, early_stopping_rounds=500)
# cat_model.fit(
#     X_train_clean,
#     y_train,
#     cat_features=cat_features,
#     eval_set=(X_val_clean, y_val),
#     early_stopping_rounds=500
# )

# cat_model = joblib.load("/kaggle/input/models/kradarsh04/catboost-init/other/default/1/catboost.joblib")
val_pred_log = cat_model.predict(val_pool)
val_rmse = np.sqrt(mean_squared_error(y_val, val_pred_log))
print("Validation RMSE (log space):", val_rmse)

# %%
import os
import joblib

joblib.dump(cat_model, "catboost_.joblib")

# %% [markdown]
# ## Using lgbm and xgboost

# %%
pip install lightgbm

# %%
import lightgbm as lgb
import xgboost as xgb
from sklearn.metrics import root_mean_squared_error

X_train_tree = X_train_lean.copy()
X_val_tree = X_val_lean.copy()
X_test_tree = X_test_lean.copy()

for col in cat_features:
    X_train_tree[col] = X_train_tree[col].astype('category')
    X_val_tree[col] = X_val_tree[col].astype('category')
    X_test_tree[col] = X_test_tree[col].astype('category')

print("\n /LightGBM...")
lgbm_model = lgb.LGBMRegressor(
    n_estimators=10000,
    learning_rate=0.03,
    num_leaves=63,             
    max_depth=10,
    min_child_samples=30,       
    subsample=0.8,         
    colsample_bytree=0.8,   
    random_state=42,
    n_jobs=-1              
)

lgb_callbacks = [lgb.early_stopping(stopping_rounds=500, verbose=True)]

lgbm_model.fit(
    X_train_tree, 
    y_train_log,
    eval_set=[(X_val_tree, y_val)],
    categorical_feature=cat_features,
    callbacks=lgb_callbacks
)

lgb_val_pred = lgbm_model.predict(X_val_tree)
lgb_rmse = root_mean_squared_error(y_val, lgb_val_pred)
print(f"/LightGBM Validation RMSE: {lgb_rmse:.5f}")

# %%
joblib.dump(lgbm_model, "lgbm.joblib")

# %%
import xgboost as xgb
from sklearn.metrics import root_mean_squared_error
from pandas.api.types import CategoricalDtype


X_train_tree = X_train_lean.copy()
X_val_tree = X_val_lean.copy()
X_test_tree = X_test_lean.copy()

for col in cat_features:
    all_cats = pd.concat([X_train_tree[col], X_val_tree[col], X_test_tree[col]]).unique()
    
    unified_cat_type = CategoricalDtype(categories=all_cats)
    
    X_train_tree[col] = X_train_tree[col].astype(unified_cat_type)
    X_val_tree[col] = X_val_tree[col].astype(unified_cat_type)
    X_test_tree[col] = X_test_tree[col].astype(unified_cat_type)
print("\n/XGBoost...")
xgb_model = xgb.XGBRegressor(
    n_estimators=12000,       
    learning_rate=0.03,
    max_depth=9,           
    subsample=0.8,
    colsample_bytree=0.8,
    tree_method='hist',    
    enable_categorical=True,
    random_state=42,
    early_stopping_rounds=500,
    eval_metric='rmse'
)

xgb_model.fit(
    X_train_tree, 
    y_train,
    eval_set=[(X_val_tree, y_val)],
    verbose=400
)

xgb_val_pred = xgb_model.predict(X_val_tree)
xgb_rmse = root_mean_squared_error(y_val, xgb_val_pred)
print(f"\n /XGBoost Validation RMSE: {xgb_rmse:.5f}")

# %%


# %%
joblib.dump(xgb_model, "xgb_model.joblib")

# %%
# np.expm1(val_rmse)

# %% [markdown]
# ### Training directly with the Catboost

# %%
# X_train_cb = X_train.copy()
# X_val_cb = X_val.copy()
# X_test_cb = test_df.copy()

# for c in cat_cols:
#     X_train_cb[c] = X_train_cb[c].fillna('Missing').astype(str)
#     X_val_cb[c]   = X_val_cb[c].fillna('Missing').astype(str)
#     X_test_cb[c]  = X_test_cb[c].fillna('Missing').astype(str)
# for c in num_cols:
#     X_train_cb[c] = X_train_cb[c].fillna(X_train_cb[c].median())
#     X_val_cb[c]   = X_val_cb[c].fillna(X_train_cb[c].median())
#     X_test_cb[c]  = X_test_cb[c].fillna(X_train_cb[c].median())

# cb_native = CatBoostRegressor(iterations=3000, learning_rate=0.05, depth=8, l2_leaf_reg=3, random_state=42, verbose=1)
# cb_native.fit(X_train_cb, y_train, cat_features=cat_cols, eval_set=(X_val_cb, y_val), early_stopping_rounds=50)

# %%
import os
import joblib

# joblib.dump(cat_model, "catboost.joblib")

# %%
# cat_model = joblib.load("/kaggle/input/models/kradarsh04/catboost-init/other/default/1/catboost_.joblib")
# np.sqrt(mean_squared_error(y_val, cat_model.predict(X_val_cb)))

# %%


# %%
fi = cat_model.get_feature_importance(prettified=True)
fi

# %%
# import matplotlib.pyplot as plt
# import seaborn as sns

# # 1. Generate validation predictions (Make sure you use your trained model and clean validation set)
# val_pred_log = cat_model.predict(X_val_clean)

# # 2. Build the analysis dataframe
# error_df = X_val_clean.copy()
# error_df['True_Log_Target'] = y_val.values
# error_df['Pred_Log_Target'] = val_pred_log

# # 3. Calculate the residuals (errors)
# error_df['Residual'] = error_df['True_Log_Target'] - error_df['Pred_Log_Target']
# error_df['Abs_Error'] = error_df['Residual'].abs()

# # Let's also look at real dollars to ground our intuition
# error_df['True_Price'] = np.expm1(error_df['True_Log_Target'])
# error_df['Pred_Price'] = np.expm1(error_df['Pred_Log_Target'])
# error_df['Dollar_Error'] = error_df['True_Price'] - error_df['Pred_Price']

# # 4. Isolate the Worst 5% of Predictions
# threshold = error_df['Abs_Error'].quantile(0.95)
# worst_offenders = error_df[error_df['Abs_Error'] > threshold].sort_values('Abs_Error', ascending=False)

# print(f"Total Validation Samples: {len(error_df)}")
# print(f"Analyzing {len(worst_offenders)} Worst Offenders...")

# %%
# import matplotlib.pyplot as plt
# import seaborn as sns

# # Set a clean plot style
# sns.set_theme(style="whitegrid")

# # Create a 2x2 subplot layout for a comprehensive error diagnosis
# fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# # 1. Actual vs. Predicted (Log Scale) with Worst 5% Highlighted
# sns.scatterplot(
#     data=error_df, 
#     x='True_Log_Target', 
#     y='Pred_Log_Target', 
#     alpha=0.5, 
#     color='blue', 
#     label='Normal Predictions', 
#     ax=axes[0, 0]
# )
# sns.scatterplot(
#     data=worst_offenders, 
#     x='True_Log_Target', 
#     y='Pred_Log_Target', 
#     color='red', 
#     alpha=0.7, 
#     label='Worst 5% Offenders', 
#     ax=axes[0, 0]
# )
# axes[0, 0].plot(
#     [error_df['True_Log_Target'].min(), error_df['True_Log_Target'].max()],
#     [error_df['True_Log_Target'].min(), error_df['True_Log_Target'].max()],
#     color='black', linestyle='--', linewidth=2
# )
# axes[0, 0].set_title('Actual vs. Predicted (Log Scale)')
# axes[0, 0].set_xlabel('True Log Target')
# axes[0, 0].set_ylabel('Predicted Log Target')
# axes[0, 0].legend()

# # 2. Residual Plot (Checking for non-constant variance / heteroscedasticity)
# sns.scatterplot(
#     data=error_df, 
#     x='Pred_Log_Target', 
#     y='Residual', 
#     alpha=0.4, 
#     color='purple', 
#     ax=axes[0, 1]
# )
# axes[0, 1].axhline(y=0, color='black', linestyle='--', linewidth=2)
# axes[0, 1].set_title('Residuals vs. Fitted Values')
# axes[0, 1].set_xlabel('Predicted Log Target')
# axes[0, 1].set_ylabel('Residual (True - Pred)')

# # 3. Distribution of Absolute Errors (Log Target)
# sns.histplot(
#     data=error_df, 
#     x='Abs_Error', 
#     kde=True, 
#     color='teal', 
#     ax=axes[1, 0]
# )
# axes[1, 0].axvline(x=threshold, color='red', linestyle=':', linewidth=2, label=f'95th Pctl ({threshold:.3f})')
# axes[1, 0].set_title('Distribution of Absolute Error')
# axes[1, 0].set_xlabel('Absolute Error (Log Scale)')
# axes[1, 0].legend()

# # 4. Dollar Error Distribution (Worst 5% Offenders)
# sns.histplot(
#     data=worst_offenders, 
#     x='Dollar_Error', 
#     kde=True, 
#     color='crimson', 
#     ax=axes[1, 1]
# )
# axes[1, 1].axvline(x=0, color='black', linestyle='--', linewidth=1.5)
# axes[1, 1].set_title('Dollar Error Distribution (Worst 5%)')
# axes[1, 1].set_xlabel('Dollar Error (True Price - Pred Price)')

# plt.tight_layout()
# plt.show()


# %%
# Compare average age and hours
# display(worst_offenders[['AssetAge', 'OperationalHoursMeter', 'HoursPerYear']].describe())
# display(error_df[['AssetAge', 'OperationalHoursMeter', 'HoursPerYear']].describe())

# %%
# What base classes is the model failing on most often?
# print("--- Worst Offenders Base Class ---")
# print(worst_offenders['Spec_BaseClass'].value_counts(normalize=True).head(5))

# print("\n--- Overall Validation Base Class ---")
# print(error_df['Spec_BaseClass'].value_counts(normalize=True).head(5))

# %%
# Positive residual = Model predicted too low. Negative = Model predicted too high.
# sns.histplot(error_df['Residual'], bins=100, kde=True)
# plt.title("Distribution of Residuals")
# plt.show()

# %%
# Example Fix based on discovery:
# X_train['is_risky_vendor_old'] = ((X_train['VendorPartnerID'] == 'Vendor_X') & (X_train['AssetAge'] > 15)).astype(int)

# %% [markdown]
# ## Submission

# %%
preds = np.expm1(cat_model.predict(test_pool))
submission = pd.DataFrame({
    'TransactionID': smpl['TransactionID'],
    'TargetValue': preds
})

submission.to_csv('submission.csv', index=False)

# %%
# df["hours_24_7"] = (((df["entry_yr"] - df["ManufactureYear"])*365*24) + ((pd.to_datetime(df["TransactionDate"]).dt.month)*30 + (pd.to_datetime(df["TransactionDate"]).dt.day))*24)

# %%
# df[["ManufactureYear", "OperationalHoursMeter", "hours_24_7"]]

# %%
# df[df["OperationalHoursMeter"]> df["hours_24_7"]]

# %%
# not_possibles_hr = df["OperationalHoursMeter"] > df["hours_24_7"]

# # set them to NaN
# df.loc[not_possibles_hr, "OperationalHoursMeter"] = np.nan

# %%
# df.drop(["hours_24_7", "entry_yr"], axis = 1, inplace = True)

# %%


# %% [markdown]
# ### Milestones

# %% [markdown]
# ## M3
# 

# %%
# df.head().T

# %%


# %%
# ### M-1

# df_train.shape, df_test.shape

# display(df_train.columns, df_test.columns)
# target = [i for i in df_train.columns if i not in df_test.columns]
# target

# df_train.select_dtypes(["int64", "float64"]).columns

# df_train.loc[:, df_train.isna().sum()>=124800]

# df["OperationalHoursMeter"].isna().sum()/df["OperationalHoursMeter"].count()*100

# y = df['TargetValue']
# X = df.drop(columns=['TargetValue'])

# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
# baseline = DummyRegressor(strategy="mean")

# baseline.fit(X_train, y_train)
# pred = baseline.predict(X_test)

# display(mean_squared_error(y_test, pred))

# mean_absolute_error(y_test, pred)

# r2_score(y_test,pred)

# dummy_pred = baseline.predict(x_test)

# submission = pd.DataFrame({
#     'TransactionID': x_test['TransactionID'],
#     'TargetValue': dummy_pred
# })


# submission.to_csv('dummy_submission.csv', index=False)

# %%



