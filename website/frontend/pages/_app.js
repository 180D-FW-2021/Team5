import React, { useState, useEffect } from 'react';
import './_app.css';
import axios from "axios";

function getMapEntries(entries) {
  let filtered = [];
  if (entries) {
    for (let item in entries) {
      if (entries[item]) {
          filtered.push(entries[item]);
      }
    }
  }
  return filtered;
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
      
      <div className='userSearchForm'>
        <label>Search Username: </label>
        <input type="text" id='userSearch' name='userSearch' onChange={(search) => {
          setuserSearch(search.target.value)
        }} onSubmit={submitUser}></input>
        <button onClick={submitUser}><img src="https://img.icons8.com/ios-glyphs/90/000000/search--v2.png"/></button>
      </div>

      <div className='Data'>
        <div className='dataTable'>
          <table>
            <tr>
              <th>Username</th>
              <th>Score</th>
              <th>Powerups Used</th>
              <th>Timestamp</th>
            </tr>
            { (userSearch == null) ? 
              getMapEntries(gameDataList).slice(1, 15).map(value => {
                return (
                    <tr>
                      <td>{value.username}</td>
                      <td>{value.score}</td>
                      <td>{value.powerups_used}</td>
                      <td>{new Date(Date.parse(value.datetimestamp)).toLocaleDateString()}</td>
                    </tr>
                )
              }) :
              getMapEntries(userData).slice(1, 15).map(value => {
                return (
                    <tr>
                      <td>{value.username}</td>
                      <td>{value.score}</td>
                      <td>{value.powerups_used}</td>
                      <td>{new Date(Date.parse(value.datetimestamp)).toLocaleDateString()}</td>
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