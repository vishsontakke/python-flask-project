import json
from sqlalchemy import (
    Column, Boolean, Integer,
    String, select, DateTime,
    Enum, Text, JSON, ForeignKey
)
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base, relationship, mapped_column
from flask_login import UserMixin
# from .database import Base
from datetime import datetime
from custome_enum import users_enum
from core.database import db_session

Base = declarative_base()

class User(Base, UserMixin):
    __tablename__ = 'users'

    id          = Column(Integer, primary_key=True)
    first_name  = Column(String(200), nullable=True)
    middle_name = Column(String(200), nullable=True)
    last_name   = Column(String(200), nullable=True)
    email       = Column(String(200), nullable=False, unique=True)
    password    = Column(String(200), nullable=False)
    role        = Column(Integer, nullable=False)
    created_at  = Column(DateTime(), default=datetime.now())
    updated_at  = Column(DateTime(), onupdate=datetime.now())
    
    def __init__(self, first_name=None, middle_name=None, last_name=None, role=None, email=None, password=None):
        self.first_name     = first_name
        self.middle_name    = middle_name
        self.last_name      = last_name
        self.role           = role
        self.email          = email
        self.password       = password

    def __repr__(self):
        return f'<User: {self.first_name!r} {self.last_name!r} ({self.role!r})>'

    @property
    def isAdmin(self):
        return self.role == users_enum.ROLE_ADMIN
    
    @property
    def fullName(self):
        return f"{self.first_name} {self.last_name}"



class Subject(Base):
    __tablename__ = 'subjects'

    id          = Column(Integer, primary_key=True)
    name        = Column(String(200), nullable=False, unique=True)
    logo        = Column(String(200), nullable=True)
    status      = Column(Boolean(), default=True)
    questions   = relationship("Question")
    created_at  = Column(DateTime(), default=datetime.now())
    updated_at  = Column(DateTime(), onupdate=datetime.now())

    def __init__(self, name=None, logo=None):
        self.name = name
        self.logo = logo

    def __repr__(self):
        return f'<Subject: {self.name}>'


class Question(Base):
    __tablename__ = 'questions'

    id          = Column(Integer, primary_key=True)
    # subject_id  = Column(Integer, ForeignKey(Subject.id), nullable=False)
    subject_id  = Column(ForeignKey("subjects.id"), nullable=False)
    level       = Column(Integer, nullable=False)
    question    = Column(Text, nullable=False)
    # options     = relationship("QuestionOption")
    marks       = Column(Integer, nullable=False)
    status      = Column(Integer, nullable=False)
    created_at  = Column(DateTime(), default=datetime.now())
    updated_at  = Column(DateTime(), onupdate=datetime.now())


    def __init__(self, question=question, subject_id=subject_id, level=level, marks=marks, status=status):
        self.subject_id = subject_id
        self.question   = question
        self.level      = level
        self.marks      = marks
        self.status     = status

    def options(self):
        all_options = db_session.query(QuestionOption).filter_by(question_id=self.id).all()
        if(all_options):
            options = []
            for i in all_options:
                options.append({
                    'id': i.id,
                    'value': i.option,
                    'is_correct': i.is_correct
                })
            return options
        else:
            return False
    
    def getSubject(self):
        subjectModel = db_session.query(Subject).filter_by(id=self.subject_id).first()
        if(subjectModel):
            response = {
                'id'    : subjectModel.id,
                'name'  : subjectModel.name,
                'logo'  : subjectModel.logo,
                'status': subjectModel.status
            }

            return response
        
        return False


    def __repr__(self):
        return f'<Question: level->{self.level} | subject->{self.subject_id}>'


class QuestionOption(Base):
    __tablename__ = 'question_options'

    id          = Column(Integer, primary_key=True)
    question_id = Column(ForeignKey("questions.id"), nullable=False)
    option      = Column(Text, nullable=True)
    is_correct  = Column(Boolean)
    created_at  = Column(DateTime(), default=datetime.now())
    updated_at  = Column(DateTime(), onupdate=datetime.now())


    def __init__(self, question_id=question_id, option=option, is_correct=False):
        self.question_id = question_id
        self.option = option
        self.is_correct = is_correct


class Test(Base):
    __tablename__ = 'tests'

    id          = Column(Integer, primary_key=True)
    name        = Column(String(200), nullable=False)
    subject_id  = Column(Integer, nullable=False)
    questions   = Column(String(200), nullable=False)
    marks       = Column(Integer, nullable=False)
    status      = Column(Integer, nullable=False)
    time        = Column(Integer, nullable=False)
    created_at  = Column(DateTime(), default=datetime.now())
    updated_at  = Column(DateTime(), onupdate=datetime.now())


    def __init__(
        self, name=name, subject_id=subject_id, questions=questions,
        marks=marks, status=status, time=time
    ):
        self.name = name
        self.subject_id = subject_id
        self.questions = questions
        self.marks = marks
        self.status = status
        self.time = time
    

    def __repr__(self):
        return f'<Test: subject->{self.subject_id} | time->{self.time}>'


    def getSubject(self):
        subject = db_session.query(Subject).filter_by(id=self.subject_id).one()
        if subject:
            return {
                'id'    : subject.id,
                'name'  : subject.name,
                'logo'  : subject.logo,
                'status': subject.status
            }
        else:
            return False

    def getQuestions(self):
        questions = json.loads(self.questions)
        questionList = []
        for i in questions:
            questionList.append(int(i['question_id']))
        

        all_questions = db_session.query(Question).filter(Question.id.in_(questionList)).all()
        if(all_questions):
            questions = []
            for i in all_questions:
                questions.append({
                    'id': i.id,
                    'question': i.question,
                    'marks': i.marks,
                })
            return questions
        else:
            return False



class TestAnswer(Base):
    __tablename__ = 'test_answers'

    id              = Column(Integer, primary_key=True)
    test_id         = Column(Integer, nullable=False)
    user_id         = Column(Integer, nullable=False)
    subject_id      = Column(Integer, nullable=False)    
    marks_obtain    = Column(Integer, nullable=False)
    total_marks     = Column(Integer, nullable=False)
    question_attend = Column(Integer, nullable=False)
    total_question  = Column(Integer, nullable=False)
    time_taken      = Column(Integer, nullable=False)
    payload         = Column(Text, nullable=False)
    certificate     = Column(Text, nullable=True)
    created_at      = Column(DateTime(), default=datetime.now())
    updated_at      = Column(DateTime(), onupdate=datetime.now())


    def __init__(
        self, test_id=test_id, user_id=user_id, subject_id=subject_id,
        marks_obtain=marks_obtain, total_marks=total_marks,
        question_attend=question_attend, total_question=total_question,
        time_taken=time_taken, payload=payload
    ):
        self.test_id        = test_id
        self.user_id        = user_id
        self.subject_id     = subject_id
        self.marks_obtain   = marks_obtain
        self.total_marks    = total_marks
        self.question_attend= question_attend
        self.total_question = total_question
        self.time_taken     = time_taken
        self.payload        = payload
    

    def getPayload(self):
        return json.loads(self.payload)
    
    def getSubject(self):
        subject = db_session.query(Subject).filter_by(id=self.subject_id).one()
        if subject:
            return {
                'id'    : subject.id,
                'name'  : subject.name,
                'logo'  : subject.logo,
                'status': subject.status
            }
        else:
            return False
    
    def getTest(self):
        test = db_session.query(Test).filter_by(id=self.test_id).one()
        if test:
            return {
                'id'    : test.id,
                'name'  : test.name,
                'marks' : test.marks,
                'time'  : test.time
            }
        else:
            return False
    