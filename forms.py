from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class SubmitForm(FlaskForm):
    tickerName = StringField('Ticker', validators=[DataRequired()])
    submit = SubmitField('View Graph and Summary Stats')