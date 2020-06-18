import os

#from app import app
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from db_classes import db, Request, Goal, Teacher, Schedule, WeekDay, Booking
from data import *

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL") #"sqlite:///test.db"

#db = SQLAlchemy(app)
app.app_context().push()
db.init_app(app)

def init_db(db):
    test_id = db.session.query(Goal).get(list(goals.keys())[0])
    if test_id is None:
        for goal_id, goal_name in goals.items(): # goals from data.py
            db.session.add(Goal(id=goal_id, name=goal_name))
        db.session.commit()

    test_id = db.session.query(WeekDay).get("mon")
    if test_id is None:
        days = {"mon": (1, "Понедельник"), "tue": (2, "Вторник"), \
                "wed": (3, "Среда"), "thu": (4, "Четверг"), "fri": (5, "Пятница"), \
                "sat": (6, "Суббота"), "sun": (7, "Воскресенье")}
        for day in days:
            db.session.add(WeekDay(id=day, order_k=days[day][0], name=days[day][1]))
        db.session.commit()

    test_id = db.session.query(Teacher).get(teachers[0]["id"])
    if test_id is None:
        for t in teachers: # teachers from data.py
            teacher = Teacher(id=t["id"], name=t["name"], about=t["about"], rating=t["rating"], \
                      picture=t["picture"], price=t["price"])
            db.session.add(teacher) # основная информация
            for g in t["goals"]:
                goal = db.session.query(Goal).get(g)
                teacher.goals.append(goal) # цели
            for day in t["free"]:
                schedule = [Schedule(teacher_id=t["id"], day=day, time=time, is_free=t["free"][day][time]) for time in t["free"][day]]
                db.session.add_all(schedule) # расписание
            db.session.commit()
    return db


if __name__ == "__main__":
    db.create_all()
    db = init_db(db)

