var express = require('express');
var router = express.Router();
const {User} = require('../models');
const crypto = require('crypto');
const jwt = require('jsonwebtoken');

router.post('/login', async(req, res, next) => {
    const {email, password} = req.body;

    findSalt(email)
        .then((doc) => createHash(password, doc.salt)) // password hash
        .then((hashedPassword) => findUser(email, hashedPassword)) // User DB에서 사용자 검색
        .then((user) => {
            if (user == null) {
                res.json({msg: "failed"}); //회원정보 없음
                return;
            }
            let accessToken = jwt.sign({email, type: user.userType, verified: user.verified}, // jwt 생성 후 토큰 반환
                process.env.JWT_SECRET_ACCESS, {expiresIn: '30m'});
            /*
            let refreshToken = jwt.sign({email, type: user.userType, verified: user.verified}, // jwt 생성 후 토큰 반환
                process.env.JWT_SECRET_REFRESH, {expiresIn: '60m'});
            
            req.cache.set(email, refreshToken);
            req.expire(email, 60 * 10);
            */
            return accessToken
        })
        .then(token => { // save access_token in redis
            const parsedKey = 'access_' + email;
            console.log("parsedKey: ", parsedKey);
            return saveRedis(req, parsedKey, token, 60 * 5);
        }) 
        .then((token) => { // save token in cookie
            console.log("result token: ",token);
            res.cookie('accessToken', token, {secure: false, httpOnly: true,readOnly : true});
            res.json({msg: 'success'}); // 성공
        })
        .catch(err => {
            res.json({msg: "failed", err});
        });
});

router.post('/logout', async(req, res, next) => {
    res.cookie('accessToken', "", {secure: false, httpOnly: true,readOnly : true});
    console.log("logout check");
    return res.json({msg: "success"});
});

function findUser(email, password) {
    return new Promise(function (resolve, reject) {
        User.findOne({
            where: {
                "email": email,
                "password": password
            }
        })
        .then(result => {
            resolve(result);
        })
        .catch((err) => {
            reject(err);
        });

    })
}

function findSalt (email) {
    return new Promise((resolve, reject) => {
        User.findOne({where: {email}})
            .then(result => {
                resolve(result);
            })
            .catch(err => {
                resolve(err);
            });
    })
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
        })
    })
}

module.exports = router;