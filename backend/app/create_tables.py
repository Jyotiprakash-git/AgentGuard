
from app.database import Base, engine
from app import models

def create_tables():
    print("Creating AgentGuard database tables...")

    Base.metadata.create_all(bind=engine)

    print("All AgentGuard tables created successfully!")

if __name__ == "__main__":
    create_tables()
