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
            let email = inputEmail.value;
            let password = inputPassword.value;
            let name = inputName.value;
            console.log(email, password, name);

            signup(email, password, name)
                .then(data => {
                    if(data.msg == "success") {
                        alert('Success SignUp');
                        window.location.href = "/";
                    } else if(data.msg == "duplicate") {
                        alert('이메일 중복입니다.');
                    } else {
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
                    email : inputEmailLogin.value,
                    password : inputPasswordLogin.value
                })
            })
            .then(res => res.json())
            .then(json => {
                if(json.msg==="success"){
                    alert("success Login");
                    window.location.href ='/main/';
                }else{
                    alert("failed Login");
                }
            }).catch(err=>{
                console.log(err);
            });
        });
    }

    function signup(email, password, name) {
        return new Promise((resolve, reject) => {
            fetch('/signup/createUser',{
                method : 'POST',
                headers : {
                    'Content-Type' : 'application/json'
                },
                body : JSON.stringify({
                    'email' : email,
                    'password' : password,
                    'name' : name
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