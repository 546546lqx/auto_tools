(function(){
  'use strict';

  const modal = document.getElementById('splitModalOverlay');
  const openBtn = document.getElementById('openSplitModalBtn');
  const emptyOpenBtn = document.getElementById('openSplitModalBtnEmpty');
  const closeBtn = document.getElementById('closeSplitModalBtn');
  const cancelBtn = document.getElementById('cancelSplitModalBtn');
  const form = document.getElementById('splitForm');
  const submitBtn = document.getElementById('submitSplitBtn');
  const toolOverlay = document.getElementById('toolOverlay');
  const toolOverlayText = document.getElementById('toolOverlayText');
  const toolResultOverlay = document.getElementById('toolResultOverlay');
  const toolResultTitle = document.getElementById('toolResultTitle');
  const toolResultText = document.getElementById('toolResultText');
  const toolResultIcon = document.getElementById('toolResultIcon');
  const toolResultConfirmBtn = document.getElementById('toolResultConfirmBtn');
  const pathPickerButtons = Array.prototype.slice.call(document.querySelectorAll('[data-path-picker]'));
  const trainInput = document.getElementById('train_ratio');
  const valInput = document.getElementById('val_ratio');
  const ratioText = document.getElementById('splitRatioText');
  const ratioBar = document.getElementById('splitRatioBar');

  function showModal(){ if (modal) modal.classList.add('visible'); document.body.classList.add('auto-label-busy'); }
  function hideModal(){ if (modal) modal.classList.remove('visible'); document.body.classList.remove('auto-label-busy'); }
  function showToolOverlay(message='请稍候，完成后会显示结果。'){
    if (toolOverlayText) toolOverlayText.textContent = message;
    if (toolOverlay) toolOverlay.classList.add('visible');
    document.body.classList.add('auto-label-busy');
    if (submitBtn){ submitBtn.disabled = true; submitBtn.textContent = '正在执行...'; }
  }
  function hideToolOverlay(){
    if (toolOverlay) toolOverlay.classList.remove('visible');
    document.body.classList.remove('auto-label-busy');
    if (submitBtn){ submitBtn.disabled = false; submitBtn.textContent = '执行划分'; }
  }
  function hideToolResultOverlay(){
    if (toolResultConfirmBtn && typeof toolResultConfirmBtn.blur === 'function') toolResultConfirmBtn.blur();
    if (toolResultOverlay) {
      toolResultOverlay.classList.remove('visible');
      toolResultOverlay.setAttribute('aria-hidden', 'true');
      toolResultOverlay.setAttribute('inert', '');
    }
    document.body.classList.remove('auto-label-busy');
  }
  function showToolResultOverlay(success,message){
    if (!toolResultOverlay) return;
    if (toolResultTitle) toolResultTitle.textContent = success ? '任务完成' : '任务失败';
    if (toolResultText) toolResultText.textContent = message || (success ? '任务已完成，请点击确认按钮关闭提示。' : '任务执行失败，请点击确认按钮关闭提示。');
    if (toolResultIcon){ toolResultIcon.className = success ? 'blocking-success-icon' : 'blocking-error-icon'; toolResultIcon.textContent = success ? '✓' : '×'; }
    if (toolResultConfirmBtn){ toolResultConfirmBtn.disabled = false; toolResultConfirmBtn.textContent = '确认'; }
    toolResultOverlay.removeAttribute('inert');
    toolResultOverlay.setAttribute('aria-hidden', 'false');
    toolResultOverlay.classList.add('visible');
    document.body.classList.add('auto-label-busy');
    if (toolResultConfirmBtn && typeof toolResultConfirmBtn.focus === 'function') toolResultConfirmBtn.focus();
  }
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
      showToolResultOverlay(false, (err && err.message) || '无法选择路径。');
    }
  }
  function updateRatioPreview(){
    const train = Math.max(0, Math.min(1, parseFloat(trainInput && trainInput.value) || 0));
    const val = Math.max(0, Math.min(1, parseFloat(valInput && valInput.value) || 0));
    const total = train + val || 1;
    const trainPct = Math.round((train / total) * 100);
    const valPct = 100 - trainPct;
    if (ratioText) ratioText.textContent = `${trainPct}% / ${valPct}%`;
    if (ratioBar) ratioBar.style.width = `${trainPct}%`;
  }

  pathPickerButtons.forEach((button) => {
    button.addEventListener('click', () => pickPath(button.dataset.pathPicker));
  });
  if (openBtn) openBtn.addEventListener('click', showModal);
  if (emptyOpenBtn) emptyOpenBtn.addEventListener('click', showModal);
  if (closeBtn) closeBtn.addEventListener('click', hideModal);
  if (cancelBtn) cancelBtn.addEventListener('click', hideModal);
  if (toolResultConfirmBtn) toolResultConfirmBtn.addEventListener('click', hideToolResultOverlay);
  if (form) form.addEventListener('submit', () => showToolOverlay('正在划分数据集，请稍候...'));
  if (modal) modal.addEventListener('click', (event) => { if (event.target === modal) hideModal(); });
  if (trainInput) trainInput.addEventListener('input', updateRatioPreview);
  if (valInput) valInput.addEventListener('input', updateRatioPreview);

  const config = window.SplitPageConfig || {};
  if (typeof config.resultSuccess !== 'undefined') {
    window.addEventListener('load', () => {
      hideToolOverlay();
      showToolResultOverlay(!!config.resultSuccess, config.resultMessage);
      if (config.resultSuccess) hideModal();
    });
  }
  updateRatioPreview();
})();
