from typing import List, Text

import spacy


def get_available_spacy_models() -> List[Text]:
    installed_models = spacy.info().get("pipelines", "")
    if not installed_models:
        return []
    return list(installed_models.keys())


def get_spacy_models_for_language(lang: Text) -> List[Text]:
    installed_models = get_available_spacy_models()
    if not installed_models:
        return []

    return [
        model_name
        for model_name in installed_models
        if model_name.split("_")[0] == lang
    ]
