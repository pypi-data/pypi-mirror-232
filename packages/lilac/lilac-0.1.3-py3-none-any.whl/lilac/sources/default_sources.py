"""Registers all available default sources."""
from .csv_source import CSVSource
from .gmail_source import GmailSource
from .huggingface_source import HuggingFaceSource
from .json_source import JSONSource
from .langsmith import LangSmithSource
from .pandas_source import PandasSource
from .parquet_source import ParquetSource
from .source_registry import register_source
from .sqlite_source import SQLiteSource


def register_default_sources() -> None:
  """Register all the default sources."""
  register_source(CSVSource)
  register_source(HuggingFaceSource)
  register_source(JSONSource)
  register_source(PandasSource)
  register_source(GmailSource)
  register_source(ParquetSource)
  register_source(LangSmithSource)
  register_source(SQLiteSource)
