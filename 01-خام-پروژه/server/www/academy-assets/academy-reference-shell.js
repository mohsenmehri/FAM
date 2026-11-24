(() => {
  'use strict';
  const $ = (id) => document.getElementById(id);
  const root = $('app-root');
  if (!root || document.querySelector('.app-shell')) return;

  const oldHeader = document.querySelector('.fa-topbar');
  const oldButtons = ['btn-paths','btn-placement','btn-tree','btn-lessons','btn-simulators','btn-blueprint','btn-coverage','btn-glossary','btn-back-paths']
    .map($).filter(Boolean);
  const stageBar = $('fam-stage4-bar');
  const searchWrap = $('s4-search-wrap');
  const planner = $('fam-stage4-panel');

  function el(tag, cls, text) {
    const node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text !== undefined) node.textContent = text;
    return node;
  }
  const skip = el('a','skip-link','پرش به محتوا'); skip.href='#app-root';
  const backdrop = el('div','fam-campus-backdrop'); backdrop.setAttribute('aria-hidden','true');
  document.body.insertBefore(backdrop, document.body.firstChild);
  document.body.insertBefore(skip, backdrop);

  const paths = {
    home: 'M3 10.5 12 3l9 7.5M5.5 9.5V20h13V9.5M10 20v-6h4v6',
    route: 'M6 19a2 2 0 1 0 0-4 2 2 0 0 0 0 4ZM18 9a2 2 0 1 0 0-4 2 2 0 0 0 0 4ZM8 17h6.5a3.5 3.5 0 0 0 0-7h-5a3.5 3.5 0 0 1 0-7H16',
    book: 'M4 5.5A2.5 2.5 0 0 1 6.5 3H20v15H6.5A2.5 2.5 0 0 0 4 20.5v-15ZM4 20.5A2.5 2.5 0 0 1 6.5 23H20M9 7.5h7M9 11h5',
    chart: 'M4 20V10M10 20V4M16 20v-8M21 20H3',
    glossary: 'M4 5.5A2.5 2.5 0 0 1 6.5 3H20v15H6.5A2.5 2.5 0 0 0 4 20.5v-15ZM9 7h7M9 11h7M9 15h4',
    search: 'M11 18a7 7 0 1 0 0-14 7 7 0 0 0 0 14ZM20 20l-4-4',
    menu: 'M4 7h16M4 12h16M4 17h16',
    sun: 'M12 16a4 4 0 1 0 0-8 4 4 0 0 0 0 8ZM12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4',
    moon: 'M20 14.5A8 8 0 0 1 9.5 4 8 8 0 1 0 20 14.5Z',
    user: 'M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8ZM4.5 20.5a7.5 7.5 0 0 1 15 0',
    help: 'M9.1 9a3 3 0 1 1 5.8 1c-.7 1.2-2.9 1.6-2.9 3.5M12 17.5h.01M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z'
  };
  function icon(name, size=18) {
    const svg = document.createElementNS('http://www.w3.org/2000/svg','svg');
    svg.setAttribute('viewBox','0 0 24 24');
    svg.setAttribute('width',String(size));
    svg.setAttribute('height',String(size));
    svg.setAttribute('fill','none');
    svg.setAttribute('stroke','currentColor');
    svg.setAttribute('stroke-width','1.8');
    svg.setAttribute('stroke-linecap','round');
    svg.setAttribute('stroke-linejoin','round');
    svg.setAttribute('aria-hidden','true');
    svg.classList.add('icon');
    const p=document.createElementNS('http://www.w3.org/2000/svg','path');
    p.setAttribute('d',paths[name] || paths.book);
    svg.appendChild(p);
    return svg;
  }
  const shell = el('div','app-shell');
  const sidebar = el('aside','sidebar');
  sidebar.id='academy-sidebar';
  const brand = el('a','brand');
  brand.href='#app-root';
  brand.setAttribute('aria-label','FAM Academy — خانه');
  const logo=el('span','brand-logo'); logo.setAttribute('aria-hidden','true');
  const brandCopy=el('span','brand-copy');
  const brandName=el('b','ltr','FAM Academy');
  const brandSub=el('small','ltr','NETWORK ENGINEERING SCHOOL');
  brandCopy.append(brandName,brandSub); brand.append(logo,brandCopy);

  const nav=el('nav','side-nav');
  nav.setAttribute('aria-label','ناوبری اصلی');
  const navItems=[
    ['home','خانه و مسیر فعلی','گام بعدی و وضعیت سطح شما','home','home'],
    ['placement','تعیین سطح و دانشکده','انتخاب دستی یا آزمون ۴گزینه‌ای','chart','placement'],
    ['paths','نقشهٔ درس‌های آماده','پیش‌نیازها و ترتیب مطالعه','route','paths'],
    ['lessons','فهرست درس‌ها','جست‌وجو و مطالعهٔ درس‌ها','book','lessons'],
    ['simulators','شبیه‌ساز و آزمایشگاه IOS','ARP، VLAN، OSPF و ترمینال','chart','simulators'],
    ['tree','درخت جامع ۷ دانشکده','از مبانی تا CCIE و CCDE','route','tree'],
    ['progress','پیشرفت و برنامهٔ من','برنامهٔ روزانه و درس‌های کامل‌شده','chart','progress'],
    ['coverage','پوشش فرمان‌های IOS','مرجع دستورات سیسکو','book','coverage'],
    ['glossary','واژه‌نامه','اصطلاحات شبکه','glossary','glossary']
  ];
  const navLinks=new Map();
  for(const [id,label,hint,ico,action] of navItems){
    const a=el('a','side-link'); a.href='#'+action; a.dataset.action=action;
    const i=el('span','side-icon'); i.append(icon(ico,20));
    const copy=el('span','side-copy'); copy.append(el('span','side-label',label),el('span','side-hint',hint));
    a.append(i,copy);
    const beam=document.createElementNS('http://www.w3.org/2000/svg','svg');
    beam.setAttribute('class','fam-nav-beam'); beam.setAttribute('viewBox','0 0 100 100');
    beam.setAttribute('preserveAspectRatio','none'); beam.setAttribute('aria-hidden','true'); beam.setAttribute('focusable','false');
    const border=document.createElementNS('http://www.w3.org/2000/svg','rect');
    for(const [key,value] of Object.entries({x:1,y:1,width:98,height:98,rx:10,pathLength:100,'vector-effect':'non-scaling-stroke'})) border.setAttribute(key,value);
    beam.appendChild(border); a.appendChild(beam);
    nav.append(a); navLinks.set(id,a);
  }
  const pathCard=el('div','side-path');
  pathCard.append(el('div','side-path-head','مسیرهای آموزشی'),el('div','side-path-name','Curriculum 5.0'));
  const pathMeter=el('div','meter'); const pathFill=el('i'); pathMeter.append(pathFill);
  const pathMeta=el('div','side-path-meta','');
  pathCard.append(pathMeter,pathMeta);
  fetch('/academy-assets/curriculum-catalog.json?v=20261123i',{cache:'no-store'})
    .then(response=>{if(!response.ok)throw new Error('catalog unavailable');return response.json();})
    .then(catalog=>{
      const total=(catalog.paths||[]).reduce((sum,path)=>sum+(path.courses||[]).reduce((courseSum,course)=>courseSum+(course.lessons||[]).length,0),0);
      pathMeta.textContent=`${total.toLocaleString('fa-IR')} درس آموزشی`;
    })
    .catch(()=>{pathMeta.textContent='فهرست درس‌ها در دسترس نیست';});
  const sideFoot=el('div','side-foot');
  sideFoot.append(el('span','live-dot'),el('span','','محتوای آموزشی و راهنمای تمرین'));
  sidebar.append(brand,nav,pathCard,sideFoot);

  const appMain=el('div','app-main');
  const topbar=el('header','topbar');
  const menuButton=el('button','icon-btn academy-menu-toggle'); menuButton.type='button';
  menuButton.setAttribute('aria-controls','academy-sidebar'); menuButton.setAttribute('aria-expanded','true');
  menuButton.setAttribute('aria-label','باز و بسته کردن منو'); menuButton.title='باز و بسته کردن منو'; menuButton.append(icon('menu',18));
  const topTitle=el('div','academy-top-title');
  topTitle.append(el('b','','آکادمی فام'),el('small','ltr','FAM ACADEMY · LEARNING'));
  const mobileBrand=el('a','brand brand-mobile'); mobileBrand.href='#app-root'; mobileBrand.append(el('span','brand-logo'));
  const crumbs=el('nav','crumbs academy-route-crumbs'); crumbs.setAttribute('aria-label','مسیر صفحه');
  const topActions=el('div','top-actions');
  const search=el('button','search-trigger'); search.type='button'; search.setAttribute('aria-label','جست‌وجو');
  search.append(icon('search',16),el('span','','جست‌وجو'),el('kbd','','Ctrl K'));
  const streak=el('a','top-chip'); streak.href='#/placement'; streak.append(el('span','','تغییر سطح / تعیین سطح'));
  const theme=el('button','icon-btn theme-toggle'); theme.type='button';
  const help=el('button','icon-btn'); help.type='button'; help.setAttribute('aria-label','راهنمای آکادمی'); help.title='راهنمای آکادمی'; help.append(icon('help',18));
  const progress=el('a','icon-btn'); progress.href='#/progress'; progress.setAttribute('aria-label','پیشرفت و برنامه مطالعه'); progress.title='پیشرفت و برنامه مطالعه'; progress.append(icon('user',18));
  topActions.append(search,streak,theme,help,progress);
  topbar.append(menuButton,topTitle,mobileBrand,crumbs,topActions);

  const sectionHead=el('section','academy-section-head');
  sectionHead.setAttribute('aria-label','جابه‌جایی بین بخش‌های FAM');
  const heading=el('div','academy-section-heading');
  heading.append(el('span','academy-head-mark','FAM'));
  const userName=window.FamAcademyBridge?.user?.username||'';
  const subText='NETWORK ENGINEERING ACADEMY'+(userName?' · '+userName:'');
  const headingCopy=el('div'); headingCopy.append(el('h2','','بخش فعال: آکادمی فام'),el('div','academy-section-sub',subText));
  heading.append(headingCopy);
  const allowedViews=window.FamAcademyBridge?.allowedViews||{panel:true,equipment:true};
  const sectionActions=el('div','academy-section-actions');
  const switchTargets=[];
  if(allowedViews.panel!==false)switchTargets.push(['/app#/panel','پایگاه داده ←','academy-section-switch academy-section-switch-primary','academy-to-database']);
  if(allowedViews.equipment!==false)switchTargets.push(['/app#/equipment/home','مدیریت تجهیزات ←','academy-section-switch academy-section-switch-primary','academy-to-equipment']);
  switchTargets.push(['/app#/chooser','انتخاب بخش','academy-section-switch','academy-workspace-picker']);
  for(const [href,label,cls,id] of switchTargets){
    const link=el('a',cls,label);link.href=href;link.id=id;sectionActions.append(link);
  }
  const hiddenTools=el('div','sr-only');hiddenTools.hidden=true;
  for(const button of oldButtons)hiddenTools.append(button);
  sectionHead.append(heading,sectionActions);

  root.className='page';
  root.removeAttribute('style');
  appMain.append(topbar,sectionHead);
  if(searchWrap)appMain.append(searchWrap);
  appMain.append(root,hiddenTools);
  for(const node of [stageBar,planner]) if(node) appMain.append(node);

  const bottom=el('nav','bottom-nav'); bottom.setAttribute('aria-label','ناوبری اصلی موبایل');
  const bottomActions=[['home','خانه'],['placement','تعیین سطح'],['lessons','درس‌ها'],['simulators','شبیه‌ساز'],['tree','دانشکده‌ها']];
  for(const [action,label] of bottomActions){
    const a=el('a',''); a.href='#'+action; a.dataset.action=action;
    a.append(icon(action==='placement'||action==='simulators'?'chart':action==='tree'?'route':action==='lessons'?'book':'home',20),el('span','',label));
    bottom.append(a);
  }
  shell.append(sidebar,appMain,bottom);
  document.body.insertBefore(shell,oldHeader || root);
  oldHeader?.remove();

  function setActive(action){
    const group=action==='home'?'home':action==='placement'?'placement':action==='tree'?'tree':action==='paths'?'paths':action==='lessons'?'lessons':action==='simulators'?'simulators':action==='coverage'?'coverage':action==='glossary'?'glossary':action==='progress'?'progress':'home';
    for(const [id,a] of navLinks){const active=id===group;a.classList.toggle('active',active);if(active)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');}
    const labels={home:'خانه و مسیر فعلی',placement:'انتخاب سطح و آزمون تعیین سطح',tree:'درخت جامع ۷ دانشکده',paths:'نقشهٔ درس‌های آماده',lessons:'فهرست درس‌ها',simulators:'شبیه‌ساز و آزمایشگاه IOS',progress:'پیشرفت و برنامهٔ من',glossary:'واژه‌نامه',coverage:'پوشش فرمان‌های IOS'};
    crumbs.replaceChildren(el('span','crumb current',labels[group]||'آکادمی'));
    document.title=(labels[group]||'آکادمی')+' — FAM Academy';
  }
  function clickExisting(id){const b=$(id);if(b)b.click();}
  function showPlanner(target){
    if(planner){planner.classList.add('open');planner.scrollIntoView({behavior:'smooth',block:'start'});}
    if(target){const node=$(target);if(node)node.scrollIntoView({behavior:'smooth',block:'center'});}
  }
  function scrollTopClean(){
    window.scrollTo({top:0,behavior:'auto'});
  }
  function action(action){
    setActive(action);
    if(action==='placement'){
      if(location.hash !== '#/placement') location.hash = '#/placement'; else clickExisting('btn-placement');
      scrollTopClean();
    }
    else if(action==='tree'){
      if(location.hash !== '#/tree') location.hash = '#/tree'; else clickExisting('btn-tree');
      scrollTopClean();
    }
    else if(action==='paths'){
      if(location.hash !== '#/paths') location.hash = '#/paths'; else { location.hash = '#/dashboard'; location.hash = '#/paths'; }
      scrollTopClean();
    }
    else if(action==='home'){
      if(location.hash !== '#/dashboard') location.hash = '#/dashboard'; else clickExisting('btn-paths');
      scrollTopClean();
    }
    else if(action==='lessons'){
      if(location.hash !== '#/lessons') location.hash = '#/lessons'; else clickExisting('btn-lessons');
      scrollTopClean();
    }
    else if(action==='simulators'){
      if(location.hash !== '#/simulators') location.hash = '#/simulators'; else clickExisting('btn-simulators');
      scrollTopClean();
    }
    else if(action==='progress'){
      if(location.hash !== '#/progress') location.hash='#/progress'; else window.FamJourney?.renderProgress();
      scrollTopClean();
    }
    else if(action==='coverage'){
      if(location.hash !== '#/coverage') location.hash = '#/coverage'; else clickExisting('btn-coverage');
      scrollTopClean();
    }
    else if(action==='sample'){clickExisting('btn-blueprint');scrollTopClean();}
    else if(action==='planner'){clickExisting('s4-toggle-btn');showPlanner();}
    else if(action==='glossary'){
      if(location.hash !== '#/glossary') location.hash = '#/glossary'; else clickExisting('btn-glossary');
      scrollTopClean();
    }
  }
  shell.addEventListener('click',(event)=>{
    const a=event.target.closest('[data-action]');
    if(!a)return;
    event.preventDefault();
    action(a.dataset.action);
    if(shell.classList.contains('academy-menu-mobile-open')){shell.classList.remove('academy-menu-mobile-open');syncMenu(false);}
  });
  function syncMenu(open){
    menuButton.setAttribute('aria-expanded',String(open));
    menuButton.classList.toggle('is-collapsed',!open);
    sidebar.inert=!open; sidebar.setAttribute('aria-hidden',String(!open));
  }
  const mobile=window.matchMedia('(max-width: 860px)').matches;
  syncMenu(!mobile);
  menuButton.addEventListener('click',()=>{
    if(window.matchMedia('(max-width: 860px)').matches){
      const open=shell.classList.toggle('academy-menu-mobile-open');syncMenu(open);
    }else{
      const collapsed=shell.classList.toggle('academy-menu-collapsed');syncMenu(!collapsed);
    }
  });
  search.addEventListener('click',()=>{
    if(location.hash !== '#/lessons') location.hash = '#/lessons';
    setTimeout(()=>{
      const input=$('fam-lessons-search')||$('s4-search');
      if(input){input.focus();scrollTopClean();}
    },60);
  });
  document.addEventListener('keydown',(event)=>{
    if((event.ctrlKey||event.metaKey)&&event.key.toLowerCase()==='k'){event.preventDefault();search.click();}
  });
  function syncTheme(){
    const light=document.documentElement.dataset.theme==='light';
    theme.replaceChildren(icon(light?'moon':'sun',18));
    theme.setAttribute('aria-label',light?'تغییر به تم تیره':'تغییر به تم روشن');
    theme.title=light?'تغییر به تم تیره':'تغییر به تم روشن';
    theme.setAttribute('aria-pressed',String(light));
  }
  syncTheme();
  theme.addEventListener('click',()=>{
    const next=document.documentElement.dataset.theme==='light'?'dark':'light';
    document.documentElement.dataset.theme=next;
    try{localStorage.setItem('fam.academy.theme',next);localStorage.setItem('fam.ui.theme',next==='light'?'light':'original');}catch(_){}
    syncTheme();
  });
  help.addEventListener('click',()=>{
    let dialog=$('academy-help-dialog');
    if(!dialog){
      dialog=el('dialog','card');dialog.id='academy-help-dialog';
      const close=el('button','btn primary','بستن');close.type='button';close.addEventListener('click',()=>dialog.close());
      dialog.append(el('h2','','راهنمای آکادمی'),el('p','','از منوی کناری مسیر یادگیری یا درس‌ها را باز کن. برای برنامه مطالعه، نقشه راه را ببین. هر درس شامل توضیح، توپولوژی، فرمان‌های IOS و بخش راستی‌آزمایی است.'),close);
      document.body.append(dialog);
    }
    if(!dialog.open)dialog.showModal();
  });
  progress.addEventListener('click',(event)=>{event.preventDefault();action('progress');});
  function syncActiveFromHash(){
    const h=location.hash;
    if(h==='#/progress')setActive('progress');
    else if(h==='#/placement')setActive('placement');
    else if(h==='#/tree')setActive('tree');
    else if(h==='#/paths')setActive('paths');
    else if(h==='#/lessons')setActive('lessons');
    else if(h==='#/simulators'||h==='#/labs')setActive('simulators');
    else if(h==='#/coverage')setActive('coverage');
    else if(h==='#/glossary')setActive('glossary');
    else if(h==='#/dashboard'||!h)setActive('home');
  }
  window.addEventListener('hashchange', syncActiveFromHash);
  streak.addEventListener('click',(event)=>{event.preventDefault();action('placement');});
  syncActiveFromHash();
  const s4Toggle=$('s4-toggle-btn');
  if(s4Toggle)s4Toggle.addEventListener('click',()=>{setActive('planner');}, {once:false});
  const progressText=$('s4-progress-text');
  function syncSidebarProgress(){
    const m=progressText?.textContent||'';
    if(m){pathFill.style.width=(m.match(/\((\d+)٪\)/)?.[1]||'0')+'%';}
  }
  const FAC_SHORT={f0:'دانشکده ۰ · مبانی',f1:'دانشکده ۱ · CCNA',f2:'دانشکده ۲ · R&S',f3:'دانشکده ۳ · CCNP',f4:'دانشکده ۴ · تخصصی',f5:'دانشکده ۵ · CCIE',f6:'دانشکده ۶ · CCDE'};
  function syncFacultyChip(){
    const stage=window.FamAcademyBridge?.progress?.profile?.currentStage||'';
    const done=Boolean(window.FamAcademyBridge?.progress?.profile?.onboardingComplete);
    const label=(done&&FAC_SHORT[stage])?`سطح فعال: ${FAC_SHORT[stage]}`:'انتخاب سطح / آزمون تعیین سطح';
    const sp=streak.querySelector('span');
    if(sp)sp.textContent=label;
    streak.classList.toggle('lit', !done);
  }
  syncFacultyChip();
  const observer=progressText?new MutationObserver(syncSidebarProgress):null;
  if(observer&&progressText)observer.observe(progressText,{childList:true,subtree:true,characterData:true});
  window.addEventListener('fam-academy-progress-updated',()=>{setTimeout(()=>{syncSidebarProgress();syncFacultyChip();},0);});
})();