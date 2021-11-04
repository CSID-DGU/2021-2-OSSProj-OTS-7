module.exports = (sequelize, DataTypes)=>{
    return sequelize.define('histories',{
        email : {
            type : DataTypes.TEXT,
            allowNull: false
        },
        name : {
            type : DataTypes.TEXT,
            allowNull : false,
        },
        win : {
            type : DataTypes.INTEGER,
            allowNull : false,
            defaultValue : 0
        },
        loss : {
            type : DataTypes.INTEGER,
            allowNull : false,
            defaultValue : 0
        },
        points : {
            type : DataTypes.INTEGER,
            allowNull : false,
            defaultValue : 0
        }
    });
}