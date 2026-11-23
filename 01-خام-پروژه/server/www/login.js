/* FAM-LAB-WORKFLOW-V1-LOGIN */
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
      if(typeof result?.user?.id!=='string'||!result.user.id||typeof result.user.revision!=='string'||!result.user.revision)throw Error('پاسخ حساب معتبر نیست؛ دوباره وارد شوید.');
      password.value='';
      // No credential is stored: a random notice locks other tabs, while the
      // temporary URL fragment binds this navigation to the account just used.
      try{localStorage.setItem('fam.session.notice.v1',crypto.randomUUID());}catch(_){}
      location.replace('app#fam-auth='+encodeURIComponent(JSON.stringify([result.user.id,result.user.revision])));
    }catch(error){show(error.message||'ارتباط با سرور برقرار نشد.');password.focus();}
    finally{button.disabled=false;}
  });
})();
