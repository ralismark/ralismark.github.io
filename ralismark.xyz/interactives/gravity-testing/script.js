'use strict';

function planet_gen() {
	return [ (Math.random() - 0.5) * 500 + innerWidth / 2,
	         (Math.random() - 0.5) * 500 + innerHeight / 2,
	         30 * Math.random() + 10 ];
}

var w = {
		//g: 0.1, // Gravity
		//b: 0.8, // Bounciness
		//l: 0, // Looping edge
		t: 2, // Trace type
		s: 0.2, // Emulation speed multiplier
		//w: innerHeight / 2, // Water level
		//d: 2, // Water Density / Buoyancy, 2 for antigrav, more for buoyancy
		//r: 1, // Water Resistance Y, neg for bounce
		//f: 0.99, // Friction / Water Resistance X
		// d: 1, r:-1 = bounce
	},
	g = {
		y: 400, // Y pos
		vy: 0, // Y Velocity
		x: 1000, // X pos
		vx: 0.55, // X Velocity
		r: 0, // Rotation
	},
	p = [
		[ 300, 300, 10 ],
		[ 1000, 300, 30 ],
		// planet_gen(),
		// planet_gen(),
		// planet_gen(),
		// planet_gen(),
		// [(innerWidth + 10 * Math.random()) / 2, innerHeight * Math.random(), 5 * Math.random() + 1],
		// [innerWidth * Math.random(), innerHeight * Math.random(), 5 * Math.random() + 1],
		//[innerWidth * Math.random(), innerHeight * Math.random(), 10 * Math.random() + 5]
	];

function tick() { /* Non-planetary physics
	//g.vx = g.y < 0.5 + w.w ? g.vx * w.f : g.vx; // Friction
	// if(g.y <= w.w) { // On the ground OR in water
	// 	//g.vy = g.vy * w.r + w.d * w.g;
	// }
	if(w.l && 0) {
		if(g.x > innerWidth) {
			g.x = g.x - innerWidth;
		} else if(g.x + 10 < 0) {
			g.x = g.x + innerWidth;
		}
	} else if(g.x + 10 > innerWidth || g.x < 0) {
		//g.vx *= -1;
	} */
	//g.vy -= w.g; // "Gravity"
	for(var i in p) {
		var d = Math.sqrt(Math.pow(p[i][0] - g.x, 2) + Math.pow(p[i][1] - g.y, 2)),
			a = Math.atan2(p[i][0] - g.x, p[i][1] - g.y);
		g.vy += Math.cos(a) * (p[i][2] / (d * d)) * w.s;
		g.vx += Math.sin(a) * (p[i][2] / (d * d)) * w.s;
	}
	g.r = (Math.atan2(g.vx, g.vy) * -180 / Math.PI + 180) % 360;
	if(g.r < 0) {
		g.r += 360;
	}
	if(g.r > 360) {
		g.r -= 460;
	}
	// g.vy = g.vy > 10 ? 10 : g.vy;
	// g.vx = g.vx > 10 ? 10 : g.vx;
	g.y += g.vy * w.s;
	g.x += g.vx * w.s;
	return g;
}

function coll() {
	var h = [];
	for(var i in p) {
		var d = Math.sqrt(Math.pow(p[i][0] - g.x, 2) + Math.pow(p[i][1] - g.y, 2));
		if(d < p[i][2]) {
			h.push(i);
		}
	}
	return h
}

function stop() {
	var highestTimeoutId = setTimeout(";");
	for (var i = 0 ; i < highestTimeoutId ; i++) {
		clearTimeout(i);
	}
}

function pos() {
	var gr = tick();
	$('#test').css({
		top: gr.y,
		left: gr.x + 2.5,
		transform: 'rotate(' + g.r + 'deg)',
	});
	$('#rot').css({
		transform: 'rotate(' + g.r + 'deg)',
	})
	$('#x').text(Math.round(gr.x * 100) / 100 + ' | ' + Math.round(gr.vx * 100) / 100);
	$('#y').text(Math.round(gr.y * 100) / 100 + ' | ' + Math.round(gr.vy * 100) / 100);
}

function init() {
	var i = setInterval(function() {
		pos();
		if(w.t == 1 || w.t == 3) {
			trace();
		}
		if(w.t == 2 || w.t == 3) {
			line();
		}
		var coll_results = coll();
		if(coll_results.length > 0) {
			stop();
			for(var i in coll_results) {break;
				var planet = p[coll_results[i]];

				var normal = { x: g.x - planet[0], y: g.x - planet[1] };
				var size = Math.sqrt(Math.pow(normal.x, 2) + Math.pow(normal.y, 2));
				normal.x /= size; normal.y /= size; // normalise

				var dprod = normal.x * g.vx + normal.y + g.vy;
				var x = { x: 2 * dprod * g.vx, y : 2 * dprod * g.vy };
				var n = { x: g.vx - x.x, y: g.vy - x.y };

				g.vx = n.x; g.vy = n.y;
				// g.vx *= -0.9; g.vy *= -0.9;
				// g.vx =0; g.vy = 0;

				var radius = planet[2] + 1;
				var minsep = { x: normal.x * radius + planet[0], y: normal.y * radius + planet[1] };

				g.x = minsep.x; g.y = minsep.y;
			}
		};
	}, 10);
	$('.planet').remove();
	for(var x in p) {
		var s = Math.abs(p[x][2]);
		$('body').append('<div class="planet s"></div>');
		$('.planet.s').removeClass('s').css({
			top: p[x][1] + 5,
			left: p[x][0] + 5,
			border: s + 'px solid ' + (p[x][2] < 0 ? '#aaa' : '#555'),
		})
	}
	//$('#water').attr('points', '0,' + (innerHeight - w.w - 5) + ' ' + innerWidth + ',' + (innerHeight - w.w - 5));
}

function input() {
	var gr = {
		y: prompt('y pos'),
		vy: prompt('y vel') / 100,
		x: prompt('x pos'),
		vx: prompt('x vel') / 100,
	};
	for(var i in gr) {
		if(isNaN(Number(gr[i])) || gr[i].match(/ +/) || !gr[i]) {
			gr[i] = g[i];
		} else {
			gr[i] = Number(gr[i]);
		}
	};
	g = gr;
}

function trace() {
	$('body').append('<div class="tracer s" style="bottom:' + g.y + 'px;left:' + g.x + 'px"></div>');
	$('div.s').removeClass('s').animate({
		opacity: 0
	}, 5000, function(){
		$(this).remove()
	});
}

function line() {
	$('polyline#trace').attr('points', ($('polyline#trace').attr('points') || '') + (Math.round(g.x * 10) / 10 + 5) + ',' + (Math.round(g.y * 10) / 10 + 5) + ' ');
}

function clear() {
	$('polyline#trace').attr('points', '');
}

function boost_in(dir) {
	g.vx += Math.cos(dir) * 0.02;
	g.vy += Math.sin(dir) * 0.02;
}

$(document).ready(function(){
	init();
	$(document).keypress(function(e) {
		var k = e.keyCode;
		console.log(k);
		if(k == 32) { // Space
			input();
		} else if(k == 120) { // X
			pos();
			if(w.t == 1) {
				trace();
			} else if(w.t == 2) {
				line();
			}
		} else if(k == 122) { // Z
			init();
		} else if(k == 99) { // C
			clear();
		} else if(k == 49) { // 1
			stop();
		} else if(k == 119) { // W
			boost_in(Math.atan2(g.vy, g.vx));
		} else if(k == 97) { // A
			boost_in(Math.atan2(g.vy, g.vx) - Math.PI / 2);
		} else if(k == 115) { // S
			boost_in(Math.atan2(g.vy, g.vx) - Math.PI);
		} else if(k == 100) { // D
			boost_in(Math.atan2(g.vy, g.vx) + Math.PI / 2);
		}
	});
	$(document).mousedown(function(e) {
		stop();
		clear();
		init();
		g.x = e.pageX - 5;
		g.y = e.pageY - 5;
		/*g.vx += (e.pageX - g.x) / 2000;
		g.vy += (e.pageY - g.y) / 2000;*/
	});
})
