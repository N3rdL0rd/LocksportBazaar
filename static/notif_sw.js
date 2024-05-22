const indexedDB = self.indexedDB || self.mozIndexedDB || self.webkitIndexedDB || self.msIndexedDB;
const IDBTransaction = self.IDBTransaction || self.webkitIDBTransaction;
const IDBKeyRange = self.IDBKeyRange || self.webkitIDBKeyRange;

const request = indexedDB.open("tokensDB", 1);

request.onupgradeneeded = function(event) {
    const db = event.target.result;
    const objectStore = db.createObjectStore("tokens", { keyPath: "id" });
    objectStore.createIndex("token", "token", { unique: false });
};

request.onsuccess = function(event) {
    const db = event.target.result;
    self.addEventListener('message', event => {
        const token = event.data;
        const transaction = db.transaction(["tokens"], "readwrite");
        const objectStore = transaction.objectStore("tokens");

        if (token !== "NONE") {
            objectStore.add({ id: 1, token: token });
        } else {
            objectStore.put({ id: 1, token: "" });
        }
    });

    self.addEventListener("sync", (event) => {
        const transaction = db.transaction(["tokens"], "readonly");
        const objectStore = transaction.objectStore("tokens");

        const getRequest = objectStore.get(1);
        getRequest.onsuccess = function() {
            const storedToken = getRequest.result.token;
            if (storedToken) {
                fetch("/push/" + storedToken)
                    .then(res => res.json())
                    .then(data => {
                        for (const notif of data) {
                            new Notification("LocksportBazaar", { body: notif.msg });
                        }
                    });
            }
        };
    });
};
