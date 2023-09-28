import pandas as pd
import numpy as np
import re
import os
import copy
from datetime import datetime
import pickle as pkl
import shelve
import pandas as pd
import math
from datetime import timedelta
from typing import Union, List
import lightgbm
from lightgbm import LGBMRanker
import matplotlib.pyplot as plt
import warnings
import shutil
import os
warnings.filterwarnings("ignore")


def recall_at_k (predictions, cdf, k):

    num = len(cdf.columns)
    predictions.fillna(np.nan , inplace=True)
    result_sub=pd.merge(cdf, predictions, on='customers_id')
    result_sub=result_sub.drop_duplicates()
    result_sub=result_sub.replace(np.nan, 0)
    P=0
    for col2 in result_sub.iloc[:,num:]:  
        P=P+1
        result_sub[col2]=result_sub[col2].replace(0, 'not_pred'+str(P))
    
    l=0
    for col1 in result_sub.iloc[:,1:num+1]:
        l=l+1
        result_sub[col1]=result_sub[col1].replace(0, 'not_bought'+str(l))
    
    dfwci=result_sub.drop('customers_id',axis=1)
    df_ = dfwci.T
    for col in df_.columns:
        duplicated = df_.duplicated(col) & df_[col].notnull()
        df_.loc[duplicated, col] = 'True Predict'  
    check=df_.T
    column_prefix = 'p_Item'
    start_column = 1
    end_column = k
    columns_to_keep = [f'{column_prefix} {i}' for i in range(start_column, end_column + 1)]
    check = check[columns_to_keep]
    check.insert(0, "customers_id", result_sub['customers_id'])
    allowed_patterns = [f'not_pred{i}' for i in range(1, len(predictions.columns)+1)]
    
    def condition(x):
        x_str = str(x) 
        if x_str == 'True Predict':
            return "True Predict"
        elif any(re.match(pattern, x_str) for pattern in allowed_patterns):
            return "No Predict"
        else:
            return 'False Predict'
    columns_to_apply_condition=[]
    for i in range(k):
        columns_to_apply_condition.append('p_Item '+str(i+1))

    for column in columns_to_apply_condition:
        check[column] = check[column].apply(condition)

    columns_to_apply_condition = columns_to_apply_condition[1:]
    met = check['p_Item 1']
    for column in columns_to_apply_condition:
        met = pd.concat([met, check[column]], ignore_index=True)
    print('Recall@'+str(k),met.value_counts())
    met = met.value_counts().reset_index()
    n_True = met.loc[met['index']=='True Predict'].iloc[0, 1]
    n_False = met.loc[met['index']=='False Predict'].iloc[0, 1]
    if 'No Predict' in met['index'].values:
        n_no_predict = met.loc[met['index'] == 'No Predict'].iloc[0, 1]
    else:
        n_no_predict=0
    map4 =100*  n_True/(n_False+n_True + n_no_predict)
    print('Recall@'+str(k)+": ",str(map4))


def one_hit_accuracy (predictions, cdf):
    k=1
    num = len(cdf.columns)
    predictions.fillna(np.nan , inplace=True)
    result_sub=pd.merge(cdf, predictions, on='customers_id')
    result_sub=result_sub.drop_duplicates()
    result_sub=result_sub.replace(np.nan, 0)
    P=0
    for col2 in result_sub.iloc[:,num:]:  
        P=P+1
        result_sub[col2]=result_sub[col2].replace(0, 'not_pred'+str(P))
    
    l=0
    for col1 in result_sub.iloc[:,1:num+1]:
        l=l+1
        result_sub[col1]=result_sub[col1].replace(0, 'not_bought'+str(l))
    
    dfwci=result_sub.drop('customers_id',axis=1)
    df_ = dfwci.T
    for col in df_.columns:
        duplicated = df_.duplicated(col) & df_[col].notnull()
        df_.loc[duplicated, col] = 'True Predict'  
    check=df_.T
    column_prefix = 'p_Item'
    start_column = 1
    end_column = k
    columns_to_keep = [f'{column_prefix} {i}' for i in range(start_column, end_column + 1)]
    check = check[columns_to_keep]
    check.insert(0, "customers_id", result_sub['customers_id'])
    allowed_patterns = [f'not_pred{i}' for i in range(1, len(predictions.columns)+1)]
    
    def condition(x):
        x_str = str(x) 
        if x_str == 'True Predict':
            return "True Predict"
        elif any(re.match(pattern, x_str) for pattern in allowed_patterns):
            return "No Predict"
        else:
            return 'False Predict'
    columns_to_apply_condition=[]
    for i in range(k):
        columns_to_apply_condition.append('p_Item '+str(i+1))

    for column in columns_to_apply_condition:
        check[column] = check[column].apply(condition)

    met1 = check['p_Item 1']
    print('One-hit accuraccy = ',met1.value_counts())
    met1 = met1.value_counts().reset_index()
    n_True = met1.loc[met1['index']=='True Predict'].iloc[0, 1]
    if 'False Predict' in met1['index'].values:
        n_False = met1.loc[met1['index']=='False Predict'].iloc[0, 1]
    else:
        n_False=0

    if 'No Predict' in met1['index'].values:
        n_no_predict = met1.loc[met1['index'] == 'No Predict'].iloc[0, 1]
    else:
        n_no_predict=0
    map1 =100*  n_True/(n_False+n_True+n_no_predict)
    cutomers_num = (n_False+n_True+n_no_predict)
    print('One-hit accuracy = ',str(map1))

import pandas as pd
import numpy as np
import re

def topk (predictions, cdf, k):

    num = len(cdf.columns)
    predictions.fillna(np.nan , inplace=True)
    result_sub=pd.merge(cdf, predictions, on='customers_id')
    result_sub=result_sub.drop_duplicates()
    result_sub=result_sub.replace(np.nan, 0)
    P=0
    for col2 in result_sub.iloc[:,num:]:  
        P=P+1
        result_sub[col2]=result_sub[col2].replace(0, 'not_pred'+str(P))
    
    l=0
    for col1 in result_sub.iloc[:,1:num+1]:
        l=l+1
        result_sub[col1]=result_sub[col1].replace(0, 'not_bought'+str(l))
    
    dfwci=result_sub.drop('customers_id',axis=1)
    df_ = dfwci.T
    for col in df_.columns:
        duplicated = df_.duplicated(col) & df_[col].notnull()
        df_.loc[duplicated, col] = 'True Predict'  
    check=df_.T
    column_prefix = 'p_Item'
    start_column = 1
    end_column = k
    columns_to_keep = [f'{column_prefix} {i}' for i in range(start_column, end_column + 1)]
    check = check[columns_to_keep]
    check.insert(0, "customers_id", result_sub['customers_id'])
    allowed_patterns = [f'not_pred{i}' for i in range(1, len(predictions.columns)+1)]
    
    def condition(x):
        x_str = str(x) 
        if x_str == 'True Predict':
            return "True Predict"
        elif any(re.match(pattern, x_str) for pattern in allowed_patterns):
            return "No Predict"
        else:
            return 'False Predict'
    columns_to_apply_condition=[]
    for i in range(k):
        columns_to_apply_condition.append('p_Item '+str(i+1))

    for column in columns_to_apply_condition:
        check[column] = check[column].apply(condition)
    def check_for_one(row):
        return 'True Predict' if 'True Predict' in row.values else 'False Predict'
    top4 = check.apply(check_for_one, axis=1)
    
    print('top@'+str(k)+': ',top4.value_counts())
    top4 = top4.value_counts().reset_index()
    n_True = top4.loc[top4['index']=='True Predict'].iloc[0, 1]
    if 'False Predict' in top4['index'].values:
        n_False = top4.loc[top4['index']=='False Predict'].iloc[0, 1]
    else:
        n_False=0
    if 'No Predict' in top4['index'].values:
        n_no_predict = top4.loc[top4['index'] == 'No Predict'].iloc[0, 1]
    else:
        n_no_predict=0
    top4 =100*  n_True/(n_False+n_True+n_no_predict)
    print('top@'+str(k)+': ',str(top4))

def rs(transactions_df, target_week):
    folder_name = 'Aras_RS'
    if os.path.exists(folder_name):
        shutil.rmtree(folder_name)
    os.mkdir(folder_name)
    def reduce_customer_id_memory(customers_df, other_dfs):
        index_to_id_dict = customers_df["customers_id"]
        file_path = "Aras_RS/id_to_index_dict.pkl"
        with open(file_path, "wb") as f:
            pkl.dump(index_to_id_dict, f)
        del index_to_id_dict

        id_to_index_dict = customers_df.reset_index().set_index("customers_id")["index"]
        customers_df["customers_id"] = (
            customers_df["customers_id"].map(id_to_index_dict).astype("int64")
        )

        for other_df in other_dfs:
            if "customers_id" in other_df:
                other_df["customers_id"] = (
                    other_df["customers_id"].map(id_to_index_dict).astype("int64")
                )
        return file_path
    def day_numbers(dates: pd.Series):
        
        pd_dates = pd.to_datetime(dates)
        unique_dates = pd.Series(pd_dates.unique())
        unique_dates = np.sort(unique_dates)
        number_range = np.arange(len(unique_dates))
        date_number_dict = dict(zip(unique_dates, number_range))

        all_day_numbers = dates.map(date_number_dict)
        all_day_numbers = all_day_numbers.astype("int16")

        return all_day_numbers
    def day_week_numbers(dates):
        day_weeks = dates//7
        return day_weeks

    def how_many_ago(sequential_numbers: pd.Series):
        return sequential_numbers - sequential_numbers.max()
    
    def feature_label_split(
        transactions_df: pd.DataFrame,
        label_week_number: int,
        feature_week_length=None,
    ):
        label_df = transactions_df.query(f"week_number=={label_week_number}").copy()
        features_df = transactions_df.query(f"week_number < {label_week_number}").copy()
        if feature_week_length is not None:
            features_df = features_df.query(
                f"week_number >= {label_week_number - feature_week_length}"
            ).copy()

        return features_df, label_df
    def report_candidates(candidates: List[str], ground_truth_candidates: List[str]):

        num_candidates = len(candidates)
        num_ground_truth = len(ground_truth_candidates)
        all_candidates = pd.concat(
            [ground_truth_candidates, candidates]
        ).drop_duplicates()
        num_true_candidates = num_candidates + num_ground_truth - len(all_candidates)
        recall = num_true_candidates / num_ground_truth
        precision = num_true_candidates / num_candidates
        return recall, precision


    def comp_average_precision(
        data_true: pd.Series,
        data_predicted: pd.Series,
    ) -> float:

        data_true = data_true.apply(list)
        data_predicted = data_predicted.apply(list)
        data_true = data_true[data_true.notna()]
        data_true = data_true[data_true.apply(len) > 0]

        if len(data_true) == 0:
            raise ValueError("data_true is empty")

        eval_df = pd.DataFrame({"true": data_true})

        eval_df["predicted"] = data_predicted  
        eval_df["predicted"] = eval_df["predicted"].apply(
            lambda x: x if isinstance(x, list) else []
        )

        eval_df["n_items_true"] = eval_df["true"].apply(len)
        eval_df["n_items_predicted"] = eval_df["predicted"].apply(lambda x: min(len(x), 4))

        non_zero_filter = eval_df["n_items_predicted"] > 0
        eval_df = eval_df[non_zero_filter].copy()

        def row_precision(items_true, items_predicted, n_items_predicted, n_items_true):
            n_correct_items = 0
            precision = 0.0

            for item_idx in range(n_items_predicted):
                if items_predicted[item_idx] in items_true:
                    n_correct_items += 1
                    precision += n_correct_items / (item_idx + 1)

            return precision / min(n_items_true, 4)

        eval_df["row_precision"] = eval_df.apply(
            lambda x: row_precision(
                x["true"], x["predicted"], x["n_items_predicted"], x["n_items_true"]
            ),
            axis=1,
        )

        return eval_df["row_precision"].sum() / len(data_true)
    def cudf_groupby_head(df, groupby, head_count):
        

        head_df = df.groupby(groupby).head(head_count)

        head_df = pd.DataFrame(head_df)

        return head_df
    def create_recent_customer_candidates(
        transactions_df, recent_customer_weeks, customers=None
    ):
        if customers is not None:
            transactions_df = transactions_df[
                transactions_df["customers_id"].isin(customers)
            ]

        last_week_number = transactions_df["week_number"].max()

        recent_customer_df = (
            transactions_df.groupby(["customers_id", "articles_id"])
            .agg(
                {
                    "week_number": "max",
                    "d_dat": "max", 
                }
            )
            .rename(
                columns={
                    "week_number": "ca_last_purchase_week",
                    "d_dat": "ca_last_purchase_date",
                }
            )
        )

        features = (["customers_id", "articles_id"], recent_customer_df)
        recent_customer_cand = (
            recent_customer_df.query(
                f"ca_last_purchase_week >= {last_week_number - recent_customer_weeks + 1}"
            )
            .reset_index()[["customers_id", "articles_id"]]
            .drop_duplicates()
        )

        return recent_customer_cand, features

    def add_features_to_candidates(candidates_df, features, customers_df, articles_df):
        for features_key in features:
            col_names, feature_df = features[features_key]

            to_delete = []
            for col_name in col_names:
                if col_name not in candidates_df:
                    if col_name in customers_df:
                        col_name_dict = customers_df.set_index("customers_id")[col_name]
                        candidates_df[col_name] = candidates_df["customers_id"].map(
                            col_name_dict
                        )
                        to_delete.append(col_name)
                    elif col_name in articles_df:
                        col_name_dict = articles_df.set_index("articles_id")[col_name]
                        candidates_df[col_name] = candidates_df["articles_id"].map(
                            col_name_dict
                        )
                        to_delete.append(col_name)

            candidates_df = candidates_df.merge(feature_df, how="left", on=col_names)

            for col_name in to_delete:
                del candidates_df[col_name]

        return candidates_df


    def filter_candidates(candidates, transactions_df, **kwargs):
        recent_art_weeks = kwargs["filter_recent_art_weeks"]
        recent_articles = transactions_df.query(
            f"week_number >= {kwargs['label_week'] - recent_art_weeks}"
        )["articles_id"]

        num_articles = kwargs.get("filter_num_articles", None)
        if num_articles is None:
            recent_articles = recent_articles.drop_duplicates()
        else:
            recent_item_counts = recent_articles.value_counts()
            most_popular_items = recent_item_counts[:num_articles].index
            most_popular_items = most_popular_items.to_pandas().to_list()
            recent_articles = most_popular_items

        candidates = candidates[candidates["articles_id"].isin(recent_articles)].copy()

        return candidates
    def get_group_lengths(df):
        return list(df.groupby("customers_id")["articles_id"].count())


    def cudf_groupby_head(df, groupby, head_count):
        

        head_df = df.groupby(groupby).head(head_count)

        head_df = pd.DataFrame(head_df)

        return head_df


    def create_predictions(ids_df, preds):
        ids_df["pred"] = preds
        ids_df = ids_df.sort_values(["customers_id", "pred"], ascending=False)
        ids_df = cudf_groupby_head(ids_df, "customers_id", 4)
        predictions = ids_df.groupby("customers_id")["articles_id"].agg(list)

        return predictions


    def pred_in_batches(model, features_df, batch_size=500):
        preds = []
        num_batches = int(len(features_df) / 500) + 1
        for batch in range(num_batches):
            batch_df = features_df.iloc[batch * batch_size : (batch + 1) * batch_size, :]
            preds.append(model.predict(batch_df))

        return np.concatenate(preds)




    def prepare_modeling_dfs(t, c, a, cand_features_func, **params):
        cf_df, label_df = cand_features_func(t, c, a, **params)
        label_df = label_df[["customers_id", "articles_id"]].drop_duplicates()
        label_df["match"] = 1
        cf_df = cf_df.merge(label_df, how="left", on=["customers_id", "articles_id"])
        cf_df["match"] = cf_df["match"].fillna(0).astype("int8")
        cf_df = cf_df.sample(frac=1, random_state=42).reset_index(drop=True)
        del label_df["match"]
        customers_with_positives = cf_df.query("match==1")["customers_id"].unique()
        cf_df = cf_df[cf_df["customers_id"].isin(customers_with_positives)]
        cf_df = cf_df.sort_values("customers_id").reset_index(drop=True)
        group_lengths = get_group_lengths(cf_df)
        ids_df = cf_df[["customers_id", "articles_id"]].copy()
        del cf_df["customers_id"], cf_df["articles_id"]
        y = cf_df[["match"]].copy()
        del cf_df["match"]
        X = cf_df
        del cf_df

        ground_truth_df = label_df
        del label_df

        
        

        y = y["match"]

        return ids_df, X, group_lengths, y, ground_truth_df


    def prepare_prediction_dfs(t, c, a, cand_features_func, customer_batch=None, **params):
        cf_df= cand_features_func(t, c, a, customer_batch=customer_batch, **params)

        ids_df = cf_df[["customers_id", "articles_id"]].copy()
        del cf_df["customers_id"], cf_df["articles_id"]
        X = cf_df
        del cf_df

        
        

        return ids_df, X


    def prepare_concat_train_modeling_dfs(t, c, a, cand_features_func, **params):
        working_params = copy.deepcopy(params)

        if params["num_concats"] > 1:
            empty_list = [None] * params["num_concats"]
            empty_lists = [empty_list.copy() for i in range(5)]

            (
                train_ids_df,
                train_X,
                train_group_lengths,
                train_y,
                train_truth_df,
            ) = empty_lists

            for i in range(params["num_concats"]):
                week_num = params["label_week"] - (i + 1)
                working_params["label_week"] = week_num
                (
                    train_ids_df[i],
                    train_X[i],
                    train_group_lengths[i],
                    train_y[i],
                    train_truth_df[i],
                ) = prepare_modeling_dfs(t, c, a, cand_features_func, **working_params)
            train_ids_df = pd.concat(train_ids_df)
            train_group_lengths = sum(train_group_lengths, [])
            train_truth_df = pd.concat(train_truth_df)
            train_X = pd.concat(train_X)
            train_y = pd.concat(train_y)
        else:
            week_num = params["label_week"] - 1
            working_params["label_week"] = week_num
            (
                train_ids_df,
                train_X,
                train_group_lengths,
                train_y,
                train_truth_df,
            ) = prepare_modeling_dfs(t, c, a, cand_features_func, **working_params)

        return train_ids_df, train_X, train_group_lengths, train_y, train_truth_df


    def prepare_train_eval_modeling_dfs(t, c, a, cand_features_func, **params):
        (
            train_ids_df,
            train_X,
            train_group_lengths,
            train_y,
            train_truth_df,
        ) = prepare_concat_train_modeling_dfs(t, c, a, cand_features_func, **params)

        (
            eval_ids_df,
            eval_X,
            eval_group_lengths,
            eval_y,
            eval_truth_df,
        ) = prepare_modeling_dfs(t, c, a, cand_features_func, **params)

        return (
            train_ids_df,
            train_X,
            train_group_lengths,
            train_y,
            train_truth_df,
            eval_ids_df,
            eval_X,
            eval_group_lengths,
            eval_y,
            eval_truth_df,
        )


    def full_cv_run(t, c, a, cand_features_func, score_func, **kwargs):
        train_eval_dfs = prepare_train_eval_modeling_dfs(
            t, c, a, cand_features_func, **kwargs
        )
        (
            train_ids_df,
            train_X,
            train_group_lengths,
            train_y,
            train_truth_df,
            eval_ids_df,
            eval_X,
            eval_group_lengths,
            eval_y,
            eval_truth_df,
        ) = train_eval_dfs

        model = LGBMRanker(**(kwargs["lgbm_params"]), random_state=42,verbose=-1)

        eval_set = [(train_X, train_y), (eval_X, eval_y)]
        eval_group = [train_group_lengths, eval_group_lengths]
        eval_names = ["train", "validation"]
        es_callback = lightgbm.early_stopping(kwargs["early_stopping"],verbose=0)

        model.fit(
            train_X,
            train_y,
            eval_set=eval_set,
            eval_names=eval_names,
            eval_group=eval_group,
            eval_metric="MAP",
            eval_at=kwargs["eval_at"],
            callbacks=[es_callback],
            group=train_group_lengths,
        )

        if kwargs.get("save_model", False):
            with open(f"Aras_RS/model_{kwargs['label_week']}", "wb") as f:
                pkl.dump(model, f)

        train_pred = model.predict(train_X)

        del train_X, train_y, train_group_lengths, train_truth_df, train_pred

        eval_pred = pred_in_batches(model, eval_X)

        eval_score = score_func(eval_ids_df, eval_pred, eval_truth_df)
        return eval_score


    def run_all_cvs(
        t, c, a, cand_features_func, score_func, cv_weeks, **params
    ):
        cv_scores = []
        total_duration = datetime.now() - datetime.now()

        for cv_week in cv_weeks:
            starting_time = datetime.now()

            cv_params = copy.deepcopy(params)
            cv_params.update({"label_week": cv_week})
            cv_score = full_cv_run(t, c, a, cand_features_func, score_func, **cv_params)

            cv_scores.append(cv_score)
            duration = datetime.now() - starting_time
            total_duration += duration

        average_scores = round(np.mean(cv_scores), 5)                
        return average_scores

    def cudf_groupby_head(df, groupby, head_count):
        

        head_df = df.groupby(groupby).head(head_count)

        head_df = pd.DataFrame(head_df)

        return head_df


    def create_pairs(transactions_df, week_number, pairs_per_item, verbose=False):

        working_t_df = transactions_df[["customers_id", "articles_id", "week_number"]].copy()

        working_t_df = working_t_df.query(f"week_number <= {week_number}").copy()
        pairs_t_df = working_t_df.query(f"week_number == {week_number}").copy()
        pairs_t_df.columns = ["customers_id", "pair_articles_id", "week_number"]

        del working_t_df["week_number"], pairs_t_df["week_number"]
        working_t_df = working_t_df.drop_duplicates()
        pairs_t_df = pairs_t_df.drop_duplicates()

        unique_articles = working_t_df["articles_id"].unique()
        batch_size = 5000
        batch_pairs_dfs = []

        for i in range(0, len(unique_articles), batch_size):

            batch_articles = unique_articles[i : i + batch_size]
            batch_t = working_t_df[working_t_df["articles_id"].isin(batch_articles)]

            all_cust_counts = batch_t.groupby("articles_id")["customers_id"].nunique()
            all_cust_counts = all_cust_counts.reset_index()
            all_cust_counts.columns = ["articles_id", "all_customer_counts"]
            all_cust_counts["all_customer_counts"] -= 1  

            batch_pairs_df = batch_t.merge(pairs_t_df, on="customers_id")

            same_article_row_idxs = batch_pairs_df.query(
                "articles_id==pair_articles_id"
            ).index
            batch_pairs_df = batch_pairs_df.drop(same_article_row_idxs)

            c1s = (
                batch_pairs_df.groupby("articles_id")[["customers_id"]]
                .nunique()
                .query("customers_id==1")
                .index
            )
            single_customer_row_idxs = batch_pairs_df[
                batch_pairs_df["articles_id"].isin(c1s)
            ].index
            batch_pairs_df = batch_pairs_df.drop(single_customer_row_idxs)

            batch_pairs_df = batch_pairs_df.groupby(["articles_id", "pair_articles_id"])[
                ["customers_id"]
            ].count()
            batch_pairs_df.columns = ["customer_count"]
            batch_pairs_df = batch_pairs_df.reset_index()
            batch_pairs_df = batch_pairs_df.sort_values(
                ["articles_id", "customer_count"], ascending=False
            )

            batch_pairs_df = cudf_groupby_head(batch_pairs_df, "articles_id", pairs_per_item)

            batch_pairs_df = batch_pairs_df.merge(all_cust_counts, on="articles_id")
            batch_pairs_df["percent_customers"] = (
                batch_pairs_df["customer_count"] / batch_pairs_df["all_customer_counts"]
            )
            del batch_pairs_df["all_customer_counts"]

            batch_pairs_dfs.append(batch_pairs_df)

        all_article_pairs_df = pd.concat(batch_pairs_dfs)

        return all_article_pairs_df

    def ground_truth(transactions_df):
        customer_trans = transactions_df[["customers_id", "articles_id"]].drop_duplicates()
        customer_trans = customer_trans.groupby("customers_id")[["articles_id"]].agg(list)
        customer_trans.columns = ["prediction"]

        gt = customer_trans.reset_index()

        return gt

    def create_candidates_with_features_df(t, c, a, customer_batch=None, **kwargs):
        features_df, label_df = feature_label_split(
            t, kwargs["label_week"], kwargs["feature_periods"]
        )
        
        features_df["d_dat"] = how_many_ago(features_df["d_dat"])
        features_df["week_number"] = how_many_ago(features_df["week_number"])

        article_pairs_df = week_number_pairs[kwargs["label_week"]-1]

        if len(label_df) > 0:
            ctm = label_df["customers_id"].unique()
        elif customer_batch is not None:
            ctm = customer_batch
        else:
            ctm = None
        

        features_db = shelve.open("Aras_RS/features_db") 
        
        recent_customer_cand, features_db["customer_article"] = (        #Active
            create_recent_customer_candidates(
                features_df,
                kwargs["ca_num_weeks"],
                customers=ctm,
            )
        )
         
        
        cand = [recent_customer_cand] 
        
        cand = pd.concat(cand).drop_duplicates()
        cand = cand.sort_values(["customers_id", "articles_id"]).reset_index(drop=True)
     
        del recent_customer_cand 
        
        
        cand = filter_candidates(cand, t, **kwargs)
        
        del features_df

        if ctm is not None:
            cand = cand[cand["customers_id"].isin(ctm)]
        

        if kwargs["cv"]:
            ground_truth_candidates = label_df[["customers_id", "articles_id"]].drop_duplicates()
            report_candidates(cand, ground_truth_candidates)
            del ground_truth_candidates        

        cand_with_f_df = add_features_to_candidates(
            cand, features_db, c, a
        )
        

        if kwargs["selected_features"] is not None:
            cand_with_f_df = cand_with_f_df[
                ["customers_id", "articles_id"] + kwargs["selected_features"]
            ]
            
        features_db.close()
        
        
        assert len(cand) == len(cand_with_f_df), "seem to have duplicates in the feature dfs"
        del cand
        
        return cand_with_f_df, label_df

    def calculate_model_score(ids_df, preds, truth_df):
        predictions = create_predictions(ids_df, preds)
        true_labels = ground_truth(truth_df).set_index("customers_id")["prediction"]
        score = round(comp_average_precision(true_labels, predictions),5)
        
        return score
    cand_features_func = create_candidates_with_features_df
    scoring_func = calculate_model_score
############################################################################################################################################################# Main Code
    t = transactions_df
    a = pd.DataFrame()
    a =  pd.Series(t['articles_id'].unique(), name="articles_id")
    c = pd.DataFrame()
    c =  pd.Series(t['customers_id'].unique(), name="customers_id")
    t["d_dat"] = day_numbers(t["d_dat"])
    t["week_number"] = day_week_numbers(t["d_dat"]).abs()
    if target_week == 'last':
        target_week = t['week_number'].max()
    
    pairs_per_item = 5
    c = c.to_csv('Aras_customers.csv', index = False)
    c = pd.read_csv('Aras_customers.csv')
    a = a.to_csv('Aras_articles.csv', index = False)
    a = pd.read_csv('Aras_articles.csv')
    t_out = t.copy()
    c_out = c.copy()
    index_to_id_dict_path = reduce_customer_id_memory(c, [t])
    week_number_pairs = {}
    num=[]
    for i in range (t['week_number'].min(),t['week_number'].max()+1):
        num.append(i)

    for week_number in num:
        week_number_pairs[week_number] = create_pairs(
            t, week_number, pairs_per_item, verbose=False
        )
    cv_params = {
        "cv": True,
        "feature_periods": target_week,
        "label_week": target_week - 1,
        "index_to_id_dict_path": index_to_id_dict_path,
        "pairs_file_version": "_v3_5_ex",
        "num_recent_candidates": 36,    
        "num_recent_articles": 12,     
        "ca_num_weeks": 3,    
        "clw_num_weeks": 25,    
        "hier_col": "group_no",
        "clw_num_pair_weeks": 4,   
        "pa_num_weeks": 1,
        "filter_recent_art_weeks": 1,   
        "filter_num_articles": None,
        "article_columns": ["index_code"],
        "selected_features": None,
        "lgbm_params": {"n_estimators": 150, "num_leaves": 8},
        "log_evaluation": 5,    
        "early_stopping": 10,    
        "eval_at": 10,          #10     
        "save_model": True,
        "num_concats": 1,  
        "verbose": -1, 
    }
    
    prediction_models = []
    #for i in range(t['week_number'].min()+60, t['week_number'].max()):
    for i in range(t['week_number'].min()+60, target_week):
        prediction_models.append('Aras_RS/model_'+str(i))
    
    sub_params = {
        "cv": False,
        "feature_periods": target_week,
        "label_week": target_week,
        "index_to_id_dict_path": index_to_id_dict_path,
        "pairs_file_version": "_v3_5_ex",
        "num_recent_candidates": 60,   
        "num_recent_articles": 12,      
        "hier_col": "group_no",
        "ca_num_weeks": 3,              
        "clw_num_weeks": 12,          
        "clw_num_pair_weeks": 2,   
        "pa_num_weeks": 1,       
        "filter_recent_art_weeks": 2, 
        "filter_num_articles": None,
        "article_columns": ["index_code"],
        "selected_features": None,
        "prediction_models": prediction_models,
        "num_concats": 5,
        "verbose": -1,
    }
    cv_weeks = []
    for i in range (t['week_number'].min()+60, t['week_number'].max()):
        cv_weeks.append(i)
    results = run_all_cvs(
        t, c, a, cand_features_func, scoring_func, 
        cv_weeks=cv_weeks, **cv_params
    )
    #######################################################################################################################
    def create_Sub_with_features_df(t_out, c_out, a, customer_batch=None, **kwargs):
        features_df = t_out.copy()

        article_pairs_df = week_number_pairs[kwargs["label_week"]-1]
        
        features_db = shelve.open("Aras_RS/features_db") 
        ctm = c_out['customers_id']
        recent_customer_cand, features_db["customer_article"] = (                
            create_recent_customer_candidates(
                features_df,
                kwargs["ca_num_weeks"],
                customers=ctm,
            )
        )
             
        cand = [recent_customer_cand] 
        
        cand = pd.concat(cand).drop_duplicates()
        cand = cand.sort_values(["customers_id", "articles_id"]).reset_index(drop=True)
        
        del recent_customer_cand 
        
        del features_df

        if ctm is not None:
            cand = cand[cand["customers_id"].isin(ctm)]
        
        cand_with_f_df = add_features_to_candidates(
            cand, features_db, c_out, a
        )
        

            
        features_db.close()
        del cand
        
        return cand_with_f_df

    week_number_pairs = {}
    num=[]
    for i in range (t_out['week_number'].min(),t_out['week_number'].max()+1):
        num.append(i)

    for week_number in num:
        week_number_pairs[week_number] = create_pairs(
            t_out, week_number, pairs_per_item, verbose=False
        )
    customer_batches = []

    num_customers = len(c_out)
    half_point = num_customers // 2

    customer_batches.append(c_out["customers_id"].to_list())

    batch_preds = []
    for idx, customer_batch in enumerate(customer_batches):

        sub_ids_df, sub_X = prepare_prediction_dfs(
            t_out, c_out, a, create_Sub_with_features_df, customer_batch=customer_batch, **sub_params
        )
        prediction_models = sub_params.get("prediction_models")
        model_nums = len(prediction_models)
        
        first_model_path = prediction_models[0]
        with open(first_model_path, "rb") as f:
            first_model = pkl.load(f)

        sub_pred = pred_in_batches(first_model, sub_X) / model_nums
        del first_model

        for model_path in prediction_models[1:]:
            with open(model_path, "rb") as f:
                model = pkl.load(f)
                sub_pred2 = pred_in_batches(model, sub_X)
                del model
                sub_pred += sub_pred2 / model_nums

        batch_preds.append(create_predictions(sub_ids_df, sub_pred))
        del sub_ids_df, sub_X, sub_pred
    predictions = pd.concat(batch_preds)
    predictions=predictions.reset_index()
    shutil.rmtree(folder_name)
    return  predictions


