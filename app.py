from fastapi import FastAPI , HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel , Field , computed_field 
from typing import Annotated , Literal , Optional 
import pickle 
import pandas as pd  

## Model Imported 

with open('model.pkl' , 'rb') as f:
    model = pickle.load(f)

# Configure the OneHotEncoder to ignore unknown categories to prevent crashes on unseen inputs
try:
    model.named_steps['preprocessor'].named_transformers_['cat'].handle_unknown = 'ignore'
except Exception as e:
    pass

## Fast Api 
app = FastAPI()

## City tier lists (from training notebook)
tier_1_cities = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Hyderabad", "Pune"]
tier_2_cities = [
    "Jaipur", "Chandigarh", "Indore", "Lucknow", "Patna", "Ranchi", "Visakhapatnam", "Coimbatore",
    "Bhopal", "Nagpur", "Vadodara", "Surat", "Rajkot", "Jodhpur", "Raipur", "Amritsar", "Varanasi",
    "Agra", "Dehradun", "Mysore", "Jabalpur", "Guwahati", "Thiruvananthapuram", "Ludhiana", "Nashik",
    "Allahabad", "Udaipur", "Aurangabad", "Hubli", "Belgaum", "Salem", "Vijayawada", "Tiruchirappalli",
    "Bhavnagar", "Gwalior", "Dhanbad", "Bareilly", "Aligarh", "Gaya", "Kozhikode", "Warangal",
    "Kolhapur", "Bilaspur", "Jalandhar", "Noida", "Guntur", "Asansol", "Siliguri", "Kota"
]

class Userinput(BaseModel):

    age : Annotated[int, Field (..., gt =0 , lt = 120 , description= "Enter The Age of User ")]
    weight : Annotated[float , Field(..., gt=50  , lt =600 ,description="Weight Please ")]
    height: Annotated[float , Field(..., description="Height Please ")]
    income_lpa : Annotated[float , Field(..., description="Income Please ")]
    smoker: Annotated[bool , Field(..., description="Smoker Please ")]
    city : Annotated[str , Field(..., description="City Please ")]
    occupation : Annotated[Literal["Engineer", "Doctor", "Lawyer", "Teacher", "Pilot", "Architect", "Banker", "Developer", "Chef", "Writer", "Artist", "Musician", "Actor", "Dancer", "Photographer", "Designer", "Marketing", "Sales", "HR", "Finance", "Consultant", "Entrepreneur", "Student", "Unemployed", "Other", "retired", "freelancer", "student", "government_job", "business_owner", "unemployed", "private_job"] , Field(..., description="Occupation Please ")]  

    @computed_field
    @property
    def bmi(self)-> float :
        return round(self.weight / (self.height**2), 2)

    @computed_field
    @property
    def age_group(self) -> str:
        if self.age < 25:
            return "young"
        elif self.age < 45:
            return "adult"
        elif self.age < 60:
            return "middle_aged"
        return "senior"

    @computed_field
    @property
    def lifestyle_risk(self) -> str:
        if self.smoker and self.bmi > 30:
            return "high"
        elif self.smoker or self.bmi > 27:
            return "medium"
        else:
            return "low"

    @computed_field
    @property
    def city_tier(self) -> int:
        if self.city in tier_1_cities:
            return 1
        elif self.city in tier_2_cities:
            return 2
        else:
            return 3

@app.post('/predict')
def predict(Data : Userinput):

    input_datadf = pd.DataFrame([{
        'bmi' : Data.bmi,
        'age_group' : Data.age_group,
        'lifestyle_risk' : Data.lifestyle_risk,
        'city_tier' : Data.city_tier,
        'income_lpa' : Data.income_lpa,
        'occupation' : Data.occupation,
    }])

    prediction = model.predict(input_datadf)[0]
    
    return JSONResponse(status_code = 200, content = { "prediction" : prediction })  