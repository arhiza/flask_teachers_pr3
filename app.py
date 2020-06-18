import os
from random import choice

from flask import Flask, request, render_template, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, HiddenField
from wtforms.validators import InputRequired
from flask_sqlalchemy import SQLAlchemy
#from flask_migrate import Migrate

from db_classes import db, Request, Goal, Teacher, Schedule, Booking


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.secret_key = os.environ.get("SECRET_KEY")

app.app_context().push()
db.init_app(app) #SQLAlchemy(app)
#migrate = Migrate(app, db)



#import db_classes
#from init_db import init_db


#db.create_all()
#db = init_db(db)
#db.session.commit()


@app.route("/")
def render_main():
    goals = {goal.id: goal.name for goal in db.session.query(Goal).all()}
    teachers = db.session.query(Teacher).order_by(db.func.random()).limit(6)
    return render_template("index.html", goals=goals, teachers=teachers)

@app.route("/goals/<goal>/")
def render_goal(goal):
    goal_curr = db.session.query(Goal).get(goal)
    return render_template("goal.html", goal=goal_curr)

@app.route("/profiles/<int:id_teacher>/")
def render_teacher(id_teacher):
    teacher = db.session.query(Teacher).get(id_teacher)
    if teacher is None:
        return "Не могу найти информацию о преподавателе. Вы уверены, что нажали на правильную ссылку?", 404
    free = teacher.get_free()
    return render_template("profile.html", teacher=teacher, free=free)


class FormRequest(FlaskForm):
    res = [(goal.id, goal.name) for goal in db.session.query(Goal).all()]
    goal = RadioField("Какая цель занятий?", [InputRequired()], choices = res)
    time = RadioField("Сколько времени есть?", [InputRequired()], \
                      choices = [("1-2","1-2 часа в\xa0неделю"), \
                                 ("3-5","3-5 часов в\xa0неделю"), \
                                 ("5-7","5-7 часов в\xa0неделю"), \
                                 ("7-10","7-10 часов в\xa0неделю")])
    name = StringField("Вас зовут", [InputRequired()])
    phone = StringField("Ваш телефон", [InputRequired()])


@app.route("/request/", methods=["GET", "POST"])
def render_request():
    form = FormRequest()
    if form.goal.data is None: # запрос по get, в форме никто ничего пока не заполнял
        form.goal.data = choice(form.goal.choices)[0]
        form.time.data = choice(form.time.choices)[0]
    if form.validate_on_submit():
        db.session.add(Request(goal=form.goal.data, time=form.time.data, \
                               name=form.name.data, phone=form.phone.data))
        db.session.commit()
        return render_template("request_done.html", form=form)
    return render_template("request.html", form=form)


class FormBooking(FlaskForm): # форма бронирования времени урока, 
                         # преподаватель-день-время берутся из параметров страницы
    name = StringField("Вас зовут", [InputRequired()])
    phone = StringField("Ваш телефон", [InputRequired()])


@app.route("/booking/<id_teacher>/<day>/<time>/", methods=["GET", "POST"])
def render_booking(id_teacher, day, time):
    teacher = db.session.query(Teacher).get(id_teacher)
    if teacher is None:
        return "Не могу найти информацию о преподавателе. " \
                + "Вы уверены, что нажали на правильную ссылку?", 404
    free = db.session.query(Schedule).filter((Schedule.teacher_id==id_teacher) \
                                             & (Schedule.day==day) \
                                             & (Schedule.time==time)).first()
    if free is None:
        return "Похоже, вы составили ссылку вручную, а не пришли со страницы преподавателя. " \
               + "Не надо так.", 404

    form = FormBooking()
    if form.validate_on_submit() and free.is_free and not(free.booking_id):
        new_booking = Booking(name=form.name.data, phone=form.phone.data)
        db.session.add(new_booking)
        db.session.commit()
        free.booking_id = new_booking.id
        db.session.commit()
        return render_template("booking_done.html", form=form, day=day, time=time, free=free)

    return render_template("booking.html", form=form, teacher=teacher, \
                                           free=free, day=day, time=time) 


if __name__ == "__main__":
    app.run() #debug=True)

