from app import db,app


# myarticles table
class myarticles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20))
    author = db.Column(db.String(50))
    body = db.Column(db.Text)
    date = db.Column(db.DateTime(timezone=True), default=func.now())


# users table
class users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    username = db.Column(db.String(30))
    email = db.Column(db.String(100))
    password = db.Column(db.String(20))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
