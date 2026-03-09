from app.utils.lang_map import get_language


class NLLBTranslator:
    def __init__(self, model_name: str, use_gpu: bool = False) -> None:
        self._model_name = model_name
        self._use_gpu_requested = use_gpu
        self._model = None
        self._tokenizer = None
        self._device = "cpu"
        self._torch = None

    def _lazy_load(self) -> None:
        if self._model is not None and self._tokenizer is not None:
            return
        import torch
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

        self._torch = torch
        use_gpu = self._use_gpu_requested and torch.cuda.is_available()
        self._device = "cuda" if use_gpu else "cpu"
        self._tokenizer = AutoTokenizer.from_pretrained(self._model_name)
        self._model = AutoModelForSeq2SeqLM.from_pretrained(self._model_name)
        self._model.to(self._device)

    def translate(self, text: str, source_language: str, target_language: str) -> str:
        self._lazy_load()
        src = get_language(source_language)
        tgt = get_language(target_language)

        self._tokenizer.src_lang = src.nllb_code
        encoded = self._tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        encoded = {key: value.to(self._device) for key, value in encoded.items()}

        generated_tokens = self._model.generate(
            **encoded,
            forced_bos_token_id=self._tokenizer.convert_tokens_to_ids(tgt.nllb_code),
            max_length=512,
        )
        translated = self._tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)
        return translated[0].strip()
