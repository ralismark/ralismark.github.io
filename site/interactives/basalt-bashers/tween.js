const Easing = {
	quadIn: x => x*x,
	quadOut: x => x*(2-x),
};

class TweenPiece
{
	constructor(easing, setter, from, to, start, end, finish)
	{
		this.easing = easing;
		this.setter = setter;
		this.from   = from;
		this.to     = to;
		this.start  = start;
		this.end    = end;
		this.finish = finish;

		this.finished = false;
	}

	step()
	{
		let time = Date.now();
		// tween hasn't started yet
		if(time < this.start) {
			return;
		}

		// tween done
		if(time > this.end) {
			if(!this.finished) {
				// final step
				this.finished = true;
				this.setter(this.to);
				this.finish();
			}
			return;
		}

		let progress = this.easing((time - this.start) / (this.end - this.start));
		let value = progress * this.to + (1 - progress) * this.from;
		this.setter(value);
	}
};

const Tween = {
	pieces: [],

	step: function() {
		this.pieces.forEach(i => i.step());
	},

	create: function(setter, from, to, duration, easing) {
		easing = easing || (i => i);
		return new Promise((r) => {
			let finish = () => {
				r();
			};

			let piece = new TweenPiece(easing, setter, from, to,
				Date.now(), Date.now() + duration * 1000, finish);

			this.pieces.push(piece);
		});
	},
};
