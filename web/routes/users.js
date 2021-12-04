var express = require('express');
var router = express.Router();
const { User } = require('../models');
const crypto = require('crypto');
const jwt = require('jsonwebtoken');

router.post('/login', async (req, res, next) => {
  const { name, password } = req.body;
  findSalt(name)
    .then((doc) => createHash(password, doc.salt)) // password hash
    .then((hashedPassword) => findUser(name, hashedPassword)) // User DB에서 사용자 검색
    .then((user) => {
      console.log();
      if (user == null) {
        res.json({ msg: 'failed' }); //회원정보 없음
        return;
      } else {
        let accessToken = jwt.sign(
          { name, type: user.userType, verified: user.verified },
          'secret',
          { expiresIn: '30m' },
        );
        let refreshToken = jwt.sign(
          { name, type: user.userType, verified: user.verified },
          'secret',
          { expiresIn: '60m' },
        );
        req.cache.set(name, refreshToken);
        //         req.expire(name, 60 * 10);
        const info = [accessToken, name];
        return info;
      }
    })
    .then((info) => {
      // save access_token in redis
      const parsedKey = 'access_' + info[1];
      const user = info[1];
      console.log('parsedKey: ', parsedKey);
      saveRedis(req, parsedKey, info[0], 60 * 5).then((token) => {
        console.log('token: ', token);
        console.log('user: ', user);
        const resarr = [user, token];
        res.json({ msg: resarr });
      });
    });
});

router.post('/logout', async (req, res, next) => {
  res.cookie('accessToken', '', { secure: false, httpOnly: true, readOnly: true });
  console.log('logout check');
  return res.json({ msg: 'success' });
});

function findUser(name, password) {
  return new Promise(function (resolve, reject) {
    User.findOne({
      where: {
        name: name,
        password: password,
      },
    })
      .then((result) => {
        resolve(result['name']);
      })
      .catch((err) => {
        reject(err);
      });
  });
}

function findSalt(name) {
  return new Promise((resolve, reject) => {
    User.findOne({ where: { name: name } })
      .then((result) => {
        resolve(result);
      })
      .catch((err) => {
        resolve(err);
      });
  });
}

function createHash(password, salt) {
  return new Promise((resolve, reject) => {
    crypto.pbkdf2(password, salt, 100000, 64, 'sha512', (err, key) => {
      if (err) reject(err);
      const hashedKey = key.toString('base64');
      resolve(hashedKey);
    });
  });
}

function saveRedis(req, key, token, expire) {
  return new Promise(async (resolve, reject) => {
    await req.cache.set(key, token, (err, data) => {
      if (err) {
        reject(err);
      }
      req.cache.expire(key, expire);
      resolve(token);
    });
  });
}

module.exports = router;
