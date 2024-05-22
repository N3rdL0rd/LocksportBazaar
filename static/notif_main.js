window.onload = () => {
    if (Notification.permission === "default") {
        if (document.location.pathname.startsWith('/profile')) {
            document.getElementById('push-container').innerHTML = `<blockquote>Push notification permissions have not yet been granted. If you want to enable push notifications, click the button below.</blockquote>`;
            document.getElementById('push-dynamic').innerHTML = `<button id='request-notif-perms' onclick='request_notif_perms();'>Request notification permissions</button>`
        }
    }
    else if (Notification.permission === "granted") {
        if (document.location.pathname.startsWith('/profile')) {
            document.getElementById('push-container').innerHTML = ``;
            document.getElementById('push-dynamic').innerHTML = "";
            // TODO: customizable notification settings
        }
        regWorker();
    }
    else {
        console.warn("Notifications are not allowed!");
        if (document.location.pathname.startsWith('/profile')) {
            document.getElementById('push-container').innerHTML = `<blockquote>Push notification permissions were denied. In order to enable push notifications, please allow it in your browser's settings.</blockquote>`;
        }
    }
}

function request_notif_perms() {
    Notification.requestPermission().then(perm => {
        if (Notification.permission === "granted") {
            regWorker().catch(err => console.error(err));
        } else {
            console.warn("Notifications are not allowed!");
            if (document.location.pathname.startsWith('/profile')) {
                document.getElementById('push-container').innerHTML = `<blockquote>Push notification permissions were denied.</blockquote>`;
                document.getElementById('push-dynamic').innerHTML = "";
            }
        }
    });
}

// https://stackoverflow.com/questions/5968196/how-do-i-check-if-a-cookie-exists
function getCookie(name) {
    var dc = document.cookie;
    var prefix = name + "=";
    var begin = dc.indexOf("; " + prefix);
    if (begin == -1) {
        begin = dc.indexOf(prefix);
        if (begin != 0) return null;
    } else {
        begin += 2;
        var end = document.cookie.indexOf(";", begin);
        if (end == -1) {
        end = dc.length;
        }
    }
    return decodeURI(dc.substring(begin + prefix.length, end));
} 

function check_token(reg) {
    if (getCookie("token_DO_NOT_SHARE")){
        reg.active.postMessage(getCookie("token_DO_NOT_SHARE"));
    } else {
        reg.active.postMessage("NONE");
    }
    setTimeout(function(){check_token(reg)}, 500);
}

async function regWorker() {
    navigator.serviceWorker.register("/push_sw.js", { scope: "/" }).catch(err => {
        console.warn(err);
        if (document.location.pathname.startsWith('/profile')) {
            document.getElementById('push-container').innerHTML = `<blockquote>Push notifications are not supported in this environment.</blockquote>`;
        }
    });
    navigator.serviceWorker.ready
        .then(reg => {
            reg.periodicSync.register("push-notifs", {
                minInterval: 300000, // every 5 minutes
            });
            check_token(reg);
        }).catch(err => {
            console.warn(err);
            if (document.location.pathname.startsWith('/profile')) {
                document.getElementById('push-container').innerHTML = `<blockquote>Push notifications are not enabled due to an error.</blockquote>`;
            }
        });    
}