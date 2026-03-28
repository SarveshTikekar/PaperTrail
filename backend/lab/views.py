import os
import re

from django.conf import settings
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import PANForm49A, VoterIDForm6
from .serializers import FormUploadSerializer


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


def normalize_text(raw_text):
    lines = [line.strip() for line in raw_text.splitlines()]
    return [line for line in lines if line]


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


def build_record_payload(instance, form_type, field_config):
    confidence_payload = instance.confidence_data or {}
    review_fields = confidence_payload.get("review_fields", [])
    raw_text = confidence_payload.get("raw_text", "")
    notes = confidence_payload.get("notes", [])

    return {
        "id": f"{form_type}-{instance.pk}",
        "record_id": instance.pk,
        "form_type": form_type,
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

        if form_type == "pan_49a":
            instance = PANForm49A.objects.create(original_image=image_file)
            language = "eng"
            field_config = PAN_FIELD_CONFIG
            parser = parse_pan_fields
        else:
            instance = VoterIDForm6.objects.create(original_image=image_file)
            language = "hin+eng"
            field_config = VOTER_FIELD_CONFIG
            parser = parse_voter_fields

        image_path = instance.original_image.path
        raw_text, notes = safe_ocr_image_to_string(image_path, language)
        confidence_lookup = build_confidence_lookup(safe_ocr_image_to_data(image_path, language))
        parsed_values = parser(raw_text)

        changed_fields = []
        for field_name, value in parsed_values.items():
            if hasattr(instance, field_name):
                setattr(instance, field_name, value)
                changed_fields.append(field_name)

        review_fields = serialize_review_fields(instance, field_config, confidence_lookup)
        instance.confidence_data = {
            "raw_text": raw_text,
            "notes": notes,
            "review_fields": review_fields,
        }
        changed_fields.append("confidence_data")
        instance.save(update_fields=changed_fields)

        return Response(build_record_payload(instance, form_type, field_config), status=status.HTTP_201_CREATED)
