import os
import strawberry
from strawberry.fastapi import GraphQLRouter
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from decimal import Decimal

# Database connection
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://admin:password123@db:5432/graphql_db")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

# Strawberry types
@strawberry.type
class User:
    id: int
    username: str
    email: str
    password: str  # VULN: Exposing password in schema
    role: str
    is_active: bool
    salary: Optional[float]  # VULN: Exposing sensitive salary data
    ssn: Optional[str]  # VULN: Exposing SSN
    created_at: str

@strawberry.type
class Post:
    id: int
    title: str
    content: str
    author_id: int
    is_published: bool
    is_private: bool  # VULN: Private flag exposed
    created_at: str

@strawberry.type
class Comment:
    id: int
    content: str
    post_id: int
    author_id: int
    created_at: str

@strawberry.type
class Product:
    id: int
    name: str
    description: Optional[str]
    price: float
    stock: int
    is_available: bool
    created_at: str

@strawberry.type
class Order:
    id: int
    user_id: int
    product_id: int
    quantity: int
    total_price: float
    status: str
    created_at: str

@strawberry.type
class Message:
    id: int
    from_user_id: int
    to_user_id: int
    content: str
    is_read: bool
    created_at: str

@strawberry.type
class SuccessResponse:
    success: bool
    message: str
    id: Optional[int] = None

# Queries
@strawberry.type
class Query:
    # VULN: No authentication checks on any queries
    # VULN: No query depth limiting
    # VULN: No query complexity limiting
    
    @strawberry.field
    def user(self, id: int) -> Optional[User]:
        """Get user by ID - VULN: No authorization check"""
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM users WHERE id = %s", (id,))
        result = cur.fetchone()
        cur.close()
        conn.close()
        if result:
            result['created_at'] = str(result['created_at'])
            return User(**result)
        return None
    
    @strawberry.field
    def users(self, limit: Optional[int] = 100) -> List[User]:
        """Get all users - VULN: No pagination limits, returns sensitive data"""
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(f"SELECT * FROM users LIMIT {limit}")  # VULN: SQL injection via limit
        results = cur.fetchall()
        cur.close()
        conn.close()
        return [User(**{**r, 'created_at': str(r['created_at'])}) for r in results]
    
    @strawberry.field
    def user_by_username(self, username: str) -> Optional[User]:
        """Search user by username - VULN: SQL injection"""
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        # VULN: Direct string interpolation leads to SQL injection
        query = f"SELECT * FROM users WHERE username = '{username}'"
        cur.execute(query)
        result = cur.fetchone()
        cur.close()
        conn.close()
        if result:
            result['created_at'] = str(result['created_at'])
            return User(**result)
        return None
    
    @strawberry.field
    def post(self, id: int) -> Optional[Post]:
        """Get post by ID - VULN: Returns private posts without auth check"""
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM posts WHERE id = %s", (id,))
        result = cur.fetchone()
        cur.close()
        conn.close()
        if result:
            result['created_at'] = str(result['created_at'])
            return Post(**result)
        return None
    
    @strawberry.field
    def posts(self, author_id: Optional[int] = None) -> List[Post]:
        """Get all posts - VULN: Returns unpublished and private posts"""
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        if author_id:
            cur.execute("SELECT * FROM posts WHERE author_id = %s", (author_id,))
        else:
            cur.execute("SELECT * FROM posts")
        results = cur.fetchall()
        cur.close()
        conn.close()
        return [Post(**{**r, 'created_at': str(r['created_at'])}) for r in results]
    
    @strawberry.field
    def comments(self, post_id: int) -> List[Comment]:
        """Get comments for a post"""
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM comments WHERE post_id = %s", (post_id,))
        results = cur.fetchall()
        cur.close()
        conn.close()
        return [Comment(**{**r, 'created_at': str(r['created_at'])}) for r in results]
    
    @strawberry.field
    def product(self, id: int) -> Optional[Product]:
        """Get product by ID"""
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM products WHERE id = %s", (id,))
        result = cur.fetchone()
        cur.close()
        conn.close()
        if result:
            result['created_at'] = str(result['created_at'])
            result['price'] = float(result['price'])
            return Product(**result)
        return None
    
    @strawberry.field
    def products(self) -> List[Product]:
        """Get all products"""
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM products")
        results = cur.fetchall()
        cur.close()
        conn.close()
        return [Product(**{**r, 'created_at': str(r['created_at']), 'price': float(r['price'])}) for r in results]
    
    @strawberry.field
    def order(self, id: int) -> Optional[Order]:
        """Get order by ID - VULN: No authorization, can view any user's orders"""
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM orders WHERE id = %s", (id,))
        result = cur.fetchone()
        cur.close()
        conn.close()
        if result:
            result['created_at'] = str(result['created_at'])
            result['total_price'] = float(result['total_price'])
            return Order(**result)
        return None
    
    @strawberry.field
    def orders(self, user_id: Optional[int] = None) -> List[Order]:
        """Get orders - VULN: Can query any user's orders without auth"""
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        if user_id:
            cur.execute("SELECT * FROM orders WHERE user_id = %s", (user_id,))
        else:
            cur.execute("SELECT * FROM orders")
        results = cur.fetchall()
        cur.close()
        conn.close()
        return [Order(**{**r, 'created_at': str(r['created_at']), 'total_price': float(r['total_price'])}) for r in results]
    
    @strawberry.field
    def messages(self, user_id: int) -> List[Message]:
        """Get messages for user - VULN: Can read any user's messages"""
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(
            "SELECT * FROM messages WHERE from_user_id = %s OR to_user_id = %s",
            (user_id, user_id)
        )
        results = cur.fetchall()
        cur.close()
        conn.close()
        return [Message(**{**r, 'created_at': str(r['created_at'])}) for r in results]
    
    @strawberry.field
    def search_users(self, query: str) -> List[User]:
        """Search users - VULN: SQL injection vulnerability"""
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        # VULN: SQL injection through LIKE clause
        sql = f"SELECT * FROM users WHERE username LIKE '%{query}%' OR email LIKE '%{query}%'"
        cur.execute(sql)
        results = cur.fetchall()
        cur.close()
        conn.close()
        return [User(**{**r, 'created_at': str(r['created_at'])}) for r in results]

# Mutations
@strawberry.type
class Mutation:
    # VULN: No authentication or authorization on mutations
    # VULN: No rate limiting
    # VULN: Mass assignment vulnerabilities
    
    @strawberry.mutation
    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        role: Optional[str] = "user",
        salary: Optional[float] = None,
        ssn: Optional[str] = None
    ) -> SuccessResponse:
        """Create user - VULN: Allows setting role, salary, SSN without restrictions"""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO users (username, email, password, role, salary, ssn) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
                (username, email, password, role, salary, ssn)
            )
            user_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            conn.close()
            return SuccessResponse(success=True, message="User created", id=user_id)
        except Exception as e:
            conn.rollback()
            cur.close()
            conn.close()
            return SuccessResponse(success=False, message=str(e))
    
    @strawberry.mutation
    def update_user(
        self,
        id: int,
        username: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
        salary: Optional[float] = None
    ) -> SuccessResponse:
        """Update user - VULN: Can update any user without auth, including role escalation"""
        conn = get_db_connection()
        cur = conn.cursor()
        updates = []
        values = []
        
        if username:
            updates.append("username = %s")
            values.append(username)
        if email:
            updates.append("email = %s")
            values.append(email)
        if password:
            updates.append("password = %s")
            values.append(password)
        if role:  # VULN: Can escalate privileges
            updates.append("role = %s")
            values.append(role)
        if is_active is not None:
            updates.append("is_active = %s")
            values.append(is_active)
        if salary is not None:
            updates.append("salary = %s")
            values.append(salary)
        
        if not updates:
            return SuccessResponse(success=False, message="No fields to update")
        
        values.append(id)
        query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"
        
        try:
            cur.execute(query, values)
            conn.commit()
            cur.close()
            conn.close()
            return SuccessResponse(success=True, message="User updated")
        except Exception as e:
            conn.rollback()
            cur.close()
            conn.close()
            return SuccessResponse(success=False, message=str(e))
    
    @strawberry.mutation
    def delete_user(self, id: int) -> SuccessResponse:
        """Delete user - VULN: Can delete any user without authorization"""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM users WHERE id = %s", (id,))
            conn.commit()
            cur.close()
            conn.close()
            return SuccessResponse(success=True, message="User deleted")
        except Exception as e:
            conn.rollback()
            cur.close()
            conn.close()
            return SuccessResponse(success=False, message=str(e))
    
    @strawberry.mutation
    def create_post(
        self,
        title: str,
        content: str,
        author_id: int,
        is_published: bool = False,
        is_private: bool = False
    ) -> SuccessResponse:
        """Create post - VULN: Can create post as any user"""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO posts (title, content, author_id, is_published, is_private) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                (title, content, author_id, is_published, is_private)
            )
            post_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            conn.close()
            return SuccessResponse(success=True, message="Post created", id=post_id)
        except Exception as e:
            conn.rollback()
            cur.close()
            conn.close()
            return SuccessResponse(success=False, message=str(e))
    
    @strawberry.mutation
    def update_post(
        self,
        id: int,
        title: Optional[str] = None,
        content: Optional[str] = None,
        is_published: Optional[bool] = None,
        is_private: Optional[bool] = None
    ) -> SuccessResponse:
        """Update post - VULN: Can update any post without ownership check"""
        conn = get_db_connection()
        cur = conn.cursor()
        updates = []
        values = []
        
        if title:
            updates.append("title = %s")
            values.append(title)
        if content:
            updates.append("content = %s")
            values.append(content)
        if is_published is not None:
            updates.append("is_published = %s")
            values.append(is_published)
        if is_private is not None:
            updates.append("is_private = %s")
            values.append(is_private)
        
        if not updates:
            return SuccessResponse(success=False, message="No fields to update")
        
        values.append(id)
        query = f"UPDATE posts SET {', '.join(updates)} WHERE id = %s"
        
        try:
            cur.execute(query, values)
            conn.commit()
            cur.close()
            conn.close()
            return SuccessResponse(success=True, message="Post updated")
        except Exception as e:
            conn.rollback()
            cur.close()
            conn.close()
            return SuccessResponse(success=False, message=str(e))
    
    @strawberry.mutation
    def delete_post(self, id: int) -> SuccessResponse:
        """Delete post - VULN: Can delete any post"""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM posts WHERE id = %s", (id,))
            conn.commit()
            cur.close()
            conn.close()
            return SuccessResponse(success=True, message="Post deleted")
        except Exception as e:
            conn.rollback()
            cur.close()
            conn.close()
            return SuccessResponse(success=False, message=str(e))
    
    @strawberry.mutation
    def create_comment(self, content: str, post_id: int, author_id: int) -> SuccessResponse:
        """Create comment"""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO comments (content, post_id, author_id) VALUES (%s, %s, %s) RETURNING id",
                (content, post_id, author_id)
            )
            comment_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            conn.close()
            return SuccessResponse(success=True, message="Comment created", id=comment_id)
        except Exception as e:
            conn.rollback()
            cur.close()
            conn.close()
            return SuccessResponse(success=False, message=str(e))
    
    @strawberry.mutation
    def create_order(
        self,
        user_id: int,
        product_id: int,
        quantity: int
    ) -> SuccessResponse:
        """Create order - VULN: Can create order for any user, no stock checking"""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            # Get product price
            cur.execute("SELECT price FROM products WHERE id = %s", (product_id,))
            result = cur.fetchone()
            if not result:
                return SuccessResponse(success=False, message="Product not found")
            
            price = float(result[0])
            total_price = price * quantity
            
            cur.execute(
                "INSERT INTO orders (user_id, product_id, quantity, total_price) VALUES (%s, %s, %s, %s) RETURNING id",
                (user_id, product_id, quantity, total_price)
            )
            order_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            conn.close()
            return SuccessResponse(success=True, message="Order created", id=order_id)
        except Exception as e:
            conn.rollback()
            cur.close()
            conn.close()
            return SuccessResponse(success=False, message=str(e))
    
    @strawberry.mutation
    def update_order_status(self, id: int, status: str) -> SuccessResponse:
        """Update order status - VULN: Can update any order status"""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("UPDATE orders SET status = %s WHERE id = %s", (status, id))
            conn.commit()
            cur.close()
            conn.close()
            return SuccessResponse(success=True, message="Order status updated")
        except Exception as e:
            conn.rollback()
            cur.close()
            conn.close()
            return SuccessResponse(success=False, message=str(e))
    
    @strawberry.mutation
    def send_message(self, from_user_id: int, to_user_id: int, content: str) -> SuccessResponse:
        """Send message - VULN: Can send message as any user"""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO messages (from_user_id, to_user_id, content) VALUES (%s, %s, %s) RETURNING id",
                (from_user_id, to_user_id, content)
            )
            message_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            conn.close()
            return SuccessResponse(success=True, message="Message sent", id=message_id)
        except Exception as e:
            conn.rollback()
            cur.close()
            conn.close()
            return SuccessResponse(success=False, message=str(e))
    
    @strawberry.mutation
    def mark_message_read(self, id: int) -> SuccessResponse:
        """Mark message as read"""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("UPDATE messages SET is_read = true WHERE id = %s", (id,))
            conn.commit()
            cur.close()
            conn.close()
            return SuccessResponse(success=True, message="Message marked as read")
        except Exception as e:
            conn.rollback()
            cur.close()
            conn.close()
            return SuccessResponse(success=False, message=str(e))

# Create schema
schema = strawberry.Schema(query=Query, mutation=Mutation)

# Create FastAPI app
app = FastAPI(title="Vulnerable GraphQL API", debug=True)

# VULN: Overly permissive CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# VULN: GraphiQL enabled in production with introspection
graphql_app = GraphQLRouter(
    schema,
    graphiql=True  # VULN: GraphiQL exposed in production
)

app.include_router(graphql_app, prefix="/graphql")

@app.get("/")
def read_root():
    return {
        "message": "Vulnerable GraphQL API",
        "graphql_endpoint": "/graphql",
        "graphiql": "/graphql (interactive playground)"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

