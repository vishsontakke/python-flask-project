
from flask_wtf import FlaskForm, csrf
from wtforms import StringField, SelectField, PasswordField, SubmitField, EmailField
from wtforms.validators import InputRequired, Length, ValidationError
from sqlalchemy import select

from flask_bcrypt import Bcrypt

from core.models import User
from core.database import db_session
from custome_enum import users_enum

class RegisterForm(FlaskForm):
    first_name  = StringField("First Name", [InputRequired(), Length(min=4, max=20)], render_kw={"class":"form-control"})
    middle_name = StringField("Middle Name", [InputRequired(), Length(min=4, max=20)], render_kw={"class":"form-control"})
    last_name   = StringField("Last Name", [InputRequired(), Length(min=4, max=20)], render_kw={"class":"form-control"})
    role        = SelectField('Role', choices=[(i, j) for i,j in users_enum.roles.items()], render_kw={"class":"form-select"})
    email       = EmailField("Email ID", [InputRequired(), Length(min=4, max=100)], render_kw={"class":"form-control"})
    password1   = PasswordField("Password", [InputRequired()], render_kw={"class":"form-control"})
    password2   = PasswordField("Confirm Password", [InputRequired()], render_kw={"class":"form-control"})
    submit      = SubmitField("Register", render_kw={"class":"btn btn-outline-success", "id":"register-form-submit", "value":"SignUp"}) 
    
    # first_name  = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"class":"form-control"})
    # middle_name = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"class":"form-control"})
    # last_name   = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"class":"form-control"})
    # email       = EmailField(validators=[InputRequired(), Length(min=4, max=100)], render_kw={"class":"form-control"})
    # password1   = PasswordField(validators=[InputRequired()], render_kw={"class":"form-control"})
    # password2   = PasswordField(validators=[InputRequired()], render_kw={"class":"form-control"})
    # submit      = SubmitField("Register", render_kw={"class":"btn btn-outline-success", "id":"register-form-submit", "value":"SignUp"}) 

    # print({
    #     'first_name': first_name.data,
    #     'middle_name': middle_name.data,
    #     'last_name': last_name.data,
    #     'email': email.data,
    #     'password1': password1.data,
    #     'password2': password2.data
    # })

    def validate_email(self, email):
        # stmt = select(User).filter(User.email==email.data)
        # result = db_session.execute(stmt)

        # for user in result.scalars():
        #     print(user.first_name)

        # existing_email = User.query.filter_by(email=email.data).first()
        existing_email = bool(db_session.query(User).filter_by(email=email.data).first())

        if existing_email:
            return False
        
        return True
    
    def validate_password(self, password1, password2):
        if password1.data != password2.data:
            return False
        
        return True 



class LoginForm(FlaskForm):
    email    = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder":"Email"})
    password = PasswordField(validators=[InputRequired()], render_kw={"placeholder":"Password"})
    submit   = SubmitField("Login") 