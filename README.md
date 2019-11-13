# ChainMore-API-Flask
The API backend of ChainMore based on Flask.

## API

| Resource                         | Method | Description |
| ---                              | ---    | ---         |
| v1/auth/signup                   | POST   | Sign up     |
| v1/auth/signin                   | POST   | Sign in     |
| v1/auth/signout                  | POST   | Sign out    |
| v1/post                          | GET    | Get posts by query |
| v1/post                          | POST   | Create a new post |
| v1/post/<post_id>                | GET    | Get the detailed post |
| v1/post/<post_id>                | DELETE | Delete a post |
| v1/post/<post_id>                | PUT    | Modify a post |
| v1/post/<post_id>/comment        | POST   | Create a new comment |
| v1/post/<post_id>/comment        | GET    | Get comments of the post |
| v1/post/<post_id>/like           | POST   | Create a new like |
| v1/post/<post_id>/like           | DELETE | Unlike |
| v1/post/<post_id>/collect        | POST   | Create a collect |
| v1/post/<post_id>/collect        | DELETE | Uncollect |
| v1/comment/<comment_id>          | GET    | Get the comment |
| v1/comment/<comment_id>          | PUT    | Update the comment |
| v1/comment/<comment_id>          | DELETE | Delete the comment |
| v1/comment/<comment_id>/vote     | POST   | Vote the comment |
| v1/comment/<comment_id>/vote     | DELETE | Unvote the comment |
| v1/domain                        | POST   | Create a domain |
| v1/domain/<domain_id>            | GET    | Get a domain |
| v1/domain/<domain_id>/watch      | POST   | Watch a domain |
| v1/domain/<domain_id>/watch      | DELETE | Unwatch a domain |
| v1/user/<username>               | GET    | Get user info |
| v1/user/<username>/follow        | POST   | Follow a user |
| v1/user/<username>/follow        | DELETE | Unfollow a user |
| v1/search                        | GET    | Search by query |



## Permission

User permission:
* ACCESS: For all users.
* NOTICE: For registered users.
* PARTICIPATE: For he who satisfy the dependency.
* MANAGE: For he who get the authentication.
* MODERATE: Preserved.
* ADMIN: 

## Model

```
User
Domain
Post
Comment
Role /* v0.2 */

Permission /* v0.2 */
Category

Domain     <--  Contain            --> Post
Role       <--  roles_permissions  --> Permission /* v0.2 */
Post       <--                     --> Category
Domain     <--  Depend             --> Domain /* v0.2 */
Domain     <--  Authenticate       --> User /* v0.2 */
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
