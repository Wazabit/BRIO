function handle_disab_frompred() {
    $('#root_var').selectpicker('toggle');
    var disab = document.getElementById("predictions");
    var selected_option = disab.options[disab.selectedIndex];

    var dd_root = document.getElementById("bs-select-2");
    var lis_root = dd_root.firstElementChild.getElementsByTagName('li');
    for (var j = 0; j < lis_root.length; j++) {
	if (lis_root[j].firstElementChild.lastElementChild.innerText == selected_option.value) {
            lis_root[j].className = "disabled";
            $('li.disabled').hide();
        }
        else {
            if (lis_root[j].classList.contains("disabled")) {
                $('li.disabled').removeAttr("style");
                $('li.disabled').show();
                lis_root[j].classList.remove("disabled");
            }
        }
    }

    $('#cond_var').selectpicker('toggle');
    var dd_cond = document.getElementById("bs-select-3");
    var lis_cond = dd_cond.firstElementChild.getElementsByTagName('li');
    for (var j = 0; j < lis_cond.length; j++) {
	if (lis_cond[j].firstElementChild.lastElementChild.innerText == selected_option.value) {
            lis_cond[j].className = "disabled";
            $('li.disabled').hide();
        }
        else {
            if (lis_cond[j].classList.contains("disabled")) {
                $('li.disabled').removeAttr("style");
                $('li.disabled').show();
                lis_cond[j].classList.remove("disabled");
            }
        }
    }
}

function handle_disab_fromroot() {
    $('#cond_var').selectpicker('toggle');
    var disab = document.getElementById("root_var");
    var selected_option = disab.options[disab.selectedIndex];
    var dd = document.getElementById("bs-select-3");
    var lis = dd.firstElementChild.getElementsByTagName('li');
    for (var j = 0; j < lis.length; j++) {
	if (lis[j].firstElementChild.lastElementChild.innerText == selected_option.value) {
            lis[j].className = "disabled";
            $('li.disabled').hide();
        }
        else if (lis[j].classList.contains("disabled")) {
            $('li.disabled').show();
            lis[j].classList.remove("disabled");
        }
    }
}

function handle_select() {
    var select = document.getElementById("cond_var").nextElementSibling;
    var textarea = document.getElementById("mytext");
    textarea.value = select.title;
}

function sel_all() {
    var textarea = document.getElementById("mytext");
    var select = document.getElementById("cond_var");
    var options = select.options;
    var values = [];
    for (var i = 0; i < options.length; i++) {
	values.push(options[i].value);
    }
    textarea.value = values.join(" ");
}

function desel_all() {
    var textarea = document.getElementById("mytext");
    textarea.value = "";
}


document.addEventListener("DOMContentLoaded", function() {
  $('[data-bs-toggle="popover"]').popover();
  var disabfrompred = document.getElementById("predictions");
  disabfrompred.addEventListener("change", handle_disab_frompred);
  var disabfromroot = document.getElementById("root_var");
  disabfromroot.addEventListener("change", handle_disab_fromroot);
  var select = document.getElementById("cond_var");
  select.addEventListener("change", handle_select);
  var select_all = document.getElementsByClassName("bs-actionsbox")[0].firstElementChild.firstElementChild;
  select_all.addEventListener("click", sel_all);
  var deselect_all = document.getElementsByClassName("bs-actionsbox")[0].firstElementChild.children[1];
  deselect_all.addEventListener("click", desel_all);
});

function calculate_value(current_value, current_target) {
    return parseFloat(current_value / current_target).toFixed(2)
}

const inputs_changed = {};

function get_current_value(v_root) {
    var current_value = 1
    inputs_changed[v_root].forEach(function (i, el) {
        const input = document.getElementById(i);
        current_value = current_value - input.value
    })
    return current_value
}

function updateRefValue(v_root,v_pred) {
    const inputs = document.querySelectorAll('[id*="prob_' + v_root + '"]');

    if(!inputs_changed[v_root] || ((inputs.length - 1) === inputs_changed[v_root].length))
     inputs_changed[v_root] = ["prob_" + v_root + "_" + v_pred]
    else if(!inputs_changed[v_root].includes("prob_" + v_root + "_" + v_pred))
        inputs_changed[v_root].push("prob_" + v_root + "_" + v_pred)

    let current_value = get_current_value(v_root)
    let current_target = inputs.length - inputs_changed[v_root].length

    inputs.forEach(function (i, el) {
        if(!inputs_changed[v_root].includes(i.id)){
            i.value = calculate_value(current_value, current_target)
            current_value = current_value - i.value
            current_target = current_target - 1
        }

     });

}
