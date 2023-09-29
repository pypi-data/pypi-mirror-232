from functools import lru_cache
from random import randint, choice

import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import make_scorer
from sklearn.model_selection import GridSearchCV

def extract_one(data, key):
    series = pd.Series(data[key], dtype=float)
    return series

def train_with_forest(data: pd.DataFrame, train_params, scorer, y_true) -> IsolationForest:
    forest = IsolationForest()
    clf = GridSearchCV(forest, train_params, scoring=scorer, verbose=2, cv=4)
    clf.fit(data.values, y_true)
    return clf.best_estimator_

def scorer(estimator, X_test, y_test):
    y_score = estimator.decision_function(X_test)
    return roc_auc_score(y_test, y_score)

def unknown_pref_metric(y_true, y_pred):
    correct_preds_r = sum(y_true & y_pred)
    trues = sum(y_true)
    return (correct_preds_r / trues) * 100


unknown_pref_scorer = make_scorer(unknown_pref_metric, greater_is_better=True)


def get_stat_param_func(data):
    @lru_cache
    def get_stat_param(feature, param):
        return getattr(data[feature], param)()
    
    return get_stat_param


def generate_random_rows(data, count):
    get_param = get_stat_param_func(data)
    rows = []
    for _ in range(count):
        row = {}
        for feature in data.columns:
            feature_mean = get_param(feature, 'mean')
            feature_std = get_param(feature, 'std')
            has_negative = get_param(feature, 'min') < 0
            mults = [-1, 1] if has_negative else [1]
            value = feature_mean + feature_std * (randint(1000, 2000) / 1000) * choice(mults)
            row[feature] = value
        rows.append(row)
    return rows


def append_rows(data, rows):
    return data.append(rows, ignore_index=True)


def unknown_and_custom_loss(model, x, true_is_anomaly):
    scores = model.score_samples(x)
    scores_order = scores.argsort()
    len_for_check = 3000
    found = 0

    for i in scores_order[:len_for_check]:
        if true_is_anomaly.iloc[i]:
            found += 1

    return (found / len_for_check) * 100
