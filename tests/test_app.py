import unittest
import shutil
import os
from app import app

class AppTest(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        self.data_path = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(self.data_path, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.data_path, ignore_errors=True)
    
    def create_document(self, name, content=""):
        with open(os.path.join(self.data_path, name), 'w') as file:
            file.write(content)
    
    def test_index(self):
        self.create_document("changes.txt")
        self.create_document("about.md")
        self.create_document("history.txt")

        response = self.client.get('/')
        print(response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "text/html; charset=utf-8")

        self.assertIn('changes.txt', response.text)
        self.assertIn('about.md', response.text)
        self.assertIn('history.txt', response.text)
    
    def test_document_view(self):
        self.create_document("changes.txt", content='There are many changes.')

        with self.client.get(f'/changes.txt') as response:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content_type, "text/plain; charset=utf-8")
            self.assertIn('There are many changes.', response.get_data(as_text=True))
    
    def test_document_not_found(self):
        # Attempt to access a non-existent file and verify a redirect occurs
        with self.client.get('/nonexistant.ext') as response:
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.headers.get('Location'), '/')
        
        # Verify redirect successfully completed and flash message appears
        with self.client.get(response.headers.get('Location')) as response:
            self.assertEqual(response.status_code, 200)
            self.assertIn('nonexistant.ext does not exist', response.get_data(as_text=True))
            
        # Assert that a page reload removes the message
        with self.client.get('/') as response:
            self.assertEqual(response.status_code, 200)
            self.assertNotIn('nonexistant.ext does not exist', response.get_data(as_text=True))

    def test_markdown_document_view(self):
        self.create_document("about.md", content='# Python is...')

        response = self.client.get('/about.md')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "text/html; charset=utf-8")
        self.assertIn("<h1>Python is...</h1>", response.get_data(as_text=True))

    def test_edit_file(self):
        self.create_document("changes.txt")

        response = self.client.get('/changes.txt/edit')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "text/html; charset=utf-8")
        self.assertIn("<textarea", response.text)
        self.assertIn('<button type="submit"', response.text)

    def test_submit_changes(self):
        with self.client.post('/changes.txt', data={'content': "There are many changes. New content."}) as response:
            self.assertEqual(response.status_code, 302)

        follow_response = self.client.get(response.headers['Location'])
        self.assertIn("changes.txt has been edited", follow_response.get_data(as_text=True))

        with self.client.get("/changes.txt") as content_response:
            self.assertEqual(content_response.status_code, 200)
            self.assertIn("New content.", content_response.get_data(as_text=True))
    
    def test_new_document_form(self):
        response = self.client.get('/new')
        self.assertEqual(response.status_code, 200)
        self.assertIn("<input ", response.text)
        self.assertIn("<button type=", response.text)
    
    def test_create_new_document(self):
        response = self.client.post('/create', 
                                    data={'document_name': 'test_file.txt'},
                                    follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('test_file.txt was created successfully', response.get_data(as_text=True))
        
        response = self.client.get('/')
        print(response)
        self.assertIn('test_file.txt', response.get_data(as_text=True))

    def test_create_new_document_without_name(self):
        response = self.client.post('/create', data={'document_name': ''})
        self.assertEqual(response.status_code, 422)
        self.assertIn("A name is required.", response.get_data(as_text=True))

if __name__ == "__main__":
    unittest.main()