import requests
import base64

# правильные запросы
print(requests.get('http://127.0.0.1:8080/api/books/3').json())
print(requests.get('http://127.0.0.1:8080/api/books').json())
print(requests.delete('http://127.0.0.1:8080/api/books/3').json())
data = base64.b64encode(open('static/images/cover.jpg', 'rb').read()).decode('utf-8')
book = {'holder': 3, 'author': 'author', 'title': 'title', 'genre': 'Фэнтези', 'age': '0+', 'cover': 'cover.jpg',
        'data': data}
print(requests.post('http://127.0.0.1:8080/api/books', json=book).json())
params = {'holder': 1}
print(requests.put('http://127.0.0.1:8080/api/books/3', json=params).json())

# get с неправильным запросом
print(requests.get('http://127.0.0.1:8080/api/books/999').json())

# delete с неправильным запросом
print(requests.delete('http://127.0.0.1:8080/api/books/999').json())

# post с неправильным запросом
book = dict()
print(requests.post('http://127.0.0.1:8080/api/books', json=book).json())

# put с неправильным запросом
params = {'cover': '1@1'}
print(requests.put('http://127.0.0.1:8080/api/books/3', json=params).json())
params = {'data': '1@1'}
print(requests.put('http://127.0.0.1:8080/api/books/3', json=params).json())
params = {}
print(requests.put('http://127.0.0.1:8080/api/books/3', json=params).json())
params = {'holder': 12}
print(requests.put('http://127.0.0.1:8080/api/books/3', json=params).json())
