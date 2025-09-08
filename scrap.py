import unittest
from app import app


app.config['TESTING'] = True
client = app.test_client()
response = client.get('/files/ext.ext')
print(response)

status = [
    response.status_code,        # HTTP status code (200, 404, 500, etc.)
    response.status,             # Status as string ("200 OK", "404 NOT FOUND")
    response.is_json,            # Boolean - True if response is JSON
    response.content_type,       # MIME type of the response
    response.mimetype,           # Just the mimetype part (without charset)
    # response.charset, 
]

# for item in status:
#     print(item)

data = [
    # response.data,               # Raw response data as bytes
    # response.get_data(),         # Raw data as bytes (same as .data)
    # response.get_data(as_text=True),  # Data as string with proper encoding
    response.text,               # Response data as text/string
]

for item in data:
    print(item)

headers = [
    # response.headers,            # All headers as a dict-like object
    response.headers.get('Location'),  # Get specific header
    # response.headers['Location'],          # Direct access to header
    # list(response.headers)      # Get all header names
]

for item in headers:
    print(item)

print(get_flashed_messages())

# response.cookies            # Cookie jar with all cookies
# response.set_cookie(...)    # Set a cookie (though rarely used in testing)