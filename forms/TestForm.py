from flask_wtf import FlaskForm, csrf
from wtforms import StringField, SelectField, SubmitField, HiddenField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_wtf.file import FileField, FileAllowed, FileRequired
from core.database import db_session

from core.models import Subject
from core.models import Test

class TestForm(FlaskForm):

    all_subjects = db_session.query(Subject).filter_by(status=True).all()

    subjectList = [('', 'Select')]
    for subject in all_subjects:
        subjectList.append((subject.id, subject.name))

    name        = StringField("Name", [InputRequired(), Length(min=4, max=20)], render_kw={"class":"form-control"})
    subject     = SelectField('Subject', choices=subjectList, render_kw={"class":"form-select"})
    marks       = StringField("Marks", [InputRequired()], render_kw={"class":"form-control", "placeholder":"Auto Calculate", "readonly":True})
    time        = StringField("Time (min.)", [InputRequired()], render_kw={"class":"form-control"})
    questions   = HiddenField("Questions", [InputRequired()], render_kw={"class":"form-control"})
    submit      = SubmitField("Save", render_kw={"class":"btn btn-outline-success", "id":"subject-form-submit", "value":"Save"}) 
    
