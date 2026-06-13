from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, FloatField, DateField, HiddenField
from wtforms.validators import DataRequired, Email, Length, Optional


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])


class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(1, 80)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(1, 120)])
    password = PasswordField("Password", validators=[DataRequired(), Length(6, 128)])


class ProjectForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(1, 120)])
    description = TextAreaField("Description", validators=[Optional()])
    color = StringField("Color", validators=[Optional(), Length(7, 7)])


class TaskForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(1, 200)])
    description = TextAreaField("Description", validators=[Optional()])
    status = SelectField("Status", choices=[("backlog", "Backlog"), ("todo", "To Do"),
                                            ("in_progress", "In Progress"), ("done", "Done")],
                         default="todo")
    priority = SelectField("Priority", choices=[("low", "Low"), ("medium", "Medium"),
                                                ("high", "High"), ("critical", "Critical")],
                           default="medium")
    due_date = DateField("Due Date", validators=[Optional()])
    estimated_hours = FloatField("Est. Hours", validators=[Optional()])
    project_id = SelectField("Project", coerce=int, validators=[Optional()])
    assignee_id = HiddenField("Assignee")


class AIForm(FlaskForm):
    title = StringField("Task Title", validators=[DataRequired(), Length(1, 200)])
