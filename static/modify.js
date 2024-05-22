// hi mow. don't hate me for this please

const old_images_raw = document.getElementById("imgs").value;
const old_images = JSON.parse(old_images_raw.replaceAll(`'`, `"`));
const input_container = document.getElementById("images-input");
const noscript_container = document.getElementById("images-noscript");

var new_inputs = [];
var i = 0;
old_images.forEach(image => {
    console.log(image);
    var label = document.createElement("label");
    var input = document.createElement("input");
    var img = document.createElement("img");
    img.src = image;
    img.style.height = "100px";
    input.id = "img-" + i;
    input.type = "text";
    input.value = image;
    input.name = "img-" + i;
    input.oninput = function() {
        img.src = input.value;
    }
    label.htmlFor = "img-" + i;
    input_container.appendChild(label);
    input_container.appendChild(input);
    input_container.appendChild(img);
    new_inputs.push(input);
    i++;
});

input_container.style.display = "block";
noscript_container.style.display = "none";

function add_image() {
    var label = document.createElement("label");
    var input = document.createElement("input");
    var img = document.createElement("img");
    img.src = "";
    img.style.height = "100px";
    input.id = "img-" + i;
    input.type = "text";
    input.value = "";
    input.name = "img-" + i;
    input.oninput = function() {
        img.src = input.value;
    }
    label.htmlFor = "img-" + i;
    input_container.appendChild(label);
    input_container.appendChild(input);
    input_container.appendChild(img);
    new_inputs.push(input);
    i++;
}

function remove_image() {
    if (new_inputs.length > 0) {
        var last_input = new_inputs[new_inputs.length - 1];
        var last_label = document.querySelector(`label[for="${last_input.id}"]`);
        var last_img = input_container.querySelector(`img[src="${last_input.value}"]`);

        if (last_label) input_container.removeChild(last_label);
        if (last_input) input_container.removeChild(last_input);
        if (last_img) input_container.removeChild(last_img);

        new_inputs.pop();
        i--;
    }
}

document.getElementById("modify_form").onsubmit = function(event){
    event.preventDefault();
    document.getElementById("imgs").remove();
    var new_inputs_values = new_inputs.map(input => input.value);
    var new_inputs_json = JSON.stringify(new_inputs_values).replaceAll(`"`, `'`);
    var hidden_input = document.createElement("input");
    hidden_input.type = "hidden";
    hidden_input.value = new_inputs_json;
    hidden_input.name = "imgs";
    hidden_input.id = "imgs";
    document.getElementById("modify_form").appendChild(hidden_input);
    document.getElementById("modify_form").submit();
};