    // Asegurarse de que el DOM esté completamente cargado
$(document).ready(function() {
        console.log("jQuery DOM cargado completamente");
        
        // Count products with low stock but not zero
let lowStockCount = 0;
// Seleccionar todas las filas de la tabla de productos con stock bajo
$('#tabla-bajo-stock tbody tr').each(function() {
    // Como estamos en la tabla de stock bajo, todas las filas ya son de productos con stock bajo
    // Solo necesitamos asegurarnos de que el stock no sea cero verificando que no contenga "Agotado"
    const stockText = $(this).find('td:nth-child(3)').text().trim();
    if (!stockText.includes('Agotado')) {
        lowStockCount += 1;
    }
});

// Si la tabla aún no se ha renderizado (porque el tab no está activo), hacer el conteo desde los datos ocultos
if (lowStockCount === 0) {
    // Buscar en todo el documento por elementos que indiquen stock bajo pero no cero
    $('.bg-amber-50, .bg-amber-900\\\/20').each(function() {
        const stockText = $(this).find('span:contains("unidades")').text().trim();
        if (stockText && !$(this).hasClass('bg-red-50') && !$(this).hasClass('bg-red-900/20')) {
            lowStockCount += 1;
        }
    });
}

// Actualizar ambos contadores
$('.stock-bajo-counter').text(lowStockCount);
$('#stock-bajo-count').text(lowStockCount);
        
        // Store initialized tables to prevent multiple initializations
        const initializedTables = {};
        
        // Function to safely initialize a DataTable
        function safeInitDataTable(tableId, options) {
            // Check if table exists
            const table = $('#' + tableId);
            if (table.length === 0) {
                console.log('Table #' + tableId + ' not found');
                return;
            }
            
            // Check if already initialized
            if (initializedTables[tableId]) {
                console.log('Table #' + tableId + ' already initialized');
                return;
            }
            
            // Check if DataTable is already initialized on this element
            if ($.fn.dataTable.isDataTable('#' + tableId)) {
                console.log('Table #' + tableId + ' already has DataTable instance');
                initializedTables[tableId] = true;
                return;
            }
            
            // Initialize DataTable
            try {
                table.DataTable(options);
                initializedTables[tableId] = true;
                console.log('Table #' + tableId + ' initialized successfully');
            } catch (e) {
                console.error('Error initializing table #' + tableId + ':', e);
            }
        }
        
        // Default DataTable options
        // Update the defaultOptions to remove buttons from DataTables
        const defaultOptions = {
            responsive: true,
            pageLength: 10,
            lengthMenu: [[10, 25, 50, -1], [10, 25, 50, "Todos"]],
            language: {
                url: '//cdn.datatables.net/plug-ins/1.11.5/i18n/es-ES.json'
            },
            dom: 'lfrtip', // Remove 'B' (buttons) from dom
            initComplete: function() {
                // Aplicar estilos adicionales después de la inicialización
                $('.dataTables_length select').addClass('border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300 rounded-md shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50');
                
                // Mejorar la apariencia de la barra de búsqueda
                $('.dataTables_filter input').addClass('border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300 rounded-md shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50 ml-2 py-2 px-4 w-64');
                
                // Agregar icono de búsqueda y mejorar el contenedor
                $('.dataTables_filter').addClass('relative');
                $('.dataTables_filter input').before('<i data-lucide="search" class="absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400"></i>');
                $('.dataTables_filter input').addClass('pl-3 pr-10');
                
                // Mejorar estilos de paginación
                $('.dataTables_paginate').addClass('flex items-center justify-center mt-4');
                $('.dataTables_paginate .paginate_button').addClass('inline-flex items-center justify-center w-10 h-10 mx-1 border border-gray-300 dark:border-gray-700 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-200');
                $('.dataTables_paginate .paginate_button.current').addClass('bg-blue-600 text-white border-blue-600 dark:bg-blue-700 dark:border-blue-700 hover:bg-blue-700 dark:hover:bg-blue-800 font-medium');
                $('.dataTables_paginate .paginate_button.disabled').addClass('text-gray-400 dark:text-gray-600 border-gray-200 dark:border-gray-800 hover:bg-transparent dark:hover:bg-transparent cursor-not-allowed opacity-50');
                
                // Estilizar los botones de navegación (anterior, siguiente, etc.)
                $('.dataTables_paginate .previous').addClass('mr-2');
                $('.dataTables_paginate .next').addClass('ml-2');
                
                // Inicializar los iconos de Lucide después de que DataTables haya terminado
                if (typeof lucide !== 'undefined') {
                    lucide.createIcons();
                }
            }
        };
        
        // Add click handlers for your custom buttons
        $('#btn-imprimir').on('click', function() {
            const table = $('.dataTable').DataTable();
            table.button('.buttons-print').trigger();
        });
        
        $('#btn-excel').on('click', function() {
            const table = $('.dataTable').DataTable();
            table.button('.buttons-excel').trigger();
        });
        
        $('#btn-pdf').on('click', function() {
            const table = $('.dataTable').DataTable();
            table.button('.buttons-pdf').trigger();
        });
        
        // Initialize DataTables with buttons but don't show them
        const tableButtonsOptions = $.extend(true, {}, defaultOptions, {
            buttons: [
                {
                    extend: 'excel',
                    className: 'hidden'
                },
                {
                    extend: 'pdf',
                    className: 'hidden',
                    customize: function (doc) {
                        // Add title and date first
                        doc.content.splice(0, 0, {
                            text: 'Reporte de Inventario',
                            fontSize: 16,
                            bold: true,
                            margin: [0, 0, 0, 8],
                            alignment: 'center'
                        }, {
                            text: 'Generado el: ' + new Date().toLocaleDateString(),
                            fontSize: 10,
                            margin: [0, 0, 0, 20],
                            alignment: 'center'
                        });
                        
                        // Try to add company logo if available
                        try {
                            // Create an image element to check if logo exists
                            const img = new Image();
                            img.src = '{% static "img/logo.png" %}';
                            
                            img.onload = function() {
                                // If logo loads successfully, add it to the PDF
                                doc.content.splice(0, 0, {
                                    image: img.src,
                                    width: 150,
                                    alignment: 'center',
                                    margin: [0, 0, 0, 12]
                                });
                            };
                            
                            img.onerror = function() {
                                console.log('Company logo not found');
                            };
                        } catch (e) {
                            console.log('Error loading company logo:', e);
                        }
                        
                        // Style the table
                        if (doc.content[3]) {
                            doc.content[3].layout = {
                                hLineWidth: function(i, node) {
                                    return (i === 0 || i === node.table.body.length) ? 2 : 1;
                                },
                                vLineWidth: function(i, node) {
                                    return (i === 0 || i === node.table.widths.length) ? 2 : 1;
                                },
                                hLineColor: function(i, node) {
                                    return (i === 0 || i === node.table.body.length) ? 'black' : 'gray';
                                },
                                vLineColor: function(i, node) {
                                    return (i === 0 || i === node.table.widths.length) ? 'black' : 'gray';
                                }
                            };
                        }
                    }
                },
                {
                    extend: 'print',
                    className: 'hidden'
                }
            ]
        });
        
        // Initialize tables with the hidden buttons
        safeInitDataTable('tabla-productos', tableButtonsOptions);
        
        // Initialize tables when tabs are clicked
        $('button[data-tab="bajo"]').on('click', function() {
            setTimeout(function() {
                safeInitDataTable('tabla-bajo-stock', defaultOptions);
            }, 100);
        });
        
        $('button[type="button"]').on('click', function() {
            const tab = $(this).attr('@click').replace("activeTab = '", "").replace("'", "");
            
            if (tab === 'todos') {
                setTimeout(function() {
                    safeInitDataTable('tabla-productos', defaultOptions);
                }, 100);
            } else if (tab === 'agotados') {
                setTimeout(function() {
                    safeInitDataTable('tabla-agotados', defaultOptions);
                }, 100);
            } else if (tab === 'categorias') {
                setTimeout(function() {
                    safeInitDataTable('tabla-categorias', defaultOptions);
                }, 100);
            }
        });
        
        // Initialize the first table (productos) on page load
        safeInitDataTable('tabla-productos', defaultOptions);
        
        // Remove duplicate table IDs to prevent initialization errors
        $('[x-show="activeTab === \'bajo\'"] table').attr('id', 'tabla-bajo-stock');
        $('[x-show="activeTab === \'agotados\'"] table').attr('id', 'tabla-agotados');
        $('[x-show="activeTab === \'categorias\'"] table').attr('id', 'tabla-categorias');
        // Modificar el CSS y la estructura de los controles de DataTables

    // Función para aplicar estilos mejorados a los controles de DataTables
    function applyDataTableStyles() {
                // Crear un contenedor flex para los controles superiores si no existe
                if ($('.dataTables_wrapper .dt-controls-top').length === 0) {
            $('.dataTables_wrapper .dataTables_length, .dataTables_wrapper .dataTables_filter').wrapAll('<div class="dt-controls-top flex justify-between items-center mb-4 w-full"></div>');
        }
        $('.dataTables_filter').addClass('ml-auto');
        // Estilizar el selector "Mostrar X registros"
        $('.dataTables_length').addClass('mb-4 flex items-center text-gray-600 dark:text-gray-300');
        $('.dataTables_length label').addClass('flex items-center gap-2 font-medium');
        $('.dataTables_length select').addClass('border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200 rounded-md shadow-sm px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200');
        
        // Estilizar el campo de búsqueda
        $('.dataTables_filter').addClass('mb-4 relative');
        $('.dataTables_filter label').addClass('flex items-center font-medium text-gray-600 dark:text-gray-300');
        $('.dataTables_filter input')
    .addClass('border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200 rounded-md shadow-sm pr-4 py-2 w-64 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200')
    .attr('placeholder', 'Buscar...');
        

        
        // Estilizar info de registros (Mostrando X a Y de Z registros)
        $('.dataTables_info').addClass('text-sm text-gray-500 dark:text-gray-400 my-4');
        
        // Estilizar controles de paginación
        $('.dataTables_paginate').addClass('flex items-center justify-end my-4 select-none');
        
        // Aplicar estilos a los botones de paginación
        $('.paginate_button').addClass('relative inline-flex items-center justify-center min-w-[40px] h-10 mx-1 px-3 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200 rounded-md transition-colors duration-200 hover:bg-gray-100 dark:hover:bg-gray-700 font-medium text-sm');
        $('.paginate_button.current').addClass('!bg-blue-600 !text-white !border-blue-600 dark:!bg-blue-700 dark:!border-blue-700 hover:!bg-blue-700 dark:hover:!bg-blue-800');
        $('.paginate_button.disabled').addClass('!text-gray-400 dark:!text-gray-600 !border-gray-200 dark:!border-gray-800 hover:!bg-transparent dark:hover:!bg-transparent cursor-not-allowed opacity-50');
        
        // Mejorar los botones anterior/siguiente con íconos
        if ($('.paginate_button.previous svg').length === 0) {
            $('.paginate_button.previous').html('<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"></polyline></svg>');
            $('.paginate_button.previous').addClass('flex items-center justify-center');
        }
        
        if ($('.paginate_button.next svg').length === 0) {
            $('.paginate_button.next').html('<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>');
            $('.paginate_button.next').addClass('flex items-center justify-center');
        }
    }
    
    // Aplicar estilos cuando se inicializa una tabla
    // Actualizar las opciones de DataTable por defecto
    $.extend(true, $.fn.dataTable.defaults, {
        responsive: true,
        language: {
            search: "",
            lengthMenu: "<span class='mr-1'>Mostrar</span> _MENU_ <span class='ml-1'>registros</span>",
            info: "Mostrando _START_ a _END_ de _TOTAL_ registros",
            infoEmpty: "Mostrando 0 a 0 de 0 registros",
            paginate: {
                first: '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="11 17 6 12 11 7"></polyline><polyline points="18 17 13 12 18 7"></polyline></svg>',
                last: '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="13 17 18 12 13 7"></polyline><polyline points="6 17 11 12 6 7"></polyline></svg>',
                previous: '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"></polyline></svg>',
                next: '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>'
            }
        },
        drawCallback: function() {
            applyDataTableStyles();
        },
        initComplete: function() {
            applyDataTableStyles();
        }
    });
    
    // Actualizar la función safeInitDataTable para incluir los nuevos estilos
    window.safeInitDataTable = function(tableId, additionalOptions = {}) {
        const table = $('#' + tableId);
        if (table.length === 0) {
            console.log('Table #' + tableId + ' not found');
            return;
        }
        
        if ($.fn.dataTable.isDataTable('#' + tableId)) {
            console.log('Table #' + tableId + ' already has DataTable instance');
            applyDataTableStyles(); // Aplicar estilos incluso si ya está inicializada
            return;
        }
        
        try {
            const options = $.extend(true, {}, additionalOptions);
            table.DataTable(options);
            console.log('Table #' + tableId + ' initialized successfully');
        } catch (e) {
            console.error('Error initializing table #' + tableId + ':', e);
        }
    };
    
    // Aplicar estilos después de cualquier acción en la tabla (como cambiar de página)
    $(document).on('draw.dt', function() {
        applyDataTableStyles();
    });
    
    // Inicializar tablas existentes con los nuevos estilos
    if (typeof initializedTables !== 'undefined') {
        const tableIds = ['tabla-productos', 'tabla-bajo-stock', 'tabla-agotados', 'tabla-categorias'];
        tableIds.forEach(function(tableId) {
            const table = $('#' + tableId);
            if (table.length && $.fn.dataTable.isDataTable('#' + tableId)) {
                applyDataTableStyles();
            }
        });
    }
});
