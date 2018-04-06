import psycopg2
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder

from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.svm import NuSVC


class Utils(object):

    @staticmethod
    def get_target(score):
        dom_score = int(score.split("-")[0])
        ext_score = int(score.split("-")[1])
        if dom_score > ext_score:
            return 1
        elif dom_score < ext_score:
            return -1
        else:
            return 0


class DataSet(object):

    @staticmethod
    def get_match_and_result():
        conn = psycopg2.connect(host="localhost", dbname="foot_dev", user="foot", password="torche")
        cur = conn.cursor()
        cur.execute("SELECT id_match, code_equipe_dom, code_equipe_ext, saison, journee, score, pays from match")
        liste_match = cur.fetchall()
        cur.close()
        match_df = pd.DataFrame(liste_match,
                                columns=["id_match", "eq_dom", "eq_ext", "saison", "journee", "score", "pays"])
        ut = Utils()
        match_df["target"] = match_df.apply(axis=1, func=lambda x: ut.get_target(x["score"]))
        del match_df["score"]

        return match_df

    @staticmethod
    def add_classement_before_match(df):
        conn = psycopg2.connect(host="localhost", dbname="foot_dev", user="foot", password="torche")
        cur = conn.cursor()
        cur.execute("SELECT id, id_match, code_equipe, classement_avant_match from stat_equipe_par_match")
        classement = cur.fetchall()
        cur.close()
        classement_df = pd.DataFrame(classement,
                                     columns=["id_stat", "id_match", "code_equipe", "classement_avant_match"])
        full_df_tmp = pd.merge(classement_df, df, how='left', on=['id_match'])
        full_df_tmp["eq_dom_class_avt_match"] = full_df_tmp.apply(axis=1,
                                                                  func=lambda x: x["classement_avant_match"] if x[
                                                                                                                    "eq_dom"] ==
                                                                                                                x[
                                                                                                                    "code_equipe"] else 0)
        full_df_tmp["eq_ext_class_avt_match"] = full_df_tmp.apply(axis=1,
                                                                  func=lambda x: x["classement_avant_match"] if x[
                                                                                                                    "eq_ext"] ==
                                                                                                                x[
                                                                                                                    "code_equipe"] else 0)
        classement_grouped = full_df_tmp[['id_match', 'eq_dom_class_avt_match', 'eq_ext_class_avt_match']].groupby(
            "id_match").sum().reset_index()
        full_df = pd.merge(df, classement_grouped, on=["id_match"])
        return full_df

    @staticmethod
    def encode_column(df, column_name):
        df_encoded = df.copy()
        le = LabelEncoder()
        le.fit(df_encoded[column_name])
        df_encoded[column_name + "_encoded"] = le.transform(df_encoded[column_name])
        del df_encoded[column_name]

        return df_encoded

    @staticmethod
    def encode_teams_into_dummies(df):
        dummies_eq_dom = pd.get_dummies(df["eq_dom"]).astype(int)
        dummies_eq_ext = pd.get_dummies(df["eq_ext"]).astype(int)
        dummies_eq_ext.replace(1, -1, inplace=True)
        dummies_teams = dummies_eq_dom + dummies_eq_ext

        match_dummies = pd.concat([df, dummies_teams], axis=1)
        del match_dummies["eq_dom"]
        del match_dummies["eq_ext"]

        return match_dummies

    @staticmethod
    def encode_column_into_dummies(df, column_name):
        df_dummmies = df.copyy()
        col_dummmies = pd.get_dummies(df_dummmies[column_name]).astype(int)
        df_dummmies = pd.concat([df_dummmies, col_dummmies], axis=1)
        del df_dummmies[column_name]

        return df_dummmies

    @staticmethod
    def remove_columns(df, list_columns):
        df_del = df.copy()
        for col in list_columns:
            del df_del[col]
        return df_del

class Controls(object):

    @staticmethod
    def check_missing_days(pays, annees, match_df):
        """
        :param pays: dictionnary with code pays and number of day in the saison, e.g. {"fr": 38, "de": 34}
        :param annees: list of annees to check
        :param match_df: dataframes of match that we want to check
        :return: 
        """
        for p, nb_game in pays.items():
            print("####################")
            print(p)
            for a in annees:
                list_team = match_df.loc[(match_df["saison"] == a) & (match_df["pays"] == p), "eq_dom"].unique()
                for t in list_team:
                    mask = ((match_df["saison"] == a) & (match_df["pays"] == p) & (
                    (match_df["eq_dom"] == t) | (match_df["eq_ext"] == t)))
                    if len(match_df[mask]) < nb_game:
                        print(len(match_df[mask]))
                        print("KO for equipe {} of annee {} in league {}".format(t, a, p))



class FeatureGeneration(object):

    ############## Handle missing values with mean by team and saison ##############
    @staticmethod
    def get_feature_stats(feature):
        # get statistics
        conn = psycopg2.connect(host="localhost", dbname="foot_dev", user="foot", password="torche")
        cur = conn.cursor()
        cur.execute("SELECT match.id_match, match.saison, match.journee, code_equipe, {}\
                from stat_equipe_par_match as stat, match\
                where match.id_match = stat.id_match\
                order by saison, journee asc".format(feature))
        feature_stats = cur.fetchall()
        cur.close()

        # Compute sum of stats per team and year
        feature_stats_df = pd.DataFrame(feature_stats,
                                        columns=["id_match", "saison", "journee", "code_equipe", feature])

        return feature_stats_df

    @staticmethod
    def get_table_mean_feature(df, feature):
        df_no_nan = df.copy()
        df_no_nan = df_no_nan[~df_no_nan.isnull().any(axis=1)]
        df_no_nan[feature] = df_no_nan[feature].astype(float)
        mean_feature = df_no_nan[["saison", "code_equipe", feature]].groupby(
            ["saison", "code_equipe"]).mean().reset_index()

        return mean_feature

    @staticmethod
    def get_mean_feature(saison, eq, mean_table, feature):
        mask = (mean_table["saison"] == saison) & (mean_table["code_equipe"] == eq)
        return mean_table.loc[mask, feature].values

    @staticmethod
    def fill_nan_with_mean_feature(feature):
        fg = FeatureGeneration()
        df_stats_feature = fg.get_feature_stats(feature)
        df_mean_feature = fg.get_table_mean_feature(df_stats_feature, feature)
        mask = (df_stats_feature.isnull().any(axis=1))
        df_stats_feature.loc[mask, feature] = df_stats_feature[mask].apply(axis=1,
                                                                           func=lambda x: fg.get_mean_feature(x["saison"], x["code_equipe"], df_mean_feature, feature))
        return df_stats_feature


    ############### Function to generate cumulate mean on any column ##############

    @staticmethod
    def add_mean_feature_after_match(df, feature_db):
        # get statistics
        conn = psycopg2.connect(host="localhost", dbname="foot_dev", user="foot", password="torche")
        cur = conn.cursor()
        cur.execute("SELECT match.id_match, match.saison, match.journee, code_equipe, {}\
                from stat_equipe_par_match as stat, match\
                where match.id_match = stat.id_match\
                order by saison, journee asc".format(feature_db))
        stats = cur.fetchall()
        cur.close()

        # Compute sum of stats per team and year
        stats_df = pd.DataFrame(stats, columns=["id_match", "saison", "journee", "code_equipe", feature_db])

        # Manage NaN with mean of the feature per saison and per team
        if len(stats_df[stats_df.isnull().any(axis=1)]) > 0:
            fg = FeatureGeneration()
            stats_df = fg.fill_nan_with_mean_feature(feature_db)

        cumsum = pd.DataFrame()
        cumsum_tmp = pd.DataFrame()
        for annee in range(2013, 2018):
            stats_one_year = stats_df[stats_df["saison"] == annee]
            list_equipes = stats_one_year["code_equipe"].unique()
            for eq in list_equipes:
                stats_one_year_one_team = stats_one_year[stats_one_year["code_equipe"] == eq].sort_values(by="journee")
                cumsum_tmp = stats_one_year_one_team[feature_db].astype(int).cumsum()
                cumsum = pd.concat([cumsum, cumsum_tmp])
        cumsum.columns = [feature_db + "_cumsum"]

        # Merge with the global infos
        stats_cumsum = pd.merge(stats_df, cumsum, left_index=True, right_index=True)

        # Compute the cum mean per team and year
        stats_cumsum[feature_db + "_mean"] = stats_cumsum.apply(axis=1,
                                                                func=lambda x: x[feature_db + "_cumsum"] / x["journee"])

        # Transform the dataframe to have one colum for the docmicile and one for the exterieur
        full_df_tmp = pd.merge(stats_cumsum[["id_match", "code_equipe", feature_db + "_mean", feature_db + "_cumsum"]], df, how='left', on=['id_match'])

        full_df_tmp["dom_" + feature_db + "_mean"] = full_df_tmp.apply(axis=1, func=lambda x: x[feature_db + "_mean"] if x["eq_dom"] == x["code_equipe"] else 0)
        full_df_tmp["ext_" + feature_db + "_mean"] = full_df_tmp.apply(axis=1, func=lambda x: x[feature_db + "_mean"] if x["eq_ext"] == x["code_equipe"] else 0)

        stats_grouped = full_df_tmp[['id_match', "dom_" + feature_db + "_mean", "ext_" + feature_db + "_mean"]].groupby("id_match").sum().reset_index()
        full_df = pd.merge(df, stats_grouped, on=["id_match"])

        return full_df

    @staticmethod
    def get_mean_feature_before_match(df, eq, journee, saison, feature_db):
        if journee == 1:
            return np.NaN
        past_journee = journee - 1

        mask = ((df["saison"] == saison) & (df["journee"] == past_journee) & ((df["eq_dom"] == eq) | (df["eq_ext"] == eq)))

        last_feature = df.loc[mask]

        if len(last_feature) > 0:
            if last_feature["eq_dom"].values[0] == eq:
                return last_feature["dom_" + feature_db + "_mean"].values[0]
            elif last_feature["eq_ext"].values[0] == eq:
                return last_feature["ext_" + feature_db + "_mean"].values[0]

        return np.NaN

    @staticmethod
    def add_mean_feature_before_match(df, feature_db):
        fg = FeatureGeneration()
        full_df = fg.add_mean_feature_after_match(df, feature_db)
        full_df["dom_" + feature_db + "_mean_new"] = full_df.apply(axis=1,
                                                                   func=lambda x: fg.get_mean_feature_before_match(full_df, x["eq_dom"], x["journee"], x["saison"], feature_db))
        full_df["ext_" + feature_db + "_mean_new"] = full_df.apply(axis=1,
                                                                   func=lambda x: fg.get_mean_feature_before_match(full_df, x["eq_ext"], x["journee"], x["saison"], feature_db))

        # Rename columns
        del full_df["dom_" + feature_db + "_mean"]
        del full_df["ext_" + feature_db + "_mean"]

        full_df.rename(columns={"dom_" + feature_db + "_mean_new": "dom_" + feature_db + "_mean"}, inplace=True)
        full_df.rename(columns={"ext_" + feature_db + "_mean_new": "ext_" + feature_db + "_mean"}, inplace=True)

        return full_df


    ############### Function to generate cumulate mean on last N days on any column ##############

    @staticmethod
    def add_stats_match(df, feature_db):
        # get statistics
        conn = psycopg2.connect(host="localhost", dbname="foot_dev", user="foot", password="torche")
        cur = conn.cursor()
        cur.execute("SELECT match.id_match, match.saison, match.journee, code_equipe, {}\
                from stat_equipe_par_match as stat, match\
                where match.id_match = stat.id_match\
                order by saison, journee asc".format(feature_db))
        stats = cur.fetchall()
        cur.close()

        # Compute sum of stats per team and year
        stats_df = pd.DataFrame(stats, columns=["id_match", "saison", "journee", "code_equipe", feature_db])

        # Manage NaN with mean of the feature per saison and per team
        if len(stats_df[stats_df.isnull().any(axis=1)]) > 0:
            fg = FeatureGeneration()
            stats_df = fg.fill_nan_with_mean_feature(feature_db)

        # Transform the dataframe to have one colum for the docmicile and one for the exterieur
        full_df_tmp = pd.merge(stats_df[["id_match", "code_equipe", feature_db]], df, how='left', on=['id_match'])

        full_df_tmp["dom_" + feature_db] = full_df_tmp.apply(axis=1, func=lambda x: x[feature_db] if x["eq_dom"] == x["code_equipe"] else 0)
        full_df_tmp["ext_" + feature_db] = full_df_tmp.apply(axis=1, func=lambda x: x[feature_db] if x["eq_ext"] == x["code_equipe"] else 0)

        stats_grouped = full_df_tmp[['id_match', "dom_" + feature_db, "ext_" + feature_db]].groupby("id_match").sum().reset_index()
        full_df = pd.merge(df, stats_grouped, on=["id_match"])

        return full_df

    @staticmethod
    def compute_mean_feature_nlast_results(df, saison, journee, equipe, n_last_days, feature_db):
        if journee <= n_last_days:
            return np.NaN

        last_days = np.arange(journee - n_last_days, journee)
        mask_dom = (df["journee"].isin(last_days)) & (df["saison"] == saison) & (df["eq_dom"] == equipe)
        mask_ext = (df["journee"].isin(last_days)) & (df["saison"] == saison) & (df["eq_ext"] == equipe)

        return (df.loc[mask_dom, "dom_" + feature_db].astype(float).sum() + df.loc[mask_ext, "ext_" + feature_db].astype(float).sum()) / n_last_days

    @staticmethod
    def add_mean_feature_nlast_results(df, n_last_days, feature_db):
        fg = FeatureGeneration()
        full_df = fg.add_stats_match(df, feature_db)
        full_df["dom_last_" + str(n_last_days) + "_" + feature_db] = full_df.apply(axis=1, func=lambda
            x: fg.compute_mean_feature_nlast_results(full_df, x["saison"], x["journee"], x["eq_dom"], n_last_days, feature_db))
        full_df["ext_last_" + str(n_last_days) + "_" + feature_db] = full_df.apply(axis=1, func=lambda
            x: fg.compute_mean_feature_nlast_results(full_df, x["saison"], x["journee"], x["eq_ext"], n_last_days, feature_db))
        return full_df


class TrainModels():

    @staticmethod
    def test_basic_models(X, y, cv):
        lr = LogisticRegression()
        print("Result for logistic regression: ")
        print(cross_val_score(lr, X, y, cv=cv))
        print("##########################################")

        svm = NuSVC()
        print("Result for SVM: ")
        print(cross_val_score(svm, X, y, cv=cv))
        print("##########################################")

        knn = KNeighborsClassifier(n_neighbors=50)
        print("Result for KNN:")
        print(cross_val_score(knn, X, y, cv=cv))
        print("##########################################")

        gbc = GradientBoostingClassifier()
        print("Result for Gradient Boosting:")
        print(cross_val_score(gbc, X, y, cv=cv))
        print("##########################################")

        rf = RandomForestClassifier(n_estimators=100, random_state=42)
        print("Result for Random Forest:")
        print(cross_val_score(rf, X, y, cv=cv))
        print("##########################################")

        mlp = MLPClassifier((100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100), random_state=42)
        print("Result for Neural Network:")
        print(cross_val_score(mlp, X, y, cv=cv))
        print("##########################################")