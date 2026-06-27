def test_package_exports():
    import currex_schema

    assert currex_schema.Base is not None
    assert currex_schema.CurrencyRates is not None


def test_models_module_import():
    from currex_schema.models import Base, CurrencyRates

    assert Base is not None
    assert CurrencyRates is not None
