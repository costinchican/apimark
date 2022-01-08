from flask import Flask
from flask_restful import Api, Resource, reqparse, abort
from pymongo import MongoClient

conn = "mongodb+srv://ctnxatv:vwren2020@ctnxatv.rzjil.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
app = Flask(__name__)
api = Api(app)
app.config['MONGODB_HOST'] = conn
mongo = MongoClient(conn)
apimark = mongo["apimark"]
listings = apimark["listings"]
users = apimark["users"]


user_post_args = reqparse.RequestParser()
user_post_args.add_argument("firstname", type=str, help="Firstname of user required", required=True)
user_post_args.add_argument("lastname", type=str, help="Lastname of user required", required=True)
user_post_args.add_argument("age", type=int, help="Age of user required", required=True)
user_post_args.add_argument("city", type=str, help="City of user required", required=True)

user_patch_args = reqparse.RequestParser()
user_patch_args.add_argument("firstname", type=str, help="Firstname must be string")
user_patch_args.add_argument("lastname", type=str, help="Lastname must be string")
user_patch_args.add_argument("age", type=int, help="Age must be integer")
user_patch_args.add_argument("city", type=str, help="City must be string")


class User(Resource):

    def post(self, user_id):
        result = users.find_one({"_id": user_id})
        if result:
            abort(409, message="User ID is taken.")
        user_args = user_post_args.parse_args()
        user = {"_id": user_id, "firstname": user_args["firstname"],
                "lastname": user_args["lastname"], "age": user_args["age"],
                "city": user_args["city"], "keywords": " "}
        users.insert_one(user)
        return user, 201

    def get(self, user_id):
        result = users.find_one({"_id": user_id})
        if not result:
            abort(404, message="User Not Found")
        user = {"_id": user_id, "firstname": result["firstname"],
                "lastname": result["lastname"], "age": result["age"],
                "city": result["city"], "keywords": result["keywords"]
                }

        return user, 200

    def put(self, user_id):
        result = users.find_one({"_id": user_id})
        if not result:
            abort(404, message="User Not Found")
        user_args = user_post_args.parse_args()
        user = {"_id": user_id, "firstname": user_args["firstname"],
                "lastname": user_args["lastname"], "age": user_args["age"],
                "city": user_args["city"], "keywords": " "}
        users.replace_one({"_id": user_id}, user)
        return user, 201

    def patch(self, user_id):
        result = users.find_one({"_id": user_id})
        if not result:
            abort(404, message="User Not Found")
        user_args = user_patch_args.parse_args()
        user_args = {k: v for k, v in user_args.items() if v}
        users.update_one({"_id": user_id}, {"$set": user_args})
        user = users.find_one({"_id": user_id})
        return user, 200

    def delete(self, user_id):
        result = users.find_one({"_id": user_id})
        if not result:
            abort(404, message="User Not Found")
        users.delete_one({"_id": user_id})
        return f"User with id = {user_id} deleted", 204


listing_post_args = reqparse.RequestParser()
listing_post_args.add_argument("title", type=str, help="Title of listing required", required=True)
listing_post_args.add_argument("category", type=str, help="Category of listing required", required=True)
listing_post_args.add_argument("description", type=str, help="Description of listing required", required=True)
listing_post_args.add_argument("price", type=int, help="Price of listing required", required=True)
listing_post_args.add_argument("keyword", type=str, help="Keyword of listing required", required=True)

listing_patch_args = reqparse.RequestParser()
listing_patch_args.add_argument("title", type=str, help="Title must be string")
listing_patch_args.add_argument("category", type=str, help="Category must be string")
listing_patch_args.add_argument("description", type=str, help="Description must be string")
listing_patch_args.add_argument("price", type=int, help="Price must be int")
listing_patch_args.add_argument("keyword", type=str, help="Keyword must be string")


class Listing(Resource):

    def post(self, listing_id):
        result = listings.find_one({"_id": listing_id})
        if result:
            abort(409, message="Listing ID is taken.")
        listing_args = listing_post_args.parse_args()
        listing = {"_id": listing_id, "title": listing_args["title"],
                   "category": listing_args["category"], "description": listing_args["description"],
                   "price": listing_args["price"], "keyword": listing_args["keyword"]}
        listings.insert_one(listing)
        return listing, 201

    def get(self, listing_id, user_id=0):
        result = listings.find_one({"_id": listing_id})
        if not result:
            abort(404, message="Listing Not Found")
        listing = {"_id": listing_id, "title": result["title"],
                   "category": result["category"], "description": result["description"],
                   "price": result["price"], "keyword": result["keyword"]
                   }

        users.update_one({"_id": user_id}, {"$set": {"keywords": result["keyword"]}})

        return listing, 200

    def put(self, listing_id):
        result = listings.find_one({"_id": listing_id})
        if not result:
            abort(404, message="Listing Not Found")
        listing_args = listing_post_args.parse_args()
        listing = {"_id": listing_id, "title": listing_args["title"],
                   "category": listing_args["category"], "description": listing_args["description"],
                   "price": listing_args["price"], "keyword": listing_args["keyword"]
                   }
        listings.replace_one({"_id": listing_id}, listing)
        return listing, 201

    def patch(self, listing_id):
        result = listings.find_one({"_id": listing_id})
        if not result:
            abort(404, message="Listing Not Found")
        listing_args = listing_patch_args.parse_args()
        listing_args = {k: v for k, v in listing_args.items() if v}
        listings.update_one({"_id": listing_id}, {"$set": listing_args})
        listing = listings.find_one({"_id": listing_id})
        return listing, 200

    def delete(self, listing_id):
        result = listings.find_one({"_id": listing_id})
        if not result:
            abort(404, message="Listing Not Found")
        listings.delete_one({"_id": listing_id})
        return f"Listing with id = {listing_id} deleted", 204


class Suggestions(Resource):

    def get(self, user_id):
        user = users.find_one({"_id": user_id})
        if not user:
            abort(404, message="User Not Found")
        results = listings.find({"keyword": user["keywords"]})
        r = []
        for res in results:
            result = {"_id": res["_id"], "title": res["title"],
                      "category": res["category"], "description": res["description"],
                      "price": res["price"], "keyword": res["keyword"]
                      }
            r.append(result)
        return r, 200

@app.route("/")
def index():
    return "<p>Welcome to Apimark - Try Our Resources: </br></br> /user/[user_id] </br> /listing/[listing_id]/[" \
           "user_id] </br> /suggestions/[user_id]</p> "

api.add_resource(User, "/user/<int:user_id>")
api.add_resource(Listing, "/listing/<int:listing_id>", "/listing/<int:listing_id>/<int:user_id>")
api.add_resource(Suggestions, "/suggestions/<int:user_id>")

if __name__ == '__main__':
    app.run(host='0.0.0.0')
