const state = { points: [], imgW: 0, imgH: 0, canvas: document.getElementById('poly_canvas'), ctx: null, img: null, dragging: -1, rtspJobId: null };
if (state.canvas) state.ctx = state.canvas.getContext('2d');

function show(id, data){ const el=document.getElementById(id); if (!el) return; el.textContent = typeof data === 'string' ? data : JSON.stringify(data, null, 2); }
async function api(url, body, out, method='POST'){ const r = await fetch(url,{method,headers:{'Content-Type':'application/json'},body:method==='GET'?undefined:JSON.stringify(body)}); const j = await r.json(); show(out, j); return j; }
function val(id){ const el=document.getElementById(id); return el ? el.value : ''; }
function maybeNum(v){ return v === '' || v == null ? null : Number(v); }
function setLog(id, text){ const el=document.getElementById(id); if (!el) return; el.textContent=text; el.scrollTop=el.scrollHeight; }

async function runCount(){ await api('/api/count-class',{labels_dir:val('count_labels_dir')},'count_result'); }
async function runCleanup(){ await api('/api/cleanup',{images_dir:val('cleanup_images_dir'),labels_dir:val('cleanup_labels_dir'),dry_run:document.getElementById('cleanup_dry_run')?.checked || false},'cleanup_result'); }
async function runSplit(){ await api('/api/split-dataset',{data_root:val('split_data_root'),train_ratio:Number(val('split_train_ratio')),random_seed:Number(val('split_seed'))},'split_result'); }
async function runBlank(){ await api('/api/blank-labels',{images_dir:val('blank_images_dir'),labels_dir:val('blank_labels_dir'),overwrite:document.getElementById('blank_overwrite')?.checked || false},'blank_result'); }
async function runRename(){ await api('/api/rename-pairs',{images_dir:val('rename_images_dir'),labels_dir:val('rename_labels_dir'),prefix:val('rename_prefix'),start:Number(val('rename_start')),digit:Number(val('rename_digit')),dry_run:document.getElementById('rename_dry_run')?.checked || false},'rename_result'); }
async function runVoc(){ syncMappingTextarea(); await api('/api/voc-to-yolo',{xml_folder:val('voc_xml_folder'),output_folder:val('voc_output_folder'),class_mapping:val('voc_class_mapping')},'voc_result'); }
async function runIds(){ await api('/api/change-ids',{labels_dir:val('ids_labels_dir'),mapping_text:val('ids_mapping_text')},'ids_result'); }
async function runFrames(){ await api('/api/extract-frames',{video_path:val('frames_video_path'),output_dir:val('frames_output_dir'),mode:val('frames_mode'),interval:Number(val('frames_interval')),quality:Number(val('frames_quality')),width:maybeNum(val('frames_width')),height:maybeNum(val('frames_height')),delete_source:document.getElementById('frames_delete_source')?.checked || false},'frames_result'); }
async function startRtsp(){ const j = await api('/api/rtsp/start',{rtsp_url:val('rtsp_url'),output_dir:val('rtsp_output_dir'),segment_minutes:Number(val('rtsp_segment_minutes')),total_duration:maybeNum(val('rtsp_total_duration')),prefix:val('rtsp_prefix')},'rtsp_result'); if (j.success) { state.rtspJobId = j.data.job_id; await refreshRtspList(); selectLatestRtspJob(); } }
async function refreshRtspList(){ const r = await fetch('/api/rtsp/list'); const j = await r.json(); const jobs = j.data.jobs || []; const sel = document.getElementById('rtspJobs'); if (!sel) return; sel.innerHTML = jobs.map(x=>`<option value="${x.job_id}">${x.job_id} · ${x.status} · ${x.prefix}</option>`).join('') || '<option value="">无任务</option>'; const summary = document.getElementById('rtspSummary'); if (summary) summary.innerHTML = jobs.length ? jobs.map(x=>`<div><strong>${x.job_id}</strong> · ${x.status} · ${x.prefix}<div class="small text-muted">${x.output_dir}</div></div>`).join('<hr class="my-2">') : '当前无任务'; if (state.rtspJobId) await refreshRtspStatus(state.rtspJobId); }
function selectLatestRtspJob(){ const sel = document.getElementById('rtspJobs'); if (sel && sel.options.length) { sel.selectedIndex = 0; state.rtspJobId = sel.value; refreshRtspStatus(state.rtspJobId); } }
function selectRtspJob(){ state.rtspJobId = document.getElementById('rtspJobs').value; refreshRtspStatus(state.rtspJobId); }
async function refreshRtspStatus(jobId){ if (!jobId) return; const r = await fetch(`/api/rtsp/status/${jobId}`); const j = await r.json(); show('rtsp_result', j); const data = j.data || {}; const lines = (data.logs || []).join('\n'); setLog('rtsp_result', JSON.stringify(j, null, 2) + '\n\n--- 日志 ---\n' + lines); }
async function stopRtsp(){ if (!state.rtspJobId) return; await api(`/api/rtsp/stop/${state.rtspJobId}`,{},'rtsp_result'); await refreshRtspStatus(state.rtspJobId); }
async function deleteRtsp(){ if (!state.rtspJobId) return; await api(`/api/rtsp/delete/${state.rtspJobId}`,{},'rtsp_result','DELETE'); state.rtspJobId = null; await refreshRtspList(); }

function resizeCanvasToImage(img){ if (!state.canvas) return; state.canvas.width = img.width; state.canvas.height = img.height; state.imgW = img.width; state.imgH = img.height; drawPoly(); updatePolyPreview(); }
function drawPoly(){ const c = state.ctx; if (!c || !state.canvas) return; c.clearRect(0,0,state.canvas.width,state.canvas.height); if(state.img) c.drawImage(state.img,0,0,state.canvas.width,state.canvas.height); if(state.points.length){ c.lineWidth=2; c.strokeStyle='#22c55e'; c.fillStyle='#3b82f6'; c.beginPath(); state.points.forEach((p,i)=>{ const x=p.x,y=p.y; if(i===0) c.moveTo(x,y); else c.lineTo(x,y); }); if(state.points.length>2) c.closePath(); c.stroke(); state.points.forEach((p,idx)=>{ c.fillStyle = idx===state.dragging ? '#ef4444' : '#3b82f6'; c.beginPath(); c.arc(p.x,p.y,idx===state.dragging?7:5,0,Math.PI*2); c.fill(); }); } updatePolyPreview(); }
function updatePolyPreview(){ const el = document.getElementById('poly_points_preview'); if (!el) return; if (!state.imgW || !state.imgH || !state.points.length){ el.value=''; return; } const pts = state.points.map(p => [Number((p.x / state.imgW).toFixed(6)), Number((p.y / state.imgH).toFixed(6))]); el.value = JSON.stringify(pts, null, 2); }
function canvasPos(e){ const rect = state.canvas.getBoundingClientRect(); return {x:(e.clientX-rect.left)*(state.canvas.width/rect.width), y:(e.clientY-rect.top)*(state.canvas.height/rect.height)}; }
function findPoint(x,y){ let best=-1, d=12; state.points.forEach((p,i)=>{ const dd=Math.hypot(p.x-x,p.y-y); if (dd<d){d=dd; best=i;}}); return best; }
if (state.canvas) {
  state.canvas.addEventListener('click', e=>{ if(!state.img) return; const p=canvasPos(e); if (findPoint(p.x,p.y) === -1) { state.points.push(p); drawPoly(); } });
  state.canvas.addEventListener('contextmenu', e=>{ e.preventDefault(); if(!state.img) return; state.points.pop(); drawPoly(); });
  state.canvas.addEventListener('mousedown', e=>{ if(!state.img) return; const p=canvasPos(e); state.dragging = findPoint(p.x,p.y); });
  state.canvas.addEventListener('mousemove', e=>{ if(state.dragging>=0){ const p=canvasPos(e); state.points[state.dragging]=p; drawPoly(); } });
  window.addEventListener('mouseup', ()=>{ state.dragging=-1; });
}
const fileInput=document.getElementById('poly_image'); if (fileInput) fileInput.addEventListener('change',()=>{ const f=fileInput.files[0]; if(!f) return; const img=new Image(); img.onload=()=>{ state.img=img; resizeCanvasToImage(img); show('poly_result','图片已加载，开始点击顶点'); }; img.onerror=()=>show('poly_result','图片加载失败'); img.src=URL.createObjectURL(f); });
function clearPoly(){ state.points=[]; drawPoly(); show('poly_result','已清空'); }
function undoPoly(){ state.points.pop(); drawPoly(); show('poly_result','已撤销'); }
async function savePoly(){ const body={image_width:state.imgW,image_height:state.imgH,points:state.points.map(p=>[p.x,p.y]),output_path:val('poly_output_path')}; await api('/api/polygon',body,'poly_result'); }
function switchPolySource(){ const type = document.getElementById('poly_source_type')?.value; const upload = document.getElementById('poly_upload_panel'); const video = document.getElementById('poly_video_panel'); if (!upload || !video) return; if (type === 'video') { upload.classList.add('d-none'); video.classList.remove('d-none'); } else { video.classList.add('d-none'); upload.classList.remove('d-none'); } }
async function loadPolyVideoFrame(){ const source = document.getElementById('poly_video_source')?.value.trim(); if (!source) { show('poly_result','请先输入 RTSP 地址或 MP4 路径'); return; } const img = new Image(); img.onload = () => { state.img = img; resizeCanvasToImage(img); show('poly_result','首帧已加载，开始点击顶点'); }; img.onerror = () => { show('poly_result','首帧加载失败，请确认视频路径或 RTSP 是否可访问'); }; img.src = `/api/polygon/frame-preview?source=${encodeURIComponent(source)}&t=${Date.now()}`; }

const search = document.getElementById('toolSearch');
if (search) search.addEventListener('input', () => {
  const q = search.value.trim().toLowerCase();
  document.querySelectorAll('.tool-item').forEach(card => {
    const title = (card.dataset.title || '').toLowerCase();
    card.style.display = title.includes(q) ? '' : 'none';
  });
  document.querySelectorAll('.tool-group').forEach(group => {
    const visible = group.querySelectorAll('.tool-item').length !== group.querySelectorAll('.tool-item[style*="display: none"]').length;
    group.style.display = visible ? '' : 'none';
  });
});

function addMappingRow(name='', idx=''){
  const list = document.getElementById('mappingList');
  if (!list) return;
  const row = document.createElement('div');
  row.className = 'mapping-row';
  row.innerHTML = `<input class="form-control form-control-sm map-name" placeholder="类别名" value="${name}"><input class="form-control form-control-sm map-id" placeholder="ID" value="${idx}"><button class="btn btn-outline-danger btn-sm" type="button">删除</button>`;
  row.querySelector('button').onclick = () => { row.remove(); syncMappingTextarea(); };
  row.querySelectorAll('input').forEach(i => i.addEventListener('input', syncMappingTextarea));
  list.appendChild(row);
  syncMappingTextarea();
}
function syncMappingTextarea(){
  const el = document.getElementById('voc_class_mapping');
  if (!el) return;
  const obj = {};
  document.querySelectorAll('.mapping-row').forEach(row => {
    const n = row.querySelector('.map-name').value.trim();
    const id = row.querySelector('.map-id').value.trim();
    if (n && id !== '') obj[n] = Number(id);
  });
  el.value = JSON.stringify(obj, null, 2);
}
async function scanVocClasses(){
  show('voc_result', '正在使用后端自动扫描类别（如果 tools/web_tools.py 选择自动映射，则执行时会自动生成）');
}

function pickDir(...ids){ const v = prompt('请输入本地目录路径（Windows 可直接粘贴绝对路径）'); if (!v) return; ids.forEach(id => { const el = document.getElementById(id); if (el) el.value = v; }); }
function pickFile(id){ const v = prompt('请输入本地文件路径'); if (!v) return; document.getElementById(id).value = v; }

addMappingRow('person', 0);
addMappingRow('car', 1);
refreshRtspList();
switchPolySource();