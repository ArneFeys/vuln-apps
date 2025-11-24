const API_URL = 'http://localhost:8000/graphql';

// Tab switching
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const tabName = btn.dataset.tab;
        
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        
        btn.classList.add('active');
        document.getElementById(`${tabName}-tab`).classList.add('active');
    });
});

// Helper function to execute GraphQL query
async function executeGraphQL(query, variables = {}) {
    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query, variables })
        });
        
        const data = await response.json();
        displayResults(data);
        return data;
    } catch (error) {
        displayResults({ error: error.message });
    }
}

// Display results
function displayResults(data) {
    const output = document.getElementById('output');
    output.textContent = JSON.stringify(data, null, 2);
}

// Get input value
function getValue(id) {
    return document.getElementById(id)?.value || '';
}

// Get checkbox value
function getChecked(id) {
    return document.getElementById(id)?.checked || false;
}

// Users queries and mutations
async function fetchAllUsers() {
    const query = `
        query {
            users {
                id
                username
                email
                password
                role
                salary
                ssn
                isActive
                createdAt
            }
        }
    `;
    await executeGraphQL(query);
}

async function fetchUser() {
    const id = prompt('Enter User ID:');
    if (!id) return;
    
    const query = `
        query GetUser($id: Int!) {
            user(id: $id) {
                id
                username
                email
                password
                role
                salary
                ssn
                isActive
                createdAt
            }
        }
    `;
    await executeGraphQL(query, { id: parseInt(id) });
}

async function searchUsers() {
    const searchQuery = prompt('Enter search query:');
    if (!searchQuery) return;
    
    const query = `
        query SearchUsers($query: String!) {
            searchUsers(query: $query) {
                id
                username
                email
                password
                role
                salary
                ssn
            }
        }
    `;
    await executeGraphQL(query, { query: searchQuery });
}

async function createUser() {
    const username = getValue('new-username');
    const email = getValue('new-email');
    const password = getValue('new-password');
    const role = getValue('new-role');
    
    if (!username || !email || !password) {
        alert('Please fill in required fields');
        return;
    }
    
    const mutation = `
        mutation CreateUser($username: String!, $email: String!, $password: String!, $role: String) {
            createUser(username: $username, email: $email, password: $password, role: $role) {
                success
                message
                id
            }
        }
    `;
    await executeGraphQL(mutation, { username, email, password, role: role || 'user' });
}

async function updateUser() {
    const id = parseInt(getValue('update-user-id'));
    const username = getValue('update-username');
    const role = getValue('update-role');
    
    if (!id) {
        alert('Please provide User ID');
        return;
    }
    
    const mutation = `
        mutation UpdateUser($id: Int!, $username: String, $role: String) {
            updateUser(id: $id, username: $username, role: $role) {
                success
                message
            }
        }
    `;
    await executeGraphQL(mutation, { id, username: username || null, role: role || null });
}

async function deleteUser() {
    const id = parseInt(getValue('delete-user-id'));
    
    if (!id) {
        alert('Please provide User ID');
        return;
    }
    
    if (!confirm(`Are you sure you want to delete user ${id}?`)) {
        return;
    }
    
    const mutation = `
        mutation DeleteUser($id: Int!) {
            deleteUser(id: $id) {
                success
                message
            }
        }
    `;
    await executeGraphQL(mutation, { id });
}

// Posts queries and mutations
async function fetchAllPosts() {
    const query = `
        query {
            posts {
                id
                title
                content
                authorId
                isPublished
                isPrivate
                createdAt
            }
        }
    `;
    await executeGraphQL(query);
}

async function fetchPost() {
    const id = prompt('Enter Post ID:');
    if (!id) return;
    
    const query = `
        query GetPost($id: Int!) {
            post(id: $id) {
                id
                title
                content
                authorId
                isPublished
                isPrivate
                createdAt
            }
        }
    `;
    await executeGraphQL(query, { id: parseInt(id) });
}

async function fetchPostsByAuthor() {
    const authorId = prompt('Enter Author ID:');
    if (!authorId) return;
    
    const query = `
        query GetPostsByAuthor($authorId: Int!) {
            posts(authorId: $authorId) {
                id
                title
                content
                authorId
                isPublished
                isPrivate
                createdAt
            }
        }
    `;
    await executeGraphQL(query, { authorId: parseInt(authorId) });
}

async function createPost() {
    const title = getValue('post-title');
    const content = getValue('post-content');
    const authorId = parseInt(getValue('post-author-id'));
    const isPublished = getChecked('post-published');
    const isPrivate = getChecked('post-private');
    
    if (!title || !content || !authorId) {
        alert('Please fill in required fields');
        return;
    }
    
    const mutation = `
        mutation CreatePost($title: String!, $content: String!, $authorId: Int!, $isPublished: Boolean!, $isPrivate: Boolean!) {
            createPost(title: $title, content: $content, authorId: $authorId, isPublished: $isPublished, isPrivate: $isPrivate) {
                success
                message
                id
            }
        }
    `;
    await executeGraphQL(mutation, { title, content, authorId, isPublished, isPrivate });
}

async function updatePost() {
    const id = parseInt(getValue('update-post-id'));
    const title = getValue('update-post-title');
    const isPublished = getChecked('update-post-published');
    
    if (!id) {
        alert('Please provide Post ID');
        return;
    }
    
    const mutation = `
        mutation UpdatePost($id: Int!, $title: String, $isPublished: Boolean) {
            updatePost(id: $id, title: $title, isPublished: $isPublished) {
                success
                message
            }
        }
    `;
    await executeGraphQL(mutation, { id, title: title || null, isPublished });
}

async function fetchComments() {
    const postId = parseInt(getValue('comments-post-id'));
    
    if (!postId) {
        alert('Please provide Post ID');
        return;
    }
    
    const query = `
        query GetComments($postId: Int!) {
            comments(postId: $postId) {
                id
                content
                postId
                authorId
                createdAt
            }
        }
    `;
    await executeGraphQL(query, { postId });
}

async function createComment() {
    const postId = parseInt(getValue('comment-post-id'));
    const authorId = parseInt(getValue('comment-author-id'));
    const content = getValue('comment-content');
    
    if (!postId || !authorId || !content) {
        alert('Please fill in all fields');
        return;
    }
    
    const mutation = `
        mutation CreateComment($content: String!, $postId: Int!, $authorId: Int!) {
            createComment(content: $content, postId: $postId, authorId: $authorId) {
                success
                message
                id
            }
        }
    `;
    await executeGraphQL(mutation, { content, postId, authorId });
}

// Products queries
async function fetchAllProducts() {
    const query = `
        query {
            products {
                id
                name
                description
                price
                stock
                isAvailable
                createdAt
            }
        }
    `;
    await executeGraphQL(query);
}

async function fetchProduct() {
    const id = prompt('Enter Product ID:');
    if (!id) return;
    
    const query = `
        query GetProduct($id: Int!) {
            product(id: $id) {
                id
                name
                description
                price
                stock
                isAvailable
                createdAt
            }
        }
    `;
    await executeGraphQL(query, { id: parseInt(id) });
}

// Orders queries and mutations
async function fetchAllOrders() {
    const query = `
        query {
            orders {
                id
                userId
                productId
                quantity
                totalPrice
                status
                createdAt
            }
        }
    `;
    await executeGraphQL(query);
}

async function fetchUserOrders() {
    const userId = prompt('Enter User ID:');
    if (!userId) return;
    
    const query = `
        query GetUserOrders($userId: Int!) {
            orders(userId: $userId) {
                id
                userId
                productId
                quantity
                totalPrice
                status
                createdAt
            }
        }
    `;
    await executeGraphQL(query, { userId: parseInt(userId) });
}

async function fetchOrder() {
    const id = prompt('Enter Order ID:');
    if (!id) return;
    
    const query = `
        query GetOrder($id: Int!) {
            order(id: $id) {
                id
                userId
                productId
                quantity
                totalPrice
                status
                createdAt
            }
        }
    `;
    await executeGraphQL(query, { id: parseInt(id) });
}

async function createOrder() {
    const userId = parseInt(getValue('order-user-id'));
    const productId = parseInt(getValue('order-product-id'));
    const quantity = parseInt(getValue('order-quantity'));
    
    if (!userId || !productId || !quantity) {
        alert('Please fill in all fields');
        return;
    }
    
    const mutation = `
        mutation CreateOrder($userId: Int!, $productId: Int!, $quantity: Int!) {
            createOrder(userId: $userId, productId: $productId, quantity: $quantity) {
                success
                message
                id
            }
        }
    `;
    await executeGraphQL(mutation, { userId, productId, quantity });
}

async function updateOrderStatus() {
    const id = parseInt(getValue('update-order-id'));
    const status = getValue('update-order-status');
    
    if (!id || !status) {
        alert('Please fill in all fields');
        return;
    }
    
    const mutation = `
        mutation UpdateOrderStatus($id: Int!, $status: String!) {
            updateOrderStatus(id: $id, status: $status) {
                success
                message
            }
        }
    `;
    await executeGraphQL(mutation, { id, status });
}

// Messages queries and mutations
async function fetchMessages() {
    const userId = parseInt(getValue('messages-user-id'));
    
    if (!userId) {
        alert('Please provide User ID');
        return;
    }
    
    const query = `
        query GetMessages($userId: Int!) {
            messages(userId: $userId) {
                id
                fromUserId
                toUserId
                content
                isRead
                createdAt
            }
        }
    `;
    await executeGraphQL(query, { userId });
}

async function sendMessage() {
    const fromUserId = parseInt(getValue('msg-from-id'));
    const toUserId = parseInt(getValue('msg-to-id'));
    const content = getValue('msg-content');
    
    if (!fromUserId || !toUserId || !content) {
        alert('Please fill in all fields');
        return;
    }
    
    const mutation = `
        mutation SendMessage($fromUserId: Int!, $toUserId: Int!, $content: String!) {
            sendMessage(fromUserId: $fromUserId, toUserId: $toUserId, content: $content) {
                success
                message
                id
            }
        }
    `;
    await executeGraphQL(mutation, { fromUserId, toUserId, content });
}

async function markMessageRead() {
    const id = parseInt(getValue('msg-read-id'));
    
    if (!id) {
        alert('Please provide Message ID');
        return;
    }
    
    const mutation = `
        mutation MarkMessageRead($id: Int!) {
            markMessageRead(id: $id) {
                success
                message
            }
        }
    `;
    await executeGraphQL(mutation, { id });
}

// Custom query execution
async function executeCustomQuery() {
    const query = getValue('custom-query');
    
    if (!query) {
        alert('Please enter a query');
        return;
    }
    
    await executeGraphQL(query);
}

