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
            var ts = $('#ts1').find(":selected").text();
            var startDate = new Date(data[4]);
            var transactionStatus = data[3].toString();
            var temp = true;
            if(ts !== "All") {temp = transactionStatus === ts;}
            if (min == null && max == null) { return temp; }
            if (min == null && startDate <= max) { return temp;}
            if(max == null && startDate >= min) {return temp;}
            if (startDate <= max && startDate >= min) { return temp; }
            return false;
        }
        );


        $("#min").datepicker({ onSelect: function () { table.draw(); }, changeMonth: true, changeYear: true });
        $("#max").datepicker({ onSelect: function () { table.draw(); }, changeMonth: true, changeYear: true });
        var table = $('#example').DataTable();

        // Event listener to the two range filtering inputs to redraw on input
        $('#min, #max, #ts1').change(function () {
            table.draw();
        });

        $.fn.dataTable.ext.search.push(
        function (settings, data, dataIndex) {
            var min = $('#min2').datepicker("getDate");
            var max = $('#max2').datepicker("getDate");
            var ts = $('#ts2').find(":selected").text();
            var startDate = new Date(data[4]);
            var transactionStatus = data[3].toString();
            var temp = true;
            if(ts !== "All") {temp = transactionStatus === ts;}
            if (min == null && max == null) { return temp; }
            if (min == null && startDate <= max) { return temp;}
            if(max == null && startDate >= min) {return temp;}
            if (startDate <= max && startDate >= min) { return temp; }
            return false;
        }
        );


        $("#min2").datepicker({ onSelect: function () { table2.draw(); }, changeMonth: true, changeYear: true });
        $("#max2").datepicker({ onSelect: function () { table2.draw(); }, changeMonth: true, changeYear: true });
        var table2 = $('#example2').DataTable();

        // Event listener to the two range filtering inputs to redraw on input
        $('#min2, #max2, #ts2').change(function () {
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