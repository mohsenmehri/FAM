(() => {
  'use strict';
  const form=document.getElementById('login-form');
  const username=document.getElementById('username');
  const password=document.getElementById('password');
  const button=document.getElementById('submit');
  const message=document.getElementById('message');
  const show=value=>{message.textContent=value||'';};
  form.addEventListener('submit',async event=>{
    event.preventDefault();show('');
    if(!form.reportValidity())return;
    button.disabled=true;
    try{
      const response=await fetch('api/login',{method:'POST',headers:{'Content-Type':'application/json'},credentials:'same-origin',cache:'no-store',body:JSON.stringify({username:username.value.trim(),password:password.value})});
      const result=await response.json().catch(()=>({error:'پاسخ سرور معتبر نیست.'}));
      if(!response.ok)throw Error(result.error||'ورود انجام نشد.');
      password.value='';
      location.replace('app');
    }catch(error){show(error.message||'ارتباط با سرور برقرار نشد.');password.focus();}
    finally{button.disabled=false;}
  });
})();
