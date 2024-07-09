# An application for working with a collection of memes

### Setting up your work environment.  
To work with this repository, you will need:
1. Docker
2. Docker-compose

### To get started, you need:
1. Clone this repository:
  ```bash
  git clone git@github.com:DziumovS/fastapi_s3_testapp.git
  ```
2. Move to directory with app:
  ```bash
  cd fastapi_s3_testapp
  ```
3. And then run command:
  ```bash
  docker compose up -d
  ```

As a result, 4 containers will be deployed: with private service, with public service, with MinIO, with postgresql database.

---
### The public service
- will be available here: `http://0.0.0.0:8002`
- functionality:  
● `GET` `/memes`: Get a list of all memes (with pagination)  
● `GET` `/memes/{id}`: Get a specific meme by its ID  
● `POST` `/memes`: Add a new meme (with picture and text)  
● `PUT` `/memes/{id}`: Update an existing meme  
● `DELETE` `/memes/{id}`: Delete a meme by its ID  

### The private service
- will be available here: `http://0.0.0.0:8001`
- functionality:  
● `POST` `/`: Add a new meme to MinIO "storage"  
● `PUT` `/`: Update an existing meme  
● `DELETE` `/{filename}`: Delete a meme by its filename  

---
Documentation is "done" using the OpenAPI included in FastAPI.

To run unit-tests, just run the `pytest` command in the root directory of the application.

--- 
  
<details>

This is the first time I've tried using "mock" in general, don't be discouraged.  
I also didn't bother with creating a user for MinIO, creating access key and secret key for it and then passing them to the "client".  
After deleting containers, `don't forget to delete postgres and minIO volumes`.
</details>