(function(){
  'use strict';

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
  const formPanel = document.getElementById('autoLabelFormPanel');
  const openBtn = document.getElementById('openAutoLabelFormBtn');
  const refreshModelsBtn = document.getElementById('refreshModelsBtn');
  const uploadModelBtn = document.getElementById('uploadModelBtn');
  const addClassBtn = document.getElementById('addClassBtn');
  const loadExampleBtn = document.getElementById('loadExampleBtn');
  const clearClassesBtn = document.getElementById('clearClassesBtn');
  const pathPickerButtons = Array.prototype.slice.call(document.querySelectorAll('[data-path-picker]'));
  let autoLabelBusy = false;

  function setOverlayVisible(overlay, visible) {
    if (!overlay) return;
    overlay.classList.toggle('visible', visible);
    overlay.setAttribute('aria-hidden', visible ? 'false' : 'true');
    if ('inert' in overlay) overlay.inert = !visible;
  }

  function setBodyBusy(isBusy) {
    document.body.classList.toggle('auto-label-busy', isBusy);
  }

  function showAutoLabelOverlay(message) {
    if (autoLabelOverlayText) autoLabelOverlayText.textContent = message || '任务正在后台运行，请稍候。完成后会自动提示结果，期间其他区域将无法点击。';
    setOverlayVisible(autoLabelOverlay, true);
    setBodyBusy(true);
    autoLabelBusy = true;
    if (autoLabelSubmitBtn) {
      autoLabelSubmitBtn.disabled = true;
      autoLabelSubmitBtn.textContent = '正在标注...';
    }
  }

  function hideAutoLabelOverlay() {
    setOverlayVisible(autoLabelOverlay, false);
    setBodyBusy(false);
    autoLabelBusy = false;
    if (autoLabelSubmitBtn) {
      autoLabelSubmitBtn.disabled = false;
      autoLabelSubmitBtn.textContent = '开始标注';
    }
  }

  function hideAutoLabelResultOverlay() {
    setOverlayVisible(autoLabelResultOverlay, false);
    setBodyBusy(false);
  }

  function showAutoLabelResultOverlay(success, message) {
    if (!autoLabelResultOverlay) return;
    if (autoLabelResultTitle) autoLabelResultTitle.textContent = success ? '自动标注完成' : '自动标注失败';
    if (autoLabelResultText) autoLabelResultText.textContent = message || (success ? '任务已完成，请点击确认按钮关闭提示。' : '任务执行失败，请点击确认按钮关闭提示。');
    if (autoLabelResultIcon) {
      autoLabelResultIcon.className = success ? 'blocking-success-icon' : 'blocking-error-icon';
      autoLabelResultIcon.textContent = success ? '✓' : '×';
    }
    if (autoLabelResultConfirmBtn) {
      autoLabelResultConfirmBtn.disabled = false;
      autoLabelResultConfirmBtn.textContent = '确认';
    }
    setOverlayVisible(autoLabelResultOverlay, true);
    setBodyBusy(true);
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

  async function pickPath(targetId, selectionType = 'directory') {
    try {
      const resp = await fetch('/api/desktop-picker', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ selection_type: selectionType })
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

  async function refreshModelList(selectPreferredPath = '') {
    const modelsDir = document.getElementById('models_dir')?.value || 'models';
    const resp = await fetch(`/api/auto-label/models?models_dir=${encodeURIComponent(modelsDir)}`);
    const data = await resp.json().catch(() => ({}));
    if (!resp.ok || !data.success) {
      alert(data.message || '刷新模型失败');
      return;
    }
    const select = document.getElementById('model_path');
    const list = document.getElementById('modelsList');
    const models = data.data.models || [];
    if (select) select.innerHTML = '<option value="">请选择模型</option>' + models.map(m => `<option value="${m.path}">${m.name}</option>`).join('');
    if (list) {
      list.innerHTML = models.length
        ? models.map(m => `<div class="path-preview"><strong>${m.name}</strong><div class="small text-muted">${m.relative_path || m.path}</div></div>`).join('')
        : '<div class="path-preview empty">当前 models 文件夹中没有可用模型</div>';
    }
    if (selectPreferredPath && select) select.value = selectPreferredPath;
  }

  function getClassRows() {
    return Array.from(document.querySelectorAll('[data-class-row]'));
  }

  function syncMappingText() {
    const mapping = document.getElementById('mapping_text');
    if (!mapping) return;
    mapping.value = getClassRows()
      .map(row => row.querySelector('[data-class-name]')?.value.trim())
      .filter(Boolean)
      .join('\n');
  }

  function syncThresholdText() {
    const hidden = document.getElementById('class_thresholds_text');
    if (!hidden) return;
    hidden.value = getClassRows()
      .map(row => {
        const name = row.querySelector('[data-class-name]')?.value.trim();
        const value = row.querySelector('[data-class-threshold]')?.value.trim() || '0.25';
        return name ? `${name}=${value}` : '';
      })
      .filter(Boolean)
      .join('\n');
  }

  function createClassRow(name = '', value = '0.25', index = 0) {
    const row = document.createElement('div');
    row.className = 'class-threshold-row';
    row.dataset.classRow = '1';
    row.innerHTML = `
      <div class="class-threshold-index">${index}</div>
      <div class="class-threshold-input-wrap">
        <label class="class-threshold-label d-md-none">类别名</label>
        <input type="text" class="form-control class-threshold-input" data-class-name placeholder="输入类别名" value="${name.replace(/"/g, '&quot;')}">
      </div>
      <div class="class-threshold-input-wrap">
        <label class="class-threshold-label d-md-none">阈值</label>
        <input type="number" class="form-control class-threshold-input" data-class-threshold min="0" max="1" step="0.01" value="${value}">
      </div>
      <button type="button" class="btn btn-outline-danger btn-sm class-threshold-remove" data-action="remove">删除</button>
    `;
    row.querySelector('[data-class-name]')?.addEventListener('input', () => {
      syncMappingText();
      syncThresholdText();
      refreshClassIndexes();
    });
    row.querySelector('[data-class-threshold]')?.addEventListener('input', syncThresholdText);
    row.querySelector('[data-action="remove"]')?.addEventListener('click', () => {
      row.remove();
      refreshClassIndexes();
      syncMappingText();
      syncThresholdText();
    });
    return row;
  }

  function refreshClassIndexes() {
    const rows = getClassRows();
    rows.forEach((row, index) => {
      const badge = row.querySelector('.class-threshold-index');
      if (badge) badge.textContent = index;
    });
    if (!rows.length) {
      const container = document.getElementById('classRows');
      if (container) container.innerHTML = '<div class="class-threshold-empty">点击“添加类别”开始配置类别和阈值</div>';
    }
  }

  function renderClassRows(rows = []) {
    const container = document.getElementById('classRows');
    if (!container) return;
    container.innerHTML = '';
    if (!rows.length) {
      container.innerHTML = '<div class="class-threshold-empty">点击“添加类别”开始配置类别和阈值</div>';
      syncMappingText();
      syncThresholdText();
      return;
    }
    rows.forEach(({ name, value }, index) => container.appendChild(createClassRow(name, value, index)));
    syncMappingText();
    syncThresholdText();
  }

  function addClassRow(name = '', value = '0.25') {
    const container = document.getElementById('classRows');
    if (!container) return;
    if (container.querySelector('.class-threshold-empty')) container.innerHTML = '';
    container.appendChild(createClassRow(name, value, container.querySelectorAll('[data-class-row]').length));
    refreshClassIndexes();
    syncMappingText();
    syncThresholdText();
  }

  function clearClassRows() {
    renderClassRows([]);
  }

  function loadMappingExample() {
    renderClassRows([
      { name: 'person', value: '0.25' },
      { name: 'car', value: '0.35' },
      { name: 'bicycle', value: '0.30' },
    ]);
  }

  async function uploadModel() {
    const sourceModelPath = document.getElementById('upload_model_input')?.value.trim();
    const modelsDir = document.getElementById('models_dir')?.value || 'models';
    if (!sourceModelPath) {
      alert('请先选择一个模型文件');
      return;
    }
    const resp = await fetch('/api/auto-label/upload-model', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ source_model_path: sourceModelPath, models_dir: modelsDir })
    });
    const data = await resp.json().catch(() => ({}));
    if (!resp.ok || !data.success) {
      alert(data.message || '上传失败');
      return;
    }
    await refreshModelList(data.data.uploaded_path);
    alert(data.message || '上传成功');
  }

  window.pickPath = pickPath;
  window.refreshModelList = refreshModelList;
  window.uploadModel = uploadModel;
  window.addClassRow = addClassRow;
  window.loadMappingExample = loadMappingExample;
  window.clearClassRows = clearClassRows;

  pathPickerButtons.forEach((button) => {
    button.addEventListener('click', () => pickPath(button.dataset.pathPicker, button.dataset.pathPicker === 'upload_model_input' ? 'file' : 'directory'));
  });
  if (refreshModelsBtn) refreshModelsBtn.addEventListener('click', () => refreshModelList());
  if (uploadModelBtn) uploadModelBtn.addEventListener('click', uploadModel);
  if (addClassBtn) addClassBtn.addEventListener('click', () => addClassRow());
  if (loadExampleBtn) loadExampleBtn.addEventListener('click', loadMappingExample);
  if (clearClassesBtn) clearClassesBtn.addEventListener('click', clearClassRows);
  if (autoLabelResultConfirmBtn) autoLabelResultConfirmBtn.addEventListener('click', hideAutoLabelResultOverlay);

  autoLabelForm.addEventListener('submit', (event) => {
    if (!getClassRows().length) {
      event.preventDefault();
      alert('请先添加至少一个类别');
      return;
    }
    syncMappingText();
    syncThresholdText();
    setTimeout(() => showAutoLabelOverlay('正在执行自动标注，请稍候...'), 0);
  });

  function scrollToForm() {
    if (formPanel?.scrollIntoView) {
      formPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  if (openBtn) openBtn.addEventListener('click', scrollToForm);

  const config = window.AutoLabelPageConfig || {};
  if (typeof config.resultSuccess !== 'undefined') {
    window.addEventListener('load', () => {
      hideAutoLabelOverlay();
      showAutoLabelResultOverlay(!!config.resultSuccess, config.resultMessage);
    });
  }

  const initialMappingText = document.getElementById('mapping_text')?.value || '';
  const initialThresholdText = document.getElementById('class_thresholds_text')?.value || '';
  const initialMappingNames = initialMappingText.split('\n').map(item => item.trim()).filter(Boolean);
  const initialThresholdMap = {};
  initialThresholdText.split('\n').map(item => item.trim()).filter(Boolean).forEach(line => {
    const [name, value] = line.split('=');
    if (name) initialThresholdMap[name.trim()] = (value || '0.25').trim();
  });
  const initialRows = (initialMappingNames.length ? initialMappingNames : ['person', 'car', 'bicycle']).map(name => ({
    name,
    value: initialThresholdMap[name] || '0.25',
  }));
  renderClassRows(initialRows);
  refreshModelList();
})();
