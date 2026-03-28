from .models import ExtractionMethod


def get_default_extraction_methods(settings):
    return [
        {
            "slug": "local_ocr",
            "name": "Local OCR",
            "provider": "Tesseract",
            "description": "Fast local OCR using Tesseract. Good for text-heavy fields, weaker on checkboxes and layout understanding.",
            "is_visible": True,
            "is_enabled": True,
            "supports_images": True,
            "supports_checkboxes": False,
            "requires_api_key": False,
            "sort_order": 1,
        },
        {
            "slug": "openai_vision",
            "name": "OpenAI Vision",
            "provider": "OpenAI",
            "description": "Uses a multimodal model to read the form image, infer label-value pairs, and reason about selected checkboxes.",
            "is_visible": True,
            "is_enabled": bool(settings.OPENAI_API_KEY),
            "supports_images": True,
            "supports_checkboxes": True,
            "requires_api_key": True,
            "sort_order": 2,
        },
        {
            "slug": "azure_document_intelligence",
            "name": "Azure Document Intelligence",
            "provider": "Microsoft Azure",
            "description": "Strong fit for document layouts, selection marks, and forms when Azure credentials are configured.",
            "is_visible": False,
            "is_enabled": False,
            "supports_images": True,
            "supports_checkboxes": True,
            "requires_api_key": True,
            "sort_order": 3,
        },
        {
            "slug": "gemini_vision",
            "name": "Gemini Vision",
            "provider": "Google Gemini",
            "description": "Uses Gemini multimodal understanding for field extraction, checkbox reasoning, and layout-aware form reading.",
            "is_visible": True,
            "is_enabled": bool(settings.GEMINI_API_KEY),
            "supports_images": True,
            "supports_checkboxes": True,
            "requires_api_key": True,
            "sort_order": 4,
        },
        {
            "slug": "google_document_ai",
            "name": "Google Document AI",
            "provider": "Google Cloud",
            "description": "Specialized document parser for forms and checkbox-style inputs when GCP setup is available.",
            "is_visible": False,
            "is_enabled": False,
            "supports_images": True,
            "supports_checkboxes": True,
            "requires_api_key": True,
            "sort_order": 5,
        },
    ]


def seed_extraction_methods(settings):
    seeded = []
    for method_config in get_default_extraction_methods(settings):
        method, _ = ExtractionMethod.objects.update_or_create(
            slug=method_config["slug"],
            defaults=method_config,
        )
        seeded.append(method)
    return seeded
