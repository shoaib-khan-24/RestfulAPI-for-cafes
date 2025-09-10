from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
from random import choice

API_KEY = "TopSecret"

app = Flask(__name__)

# CREATE DB
class Base(DeclarativeBase):
    pass
# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)

    def to_dict(self):
        my_dict = {}
        for column in self.__table__.columns:
            my_dict[column.name] = getattr(self, column.name)
        return my_dict


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
@app.route("/random", methods=['GET'])
def random():
    all_cafes = db.session.execute(db.select(Cafe).order_by(Cafe.id)).scalars().all()
    random_cafe = choice(all_cafes)
    random_cafe_dict = random_cafe.to_dict()
    return jsonify(cafe=random_cafe_dict)

@app.route("/all", methods=['GET'])
def all():
    all_cafes = db.session.execute(db.select(Cafe).order_by(Cafe.name)).scalars().all()
    return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])

@app.route("/search")
def search():
    my_loc = request.args.get("location")
    cafes_in_location = db.session.execute(db.select(Cafe).where(Cafe.location == my_loc)).scalars().all()
    if len(cafes_in_location) == 0:
        return jsonify(error={"Not Found":"Sorry, we don't have a cafe in that location."}),404
    return jsonify(cafes=[cafe.to_dict() for cafe in cafes_in_location])



# HTTP POST - Create Record
@app.route("/add", methods=['GET', 'POST'])
def add():
    cafe_to_add = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url = request.form.get("img_url"),
        location = request.form.get("location"),
        seats = request.form.get("seats"),
        has_toilet = bool(request.form.get("has_toilet")),
        has_wifi = bool(request.form.get("has_wifi")),
        has_sockets = bool(request.form.get("has_sockets")),
        can_take_calls = bool(request.form.get("can_take_calls")),
        coffee_price = request.form.get("coffee_price")
    )
    db.session.add(cafe_to_add)
    db.session.commit()

    return jsonify(response={
        'success':'Successfully added the new cafe.'
    })


# HTTP PUT/PATCH - Update Record
@app.route("/update_price/<int:cafe_id>", methods=['PATCH'])
def update_price(cafe_id):
    new_price = request.args.get("new_price")
    try:
        cafe_to_update = db.get_or_404(Cafe, cafe_id)
        cafe_to_update.coffee_price = new_price
        db.session.commit()
        return jsonify(response={
            "success" : "Successfully updated the price"
        }),200
    except Exception as e:
        print(e)
        return jsonify(error={"Not found" : "Sorry, no such cafe found with that id in the database."}),404


# HTTP DELETE - Delete Record
@app.route("/report_closed/<int:cafe_id>", methods=['DELETE'])
def delete_cafe(cafe_id):
    user_api_key = request.args.get("api_key")
    try:
        cafe_to_delete = db.get_or_404(Cafe, cafe_id)
    except Exception as e:
        print(e)
        return jsonify(error={"Not found" : "Sorry, no such cafe found with that is in the database."}),404

    if user_api_key != API_KEY:
        return jsonify(error={"Not allowed" : "Enter the correct api-key to make changes in database."}),403

    db.session.delete(cafe_to_delete)
    db.session.commit()
    return jsonify(response={"success" : "Cafe deleted successfully."}),200

if __name__ == '__main__':
    app.run(debug=True)
