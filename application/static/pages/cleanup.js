(function(){
  'use strict';

  const CleanupPage = {};
  window.CleanupPage = CleanupPage;

  const form = document.getElementById('toolForm');
  const openBtn = document.getElementById('openCleanupFormBtn');
  const emptyOpenBtn = document.getElementById('openCleanupFormBtnEmpty');
  const toolOverlay = document.getElementById('toolOverlay');
  const toolOverlayText = document.getElementById('toolOverlayText');
  const toolSubmitBtn = document.getElementById('cleanupSubmitBtn');
  const toolResultOverlay = document.getElementById('toolResultOverlay');
  const toolResultTitle = document.getElementById('toolResultTitle');
  const toolResultText = document.getElementById('toolResultText');
  const toolResultIcon = document.getElementById('toolResultIcon');
  const toolResultConfirmBtn = document.getElementById('toolResultConfirmBtn');
  const pathPickerButtons = Array.prototype.slice.call(document.querySelectorAll('[data-path-picker]'));
  const formPanel = document.getElementById('cleanupFormPanel');

  if (!form) return;

  function setBodyBusy(isBusy) {
    document.body.classList.toggle('auto-label-busy', isBusy);
  }
  function setOverlayVisible(overlay, visible) {
    if (!overlay) return;
    overlay.classList.toggle('visible', visible);
    overlay.setAttribute('aria-hidden', visible ? 'false' : 'true');
    if ('inert' in overlay) overlay.inert = !visible;
  }
  function setPathValue(targetId, path) {
    const input = document.getElementById(targetId);
    const preview = document.getElementById(targetId + '_preview');
    if (input) input.value = path || '';
    if (preview) {
      preview.textContent = path || '尚未选择路径';
      preview.classList.toggle('empty', !path);
    }
  }

  async function pickPath(targetId, selectionType='directory') {
    try {
      const resp = await fetch('/api/desktop-picker', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({selection_type: selectionType})
      });
      const data = await resp.json().catch(() => ({}));
      if (!resp.ok || !data.success || !data.path) throw new Error(data.message || '未选择路径');
      setPathValue(targetId, data.path);
      return data.path;
    } catch (err) {
      alert(err.message || '无法选择路径');
      throw err;
    }
  }

  function showToolOverlay(message='请稍候，完成后会显示结果。') {
    if (toolOverlayText) toolOverlayText.textContent = message;
    setOverlayVisible(toolOverlay, true);
    setBodyBusy(true);
    if (toolSubmitBtn) {
      toolSubmitBtn.disabled = true;
      toolSubmitBtn.textContent = '正在执行...';
    }
  }
  function hideToolOverlay() {
    setOverlayVisible(toolOverlay, false);
    setBodyBusy(false);
    if (toolSubmitBtn) {
      toolSubmitBtn.disabled = false;
      toolSubmitBtn.textContent = '清理冗余';
    }
  }
  function hideToolResultOverlay() {
    const active = document.activeElement;
    if (active && active.blur) active.blur();
    setOverlayVisible(toolResultOverlay, false);
    setBodyBusy(false);
  }
  function showToolResultOverlay(success, message) {
    if (!toolResultOverlay) return;
    if (toolResultTitle) toolResultTitle.textContent = success ? '任务完成' : '任务失败';
    if (toolResultText) toolResultText.textContent = message || (success ? '任务已完成，请点击确认按钮关闭提示。' : '任务执行失败，请点击确认按钮关闭提示。');
    if (toolResultIcon) {
      toolResultIcon.className = success ? 'blocking-success-icon' : 'blocking-error-icon';
      toolResultIcon.textContent = success ? '✓' : '×';
    }
    if (toolResultConfirmBtn) {
      toolResultConfirmBtn.disabled = false;
      toolResultConfirmBtn.textContent = '确认';
    }
    setOverlayVisible(toolResultOverlay, true);
    setBodyBusy(true);
  }

  CleanupPage.pickPath = pickPath;
  CleanupPage.showToolOverlay = showToolOverlay;
  CleanupPage.hideToolOverlay = hideToolOverlay;
  CleanupPage.showToolResultOverlay = showToolResultOverlay;
  CleanupPage.hideToolResultOverlay = hideToolResultOverlay;

  pathPickerButtons.forEach((button) => {
    button.addEventListener('click', () => pickPath(button.dataset.pathPicker));
  });
  function scrollToForm() {
    if (formPanel && formPanel.scrollIntoView) {
      formPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
      return;
    }
    if (form && form.scrollIntoView) form.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  if (openBtn) openBtn.addEventListener('click', scrollToForm);
  if (emptyOpenBtn) emptyOpenBtn.addEventListener('click', scrollToForm);
  if (toolResultConfirmBtn) toolResultConfirmBtn.addEventListener('click', hideToolResultOverlay);

  form.addEventListener('submit', (event) => {
    if (event.defaultPrevented) return;
    setTimeout(() => showToolOverlay('正在检查并清理冗余文件，请稍候...'), 0);
  });

  const config = window.CleanupPageConfig || {};
  if (typeof config.resultSuccess !== 'undefined') {
    window.addEventListener('load', () => {
      hideToolOverlay();
      showToolResultOverlay(!!config.resultSuccess, config.resultMessage);
    });
  }
})();
