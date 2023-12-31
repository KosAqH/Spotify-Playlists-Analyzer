from flask_wtf import FlaskForm
from wtforms import StringField, URLField
from wtforms.validators import DataRequired, URL

class SpotifyURL(FlaskForm):
    url = StringField('URL', validators=[DataRequired(), URL(False)], render_kw={"placeholder": "URL or ID of Spotify playlist."})

class SpotifyDoubleURL(FlaskForm):
    url1 = StringField('URL', validators=[DataRequired(), URL(False)], render_kw={"placeholder": "URL or ID of Spotify playlist."})
    url2 = StringField('URL', validators=[DataRequired(), URL(False)], render_kw={"placeholder": "URL or ID of Spotify playlist."})