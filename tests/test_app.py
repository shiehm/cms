import unittest
from app import app

class AppTest(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_index(self):
        response = self.client.get('/')
        print(response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "text/html; charset=utf-8")

        self.assertIn('changes.txt', response.text)
        self.assertIn('about.md', response.text)
        self.assertIn('history.txt', response.text)
    
    def test_document_view(self):
        with self.client.get(f'/files/changes.txt') as response:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content_type, "text/plain; charset=utf-8")
            self.assertIn('There are many changes.', response.get_data(as_text=True))
    
    def test_document_not_found(self):
        # Attempt to access a non-existent file and verify a redirect occurs
        with self.client.get('/files/nonexistant.ext') as response:
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
        response = self.client.get('/files/about.md')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "text/html; charset=utf-8")
        self.assertIn("<h1>Python is...</h1>", response.get_data(as_text=True))

if __name__ == "__main__":
    unittest.main()