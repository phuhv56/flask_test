install prerequisites pipenv before start

1. pipenv install
2. pipenv run python app.py


Login facebook api: http://localhost:5000/facebook
Login google api: http://localhost:5000/google

Create post: http://localhost:5000/post - method: POST
Header params: token: <token>
Body:
{title: 'Title', content: 'content'}

Get post: http://localhost:5000/post - method: GET

Get post detail: http://localhost:5000/post/<id> - method GET

Get own post: http://localhost:5000/own-post - method GET


Note: Login with facebook to get full access



