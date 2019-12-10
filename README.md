# ChainMore-API-Flask
The API backend of ChainMore based on Flask.

## API

| Resource                          | Method | Params | Description |
| ---                               | ---    | ---    | ---         |
| /v1/auth/signup                   | POST   |        | Sign up     |
| /v1/auth/signin                   | POST   |        | Sign in     |
| /v1/auth/signout                  | POST   |        | Sign out    |
| /v1/post                          | GET    | id     | Get a post by query |
| /v1/post                          | PUT    | id     | Modify a post |
| /v1/post                          | DELETE | id     | Delete a post |
| /v1/post                          | POST   |        | Create a new post |
| /v1/post/<post_id>                | GET    |        | Get the detailed post |
| /v1/post/<post_id>                | DELETE |        | Delete a post |
| /v1/post/<post_id>                | PUT    |        | Modify a post |
| /v1/post/comment                  | POST   | id, reply     | Create a new comment under post<id>, reply to comment<reply>|
| /v1/post/comment                  | GET    | id, offset, limit | Get comments of the post<id> |
| /v1/post/<post_id>/comment        | POST   |        | Create a new comment |
| /v1/post/<post_id>/comment        | GET    |        | Get comments of the post |
| /v1/post/like                     | POST   | id     | Create a new like for post<id> |
| /v1/post/like                     | DELETE | id     | Unlike post<id> |
| /v1/post/<post_id>/like           | POST   |        | Create a new like |
| /v1/post/<post_id>/like           | DELETE |        | Unlike |
| /v1/post/collect                  | POST   | id     | Collect the post<id> |
| /v1/post/collect                  | DELETE | id     | Uncollect post<id> |
| /v1/post/<post_id>/collect        | POST   |        | Create a collect |
| /v1/post/<post_id>/collect        | DELETE |        | Uncollect |
| /v1/comment/<comment_id>          | GET    |        | Get the comment |
| /v1/comment/<comment_id>          | PUT    |        | Update the comment |
| /v1/comment/<comment_id>          | DELETE |        | Delete the comment |
| /v1/comment/<comment_id>/vote     | POST   |        | Vote the comment |
| /v1/comment/<comment_id>/vote     | DELETE |        | Unvote the comment |
| /v1/comment/vote                  | POST   | id     | Vote the comment |
| /v1/comment/vote                  | DELETE | id     | Unvote the comment |
| /v1/comment/against               | POST   | id     | Against the comment |
| /v1/comment/against               | DELETE | id     | Cancel againsting the comment |
| /v1/domain                        | POST   |        | Create a domain |
| /v1/domain                        | GET    | id     | Get the details of the domain<id> |
| /v1/domain/<domain_id>            | GET    |        | Get a domain |
| /v1/domain/watch                  | POST   | id     | Watch a domain |
| /v1/domain/watch                  | DELETE | id     | Unwatch a domain |
| /v1/domain/<domain_id>/watch      | POST   |        | Watch a domain |
| /v1/domain/<domain_id>/watch      | DELETE |        | Unwatch a domain |
| /v1/domain/certify                | GET    | id     | Return tests |     
| /v1/domain/post                   | GET    | id, offset, limit | Get Posts of the domain<id> |
| /v1/user/<username>               | GET    |        | Get user info |
| /v1/user/<username>/follow        | POST   |        | Follow a user |
| /v1/user/<username>/follow        | DELETE |        | Unfollow a user |
| /v1/search                        | GET    | query, type, offset, limit | Search type by query |
| /v1/search/hot                    | GET    |        | Get the hot search query, update per day |
| /v1/search/recommend              | GET    | query   | Provide search recommends |


## Permission

User permission:
* ACCESS: For all users.
* NOTICE: For registered users.
* PARTICIPATE: For he who satisfy the dependency.
* MANAGE: For he who get the authentication.
* MODERATE: Preserved.
* ADMIN: Preserved.

## Credit

## 

## Model

```
User
Domain
Post
Comment
Role 
Permission 
Category

Domain     <--  Contain            --> Post
Role       <--  roles_permissions  --> Permission
Post       <--                     --> Category
Domain     <--  Depend             --> Domain
Domain     <--  Authenticate       --> User
User       <--  Watch              --> Domain
User       <--  Follow             --> User

```

## Wheels
- [x] Flask
- [x] JWT
- [x] SQLAlchemy
- [x] Whooshe
- [x] Blueprint
- [x] Restful-API
