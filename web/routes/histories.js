const express = require('express');
const router = express.Router();
const { History } = require('../models');

router.get('/userList', (req, res, next) => {
  History.findAll({
    attributes: ['id', 'name', 'win', 'loss', 'points'],
    order: [['id', 'ASC']],
  })
    .then((result) => {
      res.json(result);
    })
    .catch((err) => {
      res.send(err);
    });
});

// 승점순
router.get('/byPoints', (req, res, next) => {
  History.findAll({
    attributes: ['id', 'name', 'win', 'loss', 'points'],
    order: [['points', 'DESC']],
  })
    .then((result) => {
      res.json(result);
    })
    .catch((err) => {
      res.send(err);
    });
});

// 승수 순
router.get('/byWins', (req, res, next) => {
  History.findAll({
    attributes: ['id', 'name', 'win', 'loss', 'points'],
    order: [['win', 'DESC']],
  })
    .then((result) => {
      res.json(result);
    })
    .catch((err) => {
      res.send(err);
    });
});
router.post('/winner', (req, res, next) => {
  const { name } = req.body;
  if (!name) {
    console.error('no');
  } else {
    History.findOne({
      where: { name: name },
    })
      .then((user) => {
        const points_ = user.points;
        const win_ = user.win;
        const loss_ = user.loss;
        History.update(
          { points: points_ + 3, win: win_ + 1, loss: loss_ },
          { where: { name: name } },
        )
          .then((result) => {
            res.json(result);
          })
          .catch((err) => {
            console.log(err);
          });
      })
      .catch((err) => {
        console.log(err);
      });
  }
});

router.post('/loser', (req, res, next) => {
  const { name } = req.body;
  if (!name) {
    console.error('no');
  } else {
    History.findOne({
      where: { name: name },
    })
      .then((user) => {
        const points_ = user.points;
        const win_ = user.win;
        const loss_ = user.loss;
        History.update(
          { points: points_ - 1, win: win_, loss: loss_ + 1 },
          { where: { name: name } },
        )
          .then((result) => {
            res.json(result);
          })
          .catch((err) => {
            console.log(err);
          });
      })
      .catch((err) => {
        console.log(err);
      });
  }
});

module.exports = router;
