async function pickPath(targetId, selectionType = 'directory') {
  try {
    const response = await fetch('/api/desktop-picker', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ selection_type: selectionType }),
    });
    const data = await response.json();
    if (!response.ok || !data.success || !data.path) {
      throw new Error(data.message || '未选择路径');
    }

    const input = document.getElementById(targetId);
    const preview = document.getElementById(`${targetId}_preview`);
    if (input) input.value = data.path;
    if (preview) {
      preview.textContent = data.path;
      preview.classList.remove('empty');
    }
    return data.path;
  } catch (error) {
    alert(error.message || '无法选择路径');
    return '';
  }
}
