from fastapi import FastAPI , HTTPException ,Path ,Query
import json
from fastapi.responses import JSONResponse
from pydantic import BaseModel,Field,computed_field
from typing import Annotated,Optional,Literal
app = FastAPI()

class PATIENT(BaseModel):
    id :Annotated[str,Field(...,description="id of the patient ",examples=['P001'])]
    name: Annotated[str, Field(... ,description='name of the patient')]
    age: int
    gender: Annotated[Literal['Male','Female','Other'],Field(...,description='Gender of the patient')]
    height : float
    weight : float
    phone: str
    city:Annotated[str,Field(...,description='city of where is the patient living')]
   

    @computed_field
    @property
    def bmi(self)-> float:
        
        bmi = round(self.weight / ((self.height / 100) ** 2), 2)

        return bmi


class PATIENTUPDATE(BaseModel):
    name: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[int], Field(default=None, gt=0)]
    gender: Annotated[Optional[Literal['male', 'female']], Field(default=None)]
    height: Annotated[Optional[float], Field(default=None, gt=0)]
    weight: Annotated[Optional[float], Field(default=None, gt=0)]
    phone: Annotated[Optional[str], Field(default=None)]
    city: Annotated[Optional[str], Field(default=None)]
    


def load_data():
    with open("patient.json", "r") as f:
       data = json.load(f)
    return data

def save_data(data):
    with open('patient.json','w') as f:
        json.dump(data,f)


@app.get("/")
def home():
    return {"message": "a patient managment system"}


@app.get("/patient/{patient_id}")
def view_patient(patient_id : str = Path(...,description="id of the patient",example = ["P001"])):
    
    data = load_data()

    if patient_id in data:
        return data[patient_id]
    
    raise HTTPException(
        status_code=404,
        detail="Invalid patient ID")

@app.get("/sorted")
def sort_patient(sort_by : str = Query(...,description=("sort on the basic of age,admission_date,height,weight")),
                  order : str = Query("asc",description='sort in asc order')):
    
    valid_fields = ['age', 'height', 'weight', 'bmi']
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400,
                            detail=f'invalid fields select form{valid_fields}')
    data = load_data()

    sort_order = False if order == 'asc' else True

    # sorted_data = sorted(data.values(),key=lambda x :x.get(sort_by,0),reverse=sort_order)
    sorted_data = sorted(data.values(),key=lambda x: int(x.get(sort_by, 0))if sort_by == "age" else x.get(sort_by, ""), reverse=sort_order)
    
    return sorted_data


@app.post("/create")
def create_patient(patient:PATIENT):

    data = load_data()

    if patient.id in data:
        raise HTTPException(status_code=400,detail="patient already exist")
    
# new patiet add
    data[patient.id] = patient.model_dump(exclude={'id'})

# save datra
    
    save_data(data)

    return JSONResponse(status_code=201,content='patient created sussfully')


@app.put("/edit:{patient_id}")
def update_patient(patient_id:str,patient_update:PATIENTUPDATE):

    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail='Patient not found')
    
    existing_patient_info = data[patient_id]

    updated_patient_info = patient_update.model_dump(exclude_unset=True)

    for key, value in updated_patient_info.items():
        existing_patient_info[key] = value

    #existing_patient_info -> pydantic object -> updated bmi + verdict
    existing_patient_info['id'] = patient_id
    patient_pydandic_obj = PATIENT(**existing_patient_info)
    #-> pydantic object -> dict
    existing_patient_info = patient_pydandic_obj.model_dump(exclude={'id'})

    # add this dict to data
    data[patient_id] = existing_patient_info

    # save data
    save_data(data)

    return JSONResponse(status_code=200, content={'message':'patient updated'})

@app.delete('/delete/{patient_id}')
def delete_patient(patient_id: str):

    # load data
    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail='Patient not found')
    
    del data[patient_id]

    save_data(data)

    return JSONResponse(status_code=200, content={'message':'patient deleted'})


