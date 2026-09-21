# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
%matplotlib inline


# %%
train = pd.read_csv("datasets/train.csv")
test = pd.read_csv("datasets/test.csv")
meta = pd.read_csv("datasets/metadata.csv")

# sample = pd.read_csv("datasets/sample.csv")

# %%
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

# %%
df["ProductConfigID"] = df["ProductConfigID"].astype("object")
df["AssetID"] = df["AssetID"].astype("object")

# %%
# df["ManufactureYear"].unique()

# %%
df["ManufactureYear"] = df["ManufactureYear"].replace(1001, np.nan)

# %% [markdown]
# feature engg

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

# %%
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
# df["LogOperationalHoursMeter"] = np.log1p(df["OperationalHoursMeter"])
df["AgeBucket"] = pd.qcut(df["AssetAge"],q=5,duplicates="drop")

# %%
df["Base_Function"]=(df["Spec_BaseClass"].astype(str)+ "_"+ df["FunctionalClassification"].astype(str))
df["Base_Region"]=(df["Spec_BaseClass"].astype(str)+ "_"+ df["RegionCode"].astype(str))
# df["Vendor_Product"]=(df["VendorPartnerID"].astype(str)+ "_"+ df["Spec_BaseClass"].astype(str)) #ni
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
specs_col = ["Spec_SubClass","Spec_ReleaseSeries","Spec_VariantModifier"]
col_block_1 = ["col3", "col10"]
col_block_2 = ["col15", "col20", "col21", "col22", "col23", "col24", "col25"]

df["spec_missing_cnt"] = df[specs_col].isna().sum(axis=1)
# df["col3_col10_missing_cnt"] = df[col_block_1].isna().sum(axis=1) #no importance
# df["col15_25_missing_cnt"] = df[col_block_2].isna().sum(axis=1)
# df["specs_complete"] = (df[specs_col].notna().all(axis=1).astype(int))

# %%
to_remove = train.columns[train.isna().mean()>0.8].to_list() #removing data with more than 80% missing values

# %%
df.drop(["TransactionDate", "AssetID"]+to_remove, axis = 1, inplace = True) #"AssetID", "TransactionID" can be removed 

# %% [markdown]
# ### Imputation

# %%
cat_cols = df.select_dtypes(include = ["object","str"]).columns.to_list()
num_cols = [i for i in df.columns if (i not in cat_cols + ["TargetValue", "is_train"])]
num_cols, cat_cols

# %%
df.isna().sum()

# %%
df.dtypes

# %% [markdown]
# #### Checking the correlations 

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
for i in ['col3', 'col10', 'col15', 'col20', 'Spec_ReleaseSeries', 'AssetScaleFactor']:
    print(i)
    print(train.groupby('InventoryGroupCategory')[i].apply(lambda x: x.isna().mean()))
    print()

# %% [markdown]
# #### saparating the columns into 2 types one with low cardinality and the other with high cardinality

# %%
cat1_cols = [i for i in df[cat_cols].columns if df[i].nunique() <= 20]
cat2_cols = [i for i in df[cat_cols].columns if df[i].nunique() > 20]

[i for i in num_cols+cat1_cols+cat2_cols if i not in df.columns.to_list()]

# %%
len(num_cols+cat1_cols+cat2_cols), len(df.columns.to_list()) #these are na "TargetValue", "is_train"

# %% [markdown]
# #### df -> train + test back

# %%
train_df = df[df["is_train"]==1].drop(['is_train'], axis = 1).copy()
test_df = df[df["is_train"]==0].drop(['is_train', 'TargetValue'], axis = 1).copy()

# %%
train.shape, train_df.shape, test.shape, test_df.shape

# %% [markdown]
# ## Data Preprocessing

# %%
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
# print("These are all the cat cols:", cat_cols)

# %%
from sklearn.compose import ColumnTransformer

preprocessor = ColumnTransformer([
    ('num', num_pipe, num_cols),
    ('low_card', cat1_pipe, cat1_cols),
    ('high_card', cat2_pipe, cat2_cols),
], remainder='drop')

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
# X_train_fnl= preprocessor.fit_transform(X_train, y_train)
# X_val_fnl = preprocessor.transform(X_val)
# X_test_fnl = preprocessor.transform(test_df)

# %%
# preprocessor

# %%
# drop_model_cols = ["TransactionID", "AssetID"]

X_train = X_train.drop(["TransactionID"], errors="ignore")
X_val   = X_val.drop(["TransactionID"], errors="ignore")
X_test  = X_test.drop(["TransactionID"], errors="ignore")

# %%
product_freq = X_train["ProductConfigID"].value_counts()
vendor_freq = X_train["VendorPartnerID"].value_counts()
baseclass_freq = X_train["Spec_BaseClass"].value_counts()
region_freq = X_train["RegionCode"].value_counts()
func_freq = X_train["FunctionalClassification"].value_counts()

for d in [X_train, X_val, X_test]:
    d["ProductFreq"] = d["ProductConfigID"].map(product_freq).fillna(0)
    d["VendorFreq"] = d["VendorPartnerID"].map(vendor_freq).fillna(0)
    d["BaseClassFreq"] = d["Spec_BaseClass"].map(baseclass_freq).fillna(0)
    d["RegionFreq"] = d["RegionCode"].map(region_freq).fillna(0)
    d["FuncFreq"] = d["FunctionalClassification"].map(func_freq).fillna(0)

# %%
# by base class + age bucket
train_expected = (X_train.groupby(["Spec_BaseClass", "AgeBucket"], observed=True)["OperationalHoursMeter"].median().replace(0, np.nan))

for d in [X_train, X_val, X_test]:
    idx = d.set_index(["Spec_BaseClass", "AgeBucket"]).index
    expected = idx.map(train_expected)
    d["UsageRatio"] = d["OperationalHoursMeter"] / expected
    d["UsageRatio"] = d["UsageRatio"].replace([np.inf, -np.inf], np.nan).fillna(1.0)

# %%
base_hours_median = (
    X_train.groupby("Spec_BaseClass", observed=True)["OperationalHoursMeter"]
    .median()
    .replace(0, np.nan)
)

global_hours_median = X_train["OperationalHoursMeter"].median()

for d in [X_train, X_val, X_test]:
    expected_base = d["Spec_BaseClass"].map(base_hours_median).fillna(global_hours_median)
    d["Hours_vs_BaseMedian"] = d["OperationalHoursMeter"] / expected_base
    d["Hours_vs_BaseMedian"] = d["Hours_vs_BaseMedian"].replace([np.inf, -np.inf], np.nan).fillna(1.0)

# %%
X_train.dtypes

# %%
cat_cols = X_train.select_dtypes(include=["object", "str", "category"]).columns.tolist()
num_cols = X_train.select_dtypes(include=["int", "float"]).columns.tolist()

for d in [X_train, X_val, X_test]:
    d[cat_cols] = d[cat_cols].astype(str).replace("nan", "Missing")

for d in [X_train, X_val, X_test]:
    d[cat_cols] = d[cat_cols].fillna("Missing").astype(str)
    for c in num_cols:
        d[c] = d[c].fillna(X_train[c].median())

# %%
cat_features = X_train.select_dtypes(include="str").columns.tolist()
cat_features

# %% [markdown]
# ### Visualizing the data

# %%
# %matplotlib inline
# for i in num_cols:
#     plt.title(f"{i} v/s frequency")
#     # print(i)
#     sns.histplot(data=train_df, x=i)
#     plt.show()

# %% [markdown]
# ### Boxplots

# %%
# %matplotlib inline
# for i in num_cols:
#     plt.title(f"{i} v/s frequency")
#     # print(i)
#     sns.boxplot(data=train_df, y=i)
#     plt.show()

# %% [markdown]
# ## Model

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
    "catboost": CatBoostRegressor(iterations=500, learning_rate=0.05, depth=6, verbose=1, random_state=42),
}

# %%
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score 
results = []

# for name, model in models.items():
#     print(model, "----\n")

#     model.fit(X_train_fnl, y_train)
#     preds = model.predict(X_val_fnl)

#     results.append({
#         "Model": name,
#         "MAE": mean_absolute_error(y_val, preds),
#         "RMSE": np.sqrt(mean_squared_error(y_val, preds)),
#         "R2": r2_score(y_val, preds)
#     })

# results_df = (
#     pd.DataFrame(results).sort_values("RMSE").reset_index(drop=True)
# )


# %%
# results_df

# %%
cat_model = CatBoostRegressor(
    iterations=3000,
    learning_rate=0.05,
    depth=10,
    l2_leaf_reg=3,
    random_state=42,
    verbose=5
)

cat_model.fit(
    X_train,
    y_train,
    cat_features=cat_features,
    eval_set=(X_val, y_val),
    early_stopping_rounds=50
)

val_pred_log = cat_model.predict(X_val)
val_rmse = np.sqrt(mean_squared_error(y_val, val_pred_log))
print("Validation RMSE (log space):", val_rmse)

# %%
from lightgbm import LGBMRegressor
from sklearn.metrics import mean_squared_error
import numpy as np

X_train_lgb = X_train.copy()
X_val_lgb   = X_val.copy()
X_test_lgb  = X_test.copy()

drop_cols = ["TransactionID", "AssetID"]
for d in [X_train_lgb, X_val_lgb, X_test_lgb]:
    d.drop(columns=drop_cols, errors="ignore", inplace=True)

cat_cols = X_train_lgb.select_dtypes(include=["object", "category"]).columns.tolist()
num_cols = X_train_lgb.select_dtypes(include=["number"]).columns.tolist()

for d in [X_train_lgb, X_val_lgb, X_test_lgb]:
    d[cat_cols] = d[cat_cols].fillna("Missing").astype("category")
    for c in num_cols:
        d[c] = d[c].fillna(X_train_lgb[c].median())

lgb = LGBMRegressor(
    n_estimators=5000,
    learning_rate=0.02,
    num_leaves=128,
    subsample=0.8,
    colsample_bytree=0.8,
    device="cpu",
    n_jobs=-1,
    random_state=42
)

lgb.fit(
    X_train_lgb, y_train,
    eval_set=[(X_val_lgb, y_val)],
    eval_metric="rmse"
)

preds_lgb = lgb.predict(X_val_lgb)
rmse_lgb = np.sqrt(mean_squared_error(y_val, preds_lgb))
print(rmse_lgb)

# %%
# from xgboost import XGBRegressor

# X_train_xgb = X_train.copy()
# X_val_xgb   = X_val.copy()
# X_test_xgb  = X_test.copy()
# # 
# for d in [X_train_xgb, X_val_xgb, X_test_xgb]:
#     d.drop(columns=drop_cols, errors="ignore", inplace=True)

# cat_cols = X_train_xgb.select_dtypes(include=["object", "category"]).columns.tolist()
# num_cols = X_train_xgb.select_dtypes(include=["number"]).columns.tolist()

# for d in [X_train_xgb, X_val_xgb, X_test_xgb]:
#     d[cat_cols] = d[cat_cols].fillna("Missing").astype("category")
#     for c in num_cols:
#         d[c] = d[c].fillna(X_train_xgb[c].median())


# %%

# xgb = XGBRegressor(
#     n_estimators=5000,
#     learning_rate=0.03,
#     max_depth=8,
#     subsample=0.8,
#     colsample_bytree=0.8,
#     reg_lambda=1.0,
#     tree_method="hist",
#     enable_categorical=True,
#     random_state=42
# )

# xgb.fit(
#     X_train_xgb, y_train,
#     eval_set=[(X_val_xgb, y_val)],
#     verbose=200
# )

# preds_xgb = xgb.predict(X_val_xgb)
# rmse_xgb = np.sqrt(mean_squared_error(y_val, preds_xgb))
# print(rmse_xgb)

# %%
cat_cols = X_train_xgb.select_dtypes(include=["category"]).columns.tolist()

print(cat_cols)
print(cat_cols[0])

# %%
col = cat_cols[0]

train_vals = set(X_train_xgb[col].astype(str).unique())
val_vals   = set(X_val_xgb[col].astype(str).unique())

print("Unseen:", len(val_vals - train_vals))
print(list(val_vals - train_vals)[:20])

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

# cb_native = CatBoostRegressor(iterations=3000, learning_rate=0.05, depth=10, l2_leaf_reg=3, random_state=42, verbose=1)
# cb_native.fit(X_train_cb, y_train, cat_features=cat_cols, eval_set=(X_val_cb, y_val), early_stopping_rounds=50)

# %%
# for d in [8, 10]:
#     print(f"Training CatBoostRegressor with depth={d}")
#     m = CatBoostRegressor(iterations=3000, learning_rate=0.05, depth=d, l2_leaf_reg=3, random_state=42, verbose=1)
#     m.fit(X_train_cb, y_train, cat_features=cat_cols, eval_set=(X_val_cb, y_val), early_stopping_rounds=100)
    
#     print(d, m.get_best_score())

# %%
import os
import joblib

# os.makedirs("models", exist_ok=True)
# joblib.dump(cat_model, "catboost_1.joblib")

# %%
cat_model = joblib.load("catboost_1.joblib")

# %%
fi = cat_model.get_feature_importance(prettified=True)
fi

# %%
# dir(cat_model.feature_importances_)

# %% [markdown]
# ### Residue Analysis

# %%
preds = cat_model.predict(X_val)
residuals = np.expm1(y_val) - np.expm1(preds)

# %%
residuals.sort_values(ascending=False).head(20)

# %%
val_pred_log = cat_model.predict(X_val)
residual_log = y_val - val_pred_log
abs_resid_log = np.abs(residual_log)

# %%
residual_log.describe()

# %%
abs_resid_log.describe()

# %%
y_val_raw = np.expm1(y_val)
val_pred_raw = np.expm1(val_pred_log)

residual_raw = y_val_raw - val_pred_raw
abs_resid_raw = np.abs(residual_raw)

# %%
residual_raw.describe()

# %%
abs_resid_raw.describe()

# %%
X_train["AssetID"].shape

# %%
res_df = X_val_cb.copy()
res_df["y_true_log"] = y_val.values
res_df["y_pred_log"] = val_pred_log
res_df["residual_log"] = residual_log
res_df["abs_residual_log"] = abs_resid_log

res_df["y_true_raw"] = y_val_raw
res_df["y_pred_raw"] = val_pred_raw
res_df["residual_raw"] = residual_raw
res_df["abs_residual_raw"] = abs_resid_raw

res_df.sort_values("abs_residual_raw", ascending=False).head(20)

# %%
val_pred_log = cat_model.predict(X_val_cb)
residual_log = y_val - val_pred_log

res_df = X_val_cb.copy()
res_df["y_true_log"] = y_val.values
res_df["y_pred_log"] = val_pred_log
res_df["residual_log"] = residual_log
res_df["abs_residual_log"] = np.abs(residual_log)

res_df["y_true_raw"] = np.expm1(y_val)
res_df["y_pred_raw"] = np.expm1(val_pred_log)
res_df["residual_raw"] = res_df["y_true_raw"] - res_df["y_pred_raw"]
res_df["abs_residual_raw"] = np.abs(res_df["residual_raw"])

# %%
display(res_df.groupby(pd.cut(res_df["AssetAge"], bins=[-np.inf, 0, 5, 10, 20, np.inf]))["abs_residual_log"].mean())
display(res_df.groupby("ProductConfigID")["abs_residual_log"].mean().sort_values(ascending=False).head(20))
display(res_df.groupby("FunctionalClassification")["abs_residual_log"].mean().sort_values(ascending=False).head(20))
display(res_df.groupby("RegionCode")["abs_residual_log"].mean().sort_values(ascending=False).head(20))

# %%
preds = np.expm1(cat_model.predict(X_test_cb))

# %%
submission = pd.DataFrame({
    'TransactionID': X_test['TransactionID'],
    'TargetValue': preds
})
submission.to_csv('submission.csv', index=False)

# %%



