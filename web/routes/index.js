var express = require('express');
var router = express.Router();

router.get('/', (req, res, next) => {
  res.render('signinup');
});

router.get('/main', (req, res, next) => {
  res.render('main');
});

router.get('/histories', (req, res, next) => {
  res.render('histories');
});

router.get('/users', (req, res) => res.render('users'));

router.get('/byWins', (req, res) => res.render('byWins'));

router.get('/byPoints', (req, res) => res.render('byPoints'));

router.get('/userList', (req, res) => res.render('userList'));

router.get('/findUser', (req, res) => res.render('findUser'));
module.exports = router;
