(function(){
  'use strict';

  const StatsPage = {};
  window.StatsPage = StatsPage;

  const modal = document.getElementById('statsModalOverlay');
  const openBtn = document.getElementById('openStatsModalBtn');
  const emptyOpenBtn = document.getElementById('openStatsModalBtnEmpty');
  const closeBtn = document.getElementById('closeStatsModalBtn');
  const cancelBtn = document.getElementById('cancelStatsModalBtn');
  const form = document.getElementById('statsForm');
  const submitBtn = document.getElementById('submitStatsBtn');
  const toolOverlay = document.getElementById('toolOverlay');
  const toolOverlayText = document.getElementById('toolOverlayText');
  const toolResultOverlay = document.getElementById('toolResultOverlay');
  const toolResultTitle = document.getElementById('toolResultTitle');
  const toolResultText = document.getElementById('toolResultText');
  const toolResultIcon = document.getElementById('toolResultIcon');
  const toolResultConfirmBtn = document.getElementById('toolResultConfirmBtn');
  const pathPickerButtons = Array.prototype.slice.call(document.querySelectorAll('[data-path-picker]'));

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
    if (submitBtn){ submitBtn.disabled = false; submitBtn.textContent = '执行统计'; }
  }
  function hideToolResultOverlay(){ if (toolResultOverlay) toolResultOverlay.classList.remove('visible'); document.body.classList.remove('auto-label-busy'); }
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
    const input = document.getElementById(targetId);
    if (!input) return;
    try {
      const resp = await fetch('/api/desktop-picker', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ selection_type: 'directory' })
      });
      const data = await resp.json().catch(() => ({}));
      if (!resp.ok || !data.success || !data.path) {
        if (data.message) showToolResultOverlay(false, data.message);
        return;
      }
      setPathValue(targetId, data.path);
    } catch (err) {
      showToolResultOverlay(false, (err && err.message) || '无法打开路径选择器。');
    }
  }
  function showToolResultOverlay(success,message){
    if (!toolResultOverlay) return;
    if (toolResultTitle) toolResultTitle.textContent = success ? '统计完成' : '统计失败';
    if (toolResultText) toolResultText.textContent = message || (success ? '统计已完成。' : '统计执行失败。');
    if (toolResultIcon){ toolResultIcon.className = success ? 'blocking-success-icon' : 'blocking-error-icon'; toolResultIcon.textContent = success ? '✓' : '×'; }
    if (toolResultConfirmBtn){ toolResultConfirmBtn.disabled = false; toolResultConfirmBtn.textContent = '确认'; }
    toolResultOverlay.classList.add('visible');
    document.body.classList.add('auto-label-busy');
  }

  StatsPage.showModal = showModal;
  StatsPage.hideModal = hideModal;
  StatsPage.showToolOverlay = showToolOverlay;
  StatsPage.hideToolOverlay = hideToolOverlay;
  StatsPage.showToolResultOverlay = showToolResultOverlay;
  StatsPage.pickPath = pickPath;

  pathPickerButtons.forEach((button) => {
    button.addEventListener('click', () => pickPath(button.dataset.pathPicker));
  });
  if (openBtn) openBtn.addEventListener('click', showModal);
  if (emptyOpenBtn) emptyOpenBtn.addEventListener('click', showModal);
  if (closeBtn) closeBtn.addEventListener('click', hideModal);
  if (cancelBtn) cancelBtn.addEventListener('click', hideModal);
  if (toolResultConfirmBtn) toolResultConfirmBtn.addEventListener('click', hideToolResultOverlay);
  if (form) form.addEventListener('submit', () => showToolOverlay('正在统计匹配文件，请稍候...'));
  if (modal) modal.addEventListener('click', (event) => { if (event.target === modal) hideModal(); });

  const config = window.StatsPageConfig || {};
  if (typeof config.resultSuccess !== 'undefined') {
    window.addEventListener('load', () => {
      hideToolOverlay();
      showToolResultOverlay(!!config.resultSuccess, config.resultMessage);
      if (config.resultSuccess) hideModal();
    });
  }
})();
