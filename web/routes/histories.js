const express = require('express');
const router = express.Router();
const {History} = require('../models');


// todo 전적 테이블 렌더링
//  필요  admin쪽으로 가져와서 쓰면될듯

//이메일 삭제
router.get('/userList', (req, res, next) => {
  History.findAll({
    attributes: ['id',  'name', 'win', 'loss', 'points'],
    order: [
      ['id','ASC']
    ]
  })
  .then(result => {
    res.json(result);
  })
  .catch(err => {
    res.send(err);
  });
});

// 승점순
router.get('/byPoints', (req, res, next) => {
  History.findAll({
    attributes: ['id', 'name', 'win', 'loss', 'points'],
    order: [
      ['points','DESC']
    ]
  })
  .then(result => {
    res.json(result);
  })
  .catch(err => {
    res.send(err);
  });
});

// 승수 순
router.get('/byWins', (req, res, next) => {
  History.findAll({
    attributes: ['id', 'name', 'win', 'loss', 'points'],
    order: [
      ['win','DESC']
    ]
  })
  .then(result => {
    res.json(result);
  })
  .catch(err => {
    res.send(err);
  });
});
// router.get('/findUser', (req, res, next) => {
//   const {name} = req.body;
//   findUser(name)
//   .then(result => {
//     res.json(result);
//   })
//   .catch(err => {
//     res.send(err);
//   });
// });

// router.post('/findUser',(req, res) => {
//   const {name} = req.body;
//   findUser(name)
//   .then((user) => {
//     if (user != null){
//       res.json({msg: "success finding"})
//     }
//   })
// })
//
// // 네임 검색
// router.post('/findUser', (req, res, next) => {
//   const name = req.body;
//   History.findAll({
//     attributes: ['id', 'email', 'name', 'win', 'loss', 'points'],
//     where:{
//       "name" : name
//     }
//   })
//   .then(result => {
//     res.json(result);
//   })
//   .catch(err => {
//     res.send(err);
//   });
// });

module.exports = router;
