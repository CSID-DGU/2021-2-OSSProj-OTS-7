window.onload = () => {

    init();

    function init(){
        const inputEmailLogin = document.getElementById('emailLogin');
        const inputPasswordLogin = document.getElementById('passwordLogin')
        const btnLogin = document.getElementById('btnLogin');
        const btnLogout = document.getElementById('btnLogout');

        const inputEmail = document.getElementById('emailSignUp');
        const inputPwConfirm = document.getElementById('passwordConfirmSignUp');
        const inputPassword = document.getElementById('passwordSignUp');
        const inputName = document.getElementById('nameSignUp');
        const btnSignup = document.getElementById('btnSignup');

        btnSignup.addEventListener('click',()=>{
            let name = inputName.value;
            let password = inputPassword.value;
            console.log(name, password);

            signup(name, password)
                .then(data => {
                    if(data.msg == "success") {
                        alert('Success SignUp');
                        window.location.href = "/";
                    } else if(data.msg == "duplicate_name"){
                        alert('이름 중복입니다.')
                    }
                    else {
                        alert('error');
                    }
                })
                .catch(err=>{
                    console.log("error");
                    console.log(err);
                })
        });

        btnLogin.addEventListener('click',()=>{
            fetch('/users/login',{
                method:'POST',
                credentials: 'include',
                headers:{
                    'Content-Type' : 'application/json'
                },
                body : JSON.stringify({
                    name : nameLogin.value,
                    password : passwordLogin.value
                })
            })
            .then(res => res.json())
            .then(json => {
                if(json.msg==="failed"){
                    alert("failed Login");
                }else{
                    alert("success Login");
                    window.location.href ='/histories';
                }
            }).catch(err=>{
                console.log(err);
            });
        });
    }

    function signup(name,password) {
        return new Promise((resolve, reject) => {
            fetch('/signup/createUser',{
                method : 'POST',
                headers : {
                    'Content-Type' : 'application/json'
                },
                body : JSON.stringify({
                    'name' : name,
                    'password' : password,
                })
            })
            .then(result => {
                result.json()
                    .then(data => {
                        resolve(data);
                    })
            })
            .catch(err => {
                console.log("error in signup function");
                console.log(err);
                reject(err);
            });
        })
    }
};
