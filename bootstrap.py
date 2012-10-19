from app import *


def drop_and_create():
    print "Dropping database..."
    db.drop_all()
    print "Creating database..."
    db.create_all()
    print "Done"


def create_users():
    data = [
        ('nick@kiip.me', 'nick'),
        ('adam@kiip.me', 'adam'),
        ('soo@kiip.me', 'soo'),
        ('brad@kiip.me', 'brad')
    ]

    for d in data:
        u = User(d[0], d[1])
        db.session.add(u)
        db.session.commit()


def create_shares():
    art = Article('bbc.com')
    add_item(art)
    process_article(art)

    a = User.query.get(1)
    # a shares with both b and c, he just likes b more

    b = User.query.get(2)
    c = User.query.get(3)

    for i in xrange(0, 5):
        sh = Share(a, b, art)
        add_item(sh)
        sh = None

    for i in xrange(0, 3):
        sh = Share(a, c, art)
        add_item(sh)
        sh = None

if __name__ == "__main__":
    drop_and_create()
    create_users()
    create_shares()
