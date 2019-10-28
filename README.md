# ChainMore-API-Flask
The API backend of ChainMore based on Flask.

## API

| Resource                  | Method | Description |
| ---                       | ---    | ---         |
| v1/auth/signup            | POST   | Sign up     |
| v1/auth/signin            | POST   | Sign in     |
| v1/auth/signout           | POST   | Sign out    |
| v1/resource               | GET    | Get resources by query |
| v1/resource               | PUT    | Post a new resource |
| v1/resource/<resource_id> | GET    | Get a resource (Full details and comments) |
| v1/resource/<resource_id> | DELETE | Delete a resource |
| v1/resource/<resource_id> | POST   | Modify a resource |
| v1/domain                 | PUT    | Create a domain   |
| v1/domain/<domain_id>     | GET    | Get a domain |
| v1/user/<username>        | GET    | Get user info |
| v1/search                 | GET    | Search by query |

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
Resource
Comment
Role /* v0.2 */

Permission /* v0.2 */
Category

Domain     <--  Contain            --> Resource
Role       <--  roles_permissions  --> Permission /* v0.2 */
Resource   <--                     --> Category
Domain     <--  Depend             --> Domain /* v0.2 */
Domain     <--  Authenticate       --> User /* v0.2 */

```