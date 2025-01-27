from locust import HttpUser, task, between

class Websiteuser(HttpUser):

    grant_permission = True
    blog_number=1
    delete_number=400
    deleted_indices = set()
    added_indices=set()
    cookies={"access_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzM3NzE1MjI2LCJpYXQiOjE3Mzc3MTE2MjYsImp0aSI6Ijk2ZmY0ODIwMWZiYjQ3ODBiNTYwYTE3Y2ViZjEzMjBhIiwidXNlcl9pZCI6Nn0.tbfiB139yXaQpnCk8xjgTTOOFQqHw14p3BfMlewvfB4"
}
    @task(3)
    def get_blogs(self):
        self.client.get('/blog/blogs',cookies=self.cookies)

    @task(2)
    def get_blog1(self):
        self.client.get('/blog/blogs/6')

    @task
    def update_blog6(self):
        data={'title':"new title","content":"new content"}
        self.client.post('/blog/blogs/6/update/',data=data,cookies=self.cookies)

    
    @task(2)
    def create_blog(self):
            data={'title':f"new title {self.blog_number}","content":"new content"}
            self.blog_number+=1
            self.client.post('/blog/blogs/create/',data=data,cookies=self.cookies)

    # @task(4)
    # def delete_blog(self):
    #     if self.delete_number not in self.deleted_indices:
    #         response = self.client.delete(f'/blog/blogs/{self.delete_number}/delete/', cookies=self.cookies)
    #         print(response.status_code, response.text)

    #         if response.status_code == 200: 
    #             self.deleted_indices.add(self.delete_number) 
    #             self.delete_number += 1  
    #         else:
    #             print(f"Failed to delete blog {self.delete_number}: {response.status_code}")
    #     else:
    #         print(f"Blog {self.delete_number} already deleted.")


    @task(3)
    def like_blog(self):
        self.client.put('/blog/blogs/6/like/', cookies=self.cookies)

    @task(3)
    def change_perm(self):
        if self.grant_permission:
            url = '/blog/blogs/6/perm/3/grant/'
        else:
            url = '/blog/blogs/6/perm/3/revoke/'

        self.grant_permission = not self.grant_permission
        self.client.put(url, cookies=self.cookies)