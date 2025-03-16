from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import relationship, declarative_base, sessionmaker
from sqlalchemy.orm import sessionmaker


# PostgreSQL-Datenbank-URL (Docker-Compose nutzt "database" als Hostname)
DATABASE_URL = "postgresql://myuser:mypassword@database:5432/mydatabase"

# SQLAlchemy Setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# 🔹 Adressen-Tabelle
class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)
    street = Column(String, nullable=False)
    house_number = Column(String, nullable=False)
    city = Column(String, nullable=False)
    country = Column(String, nullable=False)

    # Beziehung zu Poems
    poem_id = Column(Integer, ForeignKey("poems.id"), nullable=True)
    poem = relationship("Poem")

# 🔹 Gedicht-Tabelle (Pro Stadt nur 1 Gedicht)
class Poem(Base):
    __tablename__ = "poems"

    id = Column(Integer, primary_key=True, index=True)
    city = Column(String, unique=True, nullable=False)  # 🔥 Einmal pro Stadt
    text = Column(String, nullable=False)  # Das generierte Gedicht

# Tabellen erstellen (falls nicht vorhanden)
def init_db():
    Base.metadata.create_all(bind=engine)
