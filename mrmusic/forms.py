from flask.ext.wtf import Form
from wtforms import RadioField, StringField, DateField

class BestAlbumForm(Form):
    deploy_preference = RadioField('Deployment Preference', choices = [
        ('The Life of Pablo', 'The Life of Pablo'),
        ('Blackstar', 'Blackstar'),
        ('Emily\'s D+Evolution', 'Emily\'s D+Evolution')], 
        default='The Life of Pablo')

class AlbumReviewForm(Form):
    Album = StringField('Album')
    Artist = StringField('Artist')
    Release = DateField('Release')

