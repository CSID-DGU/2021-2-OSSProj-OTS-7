window.onload = () => {

    const inputEmail = document.getElementById('email');
    const inputPwConfirm = document.getElementById('passwordConfirm');
    const inputPassword = document.getElementById('password');
    const inputId = document.getElementById('id');
    const signUpForm = document.getElementById('signUp');

    inputEmail.addEventListener('blur', () => {
        fetch('/users/findUserByEmail', {
            method: 'POST',
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                email: inputEmail.value
            })
        })
            .then(data => {return data.json()})
            .then(result => {
                if(result.msg==="success"){
                    inputEmail.setCustomValidity("이미 존재하는 Email입니다.");
                }else{
                    inputEmail.setCustomValidity('');
                }
            });
    });

    inputPassword.addEventListener('keyup',()=>{
        if (inputPwConfirm.value !== inputPassword.value)
            inputPwConfirm.setCustomValidity('비밀번호가 일치하지 않습니다.');
        else {
            inputPwConfirm.setCustomValidity('');
        }
    });

    inputPwConfirm.addEventListener('keyup', () => {
        if (inputPwConfirm.value !== inputPassword.value)
            inputPwConfirm.setCustomValidity('비밀번호가 일치하지 않습니다.');
        else {
            inputPwConfirm.setCustomValidity('');
        }
    });

    signUpForm.addEventListener('submit',()=>{
        console.log(inputEmail.value,inputPassword.value,inputId.value);
        fetch('/users/createUser',{
            method : 'POST',
            headers : {
                'Content-Type' : 'application/json'
            },
            body : JSON.stringify({
                'email' : inputEmail.value,
                'password' : inputPassword.value,
                'id' : inputId.value
            })
        }).then(data => {
            return data.json()
        }).then(result => {
                console.log(result);
            if(result.msg === "success"){
                alert('회원가입 성공');
                location.href = "/login";
            }
            else{
                alert('회원가입 도중 예기치 않음 문제가 발생했습니다.');
            }
        }).catch(err=>{
            console.log("에상치 못한 문제 발생");
        })
    });

};