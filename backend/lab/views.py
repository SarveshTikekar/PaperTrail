import os
import re
import json
import base64
import io
import tempfile
from datetime import datetime
from urllib import error, request

from django.conf import settings
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ExtractionMethod, PANForm49A, VoterIDForm6
from .serializers import ExtractionMethodSerializer, FormUploadSerializer
from .seeds import seed_extraction_methods


PAN_FIELD_CONFIG = [
    ("title", "Title"),
    ("full_name_last", "Surname / Last Name"),
    ("full_name_first", "First Name"),
    ("full_name_middle", "Middle Name"),
    ("name_on_card", "Name on PAN Card"),
    ("has_other_name", "Ever Known by Other Name"),
    ("other_name_last", "Other Surname / Last Name"),
    ("other_name_first", "Other First Name"),
    ("other_name_middle", "Other Middle Name"),
    ("gender", "Gender"),
    ("dob", "Date of Birth"),
    ("single_parent_mother_only", "Mother is Single Parent"),
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
            "full_name_last": "Applicant surname from section 1 only.",
            "full_name_first": "Applicant first name from section 1 only.",
            "full_name_middle": "Applicant middle name from section 1 only.",
            "name_on_card": "The PAN card print name field, usually uppercase.",
            "has_other_name": "true only when the applicant marked that they were ever known by another name.",
            "other_name_last": "Only fill when the other-name Yes checkbox is selected.",
            "other_name_first": "Only fill when the other-name Yes checkbox is selected.",
            "other_name_middle": "Only fill when the other-name Yes checkbox is selected.",
            "single_parent_mother_only": "true only when the mother-only checkbox is marked.",
            "father_last": "Father surname from the father block only.",
            "father_first": "Father first name from the father block only.",
            "father_middle": "Father middle name from the father block only.",
            "mother_last": "Mother surname from the mother block only.",
            "mother_first": "Mother first name from the mother block only.",
            "mother_middle": "Mother middle name from the mother block only.",
            "parent_to_print": "Which parent's name should be printed on the PAN card.",
            "res_flat": "Residence address line: Flat/Room/Door/Block number only.",
            "res_premises": "Residence address line: premises/building/village only.",
            "res_road": "Residence address line: road/street/lane/post office only.",
            "res_area": "Residence address line: area/locality/taluka/sub-division only.",
            "res_city": "Residence town/city/district only.",
            "res_state": "Residence state or union territory only.",
            "res_pincode": "Residence pincode only.",
            "res_country": "Residence country only.",
            "off_name": "Office name only.",
            "off_flat": "Office address line: Flat/Room/Door/Block number only.",
            "off_premises": "Office address line: premises/building/village only.",
            "off_road": "Office address line: road/street/lane/post office only.",
            "off_area": "Office address line: area/locality/taluka/sub-division only.",
            "off_city": "Office town/city/district only.",
            "off_state": "Office state or union territory only.",
            "off_pincode": "Office pincode only.",
            "off_country": "Office country only.",
            "comm_address": "Selected communication address option only: Residence or Office.",
            "ao_code_area": "AO code area value only, not the full AO block.",
            "ao_code_type": "AO type code.",
            "ao_code_range": "AO range code.",
            "ao_code_number": "AO number code.",
            "aadhaar_number": "Aadhaar number digits only.",
            "aadhaar_name": "Name exactly as shown in Aadhaar section.",
            "phone_country_code": "ISD code only.",
            "phone_std_code": "STD code only.",
            "phone_number": "Phone or mobile number only.",
        },
        "logical_groups": {
            "applicant_identity": [
                "title",
                "full_name_last",
                "full_name_first",
                "full_name_middle",
                "name_on_card",
                "gender",
                "dob",
            ],
            "other_name": [
                "has_other_name",
                "other_name_last",
                "other_name_first",
                "other_name_middle",
            ],
            "parents": [
                "single_parent_mother_only",
                "father_last",
                "father_first",
                "father_middle",
                "mother_last",
                "mother_first",
                "mother_middle",
                "parent_to_print",
            ],
            "residence_address": [
                "res_flat",
                "res_premises",
                "res_road",
                "res_area",
                "res_city",
                "res_state",
                "res_pincode",
                "res_country",
            ],
            "office_address": [
                "off_name",
                "off_flat",
                "off_premises",
                "off_road",
                "off_area",
                "off_city",
                "off_state",
                "off_pincode",
                "off_country",
            ],
            "contact_and_codes": [
                "comm_address",
                "phone_country_code",
                "phone_std_code",
                "phone_number",
                "email_id",
                "applicant_status",
                "ao_code_area",
                "ao_code_type",
                "ao_code_range",
                "ao_code_number",
                "aadhaar_number",
                "aadhaar_name",
            ],
        },
        "semantic_rules": [
            "Extract only the applicant's values for section 1 full name fields; never place parent names there.",
            "Use the name-on-card field only for the abbreviated PAN card print name.",
            "If has_other_name is false, keep all other_name_* fields empty.",
            "If single_parent_mother_only is true, keep the checkbox true but still extract father and mother names only when visible.",
            "Use father_* fields only from the father block and mother_* fields only from the mother block.",
            "For parent_to_print, choose only Father or Mother based on the selected option in the PAN-card print-name row.",
            "Residence and office address lines must stay in their own sections and must not be merged.",
            "Phone country code, STD code, and phone number must be split into separate fields when visible.",
        ],
        "grounding_rules": [
            "Only fill a field when the value is grounded in visible text or a clearly selected checkbox/radio.",
            "Do not guess missing names, dates, address parts, codes, or enum values.",
            "For checkboxes, use true only when there is a visible tick, mark, or selected radio evidence.",
            "When OCR is uncertain or ambiguous, prefer empty string for text fields and false for checkbox fields.",
            "If multiple nearby values compete for one field, choose the one closest to the field label or box on the form.",
        ],
    },
    "voter_6": {
        "document_name": "Voter ID Form 6",
        "checkbox_fields": [],
        "enum_fields": {
            "relation_type": ["Father", "Mother", "Husband", "Wife", "Legal Guardian", "Guru", "Other"],
            "gender": ["Male", "Female", "Third Gender"],
            "disability_type": ["Locomotive", "Visual", "Deaf and Dumb", "Other", ""],
        },
        "field_instructions": {
            "assembly_constituency": "Assembly constituency number and name together when present. For UT parliamentary-only forms, use the constituency shown on the application.",
            "district": "District from the present residence section or declaration fields only, not the printed office heading.",
            "state": "State or UT from the present residence or declaration fields only.",
            "name_english": "Applicant first name followed by middle name from section 1(b) English block only.",
            "surname_english": "Applicant surname from section 1(b) English block only.",
            "name_hindi": "Applicant first name followed by middle name from section 1(a) official language block only.",
            "surname_hindi": "Applicant surname from section 1(a) official language block only.",
            "relative_name_english": "Relative first name followed by middle name from section 2(b) English block only.",
            "relative_surname_english": "Relative surname from section 2(b) English block only.",
            "relative_name_hindi": "Relative first name followed by middle name from section 2(a) official language block only.",
            "relative_surname_hindi": "Relative surname from section 2(a) official language block only.",
            "relation_type": "Choose only the selected relation option: Father, Mother, Husband, Wife, Legal Guardian, Guru, or Other.",
            "mobile_number": "Prefer applicant mobile number. Use relative mobile only when the form clearly provides only that number.",
            "email_id": "Prefer applicant email. Use relative email only when the form clearly provides only that email.",
            "aadhaar_number": "Aadhaar number digits only. Leave blank when the applicant marked that Aadhaar is not available.",
            "gender": "Selected gender option only.",
            "dob": "Date of birth from section 7(a) only.",
            "place_of_birth_town": "Village or town from declaration clause (i) only.",
            "place_of_birth_district": "District from declaration clause (i) only.",
            "place_of_birth_state": "State or UT from declaration clause (i) only.",
            "house_no": "House/Building/Apartment number from present residence section only.",
            "street_area": "Street/Area/Locality/Mohalla/Road from present residence section only.",
            "town_village": "Town or village from present residence section only.",
            "post_office": "Post office from present residence section only.",
            "pincode": "PIN code from present residence section only.",
            "tehsil": "Tehsil/Taluqa/Mandal from present residence section only.",
            "disability_type": "Selected disability category only. Use Other only when another disability is written.",
            "disability_percentage": "Percentage of disability only, without the percent sign when possible.",
            "family_epic_number": "EPIC number of the family member already enrolled at the current address.",
            "residence_since": "Month/year or date since the applicant has ordinarily resided at the address, from declaration clause (ii) only.",
        },
        "logical_groups": {
            "constituency": ["assembly_constituency"],
            "applicant_name": ["name_hindi", "surname_hindi", "name_english", "surname_english"],
            "relative_details": [
                "relation_type",
                "relative_name_hindi",
                "relative_surname_hindi",
                "relative_name_english",
                "relative_surname_english",
            ],
            "identity_contact": ["mobile_number", "email_id", "aadhaar_number", "gender", "dob"],
            "birth_details": ["place_of_birth_town", "place_of_birth_district", "place_of_birth_state"],
            "present_residence": [
                "house_no",
                "street_area",
                "town_village",
                "post_office",
                "pincode",
                "tehsil",
                "district",
                "state",
            ],
            "disability_and_family": ["disability_type", "disability_percentage", "family_epic_number"],
            "declaration": ["place_of_birth_town", "place_of_birth_district", "place_of_birth_state", "residence_since"],
        },
        "semantic_rules": [
            "Keep applicant and relative names strictly separate; never swap or merge them.",
            "Use the official-language name fields only from section 1(a) and the English name fields only from section 1(b).",
            "Use relation_type only from the selected relative option in section 2.",
            "Keep given-name-plus-middle-name and surname separate when the form provides them separately.",
            "Prefer the applicant's own contact details over the relative's when both are present.",
            "Leave aadhaar_number blank when the form indicates the applicant cannot furnish Aadhaar.",
            "Use date of birth only from section 7(a), not from proof-document text.",
            "Use present residence fields only from section 8(a), not from proof-of-address instruction lines.",
            "Use disability_type only when a disability option or description is actually filled.",
            "Use family_epic_number only from section 10 and not from general printed EPIC references.",
            "Use place_of_birth_* and residence_since only from the declaration block.",
        ],
        "grounding_rules": [
            "Extract only visible user-provided values from the form image and ignore instructional text.",
            "Do not infer Hindi or English spellings when they are not visible on the page.",
            "Do not copy printed option labels as answers unless one is clearly selected or filled.",
            "If self-versus-relative contact ownership is ambiguous, keep the uncertain contact field blank.",
            "Use enum values only when the marked option, filled text, or nearby label supports them.",
            "If the residence address is partially filled, keep only the visible parts and leave the rest blank.",
            "Do not invent district, state, birth place, Aadhaar, or EPIC values from context.",
        ],
    },
}


def build_grouped_prompt_schema(field_config, guide):
    grouped = {}
    labels = {field_name: label for field_name, label in field_config}
    instructions = guide.get("field_instructions", {})
    for group_name, field_names in guide.get("logical_groups", {}).items():
        grouped[group_name] = [
            {
                "key": field_name,
                "label": labels.get(field_name, field_name),
                "instruction": instructions.get(field_name, ""),
            }
            for field_name in field_names
            if field_name in labels
        ]
    return grouped


def flatten_grouped_field_values(parsed_values, guide):
    if not isinstance(parsed_values, dict):
        return {}

    flattened = {}
    group_map = guide.get("logical_groups", {})
    for key, value in parsed_values.items():
        if key in group_map and isinstance(value, dict):
            for field_name in group_map[key]:
                if field_name in value:
                    flattened[field_name] = value.get(field_name, "")
        else:
            flattened[key] = value
    return flattened


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
    seed_extraction_methods(settings)


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
        from PIL import Image, ImageOps
    except ImportError:
        return None

    try:
        if settings.TESSERACT_CMD:
            pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD
        image = Image.open(image_path)
        candidates = [
            image,
            ImageOps.autocontrast(image.convert("L")),
        ]
        best_data = None
        best_token_count = -1
        for candidate in candidates:
            ocr_data = pytesseract.image_to_data(candidate, lang=language, output_type=pytesseract.Output.DICT)
            token_count = len([token for token in ocr_data.get("text", []) if (token or "").strip()])
            if token_count > best_token_count:
                best_data = ocr_data
                best_token_count = token_count
        return best_data
    except Exception:
        return None


def safe_ocr_image_to_string(image_path, language):
    try:
        import pytesseract
        from PIL import Image, ImageOps
    except ImportError:
        return "", ["pytesseract is not installed in the backend environment."]

    notes = []
    try:
        if settings.TESSERACT_CMD:
            pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD
        image = Image.open(image_path)
        candidates = [
            ("default", image, "--psm 6"),
            ("grayscale", ImageOps.autocontrast(image.convert("L")), "--psm 6"),
            ("sparse", ImageOps.autocontrast(image.convert("L")), "--psm 11"),
        ]
        best_text = ""
        best_label = "default"
        for label, candidate, config in candidates:
            text = pytesseract.image_to_string(candidate, lang=language, config=config).strip()
            if len(text) > len(best_text):
                best_text = text
                best_label = label
        if best_label != "default":
            notes.append(f"Tesseract used {best_label} OCR preprocessing.")
        return best_text, notes
    except Exception as exc:
        notes.append(str(exc))
        return "", notes


def encode_image_for_llm(image_path, max_size=(1600, 1600), jpeg_quality=80, force_size=None):
    """
    Encode an image as base64 JPEG for use with LLM vision APIs.

    force_size: if set to a (width, height) tuple, the image is padded to square
    then resized to exactly that size. Required for models like glm-ocr (GLM-4V)
    which assert a fixed patch-grid dimension at the GGML level (448x448).
    """
    try:
        from PIL import Image, ImageOps
    except ImportError:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    with Image.open(image_path) as image:
        prepared = ImageOps.exif_transpose(image).convert("RGB")
        if force_size is not None:
            # Pad to square first so the document isn't squashed, then resize exactly.
            w, h = prepared.size
            side = max(w, h)
            padded = Image.new("RGB", (side, side), (255, 255, 255))
            padded.paste(prepared, ((side - w) // 2, (side - h) // 2))
            prepared = padded.resize(force_size, Image.LANCZOS)
        else:
            prepared.thumbnail(max_size)
        buffer = io.BytesIO()
        prepared.save(buffer, format="JPEG", quality=jpeg_quality, optimize=True)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")


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


def collect_following_lines(lines, start_index, limit=3):
    collected = []
    for line in lines[start_index + 1 : start_index + 1 + limit]:
        if line:
            collected.append(line.strip())
    return collected


def split_name_parts(text):
    cleaned = re.sub(r"\s+", " ", str(text or "").strip(" :,-"))
    if not cleaned:
        return "", "", ""
    parts = cleaned.split(" ")
    if len(parts) == 1:
        return "", parts[0], ""
    if len(parts) == 2:
        return parts[1], parts[0], ""
    return parts[-1], parts[0], " ".join(parts[1:-1])


def extract_value_after_label(lines, patterns, max_following=2):
    for index, line in enumerate(lines):
        lowered = line.lower()
        if any(re.search(pattern, lowered) for pattern in patterns):
            if ":" in line:
                tail = line.split(":", 1)[1].strip()
                if tail:
                    return tail
            following = collect_following_lines(lines, index, max_following)
            for candidate in following:
                if not any(re.search(pattern, candidate.lower()) for pattern in patterns):
                    return candidate
    return ""


def parse_pan_fields(raw_text):
    values = parse_common_fields(raw_text)
    lines = normalize_text(raw_text)
    compact = " ".join(lines)

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

    title_match = re.search(r"\b(shri|smt|kumari|m/s)\b", compact, re.I)
    if title_match:
        title = title_match.group(1)
        values["title"] = "M/s." if title.lower() == "m/s" else title.title()

    if "parent_to_print" not in values:
        parent_match = re.search(r"Father['’]s name\s+Mother['’]s name|Father\s+Mother", compact, re.I)
        if parent_match:
            values["parent_to_print"] = "Mother"

    if "comm_address" not in values:
        comm_match = re.search(r"communication.*?(residence|office)", compact, re.I)
        if comm_match:
            values["comm_address"] = comm_match.group(1).title()

    if "applicant_status" not in values:
        status_match = re.search(
            r"\b(individual|company|trust|partnership|body of individuals|association of persons)\b",
            compact,
            re.I,
        )
        if status_match:
            values["applicant_status"] = status_match.group(1).title()

    aadhaar_name_match = re.search(r"name as per aadhaar[:\s]+([A-Z][A-Z\s.]{3,})", compact, re.I)
    if aadhaar_name_match:
        values["aadhaar_name"] = re.sub(r"\s+", " ", aadhaar_name_match.group(1)).strip()

    ao_match = re.search(
        r"Area code\s*([A-Z0-9]{1,4}).*?AO type\s*([A-Z]{1,3}).*?Range code\s*([A-Z0-9]{1,4}).*?AO No\.?\s*([A-Z0-9]{1,4})",
        compact,
        re.I,
    )
    if ao_match:
        values["ao_code_area"] = ao_match.group(1).upper()
        values["ao_code_type"] = ao_match.group(2).upper()
        values["ao_code_range"] = ao_match.group(3).upper()
        values["ao_code_number"] = ao_match.group(4).upper()

    if "dob" not in values:
        digits = "".join(re.findall(r"\d", compact))
        for index in range(max(len(digits) - 7, 0)):
            candidate = digits[index : index + 8]
            normalized = normalize_date_string(candidate)
            if normalized:
                values["dob"] = normalized
                break

    if not values.get("name_on_card"):
        candidate = extract_value_after_label(lines, [r"name on.*pan card", r"abbreviations of the above name"], 2)
        if candidate:
            values["name_on_card"] = candidate

    applicant_name_line = extract_value_after_label(lines, [r"full name", r"last name / surname"], 3)
    if applicant_name_line:
        last_name, first_name, middle_name = split_name_parts(applicant_name_line)
        values.setdefault("full_name_last", last_name)
        values.setdefault("full_name_first", first_name)
        values.setdefault("full_name_middle", middle_name)

    father_line = extract_value_after_label(lines, [r"father.?s name"], 3)
    if father_line:
        last_name, first_name, middle_name = split_name_parts(father_line)
        values.setdefault("father_last", last_name)
        values.setdefault("father_first", first_name)
        values.setdefault("father_middle", middle_name)

    mother_line = extract_value_after_label(lines, [r"mother.?s name"], 3)
    if mother_line:
        last_name, first_name, middle_name = split_name_parts(mother_line)
        values.setdefault("mother_last", last_name)
        values.setdefault("mother_first", first_name)
        values.setdefault("mother_middle", middle_name)

    return values


def parse_voter_fields(raw_text):
    values = parse_common_fields(raw_text)
    lines = normalize_text(raw_text)
    compact = " ".join(lines)

    relation_map = {
        "father": "Father",
        "mother": "Mother",
        "husband": "Husband",
        "wife": "Wife",
        "legal guardian": "Legal Guardian",
        "guru": "Guru",
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

    applicant_english = extract_value_after_label(lines, [r"name.*english", r"\(1\)\(b\)"], 3)
    if applicant_english:
        surname, first_name, middle_name = split_name_parts(applicant_english)
        values.setdefault("name_english", " ".join(part for part in [first_name, middle_name] if part).strip())
        values.setdefault("surname_english", surname)

    applicant_official = extract_value_after_label(lines, [r"name.*official language", r"\(1\)\(a\)"], 3)
    if applicant_official:
        surname, first_name, middle_name = split_name_parts(applicant_official)
        values.setdefault("name_hindi", " ".join(part for part in [first_name, middle_name] if part).strip())
        values.setdefault("surname_hindi", surname)

    relative_english = extract_value_after_label(lines, [r"relative mentioned above", r"\(2\)\(b\)"], 3)
    if relative_english:
        surname, first_name, middle_name = split_name_parts(relative_english)
        values.setdefault("relative_name_english", " ".join(part for part in [first_name, middle_name] if part).strip())
        values.setdefault("relative_surname_english", surname)

    relative_official = extract_value_after_label(lines, [r"relatives", r"official language of state", r"\(2\)\(a\)"], 3)
    if relative_official:
        surname, first_name, middle_name = split_name_parts(relative_official)
        values.setdefault("relative_name_hindi", " ".join(part for part in [first_name, middle_name] if part).strip())
        values.setdefault("relative_surname_hindi", surname)

    house_no = extract_value_after_label(lines, [r"house/building/apartment no", r"house"], 2)
    if house_no:
        values["house_no"] = house_no

    street_area = extract_value_after_label(lines, [r"street/area/locality", r"mohalla/road"], 2)
    if street_area:
        values["street_area"] = street_area

    town_village = extract_value_after_label(lines, [r"town/village"], 2)
    if town_village:
        values["town_village"] = town_village

    post_office = extract_value_after_label(lines, [r"post office"], 2)
    if post_office:
        values["post_office"] = post_office

    tehsil = extract_value_after_label(lines, [r"tehsil/taluqa/mandal"], 2)
    if tehsil:
        values["tehsil"] = tehsil

    if not values.get("district"):
        district = extract_value_after_label(lines, [r"\bdistrict\b"], 2)
        if district:
            values["district"] = district

    if not values.get("state"):
        state = extract_value_after_label(lines, [r"state/ut", r"\bstate\b"], 2)
        if state:
            values["state"] = state

    birth_place_match = re.search(
        r"place of my birth is.*?village/town\s*([A-Za-z0-9 .'-]+)\s+district\s*([A-Za-z0-9 .'-]+)\s+state/ut\s*([A-Za-z0-9 .'-]+)",
        compact,
        re.I,
    )
    if birth_place_match:
        values["place_of_birth_town"] = birth_place_match.group(1).strip()
        values["place_of_birth_district"] = birth_place_match.group(2).strip()
        values["place_of_birth_state"] = birth_place_match.group(3).strip()

    residence_since_match = re.search(r"resident .*? since\s*([A-Za-z0-9/\- ]{3,20})", compact, re.I)
    if residence_since_match:
        values["residence_since"] = residence_since_match.group(1).strip()

    disability_match = re.search(r"\b(locomotive|visual|deaf\s*&?\s*dumb|other)\b", compact, re.I)
    if disability_match:
        disability_value = disability_match.group(1).strip()
        if re.search(r"deaf", disability_value, re.I):
            values["disability_type"] = "Deaf and Dumb"
        else:
            values["disability_type"] = disability_value.title()

    percentage_match = re.search(r"percentage of disability[:\s]*([0-9]{1,3}(?:\.[0-9]+)?)", compact, re.I)
    if percentage_match:
        values["disability_percentage"] = percentage_match.group(1)

    epic_match = re.search(r"epic\s*no\.?[:\s]*([A-Z0-9]{6,})", compact, re.I)
    if epic_match:
        values["family_epic_number"] = epic_match.group(1).strip()

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


def serialize_review_fields_from_values(parsed_values, field_config, confidence_lookup):
    review_fields = []
    for field_name, label in field_config:
        value = parsed_values.get(field_name, "") or ""
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


def _string_value(value):
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value).strip()


def parsed_values_are_low_quality(parsed_values, field_config):
    if not parsed_values:
        return True, "Model returned no parsed values."

    field_names = [field_name for field_name, _ in field_config]
    values = [parsed_values.get(field_name, "") for field_name in field_names]
    filled_values = [value for value in values if value not in ("", None, False)]
    if not filled_values:
        return True, "Model returned no filled fields."

    normalized = [_string_value(value).lower() for value in filled_values if _string_value(value)]
    if not normalized:
        return True, "Model filled values collapsed to empty strings after normalization."

    repeated_ratio = max(normalized.count(item) for item in set(normalized)) / max(len(normalized), 1)
    suspicious_tokens = {
        "hello world",
        "string",
        "boolean",
        "true",
        "false",
        "null",
        "n/a",
        "unknown",
    }
    suspicious_hits = sum(1 for item in normalized if item in suspicious_tokens)

    if repeated_ratio >= 0.6:
        return True, f"Too many repeated values in model output (repeated_ratio={repeated_ratio:.2f})."
    if suspicious_hits >= max(2, len(normalized) // 2):
        return True, f"Model output contained suspicious placeholder-like values ({suspicious_hits} hits)."
    return False, ""


def merge_parsed_values(primary_values, fallback_values, field_config):
    merged = {}
    for field_name, _ in field_config:
        primary_value = primary_values.get(field_name, "")
        fallback_value = fallback_values.get(field_name, "")
        if primary_value in ("", None):
            merged[field_name] = fallback_value
        else:
            merged[field_name] = primary_value
    return merged


def normalize_for_grounding(value):
    return re.sub(r"[^a-z0-9]+", " ", str(value or "").lower()).strip()


def is_text_value_grounded(field_name, value, raw_text, guide):
    if value in ("", None, False):
        return True
    if isinstance(value, bool):
        return True

    normalized_value = normalize_for_grounding(value)
    normalized_raw = normalize_for_grounding(raw_text)
    if not normalized_value:
        return True

    enum_values = {
        item.lower()
        for item in guide.get("enum_fields", {}).get(field_name, [])
        if item
    }
    if normalized_value in enum_values:
        return True

    if field_name in {"dob", "residence_since"}:
        digits = re.sub(r"\D", "", str(value))
        return bool(digits) and digits in re.sub(r"\D", "", str(raw_text))

    if field_name in {"aadhaar_number", "phone_number", "phone_country_code", "phone_std_code", "res_pincode", "off_pincode", "pincode"}:
        digits = re.sub(r"\D", "", str(value))
        return bool(digits) and digits in re.sub(r"\D", "", str(raw_text))

    strong_tokens = [token for token in normalized_value.split() if len(token) >= 3]
    if not strong_tokens:
        return normalized_value in normalized_raw

    matched = sum(1 for token in strong_tokens if token in normalized_raw)
    return matched >= max(1, len(strong_tokens) - 1)


def filter_ungrounded_values(parsed_values, raw_text, field_config, guide):
    filtered = {}
    rejected = []
    for field_name, _ in field_config:
        value = parsed_values.get(field_name, "")
        if is_text_value_grounded(field_name, value, raw_text, guide):
            filtered[field_name] = value
        else:
            filtered[field_name] = False if field_name in set(guide.get("checkbox_fields", [])) else ""
            rejected.append(field_name)
    return filtered, rejected


def extract_with_openai_vision(image_path, field_config, form_type):
    if not settings.OPENAI_API_KEY:
        return "", ["OPENAI_API_KEY is not configured for OpenAI Vision extraction."], {}, {}

    encoded_image = encode_image_for_llm(image_path)

    field_names = [field_name for field_name, _ in field_config]
    field_labels = {field_name: label for field_name, label in field_config}
    guide = FORM_EXTRACTION_GUIDES.get(form_type, {})
    grouped_schema = build_grouped_prompt_schema(field_config, guide)
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
            "Follow the semantic and grounding rules strictly.",
            "Return only valid JSON.",
        ],
        "semantic_rules": guide.get("semantic_rules", []),
        "grounding_rules": guide.get("grounding_rules", []),
        "grouped_fields": grouped_schema,
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
    parsed_values = flatten_grouped_field_values(parsed_values, guide)
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

    encoded_image = encode_image_for_llm(image_path)

    field_names = [field_name for field_name, _ in field_config]
    field_labels = {field_name: label for field_name, label in field_config}
    guide = FORM_EXTRACTION_GUIDES.get(form_type, {})
    grouped_schema = build_grouped_prompt_schema(field_config, guide)
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
                "Follow the semantic and grounding rules strictly.",
            ],
            "semantic_rules": guide.get("semantic_rules", []),
            "grounding_rules": guide.get("grounding_rules", []),
            "grouped_fields": grouped_schema,
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
    parsed_values = flatten_grouped_field_values(parsed_values, guide)
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


def extract_with_ollama_model(image_path, field_config, form_type, model_name):
    # glm-ocr (GLM-4V) requires exactly 448x448 to satisfy GGML patch-grid assertion.
    encoded_image = encode_image_for_llm(image_path, force_size=(448, 448), jpeg_quality=85)

    field_names = [field_name for field_name, _ in field_config]
    field_labels = {field_name: label for field_name, label in field_config}
    guide = FORM_EXTRACTION_GUIDES.get(form_type, {})
    checkbox_fields = set(guide.get("checkbox_fields", []))
    grouped_schema = build_grouped_prompt_schema(field_config, guide)
    prompt_lines = [
        f"You are extracting data from {guide.get('document_name', form_type)}.",
        "Read the uploaded form image carefully and return only valid JSON.",
        "Do not explain anything. Do not return a schema. Do not describe types.",
        "The JSON must have exactly two keys: fields and notes.",
        "fields must contain actual extracted values, not placeholders.",
        "For missing values use empty string.",
        "For checkbox fields use true or false only.",
        "For dates use YYYY-MM-DD when possible, otherwise empty string.",
        "Use labels, nearby text, checkboxes, section grouping, and layout.",
        "If a checkbox is not clearly selected, use false.",
        "Follow the semantic rules and grounding rules strictly.",
        "",
        "Grouped field schema:",
        json.dumps(grouped_schema, ensure_ascii=True),
        "",
        "Semantic rules:",
    ]
    for rule in guide.get("semantic_rules", []):
        prompt_lines.append(f"- {rule}")
    prompt_lines.append("")
    prompt_lines.append("Grounding rules:")
    for rule in guide.get("grounding_rules", []):
        prompt_lines.append(f"- {rule}")
    prompt_lines.extend(
        [
            "",
            "Fields to extract:",
        ]
    )
    for field_name in field_names:
        instruction = guide.get("field_instructions", {}).get(field_name, "")
        label = field_labels[field_name]
        suffix = f" - {instruction}" if instruction else ""
        prompt_lines.append(f"- {field_name}: {label}{suffix}")

    if guide.get("enum_fields"):
        prompt_lines.append("")
        prompt_lines.append("Allowed values for enum-like fields:")
        for key, values in guide["enum_fields"].items():
            prompt_lines.append(f"- {key}: {', '.join(values)}")

    if checkbox_fields:
        prompt_lines.append("")
        prompt_lines.append(f"Checkbox fields: {', '.join(sorted(checkbox_fields))}")

    example_fields = {
        field_name: (False if field_name in checkbox_fields else "")
        for field_name in field_names
    }
    prompt_lines.extend(
        [
            "",
            "Output example:",
            json.dumps({"fields": example_fields, "notes": []}, ensure_ascii=True),
        ]
    )
    prompt = "\n".join(prompt_lines)

    payload = {
        "model": model_name,
        "messages": [
            {
                "role": "user",
                "content": prompt,
                "images": [encoded_image],
            }
        ],
        "stream": False,
        "options": {
            "temperature": 0,
            "num_ctx": 2048,
        },
        "format": {
            "type": "object",
            "properties": {
                "fields": {
                    "type": "object",
                    "properties": {
                        field_name: {"type": "boolean"} if field_name in checkbox_fields else {"type": "string"}
                        for field_name in field_names
                    },
                },
                "notes": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
            "required": ["fields"],
        },
    }

    req = request.Request(
        f"{settings.OLLAMA_BASE_URL}/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=settings.OLLAMA_REQUEST_TIMEOUT) as response:
            raw_response = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        return "", [f"Ollama Vision request failed: {exc.read().decode('utf-8', errors='ignore')}"], {}, {}
    except Exception as exc:
        return "", [f"Ollama Vision request failed: {str(exc)}"], {}, {}

    output_text = raw_response.get("message", {}).get("content", "").strip()
    try:
        parsed_output = json.loads(output_text or "{}")
    except json.JSONDecodeError:
        return output_text, ["Ollama Vision returned non-JSON output."], {}, {}

    parsed_values = parsed_output.get("fields", {})
    parsed_values = flatten_grouped_field_values(parsed_values, guide)
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


def extract_text_with_ollama_model(image_path, form_type, model_name):
    # glm-ocr (GLM-4V) requires exactly 448x448 to satisfy GGML patch-grid assertion.
    encoded_image = encode_image_for_llm(image_path, force_size=(448, 448), jpeg_quality=85)

    guide = FORM_EXTRACTION_GUIDES.get(form_type, {})
    prompt_lines = [
        f"You are transcribing text from {guide.get('document_name', form_type)}.",
        "Return plain text only.",
        "Do not summarize, explain, or convert into JSON.",
        "Preserve reading order and line breaks as much as possible.",
        "Include visible filled values, labels, section headings, and selected option text when readable.",
        "If a checkbox or radio option is visibly selected, include the selected option label in the transcription.",
        "Do not invent missing text.",
    ]
    payload = {
        "model": model_name,
        "messages": [
            {
                "role": "user",
                "content": "\n".join(prompt_lines),
                "images": [encoded_image],
            }
        ],
        "stream": False,
        "options": {
            "temperature": 0,
            "num_ctx": 2048,
        },
    }

    req = request.Request(
        f"{settings.OLLAMA_BASE_URL}/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=settings.OLLAMA_REQUEST_TIMEOUT) as response:
            raw_response = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        return "", [f"Ollama OCR request failed: {exc.read().decode('utf-8', errors='ignore')}"]
    except Exception as exc:
        return "", [f"Ollama OCR request failed: {str(exc)}"]

    output_text = raw_response.get("message", {}).get("content", "").strip()
    return output_text, []


def extract_with_ollama_vision(image_path, field_config, form_type):
    return extract_text_with_ollama_model(
        image_path,
        form_type,
        settings.OLLAMA_EXTRACTION_MODEL,
    )


def extract_with_minicpm_vision(image_path, field_config, form_type):
    return extract_text_with_ollama_model(
        image_path,
        form_type,
        settings.OLLAMA_MINICPM_MODEL,
    )


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


def get_form_processing_context(form_type):
    if form_type == "pan_49a":
        return {
            "language": "eng",
            "field_config": PAN_FIELD_CONFIG,
            "parser": parse_pan_fields,
        }
    return {
        "language": "hin+eng",
        "field_config": VOTER_FIELD_CONFIG,
        "parser": parse_voter_fields,
    }


def run_extraction_pipeline(image_path, form_type, extraction_method):
    context = get_form_processing_context(form_type)
    language = context["language"]
    field_config = context["field_config"]
    parser = context["parser"]

    local_raw_text, local_notes, local_confidence_lookup, local_parsed_values = extract_with_local_ocr(
        image_path,
        language,
        parser,
    )

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
    elif extraction_method.slug == "ollama_vision":
        raw_text, notes = extract_with_ollama_vision(
            image_path,
            field_config,
            form_type,
        )
        confidence_lookup = local_confidence_lookup
        parsed_values = parser(raw_text)
    elif extraction_method.slug == "minicpm_vision":
        raw_text, notes = extract_with_minicpm_vision(
            image_path,
            field_config,
            form_type,
        )
        confidence_lookup = local_confidence_lookup
        parsed_values = parser(raw_text)
    else:
        raw_text, notes, confidence_lookup, parsed_values = (
            local_raw_text,
            local_notes,
            local_confidence_lookup,
            local_parsed_values,
        )

    if extraction_method.slug != "local_ocr":
        guide = FORM_EXTRACTION_GUIDES.get(form_type, {})
        model_parsed_values = dict(parsed_values)
        grounded_values, rejected_fields = filter_ungrounded_values(parsed_values, local_raw_text or raw_text, field_config, guide)
        if rejected_fields:
            parsed_values = grounded_values
            notes = list(notes) + [f"Removed ungrounded model values for: {', '.join(rejected_fields[:8])}{'...' if len(rejected_fields) > 8 else ''}"]
        low_quality, low_quality_reason = parsed_values_are_low_quality(parsed_values, field_config)
        if low_quality:
            parsed_values = local_parsed_values
            confidence_lookup = local_confidence_lookup
            notes = list(notes) + ["Model output was low quality, so local OCR fields were used instead."]
            if low_quality_reason:
                notes = list(notes) + [f"Low-quality reason: {low_quality_reason}"]
        else:
            parsed_values = merge_parsed_values(parsed_values, local_parsed_values, field_config)
            if local_raw_text and not raw_text:
                raw_text = local_raw_text
            if not confidence_lookup:
                confidence_lookup = local_confidence_lookup
            if any(
                parsed_values.get(field_name, "") == local_parsed_values.get(field_name, "")
                and local_parsed_values.get(field_name, "") not in ("", None)
                for field_name, _ in field_config
            ):
                notes = list(notes) + ["Missing fields were filled from local OCR fallback."]
        debug_payload = {
            "model_parsed_values": model_parsed_values,
            "grounded_values": grounded_values,
            "rejected_fields": rejected_fields,
            "low_quality": low_quality,
            "low_quality_reason": low_quality_reason,
            "local_ocr_values": local_parsed_values,
        }
    else:
        debug_payload = {
            "model_parsed_values": {},
            "grounded_values": parsed_values,
            "rejected_fields": [],
            "low_quality": False,
            "low_quality_reason": "",
            "local_ocr_values": local_parsed_values,
        }

    return {
        "raw_text": raw_text,
        "notes": notes,
        "confidence_lookup": confidence_lookup,
        "parsed_values": parsed_values,
        "field_config": field_config,
        "debug_payload": debug_payload,
        "local_raw_text": local_raw_text,
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
        else:
            instance = VoterIDForm6.objects.create(
                original_image=image_file,
                extraction_method=extraction_method.slug,
            )

        image_path = instance.original_image.path
        extraction_result = run_extraction_pipeline(image_path, form_type, extraction_method)
        raw_text = extraction_result["raw_text"]
        notes = extraction_result["notes"]
        confidence_lookup = extraction_result["confidence_lookup"]
        parsed_values = extraction_result["parsed_values"]
        field_config = extraction_result["field_config"]
        debug_payload = extraction_result["debug_payload"]

        changed_fields = apply_parsed_values(instance, parsed_values)

        review_fields = serialize_review_fields(instance, field_config, confidence_lookup)
        instance.confidence_data = {
            "raw_text": raw_text,
            "notes": notes,
            "review_fields": review_fields,
            "method": extraction_method.slug,
            "debug": debug_payload,
        }
        changed_fields.append("confidence_data")
        changed_fields.append("extraction_method")
        instance.save(update_fields=changed_fields)

        return Response(build_record_payload(instance, form_type, field_config), status=status.HTTP_201_CREATED)


class OCRTestView(APIView):
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

        suffix = os.path.splitext(image_file.name or "")[1] or ".png"
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                for chunk in image_file.chunks():
                    temp_file.write(chunk)
                temp_path = temp_file.name

            extraction_result = run_extraction_pipeline(temp_path, form_type, extraction_method)
            review_fields = serialize_review_fields_from_values(
                extraction_result["parsed_values"],
                extraction_result["field_config"],
                extraction_result["confidence_lookup"],
            )
            return Response(
                {
                    "form_type": form_type,
                    "extraction_method": extraction_method.slug,
                    "raw_text": extraction_result["raw_text"],
                    "notes": extraction_result["notes"],
                    "parsed_values": extraction_result["parsed_values"],
                    "review_fields": review_fields,
                    "debug": extraction_result["debug_payload"],
                }
            )
        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except OSError:
                    pass


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
