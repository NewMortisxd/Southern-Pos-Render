document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const barcodeInput = document.getElementById('barcode-input');
    const manualSearchBtn = document.getElementById('manual-search');
    const searchModal = document.getElementById('search-modal');
    const closeSearchModal = document.getElementById('close-search-modal');
    const modalSearchInput = document.getElementById('modal-search-input');
    const searchResults = document.getElementById('search-results');
    const noResultsRow = document.getElementById('no-results-row');
    const productInfo = document.getElementById('product-info');
    const noProductSelected = document.getElementById('no-product-selected');
    const productQuantity = document.getElementById('product-quantity');
    const decreaseQuantityBtn = document.getElementById('decrease-quantity');
    const increaseQuantityBtn = document.getElementById('increase-quantity');
    const addToCartBtn = document.getElementById('add-to-cart');
    const cartItems = document.getElementById('cart-items');
    const emptyCartRow = document.getElementById('empty-cart-row');
    const subtotalElement = document.getElementById('subtotal');
    const taxAmountElement = document.getElementById('tax-amount');
    const totalAmountElement = document.getElementById('total-amount');
    const checkoutButton = document.getElementById('checkout-button');
    const clearSaleButton = document.getElementById('clear-sale-button');
    const holdSaleButton = document.getElementById('hold-sale-button');
    // Add customer-related DOM elements
    const customerSearchBtn = document.getElementById('customer-search-btn');
    const customerModal = document.getElementById('customer-modal');
    const closeCustomerModal = document.getElementById('close-customer-modal');
    const customerSearchInput = document.getElementById('customer-search-input');
    const customerResults = document.getElementById('customer-results');
    const selectedCustomerDisplay = document.getElementById('selected-customer-display');
    const clearCustomerBtn = document.getElementById('clear-customer-btn');

    // Current state
    let currentProduct = null;
    let cart = [];
    let selectedCustomer = null;
    let TAX_RATE = 0.12; // Default tax rate, will be updated from business config

    // Initialize
    function init() {
        // Focus on barcode input
        if (barcodeInput) barcodeInput.focus();
        
        // Get business configuration (tax rate)
        getBusinessConfig();
        
        // Hide product sidebar on initial load
        hideProductSidebar();
        
        // Load cart from localStorage if available
        loadCartFromLocalStorage();
        
        // Load selected customer from localStorage if available
        loadCustomerFromLocalStorage();
        
        // Set up event listeners
        setupEventListeners();
    }

    // Save cart to localStorage
    function saveCartToLocalStorage() {
        // Save cart items with full product details
        const cartWithDetails = cart.map(item => {
            // Include any additional product details we have
            const fullItem = {...item};
            
            // If this item matches the current product, add those details
            if (currentProduct && currentProduct.id === item.id) {
                fullItem.categoria = currentProduct.categoria;
                fullItem.stock = currentProduct.stock;
                fullItem.imagen = currentProduct.imagen;
            }
            
            return fullItem;
        });
        
        localStorage.setItem('southernPosCart', JSON.stringify(cartWithDetails));
    }

    // Load cart from localStorage
    function loadCartFromLocalStorage() {
        const savedCart = localStorage.getItem('southernPosCart');
        if (savedCart) {
            try {
                cart = JSON.parse(savedCart);
                
                // Rebuild cart UI
                if (cart.length > 0) {
                    // Hide empty cart message
                    if (emptyCartRow) {
                        emptyCartRow.classList.add('hidden');
                    }
                    
                    // Add each item to the cart UI
                    cart.forEach(item => {
                        addCartItemRow(item);
                    });
                    
                    // Update totals
                    updateCartTotals();
                }
            } catch (error) {
                console.error('Error loading cart from localStorage:', error);
                // Reset cart if there was an error
                cart = [];
            }
        }
    }

   // Clear cart from localStorage
   function clearCartFromLocalStorage() {
    localStorage.removeItem('southernPosCart');
}

    // Get business configuration
    function getBusinessConfig() {
        fetch('/configuraciones/api/business-config/')
            .then(response => {
                if (!response.ok) {
                    // If API doesn't exist, we'll keep the default tax rate
                    return null;
                }
                return response.json();
            })
            .then(data => {
                if (data && data.iva_porcentaje) {
                    // Convert percentage to decimal (e.g., 12% -> 0.12)
                    TAX_RATE = parseFloat(data.iva_porcentaje) / 100;
                    // Update any displayed tax rates
                    const taxRateElements = document.querySelectorAll('.tax-rate-display');
                    taxRateElements.forEach(el => {
                        el.textContent = `${TAX_RATE * 100}%`;
                    });
                }
            })
            .catch(error => {
                console.error('Error fetching business config:', error);
                // Keep using the default tax rate
            });
    }

    // Función para obtener el token CSRF
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Función para redirigir a la página de pago
    function redirectToPayment() {
        // Guardar el carrito actual en localStorage antes de redirigir
        saveCartToLocalStorage();
        
        // Redirigir a la página de pago
        window.location.href = '/ventas/payment/';
    }


    // Función para calcular el subtotal
    function calculateSubtotal() {
        return cart.reduce((total, item) => total + item.subtotal, 0);
    }

    // Set up event listeners
    function setupEventListeners() {
        // Barcode input
        if (barcodeInput) {
            barcodeInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    searchProductByBarcodeAndAddToCart(this.value);
                }
            });
        }

        // Manual search button
        if (manualSearchBtn) {
            manualSearchBtn.addEventListener('click', function() {
                openSearchModal();
            });
        }

        // Close search modal
        if (closeSearchModal) {
            closeSearchModal.addEventListener('click', function() {
                closeModal(searchModal);
            });
        }
        // Customer search button
        if (customerSearchBtn) {
            customerSearchBtn.addEventListener('click', function() {
                openCustomerModal();
            });
        }
        const closeProductInfoBtn = document.getElementById('close-product-info');
        if (closeProductInfoBtn) {
            closeProductInfoBtn.addEventListener('click', function() {
                hideProductSidebar();
            });
        }
        // Close customer modal
        if (closeCustomerModal) {
            closeCustomerModal.addEventListener('click', function() {
                closeModal(customerModal);
            });
        }
        if (customerSearchInput) {
            customerSearchInput.addEventListener('keyup', function(e) {
                if (e.key === 'Enter') {
                    searchCustomers(this.value);
                } else if (this.value.length >= 3) {
                    searchCustomers(this.value);
                }
            });
        }
        if (clearCustomerBtn) {
            clearCustomerBtn.addEventListener('click', function() {
                clearSelectedCustomer();
            });
        }
        // Modal search input
        if (modalSearchInput) {
            modalSearchInput.addEventListener('keyup', function(e) {
                if (e.key === 'Enter') {
                    searchProducts(this.value);
                } else if (this.value.length >= 3) {
                    searchProducts(this.value);
                }
            });
        }

        // Quantity controls
        if (decreaseQuantityBtn) {
            decreaseQuantityBtn.addEventListener('click', function() {
                decreaseQuantity();
            });
        }

        if (increaseQuantityBtn) {
            increaseQuantityBtn.addEventListener('click', function() {
                increaseQuantity();
            });
        }

        // Add to cart button
        if (addToCartBtn) {
            addToCartBtn.addEventListener('click', function() {
                addToCart();
            });
        }

        // Clear sale button
        if (clearSaleButton) {
            clearSaleButton.addEventListener('click', function() {
                clearCart();
            });
        }

        // Checkout button
// Checkout button
        if (checkoutButton) {
            checkoutButton.addEventListener('click', function() {
                if (cart.length > 0) {
                    redirectToPayment();
                } else {
                    showNotification('El carrito está vacío. Agregue productos antes de proceder al pago.', 'error');
                }
            });
        }
        
    }
    function openCustomerModal() {
        if (customerModal) {
            customerModal.classList.remove('hidden');
            setTimeout(() => {
                if (customerSearchInput) customerSearchInput.focus();
            }, 100);
        }
    }
    // Search customers
    function searchCustomers(query) {
        if (!query || query.length < 3) {
            if (customerResults) {
                customerResults.innerHTML = '<tr><td colspan="4" class="px-6 py-4 text-center text-gray-500">Ingrese al menos 3 caracteres para buscar</td></tr>';
            }
            return;
        }
        
        // Show loading state
        if (customerResults) {
            customerResults.innerHTML = '<tr><td colspan="4" class="px-6 py-4 text-center">Buscando clientes...</td></tr>';
        }
        
        // Make API request to search clients using the correct endpoint
        fetch(`/clients/?q=${query}`)
            .then(response => response.text())
            .then(html => {
                console.log("Received HTML response for client search");
                
                // Create a temporary element to parse the HTML response
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = html;
                
                // Try to find clients in the table format
                const clientTable = tempDiv.querySelector('table.min-w-full');
                if (clientTable) {
                    const clientRows = clientTable.querySelectorAll('tbody tr:not(.empty-row)');
                    
                    if (clientRows && clientRows.length > 0) {
                        // Convert HTML clients to JSON format
                        const clientes = Array.from(clientRows).map(row => {
                            const columns = row.querySelectorAll('td');
                            if (columns.length >= 3) {
                                // Extract client ID from the edit link
                                const editLink = row.querySelector('a[href*="/clients/editar/"]');
                                const id = editLink ? editLink.getAttribute('href').split('/').filter(Boolean).pop() : '';
                                
                                return {
                                    id: id,
                                    identificacion: columns[0].textContent.trim(),
                                    nombre: columns[1].textContent.trim(),
                                    email: columns[2].textContent.trim() || 'N/A'
                                };
                            }
                            return null;
                        }).filter(cliente => cliente !== null);
                        
                        if (clientes.length > 0) {
                            displayCustomerResults(clientes);
                            return;
                        }
                    }
                }
                
                // If we couldn't find clients in the table, try other formats
                const clientCards = tempDiv.querySelectorAll('.card, .client-card, .customer-card');
                if (clientCards && clientCards.length > 0) {
                    const clientes = Array.from(clientCards).map(card => {
                        // Try to find client details in various formats
                        const nombre = card.querySelector('.client-name, .customer-name, h3, .font-medium')?.textContent.trim() || '';
                        const identificacion = card.querySelector('.client-id, .customer-id, .text-sm:nth-child(2)')?.textContent.trim() || '';
                        
                        // Try to extract ID from edit link
                        const editLink = card.querySelector('a[href*="/clients/editar/"]');
                        const id = editLink ? editLink.getAttribute('href').split('/').filter(Boolean).pop() : '';
                        
                        return {
                            id,
                            identificacion,
                            nombre,
                            email: 'N/A'
                        };
                    }).filter(cliente => cliente.nombre); // Only include clients with a name
                    
                    if (clientes.length > 0) {
                        displayCustomerResults(clientes);
                        return;
                    }
                }
                
                // If we still couldn't find clients, check for a "no results" message
                const noResultsMsg = tempDiv.querySelector('.empty-results, .no-results') || 
                                    tempDiv.textContent.includes('No se encontraron clientes');
                
                if (noResultsMsg) {
                    if (customerResults) {
                        customerResults.innerHTML = '<tr><td colspan="4" class="px-6 py-4 text-center text-gray-500">No se encontraron clientes con ese término</td></tr>';
                    }
                } else {
                    // If we can't determine the structure, log the HTML for debugging
                    console.log("Could not parse client HTML structure:", html.substring(0, 500) + "...");
                    
                    if (customerResults) {
                        customerResults.innerHTML = `
                            <tr>
                                <td colspan="4" class="px-6 py-4 text-center text-gray-500">
                                    No se pudieron procesar los resultados. 
                                    <button id="add-new-client" class="ml-2 text-blue-600 hover:text-blue-800">
                                        Agregar nuevo cliente
                                    </button>
                                </td>
                            </tr>
                        `;
                        
                        // Add event listener for the "Add new client" button
                        const addNewClientBtn = customerResults.querySelector('#add-new-client');
                        if (addNewClientBtn) {
                            addNewClientBtn.addEventListener('click', function() {
                                window.open('/clients/agregar/', '_blank');
                            });
                        }
                    }
                }
            })
            .catch(error => {
                console.error('Error searching customers:', error);
                if (customerResults) {
                    customerResults.innerHTML = '<tr><td colspan="4" class="px-6 py-4 text-center text-red-500">Error al buscar clientes</td></tr>';
                }
            });
    }

    // Display customer search results
    function displayCustomerResults(clientes) {
        if (!customerResults) return;
        
        customerResults.innerHTML = '';
        
        clientes.forEach(cliente => {
            const row = document.createElement('tr');
            row.className = 'hover:bg-gray-50 cursor-pointer transition-colors';
            row.innerHTML = `
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${cliente.identificacion || 'N/A'}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${cliente.nombre}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${cliente.direccion || 'N/A'}</td>
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button class="select-customer text-blue-600 hover:text-blue-900 focus:outline-none">
                        Seleccionar
                    </button>
                </td>
            `;
            
            row.addEventListener('click', function() {
                selectCustomer(cliente);
                closeModal(customerModal);
            });
            
            customerResults.appendChild(row);
        });
        
        // Re-initialize Lucide icons
        lucide.createIcons();
    }

    // Select customer
    function selectCustomer(cliente) {
        selectedCustomer = cliente;
        
        // Update UI to show selected customer
        if (selectedCustomerDisplay) {
            selectedCustomerDisplay.textContent = cliente.nombre;
            selectedCustomerDisplay.classList.remove('text-gray-500');
            selectedCustomerDisplay.classList.add('text-emerald-600', 'font-medium');
        }
        
        if (clearCustomerBtn) {
            clearCustomerBtn.classList.remove('hidden');
        }
        
        // Save selected customer to localStorage
        saveCustomerToLocalStorage();
        
        // Show notification
        showNotification(`Cliente seleccionado: ${cliente.nombre}`, 'success');
    }

    // Clear selected customer
    function clearSelectedCustomer() {
        selectedCustomer = null;
        
        // Update UI to show default "Consumidor final"
        if (selectedCustomerDisplay) {
            selectedCustomerDisplay.textContent = 'Consumidor final';
            selectedCustomerDisplay.classList.remove('text-emerald-600', 'font-medium');
            selectedCustomerDisplay.classList.add('text-gray-500');
        }
        
        if (clearCustomerBtn) {
            clearCustomerBtn.classList.add('hidden');
        }
        
        // Remove customer from localStorage
        localStorage.removeItem('southernPosCustomer');
        
        // Show notification
        showNotification('Cliente removido', 'info');
    }

    // Save customer to localStorage
    function saveCustomerToLocalStorage() {
        if (selectedCustomer) {
            localStorage.setItem('southernPosCustomer', JSON.stringify(selectedCustomer));
        }
    }

    // Load customer from localStorage
    function loadCustomerFromLocalStorage() {
        const savedCustomer = localStorage.getItem('southernPosCustomer');
        if (savedCustomer) {
            try {
                selectedCustomer = JSON.parse(savedCustomer);
                
                // Update UI to show selected customer
                if (selectedCustomerDisplay) {
                    selectedCustomerDisplay.textContent = selectedCustomer.nombre;
                    selectedCustomerDisplay.classList.remove('text-gray-500');
                    selectedCustomerDisplay.classList.add('text-emerald-600', 'font-medium');
                }
                
                if (clearCustomerBtn) {
                    clearCustomerBtn.classList.remove('hidden');
                }
            } catch (error) {
                console.error('Error loading customer from localStorage:', error);
                selectedCustomer = null;
            }
        }
    }

    // Search product by barcode
    function searchProductByBarcode(barcode) {
        if (!barcode) return;
        
        // Show loading state
        barcodeInput.classList.add('bg-blue-50');
        
        // Make API request
        fetch(`/api/productos/buscar-codigo/?codigo=${barcode}`)
            .then(response => response.json())
            .then(data => {
                if (data.success && data.producto) {
                    displayProductInfo(data.producto);
                } else {
                    showNotification('Producto no encontrado', 'error');
                }
            })
            .catch(error => {
                console.error('Error searching product:', error);
                showNotification('Error al buscar el producto', 'error');
            })
            .finally(() => {
                barcodeInput.classList.remove('bg-blue-50');
                barcodeInput.value = '';
                barcodeInput.focus();
            });
    }

// Search product by barcode and add to cart
function searchProductByBarcodeAndAddToCart(searchTerm) {
    if (!searchTerm) return;
    
    // Show loading state
    barcodeInput.classList.add('bg-blue-50');
    
    // 1. First try the exact barcode API if it looks like a barcode
    if (isLikelyBarcode(searchTerm)) {
        fetch(`/productos/api/buscar-por-codigo/?codigo=${encodeURIComponent(searchTerm)}`)
            .then(response => {
                if (!response.ok) throw new Error('API not found');
                return response.json();
            })
            .then(data => {
                if (data.success && data.producto) {
                    // Product found by exact barcode
                    addProductToCart(data.producto, 1);
                    return;
                }
                throw new Error('Product not found by barcode');
            })
            .catch(() => {
                // If barcode search fails, proceed to general search
                return performGeneralSearch(searchTerm);
            })
            .catch(error => {
                console.error('Search error:', error);
                showNotification('Error al buscar el producto', 'error');
            })
            .finally(() => {
                resetSearchInput();
            });
    } else {
        // If it doesn't look like a barcode, go straight to general search
        performGeneralSearch(searchTerm)
            .catch(error => {
                console.error('Search error:', error);
                showNotification('Error al buscar el producto', 'error');
            })
            .finally(() => {
                resetSearchInput();
            });
    }
}

// Helper function to determine if a search term looks like a barcode
function isLikelyBarcode(term) {
    // Check if it's all numbers and at least 4 digits
    return /^\d{4,}$/.test(term);
}

// Perform general search by name or partial barcode
function performGeneralSearch(searchTerm) {
    return fetch(`/productos/buscar/?q=${encodeURIComponent(searchTerm)}`)
        .then(response => response.text())
        .then(html => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const productCards = doc.querySelectorAll('.producto-card');
            
            let productsFound = [];
            
            productCards.forEach(card => {
                const product = {
                    id: card.dataset.id,
                    codigo: card.dataset.codigo,
                    nombre: card.dataset.nombre,
                    precio: parseFloat(card.dataset.precio),
                    stock: parseInt(card.dataset.stock) || 0,
                    categoria: card.dataset.categoria || 'General',
                    imagen: card.querySelector('img')?.src || null
                };
                productsFound.push(product);
            });
            
            if (productsFound.length === 0) {
                showNotification('No se encontraron productos', 'error');
                return;
            }
            
            // If only one product found, add it directly
            if (productsFound.length === 1) {
                addProductToCart(productsFound[0], 1);
                return;
            }
            
            // If multiple products found, show selection modal
            showProductSelectionModal(productsFound, searchTerm);
        });
}

// Show a modal to select the correct product when multiple matches are found
function showProductSelectionModal(products, searchTerm) {
    // Create modal element
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
    modal.innerHTML = `
        <div class="bg-white rounded-lg p-6 max-w-md w-full max-h-[80vh] overflow-y-auto">
            <h3 class="text-lg font-medium mb-4">Seleccione producto</h3>
            <p class="text-sm text-gray-600 mb-4">Resultados para: "${searchTerm}"</p>
            <div class="space-y-2" id="product-selection-list"></div>
            <button class="mt-4 px-4 py-2 bg-gray-200 rounded-md hover:bg-gray-300" id="cancel-selection">
                Cancelar
            </button>
        </div>
    `;
    
    // Add products to selection list
    const productList = modal.querySelector('#product-selection-list');
    products.forEach(product => {
        const productItem = document.createElement('div');
        productItem.className = 'p-3 border rounded-md hover:bg-gray-50 cursor-pointer';
        productItem.innerHTML = `
            <div class="flex justify-between">
                <div>
                    <h4 class="font-medium">${product.nombre}</h4>
                    <p class="text-sm text-gray-600">Código: ${product.codigo || 'N/A'}</p>
                </div>
                <div class="text-right">
                    <p class="font-medium">$${product.precio.toFixed(2)}</p>
                    <p class="text-sm">Stock: ${product.stock}</p>
                </div>
            </div>
        `;
        
        productItem.addEventListener('click', () => {
            addProductToCart(product, 1);
            document.body.removeChild(modal);
        });
        
        productList.appendChild(productItem);
    });
    
    // Add cancel button handler
    modal.querySelector('#cancel-selection').addEventListener('click', () => {
        document.body.removeChild(modal);
    });
    
    // Add modal to DOM
    document.body.appendChild(modal);
}

// Reset search input after operation
function resetSearchInput() {
    barcodeInput.classList.remove('bg-blue-50');
    barcodeInput.value = '';
    barcodeInput.focus();
}

    // Open search modal
    function openSearchModal() {
        searchModal.classList.remove('hidden');
        setTimeout(() => {
            modalSearchInput.focus();
        }, 100);
    }

    // Close modal
    function closeModal(modal) {
        modal.classList.add('hidden');
        barcodeInput.focus();
    }

    // Search products
    function searchProducts(query) {
        if (!query || query.length < 3) {
            noResultsRow.textContent = 'Ingrese al menos 3 caracteres para buscar';
            return;
        }
        
        // Show loading state
        searchResults.innerHTML = '<tr><td colspan="6" class="px-6 py-4 text-center">Buscando productos...</td></tr>';
        
        // Make request to the existing search endpoint instead of the API
        fetch(`/productos/buscar/?q=${query}`)
            .then(response => response.text())
            .then(html => {
                // Create a temporary element to parse the HTML response
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = html;
                
                // Extract product data from the HTML
                const productCards = tempDiv.querySelectorAll('.group.relative.bg-white');
                
                if (productCards && productCards.length > 0) {
                    // Convert HTML products to JSON format
                    const productos = Array.from(productCards).map(card => {
                        const nombre = card.querySelector('h3').textContent.trim();
                        const precio = card.querySelector('.text-xl.font-bold').textContent.replace('$', '').trim();
                        const categoria = card.querySelector('.px-3.py-1.bg-emerald-100').textContent.trim();
                        
                        // Improved stock extraction
                        let stock = 0;
                        const stockElements = card.querySelectorAll('.text-sm');
                        for (const el of stockElements) {
                            const text = el.textContent.trim();
                            if (text.includes('Stock:')) {
                                const matches = text.match(/\d+/);
                                if (matches && matches.length > 0) {
                                    stock = parseInt(matches[0]);
                                    break;
                                }
                            }
                        }
                        
                        // Try to get the product ID from the edit link
                        const editLink = card.querySelector('a[href*="productos/editar"]');
                        const id = editLink ? editLink.getAttribute('href').split('/').filter(Boolean).pop() : '';
                        
                        // Try to get the product code (assuming it might be in the description or elsewhere)
                        const codigo = id || 'N/A';
                        
                        // Check if there's an image
                        const imgElement = card.querySelector('img');
                        const imagen = imgElement ? imgElement.getAttribute('src') : null;
                        
                        return {
                            id,
                            codigo,
                            nombre,
                            precio,
                            stock,
                            categoria,
                            imagen
                        };
                    });
                    
                    displaySearchResults(productos);
                } else {
                    searchResults.innerHTML = '<tr><td colspan="6" class="px-6 py-4 text-center text-gray-500">No se encontraron productos con ese término</td></tr>';
                }
            })
            .catch(error => {
                console.error('Error searching products:', error);
                searchResults.innerHTML = '<tr><td colspan="6" class="px-6 py-4 text-center text-red-500">Error al buscar productos</td></tr>';
            });
    }


// ... existing code ...

// Search product by barcode and add to cart
function searchProductByBarcodeAndAddToCart(searchTerm) {
    if (!searchTerm) return;
    
    // Show loading state
    barcodeInput.classList.add('bg-blue-50');
    
    // 1. First try the exact barcode API if it looks like a barcode
    if (isLikelyBarcode(searchTerm)) {
        fetch(`/productos/api/buscar-por-codigo/?codigo=${encodeURIComponent(searchTerm)}`)
            .then(response => {
                if (!response.ok) throw new Error('API not found');
                return response.json();
            })
            .then(data => {
                if (data.success && data.producto) {
                    // Product found by exact barcode
                    addProductToCart(data.producto, 1);
                    return;
                }
                throw new Error('Product not found by barcode');
            })
            .catch(() => {
                // If barcode search fails, proceed to general search
                return performGeneralSearch(searchTerm);
            })
            .catch(error => {
                console.error('Search error:', error);
                showNotification('Error al buscar el producto', 'error');
            })
            .finally(() => {
                resetSearchInput();
            });
    } else {
        // If it doesn't look like a barcode, go straight to general search
        performGeneralSearch(searchTerm)
            .catch(error => {
                console.error('Search error:', error);
                showNotification('Error al buscar el producto', 'error');
            })
            .finally(() => {
                resetSearchInput();
            });
    }
}

// Helper function to determine if a search term looks like a barcode
function isLikelyBarcode(term) {
    // Check if it's all numbers and at least 4 digits
    return /^\d{4,}$/.test(term);
}

// Perform general search by name or partial barcode
function performGeneralSearch(searchTerm) {
    return fetch(`/productos/buscar/?q=${encodeURIComponent(searchTerm)}`)
        .then(response => response.text())
        .then(html => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const productCards = doc.querySelectorAll('.producto-card');
            
            let productsFound = [];
            
            productCards.forEach(card => {
                const product = {
                    id: card.dataset.id,
                    codigo: card.dataset.codigo,
                    nombre: card.dataset.nombre,
                    precio: parseFloat(card.dataset.precio),
                    stock: parseInt(card.dataset.stock) || 0,
                    categoria: card.dataset.categoria || 'General',
                    imagen: card.querySelector('img')?.src || null
                };
                productsFound.push(product);
            });
            
            if (productsFound.length === 0) {
                showNotification('No se encontraron productos', 'error');
                return;
            }
            
            // If only one product found, add it directly
            if (productsFound.length === 1) {
                addProductToCart(productsFound[0], 1);
                return;
            }
            
            // If multiple products found, show selection modal
            showProductSelectionModal(productsFound, searchTerm);
        });
}

// Show a modal to select the correct product when multiple matches are found
function showProductSelectionModal(products, searchTerm) {
    // Create modal element
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
    modal.innerHTML = `
        <div class="bg-white rounded-lg p-6 max-w-md w-full max-h-[80vh] overflow-y-auto">
            <h3 class="text-lg font-medium mb-4">Seleccione producto</h3>
            <p class="text-sm text-gray-600 mb-4">Resultados para: "${searchTerm}"</p>
            <div class="space-y-2" id="product-selection-list"></div>
            <button class="mt-4 px-4 py-2 bg-gray-200 rounded-md hover:bg-gray-300" id="cancel-selection">
                Cancelar
            </button>
        </div>
    `;
    
    // Add products to selection list
    const productList = modal.querySelector('#product-selection-list');
    products.forEach(product => {
        const productItem = document.createElement('div');
        productItem.className = 'p-3 border rounded-md hover:bg-gray-50 cursor-pointer';
        productItem.innerHTML = `
            <div class="flex justify-between">
                <div>
                    <h4 class="font-medium">${product.nombre}</h4>
                    <p class="text-sm text-gray-600">Código: ${product.codigo || 'N/A'}</p>
                </div>
                <div class="text-right">
                    <p class="font-medium">$${product.precio.toFixed(2)}</p>
                    <p class="text-sm">Stock: ${product.stock}</p>
                </div>
            </div>
        `;
        
        productItem.addEventListener('click', () => {
            addProductToCart(product, 1);
            document.body.removeChild(modal);
        });
        
        productList.appendChild(productItem);
    });
    
    // Add cancel button handler
    modal.querySelector('#cancel-selection').addEventListener('click', () => {
        document.body.removeChild(modal);
    });
    
    // Add modal to DOM
    document.body.appendChild(modal);
}

// Reset search input after operation
function resetSearchInput() {
    barcodeInput.classList.remove('bg-blue-50');
    barcodeInput.value = '';
    barcodeInput.focus();
}



    // Add product to cart directly
    function addProductToCart(producto, quantity) {
        if (!producto) return;
        
        if (quantity <= 0) {
            showNotification('La cantidad debe ser mayor a 0', 'error');
            return;
        }
        
        // Check if product has stock
        if (producto.stock <= 0) {
            showNotification('No hay stock disponible para este producto', 'error');
            return;
        }
        
        if (quantity > producto.stock) {
            showNotification('No hay suficiente stock disponible', 'error');
            return;
        }
        
        // Check if product is already in cart
        const existingItemIndex = cart.findIndex(item => item.id === producto.id);
        
        if (existingItemIndex !== -1) {
            // Update quantity if product already exists
            const newQuantity = cart[existingItemIndex].quantity + quantity;
            
            if (newQuantity > producto.stock) {
                showNotification('No hay suficiente stock disponible', 'error');
                return;
            }
            
            cart[existingItemIndex].quantity = newQuantity;
            cart[existingItemIndex].subtotal = cart[existingItemIndex].precio * newQuantity;
            
            // Asegurarse de que se guarden todos los detalles del producto
            if (producto.categoria) cart[existingItemIndex].categoria = producto.categoria;
            if (producto.imagen) cart[existingItemIndex].imagen = producto.imagen;
            if (producto.stock) cart[existingItemIndex].stock = producto.stock;
            
            updateCartItemRow(cart[existingItemIndex]);
        } else {
            // Add new product to cart
            const cartItem = {
                id: producto.id,
                codigo_barras: producto.codigo_barras,  // Asegúrate de usar el nombre correcto del campo
                nombre: producto.nombre,
                precio: parseFloat(producto.precio),
                quantity: quantity,
                subtotal: parseFloat(producto.precio) * quantity,
                categoria: producto.categoria || 'Sin categoría',
                imagen: producto.imagen || null
            };
            
            cart.push(cartItem);
            addCartItemRow(cartItem);
        }
        
        // Update totals
        updateCartTotals();
        
        // Save cart to localStorage
        saveCartToLocalStorage();
        

        
        // Reset product info
        productInfo.classList.add('hidden');
        noProductSelected.classList.add('hidden');
        currentProduct = null;
        
        // Hide the product sidebar
        hideProductSidebar();
        
        // Focus on barcode input
        barcodeInput.focus();
    }

    // Decrease cart item quantity
    function decreaseCartItemQuantity(itemId) {
        const itemIndex = cart.findIndex(item => item.id === itemId);
        if (itemIndex === -1) return;
        
        if (cart[itemIndex].quantity > 1) {
            cart[itemIndex].quantity--;
            cart[itemIndex].subtotal = cart[itemIndex].precio * cart[itemIndex].quantity;
            updateCartItemRow(cart[itemIndex]);
            updateCartTotals();
            saveCartToLocalStorage();
        } else {
            removeCartItem(itemId);
        }
    }

    // Increase cart item quantity
    function increaseCartItemQuantity(itemId) {
        const itemIndex = cart.findIndex(item => item.id === itemId);
        if (itemIndex === -1) return;
        
        // Get current stock for this product by fetching the latest data
        fetch(`/productos/buscar/?q=${cart[itemIndex].codigo}`)
            .then(response => response.text())
            .then(html => {
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = html;
                
                // Try to find the product card
                const productCards = tempDiv.querySelectorAll('.group.relative.bg-white');
                let currentStock = 0;
                
                if (productCards && productCards.length > 0) {
                    // Find the matching product
                    for (const card of productCards) {
                        const nombre = card.querySelector('h3').textContent.trim();
                        if (nombre === cart[itemIndex].nombre) {
                            const stockText = card.querySelector('.text-sm.font-medium').textContent.trim();
                            currentStock = parseInt(stockText.replace('Stock:', '').trim());
                            break;
                        }
                    }
                    
                    // If no exact match found, use the first card
                    if (currentStock === 0 && productCards.length > 0) {
                        const card = productCards[0];
                        const stockText = card.querySelector('.text-sm.font-medium').textContent.trim();
                        currentStock = parseInt(stockText.replace('Stock:', '').trim());
                    }
                }
                
                // If we couldn't determine stock, use a fallback
                if (currentStock === 0) {
                    currentStock = currentProduct && currentProduct.id === itemId ? 
                        currentProduct.stock : 99;
                }
                
                // Check if we can increase quantity
                if (cart[itemIndex].quantity < currentStock) {
                    cart[itemIndex].quantity++;
                    cart[itemIndex].subtotal = cart[itemIndex].precio * cart[itemIndex].quantity;
                    updateCartItemRow(cart[itemIndex]);
                    updateCartTotals();
                    saveCartToLocalStorage();
                } else {
                    showNotification('No hay suficiente stock disponible', 'warning');
                }
            })
            .catch(error => {
                console.error('Error fetching product stock:', error);
                // Fallback to a simple check if fetch fails
                if (cart[itemIndex].quantity < 99) {
                    cart[itemIndex].quantity++;
                    cart[itemIndex].subtotal = cart[itemIndex].precio * cart[itemIndex].quantity;
                    updateCartItemRow(cart[itemIndex]);
                    updateCartTotals();
                } else {
                    showNotification('No hay suficiente stock disponible', 'warning');
                }
            });
    }

    // Display search results
// En la función displaySearchResults o donde muestras los resultados de búsqueda
function displaySearchResults(productos) {
    searchResults.innerHTML = '';
    
    if (productos.length === 0) {
        noResultsRow.innerHTML = '<td colspan="6" class="px-6 py-4 text-center text-gray-500">No se encontraron productos</td>';
        searchResults.appendChild(noResultsRow);
        return;
    }
    
    productos.forEach(producto => {
        const row = document.createElement('tr');
        row.className = 'hover:bg-gray-50 cursor-pointer';
        row.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                ${producto.codigo_barras || 'N/A'}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${producto.nombre}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${producto.categoria || 'Sin categoría'}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">$${parseFloat(producto.precio).toFixed(2)}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${producto.stock}</td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button class="text-blue-600 hover:text-blue-900 focus:outline-none" data-id="${producto.id}">
                    <i data-lucide="plus-circle" class="w-5 h-5"></i>
                </button>
            </td>
        `;
        
        row.addEventListener('click', function() {
            const productData = {
                id: producto.id,
                nombre: producto.nombre,
                precio: producto.precio,
                stock: producto.stock,
                categoria: producto.categoria,
                codigo: producto.codigo || null,
                codigo_barras: producto.codigo_barras || null,
                imagen: producto.imagen || null
            };
            displayProductInfo(productData);
            closeModal(searchModal);
        });
        
        searchResults.appendChild(row);
    });
    
    lucide.createIcons();
}

    // Hide product sidebar
    function hideProductSidebar() {
        const productSidebar = document.getElementById('product-sidebar');
        const mainSection = document.querySelector('.flex-1.flex.flex-col');
        
        if (productSidebar && mainSection) {
            productSidebar.classList.add('hidden');
            mainSection.classList.remove('flex-1');
            mainSection.classList.add('w-full');
        }
        
        productInfo.classList.add('hidden');
        noProductSelected.classList.remove('hidden');
        
        // Focus on barcode input
        barcodeInput.focus();
    }

    // Show product sidebar
    function showProductSidebar() {
        const productSidebar = document.getElementById('product-sidebar');
        const mainSection = document.querySelector('.flex-1.flex.flex-col, .w-full.flex.flex-col');
        
        if (productSidebar && mainSection) {
            productSidebar.classList.remove('hidden');
            mainSection.classList.remove('w-full');
            mainSection.classList.add('flex-1');
        }
        
        // If we have a current product, redisplay its info
        if (currentProduct) {
            // Update product info section
            document.getElementById('product-name').textContent = currentProduct.nombre;
            document.getElementById('product-category').textContent = currentProduct.categoria;
            document.getElementById('product-code').textContent = `Código: ${currentProduct.codigo}`;
            document.getElementById('product-price').textContent = `$${parseFloat(currentProduct.precio).toFixed(2)}`;
            document.getElementById('product-stock').textContent = `${currentProduct.stock} unidades`;
            document.getElementById('product-tax').textContent = `${TAX_RATE * 100}%`;
            document.getElementById('product-tax').classList.add('tax-rate-display');
            
            // Handle product image
            const productImage = document.getElementById('product-image');
            const productNoImage = document.getElementById('product-no-image');
            
            if (currentProduct.imagen) {
                productImage.src = currentProduct.imagen;
                productImage.classList.remove('hidden');
                productNoImage.classList.add('hidden');
            } else {
                productImage.classList.add('hidden');
                productNoImage.classList.remove('hidden');
            }
            
            // Show product info section
            productInfo.classList.remove('hidden');
            noProductSelected.classList.add('hidden');
        }
    }

    // Display product info - modify this function
    function displayProductInfo(producto) {
        // Show the sidebar if it's hidden
        showProductSidebar();
        
        currentProduct = producto;
        
        // Update product info section
        const productNameElement = document.getElementById('product-name');
        const productPriceElement = document.getElementById('product-price');
        const productCategoryElement = document.getElementById('product-category');
        const productStockElement = document.getElementById('product-stock');
        const productTaxElement = document.getElementById('product-tax');
        const productCodeElement = document.getElementById('product-code');
        const productImage = document.getElementById('product-image');
        const productNoImage = document.getElementById('product-no-image');
        const productBarcodeContainer = document.getElementById('product-barcode-container');
        
        if (productNameElement) productNameElement.textContent = producto.nombre;
        if (productCategoryElement) productCategoryElement.textContent = producto.categoria || 'Sin categoría';
        if (productCodeElement) {
            // Verificar todas las posibles propiedades donde podría estar el código de barras
            const barcode = producto.codigo_barras || producto.codigo || producto.barcode || '';
            productCodeElement.textContent = `Código: ${barcode || 'N/A'}`;
        }
        if (productPriceElement) productPriceElement.textContent = `$${parseFloat(producto.precio || producto.precio_venta || 0).toFixed(2)}`;
        if (productStockElement) productStockElement.textContent = `${producto.stock !== undefined ? producto.stock : 'N/A'} unidades`;
        if (productTaxElement) {
            productTaxElement.textContent = `${TAX_RATE * 100}%`;
            productTaxElement.classList.add('tax-rate-display');
        }
        
        // Reset quantity
        if (productQuantity) productQuantity.value = 1;
        
        // Handle product image
        if (productImage && productNoImage) {
            if (producto.imagen) {
                productImage.src = producto.imagen;
                productImage.classList.remove('hidden');
                productNoImage.classList.add('hidden');
            } else {
                productImage.classList.add('hidden');
                productNoImage.classList.remove('hidden');
            }
        }
        
        // Mostrar código de barras si está disponible
        if (productBarcodeContainer) {
            if (producto.codigo_barras) {
                productBarcodeContainer.innerHTML = `
                    <div class="mt-4">
                        <h3 class="text-sm font-medium text-gray-700 mb-2">Código de barras: ${producto.codigo_barras}</h3>
                        <svg id="product-barcode" class="w-full"></svg>
                    </div>
                `;
                
                // Si estás usando JsBarcode, puedes generar el código de barras así:
                // JsBarcode("#product-barcode", producto.codigo_barras);
                
                productBarcodeContainer.classList.remove('hidden');
            } else {
                productBarcodeContainer.classList.add('hidden');
            }
        } else if (producto.codigo_barras) {
            // Si el contenedor no existe, crearlo y añadirlo al sidebar
            const newBarcodeContainer = document.createElement('div');
            newBarcodeContainer.id = 'product-barcode-container';
            
            newBarcodeContainer.innerHTML = `
                <div class="mt-4">
                    <h3 class="text-sm font-medium text-gray-700 mb-2">Código de barras: ${producto.codigo_barras}</h3>
                    <svg id="product-barcode" class="w-full"></svg>
                </div>
            `;
            
            // Si estás usando JsBarcode, puedes generar el código de barras así:
            // JsBarcode("#product-barcode", producto.codigo_barras);
            
            // Añadir el contenedor al sidebar
            if (productInfo) {
                productInfo.appendChild(newBarcodeContainer);
            }
        }
        
        // Enable add to cart button
        if (addToCartBtn) {
            addToCartBtn.disabled = false;
            addToCartBtn.classList.remove('opacity-50', 'cursor-not-allowed');
            addToCartBtn.classList.add('hover:bg-blue-700');
        }
        
        // Show product info section
        if (productInfo) productInfo.classList.remove('hidden');
        if (noProductSelected) noProductSelected.classList.add('hidden');
    }

    // Decrease quantity
    function decreaseQuantity() {
        let qty = parseInt(productQuantity.value);
        if (qty > 1) {
            productQuantity.value = qty - 1;
        }
    }

    // Increase quantity
    function increaseQuantity() {
        let qty = parseInt(productQuantity.value);
        if (currentProduct && currentProduct.stock > 0 && qty < currentProduct.stock) {
            productQuantity.value = qty + 1;
        } else {
            showNotification('No hay suficiente stock disponible', 'warning');
        }
    }

    // Add to cart
    // Add to cart
    // Add to cart
    function addToCart() {
        if (!currentProduct) return;
        
        const quantity = parseInt(productQuantity.value);
        
        if (quantity <= 0) {
            showNotification('La cantidad debe ser mayor a 0', 'error');
            return;
        }
        
        // Check if product has stock
        if (currentProduct.stock <= 0) {
            showNotification('No hay stock disponible para este producto', 'error');
            return;
        }
        
        if (quantity > currentProduct.stock) {
            showNotification('No hay suficiente stock disponible', 'error');
            return;
        }
        
        // Check if product is already in cart
        const existingItemIndex = cart.findIndex(item => item.id === currentProduct.id);
        
        if (existingItemIndex !== -1) {
            // Update quantity if product already exists
            const newQuantity = cart[existingItemIndex].quantity + quantity;
            
            if (newQuantity > currentProduct.stock) {
                showNotification('No hay suficiente stock disponible', 'error');
                return;
            }
            
            cart[existingItemIndex].quantity = newQuantity;
            cart[existingItemIndex].subtotal = cart[existingItemIndex].precio * newQuantity;
            
            // Asegurarse de que se guarden todos los detalles del producto
            cart[existingItemIndex].categoria = currentProduct.categoria;
            cart[existingItemIndex].stock = currentProduct.stock;
            cart[existingItemIndex].imagen = currentProduct.imagen;
            
            updateCartItemRow(cart[existingItemIndex]);
        } else {
            // Add new product to cart
            const cartItem = {
                id: currentProduct.id,
                codigo: currentProduct.codigo,
                nombre: currentProduct.nombre,
                precio: parseFloat(currentProduct.precio),
                quantity: quantity,
                subtotal: parseFloat(currentProduct.precio) * quantity,
                // Guardar todos los detalles adicionales del producto
                categoria: currentProduct.categoria,
                stock: currentProduct.stock,
                imagen: currentProduct.imagen
            };
            
            cart.push(cartItem);
            addCartItemRow(cartItem);
        }
        
        // Update totals
        updateCartTotals();
        
        // Save cart to localStorage
        saveCartToLocalStorage();
        
        
        // Reset product info
        productInfo.classList.add('hidden');
        noProductSelected.classList.add('hidden');
        currentProduct = null;
        
        // Hide the product sidebar
        hideProductSidebar();
        
        // Focus on barcode input
        barcodeInput.focus();
    }

    // Add cart item row
    function addCartItemRow(item) {
        if (emptyCartRow) {
            emptyCartRow.classList.add('hidden');
        }
        
        const row = document.createElement('tr');
        row.id = `cart-item-${item.id}`;
        row.className = 'hover:bg-gray-50 cursor-pointer';
        row.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                ${item.codigo_barras || 'N/A'}  <!-- Cambiado de item.codigo a item.codigo_barras -->
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${item.nombre}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">$${item.precio.toFixed(2)}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <div class="flex items-center">
                    <button class="decrease-cart-item p-1 text-gray-500 hover:text-gray-700" data-id="${item.id}">
                        <i data-lucide="minus-circle" class="w-4 h-4"></i>
                    </button>
                    <span class="mx-2">${item.quantity}</span>
                    <button class="increase-cart-item p-1 text-gray-500 hover:text-gray-700" data-id="${item.id}">
                        <i data-lucide="plus-circle" class="w-4 h-4"></i>
                    </button>
                </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">$${item.subtotal.toFixed(2)}</td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button class="remove-cart-item text-red-600 hover:text-red-900" data-id="${item.id}">
                    <i data-lucide="trash-2" class="w-4 h-4"></i>
                </button>
            </td>
        `;
        
        cartItems.appendChild(row);
        
        // Add event listeners for cart item controls
        const decreaseBtn = row.querySelector('.decrease-cart-item');
        const increaseBtn = row.querySelector('.increase-cart-item');
        const removeBtn = row.querySelector('.remove-cart-item');
        
        decreaseBtn.addEventListener('click', function() {
            decreaseCartItemQuantity(item.id);
        });
        
        increaseBtn.addEventListener('click', function() {
            increaseCartItemQuantity(item.id);
        });
        
        removeBtn.addEventListener('click', function() {
            removeCartItem(item.id);
        });
        
        // Add click event to the row to show product info
        row.addEventListener('click', function(e) {
            // Only trigger if the click wasn't on a button
            if (!e.target.closest('button')) {
                showCartItemInfo(item.id);
            }
        });
        
        // Re-initialize Lucide icons
        lucide.createIcons();
    }


    function showCartItemInfo(itemId) {
        const item = cart.find(item => item.id === itemId);
        if (!item) return;
        
        // Show the sidebar if it's hidden
        showProductSidebar();
        
        // Since we already have the item in the cart, let's display it immediately
        // while we fetch additional details
        const initialProducto = {
            id: item.id,
            codigo: item.codigo,
            nombre: item.nombre,
            precio: item.precio,
            stock: item.stock || 99, // Use saved stock if available, otherwise temporary high value
            categoria: item.categoria || 'Cargando...', // Use saved category if available
            imagen: item.imagen || null // Use saved image if available
        };
        
        // Set as current product first so sidebar shows properly
        currentProduct = initialProducto;
        
        // Display initial info
        document.getElementById('product-name').textContent = initialProducto.nombre;
        document.getElementById('product-category').textContent = initialProducto.categoria;
        document.getElementById('product-code').textContent = `Código: ${initialProducto.codigo}`;
        document.getElementById('product-price').textContent = `$${parseFloat(initialProducto.precio).toFixed(2)}`;
        document.getElementById('product-stock').textContent = `${initialProducto.stock} unidades`;
        document.getElementById('product-tax').textContent = `${TAX_RATE * 100}%`;
        document.getElementById('product-tax').classList.add('tax-rate-display');
        
        // Handle product image immediately if we have it
        const productImage = document.getElementById('product-image');
        const productNoImage = document.getElementById('product-no-image');
        
        if (initialProducto.imagen) {
            productImage.src = initialProducto.imagen;
            productImage.classList.remove('hidden');
            productNoImage.classList.add('hidden');
        } else {
            productImage.classList.add('hidden');
            productNoImage.classList.remove('hidden');
        }
        
        // Update quantity to match cart
        if (productQuantity) {
            productQuantity.value = item.quantity;
        }
        
        // Show product info section
        productInfo.classList.remove('hidden');
        noProductSelected.classList.add('hidden');
        
        // Now fetch additional details to ensure we have the latest info
        fetch(`/productos/buscar/?q=${item.codigo}`)
            .then(response => response.text())
            .then(html => {
                // Create a temporary element to parse the HTML response
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = html;
                
                // Try to find the product card
                const productCards = tempDiv.querySelectorAll('.group.relative.bg-white');
                
                if (productCards && productCards.length > 0) {
                    // Try to find the matching product
                    let card = null;
                    for (const c of productCards) {
                        // Try different ways to match the product
                        const titleEl = c.querySelector('h3');
                        if (titleEl && titleEl.textContent.trim() === item.nombre) {
                            card = c;
                            break;
                        }
                    }
                    
                    // If no match found, use the first card
                    if (!card && productCards.length > 0) {
                        card = productCards[0];
                    }
                    
                    if (card) {
                        // Try to extract stock information - look for various patterns
                        let stock = 10; // Default reasonable stock value
                        
                        // Try different selectors for stock
                        const stockElements = card.querySelectorAll('.text-sm.font-medium');
                        for (const el of stockElements) {
                            const text = el.textContent.trim();
                            if (text.includes('Stock:')) {
                                const matches = text.match(/\d+/);
                                if (matches && matches.length > 0) {
                                    stock = parseInt(matches[0]);
                                    break;
                                }
                            }
                        }
                        
                        // Try to get category - use the exact selector from searchProductByBarcodeAndAddToCart
                        let categoria = 'Producto';
                        const categoryEl = card.querySelector('.px-3.py-1.bg-emerald-100');
                        if (categoryEl) {
                            categoria = categoryEl.textContent.trim();
                        }
                        
                        // Try to get image
                        let imagen = null;
                        const imgEl = card.querySelector('img');
                        if (imgEl && imgEl.getAttribute('src')) {
                            imagen = imgEl.getAttribute('src');
                        }
                        
                        // Update product info with the new details
                        const updatedProducto = {
                            id: item.id,
                            codigo: item.codigo,
                            nombre: item.nombre,
                            precio: item.precio,
                            stock: stock,
                            categoria: categoria,
                            imagen: imagen
                        };
                        
                        // Update current product
                        currentProduct = updatedProducto;
                        
                        // Update display
                        document.getElementById('product-name').textContent = updatedProducto.nombre;
                        document.getElementById('product-category').textContent = updatedProducto.categoria;
                        document.getElementById('product-code').textContent = `Código: ${updatedProducto.codigo}`;
                        document.getElementById('product-price').textContent = `$${parseFloat(updatedProducto.precio).toFixed(2)}`;
                        document.getElementById('product-stock').textContent = `${updatedProducto.stock} unidades`;
                        
                        // Handle product image
                        if (updatedProducto.imagen) {
                            productImage.src = updatedProducto.imagen;
                            productImage.classList.remove('hidden');
                            productNoImage.classList.add('hidden');
                        } else {
                            productImage.classList.add('hidden');
                            productNoImage.classList.remove('hidden');
                        }
                        
                        // Make sure quantity is still set correctly
                        if (productQuantity) {
                            productQuantity.value = item.quantity;
                        }
                        
                        // Update the item in the cart with these details
                        const cartItemIndex = cart.findIndex(cartItem => cartItem.id === item.id);
                        if (cartItemIndex !== -1) {
                            cart[cartItemIndex].categoria = categoria;
                            cart[cartItemIndex].stock = stock;
                            cart[cartItemIndex].imagen = imagen;
                            
                            // Save updated cart to localStorage
                            saveCartToLocalStorage();
                        }
                    }
                }
            })
            .catch(error => {
                console.error('Error fetching product details:', error);
                // We already displayed initial info, so no need to do anything here
            });
    }
        

    // Update cart item row
    function updateCartItemRow(item) {
        const row = document.getElementById(`cart-item-${item.id}`);
        if (!row) return;
        
        const quantityCell = row.querySelector('td:nth-child(4) span');
        const subtotalCell = row.querySelector('td:nth-child(5)');
        
        quantityCell.textContent = item.quantity;
        subtotalCell.textContent = `$${item.subtotal.toFixed(2)}`;
    }

    // Decrease cart item quantity
    function decreaseCartItemQuantity(itemId) {
        const itemIndex = cart.findIndex(item => item.id === itemId);
        if (itemIndex === -1) return;
        
        if (cart[itemIndex].quantity > 1) {
            cart[itemIndex].quantity--;
            cart[itemIndex].subtotal = cart[itemIndex].precio * cart[itemIndex].quantity;
            updateCartItemRow(cart[itemIndex]);
            updateCartTotals();
        } else {
            removeCartItem(itemId);
        }
    }

    // Increase cart item quantity
    function increaseCartItemQuantity(itemId) {
        const itemIndex = cart.findIndex(item => item.id === itemId);
        if (itemIndex === -1) return;
        
        // Get current stock for this product
        let currentStock = 99; // Default high value
        
        // If we have the current product loaded and it matches this item
        if (currentProduct && currentProduct.id === itemId) {
            currentStock = currentProduct.stock;
        }
        
        // Check if we can increase quantity
        if (cart[itemIndex].quantity < currentStock) {
            cart[itemIndex].quantity++;
            cart[itemIndex].subtotal = cart[itemIndex].precio * cart[itemIndex].quantity;
            updateCartItemRow(cart[itemIndex]);
            updateCartTotals();
        } else {
            showNotification('No hay suficiente stock disponible', 'warning');
        }
    }

    // Remove cart item
    function removeCartItem(itemId) {
        const itemIndex = cart.findIndex(item => item.id === itemId);
        if (itemIndex === -1) return;
        
        // Remove from cart array
        cart.splice(itemIndex, 1);
        
        // Save cart to localStorage
        saveCartToLocalStorage();
        
        // Remove row from DOM
        const row = document.getElementById(`cart-item-${itemId}`);
        if (row) {
            row.classList.add('bg-red-50');
            setTimeout(() => {
                row.remove();
                
                // Show empty cart message if cart is empty
                if (cart.length === 0 && emptyCartRow) {
                    emptyCartRow.classList.remove('hidden');
                }
            }, 300);
        }
        
        // Update totals
        updateCartTotals();
    }

    // Update cart totals
    function updateCartTotals() {
        // Calculate the total including tax first
        const totalWithTax = cart.reduce((total, item) => total + item.subtotal, 0);
        
        // Calculate the subtotal (total without tax)
        const subtotal = totalWithTax / (1 + TAX_RATE);
        
        // Calculate tax amount
        const taxAmount = totalWithTax - subtotal;
        
        subtotalElement.textContent = `$${subtotal.toFixed(2)}`;
        taxAmountElement.textContent = `$${taxAmount.toFixed(2)}`;
        totalAmountElement.textContent = `$${totalWithTax.toFixed(2)}`;
        
        // Enable/disable checkout button
        if (cart.length > 0) {
            checkoutButton.disabled = false;
            checkoutButton.classList.remove('opacity-50', 'cursor-not-allowed');
        } else {
            checkoutButton.disabled = true;
            checkoutButton.classList.add('opacity-50', 'cursor-not-allowed');
        }
    }

    // Clear cart
    function clearCart() {
        // Clear cart array
        cart = [];
        
        // Clear cart from localStorage
        clearCartFromLocalStorage();
        
        // Clear cart UI
        cartItems.innerHTML = '';
        
        // Show empty cart message
        if (emptyCartRow) {
            emptyCartRow.classList.remove('hidden');
        }
        
        // Update totals
        updateCartTotals();
        
        // Show notification
        showNotification('Venta cancelada', 'info');
        
        // Focus on barcode input
        barcodeInput.focus();
    }

    // Show notification
    function showNotification(message, type = 'info') {
        // You can implement a notificati system here
        // For now, we'll use alert
        alert(message);
    }

    // Initialize the POS system
    init();
    


});