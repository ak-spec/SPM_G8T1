from datetime import datetime, timedelta
from extensions import db
from models.Employee import Employee  
from models.WFH_Application import WFHApplication

class WFHSchedule(db.Model):
    __tablename__ = 'WFH_Schedule'
    
    Schedule_ID = db.Column(db.Integer, primary_key=True)
    Staff_ID = db.Column(db.Integer, db.ForeignKey(Employee.Staff_ID), nullable=False, index=True)
    Application_ID = db.Column(db.Integer, db.ForeignKey(WFHApplication.Application_ID), nullable=False, index=True)
    Team_ID = db.Column(db.Integer, db.ForeignKey(Employee.Staff_ID), nullable=False, index=True)
    Date = db.Column(db.DateTime, nullable=False)
    Time_Slot = db.Column(db.Enum('AM', 'PM', 'Day'), nullable=False)
    Status = db.Column(db.Enum('Passed', 'Upcoming', 'Cancelled'), nullable=False)
    Withdrawal_Reason = db.Column(db.String(255), nullable=True)
    Withdrawal_Confirmed = db.Column(db.Boolean, default=False)
    Manager_Notified = db.Column(db.Boolean, default=False)

    # Relationships
    employee = db.relationship('Employee', foreign_keys=[Staff_ID], backref='schedules')
    application = db.relationship('WFHApplication', backref=db.backref('schedule', uselist=False))
    reporting_manager = db.relationship('Employee', foreign_keys=[Team_ID], backref='managed_schedules')

    def __repr__(self):
        return f"WFHSchedule({self.Schedule_ID}, Staff ID: {self.Staff_ID}, Application ID: {self.Application_ID}, Date: {self.Date})"

    @classmethod
    def createSchedule(cls, staff_id, application_id, date, time_slot):

        try:

            if date <= datetime.now().date():
                raise ValueError("Invalid date. Date must be in the future.")
            
            if date > datetime.now() + timedelta(days=365):
                raise ValueError("Invalid date. Date must be within one year.")

            newSchedule = cls(Staff_ID=staff_id, 
                            Application_ID = application_id, 
                            Date = date, 
                            Time_Slot = time_slot, 
                            Status ='Upcoming')
            db.session.add(newSchedule)
            db.session.commit()
            return newSchedule
        
        except Exception as e:
            db.session.rollback()
            raise e

    @classmethod  
    def updateSchedule(cls, schedule_id, time_slot, date):

        try:
            
            schedule_retrieved = cls.query.get(schedule_id)
            if schedule_retrieved:

                if date <= datetime.now().date():
                    raise ValueError("Invalid date. Date must be in the future.")

                schedule_retrieved.time_slot = time_slot
                schedule_retrieved.date = date
                db.session.commit()

                return schedule_retrieved
            
            raise ValueError("Schedule not found")
        
        except Exception as e:
            db.session.rollback()
            raise e

    @classmethod  
    def cancelSchedule(cls, schedule_id):

        try:

            schedule = cls.query.get(schedule_id)
            if schedule:
                schedule.status = 'Cancelled'
                db.session.commit()
                return schedule
            raise ValueError("Schedule not found")

        except Exception as e:
            db.session.rollback()
            raise e