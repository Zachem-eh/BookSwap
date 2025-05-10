import requests

# правильные запросы
print(requests.get('http://127.0.0.1:8080/api/books/3').json())
print(requests.get('http://127.0.0.1:8080/api/books').json())
print(requests.delete('http://127.0.0.1:8080/api/books/2').json())
book = {'holder': 1, 'author': 'author', 'title': 'title', 'genre': 'Фэнтези', 'age': '0+', 'cover': 'cover.jpg'}
print(requests.post('http://127.0.0.1:8080/api/books', json=book).json())
params = {'title': 'title'}
print(requests.put('http://127.0.0.1:8080/api/books/3', json=params).json())

# get с неправильным запросом
print(requests.get('http://127.0.0.1:8080/api/books/999').json())

# delete с неправильным запросом
print(requests.delete('http://127.0.0.1:8080/api/books/999').json())

# post с неправильным запросом
book = dict()
print(requests.post('http://127.0.0.1:8080/api/books', json=book).json())

# put с неправильным запросом
params = {'email': '1@1'}
print(requests.put('http://127.0.0.1:8080/api/books/3', json=params).json())
params = {'password': '1@1'}
print(requests.put('http://127.0.0.1:8080/api/books/3', json=params).json())
params = {}
print(requests.put('http://127.0.0.1:8080/api/books/3', json=params).json())
