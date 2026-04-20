/* ═══════════════════════════════════════════════════════════
   Exposys Mart — Application Logic v2
   ═══════════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {

  initTraffic();

  const pg = detectPage();
  if (pg === 'home')     initHome();
  if (pg === 'product')  initProduct();
  if (pg === 'cart')     initCart();
  if (pg === 'checkout') initCheckout();
});

function detectPage() {
  const p = location.pathname;
  if (p.includes('product.html'))  return 'product';
  if (p.includes('cart.html'))     return 'cart';
  if (p.includes('checkout.html')) return 'checkout';
  return 'home';
}

/* ════════════════════════════════════════════════════════
   HOME
   ════════════════════════════════════════════════════════ */
function initHome() {
  track('homepage', 'pageview');
  renderSkeletons();
  loadProducts();
  initCategoryStrip();
  initSearch();
  updateBadge();
}

function renderSkeletons() {
  const g = document.getElementById('product-grid');
  if (!g) return;
  g.innerHTML = Array(8).fill('').map(() => `
    <div class="p-card" style="pointer-events:none">
      <div class="p-img-wrap"><div class="skeleton" style="width:140px;height:140px;border-radius:var(--r-md)"></div></div>
      <div class="p-body">
        <div class="skeleton" style="height:10px;width:60px"></div>
        <div class="skeleton" style="height:14px;width:100%;margin:6px 0"></div>
        <div class="skeleton" style="height:14px;width:75%"></div>
        <div class="skeleton" style="height:11px;width:85px;margin:8px 0"></div>
        <div class="skeleton" style="height:18px;width:80px"></div>
      </div>
    </div>
  `).join('');
}

async function loadProducts(category = null) {
  const grid = document.getElementById('product-grid');
  if (!grid) return;
  try {
    const data = await StoreAPI.getProducts(category);
    renderProducts(grid, data.products || []);
  } catch {
    grid.innerHTML = `<p style="padding:40px 0;color:var(--text-muted);font-size:.9rem;">Could not load products — is the backend running on port 8000?</p>`;
  }
}

function renderProducts(grid, products) {
  grid.innerHTML = products.map(p => {
    const disc = Math.round((1 - p.price / p.original_price) * 100);
    return `
      <div class="p-card fade-up" data-id="${p.id}" tabindex="0" role="button">
        <span class="p-badge ${badgeClass(p.badge)}">${p.badge}</span>
        <div class="p-img-wrap">
          <img src="${p.image}" alt="${p.name}" loading="lazy"
               onerror="this.closest('.p-img-wrap').innerHTML='<svg width=60 height=60 viewBox=\'0 0 24 24\' fill=none stroke=\'#c7d2fe\' stroke-width=1.5><path d=\'M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z\'/></svg>'">
        </div>
        <div class="p-body">
          <div class="p-brand">${p.brand}</div>
          <div class="p-name">${p.name}</div>
          <div class="p-stars">
            <div class="star-row">${renderStars(p.rating)}</div>
            <span class="p-review-count">(${p.reviews.toLocaleString()})</span>
          </div>
          <div class="p-price-row">
            <span class="p-price">₹${p.price.toLocaleString()}</span>
            <span class="p-original">₹${p.original_price.toLocaleString()}</span>
            <span class="p-discount">${disc}% off</span>
          </div>
          <div class="p-footer">
            <button class="btn btn-cart btn-sm add-btn" data-id="${p.id}">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="width:14px;height:14px"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 001.99 1.61h9.72a2 2 0 001.99-1.61L23 6H6"/></svg>
              Add
            </button>
            <a href="product.html?id=${p.id}" class="btn btn-secondary btn-sm">View</a>
          </div>
        </div>
      </div>
    `;
  }).join('');

  // Add to cart (login required)
  grid.querySelectorAll('.add-btn').forEach(btn => {
    btn.addEventListener('click', e => {
      e.stopPropagation();
      if (!StoreAPI.isLoggedIn()) {
        showToast('Please login to add items to cart', 'info');
        setTimeout(() => { window.location.href = 'auth.html'; }, 1200);
        return;
      }
      const id = parseInt(btn.dataset.id);
      const p  = products.find(x => x.id === id);
      if (p) { Cart.add(p, 1); showToast(`<strong>${p.name}</strong> added to cart`, 'success'); track('homepage', 'add_to_cart', id); }
    });
  });

  // Click card → product page
  grid.querySelectorAll('.p-card').forEach(card => {
    card.addEventListener('click', e => {
      if (e.target.closest('button,a')) return;
      const id = parseInt(card.dataset.id);
      track('homepage', 'click', id);
      location.href = `product.html?id=${id}`;
    });
    card.addEventListener('keydown', e => { if (e.key === 'Enter') card.click(); });
  });
}

function initCategoryStrip() {
  const strip = document.getElementById('cat-strip');
  if (!strip) return;
  strip.addEventListener('click', e => {
    const btn = e.target.closest('.cat-chip');
    if (!btn) return;
    strip.querySelectorAll('.cat-chip').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    const cat = btn.dataset.category;
    const title = document.getElementById('section-title');
    if (title) title.textContent = cat === 'all' ? 'Featured Products' : btn.textContent.trim();
    renderSkeletons();
    loadProducts(cat);
    track('homepage', 'category_filter', null, null, cat);
  });
}

/* Global function for category banners */
function filterByCategory(cat) {
  // Scroll to products section
  const productsEl = document.getElementById('products');
  if (productsEl) productsEl.scrollIntoView({ behavior: 'smooth', block: 'start' });

  // Update category strip active state
  const strip = document.getElementById('cat-strip');
  if (strip) {
    strip.querySelectorAll('.cat-chip').forEach(b => {
      b.classList.toggle('active', b.dataset.category === cat);
    });
  }

  // Update section title
  const title = document.getElementById('section-title');
  const names = { electronics: 'Electronics', fashion: 'Fashion', home: 'Home & Living', books: 'Books' };
  if (title) title.textContent = names[cat] || 'Featured Products';

  renderSkeletons();
  loadProducts(cat);
  track('homepage', 'category_filter', null, null, cat);
}

function initSearch() {
  const input = document.getElementById('search-input');
  const btn   = document.getElementById('search-btn');
  if (!input) return;

  const doSearch = async () => {
    const q = input.value.trim().toLowerCase();
    if (!q) { loadProducts(); return; }
    track('homepage', 'search', null, q);
    try {
      const data = await StoreAPI.getProducts();
      const filtered = data.products.filter(p =>
        [p.name, p.brand, p.category, p.description].join(' ').toLowerCase().includes(q)
      );
      const grid  = document.getElementById('product-grid');
      const title = document.getElementById('section-title');
      if (title) title.textContent = `"${q}" — ${filtered.length} results`;
      renderProducts(grid, filtered);
    } catch { showToast('Search failed', 'error'); }
  };

  btn?.addEventListener('click', doSearch);
  input.addEventListener('keydown', e => { if (e.key === 'Enter') doSearch(); });
}

/* ════════════════════════════════════════════════════════
   PRODUCT DETAIL
   ════════════════════════════════════════════════════════ */
async function initProduct() {
  const id = parseInt(new URLSearchParams(location.search).get('id'));
  if (!id) { location.href = 'index.html'; return; }

  track('product', 'pageview', id);
  updateBadge();

  try {
    const p = await StoreAPI.getProduct(id);
    renderDetail(p);
    loadRelated(p);
  } catch { showToast('Product not found', 'error'); }
}

function renderDetail(p) {
  document.title = `${p.name} — Exposys Mart`;
  const disc = Math.round((1 - p.price / p.original_price) * 100);

  document.getElementById('detail-img').src = p.image;
  document.getElementById('detail-img').alt = p.name;
  document.getElementById('detail-brand').textContent = p.brand;
  document.getElementById('detail-name').textContent  = p.name;
  document.getElementById('detail-price').textContent = `₹${p.price.toLocaleString()}`;
  document.getElementById('detail-orig').textContent  = `₹${p.original_price.toLocaleString()}`;
  document.getElementById('detail-save').textContent  = `Save ${disc}%`;
  document.getElementById('detail-desc').textContent  = p.description;
  document.getElementById('bc-cat').textContent  = p.category.charAt(0).toUpperCase() + p.category.slice(1);
  document.getElementById('bc-name').textContent = p.name;

  const ratingEl = document.getElementById('detail-rating');
  if (ratingEl) ratingEl.innerHTML = `
    <div class="star-row">${renderStars(p.rating)}</div>
    <strong>${p.rating}</strong>
    <span class="p-review-count">${p.reviews.toLocaleString()} ratings</span>
  `;

  const specsEl = document.getElementById('detail-specs');
  if (specsEl && p.specs) {
    specsEl.innerHTML = Object.entries(p.specs).map(([k,v]) => `
      <div class="spec-row"><span class="spec-key">${k}</span><span class="spec-val">${v}</span></div>
    `).join('');
  }

  // Quantity
  let qty = 1;
  const qtyVal = document.getElementById('qty-val');
  document.getElementById('qty-minus')?.addEventListener('click', () => { qty = Math.max(1, qty-1); qtyVal.textContent = qty; });
  document.getElementById('qty-plus')?.addEventListener('click', () => { qty = Math.min(10, qty+1); qtyVal.textContent = qty; });

  document.getElementById('add-cart-btn')?.addEventListener('click', () => {
    if (!StoreAPI.isLoggedIn()) {
      showToast('Please login to add items to cart', 'info');
      setTimeout(() => { window.location.href = 'auth.html'; }, 1200);
      return;
    }
    Cart.add(p, qty);
    showToast(`<strong>${p.name}</strong> × ${qty} added`, 'success');
    track('product', 'add_to_cart', p.id);
  });
  document.getElementById('buy-now-btn')?.addEventListener('click', () => {
    if (!StoreAPI.isLoggedIn()) {
      showToast('Please login to buy items', 'info');
      setTimeout(() => { window.location.href = 'auth.html'; }, 1200);
      return;
    }
    Cart.add(p, qty);
    track('product', 'add_to_cart', p.id);
    location.href = 'checkout.html';
  });
}

async function loadRelated(product) {
  const grid = document.getElementById('related-grid');
  if (!grid) return;
  try {
    const d = await StoreAPI.getProducts(product.category);
    const rel = (d.products || []).filter(x => x.id !== product.id).slice(0, 4);
    renderProducts(grid, rel);
  } catch {}
}

/* ════════════════════════════════════════════════════════
   CART
   ════════════════════════════════════════════════════════ */
function initCart() {
  track('cart', 'pageview');
  updateBadge();
  renderCartPage();
}

function renderCartPage() {
  const items = Cart.get();
  const list  = document.getElementById('cart-list');
  const empty = document.getElementById('cart-empty');
  const sumCard = document.getElementById('summary-card');
  if (!list) return;

  const count = Cart.getCount();
  const countLbl = document.getElementById('cart-count-label');
  if (countLbl) countLbl.textContent = `${count} item${count !== 1 ? 's' : ''}`;

  if (!items.length) {
    list.innerHTML = '';
    if (empty)   empty.style.display = 'block';
    if (sumCard) sumCard.style.opacity = '0.4';
    return;
  }
  if (empty)   empty.style.display   = 'none';
  if (sumCard) sumCard.style.opacity  = '1';

  list.innerHTML = items.map(item => `
    <div class="cart-item" data-id="${item.id}">
      <div class="cart-item-img">
        <img src="${item.image}" alt="${item.name}" onerror="this.style.display='none'">
      </div>
      <div>
        <div class="cart-item-name">${item.name}</div>
        <div class="cart-item-brand">${item.brand}</div>
        <div class="cart-item-price">₹${(item.price * item.qty).toLocaleString()}</div>
        <div style="margin-top:8px;">
          <div class="qty-ctrl" style="display:inline-flex;">
            <button class="qty-btn ci-minus" data-id="${item.id}">−</button>
            <span class="qty-val">${item.qty}</span>
            <button class="qty-btn ci-plus"  data-id="${item.id}">+</button>
          </div>
        </div>
      </div>
      <button class="remove-btn" data-id="${item.id}">
        <svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a1 1 0 011-1h4a1 1 0 011 1v2"/></svg>
        Remove
      </button>
    </div>
  `).join('');

  list.querySelectorAll('.ci-minus').forEach(b => b.addEventListener('click', () => {
    const it = items.find(x => x.id === parseInt(b.dataset.id));
    if (it && it.qty > 1) { Cart.updateQty(it.id, it.qty - 1); renderCartPage(); }
  }));
  list.querySelectorAll('.ci-plus').forEach(b => b.addEventListener('click', () => {
    const it = items.find(x => x.id === parseInt(b.dataset.id));
    if (it) { Cart.updateQty(it.id, it.qty + 1); renderCartPage(); }
  }));
  list.querySelectorAll('.remove-btn').forEach(b => b.addEventListener('click', () => {
    Cart.remove(parseInt(b.dataset.id));
    showToast('Item removed', 'info');
    renderCartPage();
  }));

  const sub = Cart.getSubtotal();
  const tax = sub * 0.08;
  const tot = sub + tax;
  setText('sum-subtotal', `₹${sub.toLocaleString()}`);
  setText('sum-tax', `₹${tax.toLocaleString()}`);
  setText('sum-total', `₹${tot.toLocaleString()}`);
}

/* ════════════════════════════════════════════════════════
   CHECKOUT
   ════════════════════════════════════════════════════════ */
function initCheckout() {
  // Login required for checkout
  if (!StoreAPI.isLoggedIn()) {
    showToast('Please login to checkout', 'info');
    setTimeout(() => { window.location.href = 'auth.html'; }, 1200);
    return;
  }
  track('checkout', 'pageview');
  renderCheckoutItems();

  document.getElementById('place-order-btn')?.addEventListener('click', async () => {
    const btn = document.getElementById('place-order-btn');
    btn.disabled = true;
    btn.textContent = 'Processing...';
    await track('checkout', 'checkout');
    
      try {
        const items = Cart.get();
        const payload = {
          total_amount: Cart.getSubtotal() * 1.08,
          items: items.map(i => ({ product_id: i.id, quantity: i.qty, price: i.price }))
        };
        
        const data = await StoreAPI.fetch('/api/store/orders', {
          method: 'POST',
          body: JSON.stringify(payload)
        });
        
        if (!data || !data.success) throw new Error('Order failed');

        document.getElementById('checkout-form').style.display = 'none';
        document.getElementById('order-success').style.display = 'block';
        document.getElementById('order-id').textContent = data.order_id || 'SZ-' + Math.random().toString(36).slice(2, 8).toUpperCase();
        Cart.clear();
        showToast('Order placed successfully!', 'success');
      } catch (e) {
        console.error('Checkout error:', e);
        btn.disabled = false;
        btn.textContent = 'Place Order';
        showToast('Order failed, please try again', 'error');
      }
  });
}

function renderCheckoutItems() {
  const items = Cart.get();
  const ctr   = document.getElementById('co-items');
  if (!ctr) return;

  ctr.innerHTML = items.map(i => `
    <div style="display:flex;justify-content:space-between;align-items:center;padding:9px 0;border-bottom:1px solid var(--border);gap:10px;">
      <div style="display:flex;align-items:center;gap:10px;">
        <img src="${i.image}" style="width:44px;height:44px;object-fit:contain;border-radius:var(--r-sm);background:var(--bg-body);padding:4px;" onerror="this.style.display='none'">
        <div>
          <div style="font-size:.83rem;font-weight:600;line-height:1.3;">${i.name}</div>
          <div style="font-size:.72rem;color:var(--text-muted);">Qty: ${i.qty}</div>
        </div>
      </div>
      <div style="font-weight:700;font-size:.88rem;white-space:nowrap;">₹${(i.price*i.qty).toLocaleString()}</div>
    </div>
  `).join('');

  const sub = Cart.getSubtotal(), tax = sub*0.08;
  setText('co-subtotal', `₹${sub.toLocaleString()}`);
  setText('co-tax', `₹${tax.toLocaleString()}`);
  setText('co-total', `₹${(sub+tax).toLocaleString()}`);
}

/* ── Helpers ──────────────────────────────────────────── */
function setText(id, val) { const el=document.getElementById(id); if(el) el.textContent=val; }

function updateBadge() {
  const count = Cart.getCount();
  document.querySelectorAll('#cart-badge').forEach(b => {
    b.textContent = count;
    b.style.display = count > 0 ? 'flex' : 'none';
  });
}

// Sub-Navbar Scroll Behavior
let lastScrollTop = 0;
window.addEventListener('scroll', () => {
  const catStrip = document.querySelector('.cat-strip');
  if (!catStrip) return;
  
  let scrollTop = window.pageYOffset || document.documentElement.scrollTop;
  // If scrolling down and past 100px, hide the strip. Otherwise show it.
  if (scrollTop > lastScrollTop && scrollTop > 100) {
    catStrip.classList.add('nav-hidden');
  } else {
    catStrip.classList.remove('nav-hidden');
  }
  lastScrollTop = scrollTop <= 0 ? 0 : scrollTop;
}, { passive: true });
