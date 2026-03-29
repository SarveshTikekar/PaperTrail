# -*- coding: utf-8 -*-
"""PaperTrail Protect V3 Service

A reusable service for image preprocessing, OCR extraction, and LLM-based structured 
field extraction from government forms.
"""

import os
import re
import json
import requests
import logging
import numpy as np
import cv2
from PIL import Image, ImageOps
import sys
import io
import time

# Force UTF-8 for Windows terminal support
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from django.conf import settings
    if not settings.configured:
        settings = None
except (ImportError, Exception):
    settings = None

try:
    import pandas as pd
except ImportError:
    pd = None
import easyocr

# Configure logging
logger = logging.getLogger(__name__)

class PaperTrailProtectV3:
    """
    Service class for processing documents using OCR (EasyOCR) and 
    LLMs (Mistral/InternVL) for field extraction.
    """

    def __init__(self, languages=['en', 'hi'], gpu=True, hf_api_key=None, featherless_api_key=None):
        """
        Initialize the Reader and API keys.
        """
        logger.info("Initializing EasyOCR Reader...")
        self.reader = easyocr.Reader(languages, gpu=gpu)
        
        if hf_api_key:
            self.hf_api_key = hf_api_key
        elif settings and hasattr(settings, "HF_API_KEY") and settings.HF_API_KEY:
            self.hf_api_key = settings.HF_API_KEY
        else:
            self.hf_api_key = os.environ.get("HF_API_KEY")

        if featherless_api_key:
            self.featherless_api_key = featherless_api_key
        elif settings and hasattr(settings, "FEATHERLESS_API_KEY") and settings.FEATHERLESS_API_KEY:
            self.featherless_api_key = settings.FEATHERLESS_API_KEY
        else:
            self.featherless_api_key = os.environ.get("FEATHERLESS_API_KEY")

        if settings and hasattr(settings, "FEATHERLESS_EXTRACTION_MODEL") and settings.FEATHERLESS_EXTRACTION_MODEL:
            self.featherless_model = settings.FEATHERLESS_EXTRACTION_MODEL
        else:
            self.featherless_model = os.environ.get("FEATHERLESS_EXTRACTION_MODEL", "mistralai/Mistral-7B-Instruct-v0.3")

        if settings and hasattr(settings, "FEATHERLESS_MAX_PROMPT_CHARS"):
            self.featherless_max_prompt_chars = settings.FEATHERLESS_MAX_PROMPT_CHARS
        else:
            self.featherless_max_prompt_chars = int(os.environ.get("FEATHERLESS_MAX_PROMPT_CHARS", "3000"))

        if settings and hasattr(settings, "FEATHERLESS_MAX_COMPLETION_TOKENS"):
            self.featherless_max_completion_tokens = settings.FEATHERLESS_MAX_COMPLETION_TOKENS
        else:
            self.featherless_max_completion_tokens = int(os.environ.get("FEATHERLESS_MAX_COMPLETION_TOKENS", "4096"))

        if not self.hf_api_key:
            logger.warning("HF_API_KEY not found. InternVL extraction will be disabled.")
        if not self.featherless_api_key:
            logger.warning("FEATHERLESS_API_KEY not found. Mistral extraction will be disabled.")

        logger.info("✅ PaperTrailProtectV3 Service Ready")

    def preprocess_image(self, img_source):
        """
        Preprocessing: EXIF Transpose & Enhanced Contrast (CLAHE)
        Accepts: file path, bytes, or numpy array.
        Returns: PIL.Image
        """
        if isinstance(img_source, str):
            img = cv2.imread(img_source)
        elif isinstance(img_source, (bytes, bytearray)):
            arr = np.frombuffer(img_source, np.uint8)
            img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        elif isinstance(img_source, np.ndarray):
            img = img_source
        else:
            # Maybe it's already a PIL image
            if hasattr(img_source, "convert"):
                return ImageOps.exif_transpose(img_source).convert("RGB")
            raise ValueError(f"Unsupported image source type: {type(img_source)}")

        if img is None:
            raise ValueError("Could not decode image with OpenCV")

        # Convert to LAB for CLAHE enhancement
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0)
        l = clahe.apply(l)
        enhanced = cv2.cvtColor(cv2.merge([l, a, b]), cv2.COLOR_LAB2BGR)
        
        # Convert to PIL and handle EXIF orientation
        pil_img = Image.fromarray(cv2.cvtColor(enhanced, cv2.COLOR_BGR2RGB))
        return ImageOps.exif_transpose(pil_img).convert("RGB")

    def extract_text_blocks(self, image):
        """
        Run EasyOCR on the PIL Image.
        """
        img_np = np.array(image)
        results = self.reader.readtext(img_np, detail=1)

        blocks = []
        for (bbox, text, conf) in results:
            x = [p[0] for p in bbox]
            y = [p[1] for p in bbox]

            blocks.append({
                "text": text,
                "confidence": float(conf),
                "bbox": (int(min(x)), int(min(y)), int(max(x)), int(max(y)))
            })

        return blocks

    def get_ocr_blocks(self, image):
        """
        Backwards-compatible alias used by existing view wrappers.
        """
        return self.extract_text_blocks(image)

    def format_blocks_for_prompt(self, blocks):
        """
        Prepare text blocks for the LLM prompt.
        """
        return "\n".join([
            f"Text: {b['text']} | Box: {b['bbox']} | Conf: {b['confidence']}"
            for b in blocks
        ])

    def compact_blocks_for_prompt(self, blocks, max_chars=None):
        """
        Keep the highest-signal OCR blocks while respecting a rough prompt budget.
        """
        if not blocks:
            return ""

        budget = max_chars or self.featherless_max_prompt_chars
        min_confidence = 0.2
        compact_lines = []
        used = 0
        seen_text = set()

        filtered_blocks = []
        for idx, block in enumerate(blocks):
            text = " ".join(str(block.get("text", "")).split())
            if not text:
                continue
            if len(text) < 2:
                continue
            if block.get("confidence", 0.0) < min_confidence:
                continue
            normalized = text.lower()
            if normalized in seen_text:
                continue
            seen_text.add(normalized)
            filtered_blocks.append((idx, block, text))

        if not filtered_blocks:
            filtered_blocks = [
                (idx, block, " ".join(str(block.get("text", "")).split()))
                for idx, block in enumerate(blocks)
                if " ".join(str(block.get("text", "")).split())
            ]

        # Prioritize confident, informative OCR text, but send only the text itself.
        scored_blocks = sorted(
            filtered_blocks,
            key=lambda item: (
                item[1].get("confidence", 0.0),
                min(len(item[2]), 80),
            ),
            reverse=True,
        )

        selected = []
        for idx, block, text in scored_blocks:
            line = text
            line_len = len(line) + 1
            if compact_lines and used + line_len > budget:
                continue
            if not compact_lines and line_len > budget:
                compact_lines.append(line[: max(0, budget - 1)])
                selected.append((idx, compact_lines[0]))
                break

            used += line_len
            selected.append((idx, line))

        selected.sort(key=lambda item: item[0])
        compact_lines = [line for _, line in selected]
        return "\n".join(compact_lines)

    def build_mistral_prompt(self, compact_blocks_text, field_list=None):
        """
        Refined prompt to enforce flat JSON structure and minimize noise.
        """
        field_instruction = ""
        if field_list:
            field_instruction = f"Extract exactly these fields if found: {field_list}. "
        
        return (
            "Extract structured form fields from the following OCR text as a flat JSON dictionary. "
            f"{field_instruction}"
            "Return ONLY a clean JSON object. No conversational text, no markdown blocks, no prefix. "
            "Use standard field names like 'surname', 'first_name', 'dob', 'pan_number', 'father_name'. "
            "Note: Dates should be in DD-MM-YYYY format if readable.\n\n"
            "OCR Data:\n"
            f"{compact_blocks_text}\n\n"
            "JSON Response:"
        )

    def mistral_extract(self, image, blocks_text, blocks=None, field_config=None):
        """
        Extract structured data using Mistral via Featherless API.
        """
        if not self.featherless_api_key:
            logger.debug("Mistral extraction skipped: FEATHERLESS_API_KEY missing.")
            return None

        field_list = None
        if field_config:
            field_list = ", ".join([f[0] for f in field_config])

        headers = {
            "Authorization": f"Bearer {self.featherless_api_key}",
            "Content-Type": "application/json",
            "x-wait-for-model": "true"
        }

        try:
            prompt_budgets = [
                min(self.featherless_max_prompt_chars, 3000),
                1800,
                1000,
            ]
            response_text = ""

            for budget in prompt_budgets:
                compact_blocks_text = (
                    self.compact_blocks_for_prompt(blocks, max_chars=budget)
                    if blocks is not None
                    else str(blocks_text or "")[:budget]
                )
                prompt = self.build_mistral_prompt(compact_blocks_text, field_list=field_list)
                payload = {
                    "model": self.featherless_model,
                    "max_tokens": self.featherless_max_completion_tokens,
                    "temperature": 0.0,
                    "messages": [{
                        "role": "user",
                        "content": prompt
                    }]
                }

                # Add a small retry for 503 errors
                res = requests.post("https://api.featherless.ai/v1/chat/completions",
                                    headers=headers, json=payload, timeout=120)
                if res.status_code == 503:
                    logger.info("Featherless 503 (Loading) - waiting 5s and retrying...")
                    time.sleep(5)
                    res = requests.post("https://api.featherless.ai/v1/chat/completions",
                                        headers=headers, json=payload, timeout=120)

                response_text = res.text[:500]
                if res.ok:
                    return res.json()["choices"][0]["message"]["content"]

                if res.status_code == 400 and "maximum context length" in res.text and budget != prompt_budgets[-1]:
                    logger.warning(
                        "Featherless prompt exceeded context window at ~%s chars; retrying with a smaller OCR slice.",
                        budget,
                    )
                    continue

                res.raise_for_status()

        except Exception as e:
            logger.error(f"Mistral API error: {e}. Response: {response_text}")
            return None

    def internvl_extract(self, blocks_text):
        """
        Extract structured data using InternVL via Hugging Face API.
        Matches Colab logic (text-only inputs).
        """
        if not self.hf_api_key:
            logger.debug("InternVL extraction skipped: HF_API_KEY missing.")
            return None

        # Try the legacy URL first as in Colab
        url = "https://api-inference.huggingface.co/models/Qwen/Qwen2-7B-Instruct"
        headers = {
            "Authorization": f"Bearer {self.hf_api_key}",
            "x-wait-for-model": "true"
        }

        prompt = f"Extract structured form data from this OCR text as a flat JSON dictionary of field:value pairs. Return ONLY JSON.\n\n{blocks_text}"
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 2048,
                "temperature": 0.01,
                "return_full_text": False
            }
        }

        try:
            res = requests.post(url, headers=headers, json=payload, timeout=90)
            if res.status_code == 410:
                logger.info("Legacy HF URL 410 (Gone) - falling back to Router...")
                router_url = "https://router.huggingface.co/v1/chat/completions"
                router_payload = {
                    "model": "Qwen/Qwen2.5-7B-Instruct",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 2048,
                    "temperature": 0.0
                }
                res = requests.post(router_url, headers=headers, json=router_payload, timeout=150)
                res.raise_for_status()
                return res.json().get('choices', [{}])[0].get('message', {}).get('content', '')
            
            res.raise_for_status()
            data = res.json()
            if isinstance(data, list) and len(data) > 0 and "generated_text" in data[0]:
                return data[0]["generated_text"]
            return data
        except Exception as e:
            logger.error(f"InternVL API error: {e}")
            return None

    def ollama_extract(self, blocks_text, field_config=None):
        """
        Extract structured data using local Ollama API.
        """
        ollama_url = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
        model = os.environ.get("OLLAMA_EXTRACTION_MODEL", "glm-ocr:latest")
        
        field_list = None
        if field_config:
            field_list = ", ".join([f[0] for f in field_config])
            
        prompt = self.build_mistral_prompt(blocks_text, field_list=field_list)
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "options": {
                "temperature": 0.0,
                "num_predict": self.featherless_max_completion_tokens
            }
        }

        try:
            logger.info(f"Trying Ollama extraction with {model}...")
            res = requests.post(f"{ollama_url}/api/chat", json=payload, timeout=180)
            res.raise_for_status()
            return res.json().get("message", {}).get("content", "")
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            return None

    def safe_parse_llm_output(self, output):
        """
        Attempt to parse LLM output into a list of dictionaries.
        """
        def normalize_fields(items):
            if not isinstance(items, list):
                return []

            normalized = []
            for item in items:
                if not isinstance(item, dict):
                    continue
                
                # Case-insensitive key lookup
                keys = {k.lower(): v for k, v in item.items()}
                
                field_name = (
                    keys.get("field_name") or 
                    keys.get("field") or 
                    keys.get("name") or 
                    keys.get("label")
                )
                
                if not field_name:
                    continue
                
                value = (
                    keys.get("value") or 
                    keys.get("text") or 
                    keys.get("content") or 
                    ""
                )
                
                is_handwritten = keys.get("is_handwritten", False)
                confidence = keys.get("confidence", 0.5)
                
                normalized.append({
                    "field_name": str(field_name),
                    "value": str(value),
                    "is_handwritten": bool(is_handwritten),
                    "confidence": float(confidence or 0.5),
                })
            return normalized

        if output is None:
            return []

        if isinstance(output, list):
            return normalize_fields(output)

        if isinstance(output, dict):
            # If it's a flat dict, convert to list of field/value objects
            if not any(isinstance(v, (dict, list)) for v in output.values()):
                return normalize_fields([{"field": k, "value": v} for k, v in output.items()])
            
            # OpenAI-style response or HF generated_text
            if "choices" in output:
                return self.safe_parse_llm_output(output["choices"][0]["message"]["content"])
            if "generated_text" in output:
                return self.safe_parse_llm_output(output["generated_text"])
            
            return normalize_fields([output])

        if isinstance(output, str):
            # 1. Try standard JSON parse
            try:
                data = json.loads(output)
                if isinstance(data, (dict, list)):
                    return self.safe_parse_llm_output(data)
            except:
                pass

            # 2. Try fenced code blocks
            try:
                fenced_match = re.search(r"```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```", output, re.DOTALL)
                if fenced_match:
                    try:
                        data = json.loads(fenced_match.group(1))
                        if isinstance(data, (dict, list)):
                            return self.safe_parse_llm_output(data)
                    except:
                        pass
            except:
                pass

            # 3. Try finding first/last brackets
            try:
                match = re.search(r'(\{.*\}|\[.*\])', output, re.DOTALL)
                if match:
                    content = match.group(0)
                    try:
                        return normalize_fields(json.loads(content))
                    except:
                        # Fix obvious truncation
                        candidate = content.strip()
                        if candidate.count('{') > candidate.count('}'):
                            candidate += '}'
                        if candidate.count('[') > candidate.count(']'):
                            candidate += ']'
                        try:
                            return normalize_fields(json.loads(candidate))
                        except:
                            pass
            except:
                pass

            # 4. Final Final Last-Ditch Effort: Greedy Regex Scraper
            # This scans the raw string for anything that looks like "key": "value"
            try:
                extracted_dict = {}
                # Regex looks for: "key" : "value" OR "key" : value (unquoted)
                kv_pattern = r'"([^"]+)"\s*:\s*(?:"([^"]*)"|([^,\n\}]+))'
                matches = re.findall(kv_pattern, output)
                
                for key, val_quoted, val_unquoted in matches:
                    val = val_quoted if val_quoted else (val_unquoted or "").strip()
                    # Clean up common noise
                    if val.endswith(',') or val.endswith('}'):
                        val = val[:-1].strip()
                    extracted_dict[key] = val
                
                if extracted_dict:
                    return normalize_fields([{"field": k, "value": v} for k, v in extracted_dict.items()])
            except Exception as e:
                logger.error(f"Last-ditch regex parser failed: {e}")

            return []

        if isinstance(output, dict):
            # Handle OpenAI-style response or HF generated_text
            if "choices" in output:
                return self.safe_parse_llm_output(output["choices"][0]["message"]["content"])
            if "generated_text" in output:
                return self.safe_parse_llm_output(output["generated_text"])

        return []

    def merge_outputs(self, out1, out2):
        """
        Merge two sets of extracted fields. Matches Colab logic.
        """
        if not out1: return out2
        if not out2: return out1

        # Union Merge: Use a dict keyed by field name to avoid duplicates
        merged_dict = {}
        
        # Add all from out2 first (often more comprehensive)
        for f in out2:
            if isinstance(f, dict) and f.get("field_name"):
                merged_dict[f["field_name"].lower()] = f
        
        # Merge-in out1 (or average confidence if duplicate)
        for f in out1:
            if not isinstance(f, dict) or not f.get("field_name"):
                continue
            name = f["field_name"].lower()
            if name in merged_dict:
                # Average confidence
                merged_dict[name]["confidence"] = (merged_dict[name].get("confidence", 0.5) + f.get("confidence", 0.5)) / 2
            else:
                merged_dict[name] = f
                
        return list(merged_dict.values())

    def calibrate_confidence(self, fields):
        """
        Apply simple heuristics to calibrate field confidence scores.
        """
        safe_fields = []
        for f in fields:
            if not isinstance(f, dict): continue

            val = str(f.get("value", ""))
            conf = f.get("confidence", 0.5)

            if len(val.strip()) == 0:
                conf *= 0.5
            if any(c.isdigit() for c in val):
                conf += 0.05

            f["confidence"] = min(1.0, conf)
            safe_fields.append(f)
        return safe_fields

    def auto_rotate(self, image):
        """
        Pick best orientation using OCR on a small thumbnail for speed.
        Reduces auto-rotation cost significantly.
        """
        # Create thumbnail for orientation detection
        thumb = image.copy()
        thumb.thumbnail((512, 512))
        
        rotations = [
            (0, thumb),
            (90, thumb.rotate(90, expand=True)),
            (180, thumb.rotate(180, expand=True)),
            (270, thumb.rotate(270, expand=True))
        ]

        best_angle = 0
        best_score = 0

        for angle, img in rotations:
            blocks = self.extract_text_blocks(img)
            score = sum([b["confidence"] for b in blocks])
            if score > best_score:
                best_score = score
                best_angle = angle

        if best_angle == 0:
            return image
        
        logger.info(f"Rotating image by {best_angle} degrees based on thumbnail OCR.")
        return image.rotate(best_angle, expand=True)

    def process_document(self, img_source, rotate=True, field_config=None):
        """
        Full pipeline for a single document.
        """
        try:
            logger.info("Processing document...")
            raw_img = self.preprocess_image(img_source)
            
            image = self.auto_rotate(raw_img) if rotate else raw_img
            
            blocks = self.extract_text_blocks(image)
            blocks_text = self.format_blocks_for_prompt(blocks)
            
            # Try Together (Original Ensemble Logic)
            print(f"[DEBUG] OCR BLOCKS TEXT: {blocks_text[:200]}...")
            out1_raw = self.mistral_extract(image, blocks_text, blocks=blocks, field_config=field_config)
            print(f"[DEBUG] MISTRAL RAW: {out1_raw}")
            out1 = self.safe_parse_llm_output(out1_raw)
            if out1:
                logger.info("Mistral extraction successful.")
            else:
                logger.warning("Mistral extraction failed or returned empty.")
 
            out2_raw = self.internvl_extract(blocks_text) # InternVL prompt doesn't yet support focus
            print(f"[DEBUG] INTERNVL RAW: {out2_raw}")
            out2 = self.safe_parse_llm_output(out2_raw)
            if out2:
                logger.info("InternVL extraction successful.")
            else:
                logger.warning("InternVL extraction failed or returned empty.")
            # Combine Cloud LLMs
            merged = self.merge_outputs(out1, out2)
            
            # Final Fallback: Ollama
            if not merged:
                out3_raw = self.ollama_extract(blocks_text, field_config=field_config)
                print(f"[DEBUG] OLLAMA RAW: {out3_raw}")
                out3 = self.safe_parse_llm_output(out3_raw)
                merged = out3
                if merged:
                    logger.info("Ollama extraction successful.")
            
            # If both LLMs fail, we still have OCR blocks!
            if not merged and blocks:
                logger.info("Both LLMs failed. Falling back to OCR blocks.")
            
            final_fields = self.calibrate_confidence(merged if isinstance(merged, list) else [])
            
            return {
                "success": True, 
                "fields": final_fields,
                "blocks": blocks,
                "metadata": {
                    "rotated": rotate,
                    "mistral_success": bool(out1_raw),
                    "internvl_success": bool(out2_raw)
                }
            }
        except Exception as e:
            logger.exception(f"Document processing failed: {e}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def mask_sensitive_data(fields):
        """
        Mask Aadhaar and PAN numbers in a list of field dictionaries.
        """
        for f in fields:
            val = str(f.get("value", ""))
            k = str(f.get("field_name", "")).lower()
            
            if "aadhaar" in k:
                f["value"] = "XXXX XXXX " + val[-4:] if len(val) >= 4 else val
            elif "pan" in k:
                f["value"] = val[:2] + "XXXXX" + val[-2:] if len(val) >= 4 else val
        return fields

# Helper for CLI/Lab usage
def display_table(fields):
    """Utility to display results in a table for terminal/notebook usage."""
    if pd is None:
        print("Pandas not installed. Printing fields directly:")
        for f in fields:
            print(f"- {f.get('field_name', '')}: {f.get('value', '')} ({f.get('confidence', 0)})")
        return

    rows = []
    for f in fields:
        rows.append([
            f.get("field_name", ""),
            f.get("value", ""),
            "handwritten" if f.get("is_handwritten") else "printed",
            round(f.get("confidence", 0), 2)
        ])
    df = pd.DataFrame(rows, columns=["Field", "Value", "Type", "Confidence"])
    print(df.to_string())

if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    
    PAN_FIELDS = [("surname", ""), ("first_name", ""), ("dob", ""), ("pan_number", ""), ("father_name", "")]
    
    if len(sys.argv) < 2:
        print("Usage: python papertrail_protectv3.py <image_path>")
    else:
        protector = PaperTrailProtectV3()
        # Guided extraction test for PAN
        result = protector.process_document(sys.argv[1], field_config=PAN_FIELDS)
        
        if result["success"]:
            print("\n📊 Extracted Data (Guided Mode):")
            display_table(result["fields"])
        else:
            print(f"❌ Error: {result['error']}")
