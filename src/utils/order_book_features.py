from .feature_utils import *
from ..config import ConFig as cfg


def get_book_features(file_path):
    book_df = pd.read_parquet(file_path)

    # calculate wap
    book_df['wap1'] = calculate_wap(book_df, rank="1")
    book_df['wap2'] = calculate_wap(book_df, rank="2")

    # calculate log return
    book_df["log_return1"] = book_df.groupby(["time_id"])["wap1"].apply(calculate_logreturn)
    book_df["log_return2"] = book_df.groupby(["time_id"])["wap2"].apply(calculate_logreturn)

    # calculate balance
    book_df["wap_balance"] = abs(book_df["wap1"] - book_df["wap2"])
    book_df["volume_imbalance"] = abs(
        (book_df["ask_size1"] + book_df["ask_size2"]) - (book_df["bid_size1"] + book_df["bid_size2"]))
    book_df["total_volume"] = book_df["ask_size1"] + book_df["ask_size2"] + book_df["bid_size1"] + book_df[
        "bid_size2"]

    # calculate spread
    book_df["price_spread1"] = (book_df["ask_price1"] - book_df["bid_price1"]) / (
            (book_df["ask_price1"] + book_df["bid_price1"]) / 2)
    book_df["price_spread2"] = (book_df["ask_price2"] - book_df["bid_price2"]) / (
            (book_df["ask_price2"] + book_df["bid_price2"]) / 2)

    book_df["bid_spread"] = book_df["bid_price1"] - book_df["bid_price2"]
    book_df["ask_spread"] = book_df["ask_price1"] - book_df["ask_price2"]

    book_df_merged = get_stats_window(book_df, seconds_in_bucket=0, features_dict=cfg.feature_dict_book)

    book_df_450 = get_stats_window(book_df, seconds_in_bucket=450, features_dict=cfg.feature_dict_book, add_suffix=True)
    book_df_300 = get_stats_window(book_df, seconds_in_bucket=300, features_dict=cfg.feature_dict_book, add_suffix=True)
    book_df_150 = get_stats_window(book_df, seconds_in_bucket=150, features_dict=cfg.feature_dict_book, add_suffix=True)

    # merge stats
    book_df_merged = book_df_merged.merge(book_df_450, how="left", left_on="time_id_", right_on="time_id__450")
    book_df_merged = book_df_merged.merge(book_df_300, how="left", left_on="time_id_", right_on="time_id__300")
    book_df_merged = book_df_merged.merge(book_df_150, how="left", left_on="time_id_", right_on="time_id__150")


    book_df_merged.drop(columns=["time_id__450", "time_id__300", "time_id__150"], inplace=True)

    book_df_merged["row_id"] = book_df_merged["time_id_"].apply(lambda x: f"{file_path.split('=')[1]}-{x}")
    book_df_merged.drop(["time_id_"], axis=1, inplace=True)

    return book_df_merged