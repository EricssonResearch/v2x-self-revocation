const maxSteps = 300;
var steps = [];
var currentStep = 0;
var realTime = true;

$(document).ready(function() {
	startWorkerRefresh();
	$("#play_btn").hide();

	$("#myToast").toast({
        autohide: true
    }); 

	create_groups();
});

document.onkeydown = checkKey;

function checkKey(e) {
    if (e.keyCode == '32') {
        // whitespace
		if(realTime) pause();
		else resume();
    }
    else if (e.keyCode == '37') {
       // left arrow
	   previous();
    }
    else if (e.keyCode == '39') {
       // right arrow
	   next();
    }

}

function refreshData(step) {
	let data = steps[step];
	refreshAll(data);
}

function pause() {
	setRealTime(false);
}

function resume() {
	goToStep(steps.length -1);
	setRealTime(true);
}

function next() {
	setRealTime(false);
	goToStep(++currentStep, disableFade = false);
}

function previous() {
	setRealTime(false);
	goToStep(--currentStep, disableFade = true);
}

function goToStep(step, disableFade = true) {
	if(step < 0 || step >= steps.length) {
		showMsg("Error", "Invalid step");
		return;
	}

	setRealTime(false);
	currentStep = step;
	
	let oldFade = fadeEffect;
	if(disableFade) {
		setFadeEffect(false);
	}

	refreshData(step);

	if(disableFade) {
		setFadeEffect(oldFade);
	}
}

function startWorkerRefresh() {
	let worker = new Worker("static/js/worker-refresh.js");
  
	worker.onmessage = function(event) {
		try {
			let data = JSON.parse(event.data);
			data.time = new Date();
			//console.log(data);
			steps.push(data);

			if(realTime) {
				steps.splice(0, steps.length -maxSteps);
				currentStep = steps.length - 1;
				refreshData(currentStep);
			}
		} catch(e) {
			//console.log(e);
			console.log("Failed to get data");
			return;
		}
	};
}

function setRealTime(val) {
	if(val) {
		realTime = true;
		$("#play_btn").hide();
		$("#pause_btn").show();
	} else {
		realTime = false;
		$("#play_btn").show();
		$("#pause_btn").hide();
	}
}