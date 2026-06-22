from fastapi import FastAPI , HTTPException
from fastapi.responses import JSONResponse
from schema.user_input import Userinput

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