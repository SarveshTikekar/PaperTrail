import os
import re
import json
import base64
from datetime import datetime
from urllib import error, request

from django.conf import settings
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ExtractionMethod, PANForm49A, VoterIDForm6
from .serializers import ExtractionMethodSerializer, FormUploadSerializer


PAN_FIELD_CONFIG = [
    ("title", "Title"),
    ("full_name_last", "Surname / Last Name"),
    ("full_name_first", "First Name"),
    ("full_name_middle", "Middle Name"),
    ("name_on_card", "Name on PAN Card"),
    ("other_name_last", "Other Surname / Last Name"),
    ("other_name_first", "Other First Name"),
    ("other_name_middle", "Other Middle Name"),
    ("gender", "Gender"),
    ("dob", "Date of Birth"),
    ("father_last", "Father Surname / Last Name"),
    ("father_first", "Father First Name"),
    ("father_middle", "Father Middle Name"),
    ("mother_last", "Mother Surname / Last Name"),
    ("mother_first", "Mother First Name"),
    ("mother_middle", "Mother Middle Name"),
    ("parent_to_print", "Parent Name to Print"),
    ("res_flat", "Residence Flat / Door / Block"),
    ("res_premises", "Residence Premises / Building / Village"),
    ("res_road", "Residence Road / Street / Lane"),
    ("res_area", "Residence Area / Locality / Taluka"),
    ("res_city", "Residence Town / City / District"),
    ("res_state", "Residence State / Union Territory"),
    ("res_pincode", "Residence Pincode"),
    ("res_country", "Residence Country"),
    ("off_name", "Office Name"),
    ("off_flat", "Office Flat / Door / Block"),
    ("off_premises", "Office Premises / Building / Village"),
    ("off_road", "Office Road / Street / Lane"),
    ("off_area", "Office Area / Locality / Taluka"),
    ("off_city", "Office Town / City / District"),
    ("off_state", "Office State / Union Territory"),
    ("off_pincode", "Office Pincode"),
    ("off_country", "Office Country"),
    ("comm_address", "Address for Communication"),
    ("phone_country_code", "ISD Code"),
    ("phone_std_code", "STD Code"),
    ("phone_number", "Phone / Mobile Number"),
    ("email_id", "Email ID"),
    ("applicant_status", "Applicant Status"),
    ("ao_code_area", "AO Code Area"),
    ("ao_code_type", "AO Code Type"),
    ("ao_code_range", "AO Code Range"),
    ("ao_code_number", "AO Code Number"),
    ("aadhaar_number", "Aadhaar Number"),
    ("aadhaar_name", "Name as per Aadhaar"),
]

VOTER_FIELD_CONFIG = [
    ("assembly_constituency", "Assembly Constituency"),
    ("district", "District"),
    ("state", "State"),
    ("name_english", "Applicant Name (English)"),
    ("name_hindi", "Applicant Name (Hindi)"),
    ("surname_english", "Applicant Surname (English)"),
    ("surname_hindi", "Applicant Surname (Hindi)"),
    ("relative_name_english", "Relative Name (English)"),
    ("relative_name_hindi", "Relative Name (Hindi)"),
    ("relative_surname_english", "Relative Surname (English)"),
    ("relative_surname_hindi", "Relative Surname (Hindi)"),
    ("relation_type", "Relation Type"),
    ("mobile_number", "Mobile Number"),
    ("email_id", "Email ID"),
    ("aadhaar_number", "Aadhaar Number"),
    ("gender", "Gender"),
    ("dob", "Date of Birth"),
    ("place_of_birth_town", "Place of Birth Town / Village"),
    ("place_of_birth_district", "Place of Birth District"),
    ("place_of_birth_state", "Place of Birth State"),
    ("house_no", "House No"),
    ("street_area", "Street / Area / Locality"),
    ("town_village", "Town / Village"),
    ("post_office", "Post Office"),
    ("pincode", "Pincode"),
    ("tehsil", "Tehsil"),
    ("disability_type", "Disability Type"),
    ("disability_percentage", "Disability Percentage"),
    ("family_epic_number", "Family EPIC Number"),
    ("residence_since", "Ordinarily Resident Since"),
]

DEFAULT_EXTRACTION_METHODS = [
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

FORM_EXTRACTION_GUIDES = {
    "pan_49a": {
        "document_name": "PAN Form 49A",
        "checkbox_fields": [
            "has_other_name",
            "single_parent_mother_only",
        ],
        "enum_fields": {
            "gender": ["Male", "Female", "Transgender"],
            "parent_to_print": ["Father", "Mother"],
            "comm_address": ["Residence", "Office"],
        },
        "field_instructions": {
            "title": "Applicant title such as Shri, Smt, Kumari, M/s.",
            "name_on_card": "The PAN card print name field, usually uppercase.",
            "has_other_name": "true only when the applicant marked that they were ever known by another name.",
            "single_parent_mother_only": "true only when the mother-only checkbox is marked.",
            "parent_to_print": "Which parent's name should be printed on the PAN card.",
            "ao_code_area": "AO code area value only, not the full AO block.",
            "ao_code_type": "AO type code.",
            "ao_code_range": "AO range code.",
            "ao_code_number": "AO number code.",
            "phone_country_code": "ISD code only.",
            "phone_std_code": "STD code only.",
            "phone_number": "Phone or mobile number only.",
        },
    },
    "voter_6": {
        "document_name": "Voter ID Form 6",
        "checkbox_fields": [],
        "enum_fields": {
            "relation_type": ["Father", "Mother", "Husband", "Wife", "Other"],
            "gender": ["Male", "Female", "Third Gender"],
            "disability_type": ["Locomotor", "Visual", "Hearing", "Speech", "Intellectual", "Other", ""],
        },
        "field_instructions": {
            "name_english": "Applicant given name in English, not surname.",
            "surname_english": "Applicant surname in English.",
            "name_hindi": "Applicant given name in Hindi if present.",
            "surname_hindi": "Applicant surname in Hindi if present.",
            "relative_name_english": "Relative given name in English.",
            "relative_surname_english": "Relative surname in English.",
            "relation_type": "Choose the relation marked on the form.",
            "family_epic_number": "EPIC number of family member or existing voter reference if present.",
            "residence_since": "Date or year since applicant has ordinarily resided at the address.",
        },
    },
}


def normalize_text(raw_text):
    lines = [line.strip() for line in raw_text.splitlines()]
    return [line for line in lines if line]


def normalize_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "yes", "checked", "selected", "1"}:
            return True
        if normalized in {"false", "no", "unchecked", "not selected", "0", ""}:
            return False
    return False


def normalize_date_string(value):
    if not value:
        return ""
    text = str(value).strip().replace("/", "-").replace(".", "-")
    text = re.sub(r"\s+", "", text)

    candidate_formats = (
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d-%m-%y",
        "%Y%m%d",
        "%d%m%Y",
        "%d%m%y",
    )
    for fmt in candidate_formats:
        try:
            parsed = datetime.strptime(text, fmt)
            return parsed.strftime("%Y-%m-%d")
        except ValueError:
            continue

    match = re.search(r"\b(\d{8})\b", text)
    if match:
        raw = match.group(1)
        for fmt in ("%d%m%Y", "%Y%m%d"):
            try:
                parsed = datetime.strptime(raw, fmt)
                return parsed.strftime("%Y-%m-%d")
            except ValueError:
                continue

    return ""


def ensure_default_methods():
    for method_config in DEFAULT_EXTRACTION_METHODS:
        ExtractionMethod.objects.update_or_create(
            slug=method_config["slug"],
            defaults=method_config,
        )


def get_method_or_default(slug):
    ensure_default_methods()
    if slug:
        return ExtractionMethod.objects.filter(slug=slug, is_enabled=True).first()
    return ExtractionMethod.objects.filter(slug="local_ocr").first()


def confidence_bucket(score):
    if score >= 85:
        return "high"
    if score >= 60:
        return "medium"
    return "low"


def safe_ocr_image_to_data(image_path, language):
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        return None

    try:
        if settings.TESSERACT_CMD:
            pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD
        image = Image.open(image_path)
        return pytesseract.image_to_data(image, lang=language, output_type=pytesseract.Output.DICT)
    except Exception:
        return None


def safe_ocr_image_to_string(image_path, language):
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        return "", ["pytesseract is not installed in the backend environment."]

    notes = []
    try:
        if settings.TESSERACT_CMD:
            pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image, lang=language).strip()
        return text, notes
    except Exception as exc:
        notes.append(str(exc))
        return "", notes


def build_confidence_lookup(ocr_data):
    if not ocr_data:
        return {}

    lookup = {}
    for text, confidence in zip(ocr_data.get("text", []), ocr_data.get("conf", [])):
        token = (text or "").strip()
        if not token:
            continue
        try:
            score = float(confidence)
        except (TypeError, ValueError):
            continue
        if score < 0:
            continue
        key = token.lower()
        lookup.setdefault(key, []).append(score)
    return lookup


def infer_confidence(value, lookup):
    tokens = re.findall(r"[A-Za-z0-9@./+-]+", str(value or "").lower())
    scores = [score for token in tokens for score in lookup.get(token, [])]
    if not scores:
        return "low"
    return confidence_bucket(sum(scores) / len(scores))


def parse_common_fields(raw_text):
    values = {}
    compact = " ".join(normalize_text(raw_text))

    email_match = re.search(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", compact, re.I)
    if email_match:
        values["email_id"] = email_match.group(0)

    aadhaar_match = re.search(r"\b\d{4}\s?\d{4}\s?\d{4}\b", compact)
    if aadhaar_match:
        values["aadhaar_number"] = aadhaar_match.group(0).replace(" ", "")

    phone_match = re.search(r"(?<!\d)(?:\+91[-\s]?)?[6-9]\d{9}(?!\d)", compact)
    if phone_match:
        values["phone_number"] = re.sub(r"\D", "", phone_match.group(0))[-10:]
        values["mobile_number"] = values["phone_number"]

    dob_match = re.search(r"\b(\d{2}[/-]\d{2}[/-]\d{4}|\d{4}[/-]\d{2}[/-]\d{2})\b", compact)
    if dob_match:
        values["dob"] = dob_match.group(1).replace("/", "-")

    gender_match = re.search(r"\b(male|female|transgender)\b", compact, re.I)
    if gender_match:
        values["gender"] = gender_match.group(1).title()

    pincode_match = re.search(r"\b\d{6}\b", compact)
    if pincode_match:
        values["res_pincode"] = pincode_match.group(0)
        values["pincode"] = pincode_match.group(0)

    return values


def parse_pan_fields(raw_text):
    values = parse_common_fields(raw_text)
    lines = normalize_text(raw_text)

    for line in lines:
        upper_line = line.upper()
        if "NAME ON CARD" in upper_line and ":" in line:
            values["name_on_card"] = line.split(":", 1)[1].strip()
        if "APPLICANT STATUS" in upper_line and ":" in line:
            values["applicant_status"] = line.split(":", 1)[1].strip()
        if "AADHAAR NAME" in upper_line and ":" in line:
            values["aadhaar_name"] = line.split(":", 1)[1].strip()

    if "name_on_card" not in values:
        for line in lines:
            if re.fullmatch(r"[A-Z][A-Z\s.]{5,}", line):
                values["name_on_card"] = line.strip()
                break

    return values


def parse_voter_fields(raw_text):
    values = parse_common_fields(raw_text)
    lines = normalize_text(raw_text)

    relation_map = {
        "father": "Father",
        "mother": "Mother",
        "husband": "Husband",
        "wife": "Wife",
        "other": "Other",
    }
    joined = " ".join(lines).lower()
    for key, label in relation_map.items():
        if key in joined:
            values["relation_type"] = label
            break

    for line in lines:
        if "constituency" in line.lower() and ":" in line:
            values["assembly_constituency"] = line.split(":", 1)[1].strip()
        if "district" in line.lower() and ":" in line:
            values.setdefault("district", line.split(":", 1)[1].strip())
        if "state" in line.lower() and ":" in line:
            values.setdefault("state", line.split(":", 1)[1].strip())

    return values


def serialize_review_fields(instance, field_config, confidence_lookup):
    review_fields = []
    for field_name, label in field_config:
        value = getattr(instance, field_name, "") or ""
        review_fields.append(
            {
                "id": field_name,
                "label": label,
                "value": str(value),
                "originalOCR": str(value),
                "confidence": infer_confidence(value, confidence_lookup) if value else "low",
            }
        )
    return review_fields


def apply_parsed_values(instance, parsed_values):
    changed_fields = []
    for field_name, value in parsed_values.items():
        if hasattr(instance, field_name):
            if field_name in {"dob", "residence_since"}:
                value = normalize_date_string(value)
                value = value or None
            setattr(instance, field_name, value)
            changed_fields.append(field_name)
    return changed_fields


def extract_with_local_ocr(image_path, language, parser):
    raw_text, notes = safe_ocr_image_to_string(image_path, language)
    confidence_lookup = build_confidence_lookup(safe_ocr_image_to_data(image_path, language))
    parsed_values = parser(raw_text)
    return raw_text, notes, confidence_lookup, parsed_values


def extract_with_openai_vision(image_path, field_config, form_type):
    if not settings.OPENAI_API_KEY:
        return "", ["OPENAI_API_KEY is not configured for OpenAI Vision extraction."], {}, {}

    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

    field_names = [field_name for field_name, _ in field_config]
    field_labels = {field_name: label for field_name, label in field_config}
    guide = FORM_EXTRACTION_GUIDES.get(form_type, {})
    prompt = {
        "task": "extract_form_fields",
        "form_type": form_type,
        "document_name": guide.get("document_name", form_type),
        "instructions": [
            "Read the uploaded government form image carefully.",
            "Map values to the provided field keys exactly.",
            "Use empty strings when a field is missing or unreadable.",
            "Understand labels, checkboxes, radio buttons, and option marks.",
            "Infer selected checkbox values when possible.",
            "Do not merge multiple fields together.",
            "Keep codes, phone numbers, Aadhaar numbers, and pincodes as plain strings.",
            "For booleans, return true or false.",
            "Return only valid JSON.",
        ],
        "fields": [
            {
                "key": field_name,
                "label": field_labels[field_name],
                "instruction": guide.get("field_instructions", {}).get(field_name, ""),
            }
            for field_name in field_names
        ],
        "checkbox_fields": guide.get("checkbox_fields", []),
        "enum_fields": guide.get("enum_fields", {}),
        "output_contract": {
            "fields": {field_name: "string|boolean" for field_name in field_names},
            "notes": ["list of short strings about ambiguity or missing values"],
        },
    }
    payload = {
        "model": settings.OPENAI_EXTRACTION_MODEL,
        "input": [
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": json.dumps(prompt)},
                    {"type": "input_image", "image_url": f"data:image/png;base64,{encoded_image}"},
                ],
            }
        ],
        "text": {"format": {"type": "json_object"}},
    }

    req = request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=90) as response:
            raw_response = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        return "", [f"OpenAI Vision request failed: {exc.read().decode('utf-8', errors='ignore')}"], {}, {}
    except Exception as exc:
        return "", [f"OpenAI Vision request failed: {str(exc)}"], {}, {}

    output_text = raw_response.get("output_text", "")
    if not output_text:
        output_chunks = []
        for item in raw_response.get("output", []):
            for content in item.get("content", []):
                if content.get("type") in {"output_text", "text"} and content.get("text"):
                    output_chunks.append(content["text"])
        output_text = "\n".join(output_chunks).strip()

    try:
        parsed_output = json.loads(output_text or "{}")
    except json.JSONDecodeError:
        return output_text, ["OpenAI Vision returned non-JSON output."], {}, {}

    parsed_values = parsed_output.get("fields", parsed_output if isinstance(parsed_output, dict) else {})
    notes = parsed_output.get("notes", [])
    if isinstance(notes, str):
        notes = [notes]

    normalized_values = {}
    checkbox_fields = set(guide.get("checkbox_fields", []))
    for field_name in field_names:
        value = parsed_values.get(field_name, "")
        if field_name in checkbox_fields:
            normalized_values[field_name] = normalize_bool(value)
        elif isinstance(value, bool):
            normalized_values[field_name] = value
        elif value is None:
            normalized_values[field_name] = ""
        else:
            normalized = str(value).strip()
            if field_name in {"dob", "residence_since"}:
                normalized = normalize_date_string(normalized)
            normalized_values[field_name] = normalized

    return output_text, notes, {}, normalized_values


def extract_with_gemini_vision(image_path, field_config, form_type):
    if not settings.GEMINI_API_KEY:
        return "", ["GEMINI_API_KEY is not configured for Gemini Vision extraction."], {}, {}

    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

    field_names = [field_name for field_name, _ in field_config]
    field_labels = {field_name: label for field_name, label in field_config}
    guide = FORM_EXTRACTION_GUIDES.get(form_type, {})
    prompt_text = json.dumps(
        {
            "task": "extract_form_fields",
            "form_type": form_type,
            "document_name": guide.get("document_name", form_type),
            "instructions": [
                "Read the government form image carefully.",
                "Use layout, labels, table sections, checkboxes, and marked options.",
                "Return only JSON with fields and notes.",
                "Use empty strings for missing values.",
                "Use booleans for checkbox fields.",
            ],
            "fields": [
                {
                    "key": field_name,
                    "label": field_labels[field_name],
                    "instruction": guide.get("field_instructions", {}).get(field_name, ""),
                }
                for field_name in field_names
            ],
            "checkbox_fields": guide.get("checkbox_fields", []),
            "enum_fields": guide.get("enum_fields", {}),
        }
    )

    schema_properties = {}
    for field_name in field_names:
        if field_name in set(guide.get("checkbox_fields", [])):
            schema_properties[field_name] = {"type": "BOOLEAN"}
        else:
            schema_properties[field_name] = {"type": "STRING"}

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "inline_data": {
                            "mime_type": "image/png",
                            "data": encoded_image,
                        }
                    },
                    {"text": prompt_text},
                ],
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": {
                "type": "OBJECT",
                "properties": {
                    "fields": {
                        "type": "OBJECT",
                        "properties": schema_properties,
                    },
                    "notes": {
                        "type": "ARRAY",
                        "items": {"type": "STRING"},
                    },
                },
                "required": ["fields"],
            },
        },
    }

    req = request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_EXTRACTION_MODEL}:generateContent",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "x-goog-api-key": settings.GEMINI_API_KEY,
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=90) as response:
            raw_response = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        return "", [f"Gemini Vision request failed: {exc.read().decode('utf-8', errors='ignore')}"], {}, {}
    except Exception as exc:
        return "", [f"Gemini Vision request failed: {str(exc)}"], {}, {}

    candidates = raw_response.get("candidates", [])
    output_text = ""
    if candidates:
        parts = candidates[0].get("content", {}).get("parts", [])
        output_text = "".join(part.get("text", "") for part in parts if part.get("text")).strip()

    try:
        parsed_output = json.loads(output_text or "{}")
    except json.JSONDecodeError:
        return output_text, ["Gemini Vision returned non-JSON output."], {}, {}

    parsed_values = parsed_output.get("fields", {})
    notes = parsed_output.get("notes", [])
    if isinstance(notes, str):
        notes = [notes]

    normalized_values = {}
    checkbox_fields = set(guide.get("checkbox_fields", []))
    for field_name in field_names:
        value = parsed_values.get(field_name, "")
        if field_name in checkbox_fields:
            normalized_values[field_name] = normalize_bool(value)
        elif value is None:
            normalized_values[field_name] = ""
        else:
            normalized = str(value).strip()
            if field_name in {"dob", "residence_since"}:
                normalized = normalize_date_string(normalized)
            normalized_values[field_name] = normalized

    return output_text, notes, {}, normalized_values


def build_record_payload(instance, form_type, field_config):
    confidence_payload = instance.confidence_data or {}
    review_fields = confidence_payload.get("review_fields", [])
    raw_text = confidence_payload.get("raw_text", "")
    notes = confidence_payload.get("notes", [])

    return {
        "id": f"{form_type}-{instance.pk}",
        "record_id": instance.pk,
        "form_type": form_type,
        "extraction_method": instance.extraction_method,
        "status": instance.status,
        "image_url": instance.original_image.url if instance.original_image else "",
        "raw_text": raw_text,
        "notes": notes,
        "review_fields": review_fields
        or serialize_review_fields(instance, field_config, {}),
        "created_at": instance.created_at.isoformat() if instance.created_at else None,
    }


class FormUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = FormUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        image_file = serializer.validated_data["image"]
        form_type = serializer.validated_data["form_type"]
        extraction_method_slug = serializer.validated_data.get("extraction_method", "").strip()
        extraction_method = get_method_or_default(extraction_method_slug)

        if not extraction_method:
            return Response(
                {"error": "No extraction method is currently enabled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if form_type == "pan_49a":
            instance = PANForm49A.objects.create(
                original_image=image_file,
                extraction_method=extraction_method.slug,
            )
            language = "eng"
            field_config = PAN_FIELD_CONFIG
            parser = parse_pan_fields
        else:
            instance = VoterIDForm6.objects.create(
                original_image=image_file,
                extraction_method=extraction_method.slug,
            )
            language = "hin+eng"
            field_config = VOTER_FIELD_CONFIG
            parser = parse_voter_fields

        image_path = instance.original_image.path
        if extraction_method.slug == "openai_vision":
            raw_text, notes, confidence_lookup, parsed_values = extract_with_openai_vision(
                image_path,
                field_config,
                form_type,
            )
        elif extraction_method.slug == "gemini_vision":
            raw_text, notes, confidence_lookup, parsed_values = extract_with_gemini_vision(
                image_path,
                field_config,
                form_type,
            )
        else:
            raw_text, notes, confidence_lookup, parsed_values = extract_with_local_ocr(
                image_path,
                language,
                parser,
            )

        changed_fields = apply_parsed_values(instance, parsed_values)

        review_fields = serialize_review_fields(instance, field_config, confidence_lookup)
        instance.confidence_data = {
            "raw_text": raw_text,
            "notes": notes,
            "review_fields": review_fields,
            "method": extraction_method.slug,
        }
        changed_fields.append("confidence_data")
        changed_fields.append("extraction_method")
        instance.save(update_fields=changed_fields)

        return Response(build_record_payload(instance, form_type, field_config), status=status.HTTP_201_CREATED)


class ExtractionMethodListView(APIView):
    def get(self, request):
        ensure_default_methods()
        methods = ExtractionMethod.objects.filter(is_visible=True)
        return Response(ExtractionMethodSerializer(methods, many=True).data)


class ExtractionMethodDetailView(APIView):
    def patch(self, request, slug):
        ensure_default_methods()
        method = ExtractionMethod.objects.filter(slug=slug).first()
        if not method:
            return Response({"error": "Extraction method not found."}, status=status.HTTP_404_NOT_FOUND)

        allowed_fields = {"is_visible", "is_enabled", "sort_order", "description", "name"}
        updated_fields = []
        for field_name, value in request.data.items():
            if field_name in allowed_fields:
                setattr(method, field_name, value)
                updated_fields.append(field_name)

        if updated_fields:
            method.save(update_fields=updated_fields)

        return Response(ExtractionMethodSerializer(method).data)
