window.onload = () => {

    init();

    function init(){
        const btnLogout = document.getElementById('btnLogout');

        btnLogout.addEventListener('click',()=>{
            fetch('/users/logout',{
                method:'POST',
                credentials: 'include',
                headers:{
                    'Content-Type' : 'application/json'
                },
            })
            .then(res => res.json())
            .then(json => {
                if(json.msg !="failed"){
                alert("success Logout");
                                    window.location.href ='/';

                }else{
                    alert("failed Logout");
                }
            }).catch(err=>{
                console.log(err);
            });
        });
    }
};