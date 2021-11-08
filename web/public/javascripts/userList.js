window.onload = () => {

  const userTable = document.getElementById('userTable');

  init();

  function init() {
    fetch('/histories/userList')
    .then(data => data.json())
    .then(result => {
      setTable(result);
      console.log(result)
    });
  }

  function setTable(userList) {

    for (let index = 0; index < userList.length; index++) {
      const tr = document.createElement('tr');
      const userNum = document.createElement('td');
      // const email = document.createElement('td');
      const name = document.createElement('td');
      const win = document.createElement('td');
      const loss = document.createElement('td');
      const points = document.createElement('td');

      userNum.innerText = userList[index].id;
      // email.innerText = userList[index].email;
      name.innerText = userList[index].name;
      win.innerText = userList[index].win;
      loss.innerText = userList[index].loss;
      points.innerText = userList[index].points;

      tr.append(userNum);
      // tr.append(email);
      tr.append(name);
      tr.append(win);
      tr.append(loss);
      tr.append(points);

      userTable.append(tr);
    }
  }
};
