from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Boolean,Sequence
from sqlalchemy.ext.declarative import declarative_base

app = FastAPI()

# Configure a conexão com o banco de dados PostgreSQL
DATABASE_URL = "postgresql://postgres:neves@127.0.0.1:5432/FastAPI"
engine = create_engine(DATABASE_URL)

# Crie uma sessão do SQLAlchemy para interagir com o banco de dados
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Task(BaseModel):
    title: str
    description: str
    done: bool = False

    class Config:
        orm_mode = True

class DBTask(Base):
    __tablename__ = "tasks"

    id = Column(Integer, Sequence('task_id_seq'),  primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    done = Column(Boolean)

Base.metadata.create_all(bind=engine)

#class TaskList:
    #def __init__(self):
    #    self.tasks = []

#    def add_task(self, task: Task):
#        self.tasks.append(task)
##

#    def list_tasks(self):
#        return self.tasks

#    def get_task(self, task_index: int):
#        if 0 <= task_index < len(self.tasks):
#            return self.tasks[task_index]
#        return None

#task_list = TaskList()

@app.post("/tasks/", response_model=Task)
def create_task(task: Task):
    try:
        # Crie uma instância da sessão
        db = SessionLocal()
        
        # Crie uma tarefa no banco de dados
        db_task = DBTask(**task.dict())
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        db.close()

        return task
    except Exception as e:
        raise HTTPException(status_code=409, detail="Erro ao criar a tarefa")


@app.get("/tasks/", response_model=list[Task])
#def read_tasks():
    #return task_list.list_tasks()
def read_tasks(skip: int = 0, limit: int = 10):
    db = SessionLocal()
    tasks = db.query(DBTask).offset(skip).limit(limit).all()
    db.close()
    return tasks
    


@app.get("/tasks/{task_index}", response_model=Task)
def read_task(task_index: int):
    '''    task = task_list.get_task(task_index)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task'''
    
    db = SessionLocal()
    task = db.query(DBTask).filter(DBTask.id == task_index).first()
    db.close()
    if task is None:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    return task

@app.put("/tasks/{task_index}", response_model=Task)
def update_task(task_index: int, task: Task):
    '''existing_task = task_list.get_task(task_index)
    if existing_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    task_list.tasks[task_index] = task
    return task'''
    db = SessionLocal()
    db_task = db.query(DBTask).filter(DBTask.id == task_index).first()
    if db_task is None:
        db.close()
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")

    for key, value in task.dict().items():
        setattr(db_task, key, value)

    db.commit()
    db.refresh(db_task)
    db.close()
    return task

@app.delete("/tasks/{task_index}", response_model=Task)
def delete_task(task_index: int):
    '''task = task_list.get_task(task_index)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    del task_list.tasks[task_index]
    return task'''
    db = SessionLocal()
    db_task = db.query(DBTask).filter(DBTask.id == task_index).first()
    if db_task is None:
        db.close()
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")

    db.delete(db_task)
    db.commit()
    db.close()
    return db_task

