from flask_sqlalchemy import SQLAlchemy
from flask import Flask, jsonify, request, render_template
from flask_restful import Api, Resource
from http import HTTPStatus
import psycopg2
from flask_migrate import Migrate
import os


class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://root:1234@localhost/Moviesdatabase'


class Development_Config(Config):
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://root:1234@localhost/Moviesdatabase'


class Production_Config(Config):
    uri = os.environ.get("DATABASE_URL")
    if uri and uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = uri


env = os.environ.get('ENV', 'Development')

if env == 'Production':
    config_str = Production_Config
else:
    config_str = Development_Config

app = Flask(__name__)
app.config.from_object(config_str)
api = Api(app)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://root:1234@localhost/Moviesdatabase'
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # this is the primary key
    title = db.Column(db.String(80), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    genre = db.Column(db.String(80), nullable=False)
    IMDbrating = db.Column(db.Integer, nullable=True)

    @staticmethod
    def addMovie(title, year, genre):
        new_movie = Movie(title=title, year=year, genre=genre)
        db.session.add(new_movie)
        db.session.commit()
        return Movie.query.all()

    @staticmethod
    def getmovie():
        mdata = Movie.query.all()
        return mdata

    @staticmethod
    def jsonmovie(data):
        movielist = []
        for i in data:
            movielist.append({'title': i.title, 'year': i.year, 'genre': i.genre})
        return jsonify((movielist), {"status": HTTPStatus.OK})

    @staticmethod
    def workreducer(data):
        if data:
            movielist = []
            movielist.append({'title': data.title, 'year': data.year, 'genre': data.genre})
            return jsonify((movielist), {"status": HTTPStatus.OK})
        else:
            return {"message": "Not Found", 'status': HTTPStatus.NOT_FOUND}

    @staticmethod
    def workreducerloop(data):
        if data:
            movielist = []
            for movies in data:
                movielist.append({'title': movies.title, 'year': movies.year, 'genre': movies.genre})
            return jsonify((movielist), {"status": HTTPStatus.OK})
        else:
            return {"message": "ID Not Found", 'status': HTTPStatus.NOT_FOUND}

    @staticmethod
    def filterbymovieid(ids):
        data = Movie.query.filter_by(id=ids).first()
        return Movie.workreducer(data)

    @staticmethod
    def filterbymoviename(name):
        data = Movie.query.filter_by(title=name).first()
        return Movie.workreducer(data)

    @staticmethod
    def filterbygenre(genres):
        data = Movie.query.filter_by(genre=genres)
        return Movie.workreducer(data)

    @staticmethod
    def deletebyid(ids):
        Movie.query.filter_by(id=ids).delete()
        db.session.commit()
        data = Movie.query.all()
        return Movie.workreducerloop(data)

    @staticmethod
    def updatemovie(ids):
        Movie.query.filter_by(id=ids).update(request.get_json())
        db.session.commit()
        data = Movie.query.all()
        return Movie.workreducerloop(data)


class Allmovies(Resource):
    def post(self):
        data = request.get_json()
        data = Movie.addMovie(title=data["title"], year=data["year"], genre=data["genre"])
        odata = Movie.jsonmovie(data)
        return odata

    def get(self):
        data = Movie.getmovie()
        odata = Movie.jsonmovie(data)
        return odata


class OneMovieid(Resource):
    def get(self, ids):
        data = Movie.filterbymovieid(ids)
        return data

    def delete(self, ids):
        data = Movie.deletebyid(ids)
        return data

    def put(self, ids):
        data=Movie.updatemovie(ids)
        return data


class OneMovietitle(Resource):
    def get(self, title):
        data = Movie.filterbymoviename(title)
        return data


class Genremovies(Resource):
    def get(self, genres):
        data = Movie.filterbygenre(genres)
        return data

@app.route('/')
def home():
    return render_template('home.html')

api.add_resource(Allmovies, "/movies")
api.add_resource(OneMovieid, "/movies/<int:ids>")
api.add_resource(OneMovietitle, "/movies/<string:title>")
api.add_resource(Genremovies, "/moviesby/<string:genres>")

port = int(os.environ.get('PORT', 5000))

if __name__ == '__main__':
    app.run(port=port)
