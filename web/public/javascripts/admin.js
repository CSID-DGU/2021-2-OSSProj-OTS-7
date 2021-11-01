window.onload = () => {

    const userTable = document.getElementById('userTable');

    init();

    function init() {
        fetch('/admin/userList')
            .then(data => data.json())
            .then(result => {
                setTable(result);
            });
    }

    function setTable(userList) {

        for (let index = 0; index < userList.length; index++) {
            const tr = document.createElement('tr');
            const userNum = document.createElement('td');
            const email = document.createElement('td');
            const name = document.createElement('td');
            const userType = document.createElement('td');
            const createAt = document.createElement('td');

            userNum.innerText = userList[index].id;
            email.innerText = userList[index].email;
            name.innerText = userList[index].name;
            userType.innerText = userList[index].userType;
            createAt.innerText = userList[index].createdAt;

            tr.append(userNum);
            tr.append(email);
            tr.append(name);
            tr.append(userType);
            tr.append(createAt);

            userTable.append(tr);
        }
    }
};