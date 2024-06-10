from flask_wtf import FlaskForm, csrf
from wtforms import StringField, SelectField, SubmitField, IntegerField, TextAreaField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_wtf.file import FileField, FileAllowed, FileRequired
from core.database import db_session

from core.models import Question, Subject
from custome_enum import question_enum

class QuestionForm(FlaskForm):

    all_subjects = db_session.query(Subject).filter_by(status=True).all()

    subjectList = [('', 'Select')]
    for subject in all_subjects:
        subjectList.append((subject.id, subject.name))

    subject_id  = SelectField('Subject', choices=subjectList, render_kw={"class":"form-select"})
    level       = SelectField('Level', choices=[('', 'Select')]+[(i, j.title()) for i,j in question_enum.levels.items()], render_kw={"class":"form-select"})
    question    = TextAreaField('Question', render_kw={"class":"form-control"})
    marks       = IntegerField('Marks', render_kw={"class":"form-control", "min":"1", "max":"10"})
    options1    = TextAreaField('Options A', render_kw={"class":"form-control"})
    options2    = TextAreaField('Options B', render_kw={"class":"form-control"})
    options3    = TextAreaField('Options C', render_kw={"class":"form-control"})
    options4    = TextAreaField('Options D', render_kw={"class":"form-control"})

    # name  = StringField("Name", [InputRequired(), Length(min=4, max=20)], render_kw={"class":"form-control"})
    # logo = FileField("Attach Logo file", [FileRequired(), FileAllowed(['jpg', 'png'], '(jpg, png only)')], render_kw={"class":"form-control"})
    # submit      = SubmitField("Save", render_kw={"class":"btn btn-outline-success", "id":"subject-form-submit", "value":"Save"}) 
 
