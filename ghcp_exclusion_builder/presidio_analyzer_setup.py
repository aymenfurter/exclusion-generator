from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
import spacy


# Global variable to cache the Presidio analyzer engine
_analyzer_engine = None

# List of PII entity types supported by Presidio
PII_ENTITY_TYPES = [
    "PERSON",
    "EMAIL_ADDRESS",
    "PHONE_NUMBER",
    "CREDIT_CARD",
    "DATE_TIME",
    "LOCATION",
    "US_SSN",
    "US_DRIVER_LICENSE",
    "IP_ADDRESS",
    "URL",
    "US_BANK_NUMBER",
    "US_PASSPORT",
    "IBAN_CODE",
    "NRP",  # National Registration Product
    "UK_NHS",
    "CRYPTO",
    "MEDICAL_LICENSE"
]


def get_presidio_analyzer():
    """
    Initialize and return a Presidio PII Analyzer with the default
    supported PII recognizers.
    """
    global _analyzer_engine
    if _analyzer_engine is None:
        try:
            spacy.load("en_core_web_lg")
        except OSError:
            print(
                "CRITICAL: SpaCy model 'en_core_web_lg' not found. Please ensure it's downloaded."
            )
            print("Run: python -m spacy download en_core_web_lg")
            raise RuntimeError(
                "SpaCy model 'en_core_web_lg' is required but not found. "
                "Please build/rebuild the devcontainer or run "
                "'python -m spacy download en_core_web_lg'."
            )

        nlp_engine_provider = NlpEngineProvider(
            nlp_configuration={
                "nlp_engine_name": "spacy",
                "models": [
                    {"lang_code": "en", "model_name": "en_core_web_lg"}
                ]
            }
        )
        _analyzer_engine = AnalyzerEngine(
            nlp_engine=nlp_engine_provider.create_engine(),
            supported_languages=["en"]
        )
        print("Presidio AnalyzerEngine initialized.")
    return _analyzer_engine
