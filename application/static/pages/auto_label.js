(function(){
  const autoLabelForm = document.getElementById('autoLabelForm');
  if (!autoLabelForm) return;

  const autoLabelOverlay = document.getElementById('autoLabelOverlay');
  const autoLabelOverlayText = document.getElementById('autoLabelOverlayText');
  const autoLabelSubmitBtn = document.getElementById('autoLabelSubmitBtn');
  const autoLabelResultOverlay = document.getElementById('autoLabelResultOverlay');
  const autoLabelResultIcon = document.getElementById('autoLabelResultIcon');
  const autoLabelResultTitle = document.getElementById('autoLabelResultTitle');
  const autoLabelResultText = document.getElementById('autoLabelResultText');
  const autoLabelResultConfirmBtn = document.getElementById('autoLabelResultConfirmBtn');
  let autoLabelBusy = false;

  function showAutoLabelOverlay(message) {
    if (autoLabelOverlayText) autoLabelOverlayText.textContent = message || '任务正在后台运行，请稍候。完成后会自动提示结果，期间其他区域将无法点击。';
    if (autoLabelOverlay) autoLabelOverlay.classList.add('visible');
    document.body.classList.add('auto-label-busy');
    autoLabelBusy = true;
    if (autoLabelSubmitBtn) { autoLabelSubmitBtn.disabled = true; autoLabelSubmitBtn.textContent = '正在标注...'; }
  }

  function setMappingExample(text) {
    const mapping = document.getElementById('mapping_text');
    if (mapping) mapping.value = text;
  }

  function hideAutoLabelOverlay() {
    if (autoLabelOverlay) autoLabelOverlay.classList.remove('visible');
    document.body.classList.remove('auto-label-busy');
    autoLabelBusy = false;
    if (autoLabelSubmitBtn) { autoLabelSubmitBtn.disabled = false; autoLabelSubmitBtn.textContent = '开始标注'; }
  }

  function showAutoLabelResultOverlay(success, message) {
    if (!autoLabelResultOverlay) return;
    if (autoLabelResultTitle) autoLabelResultTitle.textContent = success ? '自动标注完成' : '自动标注失败';
    if (autoLabelResultText) autoLabelResultText.textContent = message || (success ? '任务已完成，请点击确认按钮关闭提示。' : '任务执行失败，请点击确认按钮关闭提示。');
    if (autoLabelResultIcon) { autoLabelResultIcon.className = success ? 'blocking-success-icon' : 'blocking-error-icon'; autoLabelResultIcon.textContent = success ? '✓' : '×'; }
    if (autoLabelResultConfirmBtn) { autoLabelResultConfirmBtn.textContent = '确认'; autoLabelResultConfirmBtn.disabled = false; }
    autoLabelResultOverlay.classList.add('visible');
    document.body.classList.add('auto-label-busy');
  }

  async function refreshModelList(selectPreferredPath = '') {
    const modelsDir = document.getElementById('models_dir')?.value || 'models';
    const resp = await fetch(`/api/auto-label/models?models_dir=${encodeURIComponent(modelsDir)}`);
    const data = await resp.json();
    if (!resp.ok || !data.success) { alert(data.message || '刷新模型失败'); return; }
    const select = document.getElementById('model_path');
    const list = document.getElementById('modelsList');
    const models = data.data.models || [];
    select.innerHTML = '<option value="">请选择模型</option>' + models.map(m => `<option value="${m.path}">${m.name}</option>`).join('');
    list.innerHTML = models.length ? models.map(m => `<div class="path-preview"><strong>${m.name}</strong><div class="small text-muted">${m.relative_path || m.path}</div></div>`).join('') : '<div class="path-preview empty">当前 models 文件夹中没有可用模型</div>';
    if (selectPreferredPath) select.value = selectPreferredPath;
  }

  window.refreshModelList = refreshModelList;
  window.setMappingExample = setMappingExample;
  window.pickPath = window.pickPath;
  window.uploadModel = window.uploadModel;

  autoLabelForm.addEventListener('submit', function(){
    if (!autoLabelBusy) showAutoLabelOverlay();
  });

  if (autoLabelResultConfirmBtn) autoLabelResultConfirmBtn.addEventListener('click', hideAutoLabelResultOverlay);
})();
