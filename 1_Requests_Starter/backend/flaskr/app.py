import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy  # , or_
from flask_cors import CORS
import random

from models import setup_db, Book

BOOKS_PER_SHELF = 8


def paginated_pages(request):

    page = request.args.get('page', 1, type=int)
    start = (page - 1) * BOOKS_PER_SHELF
    end = start + BOOKS_PER_SHELF
    books = Book.query.order_by(Book.id).all()
    paginated_books = [book.format() for book in books]
    return paginated_books[start:end]


def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    # CORS Headers

    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    # TEST: When completed, the webpage will display books including title, author, and rating shown as stars

    @app.route('/')
    def books():
        current_books = paginated_pages(request)
        if len(current_books) == 0:
            abort(404)
        return jsonify({
            "success": True,
            "books": current_books,
            "total_books": len(Book.query.all())
        })

    @app.route('/books/<int:id>', methods=['PATCH'])
    def update_rating(id):
        body = request.get_json()
        if body is None:
            abort(400)
        try:
            book = Book.query.get(id)

            if "rating" in body:
                rating = int(body.get('rating'))
                book.rating = rating
            book.update()
        except:
            abort(404)

        return jsonify({
            "success": True,
            "id": id,
            "books": paginated_pages(request)
        })

    # TEST: When completed, you will be able to click on stars to update a book's rating and it will persist after refresh

    @app.route('/books/<int:id>', methods=["DELETE"])
    def delete_book(id):
        try:
            book = Book.query.filter(Book.id == id).one_or_none()
            book.delete()
        except:
            abort(422)

        return jsonify({
            'success': True,
            'deleted': id,
            'books': paginated_pages(request),
            'total_books': len(Book.query.all())
        })
    # TEST: When completed, you will be able to delete a single book by clicking on the trashcan.

    # TEST: When completed, you will be able to a new book using the form. Try doing so from the last page of books.
    #       Your new book should show up immediately after you submit it at the end of the page.

    @app.route('/books', methods=['POST'])
    def create_new_book():
        body = request.get_json()
        if body == None:
            abort(422)
        new_title = body.get("title", None)
        new_author = body.get("author", None)
        new_rating = body.get("rating", None)

        try:
            book = Book(title=new_title, author=new_author, rating=new_rating)
            book.insert()
        except:
            abort(422)

        return jsonify({
            "success": True,
            "created": book.id,
            "books": paginated_pages(request),
            "total_books": len(Book.query.all())
        })

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad Request"
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Resource Not Found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable request"
        }), 422

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "method not allowed"
        }), 405

    return app
