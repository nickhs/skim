from flask import Flask, session, render_template, request, jsonify, url_for, redirect
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.wtf import Form, TextField

app = Flask(__name__)
app.config.from_pyfile('settings.py', silent=False)

db = SQLAlchemy(app)

articles = db.Table('articles',
                    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                    db.Column('article_id', db.Integer, db.ForeignKey('article.id'))
                    )


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String)
    name = db.Column(db.String)
    password = db.Column(db.String)

    articles = db.relationship('Article', secondary=articles,
                               backref=db.backref('users', lazy='dynamic'))

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
    excerpt = db.Column(db.String(500))
    parsed = db.Column(db.Boolean)

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


class NewArticleForm(Form):
    link = TextField('Link')
    friends = TextField('Friends')


class NewUserForm(Form):
    email = TextField('Email')
    password = TextField('Password')

class LoginForm(Form):
    email = TextField("Email")
    password = TextField("Password")


@app.route('/')
def home():
    if not session.get('user'):
        return render_template('stuff')
    else:
        return render_template('home')


@app.route('/register', methods=['GET', 'POST'])
def new_user():
    form = NewUserForm()
    if form.validate_on_submit():
        user = User(form.email.data, form.password.data)
        db.session.add(user)
        db.session.commit()
        print user
        return redirect(url_for('home'))
    else:
        print "Did not validate"

    return render_template('signup.html', form=form)


@app.route('/api/user/<id>/articles/new', methods=['POST'])
def add_new_article(id):
    form = request.form
    if form.validate_on_submit():
        article = Article.query.filter_by(link=form.data.link).first()

        if article is None:
            article = Article(form.data.link)
            db.session.add(article)
            db.session.commit()
            process_article(article)

        return jsonify({'status': 'okay', 'link': article.link, 'id': article.id})


def process_article(article):
    pass

if __name__ == "__main__":
    app.run()
