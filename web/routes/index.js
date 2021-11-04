var express = require('express');
var router = express.Router();

router.get('/', (req, res, next) => {
    res.render('signinup');
});

router.get('/main', (req, res, next) => {
    res.render('main');
});

router.get('/histories', (req, res, next) =>{
    res.render('histories')
})

module.exports = router;