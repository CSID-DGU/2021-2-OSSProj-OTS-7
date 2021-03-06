const express = require('express');
const app = express();
const cookieParser = require('cookie-parser');
const path = require('path');
const dotenv = require('dotenv');
const redis = require('redis');
const logger = require('morgan');
dotenv.config();
// port
var port = process.env.PORT || 8080;
app.listen(port, function () {
  console.log('Express server has started on port ' + port);
});

// sequelize
var { sequelize } = require('./models/index');
sequelize.sync();

// redis connect
app.use((req, res, next) => {
  const redisClient = redis.createClient({
    "host": "127.0.0.1",
    "port": 6379,
    "db": 5
  });
  req.cache = redisClient;
  next();
});

// view engine
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'ejs');

app.use(logger('dev'));
app.use(cookieParser());
app.use(express.json());
app.use(express.urlencoded({ extends: true }));
app.use(express.static(path.join(__dirname, 'public')));

// router
const index = require('./routes/index');
const users = require('./routes/users');
const main = require('./routes/main');
const admin = require('./routes/admin');
const signup = require('./routes/signup');
const histories = require('./routes/histories');

app.use('/', index);
app.use('/users', users);
app.use('/main', main);
app.use('/admin', admin);
app.use('/signup', signup);
app.use('/histories', histories);

module.exports = app;
