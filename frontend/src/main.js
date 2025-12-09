// frontend/src/main.js
async function listFiles(){
  const res = await fetch('/api/files/list');
  const j = await res.json();
  const ul = document.getElementById('file-list');
  ul.innerHTML = '';
  j.files.forEach(f=>{
    const li = document.createElement('li');
    const cb = document.createElement('input');
    cb.type='checkbox'; cb.value = f.filename;
    li.appendChild(cb);
    li.appendChild(document.createTextNode(' ' + f.filename + ' (' + f.size + ' bytes)'));
    ul.appendChild(li);
  });
}
async function startAnalysis(){
  const cbs = Array.from(document.querySelectorAll('#file-list input[type=checkbox]:checked')).map(x=>x.value);
  if(cbs.length===0){ alert('select at least one file'); return;}
  const res = await fetch('/api/tasks/start', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({files:cbs})});
  const j = await res.json();
  const id = j.task_id;
  subscribeProgress();
  alert('task started: ' + id);
}
function subscribeProgress(){
  const ws = new WebSocket(`ws://${location.host}/ws/progress`);
  ws.onmessage = (e)=>{
    const obj = JSON.parse(e.data);
    document.getElementById('progress-log').innerText = JSON.stringify(obj, null, 2);
  }
}
document.getElementById('start-btn').addEventListener('click', startAnalysis);
listFiles();
