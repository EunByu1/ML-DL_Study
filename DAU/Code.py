#!/usr/bin/env python
# coding: utf-8

# ---
# # 01. Data Preparation
# ---

# In[1]:


import pandas as pd

# 데이터 불러오기(인코딩)
CancerData = pd.read_csv("cancer_reg.csv", encoding="utf-8")


# In[2]:


# 중복되는 행 제거
CancerData = CancerData.drop_duplicates()


# ---
# # 02. Data Checking
# ---

# In[3]:


# 데이터 형태 확인 
CancerData.head()


# In[4]:


# 데이터 프레임의 행을 랜덤하게 섞음
CancerData = CancerData.sample(frac=1).reset_index(drop=True)


# In[5]:


# DataFrame의 columns 확인
CancerData.columns


# In[6]:


# 데이터 정보 확인하기 
CancerData.info() 


# In[7]:


# DataFrame 전체의 결측치 갯수 확인
CancerData.isna().sum()


# In[9]:


import matplotlib.pyplot as plt

# FeatureData & TargetData
FeatureData = ['avgAnnCount', 'avgDeathsPerYear', 'incidenceRate', 'medIncome',
       'popEst2015', 'povertyPercent', 'studyPerCap', 'MedianAge',
       'MedianAgeMale', 'MedianAgeFemale', 'AvgHouseholdSize',
       'PercentMarried', 'PctNoHS18_24', 'PctHS18_24', 'PctBachDeg18_24',
       'PctHS25_Over', 'PctBachDeg25_Over', 'PctUnemployed16_Over',
       'PctPrivateCoverage', 'PctEmpPrivCoverage', 'PctPublicCoverage',
       'PctPublicCoverageAlone', 'PctWhite', 'PctBlack', 'PctAsian',
       'PctOtherRace', 'PctMarriedHouseholds', 'BirthRate']
TargetData = ['TARGET_deathRate']

# DataFrame의 value 추출
X = CancerData[FeatureData].values
y = CancerData[TargetData].values

# 산점도 그리기
num_features = len(FeatureData)
num_cols = 6  # 열의 개수 조정
num_rows = num_features // num_cols + 1

fig, axes = plt.subplots(num_rows, num_cols, figsize=(20,10))

for i, feature in enumerate(FeatureData):
    row = i // num_cols
    col = i % num_cols
    axes[row, col].scatter(X[:, i], y)
    axes[row, col].set_xlabel(feature)
    axes[row, col].set_ylabel('TARGET_deathRate')

# 빈 서브플롯 숨기기
if num_features % num_cols != 0:
    for j in range(num_features % num_cols, num_cols):
        fig.delaxes(axes[-1, j])

plt.tight_layout()
plt.show()


# ---
# # 03. Linear Regression : L2 Regularization [Ridge]
# ---

# 
# ###  * FeatureData & TargetData 형태 확인
# ``` 
# FeatureData = ['avgAnnCount', 'avgDeathsPerYear', 'incidenceRate', 'medIncome',
#        'popEst2015', 'povertyPercent', 'studyPerCap', 'MedianAge',
#        'MedianAgeMale', 'MedianAgeFemale', 'AvgHouseholdSize',
#        'PercentMarried', 'PctNoHS18_24', 'PctHS18_24', 'PctBachDeg18_24',
#        'PctHS25_Over', 'PctBachDeg25_Over', 'PctUnemployed16_Over',
#        'PctPrivateCoverage', 'PctEmpPrivCoverage', 'PctPublicCoverage',
#        'PctPublicCoverageAlone', 'PctWhite', 'PctBlack', 'PctAsian',
#        'PctOtherRace', 'PctMarriedHouseholds', 'BirthRate']
# TargetData = ['TARGET_deathRate']
# 
# X = CancerData[FeatureData].values
# y = CancerData[TargetData].values
# ```

# In[15]:


import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler

n_runs = 10
rmse_list = []
r2_list = []
optimal_reg_alpha_list = []
l2_weights = []

for epoch in range(n_runs):
    # reg_model 정의
    reg_model = Ridge()

    # 데이터 분할 - Training Data 80%, Validation Data 10%, Test Data 10%
    X_trainval, X_test, y_trainval, y_test = train_test_split(X, y, test_size=0.1)
    X_train, X_evaluation, y_train, y_evaluation = train_test_split(X_trainval, y_trainval, test_size=0.1)

    # Feature 정규화
    scaler = StandardScaler()
    X_train_normalized = scaler.fit_transform(X_train)
    X_evaluation_normalized = scaler.transform(X_evaluation)

    # 10 epoch 동안 L2 정규화 가중치 계산 및 저장
    reg_model.fit(X_train_normalized, y_train)
    l2_weights.append(reg_model.coef_)

    # 검증 데이터를 사용하여 모델 평가
    val_score = reg_model.score(X_evaluation_normalized, y_evaluation)
    y_pred = reg_model.predict(X_evaluation_normalized)
    print(f"[ Epoch {epoch+1} ]")

    mse = mean_squared_error(y_evaluation, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_evaluation, y_pred)

    print('RMSE:', rmse)
    print('R2 Score:', r2)


# In[16]:


# 저장된 가중치의 평균 계산
avg_l2_weight = np.mean(l2_weights, axis=0)

# 저장된 가중치의 평균과 편향 계산
avg_bias = np.mean(y_train)

# 최종 모델 생성 및 L2 정규화 가중치 및 편향 설정
final_ridge_model = Ridge(alpha=1.0)  # 기본 alpha 값으로 초기화
final_ridge_model.coef_ = avg_l2_weight
final_ridge_model.intercept_ = avg_bias

# 테스트 데이터를 사용하여 최종 모델 평가
X_test_normalized = scaler.transform(X_test)
y_pred = final_ridge_model.predict(X_test_normalized)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)

print('[ 최종 RMSE와 R2 Score를 사용하여 학습된 Model을 평가 ]')
print('RMSE:', rmse)
print('R2 Score:', r2)
print('avg_l2_weight:', avg_l2_weight)
print('avg_bias:', avg_bias) 


# ---
# # 04. Relevance: Statistics Indicators & TARGET_deathRate
# ---

# In[17]:


# Feature와 TARGET_deathRate 사이의 관련성 계산
correlation = []
for i, feature in enumerate(FeatureData):
    feature_values = X[:, i].reshape(-1, 1)
    correlation_value = np.corrcoef(feature_values.flatten(), y.flatten())[0, 1]
    correlation.append(correlation_value)

# 가중치와 관련성 출력
print('[ 피처와 TARGET_deathRate와의 관련성 및 가중치 ]')
for i, (feature, weight, corr) in enumerate(zip(FeatureData, final_ridge_model.coef_.reshape(-1), correlation)):
    print(f'{i+1}. "{feature}"의 상관 계수 : {corr}')
    print(f'Weight {i+1}: {weight}')

    if corr < 0:
        print(">> 음의 선형 관계")
    else:
        print(">> 양의 선형 관계")
    print()


# In[18]:


# 막대 그래프로 관련성과 가중치 시각화
x = range(len(FeatureData))
width = 0.35

fig, ax = plt.subplots()
ax.bar(x, correlation, width, label='Correlation')
ax.bar(x, final_ridge_model.coef_.reshape(-1), width, label='Weight')

ax.set_xlabel('Features')
ax.set_ylabel('Correlation / Weight')
ax.set_title('Correlation and Weight between Features and TARGET_deathRate')
ax.set_xticks(x)
ax.set_xticklabels(FeatureData, rotation=90)
ax.legend()

plt.tight_layout()
plt.show()

