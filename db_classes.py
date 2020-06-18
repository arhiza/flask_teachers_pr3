from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Request(db.Model):
    __tablename__ = 'requests'
    id = db.Column(db.Integer, primary_key=True)
    # все про запросы "найдите мне преподавателя"
    goal = db.Column(db.String, nullable=False) # TODO может быть, нужна привязка к таблице с целями
    time = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    phone = db.Column(db.String, nullable=False)


teachers_goals_association = db.Table(
    "teachers_goals",
    db.Column("teacher_id", db.Integer, db.ForeignKey("teachers.id")),
    db.Column("goal_id", db.String, db.ForeignKey("goals.id"))
)


class Goal(db.Model):
    __tablename__ = "goals"
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    teachers = db.relationship("Teacher", secondary=teachers_goals_association, \
                               back_populates="goals", order_by="desc(Teacher.rating)")


class Teacher(db.Model):
    __tablename__ = "teachers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    about = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    picture  = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    goals = db.relationship("Goal", secondary=teachers_goals_association, back_populates="teachers")

    def get_free(self): # в формате, удобном для распознавания в шаблоне
        free = []
        days = db.session.query(WeekDay).order_by(WeekDay.order_k).all()
        for day in days:
            #print(day.id, day.order_k, day.name)
            time_hours = db.session.query(Schedule).filter(Schedule.teacher_id==self.id). \
                         filter(Schedule.day==day.id).all()
            if len(time_hours) > 0:
                res = [] # сложить список свободных часов
                for t in time_hours:
                    if t.is_free and not t.booking_id: # 
                        res.append(t.time)
                res = sorted(res, key=lambda x: int(str(x).split(":")[0]))
                free.append([day.id, day.name, res])
        return free


class Schedule(db.Model): # для расписания, пометок свободно ли окно, и привязок к заявкам на бронирование
    __tablename__ = "free"
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    day = db.Column(db.String(3), db.ForeignKey('weekdays.id'))
    day_name = db.relationship('WeekDay')
    time = db.Column(db.String(5))
    is_free = db.Column(db.Boolean)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'))
    booking = db.relationship('Booking', back_populates='free')


class WeekDay(db.Model):
    __tablename__ = "weekdays"
    id = db.Column(db.String(3), primary_key=True)
    order_k = db.Column(db.Integer)
    name = db.Column(db.String(15))


class Booking(db.Model):
    __tablename__ = "bookings"
    id = db.Column(db.Integer, primary_key=True)
    free = db.relationship('Schedule', back_populates='booking')
    name = db.Column(db.String(), nullable=False)
    phone = db.Column(db.String(), nullable=False)

