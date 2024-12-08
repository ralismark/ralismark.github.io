"use strict";

const fps = 30; // renders per second
let debug_overlay = false; // show AI guides

let score = 0;

let canvas = document.querySelector("canvas");
let ctx = canvas.getContext("2d");

function createGrid(value) {
	return Array(W.gdims.x).fill().map(i => new Array(W.gdims.y).fill(value));
}

// load resources, each promise should return k-v pair for resource
let R = Promise.all([

	...["knight", "bishop", "queen", "king", "pawn", "stair"].map(i => {
		return loadImage(i + ".png")
			.then((img) => new Spritesheet(img, 16, 16))
			.then((ss) => [i, ss]);
	}),

	loadImage("dragon.png").then((img) => ["dragon", new Spritesheet(img, 32, 32)]),

]).then((res) => {
	R = res.reduce((acc, val) => {
		acc[val[0]] = val[1];
		return acc;
	}, {});
});

// global state
let W = {
	gdims: new Vector(16, 9), // grid size
	ssize: new Vector(48, 48), // square size

	p: new Vector(0, 0), // player position
	rp: null, // rendered player position
	fade: 0, // screen fade

	r: null, // alternative render positions, [ [ SpaceType, Vector ] ... ]

	C: { // cache
		pmoves: null,
		threats: null,

		update: function() {
			this.pmoves = movableTiles();
			this.threats = threatTiles();
		},
	},
};

// level data
let L = new Board();

function canvasSize()
{
	return new Vector(canvas.width, canvas.height);
}

function coordsFromSquare(v)
{
	if(arguments.length > 1) {
		return coordsFromSquare(new Vector(...arguments));
	}
	let boardSize = W.ssize.mul(W.gdims);
	let origin = canvasSize().div(2).sub(boardSize.div(2));

	return v.mul(W.ssize).add(origin);
}

function squareFromCoords(c)
{
	if(arguments.length > 1) {
		return squareFromCoords(new Vector(...arguments));
	}
	let boardSize = W.ssize.mul(W.gdims);
	let origin = canvasSize().div(2).sub(boardSize.div(2));

	let square = c.sub(origin).div(W.ssize).map(Math.floor);
	if(square.x < 0 || W.gdims.x <= square.x
	   || square.y < 0 || W.gdims.y <= square.y) {
		return null;
	}
	return square;
}

function movableTiles()
{
	return Moves[SpaceType.knight](W.p, true);
}

function threatTiles()
{
	let threatGrid = createGrid(0);

	let pieces = gridToSquares(L.board, x => (x > SpaceType.startPiece));
	pieces.forEach((p) => {
		let weights = getWeights(p);
		weights.forEach((w) => {
			threatGrid[w[0].x][w[0].y] = Math.max(w[1], threatGrid[w[0].x][w[0].y]);
		});
	});

	return threatGrid;
}

// no anitaliasing of images
ctx.imageSmoothingEnabled = false;
// text begins at the top
ctx.textBaseline = "top";

// renders world without updating it
function render()
{
	ctx.fillStyle = "#000";
	ctx.fillRect(0, 0, canvas.width, canvas.height);

	// size of rendered board
	let boardSize = W.ssize.mul(W.gdims);
	let origin = canvasSize().div(2).sub(boardSize.div(2));

	let moves = W.C.pmoves;

	for(let x = 0; x < W.gdims.x; ++x) {
		for(let y = 0; y < W.gdims.y; ++y) {
			let squareStart = origin.add(W.ssize.mul(x, y)).add(0.5, 0.5);
			let style = ((x ^ y) & 1) ? [50,50,50] : [70,70,70];

			if(moves[x][y]) {
				style[1] = 100;
			}

			if(debug_overlay && W.C.threats[x][y]) {
				style[0] = 100;
			}

			if(L.at(x, y) === SpaceType.block) {
				style = [0,0,0];
			}

			ctx.fillStyle = `rgb(${style[0]}, ${style[1]}, ${style[2]})`;

			ctx.fillRect(...squareStart, ...W.ssize);

			if(debug_overlay && W.C.threats[x][y]) {
				ctx.fillStyle = "#fff";
				ctx.fillText(x + "," + y, ...squareStart);
			}
		}
	}

	// exit
	ctx.drawImage(...R.stair.sprite, ...coordsFromSquare(L.stair), ...W.ssize);

	// draw enemies
	ctx.scale(-1, 1);
	if(W.r) {
		W.r.forEach((piece) => {
			// this loop needed to get key from value
			for(let k in SpaceType) {
				if(SpaceType[k] === piece[0] && R[k] !== undefined) {
					ctx.drawImage(...R[k].sprite, ...coordsFromSquare(...piece[1]).mul(-1, 1).sub(W.ssize.x, 0), ...W.ssize);
				}
			}
		});
	} else for(let x = 0; x < W.gdims.x; ++x) {
		for(let y = 0; y < W.gdims.y; ++y) {
			// this loop needed to get key from value
			for(let k in SpaceType) {
				if(SpaceType[k] === L.at(x, y) && R[k] !== undefined) {
					ctx.drawImage(...R[k].sprite, ...coordsFromSquare(x, y).mul(-1, 1).sub(W.ssize.x, 0), ...W.ssize);
				}
			}
		}
	}
	ctx.scale(-1, 1);

	// player
	ctx.drawImage(...R.knight.sprite, ...coordsFromSquare(W.rp || W.p), ...W.ssize);

	if(L.dragon) {
		ctx.drawImage(...R.dragon.sprite, ...coordsFromSquare(L.dragon), W.ssize[0] * 2, W.ssize[1] * 2);
	}

	ctx.font = "15px sans-serif"
	ctx.fillStyle = "#ff0";
	ctx.fillText("score: " + score, 0, 0);

	// fades
	ctx.fillStyle = `rgba(0, 0, 0, ${W.fade})`;
	ctx.fillRect(0, 0, canvas.width, canvas.height);
}

// updates world, without rendering it
let acc = 0;
function update(dt)
{
	acc += dt * 5;

	if(acc >= 1) {
		for(let k in R) {
			if(R[k] instanceof Spritesheet) {
				R[k].next();
			}
		}
		acc = acc % 1;
	}
	Tween.step();
}

function loadLevel(template)
{
	L = new Board(template);
	W.p = L.start;
	W.C.update();
}

function loadRandomLevel()
{
	let selection = roomSelectionFromScore(score);
	let levelId = Math.floor(Math.random() * selection.length);
	loadLevel(selection[levelId]);
}

loadRandomLevel();

function jumpPiece(out, from, to)
{
	const jumpHeight = 1.5;
	const jumpDuration = 0.4;

	let yt = Tween.create(p => {
		out.y = p * to.y + (1 - p) * from.y;
		out.y -= 5 * (-p * p + p); // jump animation
	}, 0, 1, jumpDuration);

	let xt = Tween.create(x => out.x = x, from.x, to.x, jumpDuration);

	return Promise.all([ xt, yt ]);
}

function moveAllEnemies()
{
	W.r = [];

	let movePiece = (type, start, end) => {
		let entry = [ type, new Vector(...start) ];
		W.r.push(entry);

		return jumpPiece(entry[1], start, end);
	};

	let taken = gridToSquares(L.board, x => x > SpaceType.startPiece);
	let isTaken = p => (taken.findIndex(x => x[0] == p[0] && x[1] == p[1]) >= 0);
	let untake = p => {
		taken.splice(taken.findIndex(x => x[0] == p[0] && x[1] == p[1]), 1);
	};

	let promises = gridToSquares(L.board, x => x > SpaceType.startPiece).map((p) => {
		let weights = getWeights(p).filter(x => !isTaken(x[0]) || (x[0][0] == p[0] && x[0][1] == p[1]));
		let totalWeight = weights.reduce((a, b) => a + b[1], 0);

		// debugger;

		let select = Math.random() * totalWeight; // picked with weights
		let sum = 0;

		for(let w in weights) {
			sum += weights[w][1];
			if(select <= sum) {
				let target = weights[w][0];

				untake(p);
				taken.push(target);

				return movePiece(L.at(...p), p, target).then(() => {
					if(W.p.x == target.x && W.p.y == target.y) {
						alert("You died!\nScore: " + score);
						W.p.x = W.p.y = undefined;
					}

					if(target.x !== p.x || target.y !== p.y) {
						L.set(L.at(...p), ...target)
						L.set(SpaceType.empty, ...p);
					}
				});
			}
		}
	});

	Promise.all(promises).then(() => {
		W.r = null;
		W.C.update();
	});
}

function moveTo(pos)
{
	W.p = pos;

	switch(L.at(...pos)) {
	case SpaceType.knight:
	case SpaceType.bishop:
		score += 30;
		break;
	case SpaceType.queen:
		score += 90;
		break;
	case SpaceType.king:
		score += 20;
		break;
	case SpaceType.pawn:
		score += 10;
		break;
	}

	L.set(SpaceType.empty, ...pos);
	moveAllEnemies();
	W.C.update();
}

// events
let inputLock = 0; // lock controls
canvas.onclick = (e) => {
	if(inputLock > 0) {
		return;
	}

	let square = squareFromCoords(e.offsetX, e.offsetY);
	if(square && movableTiles()[square.x][square.y] && L.at(...square) !== SpaceType.block) {
		++inputLock;

		if(square.x === L.stair.x && square.y === L.stair.y) {
			// exiting
			++inputLock; // both jump and fade need locks
			jumpPiece(W.rp = new Vector(...W.p), W.p, square).then(() => {
				score += 100;
				--inputLock;
				W.rp = null;
			});
			Tween.create(x => W.fade = x, 0, 1, 0.4).then(() => {
				loadRandomLevel();
				return Tween.create(x => W.fade = x, 1, 0, 0.4).then(() => {
					--inputLock;
				});
			});
		} else {
			jumpPiece(W.rp = new Vector(...W.p), W.p, square).then(() => {
				inputLock = false;
				W.rp = null;
				moveTo(square);
			});
		}
	}
};

R.then(() => {
	let updateInterval = setInterval((() => {
		let startTick = Date.now();
		let prevTick = Date.now();

		return () => {
			let currTick = Date.now();
			update((currTick - prevTick) / 1000, (currTick - startTick) / 1000);
			render()
			prevTick = currTick;
		};
	})(), 1000 / fps);
})

