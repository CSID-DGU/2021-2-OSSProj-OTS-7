var express = require('express');
var router = express.Router();
const { User, History } = require('../models');
const crypto = require('crypto');
const jwt = require('jsonwebtoken');

router.post('/createUser', (req, res, next) => {
  const { name, password } = req.body;
  var userType = 'User';
  if ((password && name) === 0) {
    res.status(400).send('bad Request');
  }
  checkName(name).then((user_) => {
    if (user_ != null) return res.json({ msg: 'duplicate_name' }); // name 중복
    crypto.randomBytes(64, (err, buf) => {
      // 64bit random salt 생성 후  pbkdf2 적용 (10만번 반복)
      const salt = buf.toString('base64');
      crypto.pbkdf2(password, salt, 100000, 64, 'sha512', (err, key) => {
        if (err) return;
        const hashPwd = key.toString('base64');

        User.count().then((count) => {
          // 첫번째 등록자를 Admin으로 설정
          if (count == 0) userType = 'Admin';

          createUser(hashPwd, name, userType, salt)
            .then(() => {
              console.log('createUser success');
              return res.status(200).json({ msg: 'success' });
            })
            .catch((err) => {
              console.log(err);
              return res.json({ msg: 'failed' });
            });
        });
      });
    });
  });
});

function createUser(password, name, userType, salt) {
  return new Promise(function (resolve, reject) {
    User.create({
      password: password,
      name: name,
      userType: userType,
      salt: salt,
    })
      .then(() => {
        History.create({
          name: name,
        });
        resolve();
      })
      .catch((err) => {
        reject(err);
      });
  });
}

//TODO
//check name 추가
function checkName(name) {
  return new Promise((resolve, reject) => {
    User.findOne({ where: { name } })
      .then((result) => {
        resolve(result);
      })
      .catch((err) => {
        resolve(err);
      });
  });
}
module.exports = router;
