var express = require('express');
var router = express.Router();
const jwt = require('jsonwebtoken');

router.use((req, res, next) => {
    const {accessToken} = req.cookies;
    console.log(accessToken);
    if (accessToken == null) {
        res.redirect('/login');
        return;
    }
    next();
});

router.get('/', (req, res, next) => {
    res.render('main');
});

module.exports = router;