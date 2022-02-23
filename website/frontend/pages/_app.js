import React, { useState, useEffect } from 'react';
import './_app.css';
import axios from "axios";

function getMapEntries(entries) {
  let filtered = [];
  let rank = 1;
  if (entries) {
    for (let item in entries) {
      if (entries[item]) {
        entries[item].rank = rank;
        filtered.push(entries[item]);
        rank++;
      }
    }
  }
  return filtered;
}

function secondsToMs(d) {
  d = Number(d);
  var h = Math.floor(d / 3600);
  var m = Math.floor(d % 3600 / 60);
  var s = Math.floor(d % 3600 % 60);

  var hDisplay = h > 0 ? h + (h == 1 ? "h:" : "h:") : "";
  var mDisplay = m > 0 ? m + (m == 1 ? "m:" : "m:") : "";
  var sDisplay = s > 0 ? s + (s == 1 ? "s" : "s") : "";
  return hDisplay + mDisplay + sDisplay; 
}

function findAverages(data) {
  let total_score = 0;
  let total_powerups_used = 0;
  //this is in seconds in game. will parse again later
  let total_num_turns = 0;
  let max_score = 0;
  let total_seconds = 0;
  let time_in_seconds = 0;
  let min_num_turns = 0;
  let min_powerups_used = 0;
  let max_time_in_seconds = 0;

  if(data.length != 0) {
    for (let item in data) {
      if (data[item]) {
        total_score += data[item].score;
        total_powerups_used += data[item].powerups_used;
        time_in_seconds = parseInt(data[item].time_in_game.split(":")[0])*3600 + parseInt(data[item].time_in_game.split(":")[1])*60 + parseInt(data[item].time_in_game.split(":")[2])
        total_seconds += time_in_seconds;
        total_num_turns += data[item].num_turns;
        if (data[item].score > max_score) {
          max_score = data[item].score; 
        }
        if (data[item].powerups_used < min_powerups_used) {
          min_powerups_used = data[item].powerups_used;
        }
        if (data[item].num_turns < min_num_turns) {
          min_num_turns = data[item].num_turns;
        }
        if (time_in_seconds > max_time_in_seconds) {
          max_time_in_seconds = time_in_seconds;
        }
      }
    }
    return [`Max Score: ${max_score}`,`Max Time Survived: \n ${secondsToMs(max_time_in_seconds)}`,``,``,``,`Avg Score: ${(total_score/data.length).toFixed(2)}`,`Avg Powerups: ${(total_powerups_used/data.length).toFixed(2)}`, `Avg Num of Turns: ${(total_num_turns/data.length).toFixed(2)}`,`Avg Time Survived: \n ${secondsToMs(Math.floor(total_seconds/data.length))}`,``,``,``,`Min Powerups: ${min_powerups_used}`,`Min Num of Turns: ${min_num_turns}`,``,``,``,`Total Powerups: ${total_powerups_used}`,`Total Num Turns: ${total_num_turns}`]
  }
  else {
    return ["Stats Unavailable"]
  }
}

function App() {
  const [gameDataList, setGameDataList] = useState([]);
  const [userSearch, setuserSearch] = useState("");
  const [userData, setUserData] = useState([]);

  const updateScores = () => {
    axios.get("https://beepboopw2d.herokuapp.com/api/get").then((response) => {
      console.log("Get Request");
      setGameDataList(response.data);
    });
  }

  useEffect(() => {
    updateScores();
  }, [])

  const submitUser = () => {
    axios.post("https://beepboopw2d.herokuapp.com/api/user", {username: userSearch}).then((response) => {
      console.log("User Request For: " + userSearch);
      setUserData(response.data)
    });
    global = false;
  }  

  return(
    <div className='App'>
      <div className='Header'>
        <h1>Beep Boop Want to Drive</h1>
      </div>

      <div className='highScore'>
        <h1>High Score</h1>
      </div>

      <div className='userSearchForm'>
        <label>Search Username: </label>
        <input type="text" id='userSearch' name='userSearch' onChange={(search) => {
          setuserSearch(search.target.value)
          if(search.target.value == "") {
            global = true;
          }
        }} onSubmit={submitUser}></input>
        <button onClick={submitUser}><img src="https://img.icons8.com/ios-glyphs/90/000000/search--v2.png"/></button>
      </div>


      <div className='Data'>
        <div className="avgData">
            {(global == false) ? <h3>Player Statistics</h3> : <h3>Global Statistics</h3>}
            {findAverages((global == false) ? getMapEntries(userData) : getMapEntries(gameDataList)).map((value) => {
              return (
                <table>
                  <tr>
                    <td>{value}</td>
                  </tr>
                </table>
              )
            })}
        </div>
        <div className='dataTable'>
          <table>
            <tr>
              <th>Rank</th>
              <th>Name</th>
              <th>Score</th>
              <th>Powerups</th>
              <th>Num. Turns</th>
              <th>Survived</th>
              <th>Date</th> 
              <th>Time</th>
            </tr>
            { (global == false) ? 
              getMapEntries(userData).slice().map(value => {
                return (
                    <tr>
                      <td>{value.rank}</td>
                      <td>{value.username}</td>
                      <td>{value.score}</td>
                      <td>{value.powerups_used}</td>
                      <td>{value.num_turns}</td>
                      <td>{value.time_in_game.split(":")[0] + "h:" + value.time_in_game.split(":")[1] + "m:" + value.time_in_game.split(":")[2] + "s"}</td>
                      <td>{new Date(Date.parse(value.datetimestamp)).toLocaleString('en-US', {timeZone: 'UTC'}).split(', ')[0]}</td>
                      <td>{new Date(Date.parse(value.datetimestamp)).toLocaleString('en-US', {timeZone: 'UTC'}).split(', ')[1]}</td>
                    </tr>
                )
              }) :
              getMapEntries(gameDataList).slice().map(value => {
                return (
                    <tr>
                      <td>{value.rank}</td>
                      <td>{value.username}</td>
                      <td>{value.score}</td>
                      <td>{value.powerups_used}</td>
                      <td>{value.num_turns}</td>
                      <td>{value.time_in_game.split(":")[0] + "h:" + value.time_in_game.split(":")[1] + "m:" + value.time_in_game.split(":")[2] + "s"}</td>
                      <td>{new Date(Date.parse(value.datetimestamp)).toLocaleString('en-US', {timeZone: 'UTC'}).split(', ')[0]}</td>
                      <td>{new Date(Date.parse(value.datetimestamp)).toLocaleString('en-US', {timeZone: 'UTC'}).split(', ')[1]}</td>
                    </tr>
                )
              })  
            }
          </table>
        </div>
      </div>
    </div>
    
  );
}

export default App