import os
from sys import platform
import time
import json
from flask import session, Flask, flash, render_template, url_for, redirect, request, session, make_response, send_file
from datetime import datetime, timedelta
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from flask_login import login_user, LoginManager, login_required, logout_user, current_user

from sqlalchemy import select

from core.database import db_session
from core.models import User, Subject, Question, QuestionOption, Test, TestAnswer
from custome_enum import users_enum, question_enum, tests_enum
from utilities import get, convert

from werkzeug.utils import secure_filename
from forms.UserForm import LoginForm, RegisterForm
from forms.SubjectForm import SubjectForm
from forms.QuestionForm import QuestionForm
from forms.TestForm import TestForm

app     = Flask(__name__)
# app.config['SECRET_KEY'] = os.urandom(32)
app.config['SECRET_KEY'] = '6bef18936ac12a9096e9fe7a8fe1f777'
app.config['WTF_CSRF_SECRET_KEY'] = 'osidfoijwsornwrnfonlsdkf64646'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
app.config['UPLOAD_FOLDER'] = 'static/img/logos'

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

bcrypt  = Bcrypt(app)
csrf = CSRFProtect(app)
csrf.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(hours=24)

@login_manager.user_loader
def load_user(user_id):
    return db_session.query(User).filter_by(id=int(user_id)).first()


@app.route('/', methods=['POST', 'GET'])
@login_required
def index():
    return render_template('index.html', users_enum=users_enum)


@app.route('/about', methods=['GET'])
def about():
    breadcrumb = {
        '<i class="fa-solid fa-house"></i>': {
            'link' : url_for('index')
        },
        'About' : {
            'link' : ''
        }
    }
    return render_template('about.html',
        breadcrumb = breadcrumb,
    )


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    
    if request.method == 'POST':
        status = False
        msg = ""
        data = {}

        user = db_session.query(User).filter_by(email=form.email.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                session.permanent = True

                # flash('You were successfully logged in', 'success')
                
                status = True
                msg    = "LogIn Successfully"
                data   = {
                    'name' : f"{user.first_name} {user.last_name}",
                    'redirect' : url_for('index')
                }

            else:
                msg = "password is incorrect"
        else:
            msg = "User not found"


        return {
            'status' : status,
            'msg'    : msg,
            'data'   : data
        }
        


    form = LoginForm()
    return render_template('login.html', form=form)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegisterForm()

    if request.method == 'POST':
        if not form.validate_email(form.email):
            return {
                'status': False,
                'msg'   : "Email already exist.",
                'data'  : {}
            }
        
        if not form.validate_password(form.password1, form.password2):
            return {
                'status': False,
                'msg'   : "Password and Confirm password did not match.",
                'data'  : {}
            }

        hashed_password = bcrypt.generate_password_hash(form.password1.data)
        new_user = User(
            first_name=form.first_name.data,
            middle_name=form.middle_name.data,
            last_name=form.last_name.data,
            role=form.role.data,
            email=form.email.data,
            password=hashed_password
        )
        db_session.add(new_user)
        db_session.commit()

        return {
            'status': True,
            'msg'   : "User created successfully",
            'data'  : {
                    'name' : f"{new_user.first_name} {new_user.last_name}",
                    'redirect' : url_for('login')
                }
        }
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)


@app.route('/subjects', methods=['POST', 'GET'])
@login_required
def subjects():
    breadcrumb = {
        '<i class="fa-solid fa-house"></i>': {
            'link' : url_for('index')
        },
        'Subjects' : {
            'link' : ''
        }
    }

    subject_form = SubjectForm()

    if request.method == 'POST':
        if request.form['action'] == 'add':
            try:
                name = request.form['name']
                file = request.files['logo']

                file_extension  = get.file_extension(file.filename)
                
                file_name       = name.strip().lower()
                file_name       = file_name.replace(' ', '_')
                file_name       = file_name + '_' + str(int(time.time())) + file_extension

                file.save(os.path.join(APP_ROOT, app.config['UPLOAD_FOLDER'], secure_filename(file_name)))
                
                new_subject = Subject(
                    name=name,
                    logo=file_name,
                )
                db_session.add(new_subject)
                db_session.commit()

                return {
                    'status': True,
                    'msg'   : "Subject Added Successfully.",
                    'data'  : {
                        'name' : file.filename,
                        'redirect' : url_for('subjects')
                    }
                }

            except Exception as e:
                
                return {
                    'status': False,
                    'msg'   : "Something went wrong.",
                    'data'  : {
                        'redirect' : url_for('subjects')
                    }
                }
        
        elif request.form['action'] == 'delete':
            if request.form['subject_id']:
                subjectModel = db_session.query(Subject).filter_by(id=request.form['subject_id']).first()
                if subjectModel:
                    subjectModel.status = False
                    db_session.commit()
                    return {
                        'status': True,
                        'msg'   : "Subject deleted.",
                        'data'  : {}
                    } 
            else:
                return {
                    'status':False,
                    'msg'   : "Something went wrong",
                    'data'  : {}
                } 

        elif request.form['action'] == 'edit':
            try:
                name = request.form['name']
                file = request.files['logo']
                subjectId = request.form['subject_id']

                if not name or not subjectId:
                    return {
                        'status': False,
                        'msg'   : "Something went wrong",
                        'data'  : {
                            'redirect' : url_for('subjects')
                        }
                    }

                if file:
                    file_extension  = get.file_extension(file.filename)
                    
                    file_name       = name.strip().lower()
                    file_name       = file_name.replace(' ', '_')
                    file_name       = file_name + '_' + str(int(time.time())) + file_extension

                    file.save(os.path.join(APP_ROOT, app.config['UPLOAD_FOLDER'], secure_filename(file_name)))
                
                subject = db_session.query(Subject).filter_by(id=int(subjectId)).first()

                if name and file:
                    subject.name = name
                    subject.logo = file_name
                elif name:
                    subject.name = name
                
                db_session.commit()

                return {
                    'status': True,
                    'msg'   : "Subject Updated Successfully.",
                    'data'  : {
                        'name' : file.filename,
                        'redirect' : url_for('subjects')
                    }
                }

            except Exception as e:
                
                return {
                    'status': False,
                    'msg'   : "Something went wrong.",
                    'data'  : {
                        'redirect' : url_for('subjects')
                    }
                }

    all_subjects = db_session.query(Subject).filter_by(status=True).all()

    subjectList = []
    for subject in all_subjects:
        subjectList.append({
            'id': subject.id,
            'name': subject.name,
            'logo': subject.logo,
            'created_at': subject.created_at
        })

    return render_template('subjects.html',
        breadcrumb = breadcrumb,
        subject_form = subject_form,
        subjectList=subjectList
    )

@app.route('/subjects/<subject_id>', methods=['POST', 'GET'])
def subject(subject_id):

    subject = db_session.query(Subject).filter_by(id=int(subject_id)).first()

    breadcrumb = {
        '<i class="fa-solid fa-house"></i>': {
            'link' : url_for('index')
        },
        'Tests': {
            'link' : url_for('subjects')
        },
        subject.name : {
            'link' : ''
        }
    }

    testList = db_session.query(Test).filter_by(status=tests_enum.STATUS_ACTIVE,subject_id=subject.id).all()
    
    all_tests = []
    if testList:
        for i in testList:
            questions = json.loads(i.questions)
            subjectObj = i.getSubject()
            all_tests.append({
                'id': i.id,
                'name': i.name,
                'subject': subjectObj['name'],
                'subject_logo': subjectObj['logo'],
                'marks': i.marks,
                'time': i.time,
                'questions': questions,
                'created_at': i.created_at
            })

    return render_template('subject-tests.html',
        subject=subject,
        breadcrumb=breadcrumb,
        all_tests=all_tests
    )


@app.route('/tests', methods=['POST', 'GET'])
@login_required
def tests():

    if request.method == 'POST':
        if request.form['action'] == 'add':
            try:
                name        = request.form['name'].strip()
                subject_id  = int(request.form['subject_id'])
                marks       = int(request.form['marks'])
                questions   = request.form['questions']
                time        = int(request.form['time'])

                new_test = Test(
                    name=name,
                    subject_id=subject_id,
                    questions=questions,
                    marks=marks,
                    status=tests_enum.STATUS_ACTIVE,
                    time=time
                )
                db_session.add(new_test)
                db_session.commit()


                return {
                    'status': True,
                    'msg'   : "Test Added Successfully.",
                    'data'  : []
                }
            except Exception:
                db_session.rollback()
                return {
                    'status': False,
                    'msg'   : "Something went wrong",
                    'data'  : []
                }

        elif request.form['action'] == 'edit':
            test_id     = request.form['test_id']
            name        = request.form['name']
            marks       = request.form['marks']
            time        = request.form['time']
            subject_id  = request.form['subject_id']
            questions   = request.form['questions']

            if(test_id):

                if test_id and name and marks and time and subject_id and questions:
                    try:

                        testModel = db_session.query(Test).filter_by(id=int(test_id)).first()

                        testModel.name          = name.strip()
                        testModel.subject_id    = int(subject_id)
                        testModel.questions     = questions
                        testModel.marks         = int(marks)
                        testModel.time          = int(time)

                        db_session.commit()

                        return {
                            'status' : True,
                            'msg' : 'Test Updated successfully.'
                        }
                    except Exception as e:
                        return {
                            'status' : False,
                            'msg' : 'Something went wrong while adding question, please try again.'
                        }
                else:
                    return {
                        'status' : False,
                        'msg' : 'All values are required.'
                    }
            else:
                return {
                    'status' : False,
                    'msg' : 'Test not found'
                }

        elif request.form['action'] == 'delete':
            test_id  = request.form['test_id']
            if(test_id):
                testModal = db_session.query(Test).filter_by(id=test_id).first()
                if testModal:
                    testModal.status = tests_enum.STATUS_INACTIVE
                    db_session.commit()
                    return {
                        'status': True,
                        'msg'   : "Test deleted.",
                        'data'  : {}
                    }


            return {
                'status' : False,
                'msg' : 'Something went wrong.'
            }

    breadcrumb = {
        '<i class="fa-solid fa-house"></i>': {
            'link' : url_for('index')
        },
        'Tests' : {
            'link' : ''
        }
    }
    test_form = TestForm()

    testList = db_session.query(Test).filter_by(status=tests_enum.STATUS_ACTIVE).all()
    
    all_subjects = db_session.query(Subject).filter_by(status=True).all()
    all_questions = db_session.query(Question, Subject).join( Subject, (Question.subject_id == Subject.id)).filter(Question.status==question_enum.STATUS_ACTIVE).all()
    all_tests = []
    for i in testList:
        all_tests.append({
            'id': i.id,
            'name': i.name,
            'subject': i.getSubject()['name'],
            'marks': i.marks,
            'time': i.time,
            'created_at': i.created_at
        })

    questionList = {}
    for question in all_questions:
        if questionList.get(f"{question.Subject.id}") is not None:
            if questionList[f"{question.Subject.id}"]["list"].get(f"{question.Question.level}") is not None:
                questionList[f"{question.Subject.id}"]["list"][f"{question.Question.level}"].append(question.Question)
            else:
                questionList[f"{question.Subject.id}"]["list"].update({
                    f"{question.Question.level}": [question.Question]
                })
        else:
            temp_dict = {
                f"{question.Subject.id}": {
                    "subject_name": question.Subject.name,
                    "list": {
                                f"{question.Question.level}": [question.Question]
                            }
                }
            }
            questionList.update(temp_dict)
    


    return render_template('tests.html',
        breadcrumb = breadcrumb,
        questionLevels = question_enum.levels,
        all_tests = all_tests,
        all_subjects = all_subjects,
        questionList = questionList,
        testForm = test_form
    )



@app.route('/get-test', methods=['POST'])
@login_required
def test():
    test_id  = request.form['test_id']

    if(test_id):
        test = db_session.query(Test).filter_by(id=int(test_id)).first()
        return {
                'status' : True,
                'msg' : '',
                'data' : {
                    'id'        : test.id,
                    'name'      : test.name,
                    'subject_id': test.subject_id,
                    'questions' : test.questions,
                    'marks'     : test.marks,
                    'status'    : test.status,
                    'time'      : test.time
                }
            }
    else:
        return {
                'status' : False,
                'msg' : 'Something went wrong.',
                'data' : []
            }



@app.route('/get-question', methods=['POST'])
@login_required
def question():
    question_id  = request.form['question_id']

    if(question_id):
        question = db_session.query(Question).filter_by(id=int(question_id)).first()
        options = question.options()
        return {
                'status' : True,
                'msg' : '',
                'data' : {
                    'question': {
                        'id': question.id,
                        'subject_id': question.subject_id,
                        'level': question.level,
                        'value': question.question,
                        'marks': question.marks,
                    },
                    'options' : options
                }
            }
    else:
        return {
                'status' : False,
                'msg' : 'Something went wrong.',
                'data' : []
            }


@app.route('/questions', methods=['POST', 'GET'])
@login_required
def questions():
    breadcrumb = {
        '<i class="fa-solid fa-house"></i>': {
            'link' : url_for('index')
        },
        'Questions' : {
            'link' : ''
        }
    }

    questionForm = QuestionForm()


    if request.method == 'POST':
        if request.form['action'] and request.form['action'] == 'add':
            subject_id  = request.form['subject_id']
            level       = request.form['level']
            marks       = request.form['marks']
            question    = request.form['question']
            options     = request.form['options']


            if subject_id and level and marks and question and options:
                try:

                    new_question = Question(
                        subject_id=int(subject_id),
                        level=int(level),
                        question=question,
                        marks=int(marks),
                        status=question_enum.STATUS_ACTIVE
                    )

                    db_session.add(new_question)
                    db_session.commit()

                    # Adding options for this question
                    options = json.loads(options)
                    optionList = []
                    for key, values in options.items():
                        optionList.append(QuestionOption(
                            question_id= new_question.id,
                            option=values['value'],
                            is_correct=values['is_correct']
                        ))

                    db_session.add_all(optionList)
                    db_session.commit()


                    return {
                        'status' : True,
                        'msg' : 'Question added successfully.'
                    }
                except Exception as e:
                    return {
                        'status' : False,
                        'msg' : 'Something went wrong while adding question, please try again.'
                    }
            else:
                return {
                    'status' : False,
                    'msg' : 'All values are required.'
                }

        elif request.form['action'] and request.form['action'] == 'edit':
            question_id  = request.form['question_id']
            subject_id  = request.form['subject_id']
            level       = request.form['level']
            marks       = request.form['marks']
            question    = request.form['question']
            options     = request.form['options']

            if(question_id):

                if subject_id and level and marks and question and options:
                    try:

                        questionModel = db_session.query(Question).filter_by(id=int(question_id)).first()

                        questionModel.subject_id    = int(subject_id)
                        questionModel.level         = int(level)
                        questionModel.question      = question
                        questionModel.marks         = int(marks)
                        questionModel.status        = question_enum.STATUS_ACTIVE

                        options = json.loads(options)
                        for key, values in options.items():
                            optionModel = db_session.query(QuestionOption).filter_by(id=int(values['id'])).first()
                            optionModel.question_id=optionModel.question_id
                            optionModel.option=values['value']
                            optionModel.is_correct=int(values['is_correct'])

                        db_session.commit()

                        return {
                            'status' : True,
                            'msg' : 'Question Updated successfully.'
                        }
                    except Exception as e:
                        return {
                            'status' : False,
                            'msg' : 'Something went wrong while adding question, please try again.'
                        }
                else:
                    return {
                        'status' : False,
                        'msg' : 'All values are required.'
                    }
            else:
                return {
                    'status' : False,
                    'msg' : 'Question not found'
                }
        
        elif request.form['action'] and request.form['action'] == 'delete':
            question_id  = request.form['question_id']
            if(question_id):
                questionModel = db_session.query(Question).filter_by(id=question_id).first()
                if questionModel:
                    questionModel.status = question_enum.STATUS_INACTIVE
                    db_session.commit()
                    return {
                        'status': True,
                        'msg'   : "Question deleted.",
                        'data'  : {}
                    }


            return {
                'status' : False,
                'msg' : 'Something went wrong.'
            }


    all_questions = db_session.query(Question).filter_by(status=question_enum.STATUS_ACTIVE).all()

    return render_template('questions.html',
        breadcrumb = breadcrumb,
        questionForm = questionForm,
        all_questions = all_questions,
        question_levels = question_enum.levels,
        level_class = question_enum.level_class
    )


    

@app.route('/practice', methods=['POST'])
@login_required
def practice():

    if request.method == 'POST':
        if request.form['action'] and request.form['action']=='start-test' and request.form['test_id']:
            testModel = db_session.query(Test).filter_by(id=request.form['test_id']).first()

            breadcrumb = {
                '<i class="fa-solid fa-house"></i>': {
                    'link' : url_for('index')
                },
                'Practice' : {
                    'link' : url_for('subjects', id=testModel.subject_id)
                },
                testModel.name :  {
                    'link' : ''
                }
            }

            if testModel:
                questions = testModel.getQuestions()

                test_questions = []
                for q in questions:
                    options = db_session.query(QuestionOption).filter_by(question_id=q['id']).all()
                    
                    optionsList = []
                    for o in options:
                        optionsList.append({
                            'option_id' : o.id,
                            'option'    : o.option
                        })

                    test_questions.append({
                        'question_id'   : q['id'],
                        'question'      : q['question'],
                        'options'       : optionsList
                    })

                return render_template('practice.html',
                    breadcrumb = breadcrumb,
                    questions=questions,
                    test_questions=test_questions,
                    time=testModel.time,
                    test_id=testModel.id,
                    subject_id=testModel.subject_id
                )

        elif request.form['action'] and request.form['action']=='save-practice':
            try:
                data    = json.loads(request.form['data'])
                qna     = data['qna']
                statics = data['statics']

                payload     = request.form['data']
                timeTaken   = statics['end_time'] - statics['start_time']
                testID      = statics['test_id']
                subjectID   = statics['subject_id']
                userID      = current_user.id

                questionAttend  = 0
                totalQuestion   = 0
                marksObtain     = 0
                totalMarks      = 0     

                for question_id, obj in qna.items():
                    totalQuestion += 1
                    questionModel  = db_session.query(Question).filter_by(id=int(question_id)).one()
                    totalMarks    += int(questionModel.marks)

                    if obj['option_id'] != False:
                        optionModel      = db_session.query(QuestionOption).filter_by(id=int(obj['option_id'])).one()
                        
                        questionAttend  += 1

                        if optionModel.is_correct:
                            marksObtain     += int(questionModel.marks)
                

                testAnswerModel = TestAnswer(
                                    test_id=testID,
                                    user_id=userID,
                                    subject_id=subjectID,
                                    marks_obtain=marksObtain,
                                    total_marks=totalMarks,
                                    question_attend=questionAttend,
                                    total_question=totalQuestion,
                                    time_taken=timeTaken,
                                    payload=payload
                                )

                db_session.add(testAnswerModel)
                db_session.commit()
                
                return {
                    'status': True,
                    'msg'   : "Practice Test added successfully.",
                    'data'  : {}
                } 
            except:
                return {
                    'status': False,
                    'msg'   : "Something went wrong, Try to re-submit your practice.",
                    'data'  : {}
                } 



@app.route('/practice-result/<practice_id>', methods=['GET', 'POST'])
@login_required
def practiceResult(practice_id):

    if current_user and practice_id:
        practiceModel = db_session.query(TestAnswer).filter_by(user_id=current_user.id, id=practice_id).first()
        testModel     = db_session.query(Test).filter_by(id=practiceModel.test_id).first()
        
        breadcrumb = {
            '<i class="fa-solid fa-house"></i>': {
                'link' : url_for('index')
            },
            'Certificates' : {
                'link' : url_for('certificates')
            },
            f'Result: {testModel.name}' : {
                'link' : ''
            }
        }

        passingPercentage   = 60
        payload             = practiceModel.getPayload()

        percentGain = round((practiceModel.marks_obtain * 100 / practiceModel.total_marks), 2) >=  passingPercentage
        practiceData = {
            'statics' : {
                'marks_obtain'      : practiceModel.marks_obtain,
                'total_marks'       : practiceModel.total_marks,
                'question_attend'   : practiceModel.question_attend,
                'total_question'    : practiceModel.total_question,
                'time_taken'        : convert.secondsToTime(practiceModel.time_taken),
                'created_at'        : practiceModel.created_at.strftime("%d / %m / %Y"),
                'result'            : "PASS" if percentGain >=  passingPercentage else "FAILED" 
            },
            'qna' : []
        }
        
        for question_id, obj in payload['qna'].items():

            questionModel   = db_session.query(Question).filter_by(id=question_id).first()
            optionModels    = db_session.query(QuestionOption).filter_by(question_id=question_id).all()
            
            right_answer = False
            for i in optionModels:
                if i.is_correct:
                    right_answer = i.id
                    break

            optionData = {
                'params'        : {
                    'selected_answer'   : int(obj['option_id']),
                    'right_answer'      : int(right_answer)
                },
                'option-list'   : []
            }
            for option in optionModels:
                optionData['option-list'].append({
                    'option_id' : option.id,
                    'option'    : option.option,
                    'is_correct': option.is_correct
                })
            
            practiceData['qna'].append({
                'question_id'   : questionModel.id,
                'question'      : questionModel.question,
                'options'       : optionData
            })
        
    
        return render_template('practice-result.html',
            breadcrumb=breadcrumb,
            practice_data=practiceData
        )



@app.route('/certificates', methods=['GET', 'POST'])
@login_required
def certificates():
    breadcrumb = {
        '<i class="fa-solid fa-house"></i>': {
            'link' : url_for('index')
        },
        'Certificates' : {
            'link' : ''
        }
    }

    all_tests_answers = db_session.query(TestAnswer).all()

    testList = {}
    for answer in all_tests_answers:
        subject = answer.getSubject()
        test    = answer.getTest()

        if str(subject['name']) not in testList:
            testList[str(subject['name'])] = {
                'subject_id'   : subject['id'],
                'subject_name' : subject['name'],
                'subject_logo' : subject['logo'],
                'test_list'    : []
            }
            

        testList[str(subject['name'])]['test_list'].append({
            'test_id'       : test['id'],
            'test_name'     : test['name'],
            'test_date'     : answer.created_at.strftime("%d %b %Y, %I:%M %p"),
            'practice_id'   : answer.id
        })


    return render_template('certificates.html',
        breadcrumb=breadcrumb,
        all_tests=all_tests_answers,
        test_list=testList
    )



@app.route('/get-certificate', methods=['POST'])
@login_required
def generateCertificate():
    if request.method == 'POST':
        practice_id     = int(request.form['practice_id'])
        practiceDetails = get.practiceDetails(practice_id)


        if int(practiceDetails['statics']['percentage']) < 60:
            return {
                'status': False,
                'msg': 'Certificates are not allowed for failed tests.',
                'data': {}
            }


        img = get.certificate(practiceDetails['statics'])

        if img['status'] and img['image_name'] and img['image']:
            
            testAnswerModel = db_session.query(TestAnswer).filter_by(user_id=current_user.id, id=practice_id).first()

            testAnswerModel.certificate = img['image_name']
            db_session.commit()


            # response = make_response(img['image'])
            # response.headers['Content-Type'] = 'image/jpeg'
            # response.headers['Content-Disposition'] = f"inline; filename={img['image_name']}"

            # return response

            return {
                'status': True,
                'msg': 'Certificate Successfully Generated',
                'data': {
                    'image_url': url_for('static', filename=f"files/certificates/{img['image_name']}")
                }
            }
        else:
            return {
                'status': False,
                'msg': 'Something went wrong',
                'data': {
                    'image_url': url_for('static', filename=f"files/certificates/{img['image_name']}")
                }
            }

    else:
        return False



if __name__ == '__main__':
    app.run(debug=True)