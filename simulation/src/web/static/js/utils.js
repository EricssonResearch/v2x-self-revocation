var groups = {};
var revoked = {};
var fadeEffect = true;
const circleRadius = 10;
const squareLength = 150;
const numSlots = 16;

function refreshAll(data) {
    // refresh time
    $("#cur_time").text(data.time.toUTCString());
    $("#cur_hb").text("Heartbeat: { Time: " + data.hb.iat + " PRL: [" + data.hb.prl + "] }");

    // refresh revoked pseudonyms info
    refreshRevoked(data);

    // refresh svg
    refreshSvg(data);
}

function refreshRevoked(data) {
    let pseudonyms = data.ps;
    let t_eff = parseInt($("#t_eff").text());

    for(let ps in revoked) {
        let id = "revoked_" + ps;

        if(!(ps in pseudonyms)) {
            $("#" + id).hide();
        } else {
            $("#" + id).show();
            let last_activity = Math.max(
                pseudonyms[ps].last_seen,
                pseudonyms[ps].last_malicious
            ) - revoked[ps];
    
            if(last_activity < 0) continue;
            $("#" + id + "_time").text(last_activity + "/" + t_eff);
        }
    }
}

function refreshSvg(data) {
    let pseudonyms = data.ps;

    // update existing pseudonyms
    $('circle').each(function(){
        let ps = this.id;
        if(ps.startsWith("old_")) return;

        if(!(ps in pseudonyms) || pseudonyms[ps].is_unseen) {
            // remove if not in data
            freeSlot($(this).attr("group"), $(this).attr("slot"));
            $(this).tooltip('dispose');
            $(this).remove();
        } else {
            // update instead
            let status = pseudonyms[ps].status.toLowerCase();
            let currentClass = $(this).attr("class");            
            let group = pseudonyms[ps].group;
            if(!(group in groups)) {
                showMsg("Error", "Group " + group + " does not exist!");
                return;
            }
            
            // check if the group has changed
            if($("#" + ps).attr("group") != group) {
                // fetch slot
                if(!("slot" in pseudonyms[ps])) {
                    let slot = getRandomSlot(group);
                    assignSlot(group, slot);
                    pseudonyms[ps].slot = slot;
                }
                
                $(this).attr("id", "old_" + ps);
                createCircle(ps, status, group, pseudonyms[ps].slot);
                freeSlot($(this).attr("group"), $(this).attr("slot"));
                if(fadeEffect) {
                    fade($(this), $("#" + ps).attr("cx"), $("#" + ps).attr("cy"));
                } else {
                    $(this).remove();
                }
            } else {
                pseudonyms[ps].slot = $(this).attr("slot");

                if(status !== currentClass) {
                    $(this).removeClass().addClass(status);
                    $(this).attr("title", ps + " " + status);
                    $(this).tooltip("dispose");
                }
            }
        }
    });

    // add new ones
    for(let ps in pseudonyms) {
        if($("#" + ps).length != 0 || pseudonyms[ps].is_unseen) continue;

        let status = pseudonyms[ps].status.toLowerCase();
        let group = pseudonyms[ps].group;

        if(!(group in groups)) {
            showMsg("Error", "Group " + group + " does not exist!");
            continue;
        }

        // assign a slot among the existing ones
        let slot = getRandomSlot(group);
        assignSlot(group, slot);
        pseudonyms[ps].slot = slot;
        createCircle(ps, status, group, slot);
    }

    // toggle tooltip
    $('[data-toggle="tooltip"]').tooltip();

    // fade arrows that got possibly stuck
    $("line").fadeOut(2000, function() {
        $(this).remove();
    });
}

function fade(elem, x, y) {
    elem.fadeOut(2000, function() {
        elem.tooltip('dispose');
        elem.remove();
    });

    createArrow(elem.attr("cx"),elem.attr("cy"),x,y);
}

function createCircle(id, className, group, slot) {
    // find x, y of slot
    let base_x = groups[group].x;
    let base_y = groups[group].y;
    let slots_per_length = Math.floor(Math.sqrt(numSlots));
    let slot_length = squareLength / slots_per_length;

    let x = base_x + (slot % slots_per_length) * slot_length + circleRadius;
    let y = base_y + Math.floor(slot / slots_per_length) * slot_length + circleRadius;

    //console.log("group: " + group + " slot: " + slot + " x: " + x + " y: " + y);

    let circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    circle.setAttribute("id", id);
    circle.setAttribute("class", className);
    circle.setAttribute("group", group);
    circle.setAttribute("slot", slot);
    circle.setAttribute("cx", x);
    circle.setAttribute("cy", y);
    circle.setAttribute("r", circleRadius);
    circle.setAttribute("data-toggle", "tooltip");
    circle.setAttribute("data-placement", "top");
    circle.setAttribute("html", "true");
    circle.setAttribute("title", id + " " + className);
    circle.setAttribute("onclick", 'revoke("' + id + '")');
    document.getElementById("map").appendChild(circle);
}

function createArrow(x1, y1, x2, y2) {
    let arrow = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    let id = "arrow_" + 
        parseInt(x1) + "_" + 
        parseInt(y1) + "_" + 
        parseInt(x2) + "_" + 
        parseInt(y2);

    arrow.setAttribute("id", id);
    arrow.setAttribute("x1", x1);
    arrow.setAttribute("y1", y1);
    arrow.setAttribute("x2", x2);
    arrow.setAttribute("y2", y2);
    arrow.setAttribute("stroke", "#000");
    arrow.setAttribute("stroke-width", "3");
    arrow.setAttribute("marker-end", "url(#arrowhead)");
    document.getElementById("map").appendChild(arrow);

    $("#" + id).fadeOut(2000, function() {
        $("#" + id).remove();
    });
}

function getRandomCoordinate(baseCoord, length) {
    return baseCoord + circleRadius + getRandomValue(length - 2*circleRadius);
}

function getRandomValue(max) {
    return Math.floor(Math.random() * max);
}

function getRandomSlot(group) {
    //TODO what if there are no slots?
    return groups[group].free_slots[Math.floor(Math.random()*groups[group].free_slots.length)]
}

function assignSlot(group, slot) {
    let ind = groups[group].free_slots.indexOf(slot);
    groups[group].free_slots.splice(ind, 1);
}

function freeSlot(group, slot) {
    groups[group].free_slots.push(slot);
}

function showMsg(title, msg){
    console.log(title + " " + msg);
    $("#toast_title").text(title);
    $("#toast_body").text(msg);
    $("#myToast").toast("show");
}

function hideMsg(){
    //$("#myToast").toast("show");
}

function revoke(ps) {
    let t_eff = parseInt($("#t_eff").text());

    $.ajax({
        url: '/revoke/' + ps,
        type: 'GET',
        success: function(data){ 
            showMsg(ps, "Revoked! Effective within " + t_eff + " seconds.");
            let now = parseInt((new Date()).getTime() / 1000);
            revoked[ps] = now;
            let id = "revoked_" + ps;
            $("#revoked_info").append(
                '<tr id="' + id + '">' + 
                '<td id="' + id + '_id" class="td-left">' + ps + '</td>' +
                '<td id="' + id + '_time" class="td-right">0/' + t_eff + '</td>' + 
                "</tr>"
            );
        },
        error: function(data) {
          console.log(data.responseText);
          showMsg(ps, "Failed to revoke: " + data.responseText)
        }
      });

}

function create_groups() {
    let num_groups = parseInt($("#num_groups").text());
    if(num_groups === NaN || num_groups === 0) {
        showMsg("Warning", "Failed to parse num groups!");
    }

    let allowed = [
        // first row
        { "id": 2, "x": 1.3, "y": 0.2 },
        { "id": 1, "x": 2.4, "y": 0.8 },
        { "id": 10, "x": 6, "y": 0.1 },
        // second row
        { "id": 3, "x": 2.1, "y": 1.95 },
        { "id": 9, "x": 5.3, "y": 1.25 },
        // third row
        { "id": 4, "x": 1, "y": 3.4 },
        { "id": 5, "x": 2.3, "y": 3.1 },
        { "id": 6, "x": 3.8, "y": 3.5 },
        { "id": 8, "x": 5.4, "y": 2.4 },
        { "id": 7, "x": 6.5, "y": 3.3 },
    ];

    if(num_groups > allowed.length) {
        showMsg("Warning", "There are more groups than in the map!");
    }

    for(const area of allowed) {
        let x = area.x * squareLength;
        let y = area.y * squareLength;

        groups[area.id] = {
            "x": x,
            "y": y,
            "free_slots": [...Array(numSlots).keys()]
        }
    }

    printGroups();
}

function printGroups() {
    for(let g_id in groups) {  
        let group = groups[g_id];
        
        let rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');

        rect.setAttribute("class", "map_group");
        rect.setAttribute("x", group.x);
        rect.setAttribute("y", group.y);
        rect.setAttribute("width", squareLength);
        rect.setAttribute("height", squareLength);

        document.getElementById("map").appendChild(rect);
    }
}

function showGroups() {
    $('rect').each(function(){ 
        $(this).removeClass("invisible");
    });
}

function hideGroups() {
    $('rect').each(function(){ 
        $(this).addClass("invisible");
    });
}

function setFadeEffect(eff) {
    fadeEffect = eff;
}

/*
function setCanvasSize() {
    let width = $("#map").width();
    let height = $("#map").height();

	$("#map").attr("width", width);
	$("#map").attr("height", height);

}

function checkCanvas() {
    let width = $("#map").width();
    let height = $("#map").height();
    //console.log("Width: " + width + " Height: " + height);

    let canvasChanged = width !== curWidth || height !== curHeight;

    //store size
    curWidth = width;
    curHeight = height;

    return canvasChanged;
}

*/