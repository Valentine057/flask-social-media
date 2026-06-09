(function(){
  const newPw = document.getElementById('newPassword');
  const confirmPw = document.getElementById('confirmPassword');
  const msg = document.getElementById('pwMessage');
  const btn = document.getElementById('changePwBtn');
  const pwForm = document.getElementById('passwordForm');
  const cancel = document.getElementById('pwCancel');

  function validate() {
    if (!newPw.value && !confirmPw.value) { msg.style.display='none'; btn.disabled=false; return; }
    if (newPw.value !== confirmPw.value) {
      msg.textContent = 'Passwords do not match.'; msg.style.display='block'; btn.disabled = true;
    } else if (newPw.value.length < 8) {
      msg.textContent = 'Password must be at least 8 characters.'; msg.style.display='block'; btn.disabled = true;
    } else { msg.style.display='none'; btn.disabled=false; }
  }

  newPw.addEventListener('input', validate);
  confirmPw.addEventListener('input', validate);

  cancel.addEventListener('click', function(){
    newPw.value = ''; confirmPw.value = ''; document.getElementById('currentPassword').value = ''; validate();
  });

  pwForm.addEventListener('submit', function(e){
    validate();
    if (btn.disabled) e.preventDefault();
  });
})();
