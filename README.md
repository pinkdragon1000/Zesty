# Zesty

* [View the Figma mockups here](https://www.figma.com/file/rKCVOp70tLCvjTWdO5pVeW/Recipe?node-id=0%3A1)

**My Setup**

Hosted on a Google Cloud VM instance running using Debian and a g1-small (1 vCPU, 1.7 GB memory) machine type.

![](/static/styles/Screenshot1.png)
![](/static/styles/Screenshot2.png)
![](/static/styles/Screenshot3.png)

**Running the Program Locally**

* Follow the instructions here to create a virtual environment: https://flask.palletsprojects.com/en/1.1.x/installation/
* Create the database schema as described here: https://github.com/pinkdragon1000/Zesty/blob/master/database.sql

Folder Structure
```
├── venv
|    └── ...
├── Zesty (this repo)
|    └── routes.py
|    └── static/
|    └── templates/

```
After the installation of MariaDB, the database information can be configured at the top of routes.py via this snipppet.  

```
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'zesty_user'
app.config['MYSQL_PASSWORD'] = 'Z3$tyU$3r54'
app.config['MYSQL_DB'] = 'Zesty'
mysql = MySQL(app)
```

Here is a shell script I used to run the application in my environment.  Change the paths for your machine: 
```
#!/bin/bash
killall flask
cd /home/sitar/zesty_app
source venv/bin/activate
cd /home/sitar/zesty_app/Zesty
export set FLASK_ENV=development
export set FLASK_APP=routes.py
flask run --host=0.0.0.0 --port=5000
```

