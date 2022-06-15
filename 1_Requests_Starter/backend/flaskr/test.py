import unittest
import json
from venv import create
from app import create_app
from models import setup_db, Book


class bookshelf_testCase(unittest.TestCase):
    def setup(self):
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "test_db"
        self.database_path = "postgres://{}/{}".format(
            'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

    def tearDown(self):
        """Executed after each test"""
        pass

    def test_get_paginated_books(self):
        res = create_app().test_client().get('/')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["books"]))
        self.assertTrue(data["total_books"])

    def test_404_page_notfound(self):
        res = create_app().test_client().get('/?page=1000', json={"rating": 1})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["error"], 404)
        self.assertEqual(data["message"], "Resource Not Found")

    def test_update_rating(self):
        res = create_app().test_client().patch(
            '/books/3', json={"rating": "3"})
        data = json.loads(res.data)
        book = Book.query.filter(Book.id == 3).one_or_none()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(book.format()["rating"], 3)
        self.assertTrue(len(data["books"]))

    def test_400_failed_update(self):
        res = create_app().test_client().patch('/books/3')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Bad Request")

    # def test_delete_book(self):
    #     res = create_app().test_client().delete('/books/6')
    #     data = json.loads(res.data)
    #     book = Book.query.filter(Book.id == 9).one_or_none()
    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(data["success"], True)
    #     self.assertEqual(data["deleted"], 9)
    #     self.assertEqual(book, None)
    #     self.assertTrue(data["total_books"])
    #     self.assertTrue(len(data["books"]))

    # def test_422_if_book_does_not_exist(self):
    #     res = create_app().test_client().delete('/books/1000')
    #     data = json.loads(res.data)
    #     self.assertEqual(res.status_code, 422)
    #     self.assertEqual(data["success"], False)
    #     self.assertEqual(data["error"], 422)
    #     self.assertEqual(data["message"], "unprocessable request")

    # def test_create_new_book(self):
    #     res = create_app().test_client().post(
    #         '/books', json={"title": "Da Vinci Code", "author": "Dan Brown", "rating": "5"})
    #     data = json.loads(res.data)
    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(data["success"], True)
    #     self.assertTrue(data['created'])
    #     self.assertTrue(len(data["books"]))

    def test_405_if_book_creation_not_allowed(self):
        res = create_app().test_client().post('/books/9')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["error"], 405)
        self.assertEqual(data["message"], "method not allowed")


if __name__ == "__main__":
    unittest.main()
