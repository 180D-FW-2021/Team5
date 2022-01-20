const express = require("express");
const bodyParser = require("body-parser");
const cors = require("cors");
const app = express();
const mysql = require('mysql');

const PORT = 3001;

const db = mysql.createPool({
    host: "us-cdbr-east-05.cleardb.net",
    user: "bab8d04d058b12",
    password: "ad928818",
    database: "heroku_c269c70f6f04f90"
});

app.use(cors());
app.use(express.json());
app.use(bodyParser.urlencoded({extended: true}));

app.get('/', function (req, res) {
    res.send("You weren't supposed to see this...")
})

app.get("/api/get", (req, res) => {
    const sql_select_all = "SELECT * FROM game_data ORDER BY score DESC, datetimestamp DESC, time_in_game DESC, powerups_used DESC, username ASC";
    db.query(sql_select_all, (err, result) => {
        res.send(result);
    })
});

app.post("/api/user", (req, res) => {
    const username = req.body.username;
    const sql_select_user = "SELECT * FROM game_data WHERE username = " + '"' + username + '" ORDER BY score DESC, datetimestamp DESC, time_in_game DESC, powerups_used DESC, username ASC'
    //const trivial_sql_insert = "INSERT INTO game_data VALUES (7,?,0,0,0,0)";
    db.query(sql_select_user, (err, result) => {
        res.send(result);
    });
});

app.post("/api/insert", (req, res) => {
    const username = req.body.username;
    const score = req.body.score;
    const powerups_used = req.body.powerups_used;
    const datetimestamp = req.body.datetimestamp;
    const time_in_game = req.body.time_in_game;
    const sql_insert_user = "INSERT INTO game_data VALUES (NULL,?,?,?,?,?)";
    db.query(sql_insert_user, [username, score, time_in_game , datetimestamp , powerups_used], (err,result) => {
        res.send(err);
        res.send(result);
    })
});

app.listen(process.env.PORT || PORT, () => {
    console.log(`running on port ${PORT}`);
});