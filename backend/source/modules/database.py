from datetime import datetime

from sqlalchemy import create_engine, Column, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class HumanDetectorDatabase:
    def __init__(self, database_url):
        self.engine = create_engine(database_url)
        self.Session = sessionmaker(bind = self.engine)
                
    def create_tables(self):
        Base.metadata.create_all(self.engine)

    def drop_tables(self):
        Base.metadata.drop_all(self.engine)

    def add_record(self, record):
        with self.Session() as session:
            session.add(record)
            session.commit()

    def get_record_by_id(self, model, record_id):
        with self.Session() as session:
            return session.query(model).get(record_id)

    def get_all_records(self, model):
        with self.Session() as session:
            return session.query(model).all()

    def get_records_from_predictions(
        self,
        query_id: int | None,
        time_min, time_max,
        num_humans_min, num_humans_max,
        page_size, page_index
    ):
        with self.Session() as session:
            query = session.query(Predictions)
            
            if query_id is not None and query_id != "":
                query = query.filter(Predictions.query_id == query_id)
            
            if time_min is not None and time_min != "":
                query = query.filter(Predictions.time >= datetime.strptime(time_min, "%Y-%m-%d_%H-%M-%S"))
            
            if time_max is not None and time_max != "":
                query = query.filter(Predictions.time <= datetime.strptime(time_max, "%Y-%m-%d_%H-%M-%S"))
            
            if num_humans_min is not None and num_humans_min != "":
                query = query.filter(Predictions.num_humans >= int(num_humans_min))
                
            if num_humans_max is not None and num_humans_max != "":
                query = query.filter(Predictions.num_humans <= int(num_humans_max))
                
            total = query.count()
            
            records = query.limit(page_size).offset(page_size * (page_index - 1)).all()
        
        return records, total
    
    def update_record(self, model, record_id, **kwargs):
        with self.Session() as session:
            record = session.query(model).get(record_id)
            if record:
                for key, value in kwargs.items():
                    setattr(record, key, value)
                session.commit()

    def delete_record(self, model, record_id):
        with self.Session() as session:
            record = session.query(model).get(record_id)
            if record:
                session.delete(record)
                session.commit()
        
class Predictions(Base):
    __tablename__ = 'predictions'

    query_id = Column(Integer, primary_key = True)
    time = Column(DateTime)
    
    query_image_file = Column(String(64))
    result_image_file = Column(String(64))
    num_humans = Column(Integer)
    