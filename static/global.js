$(document).ready(function(){

        $('#clear-db-btn').on('click', function (e) {
            e.preventDefault();
            bootbox.confirm("Are you sure you want to clear entire database?", function(result){
                if (result) {
                    $.ajax({
                        type: "POST",
                        url: "/cleardb/",
                        success: function(){
                           window.location.reload(true);
                        },
                        error: function () {
                            alert("Something went wrong, please try again.")
                        }
                    })
                }
            });
        });

        $.fn.dataTable.ext.search.push(
        function (settings, data, dataIndex) {
            var min = $('#min').datepicker("getDate");
            var max = $('#max').datepicker("getDate");
            var startDate = new Date(data[4]);
            if (min == null && max == null) { return true; }
            if (min == null && startDate <= max) { return true;}
            if(max == null && startDate >= min) {return true;}
            if (startDate <= max && startDate >= min) { return true; }
            return false;
        }
        );


        $("#min").datepicker({ onSelect: function () { table.draw(); }, changeMonth: true, changeYear: true });
        $("#max").datepicker({ onSelect: function () { table.draw(); }, changeMonth: true, changeYear: true });
        var table = $('#example').DataTable();

        // Event listener to the two range filtering inputs to redraw on input
        $('#min, #max').change(function () {
            table.draw();
        });

        $.fn.dataTable.ext.search.push(
        function (settings, data, dataIndex) {
            var min = $('#min2').datepicker("getDate");
            var max = $('#max2').datepicker("getDate");
            var startDate = new Date(data[4]);
            if (min == null && max == null) { return true; }
            if (min == null && startDate <= max) { return true;}
            if(max == null && startDate >= min) {return true;}
            if (startDate <= max && startDate >= min) { return true; }
            return false;
        }
        );


        $("#min2").datepicker({ onSelect: function () { table2.draw(); }, changeMonth: true, changeYear: true });
        $("#max2").datepicker({ onSelect: function () { table2.draw(); }, changeMonth: true, changeYear: true });
        var table2 = $('#example2').DataTable();

        // Event listener to the two range filtering inputs to redraw on input
        $('#min2, #max2').change(function () {
            table2.draw();
        });

        $('body .list-group .delete-icon').on('click', function (e) {
            e.preventDefault();
            console.log("Comes here");
            var data = $(this).data('filename');
            if (data.includes("Balance")) {
                bootbox.confirm("Are you sure?", function(result){ /* your callback code */ })
            }
        });
});