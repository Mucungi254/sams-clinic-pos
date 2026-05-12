let cart = [];

// Helper function to format currency without rounding
function formatCurrency(amount) {
    // Convert to string and preserve exact decimal places
    return parseFloat(amount.toString()).toFixed(2);
}

function handleBarcode(event) {
    let input = event.target;
    let value = input.value.trim();
    
    if (event.key === 'Enter') {
        event.preventDefault();
        if (value) {
            searchByBarcode(value);
            input.value = ''; // Clear input after scan
            hideSuggestions();
        }
    } else if (value.length >= 2) {
        // Show suggestions as user types
        showProductSuggestions(value, input);
    } else {
        hideSuggestions();
    }
}

function showProductSuggestions(query, inputElement) {
    fetch(`/api/search_product?q=${encodeURIComponent(query)}`)
    .then(res => res.json())
    .then(data => {
        let suggestionsDiv = document.getElementById('barcode-suggestions');
        if (!suggestionsDiv) {
            suggestionsDiv = document.createElement('div');
            suggestionsDiv.id = 'barcode-suggestions';
            suggestionsDiv.className = 'position-absolute w-100 bg-white border border-top-0 rounded-bottom shadow';
            suggestionsDiv.style.zIndex = '1000';
            suggestionsDiv.style.maxHeight = '200px';
            suggestionsDiv.style.overflowY = 'auto';
            
            // Position it right below the barcode input
            let inputRect = inputElement.getBoundingClientRect();
            suggestionsDiv.style.top = (inputRect.bottom + window.scrollY) + 'px';
            suggestionsDiv.style.left = (inputRect.left + window.scrollX) + 'px';
            suggestionsDiv.style.width = inputRect.width + 'px';
            
            document.body.appendChild(suggestionsDiv);
        }
        
        if (data.length > 0) {
            suggestionsDiv.innerHTML = data.map(p => `
                <div class="suggestion-item p-2 border-bottom" 
                     onclick="selectSuggestion(${p.id}, '${p.name.replace(/'/g, "\\'")}', ${p.selling_price}, ${p.stock})"
                     style="cursor: pointer; hover:background-color:#f8f9fa;">
                    <div class="fw-bold">${p.name}</div>
                    <small class="text-muted">Barcode: ${p.barcode || 'N/A'} | Stock: ${p.stock} | KES ${p.selling_price}</small>
                </div>
            `).join('');
        } else {
            suggestionsDiv.innerHTML = '<div class="p-2 text-muted">No products found</div>';
        }
    })
    .catch(error => {
        console.error('Error getting suggestions:', error);
    });
}

function selectSuggestion(id, name, price, stock) {
    addToCart(id, name, price, stock);
    hideSuggestions();
    document.getElementById('barcode-input').value = '';
}

function hideSuggestions() {
    let suggestionsDiv = document.getElementById('barcode-suggestions');
    if (suggestionsDiv) {
        suggestionsDiv.remove();
    }
}

// Hide suggestions when clicking outside
document.addEventListener('click', function(event) {
    if (!event.target.closest('#barcode-input') && !event.target.closest('#barcode-suggestions')) {
        hideSuggestions();
    }
});

function searchByBarcode(barcode) {
    fetch(`/api/search_product?q=${encodeURIComponent(barcode)}`)
    .then(res => res.json())
    .then(data => {
        if (data.length === 1) {
            // Auto-add single product to cart
            let product = data[0];
            if (product.stock > 0) {
                addToCart(product.id, product.name, product.selling_price, product.stock);
                // Flash the barcode input to show success
                let input = document.getElementById('barcode-input');
                input.style.backgroundColor = '#d4edda';
                setTimeout(() => {
                    input.style.backgroundColor = '';
                }, 300);
            } else {
                alert('Product out of stock!');
            }
        } else if (data.length === 0) {
            alert('Product not found!');
        } else {
            // Multiple products found (shouldn't happen with barcode but handle it)
            alert('Multiple products found. Please search manually.');
        }
    })
    .catch(error => {
        console.error('Error searching by barcode:', error);
        alert('Error searching for product');
    });
}

function searchProduct() {
    let q = document.getElementById('search').value;
    fetch(`/api/search_product?q=${encodeURIComponent(q)}`)
    .then(res => res.json())
    .then(data => {
        let resultsDiv = document.getElementById('product-results');
        resultsDiv.innerHTML = data.map(p => `
            <div class="d-flex justify-content-between align-items-center border-bottom py-2">
                <span>${p.name} (${p.stock} in stock) - KES ${p.selling_price}</span>
                <button class="btn btn-sm btn-primary" onclick="addToCart(${p.id}, '${p.name}', ${p.selling_price}, ${p.stock})">Add</button>
            </div>
        `).join('');
    });
}

function addToCart(id, name, price, maxQty) {
    let existing = cart.find(item => item.id === id);
    if (existing) {
        if (existing.qty < maxQty) existing.qty++;
        else alert('No more stock!');
    } else {
        cart.push({id, name, price, qty: 1, maxQty});
    }
    renderCart();
}

function renderCart() {
    let cartDiv = document.getElementById('cart-items');
    let total = 0;
    cartDiv.innerHTML = cart.map((item, index) => {
        total += item.price * item.qty;
        return `<tr>
            <td>${item.name}</td>
            <td><input type="number" min="1" max="${item.maxQty}" value="${item.qty}" onchange="updateQty(${index}, this.value)" style="width:60px"></td>
            <td>${formatCurrency(item.price*item.qty)}</td>
            <td><button class="btn btn-sm btn-danger" onclick="removeFromCart(${index})">X</button></td>
        </tr>`;
    }).join('');
    document.getElementById('cart-total').innerText = formatCurrency(total);
    updatePaymentFields();
}

function updatePaymentFields() {
    const total = parseFloat(document.getElementById('cart-total').innerText) || 0;
    
    // Update cash payment total
    document.getElementById('cash_total').value = formatCurrency(total);
    
    // Update M-Pesa amount to match total
    document.getElementById('mpesa_amount').value = formatCurrency(total);
    
    // Update mixed payment remaining balance
    updateMixedPaymentRemaining();
}

function updateMixedPaymentRemaining() {
    const total = parseFloat(document.getElementById('cart-total').innerText) || 0;
    const cashAmount = parseFloat(document.getElementById('mixed_cash').value) || 0;
    const mpesaAmount = parseFloat(document.getElementById('mixed_mpesa').value) || 0;
    const remaining = total - (cashAmount + mpesaAmount);
    
    document.getElementById('mixed_remaining').value = formatCurrency(remaining);
    
    // Update status
    const statusDiv = document.getElementById('payment-status');
    if (remaining > 0) {
        statusDiv.innerHTML = `<div class="alert alert-warning">Remaining balance: KES ${formatCurrency(remaining)}</div>`;
    } else if (remaining < 0) {
        statusDiv.innerHTML = `<div class="alert alert-info">Overpayment: KES ${formatCurrency(Math.abs(remaining))}</div>`;
    } else {
        statusDiv.innerHTML = `<div class="alert alert-success">Payment complete!</div>`;
    }
}

function calculateCashChange() {
    const total = parseFloat(document.getElementById('cash_total').value) || 0;
    const received = parseFloat(document.getElementById('cash_received').value) || 0;
    const change = received - total;
    
    document.getElementById('cash_change').value = formatCurrency(change);
    
    // Update status
    const statusDiv = document.getElementById('payment-status');
    if (received < total) {
        statusDiv.innerHTML = `<div class="alert alert-danger">Insufficient amount: KES ${formatCurrency(total - received)}</div>`;
    } else {
        statusDiv.innerHTML = `<div class="alert alert-success">Change: KES ${formatCurrency(change)}</div>`;
    }
}

function updateQty(index, newQty) {
    newQty = parseInt(newQty);
    let item = cart[index];
    if (newQty > item.maxQty) { alert('Not enough stock'); return; }
    item.qty = newQty;
    renderCart();
}

function removeFromCart(index) { cart.splice(index,1); renderCart(); }

function checkout() {
    if (cart.length === 0) { alert('Cart is empty'); return; }
    
    const total = parseFloat(document.getElementById('cart-total').innerText) || 0;
    const paymentType = document.querySelector('input[name="payment_type"]:checked').value;
    
    let paymentData = {
        items: cart.map(i => ({id:i.id, qty:i.qty})),
        payment_method: paymentType,
        total_amount: total
    };
    
    // Validate and collect payment details based on type
    if (paymentType === 'cash') {
        const cashReceived = parseFloat(document.getElementById('cash_received').value) || 0;
        if (cashReceived < total) {
            alert('Insufficient cash amount!');
            return;
        }
        paymentData.cash_amount = cashReceived;
        paymentData.amount_received = cashReceived;
        paymentData.balance_given = cashReceived - total;
        
    } else if (paymentType === 'mpesa') {
        const mpesaAmount = parseFloat(document.getElementById('mpesa_amount').value) || 0;
        const mpesaCode = document.getElementById('mpesa_code').value.trim();
        
        if (mpesaAmount < total) {
            alert('M-Pesa amount must equal total!');
            return;
        }
        if (!mpesaCode) {
            alert('M-Pesa transaction code is required!');
            return;
        }
        
        paymentData.mpesa_amount = mpesaAmount;
        paymentData.amount_received = mpesaAmount;
        paymentData.mpesa_code = mpesaCode;
        
    } else if (paymentType === 'mixed') {
        const cashAmount = parseFloat(document.getElementById('mixed_cash').value) || 0;
        const mpesaAmount = parseFloat(document.getElementById('mixed_mpesa').value) || 0;
        const mpesaCode = document.getElementById('mixed_mpesa_code').value.trim();
        const totalPaid = cashAmount + mpesaAmount;
        
        if (totalPaid < total) {
            alert('Insufficient payment amount!');
            return;
        }
        if (mpesaAmount > 0 && !mpesaCode) {
            alert('M-Pesa transaction code is required when M-Pesa payment is used!');
            return;
        }
        
        paymentData.cash_amount = cashAmount;
        paymentData.mpesa_amount = mpesaAmount;
        paymentData.amount_received = totalPaid;
        paymentData.balance_given = totalPaid - total;
        paymentData.mpesa_code = mpesaCode || null;
    }
    
    // Process the sale
    fetch('/api/checkout', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify(paymentData)
    }).then(res => res.json())
    .then(data => {
        if (data.error) { alert(data.error); }
        else { window.location.href = `/receipt/${data.receipt_id}`; }
    });
}

// Payment method change handler
function handlePaymentTypeChange() {
    const paymentType = document.querySelector('input[name="payment_type"]:checked').value;
    
    // Hide all payment sections
    document.querySelectorAll('.payment-section').forEach(section => {
        section.style.display = 'none';
    });
    
    // Show relevant payment section
    if (paymentType === 'cash') {
        document.getElementById('cash-payment').style.display = 'block';
    } else if (paymentType === 'mpesa') {
        document.getElementById('mpesa-payment').style.display = 'block';
    } else if (paymentType === 'mixed') {
        document.getElementById('mixed-payment').style.display = 'block';
    }
    
    updatePaymentFields();
}

// Add event listeners when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Payment type change listeners
    document.querySelectorAll('input[name="payment_type"]').forEach(radio => {
        radio.addEventListener('change', handlePaymentTypeChange);
    });
    
    // Cash payment listeners
    document.getElementById('cash_received').addEventListener('input', calculateCashChange);
    
    // Mixed payment listeners
    document.getElementById('mixed_cash').addEventListener('input', updateMixedPaymentRemaining);
    document.getElementById('mixed_mpesa').addEventListener('input', updateMixedPaymentRemaining);
    
    // Initialize
    handlePaymentTypeChange();
});