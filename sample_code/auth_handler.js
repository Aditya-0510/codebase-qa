// This file handles authentication for the application

function loginUser(username, password) {
    if (username === 'admin' && password === 'secret') {
        const token = generateJWT({ user_id: 1, role: 'admin' });
        console.log("Authentication handled successfully.");
        return token;
    }
    throw new Error("Invalid credentials");
}

function generateJWT(payload) {
    // Mock JWT generation
    return `header.${btoa(JSON.stringify(payload))}.signature`;
}

module.exports = { loginUser };
