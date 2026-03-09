from dataclasses import dataclass


@dataclass(frozen=True)
class LanguageSpec:
    code: str
    name: str
    nllb_code: str
    coqui_code: str


SUPPORTED_LANGUAGES: dict[str, LanguageSpec] = {
    "en": LanguageSpec("en", "English", "eng_Latn", "en"),
    "hi": LanguageSpec("hi", "Hindi", "hin_Deva", "hi"),
    "es": LanguageSpec("es", "Spanish", "spa_Latn", "es"),
    "fr": LanguageSpec("fr", "French", "fra_Latn", "fr"),
    "de": LanguageSpec("de", "German", "deu_Latn", "de"),
    "it": LanguageSpec("it", "Italian", "ita_Latn", "it"),
    "pt": LanguageSpec("pt", "Portuguese", "por_Latn", "pt"),
    "ru": LanguageSpec("ru", "Russian", "rus_Cyrl", "ru"),
    "ar": LanguageSpec("ar", "Arabic", "arb_Arab", "ar"),
    "zh": LanguageSpec("zh", "Chinese (Simplified)", "zho_Hans", "zh-cn"),
    "ja": LanguageSpec("ja", "Japanese", "jpn_Jpan", "ja"),
    "ko": LanguageSpec("ko", "Korean", "kor_Hang", "ko"),
    "bn": LanguageSpec("bn", "Bengali", "ben_Beng", "hi"),
    "ta": LanguageSpec("ta", "Tamil", "tam_Taml", "hi"),
    "te": LanguageSpec("te", "Telugu", "tel_Telu", "hi"),
    "mr": LanguageSpec("mr", "Marathi", "mar_Deva", "hi"),
    "gu": LanguageSpec("gu", "Gujarati", "guj_Gujr", "hi"),
    "pa": LanguageSpec("pa", "Punjabi", "pan_Guru", "hi"),
    "ur": LanguageSpec("ur", "Urdu", "urd_Arab", "ar"),
}


def normalize_code(code: str) -> str:
    return code.strip().lower()


def get_language(code: str) -> LanguageSpec:
    normalized = normalize_code(code)
    if normalized not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported language code: {code}")
    return SUPPORTED_LANGUAGES[normalized]
