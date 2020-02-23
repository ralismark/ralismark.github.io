// these could probably be customised later
const CONFIG_VER = 2;
const DAY_START = 8;
const DAY_END = 20;
const TIME_BOUNDS = (() => {
	let now = new Date();
	now.setMilliseconds(0);
	now.setSeconds(0);
	now.setMinutes(0);
	now.setHours(0);

	let start = new Date(now);
	start.setDate(start.getDate() - start.getDay() + 1);
	let end = new Date(start);
	end.setDate(end.getDate() + 5);

	return [start, end];
})();

function hr2pc(val) {
	return val / (DAY_END - DAY_START) * 100 + "%";
}

function stringHash(str) {
	let hash = 0;
	for(let c of str) {
		hash = str.charCodeAt(c) + ((hash << 5) - hash);
		hash = hash & hash; // to convert to int
	}
	return hash;
}

function string2color(str, opacity=1) {
	return "hsl(" + (stringHash(str) & 0xff) + "rad, 50%, 50%, " + opacity + ")";
}

function addEvent(day, start, duration, desc, id) {
	// TODO handle collisions
	let elem = document.createElement("div");
	elem.classList.add("event");

	elem.style.left = day * 20 + "%";
	elem.style.top = hr2pc(start - DAY_START);
	elem.style.height = hr2pc(duration);
	elem.style.setProperty("--color", string2color(id, 0.9));
	elem.setAttribute("calendar", id);

	let content = document.createElement("div");
	content.classList.add("summary");
	content.innerHTML = desc;
	elem.appendChild(content);

	let container = document.querySelector("#calendar");
	container.appendChild(elem);
}

let cache = {};

function fetchWebcal(url) {
	return new Promise((accept, reject) => {
		let address = url.replace(/^webcal/, "https");
		if(address in cache) {
			accept(cache[address]);
			return;
		}

		// We need to bypass CORS since a lot of webcal urls (e.g. UNSW timetables) don't support it
		let xhr = new XMLHttpRequest();
		xhr.onerror = reject;
		xhr.onload = (event) => {
			cache[address] = xhr.responseText;
			accept(cache[address]);
		};
		xhr.open("GET", "https://non-cors.herokuapp.com/" + address);
		xhr.send();
	});
}

function loadWebcal(data) {
	// parse ical to a list of events
	let jcal = ICAL.parse(data);
	let comp = new ICAL.Component(jcal);
	let events = comp.getAllSubcomponents("vevent").map(e => new ICAL.Event(e));

	let out = [];

	for(let ev of events) {
		// We need to iterate from start date, or else the time isn't applied correctly
		let iter = ev.iterator(ev.startDate);
		for(let date = iter.next(); date && date.toJSDate() < TIME_BOUNDS[1]; date = iter.next()) {
			if(date.toJSDate() < TIME_BOUNDS[0]) continue;
			let occurrence = ev.getOccurrenceDetails(date);
			let duration = occurrence.endDate.subtractDateTz(occurrence.startDate);
			let data = {
				day: occurrence.startDate.dayOfWeek() - 2,
				start: occurrence.startDate.hour + occurrence.startDate.minute / 60,
				duration: duration.hours + duration.minutes / 60,
				event: ev,
			};
			if(data.duration > 0) out.push(data);
		}
	}

	return out;
}

function addDataEvents(events, id) {
	for(let ev of events) {
		let name = ev.event.summary.replace(/[A-Z]{4}\d{4}/, "<span class=\"class\">$&</span>");
		addEvent(ev.day, ev.start, ev.duration, name, id);
	}
}

function fixNow() {
	let elem = document.querySelector("#now");
	let now = new Date();

	elem.style.left = (now.getDay() - 1) * 20 + "%";
	elem.style.top = hr2pc(now.getHours() + now.getMinutes()/60 - DAY_START);
}

let calendars = {};
let spinnerCount = 0;

let migration = {
	1: data => {
		let out = { version: 2, data: {} };
		for(let cal in data.data) out.data[cal] = { state: data.data[cal], name: cal };
		return out;
	}
};

function saveCalendars() {
	localStorage.setItem("calendars", JSON.stringify({ version: CONFIG_VER, data: calendars }));
}

function enableCalendar(url) {
	if(!(url in calendars)) {
		console.error(url, " not in calendars");
		return;
	}
	if(calendars[url].state) return; // don't load twice
	calendars[url].state = true;
	console.log("enable", url);

	if(spinnerCount++ === 0) {
		document.querySelector("body").classList.add("loading");
	}

	fetchWebcal(url).then(loadWebcal).then(d => addDataEvents(d, url)).finally(() => {
		if(--spinnerCount === 0) {
			document.querySelector("body").classList.remove("loading");
		}
	});

	saveCalendars();
}

function disableCalendar(url) {
	if(!(url in calendars)) {
		console.error(url, " not in calendars");
		return;
	}
	calendars[url].state = false;
	console.log("disable", url);

	for(let elem of document.querySelectorAll("#calendar > .event")) {
		if(elem.getAttribute("calendar") === url) {
			elem.parentNode.removeChild(elem);
		}
	}

	saveCalendars();
}

function addCalendar(url, name) {
	if(url in calendars) {
		for(let elem of document.querySelectorAll("#cal-entry")) {
			if(elem.getAttribute("calendar") === url) {
				elem.parentNode.removeChild(elem);
			}
		}
	}

	calendars[url] = {state: false, name: name};
	saveCalendars();

	let entry = document.createElement("li");
	entry.classList.add("list-group-item", "cal-entry");
	entry.setAttribute("calendar", url);

	let toggle = document.createElement("input");
	toggle.type = "checkbox";
	toggle.addEventListener("change", function() {
		if(this.checked) {
			enableCalendar(url);
		} else {
			disableCalendar(url);
		}
	});

	let label = document.createElement("label");
	label.style.color = string2color(url);
	label.appendChild(toggle);
	label.appendChild(document.createTextNode(" " + name + " "));
	entry.appendChild(label);

	let link = document.createElement("a");
	link.innerText = "\ud83d\udd17";
	link.href = url;
	entry.appendChild(link);

	let close = document.createElement("button");
	close.type = "button";
	close.classList.add("close");
	close.innerHTML = "&times;";
	close.addEventListener("click", function() {
		removeCalendar(url);
	});
	entry.appendChild(close);

	document.querySelector("#webcal-list").appendChild(entry);
}

function setCalendarToggle(url, state) {
	for(let elem of document.querySelectorAll(".cal-entry")) {
		if(elem.getAttribute("calendar") !== url) continue;
		let checkbox = elem.querySelector("input[type=checkbox]");
		checkbox.checked = state;
		checkbox.dispatchEvent(new Event("change"));
	}
}

function removeCalendar(url) {
	if(!(url in calendars)) {
		console.error(url, " not in calendars");
		return;
	}

	disableCalendar(url); // removes event elements
	delete calendars[url];
	for(let elem of document.querySelectorAll("#webcal-list > .cal-entry")) {
		if(elem.getAttribute("calendar") === url) {
			elem.parentNode.removeChild(elem);
		}
	}
}

function loadCalendarConfig(config) {
	for(let url in calendars) removeCalendar(url);

	while(config.version < CONFIG_VER) {
		config = migration[config.version](config);
	}

	for(let url in config.data) {
		addCalendar(url, config.data[url].name);
		setCalendarToggle(url, config.data[url].state);
	}
}

document.querySelector("#form-add").addEventListener("submit", function(event) {
	event.preventDefault();

	let url = this.querySelector("#add-url").value.replace(/^\s+|\s+$/g, '');
	let name = this.querySelector("#add-name").value;
	addCalendar(url, name);
	setCalendarToggle(url, true);

	this.reset();
});

fixNow();
setInterval(fixNow, 1000*60);

loadCalendarConfig(JSON.parse(localStorage.getItem("calendars")) || {});
