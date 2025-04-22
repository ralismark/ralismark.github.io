function inBounds(pos)
{
	return 0 <= pos.x && pos.x < W.gdims.x && 0 <= pos.y && pos.y < W.gdims.y;
}

function movesFromOffsets(pos, offsets, isPlayer)
{
	let grid = createGrid(false);

	offsets.forEach((o) => {
		let square = pos.add(...o);
		if(inBounds(square) && (isPlayer || L.at(...square) === SpaceType.empty)) {
			grid[square.x][square.y] = true;
		}
	});

	// can stay
	if(!isPlayer) {
		grid[pos.x][pos.y] = true;
	}

	return grid;
}

function movesFromTraces(pos, directions, isPlayer)
{
	let grid = createGrid(false);

	directions.forEach((d) => {
		let cursor = pos.add(...d);
		while(inBounds(cursor) && (isPlayer || L.at(...cursor) === SpaceType.empty)) {
			grid[cursor.x][cursor.y] = true;
			cursor = cursor.add(...d);

			// stop at capture
			if(isPlayer
			   ? (L.at(...cursor) > SpaceType.startPieces)
			   : (W.p.x == cursor.x && W.p.y == cursor.y)) {
				break;
			}
		}
	});

	// can stay
	if(!isPlayer) {
		grid[pos.x][pos.y] = true;
	}

	return grid;
}

const Moves = {
	[SpaceType.knight]: (pos, isPlayer) => movesFromOffsets(pos, [
		[-2 ,  1],
		[-1 ,  2],
		[ 1 ,  2],
		[ 2 ,  1],
		[ 2 , -1],
		[ 1 , -2],
		[-1 , -2],
		[-2 , -1],
	], isPlayer),

	[SpaceType.bishop]: (pos, isPlayer) => movesFromTraces(pos, [
		[  1,  1 ],
		[  1, -1 ],
		[ -1,  1 ],
		[ -1, -1 ],
	], isPlayer),

	[SpaceType.queen]: (pos, isPlayer) => movesFromTraces(pos, [
		[  1,  1 ],
		[  1, -1 ],
		[ -1,  1 ],
		[ -1, -1 ],
		[  1,  0 ],
		[ -1,  0 ],
		[  0,  1 ],
		[  0, -1 ],
	], isPlayer),

	[SpaceType.king]: (pos, isPlayer) => movesFromOffsets(pos, [
		[  1,  1 ],
		[  1, -1 ],
		[ -1,  1 ],
		[ -1, -1 ],
		[  1,  0 ],
		[ -1,  0 ],
		[  0,  1 ],
		[  0, -1 ],
	], isPlayer),

	[SpaceType.pawn]: (pos, isPlayer) => movesFromOffsets(pos, [
		[  1,  0 ],
		[ -1,  0 ],
		[  0,  1 ],
		[  0, -1 ],
	], isPlayer),
};

function getWeights(pos)
{
	let moveFn = Moves[L.at(...pos)];
	if(moveFn === undefined) {
		return null;
	}

	let dist = (p) => p.sub(W.p).magnitude;

	let squares = gridToSquares(moveFn(pos));
	return squares.map(p => {
		let score = 0;

		if(p.x === W.p.x && p.y === W.p.y) {
			// basically always capture if possible
			score += 100;
		}

		if(!W.C.pmoves[p.x][p.y]) {
			// reward for avoiding capture
			score += 3;
		}

		let nextMoves = moveFn(p);
		let coveringSquares = gridToSquares(nextMoves).filter(i => W.C.pmoves[i.x][i.y]);
		score += 5 * coveringSquares.length; // +5 for each [movement] square covered

		if(nextMoves[W.p.x][W.p.y]) {
			score += 2; // +2 for [directly] threatening piece
		}

		// reward for proximity (by rank)
		// score += 5 * i / squares.length;
		score += 5 * squares.filter(v => dist(v) > dist(p)).length / squares.length;

		// penalise staying still
		if(p.x === pos.x && p.y === pos.y) {
			score /= 2;
		}

		// adjusted for better weighing
		// better squares are much more likely
		let adjustedScore = score * score;

		return [ p, adjustedScore ];
	});
}
