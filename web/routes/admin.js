const express = require('express');
const router = express.Router();
const {User} = require('../models');
const jwt = require('jsonwebtoken');

router.use((req, res, next) => {
    const {accessToken} = req.cookies;
    var token;

    if (accessToken == null) 
        res.redirect("/");

    jwt.verify(accessToken, process.env.JWT_SECRET_ACCESS, (error, decoded) => {
        if (error)
            return res.json({ error: "error occur" });
        token = decoded;
    });
    //const token = jwt.decode(accessToken, process.env.JWT_SECRET);

    if (token===null || token.type !== "Admin") {
        res.status(403).send('Forbidden');
        return;
    }

    req.cache.get('access_' + token.email, (err, data) => {
        if (err || data!==accessToken) {
            res.status(403).send('Forbidden');
            return;
        }
        next();
    });

});

router.get('/', (req, res, next) => {
    res.render('admin');
});

router.get('/userList', (req, res, next) => {
    User.findAll({
        attributes: ['id', 'email', 'name', 'userType', 'createdAt']
    })
        .then(result => {
            res.json(result);
        })
        .catch(err => {
            res.send(err);
        });
});

module.exports = router;