(function(){
  const toolForm = document.getElementById('toolForm');
  const toolOverlay = document.getElementById('toolOverlay');
  const toolOverlayText = document.getElementById('toolOverlayText');
  const toolSubmitBtn = document.querySelector('#toolForm button[type="submit"]');
  const toolResultOverlay = document.getElementById('toolResultOverlay');
  const toolResultTitle = document.getElementById('toolResultTitle');
  const toolResultText = document.getElementById('toolResultText');
  const toolResultIcon = document.getElementById('toolResultIcon');
  const toolResultConfirmBtn = document.getElementById('toolResultConfirmBtn');

  function showToolOverlay(message='请稍候，完成后会显示结果。'){ if (toolOverlayText) toolOverlayText.textContent = message; if (toolOverlay) toolOverlay.classList.add('visible'); document.body.classList.add('auto-label-busy'); if (toolSubmitBtn){ toolSubmitBtn.disabled = true; toolSubmitBtn.textContent = '正在执行...'; } }
  function hideToolOverlay(){ if (toolOverlay) toolOverlay.classList.remove('visible'); document.body.classList.remove('auto-label-busy'); if (toolSubmitBtn){ toolSubmitBtn.disabled = false; toolSubmitBtn.textContent = '执行转换'; } }
  function hideToolResultOverlay(){ if (toolResultOverlay) toolResultOverlay.classList.remove('visible'); document.body.classList.remove('auto-label-busy'); }
  function showToolResultOverlay(success,message){ if (!toolResultOverlay) return; if (toolResultTitle) toolResultTitle.textContent = success ? '任务完成' : '任务失败'; if (toolResultText) toolResultText.textContent = message || (success ? '任务已完成，请点击确认按钮关闭提示。' : '任务执行失败，请点击确认按钮关闭提示。'); if (toolResultIcon){ toolResultIcon.className = success ? 'blocking-success-icon' : 'blocking-error-icon'; toolResultIcon.textContent = success ? '✓' : '×'; } if (toolResultConfirmBtn){ toolResultConfirmBtn.disabled = false; toolResultConfirmBtn.textContent = '确认'; } toolResultOverlay.classList.add('visible'); document.body.classList.add('auto-label-busy'); }

  window.pickPath = window.pickPath || function(targetId, selectionType='directory') {
    fetch('/api/desktop-picker', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({selection_type: selectionType})})
      .then(resp => resp.json().then(data => ({ok: resp.ok, data})))
      .then(({ok, data}) => {
        if (!ok || !data.success || !data.path) throw new Error(data.message || '未选择路径');
        const input = document.getElementById(targetId);
        const preview = document.getElementById(targetId + '_preview');
        if (input) input.value = data.path;
        if (preview) { preview.textContent = data.path; preview.classList.remove('empty'); }
      })
      .catch(err => alert(err.message || '无法选择路径'));
  };
  if (toolForm) toolForm.addEventListener('submit', () => showToolOverlay());
  if (toolResultConfirmBtn) toolResultConfirmBtn.addEventListener('click', hideToolResultOverlay);
  const resultSuccess = window.__PAGE_RESULT_SUCCESS__;
  const resultMessage = window.__PAGE_RESULT_MESSAGE__;
  if (typeof resultSuccess !== 'undefined') window.addEventListener('load', () => { hideToolOverlay(); showToolResultOverlay(!!resultSuccess, resultMessage); });
})();
