# Advanced_Flask_Features
Discover Advanced Features of FLASK


Documnetation LINK -> https://documenter.getpostman.com/view/6411137/SzYT52HJ?version=latest#4e454e0d-225a-49f1-a707-d01f133634e9

Migarion Problem :

Big problem, All the time that I want to make a migration I have a an import module problem.

The solution :

I can see that you solved the problem, but I want to show you the simpler solution than installing flask-script and creating manage.py file. You just have to delete __init__.py file that is at the same level as app.py file. It solved the problem for me. Cheers :)

-> flask db init
-> flask db migrate
-> flask db upgrade


