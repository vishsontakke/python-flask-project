
from flask_wtf import FlaskForm, csrf
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_wtf.file import FileField, FileAllowed, FileRequired

from core.models import Subject

class SubjectForm(FlaskForm):
    name  = StringField("Name", [InputRequired(), Length(min=4, max=20)], render_kw={"class":"form-control"})
    logo = FileField("Attach Logo file", [FileRequired(), FileAllowed(['jpg', 'png'], '(jpg, png only)')], render_kw={"class":"form-control"})
    submit      = SubmitField("Save", render_kw={"class":"btn btn-outline-success", "id":"subject-form-submit", "value":"Save"}) 
    
