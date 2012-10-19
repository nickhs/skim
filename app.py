from flask import Flask, session, render_template, request, jsonify, url_for, redirect
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask.ext.wtf import Form, TextField, PasswordField
import requests

app = Flask(__name__)
app.config.from_pyfile('settings.py', silent=False)

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String)
    name = db.Column(db.String)
    password = db.Column(db.String)

    shares = db.relationship('Share', backref='receiver',
                             primaryjoin="User.id==Share.receiver_id",
                             lazy='dynamic')

    shared = db.relationship('Share', backref='originator',
                             primaryjoin="User.id==Share.originator_id",
                             lazy="dynamic")

    def __init__(self, email, password):
        self.email = email
        self.password = password

    def __repr__(self):
        return "<User: %r>" % self.email

    def __str__(self):
        return self.email


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.String)
    title = db.Column(db.String)
    text = db.Column(db.Text)
    icon = db.Column(db.LargeBinary)
    author = db.Column(db.String)
    excerpt = db.Column(db.String(250))
    parsed = db.Column(db.Boolean)

    shares = db.relationship('Share', backref='article',
                             lazy='dynamic')

    def __init__(self, link, parsed=False):
        self.link = link
        self.parsed = parsed

    def add_params(self, title, text, author, icon=None, parsed=True):
        self.title = title
        self.text = text
        self.author = author
        self.icon = icon
        self.excerpt = self.text[0:250]
        self.parsed = parsed

    def __repr__(self):
        return "<Article: %r>" % self.title

    def __str__(self):
        return self.title


class Share(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    originator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'))
    read = db.Column(db.Boolean)
    comments = db.Column(db.Text)

    def __init__(self, originator, receiver, article, read=False):
        self.originator_id = originator.id
        self.receiver_id = receiver.id
        self.article = article
        self.read = read

    def __repr__(self):
        return "<Share: %r>" % self.id

    def __str__(self):
        return self.id


class NewUserForm(Form):
    email = TextField('Email')
    password = PasswordField('Password')


class LoginForm(Form):
    email = TextField("Email")
    password = PasswordField("Password")


class NewShareForm(Form):
    link = TextField("Link")
    friends = TextField("Friends")


@app.route('/', methods=['POST', 'GET'])
def home():
    if not session.get('user_id'):
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user is not None and user.password == form.password.data:
                session['user_id'] = user.id

        return render_template('landing.html', form=form)
    else:
        id = session.get('user_id')
        user = User.query.get(id)
        # TODO: Order by date, pagination
        shares = user.shares.all()
        return render_template('index.html', user=user, shares=shares)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = NewUserForm()
    if form.validate_on_submit():
        user = User(form.email.data, form.password.data)
        add_item(user)
        return redirect(url_for('home'))

    return render_template('signup.html', form=form)


@app.route('/share', methods=['GET', 'POST'])
def share():
    form = NewShareForm()
    if form.validate_on_submit():
        article = Article.query.filter_by(link=form.link.data).first()
        user = User.query.get(session.get('user_id'))

        if article is None:
            article = Article(form.link.data)
            add_item(article)
            process_article(article)

        friends = form.friends.data.split(' ')
        for email in friends:
            friend = User.query.filter_by(email=email).first()

            if friend is None:
                # TODO; Handle missing friend
                continue

            share = Share(user, friend, article)
            add_item(share)

        return redirect(url_for('home'))

    friends = get_most_shared(session.get('user_id'))
    return render_template('share.html', form=form, friends=friends)


@app.route('/article/<id>')
def view_article(id):
    article = Article.query.get(id)
    return render_template('article.html', article=article)


@app.route('/logout')
def logout():
    for key in session.keys():
        session.pop(key)

    return redirect(url_for('home'))


@app.route('/api/user/<id>/articles/new', methods=['POST'])
def add_new_article(id):
    data = request.json
    user = User.query.get_or_404(id)
    article = Article.query.filter_by(link=data['link']).first()

    if article is None:
        article = Article(data['link'], user)
        process_article(article)
    else:
        article.add_user(user)

    add_item(article)
    return jsonify({'status': 'okay', 'link': article.link, 'id': article.id})


def process_article(article):
    url = app.config['DIFFBOT_ENDPOINT']

    params = {
        'token': app.config['DIFFBOT_TOKEN'],
        'url': article.link,
        'summary': True,
        'stats': True,
    }

    response = requests.get(url, params=params)

    if response.status_code == requests.codes.ok:
        article.text = response.json.get('text')
        article.title = response.json.get('title')
        article.author = response.json.get('author')
        print response.json.get('tags')
        print response.json.get('stats')
        print response.json.get('summary')
        article.parsed = True
        add_item(article)

        return response


def add_item(item):
    db.session.add(item)
    db.session.commit()


def get_most_shared(user, limit=None):
    if not limit:
        limit = 10

    if type(user) == User:
        id = user.id
    else:
        id = user

    result = db.session.query(Share.receiver_id, func.count('*')).\
            filter_by(originator_id=id).\
            group_by(Share.receiver_id).\
            limit(limit).all()

    ret = []
    for r in result:
        ret.append(User.query.get(r[0]))

    return ret


if __name__ == "__main__":
    app.run()
