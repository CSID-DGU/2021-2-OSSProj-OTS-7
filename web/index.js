const express = require("express");
const bodyParser = require("body-parser");
const db = require("./config/database");

const app = express();
const router = express.Router();
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());
app.set("view engine", "ejs");

// home
app.get("/", (req, res) => {
  res.render("home");
});
// route to handle user registration
app.get("/signIn",(req,res) => {
  res.render("signIn")
})
app.post("/signIn", function(req, res) {
  function randomString () {
    const chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXTZabcdefghiklmnopqrstuvwxyz'
    const stringLength = 8
    let randomstring = ''
    for (let i = 0; i < stringLength; i++) {
      const rnum = Math.floor(Math.random() * chars.length)
      randomstring += chars.substring(rnum, rnum + 1)
    }
    return randomstring
  }
  const id_= req.body.id;
  const email_= req.body.email;
  const password_= req.body.password;
  const token_ = randomString();
  const insertAccountSql =`INSERT INTO accounts(id, email, password,token) VALUES (?,?,?,?)`
  db.query(insertAccountSql,
    [id_,email_,password_,token_],
    (error, results, fields) => {
      if (error) {
        console.log("error ocurred", error);
        res.send({
          "code": 400,
          "failed": "error ocurred"
        });
      } else {
        const insertMatchSql =`INSERT INTO matchHistory (id, email,token) VALUES (?,?,?)`
        db.query(insertMatchSql,
          [id_,email_,token_],
          (error, results, fields) => {
            if (error) {
              console.log("error ocurred", error);
              res.send({
                "code": 400,
                "failed": "error ocurred"
              });
            } else {
              console.log("The solution is: ", results);
              res.send({
                "code": 200,
                "success": "user registered sucessfully"
              });
            }
          });

      }
    });

});
app.get("/login",(req,res) => {
  res.render("login")
})
app.post("/login", function (req, res) {
  const email_ = req.body.email;
  const password_ = req.body.password;
  db.query(
    `SELECT * FROM accounts WHERE email = ?`,
    [email_, password_],
    function (error, results, fields) {
      if (error) {
        res.send({
          code: 400,
          failed: "error ocurred",
        });
      } else {
        if (results.length > 0) {
          if (results[0].password === password_) {
            res.send({
              code: 200,
              success: "login sucessfull",
            });
          } else {
            res.send({
              code: 204,
              success: "Email and password does not match",
            });
          }
        } else {
          res.send({
            code: 204,
            success: "Email does not exists",
          });
        }
      }
    }
  );
});

app.listen(5000,(error, response) => {
  if(error) {
    return error;
  } else{
    console.log("connected on http://localhost:5000/")
  }
});
