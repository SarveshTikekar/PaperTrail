import os
import time
import logging
from papertrail_protectv3 import PaperTrailProtectV3, display_table

# Configure logging to hide noisy debugs during benchmark
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("benchmark")
logger.setLevel(logging.INFO)

def run_benchmark():
    samples = [
        "../media/forms/originals/sample249A.jpeg",
        "../media/forms/originals/form49A.jpeg",
        "../media/forms/originals/form_sample_3.jpeg"
    ]
    
    # Generic PAN field list for testing Guided Extraction
    PAN_FIELDS = [
        ("surname", "Surname"),
        ("first_name", "First Name"),
        ("middle_name", "Middle Name"),
        ("dob", "Date of Birth"),
        ("pan_number", "PAN Number"),
        ("father_last", "Father Surname"),
        ("father_first", "Father First Name"),
        ("aadhaar_number", "Aadhaar Number")
    ]
    
    protector = PaperTrailProtectV3()
    
    print("\n🚀 Starting PaperTrail V3 Benchmark\n" + "="*40)
    
    for sample in samples:
        if not os.path.exists(sample):
            logger.error(f"Sample not found: {sample}")
            continue
            
        print(f"\n📄 Processing: {sample}")
        start_time = time.time()
        
        # Run with guided extraction
        result = protector.process_document(sample, field_config=PAN_FIELDS)
        
        duration = time.time() - start_time
        
        if result["success"]:
            fields = result["fields"]
            filled = [f for f in fields if f.get("value") and len(str(f["value"]).strip()) > 0]
            avg_conf = sum([f.get("confidence", 0) for f in fields]) / len(fields) if fields else 0
            
            print(f"✅ Success | Time: {duration:.2f}s | Fields Found: {len(filled)}/{len(PAN_FIELDS)} | Avg Conf: {avg_conf:.2f}")
            display_table(fields)
        else:
            print(f"❌ Error: {result['error']}")
            
    print("\n" + "="*40 + "\nBenchmark Complete.")

if __name__ == "__main__":
    run_benchmark()
