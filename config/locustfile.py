from locust import  HttpUser, task, between
from faker import Faker

fake=Faker()



class SignupUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def signup(self):
        self.client.post("/api/v1/auth/Login/", json={
            "email":"ashdcu2dd252004@gmail.com",
            "password":"Ashu2252004"
      
            
        })
   