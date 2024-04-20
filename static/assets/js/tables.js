$(document).ready(function() {
    var session_page = $('#session-page').data('page');
    var commonOptions = {
        "language": {
            "search": "Căutare:",
            // "lengthMenu": "Afișare _MENU_ înregistrări pe pagină",
            "lengthMenu": "Afișare _MENU_ înregistrări",
            "zeroRecords": "Nu s-au găsit înregistrări",
            // "info": "Afișate de la _START_ până la _END_ din _TOTAL_ înregistrări",
            "info": "<b>TOTAL</b> - _TOTAL_ înregistrări",
            // "infoEmpty": "Afișate de la 0 până la 0 din 0 înregistrări",
            "infoEmpty": "0 înregistrări",
            "infoFiltered": "(filtrate dintr-un total de _MAX_ înregistrări)",
            "paginate": {
                "first": "Prima",
                "last": "Ultima",
                "next": "Următoarea",
                "previous": "Anterioara"
            }
        },
        searching: false,
        pagingType: "numbers",
        paging: true,
        info: true
    }
    if (session_page === 'raports' || session_page === 'edit-car') {
        var table1Options = Object.assign({}, commonOptions, {
            "columnDefs": [{
                "type": "num",
                "targets": 3,
                "render": function(data, type, row) {
                    if (type === 'sort' || type === 'type') {
                        return parseFloat(data.replace(/[^\d.-]/g, ''));
                    }
                    return data;
                }
            }]
        });
        var table2Options = Object.assign({}, commonOptions, {
            "columnDefs": [{
                "type": "num",
                "targets": 2,
                "render": function(data, type, row) {
                    if (type === 'sort' || type === 'type') {
                        return parseFloat(data.replace(/[^\d.-]/g, ''));
                    }
                    return data;
                }
            }]
        });
        $('#tabel-cheltuieli').DataTable(table1Options);
        $('#tabel-venituri').DataTable(table2Options);
    }
    if (session_page === 'drivers') {
        var tableOptions = Object.assign({}, commonOptions, {
            "columnDefs": [{
                "orderable": false,
                "targets": $("#actions_column").index()
            }]
        });
        // var table = $('#tabel-soferi').DataTable(tableOptions);
        // var totalRows = table.rows().count() - 1;
        // commonOptions.language.info = "<b>TOTAL</b> - " + totalRows + " înregistrări";
        // table.destroy(); // Distrugeți tabelul existent
        // table = $('#tabel-soferi').DataTable(tableOptions); // Redefiniți tabelul cu opțiunile actualizate
        // table.draw();

        var table = $('#tabel-soferi').DataTable(tableOptions);
        var totalRows = table.rows().count() - 1;
        var infoElement = $('#tabel-soferi_info');
        infoElement.html("<b>TOTAL</b> - " + totalRows + " înregistrări");     
    }
  
    // Cautare in tabel
    $('.filterable .btn-filter').click(function() {
        var $panel = $(this).parents('.filterable'),
        $filters = $panel.find('.filters input'),
        $tbody = $panel.find('.table tbody');
        if ($filters.prop('disabled') == true) {
            $filters.prop('disabled', false);
            $filters.first().focus();
        } else {
            $filters.val('').prop('disabled', true);
            $tbody.find('.no-result').remove();
            $tbody.find('tr').show();
        }
    });
  
    $('.filterable .filters input').keyup(function(e) {
        var code = e.keyCode || e.which;
        if (code == '9') return;
        var $input = $(this),
        inputContent = $input.val().toLowerCase(),
        $panel = $input.parents('.filterable'),
        column = $panel.find('.filters th').index($input.parents('th')),
        $table = $panel.find('.table'),
        $rows = $table.find('tbody tr');
        var $filteredRows = $rows.filter(function(){
            var value = $(this).find('td').eq(column).text().toLowerCase();
            return value.indexOf(inputContent) === -1;
        });
        $table.find('tbody .no-result').remove();
        $rows.show();
        $filteredRows.hide();
        if ($filteredRows.length === $rows.length) {
            $table.find('tbody').prepend($('<tr class="no-result text-center"><td colspan="'+ $table.find('.filters th').length +'">Nu au fost gasite rezultate</td></tr>'));
        }
    });

    $('.filterable .filters input').click(function(e) {
        e.stopPropagation();
    });
    
    $(document).click(function() {
        $('.filterable .filters input').parents('th').addClass('sorting');
    });
    
});