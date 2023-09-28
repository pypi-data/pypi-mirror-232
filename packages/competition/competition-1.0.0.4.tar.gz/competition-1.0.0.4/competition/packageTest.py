


def trade_func(
        date: dt.date,
        dict_df_result: dict[str, pd.DataFrame],
        dict_df_position: dict[str, pd.DataFrame],
        logger: logging.Logger,
) -> list[tuple[str, int]]:
    symbols_and_orders = [
        ("005930", 3)
    ]
    return symbols_and_orders
