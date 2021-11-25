window.onload = () => {
  init();

  function init() {
    const inputName = document.getElementById('inputName');
    const btnFind = document.getElementById('btnFind');

    btnFind.addEventListener('click', () => {
      fetch('/histories/findUser', {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: inputName.value,
        }),
      })
        .then((res) => res.json())
        .then((json) => {
          if (json.msg === 'success finding') {
            alert('success Finding');
            window.location.href = '/users';
          } else {
            alert('failed Finding');
          }
        })
        .catch((err) => {
          console.log(err);
        });
    });
  }
};
