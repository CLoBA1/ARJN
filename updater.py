import re

def main():
    with open('inventario.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Add jsPDF to <head>
    content = content.replace('</head>', '''  <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.5.31/jspdf.plugin.autotable.min.js"></script>
</head>''')

    # 2. Add new CSS rules
    new_css = '''
/* ═══════════════════════════════════════
   MODAL CONFIRM
═══════════════════════════════════════ */
.modal-confirm-icon { text-align:center; margin-bottom:16px; }
.modal-confirm-icon svg { width:48px; height:48px; }
.modal-confirm-icon.danger svg { color: var(--color-error); }
.modal-confirm-icon.warning svg { color: var(--color-warning); }
.modal-confirm-title { font-family: var(--font-heading); font-size:22px; color:var(--color-secondary); text-align:center; margin-bottom:8px; font-weight:700; }
.modal-confirm-msg { color:var(--text-muted); text-align:center; font-size:14px; margin-bottom:24px; line-height:1.5; }
#modal-confirm .modal-box { transform: scale(0.9); opacity:0; transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
#modal-confirm.open .modal-box { transform: scale(1); opacity:1; }

/* ═══════════════════════════════════════
   IMAGE UPLOAD ZONE
═══════════════════════════════════════ */
.upload-zone {
  border: 2px dashed var(--color-primary);
  border-radius: var(--radius);
  padding: 24px 16px;
  text-align: center;
  background: var(--color-primary-light);
  cursor: pointer;
  transition: var(--transition);
  position: relative;
  overflow: hidden;
  min-height: 140px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.upload-zone:hover { background: rgba(25,140,189,0.25); }
.upload-icon { color: var(--color-primary); margin-bottom: 12px; }
.upload-text { font-weight: 700; font-size: 13px; color: var(--color-primary); margin-bottom: 4px; }
.upload-subtext { font-size: 11px; color: var(--text-muted); }
.upload-preview { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; display: none; z-index: 1; }
.upload-remove { position: absolute; top: 8px; right: 8px; background: rgba(0,0,0,0.6); color: #fff; border: none; border-radius: 50%; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; cursor: pointer; z-index: 2; opacity: 0; transition: opacity 0.2s; }
.upload-zone:hover .upload-remove { opacity: 1; }
.upload-remove:hover { background: rgba(0,0,0,0.8); }

/* ═══════════════════════════════════════
   FORM VALIDATIONS
═══════════════════════════════════════ */
.char-counter { font-size: 11px; color: var(--text-muted); text-align: right; margin-top: 4px; }
.form-control.error { border-color: var(--color-error) !important; box-shadow: 0 0 0 3px rgba(192,57,43,0.15) !important; }
.inline-warning { color: var(--color-warning); font-size: 11px; display: none; margin-top: 4px; display: flex; align-items: center; gap: 4px; }
.pass-strength { height: 4px; border-radius: 2px; margin-top: 6px; background: var(--border-color); overflow: hidden; display: flex; }
.pass-strength-bar { height: 100%; transition: width 0.3s, background 0.3s; width: 0; }
.pass-strength-text { font-size: 10px; text-align: right; margin-top: 4px; color: var(--text-muted); }

/* ═══════════════════════════════════════
   PAGINATION HIGHLIGHTS
═══════════════════════════════════════ */
.page-btn:hover:not(.active):not(:disabled) { background: var(--color-primary-light); }

/* ═══════════════════════════════════════
   TABLE SORTING
═══════════════════════════════════════ */
th.sortable { cursor: pointer; user-select: none; transition: var(--transition); }
th.sortable:hover { background: rgba(0,0,0,0.03); }
th.sortable .sort-icon { display: inline-block; margin-left: 6px; color: #bbb; transition: var(--transition); }
th.sortable.sort-asc, th.sortable.sort-desc { color: var(--color-primary); }
th.sortable.sort-asc .sort-icon, th.sortable.sort-desc .sort-icon { color: var(--color-primary); }

/* ═══════════════════════════════════════
   GLOBAL SEARCH HIGHLIGHT
═══════════════════════════════════════ */
mark { background: rgba(25,140,189,0.2); color: var(--color-primary); padding: 0 2px; border-radius: 2px; }

/* ═══════════════════════════════════════
   ANIMATIONS
═══════════════════════════════════════ */
@keyframes sectionFadeIn {
  from { opacity: 0; transform: translateY(12px); }
  to   { opacity: 1; transform: translateY(0); }
}
.view-section.entering { animation: sectionFadeIn 0.3s ease forwards; }

/* ═══════════════════════════════════════
   BREADCRUMB
═══════════════════════════════════════ */
.breadcrumb { display: flex; align-items: center; gap: 8px; font-size: 14px; }
.bc-home { color: var(--text-muted); cursor: pointer; transition: var(--transition); }
.bc-home:hover { color: var(--color-primary); }
.bc-sep { color: var(--border-color); }
.bc-current { color: var(--text-primary); font-weight: 700; font-family: var(--font-heading); font-size: 16px; }

/* ═══════════════════════════════════════
   SKELETON LOADERS
═══════════════════════════════════════ */
.skeleton {
  background: linear-gradient(90deg, 
    var(--border-color) 25%, 
    rgba(255,255,255,0.5) 50%, 
    var(--border-color) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: var(--radius-sm);
}
body.dark-mode .skeleton {
  background: linear-gradient(90deg, 
    rgba(255,255,255,0.05) 25%, 
    rgba(255,255,255,0.1) 50%, 
    rgba(255,255,255,0.05) 75%
  );
  background-size: 200% 100%;
}
@keyframes shimmer {
  0%   { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
.skeleton-box { height: 100px; width: 100%; margin-bottom: 16px; }
.skeleton-line { height: 16px; width: 100%; margin-bottom: 12px; }
.skeleton-wrapper { display: none; }
.skeleton-wrapper.active { display: block; }
'''
    content = content.replace('</style>', new_css + '\n</style>')

    # 3. Breadcrumb replace
    content = content.replace('<span id="current-section-name">Dashboard</span>', '''<div class="breadcrumb" id="breadcrumb">
        <span class="bc-home" onclick="navigateTo('dashboard')">Jesús de Nazaret</span>
        <span class="bc-sep">›</span>
        <span class="bc-current" id="current-section-name">Dashboard</span>
      </div>''')

    # 4. Global Search counter and empty state
    content = content.replace('<input type="text" id="global-search" placeholder="Buscar productos…" oninput="globalSearch(this.value)">', '''<input type="text" id="global-search" placeholder="Buscar productos…" oninput="globalSearchDebounced(this.value)" onkeyup="if(event.key==='Escape') clearSearch()">
        <button type="button" id="clear-search-btn" style="position:absolute;right:12px;top:50%;transform:translateY(-50%);background:none;border:none;color:var(--text-muted);cursor:pointer;display:none;font-weight:bold;" onclick="clearSearch()">✕</button>''')

    # 5. Table Headers Sorting (Productos)
    table_headers = '<th>Imagen</th><th>SKU</th><th>Nombre</th><th>Categoría</th>\\n                    <th>Precio</th><th>Stock</th><th>Mín.</th><th>Estado</th><th>Actualización</th><th>Acciones</th>'
    new_headers = '''<th>Imagen</th>
                    <th class="sortable" onclick="handleSort('sku')">SKU<span class="sort-icon">⇅</span></th>
                    <th class="sortable" onclick="handleSort('name')">Nombre<span class="sort-icon">⇅</span></th>
                    <th class="sortable" onclick="handleSort('cat')">Categoría<span class="sort-icon">⇅</span></th>
                    <th class="sortable" onclick="handleSort('price')">Precio<span class="sort-icon">⇅</span></th>
                    <th class="sortable" onclick="handleSort('stock')">Stock<span class="sort-icon">⇅</span></th>
                    <th>Mín.</th>
                    <th class="sortable" onclick="handleSort('estado')">Estado<span class="sort-icon">⇅</span></th>
                    <th>Actualización</th><th>Acciones</th>'''
    # Use re.sub to handle any spacing differences
    content = re.sub(r'<th>Imagen</th>\s*<th>SKU</th>\s*<th>Nombre</th>\s*<th>Categoría</th>\s*<th>Precio</th>\s*<th>Stock</th>\s*<th>Mín.</th>\s*<th>Estado</th>\s*<th>Actualización</th>\s*<th>Acciones</th>', new_headers, content)

    # 6. Skeletons for Dashboard and Productos
    dash_html = '''<section id="view-dashboard" class="view-section">
        <div class="section-header">'''
    new_dash = '''<section id="view-dashboard" class="view-section">
        <div class="skeleton-wrapper" id="skel-dashboard">
          <div style="display:flex;gap:20px;margin-bottom:24px;">
            <div class="skeleton skeleton-box" style="flex:1;"></div><div class="skeleton skeleton-box" style="flex:1;"></div><div class="skeleton skeleton-box" style="flex:1;"></div><div class="skeleton skeleton-box" style="flex:1;"></div>
          </div>
          <div style="display:flex;gap:20px;margin-bottom:24px;"><div class="skeleton skeleton-box" style="flex:6;height:240px;"></div><div class="skeleton skeleton-box" style="flex:4;height:240px;"></div></div>
          <div style="display:flex;gap:20px;"><div class="skeleton skeleton-box" style="flex:1;height:200px;"></div><div class="skeleton skeleton-box" style="flex:1;height:200px;"></div></div>
        </div>
        <div id="content-dashboard" style="display:none;">
        <div class="section-header">'''
    content = content.replace(dash_html, new_dash)
    content = content.replace('      </section>\\n\\n      <!-- ═══════════════════════\\n           PRODUCTOS', '      </div>\\n      </section>\\n\\n      <!-- ═══════════════════════\\n           PRODUCTOS', 1)
    content = re.sub(r'      </section>\s+<!-- ═══════════════════════\s+PRODUCTOS', r'      </div>\n      </section>\n\n      <!-- ═══════════════════════\n           PRODUCTOS', content, count=1)


    prod_html = '''<section id="view-productos" class="view-section">
        <div class="section-header">'''
    new_prod = '''<section id="view-productos" class="view-section">
        <div class="skeleton-wrapper" id="skel-productos">
          <div class="skeleton skeleton-line" style="height:32px;width:30%;margin-bottom:24px;"></div>
          <div class="skeleton skeleton-line" style="height:40px;margin-bottom:24px;"></div>
          <div class="skeleton skeleton-box" style="height:300px;"></div>
        </div>
        <div id="content-productos" style="display:none;">
        <div class="section-header">'''
    content = content.replace(prod_html, new_prod)
    content = re.sub(r'      </section>\s+<!-- ═══════════════════════\s+CATEGORÍAS', r'      </div>\n      </section>\n\n      <!-- ═══════════════════════\n           CATEGORÍAS', content, count=1)


    # 7. Form Validations HTML: Modal Producto
    content = content.replace('<input type="text" class="form-control" id="p-nombre" placeholder="Ej: Rosario de Madera de Olivo">', '''<input type="text" class="form-control" id="p-nombre" placeholder="Ej: Rosario de Madera de Olivo" oninput="validateProductName()">
            <div class="char-counter" id="p-nombre-counter">0/100</div>''')
    
    content = content.replace('<input type="text" class="form-control" id="p-sku" placeholder="JN-ROS-001">', '''<input type="text" class="form-control" id="p-sku" placeholder="JN-ROS-001" onblur="validateSKU()">''')
    content = content.replace('<div class="inline-error" id="err-p-cat">La categoría es requerida</div>', '''<div class="inline-error" id="err-p-cat">La categoría es requerida</div>
          <div class="inline-error" id="err-p-sku">Este SKU ya está registrado</div>''')

    content = content.replace('<div class="inline-error" id="err-p-precio">El precio es requerido</div>', '''<div class="inline-error" id="err-p-precio">El precio debe ser mayor a $0</div>
            <div class="inline-warning" id="warn-p-precio">⚠️ El precio de costo supera al precio de venta</div>''')
    
    content = content.replace('<input type="number" class="form-control" id="p-costo" style="padding-left:22px;" placeholder="0.00">', '''<input type="number" class="form-control" id="p-costo" style="padding-left:22px;" placeholder="0.00" oninput="validatePrices()">''')
    content = content.replace('<input type="number" class="form-control" id="p-precio" style="padding-left:22px;" placeholder="0.00">', '''<input type="number" class="form-control" id="p-precio" style="padding-left:22px;" placeholder="0.00" oninput="validatePrices()">''')

    content = content.replace('<input type="number" class="form-control" id="p-stock-min" placeholder="5" min="0">', '''<input type="number" class="form-control" id="p-stock-min" placeholder="5" min="0" oninput="validateStockMin()">
            <div class="inline-error" id="err-p-stock-min">El stock mínimo no puede superar el stock actual</div>''')

    # Image upload HTML
    # We use regex to be safe
    old_img_html = r'<div class="form-group">\s*<label class="form-label">URL de Imagen</label>\s*<input type="text" class="form-control" id="p-img" placeholder="https://… o dejar en blanco">\s*</div>'
    new_img_html = '''<div class="form-group">
            <label class="form-label">Imagen del Producto</label>
            <input type="hidden" id="p-img-base64">
            <div class="upload-zone" id="upload-zone" onclick="document.getElementById('p-img-file').click()" ondragover="event.preventDefault(); this.style.borderColor='var(--color-primary-hover)'" ondragleave="this.style.borderColor=''" ondrop="handleDrop(event)">
              <div class="upload-icon">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
              </div>
              <div class="upload-text">Arrastra una imagen o haz clic</div>
              <div class="upload-subtext">JPG, PNG, WEBP · Máximo 2MB</div>
              <img id="upload-preview" class="upload-preview">
              <button type="button" class="upload-remove" id="upload-remove" onclick="removeImage(event)">✕</button>
            </div>
            <input type="file" id="p-img-file" accept="image/jpeg, image/png, image/webp" style="display:none;" onchange="handleFileSelect(this)">
            <div class="inline-error" id="err-p-img">Solo se permiten imágenes JPG, PNG o WEBP de máximo 2MB</div>
          </div>'''
    content = re.sub(old_img_html, new_img_html, content)

    # User Modal validations
    content = content.replace('<input type="text" class="form-control" id="usr-user" placeholder="Ej: cmendoza">', '''<input type="text" class="form-control" id="usr-user" placeholder="Ej: cmendoza" onblur="validateUsername()">''')
    content = content.replace('<div class="inline-error" id="err-usr-user">El usuario es requerido</div>', '''<div class="inline-error" id="err-usr-user">El usuario es requerido</div>
          <div class="inline-error" id="err-usr-dup">Este nombre de usuario ya está en uso</div>''')
    
    content = content.replace('<input type="password" class="form-control" id="usr-pass" placeholder="Mínimo 6 caracteres">', '''<input type="password" class="form-control" id="usr-pass" placeholder="Mínimo 6 caracteres" oninput="checkPassStrength(this.value)">
          <div class="pass-strength"><div class="pass-strength-bar" id="pass-bar"></div></div>
          <div class="pass-strength-text" id="pass-text">Mínimo 6 caracteres</div>''')

    # Reusable Confirm Modal
    confirm_modal_html = '''
<!-- Modal Confirm -->
<div class="modal-overlay" id="modal-confirm">
  <div class="modal-box modal-sm" style="max-width:380px;">
    <div class="modal-body" style="padding-top:32px;">
      <div class="modal-confirm-icon danger" id="confirm-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
      </div>
      <div class="modal-confirm-title" id="confirm-title">¿Estás seguro?</div>
      <div class="modal-confirm-msg" id="confirm-message">Esta acción no se puede deshacer.</div>
      <div style="display:flex;gap:10px;justify-content:center;">
        <button class="btn btn-secondary" onclick="closeModal('modal-confirm')">Cancelar</button>
        <button class="btn btn-danger" id="confirm-ok">Confirmar</button>
      </div>
    </div>
  </div>
</div>
'''
    content = content.replace('<!-- Toast Container -->', confirm_modal_html + '\\n<!-- Toast Container -->')

    # PDF Buttons in Reportes
    content = content.replace('<button class="btn btn-success btn-sm" onclick="exportReportCSV(\'inventario\')">', '''<button class="btn btn-danger btn-sm" onclick="exportPDF(\'inventario\')">PDF</button>
                <button class="btn btn-success btn-sm" onclick="exportReportCSV(\'inventario\')">''')
    content = content.replace('<button class="btn btn-success btn-sm" onclick="exportReportCSV(\'movimientos\')">CSV</button>', '''<button class="btn btn-danger btn-sm" onclick="exportPDF(\'movimientos\')">PDF</button>
              <button class="btn btn-success btn-sm" onclick="exportReportCSV(\'movimientos\')">CSV</button>''')
    content = content.replace('<button class="btn btn-success btn-sm" onclick="exportReportCSV(\'top-productos\')">CSV</button>', '''<button class="btn btn-danger btn-sm" onclick="exportPDF(\'top-productos\')">PDF</button>
            <button class="btn btn-success btn-sm" onclick="exportReportCSV(\'top-productos\')">CSV</button>''')
    content = content.replace('<button class="btn btn-success btn-sm" onclick="exportReportCSV(\'valorizacion\')">CSV</button>', '''<button class="btn btn-danger btn-sm" onclick="exportPDF(\'valorizacion\')">PDF</button>
            <button class="btn btn-success btn-sm" onclick="exportReportCSV(\'valorizacion\')">CSV</button>''')

    # 9. Append JavaScript logic
    new_js = '''
/* ═══════════════════════════════════════
   NEW JS LOGIC (UPDATES)
═══════════════════════════════════════ */

// --- 2. MODAL CONFIRM ---
let confirmCallback = null;
function showConfirm(title, message, onConfirm, type='danger') {
  $('confirm-title').textContent = title;
  $('confirm-message').textContent = message;
  const icon = $('confirm-icon');
  icon.className = `modal-confirm-icon ${type}`;
  if(type==='warning'){
    icon.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>`;
    $('confirm-ok').className = 'btn btn-warning';
    $('confirm-ok').style.background = 'var(--color-warning)';
    $('confirm-ok').style.color = '#fff';
  } else {
    icon.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/></svg>`;
    $('confirm-ok').className = 'btn btn-danger';
    $('confirm-ok').style.background = '';
  }
  confirmCallback = onConfirm;
  openModal('modal-confirm');
}
$('confirm-ok').addEventListener('click', () => {
  if(confirmCallback) confirmCallback();
  closeModal('modal-confirm');
});

// Overwrite deleteProduct
window.deleteProduct = function(id) {
  showConfirm('Eliminar Producto', '¿Estás seguro de eliminar este producto? Esta acción no se puede deshacer.', () => {
    APP.products = APP.products.filter(p => p.id !== id);
    renderProductos();
    updateNotifBadge();
    showToast('Producto eliminado', 'warning');
  });
};
// Overwrite deleteUser
window.deleteUser = function(id) {
  showConfirm('Eliminar Usuario', '¿Estás seguro de eliminar este usuario? Perderá acceso al sistema.', () => {
    APP.users = APP.users.filter(u => u.id !== id);
    renderUsuarios();
    showToast('Usuario eliminado', 'warning');
  });
};

// --- 1. IMAGE UPLOAD ---
window.handleFileSelect = function(input) {
  const file = input.files[0];
  if(!file) return;
  processImageFile(file);
};
window.handleDrop = function(e) {
  e.preventDefault();
  e.currentTarget.style.borderColor='';
  const file = e.dataTransfer.files[0];
  if(!file) return;
  processImageFile(file);
};
function processImageFile(file) {
  const validTypes = ['image/jpeg', 'image/png', 'image/webp'];
  if(!validTypes.includes(file.type) || file.size > 2097152) {
    $('err-p-img').style.display='block';
    return;
  }
  $('err-p-img').style.display='none';
  const reader = new FileReader();
  reader.onload = (e) => {
    $('p-img-base64').value = e.target.result;
    $('upload-preview').src = e.target.result;
    $('upload-preview').style.display = 'block';
  };
  reader.readAsDataURL(file);
}
window.removeImage = function(e) {
  e.stopPropagation();
  $('p-img-base64').value = '';
  $('p-img-file').value = '';
  $('upload-preview').src = '';
  $('upload-preview').style.display = 'none';
};
// Update productThumb function
window.productThumb = function(p) {
  if(p.img && p.img.startsWith('data:image')) {
    return `<img src="${p.img}" class="prod-thumb" alt="${p.name}" style="object-fit:cover;">`;
  }
  if(p.img && p.img.startsWith('http')) {
    return `<img src="${p.img}" class="prod-thumb" alt="${p.name}" style="object-fit:cover;">`;
  }
  return `<div class="prod-thumb"><svg width="20" height="24" viewBox="0 0 60 70" fill="none"><rect x="24" y="0" width="12" height="70" rx="4" fill="#C9A84C" opacity="0.6"/><rect x="0" y="20" width="60" height="12" rx="4" fill="#C9A84C" opacity="0.6"/></svg></div>`;
};

// --- 3. FORM VALIDATIONS ---
window.validateProductName = function() {
  const v = $('p-nombre').value;
  $('p-nombre-counter').textContent = `${v.length}/100`;
  if(v.length > 100) $('p-nombre').value = v.substring(0,100);
};
window.validateSKU = function() {
  const sku = $('p-sku').value.trim();
  const id = $('prod-edit-id').value;
  const exists = APP.products.find(p => p.sku === sku && p.id != id);
  if(exists) {
    $('p-sku').classList.add('error');
    $('err-p-sku').style.display='block';
  } else {
    $('p-sku').classList.remove('error');
    $('err-p-sku').style.display='none';
  }
};
window.validatePrices = function() {
  const price = parseFloat($('p-precio').value)||0;
  const cost = parseFloat($('p-costo').value)||0;
  if(cost > price && price > 0) $('warn-p-precio').style.display='flex';
  else $('warn-p-precio').style.display='none';
};
window.validateStockMin = function() {
  const smin = parseInt($('p-stock-min').value)||0;
  const sact = parseInt($('p-stock').value)||0;
  if(smin > sact) {
    $('p-stock-min').classList.add('error');
    $('err-p-stock-min').style.display='block';
  } else {
    $('p-stock-min').classList.remove('error');
    $('err-p-stock-min').style.display='none';
  }
};
window.validateUsername = function() {
  const u = $('usr-user').value.trim();
  const id = $('usr-edit-id').value;
  if(APP.users.find(x => x.username === u && x.id != id)) {
    $('usr-user').classList.add('error');
    $('err-usr-dup').style.display='block';
  } else {
    $('usr-user').classList.remove('error');
    $('err-usr-dup').style.display='none';
  }
};
window.checkPassStrength = function(val) {
  const bar = $('pass-bar');
  const txt = $('pass-text');
  if(val.length === 0) { bar.style.width='0'; txt.textContent='Mínimo 6 caracteres'; return; }
  let str = 0;
  if(val.length >= 6) str += 1;
  if(val.length >= 8) str += 1;
  if(/[A-Za-z]/.test(val) && /[0-9]/.test(val)) str += 1;
  if(str === 1) { bar.style.width='33%'; bar.style.background='var(--color-error)'; txt.textContent='Débil'; txt.style.color='var(--color-error)'; }
  else if(str === 2) { bar.style.width='66%'; bar.style.background='var(--color-warning)'; txt.textContent='Media'; txt.style.color='var(--color-warning)'; }
  else if(str >= 3) { bar.style.width='100%'; bar.style.background='var(--color-success)'; txt.textContent='Fuerte'; txt.style.color='var(--color-success)'; }
};

// Hook into saveProducto
const oldSaveProd = window.saveProducto;
window.saveProducto = function() {
  validateSKU(); validateStockMin();
  const precio = parseFloat($('p-precio').value);
  if(!precio || precio <= 0) {
    $('err-p-precio').style.display = 'block';
    return;
  }
  if($('err-p-sku').style.display==='block' || $('err-p-stock-min').style.display==='block') return;
  // Overwrite img with base64 before saving
  if($('p-img-base64').value) $('p-img').value = $('p-img-base64').value;
  oldSaveProd();
};
// Hook into openModalProducto
const oldOpenModalProd = window.openModalProducto;
window.openModalProducto = function(id) {
  oldOpenModalProd(id);
  $('p-img-base64').value='';
  $('upload-preview').src='';
  $('upload-preview').style.display='none';
  if(id) {
    const p = APP.products.find(x=>x.id===id);
    if(p.img && (p.img.startsWith('data:') || p.img.startsWith('http'))) {
      $('p-img-base64').value = p.img;
      $('upload-preview').src = p.img;
      $('upload-preview').style.display = 'block';
    }
  }
  validateProductName();
  validatePrices();
};

// Hook into saveUsuario
const oldSaveUser = window.saveUsuario;
window.saveUsuario = function() {
  validateUsername();
  if($('err-usr-dup').style.display==='block') return;
  if(!$('usr-edit-id').value && $('usr-pass').value.length < 6) {
    showToast('La contraseña debe tener mínimo 6 caracteres','error'); return;
  }
  oldSaveUser();
};

// --- 5. SORTING ---
let sortCol = null;
let sortAsc = true;
window.handleSort = function(col) {
  if(sortCol === col) {
    if(sortAsc) sortAsc = false;
    else { sortCol = null; sortAsc = true; } // Reset third click
  } else {
    sortCol = col; sortAsc = true;
  }
  
  // Update icons
  document.querySelectorAll('th.sortable').forEach(th => {
    th.classList.remove('sort-asc', 'sort-desc');
    th.querySelector('.sort-icon').textContent = '⇅';
  });
  
  if(sortCol) {
    const th = document.querySelector(`th.sortable[onclick="handleSort('${col}')"]`);
    if(th) {
      th.classList.add(sortAsc ? 'sort-asc' : 'sort-desc');
      th.querySelector('.sort-icon').textContent = sortAsc ? '↑' : '↓';
    }
  }
  renderProductos();
};

const oldGetFiltered = window.getFilteredProducts;
window.getFilteredProducts = function() {
  let res = oldGetFiltered();
  if(sortCol) {
    res.sort((a,b) => {
      let va = a[sortCol], vb = b[sortCol];
      if(sortCol === 'name') { va=va.toLowerCase(); vb=vb.toLowerCase(); }
      if(sortCol === 'cat') { va=a.cat; vb=b.cat; }
      if(sortCol === 'price') { va=a.price; vb=b.price; }
      if(va < vb) return sortAsc ? -1 : 1;
      if(va > vb) return sortAsc ? 1 : -1;
      return 0;
    });
  }
  return res;
};

// --- 6. GLOBAL SEARCH DEBOUNCE & HIGHLIGHT ---
let searchTimeout;
window.globalSearchDebounced = function(val) {
  $('clear-search-btn').style.display = val ? 'block' : 'none';
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    doGlobalSearch(val);
  }, 300);
};
window.clearSearch = function() {
  $('global-search').value = '';
  $('clear-search-btn').style.display = 'none';
  $('search-dropdown').style.display = 'none';
  doGlobalSearch('');
};
function highlightText(text, query) {
  if(!query || !text) return text;
  const regex = new RegExp(`(${query})`, 'gi');
  return text.replace(regex, '<mark>$1</mark>');
}
window.globalSearch = doGlobalSearch; // Fallback
function doGlobalSearch(query) {
  const dropdown = $('search-dropdown');
  if(!query || query.length < 2) { dropdown.style.display='none'; return; }
  const q = query.toLowerCase();
  
  // Search in more fields
  const results = APP.products.filter(p =>
    p.name.toLowerCase().includes(q) || 
    p.sku.toLowerCase().includes(q) || 
    p.cat.toLowerCase().includes(q) ||
    (p.desc && p.desc.toLowerCase().includes(q)) ||
    (p.proveedor && p.proveedor.toLowerCase().includes(q))
  ).slice(0, 8);

  const total = APP.products.filter(p => 
    p.name.toLowerCase().includes(q) || 
    p.sku.toLowerCase().includes(q) || 
    p.cat.toLowerCase().includes(q) ||
    (p.desc && p.desc.toLowerCase().includes(q)) ||
    (p.proveedor && p.proveedor.toLowerCase().includes(q))
  ).length;

  if(!results.length) {
    dropdown.innerHTML = `<div class="empty-state" style="padding:16px;">
      <div style="font-size:24px;margin-bottom:8px;">🔍</div>
      <div style="font-size:12px;color:var(--text-muted);">Sin resultados para "${query}"</div>
    </div>`;
  } else {
    let html = `<div style="padding:8px 14px; font-size:11px; color:var(--text-muted); border-bottom:1px solid var(--border-color);">${total} resultados encontrados</div>`;
    html += results.map(p => {
      const sc = stockClass(p.stock, p.stockMin);
      const hName = highlightText(p.name, query);
      const hSku = highlightText(p.sku, query);
      return `<div class="search-result-item" onclick="goToProduct(${p.id})">
        ${productThumb(p)}
        <div>
          <div style="font-weight:700;font-size:13px;">${hName}</div>
          <div style="font-size:11px;color:var(--text-muted);">${hSku} · ${p.cat} · <span class="${sc}">Stock: ${p.stock}</span></div>
        </div>
      </div>`;
    }).join('');
    dropdown.innerHTML = html;
  }
  dropdown.style.display = 'block';
}

// --- 8, 9, 10. ANIMATIONS, BREADCRUMB & SKELETONS ---
window.navigateTo = function(section) {
  const empAllowed = ['productos','alertas','movimientos'];
  if(APP.currentRole==='Empleado' && !empAllowed.includes(section)) return;
  
  // Update Breadcrumb
  const currentEl = $('current-section-name');
  if(currentEl) currentEl.textContent = SECTION_NAMES[section]||section;

  // Handle Skeletons & Animations
  document.querySelectorAll('.view-section').forEach(el => el.classList.remove('active', 'entering'));
  const view = $('view-'+section);
  if(view) {
    view.classList.add('active', 'entering');
    setTimeout(() => view.classList.remove('entering'), 300);
    
    // Skeleton logic for dashboard and productos
    if(section === 'dashboard' || section === 'productos') {
      const skel = $('skel-'+section);
      const content = $('content-'+section);
      if(skel && content) {
        skel.classList.add('active');
        content.style.display = 'none';
        setTimeout(() => {
          skel.classList.remove('active');
          content.style.display = 'block';
          // Render after skeleton
          renderSectionSafe(section);
        }, 600);
      } else {
        renderSectionSafe(section);
      }
    } else {
      renderSectionSafe(section);
    }
  }
  
  APP.currentSection = section;
  window.location.hash = section;

  // Update nav active
  document.querySelectorAll('.sidebar-nav-item').forEach(el => el.classList.remove('active'));
  const navEl = $('nav-'+section);
  if(navEl) navEl.classList.add('active');

  closeMobileSidebar();
};

function renderSectionSafe(section) {
  const renders = {
    dashboard: renderDashboard,
    productos: renderProductos,
    categorias: renderCategorias,
    movimientos: renderMovimientos,
    alertas: renderAlertas,
    reportes: renderReportes,
    usuarios: renderUsuarios,
    configuracion: ()=>{}
  };
  if(renders[section]) renders[section]();
}

// --- 7. EXPORT PDF ---
window.exportPDF = function(type) {
  if(!window.jspdf) { showToast('Cargando librería PDF... intenta de nuevo', 'warning'); return; }
  const { jsPDF } = window.jspdf;
  const doc = new jsPDF('p', 'pt', 'letter');
  
  // Header
  doc.setFillColor(201, 168, 76); // Gold
  doc.rect(40, 40, 10, 40, 'F');
  doc.setFontSize(20);
  doc.setTextColor(28, 90, 127); // Secondary
  doc.setFont("helvetica", "bold");
  doc.text("Jesús de Nazaret", 60, 65);
  
  doc.setLineWidth(1);
  doc.setDrawColor(201, 168, 76);
  doc.line(40, 90, 570, 90);
  
  doc.setFontSize(14);
  doc.setTextColor(50, 50, 50);
  
  let title = '';
  let filename = '';
  let body = [];
  let head = [];
  let foot = [];
  
  if(type === 'inventario') {
    title = 'Reporte de Inventario Actual';
    filename = 'inventario_' + today() + '.pdf';
    head = [['Producto', 'SKU', 'Categoría', 'Stock', 'Precio', 'Valor']];
    let total = 0;
    body = APP.products.map(p => {
      const v = p.stock * p.price;
      total += v;
      return [p.name, p.sku, p.cat, p.stock.toString(), '$'+p.price, '$'+v];
    });
    foot = [['', '', '', '', 'TOTAL', '$'+total]];
  }
  else if(type === 'movimientos') {
    title = 'Reporte de Movimientos';
    filename = 'movimientos_' + today() + '.pdf';
    head = [['Fecha', 'Producto', 'Tipo', 'Cantidad', 'Motivo', 'Usuario']];
    body = APP.movements.map(m => {
      const p = APP.products.find(x=>x.id===m.prodId);
      return [fmtDate(m.fecha), p?p.name:'?', m.tipo, m.cantidad.toString(), m.motivo, m.user];
    });
  }
  else if(type === 'top-productos') {
    title = 'Top 10 Productos Más Movidos';
    filename = 'top_productos_' + today() + '.pdf';
    head = [['Ranking', 'Producto', 'SKU', 'Total Movido']];
    const movCounts={};
    APP.movements.forEach(m=>{ movCounts[m.prodId]=(movCounts[m.prodId]||0)+m.cantidad; });
    const top = Object.entries(movCounts).sort((a,b)=>b[1]-a[1]).slice(0,10);
    body = top.map(([id, cnt], i) => {
      const p = APP.products.find(x=>x.id===parseInt(id));
      return [(i+1).toString(), p?p.name:'?', p?p.sku:'?', cnt.toString()];
    });
  }
  else if(type === 'valorizacion') {
    title = 'Valorización del Inventario';
    filename = 'valorizacion_' + today() + '.pdf';
    head = [['Categoría', 'Productos', 'Costo Total', 'Valor Venta', 'Margen']];
    let tc=0, tv=0;
    APP.categories.forEach(cat => {
      const prods = APP.products.filter(p=>p.cat===cat.name && p.stock>0);
      if(!prods.length) return;
      const costo = prods.reduce((s,p)=>s+p.stock*(p.cost||0),0);
      const venta = prods.reduce((s,p)=>s+p.stock*p.price,0);
      tc+=costo; tv+=venta;
      body.push([cat.name, prods.length.toString(), '$'+costo, '$'+venta, '$'+(venta-costo)]);
    });
    foot = [['TOTAL', '', '$'+tc, '$'+tv, '$'+(tv-tc)]];
  }
  
  doc.text(title, 40, 120);
  
  doc.autoTable({
    startY: 140,
    head: head,
    body: body,
    foot: foot.length ? foot : false,
    theme: 'grid',
    headStyles: { fillColor: [23, 90, 127], textColor: 255, fontStyle: 'bold' },
    footStyles: { fillColor: [29, 29, 29], textColor: 255, fontStyle: 'bold' },
    alternateRowStyles: { fillColor: [248, 246, 242] },
    styles: { font: "helvetica", fontSize: 10 }
  });
  
  doc.setFontSize(9);
  doc.setTextColor(150, 150, 150);
  doc.text(`Generado el ${fmtDate(today())} por ${APP.currentUser}`, 40, doc.internal.pageSize.height - 30);
  
  doc.save(filename);
  showToast('PDF generado exitosamente');
};
'''
    content = content.replace('</script>', new_js + '\\n</script>')

    # 4. Table Pagination selector
    content = content.replace('<option value="50">50 por página</option>', '<option value="50">50 por página</option>\\n                    <option value="999999">Todos</option>')

    with open('inventario.html', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    main()
