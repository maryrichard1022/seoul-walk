import pandas as pd
import numpy as np
from scipy.stats import mode
from sklearn.metrics import f1_score
from sklearn.metrics import jaccard_score
from sklearn.model_selection import train_test_split

# 각 행 간의 Jaccard 유사도 계산
def calculate_jaccard_similarity(matrix):
    num_users = matrix.shape[0]
    similarities = np.zeros((num_users, num_users))

    for i in range(num_users):
        for j in range(i, num_users):
            similarity = jaccard_score(matrix.iloc[i], matrix.iloc[j])
            similarities[i, j] = similarity
            similarities[j, i] = similarity

    return similarities


# 정확도를 계산하는 함수 
def f1(y_true, y_pred):
    return f1_score(y_true, y_pred)

# 모델별 정확도를 계산하는 함수 
def score(model):
    id_pairs = zip(x_test['user_id'], x_test['place_id'])
    
    # 예측 값
    y_pred = np.array([model(user, place) for (user, place) in id_pairs]).astype(int)
    #print("y_pred", y_pred)
    
    # 실제 값
    y_true = np.array(x_test['heart'])
    #print("y_true", y_true)
    return f1(y_true, y_pred)



likes = pd.read_csv(f"C:/Users/김가연/Desktop/23-2학기/캡스톤2/data/hearts_data.csv", encoding='UTF-8-SIG')
likes = likes[["place_id", "user_id"]]
likes.loc[:, "heart"] = 1
likes = likes.drop_duplicates(subset=['place_id', 'user_id'], keep='first')


x = likes.copy()
y = likes['user_id']


x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25, stratify=y)

#  train 데이터로 Full matrix 구하기 
likes_matrix = x_train.pivot(index='user_id', columns='place_id', values='heart')

# train set 사용자들의 Cosine similarities 계산
matrix_dummy = likes_matrix.copy().fillna(0)


# 자카드 유사도
user_similarity = calculate_jaccard_similarity(matrix_dummy)
user_similarity = pd.DataFrame(user_similarity, index=likes_matrix.index, columns=likes_matrix.index)

def cf_binary(user_id, place_id):
    if place_id in likes_matrix:

        sim_scores = user_similarity[user_id].copy()   
        place_likes = likes_matrix[place_id].copy()     
        none_likes_idx = place_likes[place_likes.isnull()].index
        place_likes = place_likes.drop(none_likes_idx)
        sim_scores = sim_scores.drop(none_likes_idx)

        if sim_scores.sum() != 0.0:
            predicted_likes = np.dot(sim_scores, place_likes) / sim_scores.sum()
        else:
            predicted_likes = mode(place_likes, keepdims=True).mode[0]
            #predicted_likes = 0.0
        
    else:
        predicted_likes = 0.0 # 특정 장소에 대한 좋아요 없는 경우 예측 불가
    return predicted_likes

# 정확도 계산
print(score(cf_binary))



#####주어진 사용자에 대해 추천받기 
# 전체 데이터로 full matrix와 자가드 유사도 구하기 
likes_matrix = likes.pivot_table(index='user_id', columns='place_id', values='heart')
matrix_dummy = likes_matrix.copy().fillna(0)
user_similarity = calculate_jaccard_similarity(matrix_dummy)
user_similarity = pd.DataFrame(user_similarity, index=likes_matrix.index, columns=likes_matrix.index)


def recommender(user, n_items):
    #현재 사용자의 모든 아이템에 대한 예상 평점 계산
    predictions = []
    liked_index = likes_matrix.loc[user][likes_matrix.loc[user] > 0].index    # 이미 찜하기 누른 장소 인덱스 가져옴
    #print("liked_index", liked_index)
    items = likes_matrix.loc[user].drop(liked_index) # 찜하기 누른 장소 제외하고 추천하기 위해
    #print(items)
    
    for item in items.index:
        predictions.append(cf_binary(user, item))                   # 예상 1, 0계산
    recommendations = pd.Series(data=predictions, index=items.index, dtype=float)
    recommendations = recommendations.sort_values(ascending=False)[:n_items]    # 예상 0, 1중에 랜덤하게 고르기?
    recommendations = recommendations[recommendations==1.0]
    return recommendations



# 52번 사용자에게 추천할 장소
# 최대 장소 10개 가져오도록
print(recommender(user=52, n_items=10))