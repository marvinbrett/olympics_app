document.addEventListener('DOMContentLoaded', () => {
  const badge = document.getElementById('cart-count');
  const offcanvasList = document.getElementById('offcanvasCartList');

  function createOffcanvasItem(offer) {
    const li = document.createElement('li');
    li.className = 'list-group-item d-flex justify-content-between align-items-center';
    li.dataset.offerId = offer.id;
    li.innerHTML = `
      ${offer.name} – €${offer.price}
      <button class="btn btn-sm btn-danger remove-from-cart" data-offer-id="${offer.id}">&times;</button>
    `;
    return li;
  }

  document.querySelectorAll('.add-to-cart').forEach(btn => {
    btn.addEventListener('click', async () => {
      const offerId = parseInt(btn.dataset.offerId, 10);
      try {
        const res = await fetch('/add_to_cart', {
          method: 'POST',
          credentials: 'same-origin',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ offer_id: offerId })
        });
        if (!res.ok) throw new Error('Erreur réseau');
        const data = await res.json();

        badge.textContent = data.cart_count;

        const placeholder = offcanvasList.querySelector('li.text-muted');
        if (placeholder) placeholder.remove();

        const cardBody = btn.closest('.card-body');
        const name = cardBody.querySelector('.card-title').textContent;
        const priceMatch = cardBody.querySelector('.card-text').textContent.match(/€(\d+)/);
        const price = priceMatch ? priceMatch[1] : '0';
        const newItem = createOffcanvasItem({ id: offerId, name, price });
        offcanvasList.appendChild(newItem);

      } catch (err) {
        console.error(err);
        alert('Erreur lors de l’ajout au panier.');
      }
    });
  });

  // SUPPRESSION (offcanvas & page /cart)
  document.body.addEventListener('click', async e => {
    const btn = e.target.closest('.remove-from-cart');
    if (!btn) return;

    const offerId = parseInt(btn.dataset.offerId, 10);
    try {
      const res = await fetch('/remove_from_cart', {
        method: 'POST',
        credentials: 'same-origin',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ offer_id: offerId })
      });
      if (!res.ok) throw new Error('Erreur réseau');
      const data = await res.json();

      badge.textContent = data.cart_count;

      const li = btn.closest('li');
      if (li) li.remove();

      if (data.cart_count === 0) {
        const emptyLi = document.createElement('li');
        emptyLi.className = 'list-group-item text-muted';
        emptyLi.textContent = 'Panier vide';
        offcanvasList.appendChild(emptyLi);
      }

    } catch (err) {
      console.error(err);
      alert('Erreur lors de la suppression.');
    }
  });
});