module.exports = (sequelize, DataTypes) => {
  return sequelize.define('histories', {
    name: {
      type: DataTypes.TEXT,
      allowNull: false,
    },
    win: {
      type: DataTypes.INTEGER,
      allowNull: false,
      defaultValue: 0,
    },
    loss: {
      type: DataTypes.INTEGER,
      allowNull: false,
      defaultValue: 0,
    },
    points: {
      type: DataTypes.INTEGER,
      allowNull: false,
      defaultValue: 0,
    },
  });
};
