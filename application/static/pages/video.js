(function(){
  'use strict';

  const modal = document.getElementById('videoModalOverlay');
  const openBtn = document.getElementById('openVideoModalBtn');
  const emptyOpenBtn = document.getElementById('openVideoModalBtnEmpty');
  const closeBtn = document.getElementById('closeVideoModalBtn');
  const cancelBtn = document.getElementById('cancelVideoModalBtn');
  const form = document.getElementById('videoForm');
  const submitBtn = document.getElementById('submitVideoBtn');
  const stopBtn = document.getElementById('stopVideoBtn');
  const toolOverlay = document.getElementById('toolOverlay');
  const toolOverlayText = document.getElementById('toolOverlayText');
  const toolOverlayProgress = document.querySelector('#toolOverlay .blocking-progress-bar');
  const toolResultOverlay = document.getElementById('toolResultOverlay');
  const toolResultTitle = document.getElementById('toolResultTitle');
  const toolResultText = document.getElementById('toolResultText');
  const toolResultIcon = document.getElementById('toolResultIcon');
  const toolResultConfirmBtn = document.getElementById('toolResultConfirmBtn');
  const pathPickerButtons = Array.prototype.slice.call(document.querySelectorAll('[data-path-picker]'));
  const config = window.VideoPageConfig || {};
  let currentJobId = null;
  let progressTimer = null;

  function showModal(){ if (modal) modal.classList.add('visible'); document.body.classList.add('auto-label-busy'); }
  function hideModal(){ if (modal) modal.classList.remove('visible'); document.body.classList.remove('auto-label-busy'); }
  function setPathValue(targetId, path){
    const input = document.getElementById(targetId);
    const preview = document.getElementById(targetId + '_preview');
    if (!input) return;
    input.value = path || '';
    if (preview) {
      preview.textContent = path || '尚未选择路径';
      preview.classList.toggle('empty', !path);
    }
  }
  async function pickPath(targetId){
    try {
      const resp = await fetch('/api/desktop-picker', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ selection_type: 'directory' })
      });
      const data = await resp.json().catch(() => ({}));
      if (!resp.ok || !data.success || !data.path) throw new Error(data.message || '未选择路径');
      setPathValue(targetId, data.path);
    } catch (err) {
      showToolResultOverlay(false, (err && err.message) || '无法选择路径');
    }
  }
  function setProgress(value){
    if (!toolOverlayProgress) return;
    const pct = Math.max(8, Math.min(100, Number.isFinite(value) ? value : 100));
    toolOverlayProgress.style.width = pct + '%';
  }
  function showToolOverlay(message='请稍候，完成后会显示结果。'){
    if (toolOverlayText) toolOverlayText.textContent = message;
    if (toolOverlay) toolOverlay.classList.add('visible');
    document.body.classList.add('auto-label-busy');
    if (submitBtn){ submitBtn.disabled = true; submitBtn.textContent = '正在执行...'; }
    if (stopBtn){ stopBtn.classList.remove('d-none'); stopBtn.disabled = false; stopBtn.textContent = '停止抽帧'; }
    setProgress(100);
  }
  function hideToolOverlay(){
    if (toolOverlay) toolOverlay.classList.remove('visible');
    document.body.classList.remove('auto-label-busy');
    if (submitBtn){ submitBtn.disabled = false; submitBtn.textContent = '执行抽帧'; }
    if (stopBtn){ stopBtn.classList.add('d-none'); stopBtn.disabled = false; }
  }
  function hideToolResultOverlay(){ if (toolResultOverlay) toolResultOverlay.classList.remove('visible'); document.body.classList.remove('auto-label-busy'); }
  function showToolResultOverlay(success,message){
    if (!toolResultOverlay) return;
    if (toolResultTitle) toolResultTitle.textContent = success ? '任务完成' : '任务失败';
    if (toolResultText) toolResultText.textContent = message || (success ? '任务已完成，请点击确认按钮关闭提示。' : '任务执行失败，请点击确认按钮关闭提示。');
    if (toolResultIcon){ toolResultIcon.className = success ? 'blocking-success-icon' : 'blocking-error-icon'; toolResultIcon.textContent = success ? '✓' : '×'; }
    if (toolResultConfirmBtn){ toolResultConfirmBtn.disabled = false; toolResultConfirmBtn.textContent = '确认'; }
    toolResultOverlay.classList.add('visible');
    document.body.classList.add('auto-label-busy');
  }
  function startPolling(jobId){
    if (progressTimer) clearInterval(progressTimer);
    progressTimer = setInterval(async () => {
      try {
        const resp = await fetch('/api/video/status/' + jobId);
        const data = await resp.json();
        if (!resp.ok || !data.success) throw new Error(data.message || '获取进度失败');
        const job = data.data || {};
        const saved = job.saved_count || (job.result && job.result.saved_count) || 0;
        const total = job.total_frames || 0;
        if (toolOverlayText) {
          toolOverlayText.textContent = total ? `当前进度：${saved}/${total}，状态：${job.status || 'running'}` : `当前已保存 ${saved} 帧，状态：${job.status || 'running'}`;
        }
        if (total) {
          setProgress((saved / total) * 100);
        } else {
          setProgress(100);
        }
        if (job.status === 'completed' || job.status === 'stopped' || job.status === 'failed') {
          clearInterval(progressTimer);
          progressTimer = null;
          hideToolOverlay();
          showToolResultOverlay(job.status !== 'failed', job.message || config.resultMessage || '任务结束');
          currentJobId = null;
        }
      } catch (err) {
        clearInterval(progressTimer);
        progressTimer = null;
        hideToolOverlay();
        showToolResultOverlay(false, (err && err.message) || '获取进度失败');
      }
    }, 1000);
  }
  async function startJob(){
    const sourceInput = document.getElementById('source');
    const outputDirInput = document.getElementById('output_dir');
    const intervalInput = document.querySelector('input[name="interval"]');
    const outputFormatInput = document.querySelector('select[name="output_format"]');
    const payload = {
      source: sourceInput && sourceInput.value,
      output_dir: outputDirInput && outputDirInput.value,
      interval: intervalInput && intervalInput.value,
      output_format: outputFormatInput && outputFormatInput.value,
    };
    showToolOverlay('正在启动抽帧任务...');
    const resp = await fetch('/api/video/start', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload) });
    const data = await resp.json();
    if (!resp.ok || !data.success) throw new Error(data.message || '启动失败');
    currentJobId = data.job_id;
    showToolOverlay('抽帧任务已启动，正在处理...');
    startPolling(currentJobId);
  }

  pathPickerButtons.forEach((button) => button.addEventListener('click', () => pickPath(button.dataset.pathPicker)));
  if (openBtn) openBtn.addEventListener('click', showModal);
  if (emptyOpenBtn) emptyOpenBtn.addEventListener('click', showModal);
  if (closeBtn) closeBtn.addEventListener('click', hideModal);
  if (cancelBtn) cancelBtn.addEventListener('click', hideModal);
  if (toolResultConfirmBtn) toolResultConfirmBtn.addEventListener('click', hideToolResultOverlay);
  if (stopBtn) stopBtn.addEventListener('click', async () => {
    if (!currentJobId) return;
    stopBtn.disabled = true;
    showToolOverlay('已发送停止请求，正在保留已保存的数据...');
    try {
      const resp = await fetch('/api/video/stop/' + currentJobId, { method: 'POST' });
      const data = await resp.json().catch(() => ({}));
      if (!resp.ok || !data.success) throw new Error(data.message || '停止失败');
    } catch (err) {
      stopBtn.disabled = false;
      showToolResultOverlay(false, (err && err.message) || '停止失败');
    }
  });
  if (form) form.addEventListener('submit', async (event) => { event.preventDefault(); try { await startJob(); } catch (err) { hideToolOverlay(); showToolResultOverlay(false, (err && err.message) || '抽帧失败'); } });
  if (modal) modal.addEventListener('click', (event) => { if (event.target === modal) hideModal(); });
  if (typeof config.resultSuccess !== 'undefined') {
    window.addEventListener('load', () => {
      hideToolOverlay();
      showToolResultOverlay(!!config.resultSuccess, config.resultMessage);
    });
  }
})();
