from flask import Flask, request, render_template, make_response, flash, redirect, url_for, send_from_directory, jsonify
from flask_script import Manager, Shell
import requests
import os

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from flask_sqlalchemy import SQLAlchemy

from flask_migrate import Migrate, MigrateCommand
from flask_mail import Mail, Message

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField, PasswordField, BooleanField, SelectMultipleField, ValidationError
from wtforms.validators import Required, Length, Email, Regexp, EqualTo

from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import LoginManager, login_required, logout_user, login_user, UserMixin, current_user

# Configure base directory of app
basedir = os.path.abspath(os.path.dirname(__file__))

# Application configurations
app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'hardtoguessstringfromsi364'

UPLOAD_FOLDER = 'cover_art/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
	return '.' in filename and \
		   filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost/smorossFinal"
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#Configure email 
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587 #default
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'smoross364@gmail.com'
app.config['MAIL_PASSWORD'] = 'ryebrooktecmichigan'
app.config['MAIL_SUBJECT_PREFIX'] = '[Music Video App]'
app.config['MAIL_SENDER'] = 'smoross364@gmail.com'
app.config['ADMIN'] = 'smoross364@gmail.com'

# Set up Flask debug
manager = Manager(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db) 
manager.add_command('db', MigrateCommand) 
mail = Mail(app)

# Login configurations setup
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'
login_manager.init_app(app) # set up login manager

def make_shell_context():
	return dict(app=app, db=db, text=text, User=User, ) #FIX THESE

manager.add_command("shell", Shell(make_context=make_shell_context))

#send email function
def send_email(to, subject, template, **kwargs):
	with app.app_context():
		msg = Message(app.config['MAIL_SUBJECT_PREFIX'] + ' ' + subject, sender=app.config['MAIL_SENDER'], recipients=[to])
		msg.body = render_template(template + '.txt', **kwargs)
		msg.html = render_template(template + '.html', **kwargs)
		mail.send(msg)

# Models

# Playlists:Music_Videos = Many:Many
# User:Playlists = One:Many

class Music_Video(db.Model):
	__tablename__ = 'music_videos'
	id = db.Column(db.Integer, primary_key=True)
	artist = db.Column(db.String) 
	title = db.Column(db.String)
	embedURL = db.Column(db.String(256))

# Login and registration
class User(UserMixin, db.Model):
	__tablename__ = "users"
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(64), unique=True, index=True)
	password_hash = db.Column(db.String(200))

	@property
	def password(self):
		raise AttributeError('password is not a readable attribute')

	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)

	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)

# User Playlists
class Playlist(db.Model):
	__tablename__ = "playlists"
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(255))
	user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

class Playlist_to_Song(db.Model):
	__tablename__ = "association_table"
	id = db.Column(db.Integer, primary_key=True)
	playlist_id = db.Column(db.Integer, db.ForeignKey("playlists.id"))
	video_id = db.Column(db.Integer, db.ForeignKey("music_videos.id"))
#get_or_create function here

class UserUpload(db.Model): 
	__tablename__ = 'cover_art'
	id = db.Column(db.Integer, primary_key=True)
	fileName = db.Column(db.String, unique=True)
	playlist_id = db.Column(db.Integer, db.ForeignKey("playlists.id"))

class ItunesForm(FlaskForm):
	text = StringField("Enter an artist or song that you would like to see music videos for: ", validators=[Required()])
	submit = SubmitField('Submit')

#get_or_create functions 
def get_or_create_user(db_session, username, email):
	user = db_session.query(User).filter_by(username=username, email=email).first()
	if user:
		return user
	else:
		user = User(username=username, email=email)
		db_session.add(user)
		db_session.commit()
		return user

def get_or_create_search(db_session, input_text): 
	search = db_session.query(Search).filter_by(text=input_text).first()
	if search:
		return search
	else:
		search = Search(text=input_text)
		db_session.add(search)
		db_session.commit()
		return search

def get_or_create_music_video(artist, title, url):
	video = db.session.query(Music_Video).filter_by(title = title).first()
	if video:
		return video
	else:
		video = Music_Video(title=title, artist=artist, embedURL=url)
		db.session.add(video)
		db.session.commit()
		return video

def get_or_create_playlist_song(playlist_id, title):
	video_id = db.session.query(Music_Video).filter_by(title = title).first().id
	playlist_song = db.session.query(Playlist_to_Song).filter_by(playlist_id=playlist_id, video_id=video_id).first()
	if playlist_song:
		return playlist_song
	else:
		playlist_song = Playlist_to_Song(playlist_id=playlist_id, video_id=video_id)
		db.session.add(playlist_song)
		db.session.commit()
		return playlist_song

def get_or_create_playlist(name, user_id):
	playlist = db.session.query(Playlist).filter_by(name = name, user_id=user_id).first()
	if playlist:
		return playlist
	else:
		playlist = Playlist(name = name, user_id=user_id)
		db.session.add(playlist)
		db.session.commit()
		return playlist
	
# Error handling routes
@app.errorhandler(404)
def page_not_found(e): 
	return render_template('404_FP.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
	return render_template('500_FP.html'), 500

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id)) # Returns User object or None

class RegistrationForm(FlaskForm):
	email = StringField('Email:', validators=[Required(),Length(1,64),Email()])
	password = PasswordField('Password:',validators=[Required(),EqualTo('password2',message="Passwords must match")])
	password2 = PasswordField("Confirm Password:",validators=[Required()])
	submit = SubmitField('Register User')

	def validate_email(self,field):
		if User.query.filter_by(email=field.data).first():
			raise ValidationError('Email already registered.')

class LoginForm(FlaskForm):
	email = StringField('Email', validators=[Required(), Length(1,64), Email()])
	password = PasswordField('Password', validators=[Required()])
	remember_me = BooleanField('Keep me logged in')
	submit = SubmitField('Log In')

class CreatePlaylist(FlaskForm):
	playlist_name = StringField('Enter a new playlist name: ', validators=[Required()])
	submit = SubmitField('Create Playlist')

# Login Routes -- Authentication
@app.route('/login',methods=["GET","POST"])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user is not None and user.verify_password(form.password.data):
			login_user(user, form.remember_me.data)
			return redirect(request.args.get('next') or url_for('form'))
		flash('Invalid username or password.')
	return render_template('login_form.html',form=form)

@app.route('/logout')
@login_required
def logout():
	logout_user()
	flash('You have been logged out')
	return redirect(url_for('form'))

@app.route('/register',methods=["GET","POST"])
def register_user():
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(email=form.email.data,password=form.password.data)
		db.session.add(user)
		db.session.commit()
		flash('You can now log in!')
		return redirect(url_for('login'))
	return render_template('register_user.html',form=form)

@app.route('/secret')
@login_required
def secret():
	return "Only authenticated users can do this! Try to log in or contact the site admin."

def searchMusicVideos(searchTerm):
	data = requests.get("https://itunes.apple.com/search", params = {
		"entity" : "musicVideo",
		"term" : searchTerm
		}).json()["results"]
	for video in data:
		get_or_create_music_video(video["artistName"], video["trackName"], video["previewUrl"])
		if video["previewUrl"] == 'None':
			return render_template('No_Results.html', form=Form)
		else:
			return data

# Main Routes

@app.route('/', methods=["GET", "POST"])
@login_required
def form():
	playlist_form = CreatePlaylist()
	Form = ItunesForm()
	if playlist_form.validate_on_submit():
		get_or_create_playlist(playlist_form.playlist_name.data, current_user.id)
		return redirect("/playlists")
	return render_template('Itunes_Form.html', form=Form, playlist_form=playlist_form) #render WTF form

@app.route('/result', methods= ['POST'])
@login_required
def result(): 
	form = ItunesForm(request.form)
	if request.method == 'POST' and form.validate_on_submit():
		text = form.text.data
		data = searchMusicVideos(text)
		return render_template('musicVideos.html', results = data, searchTerm=text)

@app.route("/video/<artistName>/<trackName>", methods=["GET", "POST"])
@login_required
def trackName(artistName, trackName):
	if request.method == "POST":
		get_or_create_playlist_song(request.form.get('playlist'), trackName)
		playlist_name=db.session.query(Playlist).filter_by(id=request.form.get('playlist')).first().name
		send_email(current_user.email, "You just added a new song!", "mail/new_video", trackName=trackName, artistName=artistName, playlist_name=playlist_name)
		return redirect(url_for("show_playlist"))
	data = searchMusicVideos("{} by {}".format(trackName, artistName))
	playlist_for_user = db.session.query(Playlist).filter_by(user_id=current_user.id).all()
	return render_template('musicVideoPreview.html', result = data[0], trackName=trackName, artistName=artistName, playlists=playlist_for_user)

@app.route('/playlists')
@login_required
def show_playlist():
	data_dict = {}
	playlist_for_user = db.session.query(Playlist).filter_by(user_id=current_user.id).all()

	for playlist in playlist_for_user:
		data_dict[playlist.name] = [video.Music_Video.title for video in db.session.query(Playlist_to_Song, Music_Video).filter(Playlist_to_Song.playlist_id == playlist.id).join(Music_Video).all()]
	return render_template('playlists.html', data=data_dict)

@app.route('/<playlist_name>/upload', methods=["POST"])	
@login_required
def upload_art(playlist_name):
	if 'file' not in request.files:
		flash('No file part')
		return redirect("/playlists")
	file = request.files['file']
	if file.filename == '':
		flash('No selected file')
		return redirect("/playlists")
	if file and allowed_file(file.filename):
		filename = secure_filename(file.filename)
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		new_coverArt=UserUpload(fileName = filename, playlist_id=db.session.query(Playlist).filter_by(name=playlist_name).first().id)
		db.session.add(new_coverArt)
		db.session.commit()
		return redirect('/playlists')

@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
	return send_from_directory(app.config['UPLOAD_FOLDER'],
							   filename)

@app.route('/ajax/<playlist_name>')
@login_required
def ajax(playlist_name):
	playlist_id = db.session.query(Playlist).filter_by(name=playlist_name, user_id=current_user.id).first().id
	return jsonify({
		"imageLink" : db.session.query(UserUpload).filter_by(playlist_id=playlist_id).first().fileName
		})

if __name__ == '__main__':
	db.create_all()
	manager.run() # Run with: python main_app.py runserver
