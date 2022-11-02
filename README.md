# Description:
This is a recipe API built with **Django**, **Django Rest Framework** and **Python.** The API is dockerized with **Github actions** and workflows. 
The API takes advantage of the Django built-in authentication system and extends it. The default Django login with username and password was replaced with login with email address and password. The API also makes use of the builth in **Django testing suite** to implement testing for the entire codebase. 

For better documentation, the API uses the **Swagger Open API documentation**, although you could still use the default Django Rest Framework API templates. Finally, the API was deployed on **Amazon EC2**, an Amazon AWS service. You can check it out on this url: https://ec2-52-91-166-79.compute-1.amazonaws.com/ If you accessing this link in the future and it's not available, just know that I have deleted or stopped this EC2 instance as I dont want Amazon to be charging me. 🤓
![Recipe API with Swagger and DRF.](https://www.dailywire.ng/wp-content/uploads/2022/11/Recipe-Api-with-User-Authentication.png)

# Getting Started
You can clone or fork this repository. Start with seetting up a virtual environment for your local computer.
Run this code: `python3 -m venv venv`. Start the virtual environment with this command for mac: `source venv/bin/activate`
Since we are working with Docker, we don't even need to setup this virtual env on our local computer. This step should just be skipped. The virtual environment can be deactivated with this code: `deactivate`.

# Working with Docker
![Working with Docker](https://www.memesmonkey.com/images/memesmonkey/ef/ef4435225f1aca10632d610ce506df08.jpeg)
Working with Docker has always made my life easier as a developer. Infact, I am on a holy mission to dockerize all my projects. 😄
When you clone this repository and run it using my Docker, you can be absolutely sure that the whole environment, dependencies, and dev dependencies are available on your machine. To be honest, they are not actually on your machine, they are all contained in the Docker container, so it doesn't matter what dependencies are avaliable on your machine, just use my Docker image that comes with this project and we are good to go.

# Working with Github Actions.
The first time I tried to work with Github Actions, it felt like magic 🥹. Well, in my opinion, it still feels like magic to me. The fact that I can write my code and push it to Github and then all hell is let loose over there amazes me. with very little configuration and using Docker Hub, you are absolutely good to go.

# How to Run this Project using Docker.
Even if you have not used Docker before, you can give this a shot and see how it works. There is no harm in trying right?

## Start Django Application.
To start this Django Application just run this docker command. `docker-compose up`
To stop the Django Application, just run this docker command. `docker-compose down`

# Django Project and Development with Docker.
Because we already have our python image in our docker container, we can simply run this command because Django is already installed in that docker image.

## Start a django project using docker.
Run this command to create a django project in our working directory app.

`docker-compose run --rm app sh -c 'django-admin startproject app .'`


## Create a Django app.
 Now to create apps using docker in our current working directory, all we have to do is to use this command.

`docker-compose run --rm app sh -c "python manage.py startapp name_of_app"`
