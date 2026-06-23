"""
Feature engineering module initialization.
Imports are lazy to avoid loading heavy dependencies (like pandas-ta) when not needed.
"""


def __getattr__(name):
    if name == "TechnicalFeatureEngineer":
        from src.features.technical import TechnicalFeatureEngineer
        return TechnicalFeatureEngineer
    if name == "FundamentalFeatureEngineer":
        from src.features.fundamental import FundamentalFeatureEngineer
        return FundamentalFeatureEngineer
    if name == "SentimentFeatureEngineer":
        from src.features.sentiment import SentimentFeatureEngineer
        return SentimentFeatureEngineer
    if name == "FeaturePipeline":
        from src.features.pipeline import FeaturePipeline
        return FeaturePipeline
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "TechnicalFeatureEngineer",
    "FundamentalFeatureEngineer",
    "SentimentFeatureEngineer",
    "FeaturePipeline",
]