from django.db import models

class BaseForm(models.Model):
    original_image = models.ImageField(upload_to='forms/originals/')
    processed_image = models.ImageField(upload_to='forms/processed/', null=True, blank=True)
    status = models.CharField(
        max_length=20, 
        choices=[('pending', 'Pending'), ('verified', 'Verified'), ('flagged', 'Flagged')],
        default='pending'
    )
    confidence_data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class PANForm49A(BaseForm):
    # 0. Title
    title = models.CharField(max_length=10, blank=True)

    # 1. Full Name
    full_name_last = models.CharField(max_length=100, blank=True)
    full_name_first = models.CharField(max_length=100, blank=True)
    full_name_middle = models.CharField(max_length=100, blank=True)
    
    # 2. Abbreviations
    name_on_card = models.CharField(max_length=200, blank=True)
    
    # 3. Other Names
    has_other_name = models.BooleanField(default=False)
    other_name_title = models.CharField(max_length=10, blank=True)
    other_name_last = models.CharField(max_length=100, blank=True)
    other_name_first = models.CharField(max_length=100, blank=True)
    other_name_middle = models.CharField(max_length=100, blank=True)
    
    # 4. Gender
    gender = models.CharField(max_length=20, blank=True) # Male, Female, Transgender
    
    # 5. Date of Birth
    dob = models.DateField(null=True, blank=True)
    
    # 6. Details of Parents
    father_last = models.CharField(max_length=100, blank=True)
    father_first = models.CharField(max_length=100, blank=True)
    father_middle = models.CharField(max_length=100, blank=True)
    
    mother_last = models.CharField(max_length=100, blank=True)
    mother_first = models.CharField(max_length=100, blank=True)
    mother_middle = models.CharField(max_length=100, blank=True)
    single_parent_mother_only = models.BooleanField(default=False)
    
    parent_to_print = models.CharField(max_length=20, blank=True) # Father's Name / Mother's Name
    
    # 7. Address - Residence
    res_flat = models.CharField(max_length=255, blank=True)
    res_premises = models.CharField(max_length=255, blank=True)
    res_road = models.CharField(max_length=255, blank=True)
    res_area = models.CharField(max_length=255, blank=True)
    res_city = models.CharField(max_length=100, blank=True)
    res_state = models.CharField(max_length=100, blank=True)
    res_pincode = models.CharField(max_length=20, blank=True)
    res_country = models.CharField(max_length=100, blank=True)

    # 7. Address - Office
    off_name = models.CharField(max_length=255, blank=True)
    off_flat = models.CharField(max_length=255, blank=True)
    off_premises = models.CharField(max_length=255, blank=True)
    off_road = models.CharField(max_length=255, blank=True)
    off_area = models.CharField(max_length=255, blank=True)
    off_city = models.CharField(max_length=100, blank=True)
    off_state = models.CharField(max_length=100, blank=True)
    off_pincode = models.CharField(max_length=20, blank=True)
    off_country = models.CharField(max_length=100, blank=True)
    
    # 8. Address for Communication
    comm_address = models.CharField(max_length=20, blank=True) # Residence / Office
    
    # 9. Phone & Email (ISD + STD + Number)
    phone_country_code = models.CharField(max_length=5, blank=True)
    phone_std_code = models.CharField(max_length=10, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    email_id = models.EmailField(blank=True, null=True)
    
    # 10. Status of Applicant
    applicant_status = models.CharField(max_length=100, blank=True)

    # 11. AO code
    ao_code_area = models.CharField(max_length=10, blank=True)
    ao_code_type = models.CharField(max_length=5, blank=True)
    ao_code_range = models.CharField(max_length=10, blank=True)
    ao_code_number = models.CharField(max_length=10, blank=True)
    
    # 12. Aadhaar
    aadhaar_number = models.CharField(max_length=20, blank=True)
    aadhaar_name = models.CharField(max_length=255, blank=True)
    
    # 13. Source of Income
    source_of_income = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"PAN 49A - {self.name_on_card or self.id}"

class VoterIDForm6(BaseForm):
    # 1. Constituency details
    assembly_constituency = models.CharField(max_length=150, blank=True)
    district = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)

    # 2. Name of Applicant
    name_english = models.CharField(max_length=255, blank=True)
    name_hindi = models.CharField(max_length=255, blank=True)
    surname_english = models.CharField(max_length=255, blank=True)
    surname_hindi = models.CharField(max_length=255, blank=True)
    
    # 3. Relative
    relative_name_english = models.CharField(max_length=255, blank=True)
    relative_name_hindi = models.CharField(max_length=255, blank=True)
    relative_surname_english = models.CharField(max_length=255, blank=True)
    relative_surname_hindi = models.CharField(max_length=255, blank=True)
    relation_type = models.CharField(max_length=50, blank=True) # Father/Mother/Husband/Wife/Other
    
    # 4. Contact
    mobile_number = models.CharField(max_length=20, blank=True)
    email_id = models.EmailField(blank=True, null=True)
    
    # 5. Aadhaar
    aadhaar_number = models.CharField(max_length=20, blank=True)
    
    # 6. Gender
    gender = models.CharField(max_length=20, blank=True)
    
    # 7. DOB
    dob = models.DateField(null=True, blank=True)
    place_of_birth_town = models.CharField(max_length=100, blank=True)
    place_of_birth_state = models.CharField(max_length=100, blank=True)
    place_of_birth_district = models.CharField(max_length=100, blank=True)
    
    # 8. Address
    house_no = models.CharField(max_length=100, blank=True)
    street_area = models.CharField(max_length=255, blank=True)
    town_village = models.CharField(max_length=100, blank=True)
    post_office = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=20, blank=True)
    tehsil = models.CharField(max_length=100, blank=True)
    
    # 9. Disability (optional section)
    disability_type = models.CharField(max_length=50, blank=True)  # locomotor, visual, hearing, speech, intellectual, none
    disability_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    # 10. Family/neighbor EPIC for verification
    family_epic_number = models.CharField(max_length=20, blank=True)
    residence_since = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"Voter ID Form 6 - {self.name_english or self.id}"
