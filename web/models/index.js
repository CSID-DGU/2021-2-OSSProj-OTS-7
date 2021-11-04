const path = require('path');MgxNBpMlBwgl3h4zf3ZNSQ8HI7Y2w7n…
const Sequelize = require('sequelize');

const env = process.env.NODE_ENV || 'development';
const config = require(path.join(__dirname,'..','config','config.json'))[env];
const db = {};

let sequelize = new Sequelize(config.database,config.username,config.password,config);

db.sequelize = sequelize;
db.Sequelize = Sequelize;

db.User = require('./user')(sequelize,Sequelize);
db.History = require('./history')(sequelize,Sequelize);

module.exports = db;