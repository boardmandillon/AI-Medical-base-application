from app.models.project_base import ProjectBase
from app import db_mongo as db


class AAPDiagnosisModel(ProjectBase):
    """Document definition for AAP diagnosis."""
    possible_labels = {
        "Appendicitis": 1,
        "Diverticular Disease": 2,
        "Perforated Ulcer": 3,
        "Non Specific Abdominal Pain": 4,
        "Cholecystitis": 5,
        "Bowel Obstruction": 6,
        "Pancreatitis": 7,
        "Renal Colic": 8,
        "Dyspepsia": 9,
    }

    sight_of_pain_labels = [
        "Right Upper Quadrant", "Left Upper Quadrant",
        "Right Lower Quadrant", "Left Lower Quadrant",
        "Upper Half", "Lower Half", "Right Side", "Left Side",
        "Central", "General", "Right Loin", "Left Loin", "No Pain",
    ]

    ml_sex = db.StringField(required=True, choices=["Male", "Female"])
    ml_age = db.StringField(required=True, choices=[
        "<10", "10s", "20s", "30s", "40s", "50s", "60s", "70+"])
    ml_site_of_pain_at_onset = db.StringField(choices=sight_of_pain_labels)
    ml_site_of_pain_at_present = db.StringField(
        required=True, choices=sight_of_pain_labels)
    ml_aggravating_factors = db.ListField(db.StringField(choices=[
        "Movement", "Coughing", "Respiration", "Food", "Other", "None"]))
    ml_relieving_factors = db.ListField(db.StringField(choices=[
        "Lying Still", "Vomiting", "Antacids", "Food", "Other", "None"]))
    ml_progress = db.StringField(choices=["Better", "Same", "Worse"])
    ml_duration = db.StringField(choices=[
        "<12 hours", "12-23 hours", "24-48 hours", "2-7 days"])
    ml_type = db.StringField(choices=["Intermittent", "Steady", "Colicky"])
    ml_severity = db.StringField(choices=["Moderate", "Severe"])
    ml_nausea = db.BooleanField()
    ml_vomiting = db.BooleanField()
    ml_anorexia = db.BooleanField()
    ml_previous_indigestion = db.BooleanField()
    ml_jaundice = db.BooleanField()
    ml_bowels = db.ListField(db.StringField(choices=[
        "Normal", "Constipation", "Diarrhoea", "Blood", "Mucus"]))
    ml_micturition = db.ListField(db.StringField(choices=[
        "Normal", "Frequency", "Dysuria", "Dark", "Haematuria"]))
    ml_previous_similar_pain = db.BooleanField()
    ml_previous_abdo_surgery = db.BooleanField()
    ml_drugs_for_abdo_pain = db.BooleanField()
    ml_mood = db.StringField(choices=["Normal", "Distressed", "Anxious"])
    ml_colour = db.ListField(db.StringField(choices=[
        "Normal", "Pale", "Flushed", "Jaundiced", "Cyanosed"]))
    ml_abdo_movement = db.StringField(choices=[
        "Normal", "Poor", "Peristalsis"])
    ml_scar = db.BooleanField()
    ml_distension = db.BooleanField()
    ml_site_of_tenderness = db.StringField(choices=sight_of_pain_labels)
    ml_rebound = db.BooleanField()
    ml_guarding = db.BooleanField()
    ml_rigidity = db.BooleanField()
    ml_mass = db.BooleanField()
    ml_murphy = db.BooleanField()
    ml_bowel = db.StringField(choices=["Normal", "Decreased", "Hyper"])
    ml_rectal_tenderness = db.ListField(db.StringField(choices=[
        "Left", "Right", "General", "Mass", "None"]))

    t_diagnosis = db.StringField(choices=possible_labels.keys(), null=True)
    l_actual_diagnosis = db.StringField(
        choices=possible_labels.keys(), null=True)


class AAPGynDiagnosisModel(AAPDiagnosisModel):
    """Document definition for AAP diagnosis with additional gynae fields."""
    possible_labels = {
        "Appendicitis": 1,
        "Non Specific Abdominal Pain": 2,
        "Urinary Tract Infection": 3,
        "Pelvic Inflammatory Disease": 4,
        "Ovarian Cyst": 5,
        "Ectopic Pregnancy": 6,
        "Incomplete Abortion": 7,
    }

    ml_periods = db.StringField(choices=[
        "Not Started", "Ceased", "Regular", "Irregular"])
    ml_last_monthly_period = db.StringField(choices=["Normal", "Late/Overdue"])
    ml_vaginal_discharge = db.BooleanField()
    ml_pregnancy = db.StringField(choices=[
        "Impossible", "Possible", "Confirmed"])
    ml_faint = db.BooleanField()
    ml_previous_history_of_salpingitis_or_std = db.BooleanField()
    ml_vaginal_tenderness = db.ListField(db.StringField(choices=[
        "Normal", "Right", "Left", "Cervix", "General", "Mass",
        "Blood(clots)"]))

    t_diagnosis = db.StringField(choices=possible_labels.keys(), null=True)
    l_actual_diagnosis = db.StringField(
        choices=possible_labels.keys(), null=True)
