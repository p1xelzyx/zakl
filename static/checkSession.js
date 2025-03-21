window.onload = function() {
    console.log("checking session")
    $.ajax({
        type: "POST",
        url: "/checkSession",
        xhrFields: {
            withCredentials: true
        },
        success: function (data) {
            if (data.status == "not found") {
                window.location.href = "/";
            }
        },
        error: function (errMsg) {
            console.log(errMsg);
        }
    });
};