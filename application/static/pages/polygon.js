(function(){
  'use strict';

  const PolygonPage = {};
  window.PolygonPage = PolygonPage;

  const state = {
    image: null,
    imageUrl: '',
    imageWidth: 0,
    imageHeight: 0,
    points: [],
    draggingIndex: -1,
    dpr: window.devicePixelRatio || 1,
    rafPending: false,
    mode: 'upload',
  };

  const canvas = document.getElementById('poly_canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const uploadInput = document.getElementById('poly_image');
  const sourceType = document.getElementById('poly_source_type');
  const uploadPanel = document.getElementById('poly_upload_panel');
  const rtspPanel = document.getElementById('poly_rtsp_panel');
  const mp4Panel = document.getElementById('poly_mp4_panel');
  const rtspSource = document.getElementById('poly_rtsp_source');
  const mp4Input = document.getElementById('poly_mp4_file');
  const preview = document.getElementById('poly_points_preview');
  const resultBox = document.getElementById('poly_result');
  const loadRtspFrameBtn = document.getElementById('loadPolyRtspFrameBtn');
  const loadMp4FrameBtn = document.getElementById('loadPolyMp4FrameBtn');
  const downloadTxtBtn = document.getElementById('downloadPolyTxtBtn');

  function setMessage(text, kind){ resultBox.className = 'alert mb-0 ' + (kind || 'alert-info'); resultBox.textContent = text; }
  function resizeCanvas(){ const rect = canvas.getBoundingClientRect(); const width = Math.max(640, Math.floor(rect.width || 0)); const height = Math.max(420, Math.floor(rect.height || Math.min(window.innerHeight * 0.58, 620))); canvas.style.height = height + 'px'; canvas.width = Math.floor(width * state.dpr); canvas.height = Math.floor(height * state.dpr); ctx.setTransform(state.dpr, 0, 0, state.dpr, 0, 0); scheduleRender(); }
  function scheduleRender(){ if (state.rafPending) return; state.rafPending = true; requestAnimationFrame(function(){ state.rafPending = false; render(); }); }
  function getCanvasPoint(evt){ const rect = canvas.getBoundingClientRect(); return { x: evt.clientX - rect.left, y: evt.clientY - rect.top }; }
  function imageRect(){ const cw = canvas.clientWidth; const ch = canvas.clientHeight; if (!state.image || !state.imageWidth || !state.imageHeight) return { x: 0, y: 0, w: cw, h: ch }; const scale = Math.min(cw / state.imageWidth, ch / state.imageHeight); const w = state.imageWidth * scale; const h = state.imageHeight * scale; return { x: (cw - w) / 2, y: (ch - h) / 2, w, h }; }
  function pointToImage(pt){ const rect = imageRect(); return { x: (pt.x - rect.x) * state.imageWidth / rect.w, y: (pt.y - rect.y) * state.imageHeight / rect.h }; }
  function pointToCanvas(pt){ const rect = imageRect(); return { x: rect.x + pt.x * rect.w / state.imageWidth, y: rect.y + pt.y * rect.h / state.imageHeight }; }
  function clampPoint(pt){ return { x: Math.max(0, Math.min(state.imageWidth, pt.x)), y: Math.max(0, Math.min(state.imageHeight, pt.y)) }; }
  function updatePreview(){ if (!state.points.length || !state.imageWidth || !state.imageHeight) { preview.value = ''; return; } preview.value = JSON.stringify(state.points.map(function(pt){ return [Number((pt.x / state.imageWidth).toFixed(6)), Number((pt.y / state.imageHeight).toFixed(6))]; }), null, 2); }
  function render(){ const cw = canvas.clientWidth; const ch = canvas.clientHeight; ctx.clearRect(0, 0, cw, ch); ctx.fillStyle = '#ffffff'; ctx.fillRect(0, 0, cw, ch); if (!state.image) { ctx.fillStyle = '#94a3b8'; ctx.font = '16px system-ui, sans-serif'; ctx.textAlign = 'center'; ctx.fillText('请先上传图片或加载首帧', cw / 2, ch / 2 - 10); ctx.fillText('然后点击画布开始绘制多边形', cw / 2, ch / 2 + 18); updatePreview(); return; } const rect = imageRect(); ctx.drawImage(state.image, rect.x, rect.y, rect.w, rect.h); if (state.points.length) { ctx.save(); ctx.lineWidth = 2; ctx.strokeStyle = '#2563eb'; ctx.fillStyle = '#2563eb'; ctx.beginPath(); state.points.forEach(function(pt, index){ const canvasPt = pointToCanvas(pt); if (index === 0) ctx.moveTo(canvasPt.x, canvasPt.y); else ctx.lineTo(canvasPt.x, canvasPt.y); }); if (state.points.length > 1) ctx.closePath(); ctx.stroke(); state.points.forEach(function(pt, index){ const canvasPt = pointToCanvas(pt); ctx.beginPath(); ctx.arc(canvasPt.x, canvasPt.y, 5, 0, Math.PI * 2); ctx.fill(); ctx.fillStyle = '#ffffff'; ctx.font = '12px system-ui, sans-serif'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(String(index + 1), canvasPt.x, canvasPt.y - 1); ctx.fillStyle = '#2563eb'; }); ctx.restore(); } updatePreview(); }
  function loadImageFromUrl(url, filename){ if (!url) return; const img = new Image(); img.onload = function(){ state.image = img; state.imageWidth = img.naturalWidth || img.width; state.imageHeight = img.naturalHeight || img.height; state.points = []; state.draggingIndex = -1; state.imageUrl = url; setMessage('已加载 ' + (filename || '图片') + '，请在画布中点击绘制多边形。', 'alert-success'); scheduleRender(); }; img.onerror = function(){ setMessage('图片加载失败，请检查文件是否有效或浏览器无法访问该图片地址。', 'alert-danger'); }; img.src = url; }
  function buildPolygonText(){ if (!state.image || state.points.length < 3) throw new Error('多边形至少需要 3 个点。'); return JSON.stringify({ image_width: state.imageWidth, image_height: state.imageHeight, points: state.points.map(function(pt){ return [Number((pt.x / state.imageWidth).toFixed(6)), Number((pt.y / state.imageHeight).toFixed(6))]; }) }, null, 2); }
  function downloadPolyTxt(){ try { const text = buildPolygonText(); const blob = new Blob([text], { type: 'text/plain;charset=utf-8' }); const url = URL.createObjectURL(blob); const a = document.createElement('a'); a.href = url; a.download = 'polygon_coords.txt'; document.body.appendChild(a); a.click(); a.remove(); setTimeout(function(){ URL.revokeObjectURL(url); }, 1000); setMessage('已生成 TXT 下载。', 'alert-success'); } catch (err) { setMessage(err.message || '无法下载 TXT。', 'alert-danger'); } }
  function switchPolySource(){
    state.mode = sourceType.value;
    uploadPanel.classList.toggle('d-none', state.mode !== 'upload');
    rtspPanel.classList.toggle('d-none', state.mode !== 'rtsp');
    mp4Panel.classList.toggle('d-none', state.mode !== 'mp4');
  }
  async function loadPolyFrame(source, filename){
    if (!source) { setMessage('请输入有效的输入源。', 'alert-danger'); return; }
    try {
      setMessage('正在请求首帧，请稍候...', 'alert-info');
      const resp = await fetch('/polygon/frame-preview?source=' + encodeURIComponent(source));
      const data = await resp.json();
      if (!resp.ok || !data.success || !data.image_url) throw new Error(data.message || ('首帧加载失败（HTTP ' + resp.status + '）'));
      loadImageFromUrl(data.image_url + '?t=' + Date.now(), data.filename || filename || '首帧');
    } catch (err) { setMessage(err.message || '加载首帧失败。', 'alert-danger'); }
  }
  async function loadPolyRtspFrame(){ const source = (rtspSource.value || '').trim(); if (!source) { setMessage('请输入 RTSP 地址。', 'alert-danger'); return; } await loadPolyFrame(source, 'RTSP 首帧'); }
  async function loadPolyMp4Frame(){
    const file = mp4Input && mp4Input.files && mp4Input.files[0];
    if (!file) { setMessage('请选择 MP4 文件。', 'alert-danger'); return; }

    const url = URL.createObjectURL(file);
    try {
      setMessage('正在读取 MP4 首帧，请稍候...', 'alert-info');
      const video = document.createElement('video');
      video.preload = 'auto';
      video.muted = true;
      video.playsInline = true;
      video.src = url;

      await new Promise(function(resolve, reject){
        video.addEventListener('loadeddata', function(){ resolve(); }, { once: true });
        video.addEventListener('error', function(){ reject(new Error('MP4 文件加载失败，请确认文件可播放。')); }, { once: true });
      });

      if (!video.videoWidth || !video.videoHeight) throw new Error('无法读取 MP4 尺寸信息。');
      video.currentTime = 0;
      await new Promise(function(resolve, reject){
        video.addEventListener('seeked', function(){ resolve(); }, { once: true });
        video.addEventListener('error', function(){ reject(new Error('MP4 首帧定位失败。')); }, { once: true });
      });

      const offscreen = document.createElement('canvas');
      offscreen.width = video.videoWidth;
      offscreen.height = video.videoHeight;
      const offCtx = offscreen.getContext('2d');
      offCtx.drawImage(video, 0, 0, offscreen.width, offscreen.height);
      loadImageFromUrl(offscreen.toDataURL('image/jpeg', 0.95), file.name + ' 首帧');
    } catch (err) {
      setMessage(err.message || 'MP4 首帧读取失败。', 'alert-danger');
    } finally {
      setTimeout(function(){ URL.revokeObjectURL(url); }, 1000);
    }
  }
  function undoPoly(){ if (!state.points.length) return; state.points.pop(); updatePreview(); scheduleRender(); }

  PolygonPage.downloadTxt = downloadPolyTxt;
  PolygonPage.loadRtspFrame = loadPolyRtspFrame;
  PolygonPage.loadMp4Frame = loadPolyMp4Frame;
  PolygonPage.switchSource = switchPolySource;
  PolygonPage.undo = undoPoly;

  if (uploadInput) uploadInput.addEventListener('change', function(){ const file = uploadInput.files && uploadInput.files[0]; if (!file) return; const url = URL.createObjectURL(file); if (state.imageUrl && state.imageUrl.startsWith('blob:')) URL.revokeObjectURL(state.imageUrl); loadImageFromUrl(url, file.name); });
  if (sourceType) sourceType.addEventListener('change', switchPolySource);
  if (rtspSource) rtspSource.addEventListener('change', function(){ if (state.mode === 'rtsp' && rtspSource.value.trim()) loadPolyRtspFrame(); });
  if (mp4Input) mp4Input.addEventListener('change', function(){ if (state.mode === 'mp4' && mp4Input.files && mp4Input.files[0]) loadPolyMp4Frame(); });
  if (loadRtspFrameBtn) loadRtspFrameBtn.addEventListener('click', loadPolyRtspFrame);
  if (loadMp4FrameBtn) loadMp4FrameBtn.addEventListener('click', loadPolyMp4Frame);
  if (downloadTxtBtn) downloadTxtBtn.addEventListener('click', downloadPolyTxt);
  window.addEventListener('contextmenu', function(evt){ if (evt.target === canvas) evt.preventDefault(); });
  canvas.addEventListener('pointerdown', function(evt){ if (evt.button === 2) { evt.preventDefault(); if (!state.points.length) return; state.points.pop(); updatePreview(); scheduleRender(); return; } if (evt.button !== 0 || !state.image) return; const pt = getCanvasPoint(evt); const hitRadius = 10; for (let i = state.points.length - 1; i >= 0; i--) { const canvasPt = pointToCanvas(state.points[i]); const dx = canvasPt.x - pt.x; const dy = canvasPt.y - pt.y; if (Math.sqrt(dx * dx + dy * dy) <= hitRadius) { state.draggingIndex = i; return; } } const imagePt = clampPoint(pointToImage(pt)); state.points.push(imagePt); updatePreview(); scheduleRender(); });
  window.addEventListener('mousemove', function(evt){ if (state.draggingIndex < 0 || !state.image) return; const pt = getCanvasPoint(evt); const imagePt = clampPoint(pointToImage(pt)); state.points[state.draggingIndex] = imagePt; updatePreview(); scheduleRender(); });
  window.addEventListener('mouseup', function(){ state.draggingIndex = -1; });
  window.addEventListener('resize', resizeCanvas);
  window.addEventListener('load', function(){ resizeCanvas(); switchPolySource(); setMessage('请选择图片或加载首帧后开始标注。', 'alert-info'); });
})();
