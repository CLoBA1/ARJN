"""
connect_api.py
Reemplaza el bloque de datos hardcodeados en inventario.html 
con la capa de conexión async/await a la API REST.
"""
import re

src = r"c:\xampp\htdocs\ARN 2026\inventario.html"

with open(src, encoding="utf-8") as f:
    html = f.read()

# ── Nuevo bloque JS que sustituye desde "const APP = {" hasta el console.log de credenciales
OLD_APP_BLOCK_START = "const APP = {"
OLD_APP_BLOCK_END   = "console.log('%cCredenciales: admin/admin123 (Admin) | empleado/emp123 (Empleado)', 'color:#C9A84C;');"

NEW_APP_BLOCK = r"""
/* ═══════════════════════════════════════
   API BASE — cambiar solo esta línea para producción
═══════════════════════════════════════ */
const API_BASE = 'http://localhost/ARN%202026/api';

/* ═══════════════════════════════════════
   APP STATE
═══════════════════════════════════════ */
const APP = {
  token: null,
  currentUser: null,
  currentRole: null,
  currentSection: 'dashboard',
  productView: 'table',
  productPage: 1,
  productPageSize: 10,
  productFiltered: [],
  movPage: 1,
  movPageSize: 15,
  movFiltered: [],
  selectedMovType: 'entrada',
  darkMode: false,
  categories: [],
  products: [],
  movements: [],
  users: [],
  config: {}
};

/* ═══════════════════════════════════════
   SIDEBAR NAV DEFINITIONS
═══════════════════════════════════════ */
const NAV_ADMIN = [
  { id:'dashboard',     label:'Dashboard',       icon:'chart' },
  { id:'productos',     label:'Productos',        icon:'box' },
  { id:'categorias',    label:'Categorías',       icon:'tag' },
  { id:'movimientos',   label:'Movimientos',      icon:'arrows' },
  { id:'alertas',       label:'Alertas de Stock', icon:'bell', badge:true },
  { id:'reportes',      label:'Reportes',         icon:'doc' },
  { id:'usuarios',      label:'Usuarios',         icon:'users' },
  { id:'configuracion', label:'Configuración',    icon:'gear' }
];
const NAV_EMPLEADO = [
  { id:'productos',   label:'Productos',        icon:'box' },
  { id:'alertas',     label:'Alertas de Stock', icon:'bell', badge:true },
  { id:'movimientos', label:'Movimientos',      icon:'arrows' }
];

/* ═══════════════════════════════════════
   API HELPER — fetch autenticado
═══════════════════════════════════════ */
async function api(endpoint, method = 'GET', body = null) {
  const headers = { 'Content-Type': 'application/json' };
  if (APP.token) headers['X-Session-Token'] = APP.token;
  const options = { method, headers };
  if (body && method !== 'GET') options.body = JSON.stringify(body);
  try {
    const res = await fetch(`${API_BASE}${endpoint}`, options);
    if (res.status === 401) {
      doLogout();
      showToast('Sesión expirada, inicia sesión nuevamente', 'warning');
      return { success: false };
    }
    return await res.json();
  } catch (err) {
    console.error('API Error:', err);
    return { success: false, message: 'Error de conexión con el servidor' };
  }
}

/* ═══════════════════════════════════════
   UTILITY FUNCTIONS
═══════════════════════════════════════ */
function $(id) { return document.getElementById(id); }
function fmtDate(d) { if(!d) return '—'; const p=d.split(/[T ]/)[0].split('-'); return `${p[2]}/${p[1]}/${p[0]}`; }
function fmtMoney(n) { return '$' + Number(n).toLocaleString('es-MX'); }
function today() { return new Date().toISOString().split('T')[0]; }
function avatarColor(name) {
  const colors = ['#198cbd','#175a7f','#2d8a4e','#9b59b6','#d4820a','#c0392b','#C9A84C'];
  let h = 0; for(let c of name) h = (h*31+c.charCodeAt(0))%colors.length;
  return colors[h];
}
function initials(name) { return name.split(' ').map(w=>w[0]).join('').substring(0,2).toUpperCase(); }

/* ═══════════════════════════════════════
   LOGIN / LOGOUT
═══════════════════════════════════════ */
async function doLogin(e) {
  e.preventDefault();
  const username = $('login-user').value.trim();
  const password = $('login-pass').value;
  const errEl = $('login-error');
  errEl.style.display = 'none';

  const btn = document.querySelector('#login-screen button[type=submit]') ||
              document.querySelector('#login-screen .btn-login') ||
              document.querySelector('#login-screen button');
  if (btn) { btn.disabled = true; btn.textContent = 'Ingresando...'; }

  const res = await api('/auth/login.php', 'POST', { username, password });

  if (res.success) {
    APP.token       = res.token;
    APP.currentUser = res.usuario.username;
    APP.currentRole = res.usuario.rol === 'admin' ? 'Admin' : 'Empleado';

    const nombre = res.usuario.nombre;
    $('user-avatar-topbar').textContent = initials(nombre);
    $('user-avatar-topbar').style.background = avatarColor(nombre);
    $('topbar-username').textContent = nombre;
    $('topbar-role').textContent = APP.currentRole === 'Admin' ? 'Administrador' : 'Empleado';
    $('role-badge').textContent = APP.currentRole.toUpperCase();
    $('role-badge').className = `badge ${APP.currentRole === 'Admin' ? 'badge-primary' : 'badge-warning'}`;

    document.querySelectorAll('.admin-only').forEach(el => {
      el.style.display = APP.currentRole === 'Admin' ? '' : 'none';
    });

    $('login-screen').style.display = 'none';
    $('app-panel').style.display = 'flex';
    $('app-panel').style.flexDirection = 'column';
    $('dash-date').textContent = new Date().toLocaleDateString('es-MX',{weekday:'long',year:'numeric',month:'long',day:'numeric'});

    // Load categories into APP.categories for selects and render
    await loadCategorias();

    buildSidebar();
    const defaultSection = APP.currentRole === 'Admin' ? 'dashboard' : 'productos';
    navigateTo(defaultSection);

  } else {
    errEl.style.display = 'block';
    if (btn) { btn.disabled = false; btn.textContent = 'Ingresar'; }
  }
}

function doLogout() {
  if (APP.token) api('/auth/logout.php', 'POST');
  APP.token = null;
  APP.currentUser = null;
  APP.currentRole = null;
  APP.products = [];
  APP.movements = [];
  APP.users = [];
  $('app-panel').style.display = 'none';
  $('login-screen').style.display = 'flex';
  $('login-user').value = '';
  $('login-pass').value = '';
  $('login-error').style.display = 'none';
}

/* ═══════════════════════════════════════
   SIDEBAR
═══════════════════════════════════════ */
let sidebarCollapsed = false;

function buildSidebar() {
  const nav = APP.currentRole === 'Admin' ? NAV_ADMIN : NAV_EMPLEADO;
  const container = $('sidebar-nav');
  container.innerHTML = nav.map(item => `
    <div class="sidebar-nav-item" id="nav-${item.id}" onclick="navigateTo('${item.id}')">
      ${SVG_ICONS[item.icon]||''}
      <span class="nav-label">${item.label}</span>
      ${item.badge ? `<span class="nav-badge" id="nav-badge-${item.id}">0</span>` : ''}
      <span class="sidebar-tooltip">${item.label}</span>
    </div>
  `).join('');
}

function toggleSidebar() {
  const sidebar = $('sidebar');
  const main = $('main-content');
  if(window.innerWidth <= 768) {
    sidebar.classList.toggle('mobile-open');
    $('sidebar-overlay').classList.toggle('active');
  } else {
    sidebarCollapsed = !sidebarCollapsed;
    sidebar.classList.toggle('collapsed', sidebarCollapsed);
    main.style.marginLeft = sidebarCollapsed ? 'var(--sidebar-collapsed)' : 'var(--sidebar-width)';
    $('sidebar-version-text').textContent = sidebarCollapsed ? 'v1.0' : 'Sistema de Inventario v1.0.0';
  }
}

function closeMobileSidebar() {
  $('sidebar').classList.remove('mobile-open');
  $('sidebar-overlay').classList.remove('active');
}

function updateNotifBadge(count) {
  const badge = $('notif-badge');
  if (badge) { badge.textContent = count; badge.style.display = count > 0 ? 'flex' : 'none'; }
  document.querySelectorAll('.nav-badge').forEach(b => b.textContent = count);
}

/* ═══════════════════════════════════════
   SPA NAVIGATION
═══════════════════════════════════════ */
const SECTION_NAMES = {
  dashboard:'Dashboard', productos:'Productos', categorias:'Categorías',
  movimientos:'Movimientos', alertas:'Alertas de Stock',
  reportes:'Reportes', usuarios:'Usuarios', configuracion:'Configuración'
};

function navigateTo(section) {
  const empAllowed = ['productos','alertas','movimientos'];
  if(APP.currentRole==='Empleado' && !empAllowed.includes(section)) return;

  APP.currentSection = section;
  window.location.hash = section;

  const currentEl = $('current-section-name');
  if(currentEl) currentEl.textContent = SECTION_NAMES[section]||section;

  document.querySelectorAll('.view-section').forEach(el => el.classList.remove('active','entering'));
  const view = $('view-'+section);
  if(view) {
    view.classList.add('active','entering');
    setTimeout(() => view.classList.remove('entering'), 300);

    if(section === 'dashboard' || section === 'productos') {
      const skel = $('skel-'+section);
      const content = $('content-'+section);
      if(skel && content) {
        skel.classList.add('active');
        content.style.display = 'none';
        setTimeout(() => {
          skel.classList.remove('active');
          content.style.display = 'block';
          loadSectionData(section);
        }, 600);
        return;
      }
    }
    loadSectionData(section);
  }

  document.querySelectorAll('.sidebar-nav-item').forEach(el => el.classList.remove('active'));
  const navEl = $('nav-'+section);
  if(navEl) navEl.classList.add('active');
  closeMobileSidebar();
}

async function loadSectionData(section) {
  switch(section) {
    case 'dashboard':    await loadDashboard();   break;
    case 'productos':    await loadProductos();   break;
    case 'categorias':   await loadCategorias();  break;
    case 'movimientos':  await loadMovimientos();  break;
    case 'alertas':      await loadAlertas();     break;
    case 'reportes':     await loadReportes();    break;
    case 'usuarios':     await loadUsuarios();    break;
    case 'configuracion':await loadConfiguracion();break;
  }
}

/* ═══════════════════════════════════════
   GLOBAL SEARCH (API-backed)
═══════════════════════════════════════ */
let searchTimeout;
function globalSearchDebounced(val) {
  $('clear-search-btn').style.display = val ? 'block' : 'none';
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => doGlobalSearch(val), 300);
}
function clearSearch() {
  $('global-search').value = '';
  $('clear-search-btn').style.display = 'none';
  $('search-dropdown').style.display = 'none';
}
function highlightText(text, query) {
  if(!query || !text) return text;
  const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')})`, 'gi');
  return String(text).replace(regex, '<mark>$1</mark>');
}
async function doGlobalSearch(query) {
  const dropdown = $('search-dropdown');
  if(!query || query.length < 2) { dropdown.style.display='none'; return; }

  const res = await api(`/productos/index.php?buscar=${encodeURIComponent(query)}&limit=8`);
  if(!res.success || !res.data.length) {
    dropdown.innerHTML = `<div class="empty-state" style="padding:16px;"><div style="font-size:24px;margin-bottom:8px;">🔍</div><div style="font-size:12px;color:var(--text-muted);">Sin resultados para "${query}"</div></div>`;
    dropdown.style.display = 'block';
    return;
  }

  let html = `<div style="padding:8px 14px;font-size:11px;color:var(--text-muted);border-bottom:1px solid var(--border-color);">${res.pagination.total} resultados encontrados</div>`;
  html += res.data.map(p => `<div class="search-result-item" onclick="goToProduct(${p.id})">
    <div class="prod-thumb"><svg width="20" height="24" viewBox="0 0 60 70" fill="none"><rect x="24" y="0" width="12" height="70" rx="4" fill="#C9A84C" opacity="0.6"/><rect x="0" y="20" width="60" height="12" rx="4" fill="#C9A84C" opacity="0.6"/></svg></div>
    <div>
      <div style="font-weight:700;font-size:13px;">${highlightText(p.nombre, query)}</div>
      <div style="font-size:11px;color:var(--text-muted);">${highlightText(p.sku, query)} · ${p.nombre_categoria||''} · <span class="${stockClassFromStatus(p.stock_status)}">Stock: ${p.stock_actual}</span></div>
    </div>
  </div>`).join('');
  dropdown.innerHTML = html;
  dropdown.style.display = 'block';
}
function goToProduct(id) {
  $('search-dropdown').style.display = 'none';
  $('global-search').value = '';
  navigateTo('productos');
}
window.globalSearch = doGlobalSearch;
window.globalSearchDebounced = globalSearchDebounced;
window.clearSearch = clearSearch;

document.addEventListener('click', e => {
  const gs = $('global-search');
  if(gs && !gs.contains(e.target)) $('search-dropdown').style.display='none';
});

function stockClassFromStatus(status) {
  if(status === 'sin_stock') return 'stock-bad';
  if(status === 'stock_bajo') return 'stock-warn';
  return 'stock-ok';
}

/* ═══════════════════════════════════════
   DASHBOARD
═══════════════════════════════════════ */
async function loadDashboard() {
  const res = await api('/dashboard/stats.php');
  if(!res.success) { showToast('Error cargando dashboard', 'error'); return; }

  const { kpis, movimientos_semana, productos_por_categoria, ultimos_movimientos, alertas_stock } = res.data;

  // KPI Cards
  const kpiMap = {
    'kpi-total':      kpis.total_productos,
    'kpi-activos':    kpis.total_productos,
    'kpi-stock-bajo': kpis.productos_stock_bajo,
    'kpi-valor':      '$' + Number(kpis.valor_inventario).toLocaleString('es-MX')
  };
  Object.entries(kpiMap).forEach(([id, val]) => { const el=$(id); if(el) el.textContent=val; });

  updateNotifBadge((kpis.productos_stock_bajo||0) + (kpis.productos_sin_stock||0));

  renderDashMovimientosAPI(ultimos_movimientos);
  renderDashStockLowAPI(alertas_stock);
  renderBarChartAPI(movimientos_semana);
  renderDonutChartAPI(productos_por_categoria);
}

function renderDashMovimientosAPI(movs) {
  const tbody = $('dash-movimientos-body');
  if(!tbody) return;
  tbody.innerHTML = (movs||[]).slice(0,5).map(m => {
    const badgeClass = m.tipo==='entrada'?'badge-success':m.tipo==='salida'?'badge-error':'badge-primary';
    const tipoCap = m.tipo.charAt(0).toUpperCase()+m.tipo.slice(1);
    return `<tr>
      <td><div style="max-width:130px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="${m.nombre_producto||''}">${m.nombre_producto||'?'}</div></td>
      <td><span class="badge ${badgeClass}">${tipoCap}</span></td>
      <td style="font-weight:700;">${m.tipo==='salida'?'-':'+'}<span style="color:${m.tipo==='salida'?'var(--color-error)':m.tipo==='entrada'?'var(--color-success)':'var(--color-primary)'}">${m.cantidad}</span></td>
      <td>${fmtDate(m.created_at)}</td>
      <td><span style="font-size:11px;color:var(--text-muted);">${m.nombre_usuario||'—'}</span></td>
    </tr>`;
  }).join('') || '<tr><td colspan="5" style="text-align:center;color:var(--text-muted);padding:20px;">Sin movimientos recientes</td></tr>';
}

function renderDashStockLowAPI(alertas) {
  const tbody = $('dash-stock-low-body');
  if(!tbody) return;
  tbody.innerHTML = (alertas||[]).slice(0,5).map(p => `<tr>
    <td><div style="max-width:130px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${p.nombre}</div></td>
    <td><span style="font-size:11px;">${p.categoria}</span></td>
    <td class="${p.stock_actual===0?'stock-bad':'stock-warn'}">${p.stock_actual}</td>
    <td>${p.stock_minimo}</td>
    <td><button class="btn btn-primary btn-xs" onclick="openModalStockByName('${p.nombre}')">+Stock</button></td>
  </tr>`).join('') || '<tr><td colspan="5" style="text-align:center;color:var(--text-muted);padding:20px;">✅ Sin alertas de stock</td></tr>';
}

function renderBarChartAPI(data) {
  const canvas = $('chart-movimientos');
  if(!canvas || !data) return;
  const ctx = canvas.getContext('2d');
  const W = canvas.parentElement.offsetWidth - 40 || 400;
  const H = 200;
  canvas.width = W; canvas.height = H;

  const labels = (data||[]).map(d => {
    const dt = new Date(d.fecha+'T12:00:00');
    return ['Dom','Lun','Mar','Mié','Jue','Vie','Sáb'][dt.getDay()];
  });
  const entradas = (data||[]).map(d => parseInt(d.entradas)||0);
  const salidas  = (data||[]).map(d => parseInt(d.salidas)||0);

  const maxVal = Math.max(...entradas,...salidas,10);
  const padL=36,padR=20,padT=20,padB=36;
  const chartW=W-padL-padR, chartH=H-padT-padB;
  const n = labels.length || 7;
  const barW=chartW/n*0.35, gap=chartW/n;

  ctx.clearRect(0,0,W,H);
  ctx.strokeStyle = 'rgba(0,0,0,0.1)'; ctx.lineWidth=1;
  for(let i=0;i<=4;i++){
    const y=padT+chartH*(1-i/4);
    ctx.beginPath(); ctx.moveTo(padL,y); ctx.lineTo(W-padR,y); ctx.stroke();
    ctx.fillStyle='#888'; ctx.font='10px Lato,sans-serif'; ctx.textAlign='right';
    ctx.fillText(Math.round(maxVal*i/4),padL-4,y+4);
  }

  labels.forEach((lbl,i)=>{
    const x=padL+i*gap+gap*0.15;
    const eh=entradas[i]/maxVal*chartH;
    const sh=salidas[i]/maxVal*chartH;
    ctx.fillStyle='#198cbd';
    ctx.beginPath(); if(ctx.roundRect) ctx.roundRect(x,padT+chartH-eh,barW,eh,3); else ctx.rect(x,padT+chartH-eh,barW,eh); ctx.fill();
    ctx.fillStyle='#43484c';
    ctx.beginPath(); if(ctx.roundRect) ctx.roundRect(x+barW+4,padT+chartH-sh,barW,sh,3); else ctx.rect(x+barW+4,padT+chartH-sh,barW,sh); ctx.fill();
    ctx.fillStyle='#888'; ctx.textAlign='center'; ctx.font='11px Lato,sans-serif';
    ctx.fillText(lbl, x+barW+2, H-10);
  });
  const lx=W-130, ly=12;
  ctx.fillStyle='#198cbd'; ctx.fillRect(lx,ly,12,10);
  ctx.fillStyle='#43484c'; ctx.textAlign='left'; ctx.font='11px Lato,sans-serif'; ctx.fillText('Entradas',lx+16,ly+9);
  ctx.fillStyle='#43484c'; ctx.fillRect(lx+70,ly,12,10);
  ctx.fillText('Salidas',lx+86,ly+9);
}

function renderDonutChartAPI(data) {
  const canvas = $('chart-donut');
  if(!canvas || !data) return;
  const ctx = canvas.getContext('2d');
  const W=160, H=160; canvas.width=W; canvas.height=H;
  const cx=W/2, cy=H/2, R=68, r=36;
  const total = (data||[]).reduce((s,d)=>s+(parseInt(d.total)||0),0);
  let angle=-Math.PI/2;
  (data||[]).forEach((d,i)=>{
    const count=parseInt(d.total)||0;
    const slice=2*Math.PI*(count/total);
    ctx.beginPath(); ctx.moveTo(cx,cy); ctx.arc(cx,cy,R,angle,angle+slice); ctx.closePath();
    ctx.fillStyle=d.color||'#198cbd'; ctx.fill();
    ctx.strokeStyle='#fff'; ctx.lineWidth=2; ctx.stroke();
    angle+=slice;
  });
  ctx.beginPath(); ctx.arc(cx,cy,r,0,2*Math.PI);
  ctx.fillStyle=document.body.classList.contains('dark-mode')?'#1e1e1e':'#fff'; ctx.fill();
  ctx.fillStyle='#1d1d1d'; ctx.font='bold 20px Lato,sans-serif'; ctx.textAlign='center'; ctx.textBaseline='middle';
  ctx.fillText(total, cx, cy-6);
  ctx.font='9px Lato,sans-serif'; ctx.fillStyle='#888'; ctx.fillText('productos', cx, cy+10);

  const legend=$('donut-legend');
  if(legend) legend.innerHTML=(data||[]).map(d=>`<div class="legend-item"><div class="legend-dot" style="background:${d.color||'#198cbd'}"></div>${d.categoria||d.nombre||''} (${d.total||0})</div>`).join('');
}

function renderDashboard() { loadDashboard(); }

/* ═══════════════════════════════════════
   CATEGORÍAS — API
═══════════════════════════════════════ */
const CAT_COLORS_DEFAULT = ['#198cbd','#C9A84C','#9b59b6','#2d8a4e','#d4820a','#c0392b','#175a7f'];

async function loadCategorias() {
  const res = await api('/categorias/index.php');
  if(!res.success) return;
  APP.categories = res.data;
  poblarSelectCategorias(res.data);
  if(APP.currentSection === 'categorias') renderCategoriasGrid(res.data);
}

function poblarSelectCategorias(cats) {
  document.querySelectorAll('.select-categoria, #filter-cat, #p-cat').forEach(sel => {
    const val = sel.value;
    const isFilter = sel.id === 'filter-cat';
    sel.innerHTML = (isFilter ? '<option value="">Todas las categorías</option>' : '<option value="">-- Selecciona --</option>') +
      cats.map(c => `<option value="${c.id}">${c.nombre}${c.total_productos!==undefined?' ('+c.total_productos+')':''}</option>`).join('');
    if(val) sel.value = val;
  });
}

function renderCategorias() { loadCategorias(); }

function renderCategoriasGrid(cats) {
  const grid = $('categories-grid');
  if(!grid) return;
  grid.innerHTML = cats.map((cat, i) => {
    const color = CAT_COLORS_DEFAULT[i % CAT_COLORS_DEFAULT.length];
    return `<div class="category-card">
      <div class="cat-icon" style="background:${color}22;color:${color}">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M9 9h6M9 12h6M9 15h4"/></svg>
      </div>
      <div class="cat-name">${cat.nombre}</div>
      <div class="cat-count">${cat.descripcion||'Sin descripción'}</div>
      <div class="cat-stats">
        <div class="cat-stat"><div class="cat-stat-val">${cat.total_productos||0}</div><div class="cat-stat-lbl">Productos</div></div>
        <div class="cat-stat"><div class="cat-stat-val" style="color:var(--color-success)">${cat.total_productos||0}</div><div class="cat-stat-lbl">Activos</div></div>
      </div>
      <div style="display:flex;gap:6px;justify-content:center;">
        <button class="btn btn-secondary btn-sm" onclick="openModalCategoria(${cat.id})">✏️ Editar</button>
        <button class="btn btn-primary btn-sm" onclick="filterByCategory(${cat.id})">Ver productos</button>
      </div>
    </div>`;
  }).join('');
}

function filterByCategory(catId) {
  navigateTo('productos');
  setTimeout(()=>{ const sel=$('filter-cat'); if(sel){sel.value=catId;} loadProductos(); },700);
}

function openModalCategoria(id) {
  const cat = APP.categories.find(c=>c.id===id);
  if(!cat) return;
  $('cat-edit-id').value=cat.id;
  $('cat-nombre').value=cat.nombre;
  $('cat-desc').value=cat.descripcion||'';
  $('cat-estado').value=cat.estado||'activo';
  openModal('modal-categoria');
}

async function saveCategoria() {
  const id = $('cat-edit-id').value;
  const data = { nombre:$('cat-nombre').value.trim(), descripcion:$('cat-desc').value.trim() };
  const res = await api(`/categorias/update.php?id=${id}`, 'PUT', data);
  if(res.success) { closeModal('modal-categoria'); showToast('Categoría actualizada'); loadCategorias(); }
  else showToast(res.message||'Error','error');
}

/* ═══════════════════════════════════════
   PRODUCTOS — API
═══════════════════════════════════════ */
// Estado de paginación/filtros productos
const productosState = {
  page:1, limit:10, total:0, pages:0,
  buscar:'', categoria_id:'', estado:'', stock:'',
  orderby:'nombre', order:'asc'
};

async function loadProductos() {
  const params = new URLSearchParams({
    page:         productosState.page,
    limit:        APP.productPageSize || productosState.limit,
    orderby:      productosState.orderby,
    order:        productosState.order,
  });
  if(productosState.buscar)       params.set('buscar',       productosState.buscar);
  if(productosState.categoria_id) params.set('categoria_id', productosState.categoria_id);
  if(productosState.estado)       params.set('estado',       productosState.estado);
  if(productosState.stock)        params.set('stock',        productosState.stock);

  const res = await api(`/productos/index.php?${params}`);
  if(!res.success) { showToast('Error cargando productos','error'); return; }

  APP.products = res.data;
  APP.productFiltered = res.data;
  productosState.total = res.pagination.total;
  productosState.pages = res.pagination.pages;

  $('productos-count-label').textContent = `Productos (${res.pagination.total})`;

  if(APP.productView==='table') renderProductTable();
  else renderProductCards();
}

function applyProductFilters() {
  const cat   = $('filter-cat')?.value   || '';
  const estado= $('filter-estado')?.value|| '';
  const stock = $('filter-stock')?.value || '';
  const buscar= $('prod-search')?.value  || '';
  productosState.categoria_id = cat;
  productosState.estado       = estado;
  productosState.stock        = stock;
  productosState.buscar       = buscar;
  productosState.page         = 1;
  APP.productPage = 1;
  loadProductos();
}

function renderProductos() { loadProductos(); }

function renderProductTable() {
  const tbody = $('productos-tbody');
  const isAdmin = APP.currentRole==='Admin';
  tbody.innerHTML = APP.products.map(p => {
    const sc = stockClassFromStatus(p.stock_status);
    const img = p.imagen
      ? `<img src="${p.imagen}" class="prod-thumb" alt="${p.nombre}" style="object-fit:cover;">`
      : `<div class="prod-thumb"><svg width="20" height="24" viewBox="0 0 60 70" fill="none"><rect x="24" y="0" width="12" height="70" rx="4" fill="#C9A84C" opacity="0.6"/><rect x="0" y="20" width="60" height="12" rx="4" fill="#C9A84C" opacity="0.6"/></svg></div>`;
    const estadoMap = { activo:'Activo', inactivo:'Inactivo', agotado:'Agotado' };
    const estadoLabel = estadoMap[p.estado]||p.estado;
    const badgeClass = { Activo:'badge-success', Inactivo:'badge-neutral', Agotado:'badge-error' }[estadoLabel]||'badge-neutral';
    const actions = isAdmin
      ? `<div style="display:flex;gap:4px;align-items:center;">
           <button class="btn-icon" onclick="editProducto(${p.id})" title="Editar">
             <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
           </button>
           <button class="btn-icon" onclick="deleteProduct(${p.id},'${p.nombre.replace(/'/g,"\\'")}')" title="Eliminar" style="color:var(--color-error)">
             <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/></svg>
           </button>
         </div>`
      : `<button class="btn btn-primary btn-xs" onclick="openModalStock(${p.id})">Actualizar Stock</button>`;
    return `<tr data-prod-id="${p.id}">
      <td class="check-col"><input type="checkbox" class="prod-check" value="${p.id}"></td>
      <td>${img}</td>
      <td><code style="font-size:11px;background:var(--color-primary-light);padding:2px 6px;border-radius:4px;color:var(--color-primary);">${p.sku}</code></td>
      <td><div class="prod-name">${p.nombre}</div><div class="prod-sku">${p.proveedor||''}</div></td>
      <td><span class="badge" style="background:${CAT_COLORS_DEFAULT[0]+'22'};color:${CAT_COLORS_DEFAULT[0]}">${p.nombre_categoria||''}</span></td>
      <td style="font-weight:700;">${fmtMoney(p.precio_venta)}</td>
      <td class="${sc}" style="font-size:15px;font-weight:700;">${p.stock_actual}</td>
      <td style="color:var(--text-muted);">${p.stock_minimo}</td>
      <td><span class="badge ${badgeClass}">${estadoLabel}</span></td>
      <td style="color:var(--text-muted);font-size:12px;">${fmtDate(p.updated_at)}</td>
      <td>${actions}</td>
    </tr>`;
  }).join('') || `<tr><td colspan="11"><div class="empty-state"><div class="empty-state-text">No se encontraron productos</div></div></td></tr>`;

  $('prod-pag-info').textContent = `Mostrando ${Math.min((productosState.page-1)*productosState.limit+1,productosState.total)}–${Math.min(productosState.page*productosState.limit,productosState.total)} de ${productosState.total}`;
  renderPagination('prod-pagination', productosState.page, productosState.pages, pg => { productosState.page=pg; APP.productPage=pg; loadProductos(); });
}

function renderProductCards() {
  const grid = $('prod-cards-grid');
  if(!grid) return;
  grid.innerHTML = APP.products.map(p => {
    const sc = stockClassFromStatus(p.stock_status);
    const img = p.imagen ? `<img src="${p.imagen}" style="width:100%;height:100%;object-fit:cover;" alt="${p.nombre}">` : `<svg width="40" height="46" viewBox="0 0 60 70" fill="none"><rect x="24" y="0" width="12" height="70" rx="4" fill="#C9A84C" opacity="0.7"/><rect x="0" y="20" width="60" height="12" rx="4" fill="#C9A84C" opacity="0.7"/></svg>`;
    const estadoLabel = {activo:'Activo',inactivo:'Inactivo',agotado:'Agotado'}[p.estado]||p.estado;
    const badgeClass = {Activo:'badge-success',Inactivo:'badge-neutral',Agotado:'badge-error'}[estadoLabel]||'badge-neutral';
    return `<div class="product-card">
      <div class="product-card-img">${img}</div>
      <div class="product-card-name">${p.nombre}</div>
      <div class="product-card-sku">${p.sku}</div>
      <div class="product-card-price">${fmtMoney(p.precio_venta)}</div>
      <div class="product-card-stock"><span class="${sc}">Stock: ${p.stock_actual}</span> <span class="badge ${badgeClass}">${estadoLabel}</span></div>
      <div style="margin-top:10px;display:flex;gap:6px;">
        ${APP.currentRole==='Admin'
          ? `<button class="btn btn-primary btn-xs" style="flex:1" onclick="editProducto(${p.id})">Editar</button>
             <button class="btn btn-danger btn-xs" onclick="deleteProduct(${p.id},'${p.nombre.replace(/'/g,"\\'")}')">🗑</button>`
          : `<button class="btn btn-primary btn-xs" style="flex:1" onclick="openModalStock(${p.id})">Actualizar Stock</button>`}
      </div>
    </div>`;
  }).join('') || `<div class="empty-state" style="grid-column:1/-1;"><div class="empty-state-text">No se encontraron productos</div></div>`;
}

function setProductView(view) {
  APP.productView = view;
  $('btn-view-table').classList.toggle('active', view==='table');
  $('btn-view-cards').classList.toggle('active', view==='cards');
  $('prod-table-view').classList.toggle('hidden', view==='cards');
  $('prod-cards-view').classList.toggle('hidden', view==='table');
  renderProductTable();
}
function selectAllProducts(cb) { document.querySelectorAll('.prod-check').forEach(c=>c.checked=cb.checked); }
function changeProductPageSize(val) { APP.productPageSize=parseInt(val); productosState.limit=parseInt(val); productosState.page=1; APP.productPage=1; loadProductos(); }

function renderPagination(containerId, current, total, onPage) {
  const el=$(containerId); if(!el) return;
  let html='';
  html+=`<button class="page-btn" onclick="(${onPage})(${current-1})" ${current<=1?'disabled':''}>‹</button>`;
  const delta=2;
  for(let p=1;p<=total;p++){
    if(p===1||p===total||Math.abs(p-current)<=delta) html+=`<button class="page-btn${p===current?' active':''}" onclick="(${onPage})(${p})">${p}</button>`;
    else if(Math.abs(p-current)===delta+1) html+='<span style="padding:0 4px;color:var(--text-muted)">…</span>';
  }
  html+=`<button class="page-btn" onclick="(${onPage})(${current+1})" ${current>=total?'disabled':''}>›</button>`;
  el.innerHTML=html;
}

/* ═══════════════════════════════════════
   SORTING
═══════════════════════════════════════ */
let sortCol=null, sortAsc=true;
window.handleSort = function(col) {
  const colMap = { name:'nombre', sku:'sku', cat:'nombre_categoria', price:'precio_venta', stock:'stock_actual' };
  const apiCol = colMap[col]||col;
  if(productosState.orderby===apiCol) {
    if(productosState.order==='asc') productosState.order='desc';
    else { productosState.orderby='nombre'; productosState.order='asc'; }
  } else { productosState.orderby=apiCol; productosState.order='asc'; }
  document.querySelectorAll('th.sortable').forEach(th=>{th.classList.remove('sort-asc','sort-desc');th.querySelector('.sort-icon').textContent='⇅';});
  const th=document.querySelector(`th.sortable[onclick="handleSort('${col}')"]`);
  if(th){th.classList.add(productosState.order==='asc'?'sort-asc':'sort-desc');th.querySelector('.sort-icon').textContent=productosState.order==='asc'?'↑':'↓';}
  loadProductos();
};

/* ═══════════════════════════════════════
   PRODUCT MODAL
═══════════════════════════════════════ */
function openModalProducto(id) {
  if(id===null) {
    $('modal-producto-title').textContent='Agregar Producto';
    $('prod-edit-id').value='';
    ['p-nombre','p-sku','p-desc','p-proveedor','p-notas'].forEach(f=>{const el=$(f);if(el)el.value='';});
    ['p-precio','p-costo','p-stock','p-stock-min','p-stock-max'].forEach(f=>{const el=$(f);if(el)el.value='';});
    $('p-cat').value=''; $('p-estado').value='activo'; $('p-unidad').value='pieza';
    if($('p-img-base64'))$('p-img-base64').value='';
    if($('upload-preview')){$('upload-preview').src='';$('upload-preview').style.display='none';}
    const errIds=['err-p-nombre','err-p-cat','err-p-precio','err-p-stock','err-p-sku','err-p-stock-min'];
    errIds.forEach(e=>{const el=$(e);if(el)el.style.display='none';});
  } else {
    editProducto(id); return;
  }
  openModal('modal-producto');
}

async function editProducto(id) {
  const res = await api(`/productos/show.php?id=${id}`);
  if(!res.success) { showToast('Error cargando producto','error'); return; }
  const p = res.data || res;
  $('modal-producto-title').textContent='Editar Producto';
  $('prod-edit-id').value=p.id;
  $('p-nombre').value=p.nombre;
  $('p-sku').value=p.sku;
  $('p-cat').value=p.categoria_id;
  $('p-desc').value=p.descripcion||'';
  $('p-precio').value=p.precio_venta;
  $('p-costo').value=p.precio_costo||'';
  $('p-estado').value=p.estado;
  $('p-stock').value=p.stock_actual;
  $('p-stock-min').value=p.stock_minimo;
  $('p-stock-max').value=p.stock_maximo||'';
  $('p-unidad').value=p.unidad_medida||'pieza';
  $('p-proveedor').value=p.proveedor||'';
  $('p-notas').value=p.notas||'';
  if(p.imagen&&$('p-img-base64')) {
    $('p-img-base64').value=p.imagen;
    if($('upload-preview')){$('upload-preview').src=p.imagen;$('upload-preview').style.display='block';}
  } else if($('upload-preview')){$('upload-preview').src='';$('upload-preview').style.display='none';}
  openModal('modal-producto');
}

function generateSKU() {
  const cat=$('p-cat'); if(!cat||!cat.value) return;
  const catObj=APP.categories.find(c=>c.id==cat.value);
  if(!catObj) return;
  const prefixes={'Imágenes y Santos':'IMG','Velas y Veladoras':'VEL','Rosarios y Medallas':'ROS',
    'Libros y Biblias':'LIB','Incienso y Sahumerios':'INC','Artículos Litúrgicos':'LIT','Joyería Religiosa':'JOY'};
  const prefix=prefixes[catObj.nombre]||catObj.nombre.substring(0,3).toUpperCase();
  const num=String(Math.floor(Math.random()*900)+100).padStart(3,'0');
  $('p-sku').value=`JN-${prefix}-${num}`;
}

async function saveProducto() {
  validateSKU(); validateStockMin();
  const nom=$('p-nombre').value.trim();
  const cat=$('p-cat').value;
  const precio=parseFloat($('p-precio').value);
  let valid=true;
  if(!nom){$('err-p-nombre').style.display='block';valid=false;}else{$('err-p-nombre').style.display='none';}
  if(!cat){$('err-p-cat').style.display='block';valid=false;}else{$('err-p-cat').style.display='none';}
  if(!precio||precio<=0){$('err-p-precio').style.display='block';valid=false;}else{$('err-p-precio').style.display='none';}
  if(isNaN(parseInt($('p-stock').value))){$('err-p-stock').style.display='block';valid=false;}else{$('err-p-stock').style.display='none';}
  if($('err-p-sku')&&$('err-p-sku').style.display==='block') valid=false;
  if(!valid) return;

  const editId=$('prod-edit-id').value;
  const data={
    nombre:nom, sku:$('p-sku').value.trim(), categoria_id:parseInt(cat),
    descripcion:$('p-desc').value.trim(), precio_venta:precio,
    precio_costo:parseFloat($('p-costo').value)||0,
    stock_actual:parseInt($('p-stock').value)||0,
    stock_minimo:parseInt($('p-stock-min').value)||5,
    stock_maximo:parseInt($('p-stock-max').value)||null,
    unidad_medida:$('p-unidad').value, proveedor:$('p-proveedor').value.trim(),
    estado:$('p-estado').value, notas:$('p-notas').value.trim(),
    imagen:$('p-img-base64')?.value||null
  };

  const btn=$('btn-save-prod')||document.querySelector('#modal-producto .btn-primary');
  if(btn){btn.disabled=true;btn.textContent='Guardando...';}

  let res;
  if(editId) res=await api(`/productos/update.php?id=${editId}`,'PUT',data);
  else res=await api('/productos/store.php','POST',data);

  if(btn){btn.disabled=false;btn.textContent='Guardar Producto';}

  if(res.success){ closeModal('modal-producto'); showToast(editId?'Producto actualizado':'Producto creado'); loadProductos(); loadDashboard(); }
  else showToast(res.message||'Error al guardar','error');
}

window.deleteProduct = async function(id, nombre) {
  showConfirm('Eliminar Producto',`¿Deseas eliminar "${nombre}"? El producto quedará inactivo.`, async()=>{
    const res=await api(`/productos/delete.php?id=${id}`,'DELETE');
    if(res.success){showToast('Producto eliminado','warning');loadProductos();loadDashboard();}
    else showToast(res.message||'Error al eliminar','error');
  });
};

function toggleProductState(id) {
  const p=APP.products.find(x=>x.id===id); if(!p) return;
  const nuevoEstado = p.estado==='activo'?'inactivo':'activo';
  api(`/productos/update.php?id=${id}`,'PUT',{...p,estado:nuevoEstado}).then(res=>{
    if(res.success){showToast(`Producto ${nuevoEstado==='activo'?'activado':'desactivado'}`,'info');loadProductos();}
    else showToast(res.message||'Error','error');
  });
}

/* ═══════════════════════════════════════
   STOCK MODAL
═══════════════════════════════════════ */
function openModalStock(id) {
  const p=APP.products.find(x=>x.id===id); if(!p) return;
  $('stock-prod-id').value=p.id;
  $('stock-prod-name').textContent=p.nombre;
  $('stock-prod-sku').textContent=p.sku;
  $('stock-display-val').textContent=p.stock_actual;
  $('stock-display-val').className='stock-display-value '+stockClassFromStatus(p.stock_status);
  $('stock-cantidad').value='';
  $('stock-nota').value='';
  $('stock-motivo').value='compra';
  selectMovType('entrada');
  $('err-stock-cantidad').style.display='none';
  openModal('modal-stock');
}
function openModalStockByName(nombre) {
  const p=APP.products.find(x=>x.nombre===nombre);
  if(p) openModalStock(p.id);
}
function selectMovType(type) {
  APP.selectedMovType=type;
  ['entrada','salida','ajuste'].forEach(t=>{const el=$('rc-'+t);if(el)el.classList.toggle('checked',t===type);});
}
async function registrarMovimiento() {
  const cant=parseInt($('stock-cantidad').value);
  if(!cant||cant<=0){$('err-stock-cantidad').style.display='block';return;}
  $('err-stock-cantidad').style.display='none';
  const data={
    producto_id:parseInt($('stock-prod-id').value),
    tipo:APP.selectedMovType, cantidad:cant,
    motivo:$('stock-motivo').value||'otro',
    notas:$('stock-nota').value.trim()
  };
  const btn=document.querySelector('#modal-stock .btn-primary');
  if(btn){btn.disabled=true;btn.textContent='Registrando...';}
  const res=await api('/movimientos/store.php','POST',data);
  if(btn){btn.disabled=false;btn.textContent='Registrar Movimiento';}
  if(res.success){closeModal('modal-stock');showToast(`Movimiento registrado. Stock nuevo: ${res.data?.stock_nuevo??'—'}`,'success');loadProductos();loadDashboard();}
  else showToast(res.message||'Error al registrar','error');
}

/* ═══════════════════════════════════════
   MOVIMIENTOS — API
═══════════════════════════════════════ */
async function loadMovimientos() {
  const desde=$('mov-desde')?.value||'';
  const hasta=$('mov-hasta')?.value||'';
  const tipo=$('mov-tipo')?.value||'';
  const params=new URLSearchParams({page:APP.movPage||1, limit:APP.movPageSize||15});
  if(desde) params.set('desde',desde);
  if(hasta) params.set('hasta',hasta);
  if(tipo)  params.set('tipo',tipo);

  const res=await api(`/movimientos/index.php?${params}`);
  if(!res.success){showToast('Error cargando movimientos','error');return;}
  APP.movements=res.data;
  APP.movFiltered=res.data;
  renderMovimientos();
}

function applyMovFilters(){ APP.movPage=1; loadMovimientos(); }
function clearMovFilters(){
  ['mov-desde','mov-hasta','mov-tipo','mov-cat','mov-user','mov-search'].forEach(id=>{const el=$(id);if(el)el.value='';});
  applyMovFilters();
}

function renderMovimientos() {
  const tbody=$('movimientos-tbody');
  tbody.innerHTML=(APP.movements||[]).map(m=>{
    const badgeClass=m.tipo==='entrada'?'badge-success':m.tipo==='salida'?'badge-error':'badge-primary';
    const tipoCap=m.tipo.charAt(0).toUpperCase()+m.tipo.slice(1);
    const change=m.tipo==='entrada'?'+':m.tipo==='salida'?'-':'~';
    return `<tr>
      <td style="color:var(--text-muted);font-size:12px;">${m.id}</td>
      <td style="white-space:nowrap;font-size:12px;">${fmtDate(m.created_at)}</td>
      <td><div style="max-width:140px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-weight:700;">${m.nombre_producto||'?'}</div></td>
      <td><code style="font-size:11px;">${m.sku||'—'}</code></td>
      <td><span class="badge ${badgeClass}">${tipoCap}</span></td>
      <td style="font-weight:700;color:${m.tipo==='entrada'?'var(--color-success)':m.tipo==='salida'?'var(--color-error)':'var(--color-primary)'};">${change}${m.cantidad}</td>
      <td style="color:var(--text-muted);">${m.stock_anterior}</td>
      <td style="font-weight:700;">${m.stock_nuevo}</td>
      <td>${m.motivo}</td>
      <td style="font-size:11px;color:var(--text-muted);">${m.nombre_usuario||'—'}</td>
      <td style="font-size:11px;color:var(--text-muted);max-width:100px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${m.notas||'—'}</td>
    </tr>`;
  }).join('')||`<tr><td colspan="11"><div class="empty-state"><div class="empty-state-text">No hay movimientos registrados</div></div></td></tr>`;
}

async function exportMovimientosCSV() {
  const headers=['#','Fecha','Producto','SKU','Tipo','Cantidad','Stock Ant.','Stock Nuevo','Motivo','Usuario','Notas'];
  const rows=(APP.movements||[]).map(m=>[m.id,m.created_at,m.nombre_producto||'?',m.sku||'?',m.tipo,m.cantidad,m.stock_anterior,m.stock_nuevo,m.motivo,m.nombre_usuario||'',m.notas||''].map(v=>`"${v}"`).join(','));
  downloadCSV('movimientos_'+today()+'.csv',[headers.join(','),...rows].join('\n'));
  showToast('CSV exportado exitosamente');
}

/* ═══════════════════════════════════════
   ALERTAS — API
═══════════════════════════════════════ */
async function loadAlertas() {
  const res=await api('/dashboard/stats.php');
  if(!res.success) return;
  const alertas=res.data.alertas_stock||[];
  const sinStock=alertas.filter(p=>p.stock_actual===0||p.stock_actual==='0');
  const stockBajo=alertas.filter(p=>parseInt(p.stock_actual)>0&&parseInt(p.stock_actual)<=parseInt(p.stock_minimo));
  const proximo=alertas.filter(p=>parseInt(p.stock_actual)>parseInt(p.stock_minimo)&&parseInt(p.stock_actual)<=parseInt(p.stock_minimo)+5);
  $('badge-sin').textContent=sinStock.length;
  $('badge-bajo').textContent=stockBajo.length;
  $('badge-proximo').textContent=proximo.length;
  updateNotifBadge(sinStock.length+stockBajo.length);

  $('alert-sin-body').innerHTML=sinStock.map(p=>`<tr>
    <td><span style="font-weight:700;">${p.nombre}</span></td>
    <td><code style="font-size:11px;">${p.sku}</code></td>
    <td><span class="badge" style="background:#198cbd22;color:#198cbd">${p.categoria}</span></td>
    <td style="font-size:12px;color:var(--text-muted);">—</td>
    <td><button class="btn btn-success btn-xs" onclick="openModalStockByName('${p.nombre.replace(/'/g,"\\'")}')">Registrar Entrada</button></td>
  </tr>`).join('')||'<tr><td colspan="5" style="text-align:center;padding:20px;color:var(--text-muted);">✅ Sin productos agotados</td></tr>';

  $('alert-bajo-body').innerHTML=stockBajo.map(p=>`<tr>
    <td><span style="font-weight:700;">${p.nombre}</span></td>
    <td class="stock-warn" style="font-weight:700;">${p.stock_actual}</td>
    <td>${p.stock_minimo}</td>
    <td class="stock-bad">-${p.diferencia}</td>
    <td><button class="btn btn-primary btn-xs" onclick="openModalStockByName('${p.nombre.replace(/'/g,"\\'")}')">Registrar Entrada</button></td>
  </tr>`).join('')||'<tr><td colspan="5" style="text-align:center;padding:20px;color:var(--text-muted);">✅ Sin productos en stock bajo</td></tr>';

  $('alert-proximo-body').innerHTML=proximo.map(p=>`<tr>
    <td><span style="font-weight:700;">${p.nombre}</span></td>
    <td style="font-weight:700;color:var(--color-warning);">${p.stock_actual}</td>
    <td>${p.stock_minimo}</td>
    <td>📉 Descendente</td>
    <td style="color:var(--color-warning);font-weight:700;">~${Math.round(parseInt(p.stock_actual)*2.5)} días</td>
    <td><button class="btn btn-primary btn-xs" onclick="openModalStockByName('${p.nombre.replace(/'/g,"\\'")}')">Registrar Entrada</button></td>
  </tr>`).join('')||'<tr><td colspan="6" style="text-align:center;padding:20px;color:var(--text-muted);">✅ Sin productos próximos a agotarse</td></tr>';
}

function renderAlertas() { loadAlertas(); }

/* ═══════════════════════════════════════
   REPORTES — API
═══════════════════════════════════════ */
async function loadReportes() {}

async function selectReport(id, card) {
  document.querySelectorAll('.report-card').forEach(c=>c.classList.remove('selected'));
  document.querySelectorAll('.report-detail').forEach(d=>d.classList.remove('active'));
  card.classList.add('selected');
  $('report-'+id).classList.add('active');
  const tipo=id.replace('-','_');
  const res=await api(`/reportes/index.php?tipo=${tipo}`);
  if(!res.success){showToast('Error cargando reporte','error');return;}
  if(id==='inventario') renderReportInventario(res.data);
  else if(id==='movimientos') renderReportMovimientosAPI(res.data);
  else if(id==='top-productos') renderReportTopAPI(res.data);
  else if(id==='valorizacion') renderReportValorizacionAPI(res.data);
}

function renderReportInventario(data) {
  if(!data) return;
  let totalVal=data.reduce((s,p)=>s+parseFloat(p.valor_total||0),0);
  $('report-inventario-content').innerHTML=`
    <div class="data-table-wrapper" style="overflow-x:auto;">
      <table class="data-table">
        <thead><tr><th>Producto</th><th>SKU</th><th>Categoría</th><th>Stock</th><th>Precio</th><th style="text-align:right;">Valor</th></tr></thead>
        <tbody>${data.map(p=>`<tr><td>${p.nombre}</td><td><code style="font-size:11px;">${p.sku}</code></td><td>${p.categoria}</td><td>${p.stock_actual}</td><td>${fmtMoney(p.precio_venta)}</td><td style="text-align:right;">${fmtMoney(p.valor_total)}</td></tr>`).join('')}</tbody>
        <tfoot><tr style="font-weight:700;border-top:2px solid var(--color-gold);"><td colspan="5">TOTAL INVENTARIO</td><td style="text-align:right;color:var(--color-gold);font-size:15px;">${fmtMoney(totalVal)}</td></tr></tfoot>
      </table>
    </div>`;
}

function renderReportMovimientosAPI(data) {
  if(!data) return;
  const entradas=data.filter(m=>m.tipo==='entrada');
  const salidas=data.filter(m=>m.tipo==='salida');
  const totEnt=entradas.reduce((s,m)=>s+parseInt(m.cantidad),0);
  const totSal=salidas.reduce((s,m)=>s+parseInt(m.cantidad),0);
  $('report-movimientos-content').innerHTML=`
    <div class="summary-boxes">
      <div class="summary-box"><div class="summary-box-val" style="color:var(--color-success)">${totEnt}</div><div class="summary-box-lbl">Total Entradas</div></div>
      <div class="summary-box" style="background:rgba(192,57,43,0.12)"><div class="summary-box-val" style="color:var(--color-error)">${totSal}</div><div class="summary-box-lbl">Total Salidas</div></div>
      <div class="summary-box" style="background:rgba(45,138,78,0.12)"><div class="summary-box-val" style="color:var(--color-success)">${totEnt>totSal?'+':''}${totEnt-totSal}</div><div class="summary-box-lbl">Balance Neto</div></div>
    </div>
    <div class="data-table-wrapper" style="overflow-x:auto;">
      <table class="data-table">
        <thead><tr><th>Fecha</th><th>Producto</th><th>Tipo</th><th>Cantidad</th><th>Motivo</th><th>Usuario</th></tr></thead>
        <tbody>${data.map(m=>{const bc=m.tipo==='entrada'?'badge-success':m.tipo==='salida'?'badge-error':'badge-primary';return `<tr><td>${fmtDate(m.created_at)}</td><td>${m.nombre_producto||'?'}</td><td><span class="badge ${bc}">${m.tipo}</span></td><td style="font-weight:700;">${m.cantidad}</td><td>${m.motivo}</td><td>${m.nombre_usuario||''}</td></tr>`;}).join('')}</tbody>
      </table>
    </div>`;
}

function renderReportTopAPI(data) {
  if(!data) return;
  const maxVal=data[0]?parseInt(data[0].total_movido):1;
  $('report-top-content').innerHTML=`<div class="bar-chart-horiz">${data.map(p=>{const pct=parseInt(p.total_movido)/maxVal*100;return `<div class="bar-horiz-item"><div class="bar-horiz-label" title="${p.nombre}">${p.nombre}</div><div class="bar-horiz-track"><div class="bar-horiz-fill" style="width:${pct}%"></div></div><div class="bar-horiz-val">${p.total_movido}</div></div>`;}).join('')}</div>`;
}

function renderReportValorizacionAPI(data) {
  if(!data) return;
  let tc=data.reduce((s,d)=>s+parseFloat(d.costo_total||0),0);
  let tv=data.reduce((s,d)=>s+parseFloat(d.valor_venta||0),0);
  $('report-valorizacion-content').innerHTML=`
    <div class="summary-boxes">
      <div class="summary-box"><div class="summary-box-val">${fmtMoney(tc)}</div><div class="summary-box-lbl">Costo Total</div></div>
      <div class="summary-box" style="background:rgba(45,138,78,0.12)"><div class="summary-box-val" style="color:var(--color-success)">${fmtMoney(tv)}</div><div class="summary-box-lbl">Valor Venta</div></div>
      <div class="summary-box" style="background:rgba(201,168,76,0.12)"><div class="summary-box-val" style="color:var(--color-gold)">${fmtMoney(tv-tc)}</div><div class="summary-box-lbl">Margen Bruto</div></div>
    </div>
    <div class="data-table-wrapper" style="overflow-x:auto;">
      <table class="data-table">
        <thead><tr><th>Categoría</th><th>Productos</th><th>Costo Total</th><th>Valor Venta</th><th>Margen</th></tr></thead>
        <tbody>${data.map(d=>`<tr><td>${d.categoria}</td><td>${d.productos||0}</td><td>${fmtMoney(d.costo_total)}</td><td>${fmtMoney(d.valor_venta)}</td><td style="color:var(--color-success);font-weight:700;">${fmtMoney(parseFloat(d.valor_venta||0)-parseFloat(d.costo_total||0))}</td></tr>`).join('')}</tbody>
        <tfoot><tr style="font-weight:700;border-top:2px solid var(--color-gold);"><td colspan="2">TOTAL</td><td>${fmtMoney(tc)}</td><td>${fmtMoney(tv)}</td><td style="color:var(--color-success);">${fmtMoney(tv-tc)}</td></tr></tfoot>
      </table>
    </div>`;
}

async function exportReportCSV(type) {
  const res=await api(`/reportes/index.php?tipo=${type.replace('-','_')}`);
  if(!res.success){showToast('Error al exportar','error');return;}
  let content='',filename='';
  if(type==='inventario'){
    content=['Producto,SKU,Categoría,Stock,Precio,Valor',...res.data.map(p=>[p.nombre,p.sku,p.categoria,p.stock_actual,p.precio_venta,p.valor_total].map(v=>`"${v}"`).join(','))].join('\n');
    filename='inventario_'+today()+'.csv';
  } else if(type==='movimientos'){
    content=['Fecha,Producto,Tipo,Cantidad,Motivo,Usuario',...res.data.map(m=>[m.created_at,m.nombre_producto||'',m.tipo,m.cantidad,m.motivo,m.nombre_usuario||''].map(v=>`"${v}"`).join(','))].join('\n');
    filename='movimientos_'+today()+'.csv';
  }
  if(content){ downloadCSV(filename,content); showToast('CSV exportado'); }
}

function renderReportes() {}

/* ═══════════════════════════════════════
   USUARIOS — API
═══════════════════════════════════════ */
async function loadUsuarios() {
  const res=await api('/usuarios/index.php');
  if(res.success){ APP.users=res.data; renderUsuarios(); }
}

function renderUsuarios() {
  const tbody=$('usuarios-tbody');
  tbody.innerHTML=(APP.users||[]).map(u=>`<tr>
    <td><div class="user-list-avatar" style="background:${avatarColor(u.nombre)}">${initials(u.nombre)}</div></td>
    <td style="font-weight:700;">${u.nombre}</td>
    <td><code style="font-size:12px;">${u.username}</code></td>
    <td><span class="badge ${u.rol==='admin'?'badge-primary':'badge-warning'}">${u.rol}</span></td>
    <td>${u.estado==='activo'?'<span class="badge badge-success">Activo</span>':'<span class="badge badge-neutral">Inactivo</span>'}</td>
    <td style="font-size:12px;color:var(--text-muted);">${u.ultimo_acceso?fmtDate(u.ultimo_acceso):'Nunca'}</td>
    <td>
      <div style="display:flex;gap:4px;">
        <button class="btn-icon" onclick="openModalUsuario(${u.id})" title="Editar">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
        </button>
        <button class="btn-icon" style="color:var(--color-error)" onclick="deleteUser(${u.id},'${u.nombre.replace(/'/g,"\\'")}')">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/></svg>
        </button>
      </div>
    </td>
  </tr>`).join('');
}

function openModalUsuario(id) {
  $('usr-pass-group').style.display='block';
  if(id===null){
    $('modal-usuario-title').textContent='Agregar Usuario';
    $('usr-edit-id').value='';
    ['usr-nombre','usr-user','usr-pass'].forEach(f=>{const el=$(f);if(el)el.value='';});
    $('usr-rol').value='empleado'; $('usr-estado').value='activo';
  } else {
    const u=APP.users.find(x=>x.id===id); if(!u) return;
    $('modal-usuario-title').textContent='Editar Usuario';
    $('usr-edit-id').value=u.id;
    $('usr-nombre').value=u.nombre;
    $('usr-user').value=u.username;
    $('usr-pass').value='';
    $('usr-pass-group').style.display='none';
    $('usr-rol').value=u.rol;
    $('usr-estado').value=u.estado;
  }
  ['err-usr-nombre','err-usr-user','err-usr-dup'].forEach(id=>{const el=$(id);if(el)el.style.display='none';});
  openModal('modal-usuario');
}

async function saveUsuario() {
  validateUsername();
  const nom=$('usr-nombre').value.trim();
  const user=$('usr-user').value.trim();
  let valid=true;
  if(!nom){$('err-usr-nombre').style.display='block';valid=false;}else{$('err-usr-nombre').style.display='none';}
  if(!user){$('err-usr-user').style.display='block';valid=false;}else{$('err-usr-user').style.display='none';}
  if($('err-usr-dup')&&$('err-usr-dup').style.display==='block') valid=false;
  if(!valid) return;

  const editId=$('usr-edit-id').value;
  const data={nombre:nom, username:user, rol:$('usr-rol').value, estado:$('usr-estado').value};
  if(!editId){
    data.password=$('usr-pass').value;
    if(!data.password||data.password.length<6){showToast('La contraseña debe tener mínimo 6 caracteres','error');return;}
  } else {
    const pass=$('usr-pass').value;
    if(pass&&pass.length>=6) data.password=pass;
  }

  const btn=document.querySelector('#modal-usuario .btn-primary');
  if(btn){btn.disabled=true;}

  let res;
  if(editId) res=await api(`/usuarios/update.php?id=${editId}`,'PUT',data);
  else res=await api('/usuarios/store.php','POST',data);
  if(btn){btn.disabled=false;}

  if(res.success){closeModal('modal-usuario');showToast(editId?'Usuario actualizado':'Usuario creado');loadUsuarios();}
  else showToast(res.message||'Error al guardar usuario','error');
}

window.deleteUser = async function(id, nombre) {
  showConfirm('Desactivar Usuario',`¿Desactivar a "${nombre}"? Ya no podrá iniciar sesión.`, async()=>{
    const res=await api(`/usuarios/delete.php?id=${id}`,'DELETE');
    if(res.success){showToast('Usuario desactivado','warning');loadUsuarios();}
    else showToast(res.message||'Error','error');
  },'warning');
};

/* ═══════════════════════════════════════
   CONFIGURACIÓN — API
═══════════════════════════════════════ */
async function loadConfiguracion() {
  const res=await api('/configuracion/index.php');
  if(!res.success) return;
  const cfg=res.data;
  const map={
    'cfg-nombre':'nombre_negocio','cfg-direccion':'direccion',
    'cfg-telefono':'telefono','cfg-email':'email',
    'cfg-moneda':'moneda','cfg-stock-min':'stock_minimo_global','cfg-iva':'iva_porcentaje'
  };
  Object.entries(map).forEach(([elId,key])=>{const el=$(elId);if(el&&cfg[key]!==undefined)el.value=cfg[key];});
}

async function saveConfig() {
  const config={};
  const map={
    'cfg-nombre':'nombre_negocio','cfg-direccion':'direccion',
    'cfg-telefono':'telefono','cfg-email':'email',
    'cfg-moneda':'moneda','cfg-stock-min':'stock_minimo_global','cfg-iva':'iva_porcentaje'
  };
  Object.entries(map).forEach(([elId,key])=>{const el=$(elId);if(el)config[key]=el.value;});
  const res=await api('/configuracion/update.php','PUT',{config});
  if(res.success) showToast('Configuración guardada exitosamente');
  else showToast('Error al guardar configuración','error');
}

/* ═══════════════════════════════════════
   DARK MODE
═══════════════════════════════════════ */
function toggleDarkMode(enabled) {
  APP.darkMode=enabled;
  document.body.classList.toggle('dark-mode',enabled);
  const cb=$('toggle-dark-mode'); if(cb) cb.checked=enabled;
  if(APP.currentSection==='dashboard') setTimeout(()=>{loadDashboard();},100);
  showToast(enabled?'Modo oscuro activado':'Modo claro activado','info');
}

/* ═══════════════════════════════════════
   VALIDACIONES (preservadas)
═══════════════════════════════════════ */
window.validateProductName=function(){const v=$('p-nombre').value;const cnt=$('p-nombre-counter');if(cnt)cnt.textContent=`${v.length}/100`;if(v.length>100)$('p-nombre').value=v.substring(0,100);};
window.validateSKU=function(){const sku=$('p-sku').value.trim();const id=$('prod-edit-id').value;const exists=APP.products.find(p=>p.sku===sku&&p.id!=id);if(exists){$('p-sku').classList.add('error');if($('err-p-sku'))$('err-p-sku').style.display='block';}else{$('p-sku').classList.remove('error');if($('err-p-sku'))$('err-p-sku').style.display='none';}};
window.validatePrices=function(){const price=parseFloat($('p-precio').value)||0;const cost=parseFloat($('p-costo').value)||0;if(cost>price&&price>0)$('warn-p-precio').style.display='flex';else if($('warn-p-precio'))$('warn-p-precio').style.display='none';};
window.validateStockMin=function(){const smin=parseInt($('p-stock-min').value)||0;const sact=parseInt($('p-stock').value)||0;if(smin>sact){$('p-stock-min').classList.add('error');if($('err-p-stock-min'))$('err-p-stock-min').style.display='block';}else{$('p-stock-min').classList.remove('error');if($('err-p-stock-min'))$('err-p-stock-min').style.display='none';}};
window.validateUsername=function(){const u=$('usr-user').value.trim();const id=$('usr-edit-id').value;if(APP.users.find(x=>x.username===u&&x.id!=id)){$('usr-user').classList.add('error');if($('err-usr-dup'))$('err-usr-dup').style.display='block';}else{$('usr-user').classList.remove('error');if($('err-usr-dup'))$('err-usr-dup').style.display='none';}};
window.checkPassStrength=function(val){const bar=$('pass-bar');const txt=$('pass-text');if(!bar||!txt)return;if(val.length===0){bar.style.width='0';txt.textContent='Mínimo 6 caracteres';return;}let str=0;if(val.length>=6)str++;if(val.length>=8)str++;if(/[A-Za-z]/.test(val)&&/[0-9]/.test(val))str++;if(str===1){bar.style.width='33%';bar.style.background='var(--color-error)';txt.textContent='Débil';txt.style.color='var(--color-error)';}else if(str===2){bar.style.width='66%';bar.style.background='var(--color-warning)';txt.textContent='Media';txt.style.color='var(--color-warning)';}else if(str>=3){bar.style.width='100%';bar.style.background='var(--color-success)';txt.textContent='Fuerte';txt.style.color='var(--color-success)';}};

/* ═══════════════════════════════════════
   IMAGE UPLOAD (preservado)
═══════════════════════════════════════ */
window.handleFileSelect=function(input){const file=input.files[0];if(!file)return;processImageFile(file);};
window.handleDrop=function(e){e.preventDefault();e.currentTarget.style.borderColor='';const file=e.dataTransfer.files[0];if(!file)return;processImageFile(file);};
function processImageFile(file){const validTypes=['image/jpeg','image/png','image/webp'];if(!validTypes.includes(file.type)||file.size>2097152){if($('err-p-img'))$('err-p-img').style.display='block';return;}if($('err-p-img'))$('err-p-img').style.display='none';const reader=new FileReader();reader.onload=(e)=>{if($('p-img-base64'))$('p-img-base64').value=e.target.result;if($('upload-preview')){$('upload-preview').src=e.target.result;$('upload-preview').style.display='block';}};reader.readAsDataURL(file);}
window.removeImage=function(e){e.stopPropagation();if($('p-img-base64'))$('p-img-base64').value='';if($('p-img-file'))$('p-img-file').value='';if($('upload-preview')){$('upload-preview').src='';$('upload-preview').style.display='none';}};

/* ═══════════════════════════════════════
   MODAL CONFIRM (preservado)
═══════════════════════════════════════ */
let confirmCallback=null;
function showConfirm(title,message,onConfirm,type='danger'){
  $('confirm-title').textContent=title;
  $('confirm-message').textContent=message;
  const icon=$('confirm-icon');
  icon.className=`modal-confirm-icon ${type}`;
  if(type==='warning'){
    icon.innerHTML=`<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>`;
    $('confirm-ok').className='btn btn-warning';$('confirm-ok').style.background='var(--color-warning)';$('confirm-ok').style.color='#fff';
  }else{
    icon.innerHTML=`<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/></svg>`;
    $('confirm-ok').className='btn btn-danger';$('confirm-ok').style.background='';
  }
  confirmCallback=onConfirm;
  openModal('modal-confirm');
}
document.addEventListener('DOMContentLoaded',()=>{const btn=$('confirm-ok');if(btn)btn.addEventListener('click',()=>{if(confirmCallback)confirmCallback();closeModal('modal-confirm');});});

/* ═══════════════════════════════════════
   EXPORT PDF (usando datos de API)
═══════════════════════════════════════ */
window.exportPDF = async function(type) {
  if(!window.jspdf) { showToast('Cargando librería PDF... intenta de nuevo','warning'); return; }
  const { jsPDF } = window.jspdf;
  const doc = new jsPDF('p','pt','letter');
  doc.setFillColor(201,168,76); doc.rect(40,40,10,40,'F');
  doc.setFontSize(20); doc.setTextColor(28,90,127); doc.setFont("helvetica","bold");
  doc.text("Jesús de Nazaret",60,65);
  doc.setLineWidth(1); doc.setDrawColor(201,168,76); doc.line(40,90,570,90);
  doc.setFontSize(14); doc.setTextColor(50,50,50);

  let title='',filename='',body=[],head=[],foot=[];
  const tipo=type.replace('-','_');
  const res=await api(`/reportes/index.php?tipo=${tipo}`);
  if(!res.success){showToast('Error generando PDF','error');return;}

  if(type==='inventario'){
    title='Reporte de Inventario Actual'; filename='inventario_'+today()+'.pdf';
    head=[['Producto','SKU','Categoría','Stock','Precio','Valor']];
    let total=0;
    body=res.data.map(p=>{total+=parseFloat(p.valor_total||0);return [p.nombre,p.sku,p.categoria,p.stock_actual.toString(),'$'+p.precio_venta,'$'+p.valor_total];});
    foot=[['','','','','TOTAL','$'+total]];
  } else if(type==='movimientos'){
    title='Reporte de Movimientos'; filename='movimientos_'+today()+'.pdf';
    head=[['Fecha','Producto','Tipo','Cantidad','Motivo','Usuario']];
    body=res.data.map(m=>[fmtDate(m.created_at),m.nombre_producto||'?',m.tipo,m.cantidad.toString(),m.motivo,m.nombre_usuario||'']);
  } else if(type==='top-productos'){
    title='Top 10 Productos Más Movidos'; filename='top_productos_'+today()+'.pdf';
    head=[['Ranking','Producto','SKU','Total Movido']];
    body=res.data.map((p,i)=>[(i+1).toString(),p.nombre,p.sku,p.total_movido.toString()]);
  } else if(type==='valorizacion'){
    title='Valorización del Inventario'; filename='valorizacion_'+today()+'.pdf';
    head=[['Categoría','Productos','Costo Total','Valor Venta','Margen']];
    let tc=0,tv=0;
    body=res.data.map(d=>{tc+=parseFloat(d.costo_total||0);tv+=parseFloat(d.valor_venta||0);return [d.categoria,d.productos||'0','$'+d.costo_total,'$'+d.valor_venta,'$'+(parseFloat(d.valor_venta||0)-parseFloat(d.costo_total||0))];});
    foot=[['TOTAL','','$'+tc,'$'+tv,'$'+(tv-tc)]];
  }

  doc.text(title,40,120);
  doc.autoTable({startY:140,head,body,foot:foot.length?foot:false,theme:'grid',headStyles:{fillColor:[23,90,127],textColor:255,fontStyle:'bold'},footStyles:{fillColor:[29,29,29],textColor:255,fontStyle:'bold'},alternateRowStyles:{fillColor:[248,246,242]},styles:{font:"helvetica",fontSize:10}});
  doc.setFontSize(9); doc.setTextColor(150,150,150);
  doc.text(`Generado el ${fmtDate(today())} por ${APP.currentUser}`,40,doc.internal.pageSize.height-30);
  doc.save(filename);
  showToast('PDF generado exitosamente');
};

/* ═══════════════════════════════════════
   HASH NAVIGATION + CANVAS POLYFILL
═══════════════════════════════════════ */
window.addEventListener('hashchange',()=>{
  if(!APP.currentUser) return;
  const hash=window.location.hash.replace('#','');
  if(hash) navigateTo(hash);
});

if(!CanvasRenderingContext2D.prototype.roundRect){
  CanvasRenderingContext2D.prototype.roundRect=function(x,y,w,h,r){
    if(w<2*r)r=w/2;if(h<2*r)r=h/2;
    this.beginPath();this.moveTo(x+r,y);this.arcTo(x+w,y,x+w,y+h,r);this.arcTo(x+w,y+h,x,y+h,r);this.arcTo(x,y+h,x,y,r);this.arcTo(x,y,x+w,y,r);this.closePath();return this;
  };
}

/* ═══════════════════════════════════════
   INIT
═══════════════════════════════════════ */
setTimeout(()=>{
  const repDesde=$('rep-mov-desde');
  const repHasta=$('rep-mov-hasta');
  if(repDesde&&repHasta){
    const d=new Date();
    repDesde.value=new Date(d.getFullYear(),d.getMonth(),1).toISOString().split('T')[0];
    repHasta.value=today();
  }
},0);

function switchConfigTab(id,btn){document.querySelectorAll('#view-configuracion .tab-btn').forEach(b=>b.classList.remove('active'));document.querySelectorAll('#view-configuracion .tab-pane').forEach(p=>p.classList.remove('active'));btn.classList.add('active');$('config-tab-'+id).classList.add('active');}
function switchAlertTab(id,btn){document.querySelectorAll('#view-alertas .tab-btn').forEach(b=>b.classList.remove('active'));document.querySelectorAll('#view-alertas .tab-pane').forEach(p=>p.classList.remove('active'));btn.classList.add('active');$('tab-'+id).classList.add('active');}

function downloadCSV(filename,content){const blob=new Blob(['\uFEFF'+content],{type:'text/csv;charset=utf-8;'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=filename;a.click();URL.revokeObjectURL(a.href);}

console.log('%c\u{1F54A}\uFE0F Panel Inventario — Jesús de Nazaret v2.0 (API)', 'font-size:14px;color:#198cbd;font-weight:bold;');
console.log('%cConectado a: ' + API_BASE, 'color:#C9A84C;');"""

# Find exact positions
start_idx = html.find(OLD_APP_BLOCK_START)
end_idx   = html.find(OLD_APP_BLOCK_END)

if start_idx == -1:
    print("ERROR: No se encontró 'const APP = {' en el archivo.")
    exit(1)
if end_idx == -1:
    print("ERROR: No se encontró el console.log final.")
    exit(1)

end_idx += len(OLD_APP_BLOCK_END)

print(f"Bloque JS encontrado: líneas aproximadas {html[:start_idx].count(chr(10))+1} – {html[:end_idx].count(chr(10))+1}")
print(f"Tamaño del bloque a reemplazar: {end_idx - start_idx} bytes")

new_html = html[:start_idx] + NEW_APP_BLOCK + html[end_idx:]

with open(src, "w", encoding="utf-8") as f:
    f.write(new_html)

print(f"✅ inventario.html actualizado. Nuevo tamaño: {len(new_html.splitlines())} líneas")
