from typing import Optional
from fastapi import FastAPI , Path , HTTPException , Query 
import json 
from fastapi.responses import JSONResponse
from pydantic import BaseModel , Field 
from typing import Annotated ,Literal , Optional

class User(BaseModel):
    id : Annotated[str , Field(..., description = 'The id number ')]
    name :Annotated[str, Field(..., description = 'The name of patient ')]
    email: Annotated[str, Field(..., description = 'The email ')]
    age : Annotated[int, Field(..., description = 'The age ')]
    role :Annotated[Literal["Admin", "User"], Field(..., description = 'The Role ')]



class UserUpdate(BaseModel):
    id : Annotated[Optional[str] , Field(default=None)]
    name :Annotated[Optional[str], Field(default=None)]
    email: Annotated[Optional[str], Field(default=None)]
    age : Annotated[Optional[int], Field(default=None)]
    role :Annotated[Optional[Literal["Admin", "User"] ], Field(default=None)]





app = FastAPI()


def load_data():
    with open('users.json', 'r') as f:
        data = json.load(f)
    return data

def save_data(data):
    with open('users.json' ,'w') as f:
        json.dump(data, f)      






@app.put('/edit/{user_id}')
def user_update(user_id : str , user_update : UserUpdate ):
    data = load_data()
    user_found = False
    
    for item in data:
        if user_id in item:
            user_found = True
            exist_user_id = item[user_id]
            updated_user_id = user_update.model_dump(exclude_unset=True)

            for key , value in updated_user_id.items():
                exist_user_id[key] = value
            
            break
            
    if not user_found:
        raise HTTPException( status_code = 404 , detail = "No User id found")
        
    save_data(data)
    return JSONResponse(status_code= 200 , content = {"message" : "Updated"})
        



@app.get("/views")
def views():

    data = load_data()
    return data


@app.get("/")
def hello():
    return {'message' : 'Pateint managemnet Syatem Api '}


@app.get("/about")
def about():
    return {
        "message" : "This is a pateint management system api",
        "version" : "1.0.0",
        "author" : "Ali Sachal",
        "" : ""
    }

@app.get('/user/{user_id}')
def user_data(user_id : str = Path(..., description = "The id number in the text file ") ,):
    data = load_data()

    for item in data:
        if user_id in item:
            return item[user_id]
    raise HTTPException( status_code = 404 , detail = "user Not found")

@app.get('/sort')
def sort(sort_by : str = Query (..., description ="Enter name or age"), order : str =Query("ase" ) ):

    valid_field = ['name', 'email']

    if sort_by not in valid_field:
        raise HTTPException(status_code = 400 , detail="Not  a ccorrret field {valid_field}") 

    if order not in ['asc' , 'dsc']:
        raise HTTPException( status_code = 400 )

    data = load_data() 

    sort_order = True if order == "desc" else False
    sorted_data = sorted(data.values(), key=lambda user : user [sort_by] , reverse = (order == 'asc'))
    return sorted_data

@app.post('/create')
def Crete_user(user: User ):
  # Load Data
    data = load_data()
  # Check data Vaidation   
    for item in data:
        if user.id in item:
            raise HTTPException(status_code = 400 , detail = "Id Already Exists ")
    # Add data 
    new_user = {user.id: user.model_dump(exclude=['id'])}
    data.append(new_user)

    save_data(data)

    return JSONResponse(status_code = 201, content = { "message": "Data Saev Successfully"})




