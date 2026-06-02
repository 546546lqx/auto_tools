function pickPath(targetId, selectionType = 'directory') {
  fetch('/api/desktop-picker', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ selection_type: selectionType }),
  })
    .then((resp) => resp.json().then((data) => ({ ok: resp.ok, data })))
    .then(({ ok, data }) => {
      if (!ok || !data.success || !data.path) {
        throw new Error(data.message || '未选择路径');
      }

      const input = document.getElementById(targetId);
      const preview = document.getElementById(`${targetId}_preview`);
      if (input) input.value = data.path;
      if (preview) {
        preview.textContent = data.path;
        preview.classList.remove('empty');
      }
    })
    .catch((err) => {
      alert(err.message || '无法选择路径');
    });
}

window.pickPath = pickPath;
