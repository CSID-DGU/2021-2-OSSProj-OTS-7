module.exports = (sequelize, DataTypes)=>{
    return sequelize.define('user',{
        email : {
            type : DataTypes.TEXT,
            allowNull: false
//             unique: true,
        },
        password : {
            type : DataTypes.TEXT,
            allowNull: false,
        },
        name : {
            type : DataTypes.TEXT,
            allowNull : false,
        },
        salt : {
            type : DataTypes.TEXT,
            allowNull : false
        },
        verified : {
            type : DataTypes.BOOLEAN,
            defaultValue : true
        },
        userType : {
            type : DataTypes.TEXT,
            allowNull : false,
        }
    },{
        timestamps: true,
    });
}