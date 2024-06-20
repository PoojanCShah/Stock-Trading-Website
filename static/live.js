function updateTable(data, columns) {
    var tbody = document.getElementById('tbody');

    // Remove existing rows from tbody
    if (tbody) {
        tbody.innerHTML = '';

        // Create table rows
        data.forEach(function (item) {
            var tr = document.createElement('tr');
            if (item['Percentage Change'] > 0)
            {
                tr.classList.add('green');
            }
            else
            {
                tr.classList.add('red');
            }
            columns.forEach(function (column) {
                var td = document.createElement('td');
                td.textContent = item[column];
                tr.appendChild(td);
            });
            tbody.appendChild(tr);
        });
    }
}
function reset(){
    rows = all_rows.slice();
    updateTable(rows, columns);
}
function filter(){
    var temp = [];
    var column_to_filter = document.getElementById("filter").value;
    var from_v = document.getElementById("from").value;
    var to_v = document.getElementById("to").value;
    if (from_v == "" && to_v == "")
    {
        alert("Please enter a value to filter");
        return;
    }
    if (from_v == "")
    {
        from_v = -Infinity;
    }
    if (to_v == "")
    {
        to_v = Infinity;
    }
    for (var i = 0; i < rows.length; i++) {
        if (rows[i][column_to_filter] >= from_v && rows[i][column_to_filter] <= to_v)
        {
            temp.push(rows[i]);
        }
    }
    rows = temp;
    updateTable(rows, columns);
}


function sort_column(column_to_sort){
    current_column = document.getElementById(column_to_sort);
    for (let index = 0; index < filterable_columns.length; index++) {
        const colu = filterable_columns[index];
        if (colu != column_to_sort)
        {
            document.getElementById(colu).classList.remove("asc");
            document.getElementById(colu).classList.remove("desc");
            document.getElementById(colu).classList.add("ascdesc");
        }
    }
    if (current_column.classList.contains("asc"))
    {
        current_column.classList.remove("asc");
        current_column.classList.add("desc");
        rows.sort(function(a, b) {
            return parseFloat(a[column_to_sort]) - parseFloat(b[column_to_sort]);
        });
    }
    else
    {
        current_column.classList.remove("desc");
        current_column.classList.add("asc");
        rows.sort(function(a, b) {
            return parseFloat(b[column_to_sort]) - parseFloat(a[column_to_sort]);
        });
    }
    current_column.classList.remove("ascdesc");
    updateTable(rows, columns);
}