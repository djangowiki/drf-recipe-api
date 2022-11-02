# Description:
This is a recipe API built with Django, DRF and Python. The API is dockerized with Github actions and workflows. 
The API takes advantage of the Django built-in authentication system and extends it. The default Django login with username and password was replaced with login with email address and password. The API also makes use of the builth in Django testing suite to implement testing for the entire codebase. For better documentation, the API uses the Swagger Open API documentation, although you could still use the default Django Rest Framework API templates. Finally, the API was deployed on Amazon EC2, an Amazon AWS service. You can check it out on this url: https://ec2-52-91-166-79.compute-1.amazonaws.com/ If you accessing this link in the future and it's not available, just know that I have deleted or stopped this EC2 instance as I dont want Amazon to be charging me. 🤓
![Recipe API with Swagger and DRF.](https://www.dailywire.ng/wp-content/uploads/2022/11/Recipe-Api-with-User-Authentication.png)

# Getting Started
You can clone or fork this repository. Start with seetting up a virtual environment for your local computer.
Run this code: `python3 -m venv venv`. Start the virtual environment with this command for mac: `source venv/bin/activate`
Since we are working with Docker, we don't even need to setup this requirement we have a virtual env on the local computer. This step should just be skipped. The virtual environment can be deactivated with this code: `deactivate`.

# Working with Docker
![Working with Docker](https://www.memesmonkey.com/images/memesmonkey/ef/ef4435225f1aca10632d610ce506df08.jpeg)
