/* ═══════════════════════════════════════════════════════════
   Exposys Mart — Cart Management (localStorage)
   ═══════════════════════════════════════════════════════════ */

const CART_KEY = 'shopzone_cart';

const Cart = {
  get() {
    try {
      return JSON.parse(localStorage.getItem(CART_KEY)) || [];
    } catch { return []; }
  },

  save(items) {
    localStorage.setItem(CART_KEY, JSON.stringify(items));
    this.updateBadge();
  },

  add(product, qty = 1) {
    const items = this.get();
    const existing = items.find(i => i.id === product.id);
    if (existing) {
      existing.qty += qty;
    } else {
      items.push({
        id: product.id,
        name: product.name,
        brand: product.brand,
        price: product.price,
        image: product.image,
        qty: qty,
      });
    }
    this.save(items);
    return items;
  },

  remove(productId) {
    const items = this.get().filter(i => i.id !== productId);
    this.save(items);
    return items;
  },

  updateQty(productId, qty) {
    const items = this.get();
    const item = items.find(i => i.id === productId);
    if (item) {
      item.qty = Math.max(1, qty);
    }
    this.save(items);
    return items;
  },

  clear() {
    localStorage.removeItem(CART_KEY);
    this.updateBadge();
  },

  getCount() {
    return this.get().reduce((sum, i) => sum + i.qty, 0);
  },

  getSubtotal() {
    return this.get().reduce((sum, i) => sum + i.price * i.qty, 0);
  },

  updateBadge() {
    const badges = document.querySelectorAll('#cart-badge');
    const count = this.getCount();
    badges.forEach(b => { b.textContent = count; });
  },
};

// Initialize cart badge on load
document.addEventListener('DOMContentLoaded', () => Cart.updateBadge());
