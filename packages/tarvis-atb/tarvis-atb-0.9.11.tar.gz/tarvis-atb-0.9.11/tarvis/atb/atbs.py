import copy
import tarvis.common.logging


def run(
    indicator_source_classes,
    exchange_classes,
    additional_providers=None,
    additional_modules=None,
):
    import logging

    try:
        from dependency_injector import containers, providers
        from importlib import metadata
        import tarvis.common.config
        import tarvis.common.monitoring
        import tarvis.common.secrets
        import sys
        from . import AdvancedTradingBot, ExchangeAccount, ExchangeAccountDivision

        container = containers.DynamicContainer()
        container.config = tarvis.common.config.Configuration()
        container.watchdog = providers.ThreadSafeSingleton(
            tarvis.common.monitoring.Watchdog
        )

        if additional_providers:
            for name, provider in additional_providers:
                setattr(container, name, provider)

        if additional_modules is None:
            additional_modules = []

        container.wire(
            modules=[
                __name__,
                tarvis.common.config,
                tarvis.common.logging,
                tarvis.common.monitoring,
                tarvis.common.secrets,
                tarvis.atb.advancedtradingbot,
                *additional_modules,
            ]
        )

        # Adjust logging after configuration is available
        tarvis.common.logging.load_config()

        indicator_source_class_map = {}
        for indicator_source_class in indicator_source_classes:
            indicator_source_class_map[
                indicator_source_class.INDICATOR_SOURCE_NAME
            ] = indicator_source_class

        exchange_class_map = {}
        for exchange_class in exchange_classes:
            exchange_class_map[exchange_class.EXCHANGE_NAME] = exchange_class

        bots = container.config.bots()
        bot_threads = []
        bot_id = 0
        exchange_account_id = 0

        def _rename_attr(d: dict, old_name: str, new_name: str, required: bool = True):
            old_found = old_name in d
            new_found = new_name in d
            if (not old_found) and (not new_found):
                if required:
                    raise ValueError(f"{old_name} and {new_name} not specified.")
                else:
                    return
            if old_found and new_found:
                raise ValueError(f"{old_name} and {new_name} both specified.")
            if old_found:
                value = d.pop(old_name)
                d[new_name] = value

        if not bots:
            logging.error("No bots defined.")
        else:
            config_logging = True
            logging_config = container.config.get("logging")
            if logging_config is not None:
                config_logging = logging_config.get("config", True)

            for bot_config in bots:
                if config_logging:
                    logging_bot_config = copy.deepcopy(bot_config)
                    # Remove API key if it exists for security reasons
                    try:
                        logging_bot_config["indicator_source"]["headers"][
                            "X-API-Key"
                        ] = "REDACTED"
                    finally:
                        pass
                    versions = {
                        d.name: d.version
                        for d in metadata.distributions()
                        if d.name.startswith("tarvis-")
                    }
                    logging.info(
                        "Bot configuration loaded",
                        extra={"config": logging_bot_config, "versions": versions},
                    )

                # Backward compatibility
                # Remove this because it is now only used as a default indicator base
                # asset for older configuration versions
                indicator_base_asset = bot_config.pop("base_asset", None)
                # Renamed and now used as a default
                _rename_attr(bot_config, "quote_asset", "indicator_quote_asset")
                indicator_quote_asset = bot_config.pop("indicator_quote_asset", None)

                indicator_source_config = bot_config.pop("indicator_source")

                indicator_source_name = indicator_source_config.pop("name")
                indicator_source_class = indicator_source_class_map.get(
                    indicator_source_name
                )

                if indicator_source_class is None:
                    raise ValueError(
                        f"indicator_source {indicator_source_name} not recognized."
                    )
                else:
                    indicator_source = indicator_source_class(**indicator_source_config)

                    accounts_config = bot_config.pop("accounts")
                    accounts = []

                    for account_config in accounts_config:
                        exchange_config = account_config.pop("exchange")
                        exchange_name = exchange_config.pop("name")

                        exchange_class = exchange_class_map.get(exchange_name)
                        if exchange_class is None:
                            raise ValueError(
                                f"exchange {exchange_name} not recognized."
                            )

                        exchange = exchange_class(**exchange_config)

                        division_configs = account_config.pop("divisions", None)

                        # Backward compatibility
                        # Renamed
                        _rename_attr(
                            account_config, "quote_asset", "exchange_quote_asset"
                        )
                        _rename_attr(account_config, "reserve", "reserve_minimum")

                        # Convert a single base_asset into single division
                        if not division_configs:
                            exchange_base_asset = account_config.pop("base_asset")
                            division_configs = [
                                {
                                    "exchange_base_asset": exchange_base_asset,
                                    "allocation": 1,
                                    "indicator_base_asset": indicator_base_asset,
                                    "indicator_quote_asset": indicator_quote_asset,
                                }
                            ]

                        divisions = []
                        for division_config in division_configs:
                            if division_config.get("indicator_quote_asset") is None:
                                division_config[
                                    "indicator_quote_asset"
                                ] = indicator_quote_asset
                            account_division = ExchangeAccountDivision(
                                **division_config
                            )
                            divisions.append(account_division)

                        account = ExchangeAccount(
                            exchange_account_id,
                            exchange,
                            divisions,
                            **account_config,
                        )
                        accounts.append(account)

                        exchange_account_id += 1

                    if len(accounts) == 0:
                        raise ValueError("No accounts defined.")

                    bot_config["bot_id"] = bot_id
                    bot_config["indicator_source"] = indicator_source
                    bot_config["accounts"] = accounts
                    bot = AdvancedTradingBot(**bot_config)
                    bot_threads.append(bot.start())

                    bot_id += 1

        if len(bot_threads) == 0:
            logging.critical("No bots started.")
        else:
            for thread in bot_threads:
                thread.join()

    except Exception as unhandled_exception:
        logging.critical(f"Unhandled exception: {unhandled_exception}", exc_info=True)
        _EXIT_FAILURE = 1
        exit(_EXIT_FAILURE)
