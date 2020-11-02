import json
import os
from flask import (
    Flask,
    request,
    jsonify,
    abort
)
from flask_cors import CORS
from sqlalchemy import exc
from .auth.auth import (
    AuthError,
    requires_auth
)
from .database.models import (
    db_drop_and_create_all,
    setup_db, Drink
)

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
        returns status code 200 and json {"success": True, "drinks": drinks}
        where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['GET'])
def get_drinks():
    try:
        menu = []
        drinks = Drink.query.all()
        for i in drinks:
            menu.append(i.short())
        return jsonify({
            'success': True,
            'drinks': menu
        }), 200
    except BaseException:
        abort(422)


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drinks}
        where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail', methods=['GET'])
@requires_auth("get:drinks-detail")
def get_drinks_detail(payload):
    try:
        recipe = []
        alldrinks = Drink.query.all()
        for i in alldrinks:
            recipe.append(i.long())
        return jsonify({
            'success': True,
            'drinks': recipe
        }), 200
    except BaseException:
        abort(404)


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drink}
        where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth("post:drinks")
def post_drinks(payload):
    body = request.get_json()
    title = body.get('title', None)
    if isinstance(body.get('recipe'), str):
        recipe = body.get('recipe')
    else:
        recipe = json.dumps(body.get('recipe'))
    try:
        drink = Drink(
            title=title,
            recipe=recipe
        )
        drink.insert()
        return jsonify(
            {'success': True,
             'drinks': drink.long()
             }, 200
        )
    except BaseException:
        abort(422)


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drink}
        where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth("patch:drinks")
def patch_drinks(payload, id):
    # drink from db and display
    drink = Drink.query.filter(Drink.id == id).first()
    if not drink:
        abort(404)
    body = request.get_json()
    title = body.get('title', None)
    recipe = body.get('recipe', None)
    # get new data
    try:
        drink.title = json.dumps(title)
        drink.recipe = json.dumps(recipe)
    # update in db
        drink.update()
        return jsonify(
            {"success": True,
             "drinks": [drink.long()]}
        ), 200
    except BaseException:
        abort(422)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
        returns status code 200 and json {"success": True, "delete": id}
        where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth("delete:drinks")
def delete_drinks(payload, id):
    error = False
    try:
        drink = Drink.query.filter(Drink.id == id).first()
        drink.delete()
        if error:
            abort(500)
        else:
            return jsonify({
                'success': True,
                'delete': id
            }), 200
    except BaseException:
        abort(422)


# Error Handling

@app.errorhandler(400)
def bad_request_error(error):
    print('debug')
    print(error)
    return jsonify({
        'success': False,
        'error': 400,
        'message': "Bad Request"
    }), 400


@app.errorhandler(401)
def unauthorized_error(error):
    return jsonify({
        'success': False,
        'error': 401,
        'message': "Unauthorized"
    }), 401


@app.errorhandler(403)
def forbidden_error(error):
    return jsonify({
        'success': False,
        'error': 403,
        'message': "Forbidden"
    }), 403


@app.errorhandler(404)
def not_found_error(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': "Ressource Not Found"
    }), 404


@app.errorhandler(405)
def invalid_method_error(error):
    return jsonify({
        'success': False,
        'error': 405,
        'message': "Invalid Method"
    }), 405


@app.errorhandler(409)
def duplicate_resource_error(error):
    return jsonify({
        'success': False,
        'error': 409,
        'message': "Duplicate Resource"
    }), 409


@app.errorhandler(422)
def not_processable_error(error):
    return jsonify({
        'success': False,
        'error': 422,
        'message': "Not Processable"
    }), 422


@app.errorhandler(500)
def server_error(error):
    return jsonify({
        'success': False,
        'error': 500,
        'message': "Server Error"
    }), 500


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''


@app.errorhandler(AuthError)
def handle_auth_error(ex):
    """
    Unauthorized error handler to avoid 500 error when authorization is missing
    """
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response
