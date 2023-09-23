const express = require('express');
const bodyParser = require('body-parser');
const path = require('path');
const app = express();

// Middleware to parse JSON request bodies
app.use(bodyParser.json());

// Serve a simple HTML form for GET requests
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname+'/data/index.html'));
});

// Handle POST requests
app.post('/post', (req, res) => {
    const postData = req.body.data;
    res.json({ message: 'POST request received', data: postData });
});

const port = 3000;

app.listen(port, () => {
    console.log(`Server is listening on port ${port}`);
});
